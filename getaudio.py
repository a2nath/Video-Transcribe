import ffmpeg
import os
import argparse
from pathlib import Path, PurePath
import time

video_supported = [".mkv", ".mov",  ".avi", ".mp4"]
audio_supported = [".mp3", ".wave", ".aac", ".flac"]

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

def main():

    video_files = []
    parser = argparse.ArgumentParser("Generates audio of the video file as an input")
    parser.add_argument("--input_dir", "-i", help="Input directory where video files are", default=os.getcwd())
    parser.add_argument("--filename", "-f", help="Name of the video file that needs to subtitles", type=argparse.FileType('r', encoding='UTF-8'))
    parser.add_argument("--output_dir", "-o", help="Ouput directory", default=os.getcwd())
    parser.add_argument("--format", help="Ouput format to produce", choices=audio_supported, default="mp3")

    args = parser.parse_args()
    args.input_dir = str(Path(args.input_dir).resolve())

    # make the directory is missing
    if args.output_dir is not None:
        Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    if args.filename is not None:
        args.filename = args.filename.name
        if isVideoFile(Path(args.filename).suffix) == True:
            video_files.append(PurePath(args.input_dir, filename))

    elif args.input_dir is not None:
        for f in os.listdir(args.input_dir):
            if os.path.isfile(os.path.join(args.input_dir, f)) and isVideoFile(Path(f).suffix) == True:
                video_files.append(PurePath(args.input_dir, f))

    if len(video_files) == 0:
        print("There were no files to process")
        exit(0)
    else:
        print("Found ", len(video_files), " files")

    print("\nSettings as follows:")
    print("-------------------------------------------------------")

    arguments = vars(args);
    for arg in arguments:
        print(arg, '\t', getattr(args, arg))

    time.sleep(1)

    print("\nRunning:")
    print("-------------------------------------------------------")

    for videofile in video_files:
        output_filename = str(PurePath(args.output_dir, videofile.stem + "." + time.strftime("%Y%m%d-%H%M%S") + "." + args.format))
        print("\tOutput file", '\t', output_filename)
        ffmpeg.input(videofile).output(output_filename).run()
        print("\tDone")

    print("\nFinished:")
    print("-------------------------------------------------------")


    # cleanup the audio file that is no longer needed
    # close()

    return 0

if __name__ == "__main__":
    main()
