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
	def get_fullpath(self, output_dir, output_file):
		output_filepath = Path(output_file).resolve()

		if output_filepath.parent != Path(output_dir).resolve():
			output_filepath.parent.mkdir(parents=True, exist_ok=True)
			output_dir = output_filepath.parent
			output_file = Path(output_file).name

		return Path(output_dir, output_file)

	def adjust_format(self, args):

		try:
			if args.bin:
				self.model_bin = str(Path(args.bin).resolve())
		except FileNotFoundError as e:
			print(e)

		if args.list:
			self.opts += ["-F", args.url]
			return

		if args.audio_only:
			args.format = self.get_audio_format
			args.merge = False
		elif args.video_only:
			args.format = self.get_video_format
			args.merge = False

		self.opts = [args.url, "-f", args.format]

		if args.keep:
			self.opts += ["-k"]

		if args.output_dir:
			self.output_dir = args.output_dir

		if args.output_name:
			self.filepath = self.get_fullpath(self.output_dir, args.output_name)

		if args.verbose:
			self.opts += ["--verbose"]

		if args.merge is not None and args.merge:
			self.opts += ["--merge-output-format", args.merge[0]]
		elif args.merge is not None:
			self.opts += ["--merge-output-format", self.get_merge_format]

		if args.overwrite:
			self.opts += ["--yes-overwrites"]

		if args.username:
			self.opts += ["-u", args.username]
			if args.password:
				self.opts += ["-p", args.password]

		if args.playlist_start:
			self.opts += ["--playlist-start", args.playlist_start]

		if args.playlist_end:
			self.opts += ["--playlist-end", args.playlist_end]

		if args.timeout is not None:
			self.timeout = args.timeout

	# Input: filename to use for output if using externally
	# Return: [list of filenames] that were processed, and [retcode]
	def get_youtube_vid(self, filepath = None):
		if filepath:
			self.filepath = self.get_fullpath(self.output_dir, filepath)

		if self.filepath:
			self.opts += ["-o", str(self.filepath)]

		process = subprocess.Popen([self.model_bin] + self.opts, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)

		if self.debug_flag == True:
			print(f"Starting with parameters: {self.opts}\n")

		media_list = []
		output_file = ''
		start_time = timeit.default_timer()

		while True:
			stdout_line_bytes = process.stdout.readline()
			if not stdout_line_bytes and process.poll() is not None:
				break

			elif not stdout_line_bytes:
				stderr_line = process.stderr.readline()
				if stderr_line:
					print(stderr_line.decode('utf-8').rstrip())
				break

			try:
				# Attempt to decode the line as UTF-8
				stdout_line = stdout_line_bytes.decode('utf-8')
				stdout_line = stdout_line.rstrip()
			except UnicodeDecodeError as e:
				# Handle decoding error gracefully
				print(f"Error decoding line from stdout: {e}")
				print(f"Problematic byte sequence: {stdout_line_bytes}")
				continue
			except KeyboardInterrupt:
				process.kill()
				outs, errs = process.communicate(timeout = 60)
				print("----------------------KILLED---------------------------")
				print(f"Process interrupted with media list {media_list}\nouts = {outs.decode('utf-8').rstrip()}\nerrs = {errs.decode('utf-8').rstrip()}")

			# if just listing the formats, then stop here
			if "-F" in self.opts:
				print(stdout_line, flush=True)
				continue;
			#out, err = process.communicate() #blocking process

			# Read and print the output line by line
			merger_pattern     = "[Merger] Merging formats into \""
			download_pattern   = "[download] Destination: "
			downloaded_pattern = " has already been downloaded"

			if stdout_line:
				if stdout_line.startswith(merger_pattern):
					output_file = stdout_line[len(merger_pattern):-1]

				elif output_file == '' and stdout_line.startswith(download_pattern):
					output_file = stdout_line[len(download_pattern):]

				elif output_file == '' and downloaded_pattern in stdout_line:
					output_file = stdout_line[len("[download] "):stdout_line.index(downloaded_pattern)]

				if output_file and 'Extracting URL:' in stdout_line:
					media_list.append(output_file)
					output_file = ''

				print(stdout_line, flush=True)

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
			if media_list and self.output_dir != Path(media_list[0]).resolve().parent:
				for output_file in media_list:
					shutil.move(output_file, str(Path(self.output_dir, Path(output_file).resolve().name)))
			else:
				raise Exception(f"Nothing to process\nouts = {outs.decode('utf-8').rstrip()}\nerrs = {errs.decode('utf-8').rstrip()}")
		except Exception as e:
			print(e)

		if self.debug_flag == True:
			print("-----------------------FINISHED------------------------")
			print(f"Media file(s) '{media_list}' returned code {return_code}")

		return media_list, return_code

	def run(self, filepath = None):

		if self.debug_flag:
			print("\nDownloading:")
			print("-------------------------------------------------------")
			print(f"Parameters {self.opts}\n")

		# download the media file from the internet
		video_name, retcode = self.get_youtube_vid(filepath)

		return video_name, retcode;

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
	parser.add_argument("-o", "--output_name", help="Ouput format")
	parser.add_argument("-d", "--output_dir", help="Ouput directory", default=os.getcwd())
	parser.add_argument("-a", "--audio_only", help="Audio only download", action='store_true')
	parser.add_argument("-v", "--video_only", help="Video only download", action='store_true')
	parser.add_argument("-b", "--bin", help="Path to the binary to choose")
	parser.add_argument("-m", "--merge", help="Whether to merge the audio and video. Default format: mkv", nargs='*')
	parser.add_argument("--quiet", help="Debug print off", action='store_true')
	parser.add_argument("--overwrite", help="Overwrite an exising file", action='store_true')
	parser.add_argument("--timeout", help="Amount of time to wait for the download to finish (seconds)")
	parser.add_argument("--playlist_start", help="Starting position from a list of media, to start downloading from")
	parser.add_argument("--playlist_end", help="Ending position from a list of media, to stop downloading at")

	args = parser.parse_args()
	downloader = Download(args, debug=not args.quiet)

	# make the directory if missing
	Path(args.output_dir).resolve().mkdir(parents=True, exist_ok=True)

	if not args.quiet:

		print("\nSettings as follows:")
		print("-------------------------------------------------------")

		arguments = vars(args);
		for key in arguments:
			value = getattr(args, key)
			if (key and type(value) != bool and value != None) or type(value) == bool:
				print(key, '\t', value)

		print("\nDownloader:")
		print("-------------------------------------------------------")

	downloader.get_youtube_vid()


if __name__ == '__main__':
	main()
