# Video Transcribe Tool using Open-AI's Whisper
Using OpenAI's whisper or whisper-faster and ffmpeg take a list of video and audio files and provide subtitles

## Tested on
* Windows 10 64-bit, 19045.3693
* Python 3.9.13 64-bit
* ffmpeg v4.4-full_build
* Open-AI's whisper 20231117 release (CPU-based computation)
* Whister-faster 0.10.0 with support for large-v3 model (GPU-based computation)
* CUDA 11.8
* cuDNN v8.9.6 11.x release
* nVidia GTX 1080 

## Usage
### Local Files
Usage on GPUs with defaults
```
python whisper-gpu.py -f /path/to/local/file
```
or on CPU with defaults
```
python whisper-og.py -f /path/to/local/file
```
If you want to transcribe videos in a specific dir then provide a path like so
```
path whisper-gpu.py -i /path/to/local/dir 
```
or for current directory, copy the script to that dir and provide a path like so
```
path whisper-gpu.py -i .
Found  18  files

Settings as follows:
-------------------------------------------------------
input_dir        .
filename         None
output_dir       C:\Users\<username>\Videos
language         en
beam_size        5
precision        auto
device           cuda
model_size       small
nproc            8

Initializing:
-------------------------------------------------------
...
```
### Internet Files 
If you want to transcribe videos and audio from the internet, depending on whether the yt-dl (Youtube Downloader) can download them as intermediate files, you can also provide a URL: 
```
path whisper-gpu.py -f https://www.youtube.com/watch?v=jAa58N4Jlos
```
and it doesn't have to be from youtube. Youtube Downloader gets better over time and has its own reporsitory. Here it uses a soundcloud link to download a song
```
path whisper-gpu.py -f https://soundcloud.com/prznt/prznt-x-2scratch-stay
```

## Standalone Testing

### Youtube Downloader

In case you want to test a script standalone before using the whisper package. Here's the command
```
python download_best.py -u https://soundcloud.com/prznt/prznt-x-2scratch-stay
```
Checkout the various formats and quality of the files avaiallable before downloading. Note that this may not have an impact on the performance of transcription.
```
python download_best.py -u https://soundcloud.com/prznt/prznt-x-2scratch-stay -F

Settings as follows:
-------------------------------------------------------
url            https://soundcloud.com/prznt/prznt-x-2scratch-stay
list           True
verbose        False
keep           False
format         bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best
output_dir     C:\Users\<username>\Videos
audio_only     False
video_only     False
bin            yt-dlp.exe
merge          False
merge_format   mkv
quiet          False
overwrite      False

Running:
-------------------------------------------------------
Starting process <Popen: returncode: None args: ['yt-dlp.exe', '-F', 'https://soundcloud.com/...>

[soundcloud] Extracting URL: https://soundcloud.com/prznt/prznt-x-2scratch-stay
[soundcloud] prznt/prznt-x-2scratch-stay: Downloading info JSON
[soundcloud] 715263370: Downloading JSON metadata
[soundcloud] 715263370: Downloading JSON metadata
[soundcloud] 715263370: Downloading JSON metadata
[info] Available formats for 715263370:
ID           EXT  RESOLUTION | FILESIZE  TBR PROTO | VCODEC     ACODEC   ABR
----------------------------------------------------------------------------
hls_opus_64  opus audio only | ~1.39MiB  64k m3u8  | audio only unknown  64k
hls_mp3_128  mp3  audio only | ~2.78MiB 128k m3u8  | audio only unknown 128k
http_mp3_128 mp3  audio only | ~2.78MiB 128k http  | audio only unknown 128k
-------------------------------------------------------
Video file: '' returned code 0
```
And when downloading an intermediate file before the transcription, the output looks like:
```
Running:
-------------------------------------------------------
Starting process <Popen: returncode: None args: ['yt-dlp.exe', 'https://soundcloud.com/prznt/...>

[soundcloud] Extracting URL: https://soundcloud.com/prznt/prznt-x-2scratch-stay
[soundcloud] prznt/prznt-x-2scratch-stay: Downloading info JSON
[soundcloud] 715263370: Downloading JSON metadata
[soundcloud] 715263370: Downloading JSON metadata
[soundcloud] 715263370: Downloading JSON metadata
[info] 715263370: Downloading 1 format(s): http_mp3_128
[download] Destination: Prznt x 2Scratch - Stay [715263370].mp3
[download] 100% of    2.71MiB in 00:00:00 at 6.74MiB/s:00
-------------------------------------------------------
Media file: 'Prznt x 2Scratch - Stay [715263370].mp3' returned code 0
```

## Setup
### Faster-whisper
More information can be found at https://github.com/SYSTRAN/faster-whisper?tab=readme-ov-file#installation
<br />
<br />`pip install whisper-faster`

### Open-AI's whisper
More information can be found at https://github.com/openai/whisper?tab=readme-ov-file#setup
<br />
<br />`pip install -U openai-whisper`

### Youtube Downloader
To validate URLs when using whisper script to download files from the internet and transcribe in one step.
<br />
<br />`pip install validator`



