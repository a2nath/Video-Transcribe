import os
import whisper
import argparse
import numpy as np
from pathlib import Path
from typing import Iterator, TextIO

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

def main():
    parser = argparse.ArgumentParser("Generates subtitiles of the video file as an input")
    parser.add_argument("--filename", "-f", help="Name of the video file that needs to subtitles", type=argparse.FileType('r', encoding='UTF-8'))
    parser.add_argument("--rawfile", "-r", help="raw subtitiles", type=argparse.FileType('r', encoding='UTF-8'))
    parser.add_argument("--language", "-l", help="Language to be translated from", default='en', type=str)
    parser.add_argument("--output_dir", "-o", help="Ouput file directory", default=os.getcwd())
    parser.add_argument("--model_size", "-s", help="Size of the model, default is large. For testing use tiny", default='large')

    args = parser.parse_args()

    if args.rawfile is not None:
        args.rawfile = args.rawfile.name
    elif args.filename is not None:
        args.filename = args.filename.name

    print("\nSettings as follows:")
    print("----------------------")
    arguments = vars(args);
    for arg in arguments:
        print(arg, '\t', getattr(args, arg))
    print("----------------------\n")

    model = whisper.load_model(args.model_size)
    if args.rawfile is not None:
        f = open(args.rawfile, "r")
        result = f.read()
    elif args.filename is not None:
        result = model.transcribe(args.filename, verbose=True, language=args.language)

    # save SRT
    with open(os.path.join(args.output_dir, Path(args.filename).stem + f".{args.language}.srt"), "w") as srt:
        write_srt(result["segments"], file=srt)

    return 0

if __name__ == "__main__":
    main()
