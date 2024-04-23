import ffmpeg
import os
import argparse
from pathlib import Path, PurePath
import time
import re
import pdb

class AudioProcess:

	@staticmethod
	def valid_time(time_str):
		pattern = r'^\d{2}:\d{2}:\d{2}$'  # Regular expression pattern for xx:xx:xx format
		if not re.match(pattern, time_str):
			raise argparse.ArgumentTypeError(f"Invalid time format: {time_str}. Must be in the format xx:xx:xx")
		return time_str

	def findarg(self, args, key: str) -> bool:
		return key in args and getattr(args, key)

	def get_fullpath(self, output_dir, output_file) -> tuple[Path, str]:
		output_filepath = Path(output_file).resolve()

		if output_filepath.parent != Path(output_dir).resolve():
			output_dir = output_filepath.parent
			output_file = Path(output_file).name

		return Path(output_dir, output_file), output_dir

	def set_options(self, args):
		# ------------------------------------------------------------------
		# input options for various parameters that will go here
		if self.findarg(self.opts, 'start'):
			self.input_options['ss'] = self.opts.start

		if self.findarg(self.opts, 'end'):
			self.input_options['to'] = self.opts.end

		# no video
		self.input_options['vn'] = None

# ------------------------------------------------------------------
		# input options for various parameters that will go here
		#self.output_options['vn'] = True # Always true in this class

		if self.findarg(self.opts, 'audio_filter'):
			self.output_options['af'] = self.opts.audio_filter

		if self.findarg(self.opts, 'codec'):
			self.output_options['acodec'] = self.opts.codec

		if self.findarg(self.opts, 'bitrate'):
			self.output_options['audio_bitrate'] = self.opts.bitrate

		if self.findarg(self.opts, 'verbose'):
			self.output_options['loglevel'] = "verbose"

		if self.findarg(self.opts, 'debug'):
			self.output_options['loglevel'] = "warning"

	def set_output_dir(self, dir):
		try:
			dir = str(Path(dir).resolve(strict=False))
			Path(dir).mkdir(parents=True, exist_ok=True)
		except FileNotFoundError as e:
			print(f"dir argument error: {e}")


	# Input: Path(media_file)
	# Return: return code
	def extract_audio(self, input_filepath, output_filepath = None, overwrite = None):

		media_file = Path(input_filepath).resolve()
		output_filename = media_file.stem + "." + time.strftime("%Y%m%d-%H%M%S") + "." + self.opts.extension

		if output_filepath is not None and output_filepath:
			self.opts.output_name, self.opts.output_dir = self.get_fullpath(os.getcwd(), output_filepath)

		pdb.set_trace()
		# start evaluating here
		if self.findarg(self.opts, 'output_name') and self.findarg(self.opts, 'output_dir'):
			output_filename = Path(self.opts.output_dir, Path(self.opts.output_name).name)
			self.set_output_dir(self.opts.output_dir)

		elif self.findarg(self.opts, 'output_dir'):
			output_filename = Path(self.opts.output_dir, Path(media_file.name).stem + "." + time.strftime("%Y%m%d-%H%M%S") + "." + self.opts.extension)
			self.set_output_dir(self.opts.output_dir)

		media_file = str(media_file)
		output_filename = str(output_filename)

		assert type(media_file) == str
		assert type(output_filename) == str

		try:

			stream = ffmpeg.input(str(media_file), **self.input_options)
			stream = ffmpeg.output(stream, output_filename, **self.output_options)
			#stream = ffmpeg.run(stream)#, **self.global_options)
		except Exception as e:
			# Handle the exception here
			print("An error occurred:", e)
			exit()


		print(f"** ffmpeg compiled as {stream.compile()} **")
		# Start the subprocess
		try:
			if self.findarg(self.opts, 'overwrite'):
				out, err = ffmpeg.run(stream, capture_stdout=True, capture_stderr=True, overwrite_output=True)
			else:
				out, err = ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)

			print("FFmpeg output:", out.decode())
			print("FFmpeg error:", err.decode())
			return 0, ""

		except ffmpeg.Error as e:
			print("Error", e.stderr.decode())

	def extract_audio_list(self, list = None):
		if list is not None:
			self.media_files = list

		completed = 0
		remaining = {}

		if not self.findarg(self.opts, 'quiet'):
			print("-----------------------RUNNING-------------------------")

		for media_file in self.media_files:

			retcode, error_string = self.extract_audio(media_file)
			if retcode == 0:
				completed += 1
			else:
				remaining[media_file] = f"{retcode}: {error_string}"

		if not self.findarg(self.opts, 'quiet'):
			print("----------------------FINISHED-------------------------")

		return completed, remaining

	def __init__(self, args):
		self.media_files = []
		self.opts = args
		self.asmr_filter = ''
		self.input_options  = {}
		self.output_options = {}
		self.global_options = {}

		if not self.findarg(self.opts, 'quiet'):
			print("----------------------GET-AUDIO INIT-------------------")

		# single file as a source
		if self.findarg(self.opts, 'filename') and Path(self.opts.filename).exists():
			self.opts.filename, self.opts.output_dir = self.get_fullpath(os.getcwd(), self.opts.filename)
			self.media_files.append(str(self.opts.filename))

		# inputput_dir source
		elif self.findarg(self.opts, 'input_dir') and Path(self.opts.input_dir).exists():
			try:
				self.opts.input_dir = str(Path(self.opts.input_dir).resolve())

				if not self.findarg(self.opts, 'output_dir'):
					self.opts.output_dir = self.opts.input_dir

			except FileNotFoundError as e:
				print(f"self.opts.input_dir argument error: {e}")

			for filename in os.listdir(self.opts.input_dir):
				filename = Path(self.opts.input_dir, filename)
				if filename.is_file():
					self.media_files.append(str(filename))

		elif self.findarg(self.opts, 'input_dir'):
			raise FileNotFoundError("--input_dir parameter did not have a valid argument {self.opts.input_dir}")

		if len(self.media_files) == 0:
			print("WARNING: There were no files to process. Pass in parameters: input_filepath, output_filepath when calling extract_audio()")

		# validate the model for audio filter
		if self.findarg(self.opts, 'model'):
			try:
				self.opts.model = str(Path(self.opts.model).resolve())
				self.opts.model = self.opts.model.replace('\\', '/')
				self.asmr_filter = 'highpass=f=50,lowpass=f=18200,afftdn,dynaudnorm,loudnorm,arnndn=m={self.opts.model}'
			except FileNotFoundError as e:
				print(f"self.opts.model argument error: {e}")

		if not self.findarg(self.opts, 'quiet'):
			print(f"{self.__class__.__name__} initialized with {len(self.media_files)} files as target")

		self.set_options(args)

def main():
	parser = argparse.ArgumentParser("Generates audio of the video file as an input")
	parser.add_argument("-i", "--filename", help="Name of the media file that needs to subtitles")
	parser.add_argument("--input_dir", help="Input directory where video files are")
	parser.add_argument("-af", "--audio_filter", help="Audio or video filters to use, no spaces, just comma-separated")
	parser.add_argument("-d", "--output_dir", help="Ouput directory")
	parser.add_argument("-o", "--output_name", help="Output filename to give to the new file. Default is the [input-filename.requested-extension]")
	parser.add_argument("-x", "--extension", help="Codec to use to produce the disired extension", default="mp3")
	parser.add_argument("-m", "--model", help="Path to the RNN model to use for noise supression")
	parser.add_argument("-s", "--start", help="Start time in 00:00:00 format", type=AudioProcess.valid_time)
	parser.add_argument("-e", "--end", help="End time in 00:00:00 format", type=AudioProcess.valid_time)
	parser.add_argument("-y", "--overwrite", help="Overwrite the file if exists", action='store_true')
	parser.add_argument("-c", "--codec", help="Audio codec to use")
	parser.add_argument("-b", "--bitrate", help="Audio bitrate to use")
	parser.add_argument("-v", "--verbose", help="Verbose output", action='store_true')
	parser.add_argument("--debug", help="Only show warnings or error. Useful for condensed info when debugging", action='store_true')
	parser.add_argument("--noenc", help="Simply copy the audio component (without encoder) into a new container of the exension given. \
						Without this AAC for e.g. does not create a seek table", action='store_true')
	parser.add_argument("--quiet", help="Debug print off", action='store_true')

	args = parser.parse_args()

	if args.quiet == False:
		print("-----------------------SETTINGS------------------------")

		arguments = vars(args)
		for arg in arguments:
			print(arg, '\t', getattr(args, arg))

	ffmpeg_handler = AudioProcess(args)
	ffmpeg_handler.extract_audio_list();

	return 0

if __name__ == "__main__":
	main()
