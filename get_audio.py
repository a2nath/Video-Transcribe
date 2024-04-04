import ffmpeg
import os
import argparse
from pathlib import Path, PurePath
import time
import re

class AudioProcess:

	@staticmethod
	def valid_time(time_str):
		pattern = r'^\d{2}:\d{2}:\d{2}$'  # Regular expression pattern for xx:xx:xx format
		if not re.match(pattern, time_str):
			raise argparse.ArgumentTypeError(f"Invalid time format: {time_str}. Must be in the format xx:xx:xx")
		return time_str

	def extract_audio(self):

		time.sleep(1)

		print("\nRunning:")
		print("-------------------------------------------------------")

		for media_file in self.media_files:
			output_filename = str(Path(self.opts.output_dir, media_file.stem + "." + time.strftime("%Y%m%d-%H%M%S") + "." + self.opts.extension))
			print("\tOutput file", '\t', output_filename)

			if self.opts.start and self.opts.end:
				stream = ffmpeg.input(str(media_file), ss=self.opts.start, to=self.opts.end)
			elif self.opts.start:
				stream = ffmpeg.input(str(media_file), ss=self.opts.start)
			elif self.opts.end:
				stream = ffmpeg.input(str(media_file), to=self.opts.end)
			else:
				stream = ffmpeg.input(str(media_file))

			if self.opts.audio_filter:
				stream = ffmpeg.output(stream, output_filename, af=self.opts.audio_filter)
			else:
				stream = ffmpeg.output(stream, output_filename)

			print(f"ffmpeg compiled as {stream.compile()}")
			# Start the subprocess
			try:
				if self.opts.overwrite:
					out, err = ffmpeg.run(stream, capture_stdout=True, capture_stderr=True, overwrite_output=True)
				else:
					out, err = ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
			except ffmpeg.Error as e:
			    print("FFmpeg error:", e.stderr.decode())
			else:
			    print("FFmpeg output:", out.decode())
			    print("FFmpeg error:", err.decode())

		print("\nFinished:")
		print("-------------------------------------------------------")


	def init_params(self):
		if self.opts.input_dir is None:
			self.opts.input_dir = os.getcwd()
		else:
			try:
				self.opts.input_dir = str(Path(self.opts.input_dir).resolve())
			except FileNotFoundError  as e:
				print(f"self.opts.input_dir argument error: {e}")

		if self.opts.model:
			try:
				self.opts.model = str(Path(self.opts.model).resolve())
				self.opts.model = self.opts.model.replace('\\', '/')
				self.asmr_filter = 'highpass=f=50,lowpass=f=18200,afftdn,dynaudnorm,loudnorm,arnndn=m={self.opts.model}'

			except FileNotFoundError  as e:
				print(f"self.opts.model argument error: {e}")

		if self.opts.output_dir is not None:
			try:
				self.opts.output_dir = str(Path(self.opts.output_dir).resolve(strict=False))
			except FileNotFoundError  as e:
				print(f"self.opts.output_dir argument error: {e}")


	def __init__(self, args, debug=False):
		self.input_args = ""
		self.output_args = ""
		self.media_files = []
		self.debug = debug
		self.opts = args
		self.asmr_filter = ''

		# init and check for valid paths
		self.init_params()

		if self.opts.filename is not None:
			self.opts.filename = Path(self.opts.input_dir, self.opts.filename.name)
			self.media_files.append(self.opts.filename)

		elif self.opts.input_dir is not None:
			for filename in os.listdir(self.opts.input_dir):
				filename = Path(self.opts.input_dir, filename)
				if filename.is_file():
					self.media_files.append(filename);

		if len(self.media_files) == 0:
			print("There were no files to process")
			exit(0)

		print("Found ", len(self.media_files), " files")
		if self.opts.output_dir is None:
			self.opts.output_dir = self.media_files[0].parents[0]

		# make the directory if missing
		Path(self.opts.output_dir).mkdir(parents=True, exist_ok=True)


def main():
	parser = argparse.ArgumentParser("Generates audio of the video file as an input")
	parser.add_argument("-i", "--filename", help="Name of the media file that needs to subtitles", type=argparse.FileType('r', encoding='UTF-8'))
	parser.add_argument("--input_dir", help="Input directory where video files are")
	parser.add_argument("-o", "--output_dir", help="Ouput directory")
	parser.add_argument("-x", "--extension", help="Codec to use to produce the disired extension", default="mp3")
	parser.add_argument("-af", "--audio_filter", help="Audio or video filters to use, no spaces, just comma-separated")
	parser.add_argument("-m", "--model", help="Path to the RNN model to use for noise supression")
	parser.add_argument("-s", "--start", help="Start time in 00:00:00 format", type=AudioProcess.valid_time)
	parser.add_argument("-e", "--end", help="End time in 00:00:00 format", type=AudioProcess.valid_time)
	parser.add_argument("-y", "--overwrite", help="Overwrite the file if exists", action='store_true')
	parser.add_argument("--noenc", help="Simply copy the audio component (without encoder) into a new container of the exension given. \
						Without this AAC for e.g. does not create a seek table", action='store_true')
	parser.add_argument("--quiet", help="Debug print off", action='store_true')


	args = parser.parse_args()

	if args.quiet == False:
		print("\nSettings as follows:")
		print("-------------------------------------------------------")

		arguments = vars(args)
		for arg in arguments:
			print(arg, '\t', getattr(args, arg))

	ffmpeg_handler = AudioProcess(args, debug=not args.quiet)
	ffmpeg_handler.extract_audio();

	return 0

if __name__ == "__main__":
	main()
