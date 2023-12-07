from faster_whisper import WhisperModel as whisper
import argparse
from pathlib import Path
import ffmpeg
from os import getcwd, listdir, remove
from os.path import isfile, join
from typing import Iterator, TextIO

# debug only
from pdb import set_trace

# Note:
# by default large model is used and float32 precision
#
#

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
    if file_suffix == ".mkv" or file_suffix == ".avi" or file_suffix == ".mp4":
        return True

    return False

def isAudioFile(file_suffix):
    file_suffix = file_suffix.lower()
    if file_suffix == ".mp3" or file_suffix == ".wave" or file_suffix == ".aac":
        return True

    return False

def transcribe(args, videofile, audiofile = None):
    if audiofile is None:
        audiofile = videofile

    if args.device != "cpu":
        model = whisper(args.model_size, device=args.device, compute_type=args.precision)
    else:
        model = whisper(args.model_size, compute_type=args.precision)

    segments, stats = model.transcribe(audiofile, beam_size=args.beam_size, language=args.language)

    print("Detected language '%s' with probability %f" % (stats.language, stats.language_probability))

    # save SRT
    with open(join(args.output_dir, Path(videofile).stem + f".{args.language}.srt"), "w") as srt:
        write_srt(segments, file=srt)

def main():

    video_files = []
    audio_files = []

    parser = argparse.ArgumentParser("Generates subtitiles of the video file as an input")
    parser.add_argument("--input_dir", "-i", help="Input directory where video files are", default=getcwd())
    parser.add_argument("--filename", "-f", help="Name of the video file that needs to subtitles", type=argparse.FileType('r', encoding='UTF-8'))
    parser.add_argument("--output_dir", "-o", help="Ouput directory", default=getcwd())
    parser.add_argument("--language", "-l", help="Language to be translated from", default='en', type=str)
    parser.add_argument("--beam_size", "-b", help="Beam size parameter for whisper faster parameter", type=int, default=5)
    parser.add_argument("--precision", "-p", help="Precision to use to create the model", type=str, default="float32")
    parser.add_argument("--device", "-d", help="Device to use such a CPU or GPU", default="cuda")
    parser.add_argument("--model_size", "-s", help="Size of the model, default is large. For testing use tiny", default="large")

    args = parser.parse_args()
    print("\nSettings as follows:")
    print("----------------------")

    arguments = vars(args);
    for arg in arguments:
        print(arg, '\t', getattr(args, arg))

    print("----------------------\n")

    if args.filename is not None:
        if isVideoFile(Path(args.filename.name).suffix) == True:
            video_files.append(args.filename.name)
        elif isAudioFile(Path(args.filename.name).suffix) == True:
            audio_files.append(args.filename.name)

    elif args.input_dir is not None:
        for f in listdir(args.input_dir):
            if isfile(join(args.input_dir, f)) and isVideoFile(Path(f).suffix) == True:
                video_files.append(f);
            elif isfile(join(args.input_dir, f)) and isAudioFile(Path(f).suffix) == True:
                audio_files.append(f);

    if len(video_files) == 0 and len(audio_files) == 0:
        print("There were no files to process")
        exit(0)

    # convert the videofile into audiofile before processing
    for videoFile in video_files:
        ffmpeg.input(videoFile).output("output.mp3").run()
        transcribe(args, videoFile, "output.mp3")

    # convert the audiofile before processing
    for audiofile in audio_files:
        transcribe(args, audiofile)

    # cleanup the audio file that is no longer needed
    if isfile("output.mp3"):
        remove("output.mp3")
    return 0

if __name__ == "__main__":
    main()
