# open-AIs version of the implmentation
import os
from os.path import isfile, join
import argparse
import psutil
import ffmpeg
import whisper
import timeit
import time
from whisper import available_models
from pathlib import Path
from typing import Iterator, TextIO
from utils.download_best import Download
import validators
from utils.get_audio import AudioProcess

temp_audio_filepath = "temp_audio.mp3"

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

def findarg(args, key: str) -> bool:
	return key in args and getattr(args, key)

def get_fullpath(output_dir, output_file) -> tuple[Path, str]:
	output_filepath = Path(output_file).resolve()

	if output_filepath.parent != Path(output_dir).resolve():
		output_dir = output_filepath.parent
		output_file = Path(output_file).name

	return Path(output_dir, output_file), output_dir

def transcribe(args, model, full_filepath, filename = None):

	assert type(full_filepath) == str

	if filename is None: # same as path implicitly
		filename = full_filepath

	start_time = timeit.default_timer()
	segments = model.transcribe(full_filepath, verbose=True, beam_size=args.beam_size, language=args.language)

	# save SRT
	srt_subtitle_filename = join(args.output_dir, Path(filename).stem + "." + time.strftime("%Y%m%d-%H%M%S") + f".{args.language}.srt")

	with open(srt_subtitle_filename, "w") as srt:
		write_srt(segments["segments"], file=srt)

	print(filename," took ","{:.1f}".format(timeit.default_timer() - start_time)," seconds")
	print("-------------------------------------------------------")

def initialize(args):

	print("--------------------INITIALIZING-----------------------")

	# cleanup the audio file that is no longer needed
	if isfile(temp_audio_filepath):
		os.remove(temp_audio_filepath)

	os.environ["OMP_NUM_THREADS"] = str(args.nproc)


	# initialize the model with given args
	model = whisper.load_model(args.model_size, device='cpu')

	return model;

def close(args):

	if not findarg(args, 'keep') and isfile(temp_audio_filepath):
		os.remove(temp_audio_filepath)

	if findarg(args, 'filename') and isfile(args.filename):
		args.filename.close()

def add_media_files(args, media_files, debug = False, verbose = False):

	if findarg(args, 'filename'):
		if validators.url(args.filename):
			args.url         = args.filename
			args.audio_only  = True
			args.restrict_filenames   = True
			args.overwrite            = True
			args.verbose              = False
			args.audio_format         = 'mp3'

			download = Download(args, debug)
			audio_file_list, retcode = download.run()

			if retcode == 0:# and audio_file_list == args.output_name:
				media_files += audio_file_list
			else:
				print(f"Could not process the URL, code {retcode} and audio file {audio_file_list} and args.output_name {args.output_name}")
				close(args)
				exit(-1)

		elif Path(args.filename).exists():
			args.filename, args.output_dir = get_fullpath(os.getcwd(), args.filename)
			media_files.append(str(args.filename))

	elif findarg(args, 'input_dir'):
		if Path(args.input_dir).exists():
			for filename in os.listdir(args.input_dir):
				filename = Path(args.input_dir, filename)
				if filename.is_file():
					media_files.append(str(filename));
		else:
			raise FileNotFoundError(f"--input_dir argument does not specify a valid dir: {args.input_dir}")

	# did not find any files
	if len(media_files) == 0:
		if args.filename:
			print("URL is not valid")
			close(args)
			exit(-1)
		else:
			print("There were no media to process")
			close(args)
			exit(0)

	print(f"Media files found {len(media_files)}")


def main():

	global temp_audio_filepath
	media_files = []

	parser = argparse.ArgumentParser("Generates subtitiles of the video file as an input")
	parser.add_argument("-f", "--filename", help="Name of the media file stored in the filesystem or URL \
						of a video/audio file that needs to subtitles. URL can also be a list of media")
	parser.add_argument("-i", "--input_dir", help="Input directory where video files are. --filename overrides this")
	parser.add_argument("-af", "--audio_filter", help="Audio or video filters to use before transcription \
						(for ffmpeg), no spaces, just comma-separated")
	parser.add_argument("-o", "--output_name", help="Output filename in case of issues with title")
	parser.add_argument("-od", "--output_dir", help="Ouput directory", default=os.getcwd())
	parser.add_argument("-l", "--language", help="Language to be translated from", default='en', type=str)
	parser.add_argument("-b", "--beam_size", help="Beam size parameter or best_of equivalent from Open-AI whisper", type=int, default=5)
	parser.add_argument("-s", "--model_size", help="Size of the model, default is small.", choices=sizes_supported(), nargs='?', default="small")
	parser.add_argument("-n", "--nproc", help="Number of CPUs to use", default=psutil.cpu_count(logical=False), type=int)
	parser.add_argument('-k', "--keep", help="Keep intermediate files", action='store_true')
	parser.add_argument("--verbose", help="Verbose print from dependent processes", action='store_true')
	parser.add_argument("--quiet", help="Debug print off", action='store_true')
	parser.add_argument("--playlist_start", help="Starting position from a list of media, to start downloading from")
	parser.add_argument("--playlist_end", help="Ending position from a list of media, to stop downloading at")

	args = parser.parse_args()

	# print out the list of possible sizes if no argument is given
	if 'model_size' in args and getattr(args, 'model_size') is None:
		supported = sizes_supported()
		print("\nSupported size in faster-whisper")
		print("-------------------------------------------------------")
		for size in supported:
			print(f"*  {size}");
		close(args)
		exit(0)


	# make the directory if missing, output_name override output_dir if former has dir already
	if findarg(args, 'output_name'):
		args.output_name, args.output_dir = get_fullpath(args.output_dir, args.output_name)
	Path(args.output_dir).mkdir(parents=True, exist_ok=True)

	# print out the settings, some of them belongs to dependent scripts such as downloader or get-audio
	if args.quiet == False:
		print("-----------------------SETTINGS------------------------")
		arguments = vars(args)
		for arg in arguments:
			print(arg, '\t', getattr(args, arg))

	temp_audio_filepath = str(Path(args.output_dir, temp_audio_filepath))

	add_media_files(args, media_files, debug = not args.quiet, verbose = args.verbose)
	model = initialize(args);

	# convert the videofile into audiofile before processing
	for media_file in media_files:
		if args.quiet == False:
			print(f"Processing file {media_file} and using audio filter")

		if args.audio_filter:
			if args.quiet == False:
				print(f"File {audiofile}")
				print(f"Filter {args.audio_filter}")

			audio_processor = AudioProcess(args)
			audio_processor.extract_audio(input_filepath=media_file, output_filepath=temp_audio_filepath, overwrite=True);

			# output_name is set by setting output_filepath
			transcribe(args, model, temp_audio_filepath, media_file)

		else:
			# output_name is set by setting output_filepath
			transcribe(args, model, media_file)

	# cleanup the audio file that is no longer needed
	close(args)
	print("Done.")

	return 0

if __name__ == "__main__":
	main()
