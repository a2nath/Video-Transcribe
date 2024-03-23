from __future__ import unicode_literals
import os
import youtube_dl
import argparse
import subprocess
import shutil
from pathlib import Path, PurePath


global_model_bin        = "yt-dlp.exe"
global_get_best_format  = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
global_get_video_format = "bestvideo[ext=mp4]/best[ext=mp4]"
global_get_audio_format = "bestaudio[ext=m4a]/best[ext=aac]"
global_get_merge_format = 'mkv'

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

	def adjust_format(self, args):

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

		if args.output:
			self.opts += ["-o", Path(args.output_dir, args.output)]

		if args.verbose:
			self.opts += ["--verbose"]

		if args.merge:
			self.opts += ["--merge-output-format", args.merge_format]

		if args.overwrite:
			self.opts += ["--yes-overwrites"]

		if args.username:
			self.opts += ["-u", args.username]
			if args.password:
				self.opts += ["-p", args.password]

		if args.bin:
			self.model_bin = str(Path(args.bin).resolve())

	def get_youtube_vid(self):

		process = subprocess.Popen([self.model_bin] + self.opts, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

		if self.debug_flag == True:
			print(f"Starting process {process}\n")

		video_name = ""
		stdout_line = "start";

		while stdout_line:

			stdout_line_bytes = process.stdout.readline()

			# Check if stdout_line_bytes is empty, indicating the end of output
			if not stdout_line_bytes:
				stderr_line = process.stderr.readline().decode('utf-8')
				if stderr_line:
					print(stderr_line.strip())
				break

			try:
				# Attempt to decode the line as UTF-8
				stdout_line = stdout_line_bytes.decode('utf-8')
				stdout_line = stdout_line.strip()
			except UnicodeDecodeError as e:
				# Handle decoding error gracefully
				print(f"Error decoding line from stdout: {e}")
				print(f"Problematic byte sequence: {stdout_line_bytes}")
				continue

			# if just listing the formats, then stop here
			if "-F" in self.opts:
				print(stdout_line)
				continue;
			#out, err = process.communicate() #blocking process

			# Read and print the output line by line
			merger_pattern     = "[Merger] Merging formats into \""
			download_pattern   = "[download] Destination: "
			downloaded_pattern = " has already been downloaded"

			if stdout_line.startswith(merger_pattern):
				video_name = stdout_line[len(merger_pattern):-1]
				print(stdout_line)
				continue

			elif not video_name and stdout_line.startswith(download_pattern):
				video_name = stdout_line[len(download_pattern):]
				print(stdout_line)
				continue

			elif downloaded_pattern in stdout_line:
				video_name = stdout_line[len("[download] "):stdout_line.index(downloaded_pattern)]
				print(stdout_line)
				break

			print(stdout_line)

		# Wait for the process to finish
		return_code = process.wait()

		#if args.output_dir != os.getcwd():
		#	shutil.move(os.getcwd(), args.output_dir)

		if self.debug_flag == True:
			print("-------------------------------------------------------")
			print(f"Media file '{video_name}' returned code {return_code}")

		return video_name, return_code

	def run(self):

		if self.debug_flag:
			print("\nDownloaderg:")
			print("-------------------------------------------------------")
			print(f"Parameters {self.opts}\n")
		video_name, retcode = self.get_youtube_vid(self.model_bin, self.opts)

		return video_name, retcode;

	def __init__(self, args, debug = False):

		global global_model_bin
		global global_get_best_format
		global global_get_video_format
		global global_get_audio_format
		global global_get_merge_format

		self.debug_flag       = debug
		self.model_bin        = global_model_bin
		self.get_best_format  = global_get_best_format
		self.get_audio_format = global_get_audio_format
		self.get_video_format = global_get_video_format
		self.get_merge_format = global_get_merge_format
		self.opts             = []

		# parse input arguments
		self.adjust_format(args)

def main():

	parser = argparse.ArgumentParser("Downloads the best quality video from source", add_help=True)
	parser.add_argument("-l", "--url", help="URL or source of one or more videos", required=True)
	parser.add_argument("-F", "--list", help="List all formats that can be downloaded", action='store_true')
	parser.add_argument("--verbose", help="Verbose output", action='store_true')
	parser.add_argument('-k', "--keep", help="Keep intermediate files", action='store_true')
	parser.add_argument("-f", "--format", help="Format of the video to download", default=global_get_best_format)
	parser.add_argument("-u", "--username", help="Username to login with")
	parser.add_argument("-p", "--password", help="Password for the credentials. Used with username")
	parser.add_argument("-o", "--output", help="Ouput format", action='store_true')
	parser.add_argument("-d", "--output_dir", help="Ouput directory", default=os.getcwd())
	parser.add_argument("-a", "--audio_only", help="Audio only download", action='store_true')
	parser.add_argument("-v", "--video_only", help="Video only download", action='store_true')
	parser.add_argument("-b", "--bin", help="Path to the binary to choose", default=global_model_bin)
	parser.add_argument("-m", "--merge", help="Bool on whether to merge the audio and video", type=bool, default=False)
	parser.add_argument("--merge_format", help="Fomat of merging the audio and video. Default format: mkv", default=global_get_merge_format)
	parser.add_argument("--quiet", help="Debug print off", action='store_true')
	parser.add_argument("--overwrite", help="Overwrite an exising file", action='store_true')

	args = parser.parse_args()
	downloader = Download(args, debug=not args.quiet)

	# make the directory if missing
	Path(args.output_dir).mkdir(parents=True, exist_ok=True)

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
