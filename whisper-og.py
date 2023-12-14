# open-AIs version of the implmentation
import os
from os.path import isfile, join
import argparse
import psutil
import ffmpeg
import whisper
import timeit
import time
from pathlib import Path
from typing import Iterator, TextIO


# Note:
# by default large model is used and float32 precision
#
#
sizes_supported = ["tiny", "base", "small", "medium", "large-v1", "large-v2", "large-v3", "large"]

video_supported = [".mkv", ".mov",  ".avi", ".mp4"]
audio_supported = [".mp3", ".wave", ".aac", ".flac"]
scrapfile = ""

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

def write_srt(transcript: Iterator[dict], file: TextIO):

    print("\nBegin transcription and creating subtitle file:")
    print("-------------------------------------------------------")

    count = 0
    for segment in transcript:
        count +=1
        print(
            f"{count}\n"
            f"{srt_format_timestamp(segment['start'])} --> {srt_format_timestamp(segment['end'])}\n"
            f"{segment['text'].replace('-->', '->').strip()}\n",
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

    segments = model.transcribe(audiofile, verbose=True, beam_size=args.beam_size, language=args.language)

    # save SRT
    with open(join(args.output_dir, Path(videofile).stem + "." + time.strftime("%Y%m%d-%H%M%S") + f".{args.language}.srt"), "w") as srt:
        write_srt(segments["segments"], file=srt)

    print(videofile," took ","{:.1f}".format(timeit.default_timer() - start_time)," seconds")
    print("-------------------------------------------------------")

def initialize(args):

    print("\nInitializing:")
    print("-------------------------------------------------------")

    # cleanup the audio file that is no longer needed
    if isfile(scrapfile):
        os.remove(scrapfile)

    os.environ["OMP_NUM_THREADS"] = str(args.nproc)


    # initialize the model with given args
    model = whisper.load_model(args.model_size, device=args.device)

    return model;

def close():

    if isfile(scrapfile):
        os.remove(scrapfile)

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
    parser.add_argument("--device", "-d", help="Device to use such a CPU or GPU", choices=["cpu", "cuda"], default="cpu")
    parser.add_argument("--model_size", "-s", help="Size of the model, default is large.", choices=sizes_supported, default="small")
    parser.add_argument("--nproc", "-n", help="Number of CPUs to use", default=psutil.cpu_count(logical=False), type=int)

    args = parser.parse_args()
    args.input_dir = str(Path(args.input_dir).resolve())

    # make the directory if missing
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    scrapfile = str(Path(args.output_dir, "output.mp3"))

    if args.filename is not None:
        args.filename = Path(args.input_dir, args.filename.name)
        if isVideoFile(args.filename.suffix) == True:
            video_files.append(str(args.filename))
        elif isAudioFile(args.filename.suffix) == True:
            audio_files.append(str(args.filename))

    elif args.input_dir is not None:
        for filename in os.listdir(args.input_dir):
            filename = Path(args.input_dir, filename)
            if filename.is_file() and isVideoFile(filename.suffix) == True:
                video_files.append(str(filename));
            elif filename.is_file() and isAudioFile(filename.suffix) == True:
                audio_files.append(str(filename));

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
        ffmpeg.input(videoFile).output(scrapfile).run(overwrite_output=True)
        transcribe(args, model, videoFile, scrapfile)

    # convert the audiofile before processing
    for audiofile in audio_files:
        transcribe(args, model, audiofile)


    # cleanup the audio file that is no longer needed
    close()

    return 0

if __name__ == "__main__":
    main()
