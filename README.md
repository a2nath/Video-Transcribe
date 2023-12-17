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
Usage on GPUs with defaults
```
python whisper-gpu.py -f /path/to/file
```
or on CPU with defaults
```
python whisper-og.py -f /path/to/file
```
If you want to transcribe videos in a specific dir then provide a path like so
```
path whisper-gpu.py -i /path/to/dir 
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
## Setup
#### Faster-whisper
More information can be found at https://github.com/SYSTRAN/faster-whisper?tab=readme-ov-file#installation
<br />
<br />`pip install whisper-faster`

#### Open-AI's whisper
More information can be found at https://github.com/openai/whisper?tab=readme-ov-file#setup
<br />
<br />`pip install -U openai-whisper`


