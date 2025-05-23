from __future__ import unicode_literals
import sys
import os
import youtube_dl
import argparse
import subprocess
import shutil
from pathlib import Path, PurePath
import timeit
import pdb
import io
import sys

default_model_bin        = "yt-dlp.exe"
default_get_best_format  = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
default_get_video_format = "bestvideo[ext=mp4]/best[ext=mp4]"
default_get_audio_format = "bestaudio[ext=m4a]/best[ext=aac]"
default_get_merge_format = 'mkv'

class Download:

	# print unicode characters instead of ascii
	#def printuni(text):
	#
	#	stdout_bytes = text.encode('utf-8')
	#	print(f"bytes: {stdout_bytes}")
	#
	#	idxlist = []
	#	for idx, byte_value in enumerate(stdout_bytes):
	#		print(byte_value)
	#		if byte_value < 32 or byte_value > 126:
	#			# Non-printable character found
	#			idxlist.append(idx)
	#
	#	print(f'size {idxlist}')
	#
	#	#print(c, end="") for idx, c in enumerate(stdout_bytes) if idx not in idxlist else print(ord(c), end="")
	#
	#	for idx, c in enumerate(text):
	#		if idx not in idxlist:
	#			print(f'{c}', end="")
	#		else:
	#			print(ord(c), end="")
	#
	#	print("")

	# Input: str:output_dir, str:output_file
	# Return: Path:output_dir/output_file
	# Info: if output_file has a path, it overrides output_dir

	def findarg(self, args, key: str) -> bool:
		return key in args and getattr(args, key)

	def get_fullpath(self, output_dir, output_file) -> tuple[Path, str]:
		output_filepath = Path(output_file).resolve()

		if output_filepath.parent != Path(output_dir).resolve():
			output_dir = output_filepath.parent
			output_file = Path(output_file).name

		return Path(output_dir, output_file), output_dir

	def adjust_format(self, args):

		try:
			if self.findarg(args, 'bin'):
				self.model_bin = str(Path(args.bin).resolve())
		except FileNotFoundError as e:
			print(e)

		if self.findarg(args, 'list'):
			self.opts += ["-F", args.url]
			return

		if self.findarg(args, 'audio_only'):
			args.format = self.get_audio_format
			args.merge = False
		elif self.findarg(args, 'video_only'):
			args.format = self.get_video_format
			args.merge = False

		self.opts = [args.url, "-f", args.format]

		if self.findarg(args, 'keep'):
			self.opts += ["-k"]

		if self.findarg(args, 'output_name'):
			self.filepath, self.output_dir = self.get_fullpath(self.output_dir, args.output_name)
			Path(self.output_dir).mkdir(parents=True, exist_ok=True)

		elif self.findarg(args, 'output_dir'):
			self.output_dir = Path(args.output_dir).resolve()
			Path(self.output_dir).mkdir(parents=True, exist_ok=True)

			# need this for proper handle to file(s)
			self.opts += ["--restrict-filenames"]


		if self.findarg(args, 'verbose'):
			self.opts += ["--verbose"]

		if 'merge' in args and args.merge:
			self.opts += ["--merge-output-format", args.merge[0]]
		elif 'merge' in args:
			self.opts += ["--merge-output-format", self.get_merge_format]

		if self.findarg(args, 'overwrite'):
			self.opts += ["--yes-overwrites"]

		if self.findarg(args, 'username'):
			self.opts += ["-u", args.username]
			if self.findarg(args, 'password'):
				self.opts += ["-p", args.password]

		if self.findarg(args, 'playlist_start'):
			self.opts += ["--playlist-start", args.playlist_start]

		if self.findarg(args, 'playlist_end'):
			self.opts += ["--playlist-end", args.playlist_end]

		if self.findarg(args, 'audio_format'):
			self.opts += ["--extract-audio", "--audio-format", args.audio_format]

		if self.findarg(args, 'restrict_filenames'):
			self.opts += ["--restrict-filenames"]

		if self.findarg(args, 'timeout'):
			self.timeout = args.timeout

	# Input: filename to use for output if using externally
	# Return: [list of filenames] that were processed, and [retcode]
	def get_youtube_vid(self, filepath = None):
		if filepath:
			self.filepath, self.output_dir = self.get_fullpath(self.output_dir, filepath)
			Path(self.output_dir).mkdir(parents=True, exist_ok=True)

		if self.filepath:
			self.opts += ["-o", str(self.filepath)]

		process = subprocess.Popen([self.model_bin] + self.opts, encoding="utf8", stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)

		if self.debug_flag == True:
			print(f"Parameters: {self.opts}\n")

		media_list = []
		output_file = ''
		start_time = timeit.default_timer()

		while True:
			stdout_line_str = process.stdout.readline()
			if not stdout_line_str and process.poll() is not None:
				break

			elif not stdout_line_str:
				while True:
					stdout_line_str = process.stderr.readline()

					if not stdout_line_str and process.poll() is not None:
						break

					if stdout_line_str:
						print(stdout_line_str.rstrip())
					break

			try:
				stdout_line_str = stdout_line_str.rstrip()
			except UnicodeDecodeError as e:
				# Handle decoding error gracefully
				print(f"Error decoding line from stdout: {e}")
				print(f"Problematic byte sequence: {stdout_line_str}")
				continue
			except KeyboardInterrupt:
				process.kill()
				outs, errs = process.communicate(timeout = 60)
				print("----------------------KILLED---------------------------")
				print(f"Process interrupted with media list {media_list}\nouts = {outs.decode('utf-8').rstrip()}\nerrs = {errs.decode('utf-8').rstrip()}")

			# if just listing the formats, then stop here
			if "-F" in self.opts:
				print(stdout_line_str, flush=True)
				continue;
			#out, err = process.communicate() #blocking process

			# Read and print the output line by line
			merger_pattern     = "[Merger] Merging formats into \""
			download_pattern   = "[download] Destination: "
			post_audio_fix_pattern   = "[ExtractAudio] Destination: "
			downloaded_pattern = " has already been downloaded"

			if stdout_line_str:
				if stdout_line_str.startswith(merger_pattern):
					output_file = stdout_line_str[len(merger_pattern):-1]

				elif stdout_line_str.startswith(post_audio_fix_pattern):
					output_file = stdout_line_str[len(post_audio_fix_pattern):]

				elif output_file == '' and stdout_line_str.startswith(download_pattern):
					output_file = stdout_line_str[len(download_pattern):]

				elif output_file == '' and downloaded_pattern in stdout_line_str:
					output_file = stdout_line_str[len("[download] "):stdout_line_str.index(downloaded_pattern)]

				if output_file and 'Extracting URL:' in stdout_line_str:
					media_list.append(output_file)
					output_file = ''

				print(stdout_line_str, flush=True)

			if self.timeout is not None and float(timeit.default_timer() - start_time) > float(self.timeout):
				process.kill()
				outs, errs = process.communicate(timeout = 60)
				print("----------------------KILLED---------------------------")
				print(f"Process timed out after {self.timeout} seconds\nouts = {outs.decode('utf-8').rstrip()}\nerrs = {errs.decode('utf-8').rstrip()}")


		if output_file and output_file not in media_list:
			media_list.append(output_file)

		# Wait for the process to finish
		if self.timeout is not None:
			outs, errs  = process.communicate(timeout = self.timeout)
		else:
			outs, errs  = process.communicate()
		return_code = process.returncode

		try:
			if media_list and self.output_dir != Path(media_list[0]).parent.resolve():
				for index in range(len(media_list)):

					output_file = media_list[index]
					dst = shutil.move(output_file, str(Path(self.output_dir, Path(output_file).resolve().name)))

					# change the item in the list
					media_list[index] = dst

			elif not media_list:
				raise Exception(f"Nothing to process\nouts = {outs.decode('utf-8').rstrip()}\nerrs = {errs.decode('utf-8').rstrip()}")

		except (shutil.Error, OSError) as e:
			print("Error moving file:", e)

		except Exception as e:
			print(e)

		if self.debug_flag == True:
			for file in media_list:
				print(f"Downloaded file {file}")
			print(f"Returned code {return_code}")
			print("-----------------------FINISHED------------------------")

		return media_list, return_code

	def run(self, filepath = None):

		if self.debug_flag:
			print("---------------------DOWNLOADING-----------------------")

		# download the media file from the internet
		video_names, retcode = self.get_youtube_vid(filepath)

		return video_names, retcode;

	def __init__(self, args, debug = False):

		global default_model_bin
		global default_get_best_format
		global default_get_video_format
		global default_get_audio_format
		global default_get_merge_format

		# validate the executatable
		if shutil.which(default_model_bin) is not None:
			self.debug_flag       = debug
			self.model_bin        = default_model_bin
			self.get_best_format  = default_get_best_format
			self.get_audio_format = default_get_audio_format
			self.get_video_format = default_get_video_format
			self.get_merge_format = default_get_merge_format
			self.opts             = []
			self.output_dir       = os.getcwd()
			self.filepath         = ''
			self.timeout          = None
		else:
			raise FileNotFoundError(f"Executable file has a problem or does not exist {default_model_bin}")

		# parse input arguments
		self.adjust_format(args)

def main():

	parser = argparse.ArgumentParser("Downloads the best quality video from source", add_help=True)
	parser.add_argument("-l", "--url", help="URL or source of one or more videos", required=True)
	parser.add_argument("-F", "--list", help="List all formats that can be downloaded", action='store_true')
	parser.add_argument("--verbose", help="Verbose output", action='store_true')
	parser.add_argument('-k', "--keep", help="Keep intermediate files", action='store_true')
	parser.add_argument("-f", "--format", help="Format of the video to download", default=default_get_best_format)
	parser.add_argument("-u", "--username", help="Username to login with")
	parser.add_argument("-p", "--password", help="Password for the credentials. Used with username")
	parser.add_argument("-o", "--output_name", help="Ouput filename")
	parser.add_argument("-od", "--output_dir", help="Ouput directory", default=os.getcwd())
	parser.add_argument("-a", "--audio_only", help="Audio only download", action='store_true')
	parser.add_argument("-v", "--video_only", help="Video only download", action='store_true')
	parser.add_argument("-b", "--bin", help="Path to the binary to choose")
	parser.add_argument("-m", "--merge", help="Whether to merge the audio and video. Default format: mkv", nargs='*')
	parser.add_argument("--quiet", help="Debug print off", action='store_true')
	parser.add_argument("--overwrite", help="Overwrite an exising file", action='store_true')
	parser.add_argument("--timeout", help="Amount of time to wait for the download to finish (seconds)")
	parser.add_argument("--playlist_start", help="Starting position from a list of media, to start downloading from")
	parser.add_argument("--playlist_end", help="Ending position from a list of media, to stop downloading at")
	parser.add_argument("--audio_format", help="Specify the audio format to use in post-processing", action='store_true')
	parser.add_argument("--restrict_filenames", help="Restrict filenames to only ASCII characters, and avoid '&' and spaces in filenames", action='store_true')

	args = parser.parse_args()
	downloader = Download(args, debug=not args.quiet)

	if not args.quiet:

		print("-----------------------SETTINGS------------------------")

		arguments = vars(args);
		for key in arguments:
			value = getattr(args, key)
			if (key and type(value) != bool and value != None) or type(value) == bool:
				print(key, '\t', value)

		print("---------------------DOWNLOADING-----------------------")

	downloader.get_youtube_vid()


if __name__ == '__main__':
	main()
