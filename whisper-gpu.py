import os
from os.path import isfile, join
import argparse
import psutil
import ffmpeg
import timeit
import time
from faster_whisper import WhisperModel as whisper
from faster_whisper.utils import available_models
from pathlib import Path
from typing import Iterator, TextIO
from download_best import Download
import validators

# Note:
# by default large model is used and float32 precision
#
#
video_supported = [".mkv", ".mov",  ".avi", ".mp4"]
audio_supported = [".mp3", ".wave", ".aac", ".flac"]
scrap_filename = "output.aac"

def sizes_supported() -> list[str]:
	return available_models()

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
	with open(join(args.output_dir, Path(videofile).stem + "." + time.strftime("%Y%m%d-%H%M%S") + f".{args.language}.srt"), "w") as srt:
		write_srt(segments, file=srt)

	print(videofile," took ","{:.1f}".format(timeit.default_timer() - start_time)," seconds")
	print("-------------------------------------------------------")

def initialize(args):

	print("\nInitializing:")
	print("-------------------------------------------------------")

	# cleanup the audio file that is no longer needed
	if isfile(scrap_filename):
		os.remove(scrap_filename)

	# initialize the model with given args
	if args.device != "cuda":
		#overrides the os.environ["OMP_NUM_THREADS"]
		threads = str(args.nproc)
		model = whisper(args.model_size, cpu_threads=threads, num_workers=4, device=args.device, compute_type=args.precision)
	else:
		model = whisper(args.model_size, device=args.device, compute_type=args.precision)

	return model;

def close(args):

	if isfile(scrap_filename):
		os.remove(scrap_filename)

	if Path(args.filename).exists():
		args.filename.close()

def add_media_files(args, video_files, audio_files, debug = False, verbose = False):

	if args.filename:
		if validators.url(args.filename):
			args.url        = args.filename
			args.list       = None
			args.audio_only = True
			args.video_only = None
			args.keep       = False
			args.output     = scrap_filename
			args.merge      = False
			args.overwrite  = None
			args.username   = None
			args.bin        = None
			args.verbose    = True

			download = Download(args, debug)
			audio_file, retcode = download.run()

			if retcode == 0 and audio_file == args.output:
				audio_files.append(audio_file)

			else:
				print(f"Could not process the URL, code {retcode} and audio file {audio_file} and args.output {args.output}")
				close(args)
				exit(-1)
		else:
			args.filename = Path(args.input_dir, args.filename.name)
			if args.filename.exists():
				if isVideoFile(args.filename.suffix) == True:
					video_files.append(str(args.filename))
				elif isAudioFile(args.filename.suffix) == True:
					audio_files.append(str(args.filename))

	if args.input_dir:
		for filename in os.listdir(args.input_dir):
			filename = Path(args.input_dir, filename)
			if filename.is_file() and isVideoFile(filename.suffix) == True:
				video_files.append(str(filename));
			elif filename.is_file() and isAudioFile(filename.suffix) == True:
				audio_files.append(str(filename))

	if len(video_files) + len(audio_files) == 0:
		if args.filename:
			print("URL is not valid")
			close(args)
			exit(-1)
		else:
			print("There were no media to process")
			close(args)
			exit(0)

	print("Found ", len(video_files) + len(audio_files), " files")


def main():

	global scrap_filename
	video_files = []
	audio_files = []


	parser = argparse.ArgumentParser("Generates subtitiles of the video file as an input")
	parser.add_argument("--input_dir", "-i", help="Input directory where video files are")
	parser.add_argument("--filename", "-f", help="Name of the media file stored in the filesystem or URL of a video/audio file that needs to subtitles")
	parser.add_argument("--output_dir", "-o", help="Ouput directory", default=os.getcwd())
	parser.add_argument("--language", "-l", help="Language to be translated from", default='en', type=str)
	parser.add_argument("--beam_size", "-b", help="Beam size parameter or best_of equivalent from Open-AI whisper", type=int, default=5)
	parser.add_argument("--precision", "-p", help="Precision to use to create the model", type=str, default="auto")
	parser.add_argument("--device", "-d", help="Device to use such a CPU or GPU", choices=["cpu", "cuda"], default="cuda")
	parser.add_argument("--model_size", "-s", help="Size of the model, default is small.", choices=sizes_supported(), default="small")
	parser.add_argument("--nproc", "-n", help="Number of CPUs to use", default=psutil.cpu_count(logical=False), type=int)
	parser.add_argument("--verbose", help="Verbose print from dependent processes", action='store_true')
	parser.add_argument("--quiet", help="Debug print off", action='store_true')

	args = parser.parse_args()
	if args.input_dir:
		args.input_dir = str(Path(args.input_dir).resolve())

	# make the directory if missing
	Path(args.output_dir).mkdir(parents=True, exist_ok=True)
	scrap_filename = str(Path(args.output_dir, scrap_filename))

	print("\nSettings as follows:")
	print("-------------------------------------------------------")

	arguments = vars(args);
	for arg in arguments:
		print(arg, '\t', getattr(args, arg))

	model = initialize(args);

	add_media_files(args, video_files, audio_files, debug = not args.quiet, verbose = args.verbose)

	# convert the videofile into audiofile before processing
	for videoFile in video_files:
		ffmpeg.input(videoFile).output(scrap_filename).run(overwrite_output=True)
		transcribe(args, model, videoFile, scrap_filename)

	# convert the audiofile before processing
	for audiofile in audio_files:
		transcribe(args, model, audiofile)


	# cleanup the audio file that is no longer needed
	close(args)
	print("Done.")

	return 0

if __name__ == "__main__":
	main()
