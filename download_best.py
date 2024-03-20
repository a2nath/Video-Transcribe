from __future__ import unicode_literals
import os
import youtube_dl
import argparse
import subprocess
import shutil
from pathlib import Path, PurePath

debug_flag       = True
model_bin        = "yt-dlp.exe"
get_best_format  = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
get_video_format = "bestvideo[ext=mp4]/best[ext=mp4]"
get_audio_format = "bestaudio[ext=m4a]/best[ext=aac]"
get_merge_format = 'mkv'

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

def adjust_format(args):

	global debug_flag

	opts = []

	if args.quiet:
		debug_flag = False

	if args.list:
		opts += ["-F", args.url]
		return opts

	if args.audio_only:
		args.format = get_audio_format
		args.merge = False
	elif args.video_only:
		args.format = get_video_format
		args.merge = False


	opts = [args.url, "-f", args.format]

	if args.merge:
		opts += ["--merge-output-format", args.merge_format]

	if args.keep:
		opts += ["-k"]

	if args.verbose:
		opts += ["--verbose"]

	if args.overwrite:
		opts += ["--yes-overwrites"]

	return opts

def status(d):
	if d['status'] == 'downloading':
		print('Downloading video!')
	if d['status'] == 'finished':
		print('Downloaded!')


def get_youtube_vid(binary, opts):

	global debug_flag

	process = subprocess.Popen([model_bin] + opts, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	if debug_flag == True:
		print(f"Starting process {process}\n")

	video_name = ""

	stdout_line = "start";
	while stdout_line:

		stdout_line = process.stdout.readline()

		if not stdout_line:
			stderr_line = process.stderr.readline().decode('utf-8')
			if stderr_line:
				print(stderr_line.strip())
			break

		# if just listing the formats, then stop here
		if "-F" in opts:
			print(stdout_line.decode('utf-8').strip())
			continue;
		#out, err = process.communicate() #blocking process

		# Read and print the output line by line
		merger_pattern     = "[Merger] Merging formats into \""
		download_pattern   = "[download] Destination: "
		downloaded_pattern = " has already been downloaded"

		# Convert stdout_line to bytes
		stdout_line = stdout_line.decode('utf-8').strip()

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

	return video_name, return_code

def main():

	parser = argparse.ArgumentParser("Downloads the best quality video from source", add_help=True)
	parser.add_argument("-u", "--url", help="URL or source of one or more videos", required=True)
	parser.add_argument("-F", "--list", help="List all formats that can be downloaded", action='store_true')
	parser.add_argument("--verbose", help="Verbose output", action='store_true')
	parser.add_argument('-k', "--keep", help="Keep intermediate files", action='store_true')
	parser.add_argument("-f", "--format", help="Format of the video to download", default=get_best_format)
	parser.add_argument("-o", "--output_dir", help="Ouput directory", default=os.getcwd())
	parser.add_argument("-a", "--audio_only", help="Audio only download", action='store_true')
	parser.add_argument("-v", "--video_only", help="Video only download", action='store_true')
	parser.add_argument("-b", "--bin", help="Path to the binary to choose", default=model_bin)
	parser.add_argument("-m", "--merge", help="Bool on whether to merge the audio and video", type=bool, default=False)
	parser.add_argument("--merge_format", help="Fomat of merging the audio and video. Default format: mkv", default=get_merge_format)
	parser.add_argument("--quiet", help="Debug print off", action='store_true')
	parser.add_argument("--overwrite", help="Overwrite an exising file", action='store_true')

	args = parser.parse_args()
	opts = adjust_format(args)

	# make the directory if missing
	Path(args.output_dir).mkdir(parents=True, exist_ok=True)

	print("\nSettings as follows:")
	print("-------------------------------------------------------")

	arguments = vars(args);
	for key in arguments:
		value = getattr(args, key)
		if (key and type(value) != bool and value != None) or type(value) == bool:
			print(key, '\t', value)

	print("\nRunning:")
	print("-------------------------------------------------------")

	#print(f"Starting with opts {opts.split(' ')}\n")
	video_name, retcode = get_youtube_vid(args.bin, opts)
	print("-------------------------------------------------------")
	print(f"Video file: '{video_name}' returned code", retcode)


''
if __name__ == '__main__':
	main()
