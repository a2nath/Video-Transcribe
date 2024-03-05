from __future__ import unicode_literals
import os
import youtube_dl
import argparse
import subprocess
from pathlib import Path, PurePath

model_bin = "yt-dlp.exe"
get_best_format  = "'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'"
get_video_format = "'bestvideo[ext=mp4]/best[ext=mp4]'"
get_audio_format = "'bestaudio[ext=m4a]/best[ext=aac]'"

def adjust_format(args):

	if args.list:
		opts = f" {args.url} -F"
		return opts

	merge_format = 'mkv'

	if args.audio_only:
		args.format = get_audio_format
		args.merge_format = False
	elif args.video_only:
		args.format = get_video_format
		args.merge_format = False
	else:
		args.format = get_best_format

	opts = f" {args.url} -f {args.format} -o {args.output_dir}"
	if args.merge_format:
		opts += f" --merge-output-format {merge_format}"

	return opts

def status(d):
	if d['status'] == 'downloading':
		print('Downloading video!')
	if d['status'] == 'finished':
		print('Downloaded!')


def get_youtube_vid(binary, opts):

	print([binary, opts])

	if "-F" in opts:
		stdout_line = "test";
		process = subprocess.Popen([binary, opts], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		print(f"Starting process {process}\n")

		while stdout_line:
			stdout_line = process.stdout.readline().decode('utf-8')

			if not stdout_line:
				stderr_line = process.stderr.readline().decode('utf-8')
				if stderr_line:
					print(stderr_line.strip())
				break

			print(stdout_line.strip())

		return


	process = subprocess.Popen([binary, opts], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	print(f"Starting process {process}\n")

	#out, err = process.communicate() #blocking process

	# Read and print the output line by line
	stdout_line = "";
	pattern = "[download] Destination:"
	downloaded_pattern = "already been downloaded"

	while stdout_line.find(pattern) != 0:

		stdout_line = process.stdout.readline().decode('utf-8')

		if not stdout_line:
			stderr_line = process.stderr.readline().decode('utf-8')
			if stderr_line:
				print(stderr_line.strip())
			break

		print(stdout_line.strip())
		if downloaded_pattern in stdout_line:
			return

	video_name = ""
	if stdout_line.find(pattern) == 0:
		video_name = stdout_line[len(pattern) + 1:].strip()

	out, err = process.communicate() #blocking process

	if not out:
		print(err.decode('utf-8'))
	else:
		for line in out.decode('utf-8').split('\n'):
			print(line)

	# Wait for the process to finish
	return_code = process.wait()
	print("-------------------------------------------------------")
	print(f"Video file: '{video_name}' returned code", return_code)

def main():


	parser = argparse.ArgumentParser("Downloads the best quality video from source", add_help=True)
	parser.add_argument("-u", "--url", help="URL or source of one or more videos", required=True)
	parser.add_argument("-F", "--list", help="List all formats that can be downloaded", action='store_true')
	parser.add_argument("-f", "--format", help="Format of the video to download", default=get_best_format)
	parser.add_argument("-o", "--output_dir", help="Ouput directory", default=os.getcwd())
	parser.add_argument("-a", "--audio_only", help="Audio only download")
	parser.add_argument("-v", "--video_only", help="Video only download")
	parser.add_argument("-b", "--bin", help="Path to the binary to choose", default=model_bin)
	parser.add_argument("-m", "--merge_format", help="Bool on whether to merge the audio and video to mkv", type=bool, default=True)

	args = parser.parse_args()
	opts = adjust_format(args)

	# make the directory if missing
	Path(args.output_dir).mkdir(parents=True, exist_ok=True)

	print("\nSettings as follows:")
	print("-------------------------------------------------------")

	arguments = vars(args);
	for key in arguments:
		value = getattr(args, key)
		if (key and type(value) != bool and value != None) or value == True:
			print(key, '\t', value)

	print("\nRunning:")
	print("-------------------------------------------------------")

	#print(f"Starting with opts {opts.split(' ')}\n")
	get_youtube_vid(args.bin, opts)


''
if __name__ == '__main__':
	main()
