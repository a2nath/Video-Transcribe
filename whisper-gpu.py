import os
from os.path import isfile, join
import argparse
import psutil
import ffmpeg
import timeit
from faster_whisper import WhisperModel as whisper
from pathlib import Path
from typing import Iterator, TextIO


# Note:
# by default large model is used and float32 precision
#
#
sizes_supported = ["tiny", "base", "small", "medium", "large-v1", "large-v2", "large-v3", "large"]

video_supported = [".mkv", ".mov",  ".avi", ".mp4"]
audio_supported = [".mp3", ".wave", ".aac", ".flac"]

def srt_format_timestamp(seconds: float):
    assert seconds >= 0, "non-negative timestamp expected"
    milliseconds = round(seconds * 1000.0)

    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000

    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000

    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000

    return (f"{hours}:") + f"{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def write_srt(segments, file: TextIO):

    print("\nBegin transcription and creating subtitle file:")
    print("-------------------------------------------------------")

    count = 0
    for segment in segments:
        count +=1
        print(
            f"{count}\n"
            f"{srt_format_timestamp(segment.start)} --> {srt_format_timestamp(segment.end)}\n"
            f"{segment.text.replace('-->', '->').strip()}\n",
            file=file,
            flush=True,
        )

def isVideoFile(file_suffix):
    file_suffix = file_suffix.lower()
    if file_suffix in video_supported:
        return True

    return False

def isAudioFile(file_suffix):
    file_suffix = file_suffix.lower()
    if file_suffix in audio_supported:
        return True

    return False

def transcribe(args, model, videofile, audiofile = None):

    start_time = timeit.default_timer()

    if audiofile is None:
        audiofile = videofile

    segments, stats = model.transcribe(audiofile, beam_size=args.beam_size, language=args.language)

    print("\nDetected language '%s' with probability %f" % (stats.language, stats.language_probability))

    # save SRT
    with open(join(args.output_dir, Path(videofile).stem + f".{args.language}.srt"), "w") as srt:
        write_srt(segments, file=srt)

    print(videofile," took ","{:.1f}".format(timeit.default_timer() - start_time)," seconds")
    print("-------------------------------------------------------")

def initialize(args):

    print("\nInitializing:")
    print("-------------------------------------------------------")

   # cleanup the audio file that is no longer needed
    if isfile("output.mp3"):
        os.remove("output.mp3")

    os.environ["OMP_NUM_THREADS"] = str(args.nproc)


    # initialize the model with given args
    model = whisper(args.model_size, device=args.device, compute_type=args.precision)
    return model;

def close(prog_duration):

    if isfile("output.mp3"):
        os.remove("output.mp3")

    print("Done.")

def main():

    video_files = []
    audio_files = []

    parser = argparse.ArgumentParser("Generates subtitiles of the video file as an input")
    parser.add_argument("--input_dir", "-i", help="Input directory where video files are", default=os.getcwd())
    parser.add_argument("--filename", "-f", help="Name of the video file that needs to subtitles", type=argparse.FileType('r', encoding='UTF-8'))
    parser.add_argument("--output_dir", "-o", help="Ouput directory", default=os.getcwd())
    parser.add_argument("--language", "-l", help="Language to be translated from", default='en', type=str)
    parser.add_argument("--beam_size", "-b", help="Beam size parameter or best_of equivalent from Open-AI whisper", type=int, default=5)
    parser.add_argument("--precision", "-p", help="Precision to use to create the model", type=str, default="auto")
    parser.add_argument("--device", "-d", help="Device to use such a CPU or GPU", choices=["cpu", "cuda"], default="cuda")
    parser.add_argument("--model_size", "-s", help="Size of the model, default is large.", choices=sizes_supported, default="small")
    parser.add_argument("--nproc", "-n", help="Number of CPUs to use", default=psutil.cpu_count(logical=False), type=int)

    args = parser.parse_args()

    if args.filename is not None:
        args.filename = args.filename.name
        if isVideoFile(Path(args.filename).suffix) == True:
            video_files.append(args.filename)
        elif isAudioFile(Path(args.filename).suffix) == True:
            audio_files.append(args.filename)

    elif args.input_dir is not None:
        for f in os.listdir(args.input_dir):
            if isfile(join(args.input_dir, f)) and isVideoFile(Path(f).suffix) == True:
                video_files.append(f);
            elif isfile(join(args.input_dir, f)) and isAudioFile(Path(f).suffix) == True:
                audio_files.append(f);

    if len(video_files) == 0 and len(audio_files) == 0:
        print("There were no files to process")
        exit(0)
    else:
        print("Found ", len(video_files)+len(audio_files), " files")

    print("\nSettings as follows:")
    print("-------------------------------------------------------")

    arguments = vars(args);
    for arg in arguments:
        print(arg, '\t', getattr(args, arg))

    model = initialize(args);

    # convert the videofile into audiofile before processing
    for videoFile in video_files:
        ffmpeg.input(videoFile).output("output.mp3").run()
        transcribe(args, model, videoFile, "output.mp3")

    # convert the audiofile before processing
    for audiofile in audio_files:
        transcribe(args, model, audiofile)


    # cleanup the audio file that is no longer needed
    close()

    return 0

if __name__ == "__main__":
    main()
