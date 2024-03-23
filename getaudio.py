import ffmpeg
import os
import argparse
from pathlib import Path, PurePath
import time
import re

video_supported = ["mkv", "webm", "mov",  "avi", "mp4"]
audio_supported = ["mp3", "wave", "aac", "flac"]

def isVideoFile(file_suffix):
	if file_suffix.split('.')[-1].lower() in video_supported:
		return True

	return False

def isAudioFile(file_suffix):
	if file_suffix.lower() in audio_supported:
		return True

	return False

def valid_time(time_str):
	pattern = r'^\d{2}:\d{2}:\d{2}$'  # Regular expression pattern for xx:xx:xx format
	if not re.match(pattern, time_str):
		raise argparse.ArgumentTypeError(f"Invalid time format: {time_str}. Must be in the format xx:xx:xx")
	return time_str

def extract_audio(args):

	video_files = []
	if args.filename is not None:
		args.filename = Path(args.input_dir, args.filename.name)
		if isVideoFile(args.filename.suffix) == True:
			video_files.append(args.filename)

	elif args.input_dir is not None:
		for filename in os.listdir(args.input_dir):
			filename = Path(args.input_dir, filename)
			if filename.is_file() and isVideoFile(filename.suffix) == True:
				video_files.append(filename);

	if len(video_files) == 0:
		print("There were no files to process")
		exit(0)
	else:
		print("Found ", len(video_files), " files")
		if args.output_dir is None:
			args.output_dir = video_files[0].parents[0]

	# make the directory if missing
	Path(args.output_dir).mkdir(parents=True, exist_ok=True)

	print("\nSettings as follows:")
	print("-------------------------------------------------------")

	arguments = vars(args);
	for arg in arguments:
		print(arg, '\t', getattr(args, arg))

	# join all arguments for the program
	if args.start and args.end:
		options = " ".join(["-ss", args.start, "-to", args.end])
	elif args.start:
		options = " ".join(["-ss", args.start]);
	elif args.end:
		options = " ".join(["-to", args.end]);
	else:
		options = ""

	time.sleep(1)
	
	print("\nRunning:")
	print("-------------------------------------------------------")

	for videofile in video_files:
		output_filename = str(Path(args.output_dir, videofile.stem + "." + time.strftime("%Y%m%d-%H%M%S") + "." + args.format))
		print("\tOutput file", '\t', output_filename)
		
		if args.start and args.end:
			ffmpeg.input(str(videofile), ss=args.start, to=args.end).output(output_filename).run()
		elif args.start:
			ffmpeg.input(str(videofile), ss=args.start).output(output_filename).run()
		elif args.end:
			ffmpeg.input(str(videofile), to=args.end).output(output_filename).run()
		else:
			ffmpeg.input(str(videofile)).output(output_filename).run()

		print("\tDone")

	print("\nFinished:")
	print("-------------------------------------------------------")

def main():
	parser = argparse.ArgumentParser("Generates audio of the video file as an input")
	parser.add_argument("-i", "--input_dir", help="Input directory where video files are", default=os.getcwd())
	parser.add_argument("-f", "--filename", help="Name of the video file that needs to subtitles", type=argparse.FileType('r', encoding='UTF-8'))
	parser.add_argument("-o", "--output_dir", help="Ouput directory")
	parser.add_argument("--format", help="Ouput format to produce", choices=audio_supported, default="mp3")
	parser.add_argument("-s", "--start", help="Start time in 00:00:00 format", type=valid_time)
	parser.add_argument("-e", "--end", help="End time in 00:00:00 format", type=valid_time)

	args = parser.parse_args()
	args.input_dir = str(Path(args.input_dir).resolve())

	extract_audio(args)

	# cleanup the audio file that is no longer needed
	# close()

	return 0

if __name__ == "__main__":
	main()
