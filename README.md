# Video Transcribe Tool using Open-AI's Whisper
Using OpenAI's whisper or whisper-faster and ffmpeg take a list of video and audio files and provide subtitles. These subtitle files can be used to feed it further into a LLM model and create a ML knowledge database to be queried by a user. 

## Tested on
* Windows 10 64-bit, 19045.3693
* Python 3.9.13 64-bit
* ffmpeg v4.4-full_build
* Open-AI's whisper 20231117 release (CPU-based computation)
* Whister-faster 1.0.1 with support for large-v3 model (GPU-based computation)
* CUDA 11.8
* cuDNN v8.9.6 11.x release
* nVidia GTX 1080 

## Demo

Let's get subtitles of the first 10 videos from Mr. Beast's youtube channel using CUDA

```python
python whisper-gpu.py -f https://www.youtube.com/@MrBeast/videos --playlist_end 10 -od mrbeast

Output
-----------------------SETTINGS------------------------
filename         https://www.youtube.com/@MrBeast/videos
input_dir        None
audio_filter     None
output_name      None
output_dir       mrbeast
language         en
beam_size        5
precision        auto
device           cuda
model_size       small
nproc            8
keep             False
verbose          False
quiet            False
playlist_start   None
playlist_end     10
---------------------DOWNLOADING-----------------------
```
<details>
<summary>More Output</summary>
  
```python
Parameters ['https://www.youtube.com/@MrBeast/videos', '-f', 'bestaudio[ext=m4a]/best[ext=aac]', '--merge-output-format', 'mkv', '--yes-overwrites', '--playlist-end', '10']

[youtube:tab] Extracting URL: https://www.youtube.com/@MrBeast/videos
[youtube:tab] @MrBeast/videos: Downloading webpage
[download] Downloading playlist: MrBeast - Videos
[youtube:tab] Playlist MrBeast - Videos: Downloading 10 items
[download] Downloading item 1 of 10
[youtube] Extracting URL: https://www.youtube.com/watch?v=erLbbextvlY
[youtube] erLbbextvlY: Downloading webpage
[youtube] erLbbextvlY: Downloading ios player API JSON
[youtube] erLbbextvlY: Downloading android player API JSON
[youtube] erLbbextvlY: Downloading m3u8 information
[info] erLbbextvlY: Downloading 1 format(s): 140-15
[download] Destination: 7 Days Stranded On An Island [erLbbextvlY].m4a
[download] 100% of   20.77MiB in 00:00:00 at 21.64MiB/s00
[FixupM4a] Correcting container of "7 Days Stranded On An Island [erLbbextvlY].m4a"
[download] Downloading item 2 of 10
[youtube] Extracting URL: https://www.youtube.com/watch?v=mKdjycj-7eE
[youtube] mKdjycj-7eE: Downloading webpage
[youtube] mKdjycj-7eE: Downloading ios player API JSON
[youtube] mKdjycj-7eE: Downloading android player API JSON
[youtube] mKdjycj-7eE: Downloading m3u8 information
[info] mKdjycj-7eE: Downloading 1 format(s): 140-14
[download] Destination: Stop This Train, Win a Lamborghini [mKdjycj-7eE].m4a
[download] 100% of   17.49MiB in 00:00:00 at 18.90MiB/s00
[FixupM4a] Correcting container of "Stop This Train, Win a Lamborghini [mKdjycj-7eE].m4a"
[download] Downloading item 3 of 10
[youtube] Extracting URL: https://www.youtube.com/watch?v=tWYsfOSY9vY
[youtube] tWYsfOSY9vY: Downloading webpage
[youtube] tWYsfOSY9vY: Downloading ios player API JSON
[youtube] tWYsfOSY9vY: Downloading android player API JSON
[youtube] tWYsfOSY9vY: Downloading m3u8 information
[info] tWYsfOSY9vY: Downloading 1 format(s): 140-15
[download] Destination: I Survived 7 Days In An Abandoned City [tWYsfOSY9vY].m4a
[download] 100% of   16.10MiB in 00:00:00 at 21.02MiB/s00
[FixupM4a] Correcting container of "I Survived 7 Days In An Abandoned City [tWYsfOSY9vY].m4a"
[download] Downloading item 4 of 10
[youtube] Extracting URL: https://www.youtube.com/watch?v=KOEfDvr4DcQ
[youtube] KOEfDvr4DcQ: Downloading webpage
[youtube] KOEfDvr4DcQ: Downloading ios player API JSON
[youtube] KOEfDvr4DcQ: Downloading android player API JSON
[youtube] KOEfDvr4DcQ: Downloading m3u8 information
[info] KOEfDvr4DcQ: Downloading 1 format(s): 140-14
[download] Destination: Face Your Biggest Fear To Win $800,000 [KOEfDvr4DcQ].m4a
[download] 100% of   20.42MiB in 00:00:01 at 15.06MiB/s00
[FixupM4a] Correcting container of "Face Your Biggest Fear To Win $800,000 [KOEfDvr4DcQ].m4a"
[download] Downloading item 5 of 10
[youtube] Extracting URL: https://www.youtube.com/watch?v=krsBRQbOPQ4
[youtube] krsBRQbOPQ4: Downloading webpage
[youtube] krsBRQbOPQ4: Downloading ios player API JSON
[youtube] krsBRQbOPQ4: Downloading android player API JSON
[youtube] krsBRQbOPQ4: Downloading m3u8 information
[info] krsBRQbOPQ4: Downloading 1 format(s): 140-14
[download] Destination: $1 vs $250,000,000 Private Island! [krsBRQbOPQ4].m4a
[download] 100% of   15.72MiB in 00:00:00 at 18.04MiB/s00
[FixupM4a] Correcting container of "$1 vs $250,000,000 Private Island! [krsBRQbOPQ4].m4a"
[download] Downloading item 6 of 10
[youtube] Extracting URL: https://www.youtube.com/watch?v=7ESeQBeikKs
[youtube] 7ESeQBeikKs: Downloading webpage
[youtube] 7ESeQBeikKs: Downloading ios player API JSON
[youtube] 7ESeQBeikKs: Downloading android player API JSON
[youtube] 7ESeQBeikKs: Downloading m3u8 information
[info] 7ESeQBeikKs: Downloading 1 format(s): 140-13
[download] Destination: Protect $500,000 Keep It! [7ESeQBeikKs].m4a
[download] 100% of   14.42MiB in 00:00:00 at 19.46MiB/s00
[FixupM4a] Correcting container of "Protect $500,000 Keep It! [7ESeQBeikKs].m4a"
[download] Downloading item 7 of 10
[youtube] Extracting URL: https://www.youtube.com/watch?v=K_CbgLpvH9E
[youtube] K_CbgLpvH9E: Downloading webpage
[youtube] K_CbgLpvH9E: Downloading ios player API JSON
[youtube] K_CbgLpvH9E: Downloading android player API JSON
[youtube] K_CbgLpvH9E: Downloading m3u8 information
[info] K_CbgLpvH9E: Downloading 1 format(s): 140-13
[download] Destination: I Spent 7 Days In Solitary Confinement [K_CbgLpvH9E].m4a
[download] 100% of   18.77MiB in 00:00:00 at 21.75MiB/s00
[FixupM4a] Correcting container of "I Spent 7 Days In Solitary Confinement [K_CbgLpvH9E].m4a"
[download] Downloading item 8 of 10
[youtube] Extracting URL: https://www.youtube.com/watch?v=lOKASgtr6kU
[youtube] lOKASgtr6kU: Downloading webpage
[youtube] lOKASgtr6kU: Downloading ios player API JSON
[youtube] lOKASgtr6kU: Downloading android player API JSON
[youtube] lOKASgtr6kU: Downloading m3u8 information
[info] lOKASgtr6kU: Downloading 1 format(s): 140-13
[download] Destination: I Saved 100 Dogs From Dying [lOKASgtr6kU].m4a
[download] 100% of   13.93MiB in 00:00:00 at 20.23MiB/s00
[FixupM4a] Correcting container of "I Saved 100 Dogs From Dying [lOKASgtr6kU].m4a"
[download] Downloading item 9 of 10
[youtube] Extracting URL: https://www.youtube.com/watch?v=9RhWXPcKBI8
[youtube] 9RhWXPcKBI8: Downloading webpage
[youtube] 9RhWXPcKBI8: Downloading ios player API JSON
[youtube] 9RhWXPcKBI8: Downloading android player API JSON
[youtube] 9RhWXPcKBI8: Downloading m3u8 information
[info] 9RhWXPcKBI8: Downloading 1 format(s): 140-13
[download] Destination: Survive 100 Days Trapped, Win $500,000 [9RhWXPcKBI8].m4a
[download] 100% of   25.12MiB in 00:00:01 at 21.34MiB/s00
[FixupM4a] Correcting container of "Survive 100 Days Trapped, Win $500,000 [9RhWXPcKBI8].m4a"
[download] Downloading item 10 of 10
[youtube] Extracting URL: https://www.youtube.com/watch?v=tnTPaLOaHz8
[youtube] tnTPaLOaHz8: Downloading webpage
[youtube] tnTPaLOaHz8: Downloading ios player API JSON
[youtube] tnTPaLOaHz8: Downloading android player API JSON
[youtube] tnTPaLOaHz8: Downloading m3u8 information
[info] tnTPaLOaHz8: Downloading 1 format(s): 140-13
[download] Destination: $10,000 Every Day You Survive In A Grocery Store [tnTPaLOaHz8].m4a
[download] 100% of   19.94MiB in 00:00:00 at 20.84MiB/s00
[FixupM4a] Correcting container of "$10,000 Every Day You Survive In A Grocery Store [tnTPaLOaHz8].m4a"
[download] Finished downloading playlist: MrBeast - Videos
WARNING: [youtube] Skipping player responses from android clients (got player responses for video "aQvGIIdgFDM" instead of "erLbbextvlY")
Downloaded file C:\projects\mrbeast\7 Days Stranded On An Island [erLbbextvlY].m4a
Downloaded file C:\projects\mrbeast\Stop This Train, Win a Lamborghini [mKdjycj-7eE].m4a
Downloaded file C:\projects\mrbeast\I Survived 7 Days In An Abandoned City [tWYsfOSY9vY].m4a
Downloaded file C:\projects\mrbeast\Face Your Biggest Fear To Win $800,000 [KOEfDvr4DcQ].m4a
Downloaded file C:\projects\mrbeast\$1 vs $250,000,000 Private Island! [krsBRQbOPQ4].m4a
Downloaded file C:\projects\mrbeast\Protect $500,000 Keep It! [7ESeQBeikKs].m4a
Downloaded file C:\projects\mrbeast\I Spent 7 Days In Solitary Confinement [K_CbgLpvH9E].m4a
Downloaded file C:\projects\mrbeast\I Saved 100 Dogs From Dying [lOKASgtr6kU].m4a
Downloaded file C:\projects\mrbeast\Survive 100 Days Trapped, Win $500,000 [9RhWXPcKBI8].m4a
Downloaded file C:\projects\mrbeast\$10,000 Every Day You Survive In A Grocery Store [tnTPaLOaHz8].m4a
Returned code 0
-----------------------FINISHED------------------------
Media files found 10
--------------------INITIALIZING-----------------------
Processing file: C:\projects\mrbeast\7 Days Stranded On An Island [erLbbextvlY].m4a

Detected language 'en' with probability 1.000000

Begin transcription and creating subtitle file:
-------------------------------------------------------
C:\projects\mrbeast\7 Days Stranded On An Island [erLbbextvlY].m4a  took  127.4  seconds
-------------------------------------------------------
Processing file: C:\projects\mrbeast\Stop This Train, Win a Lamborghini [mKdjycj-7eE].m4a

Detected language 'en' with probability 1.000000

Begin transcription and creating subtitle file:
-------------------------------------------------------
C:\projects\mrbeast\Stop This Train, Win a Lamborghini [mKdjycj-7eE].m4a  took  109.4  seconds
-------------------------------------------------------
Processing file: C:\projects\mrbeast\I Survived 7 Days In An Abandoned City [tWYsfOSY9vY].m4a

Detected language 'en' with probability 1.000000

Begin transcription and creating subtitle file:
-------------------------------------------------------
C:\projects\mrbeast\I Survived 7 Days In An Abandoned City [tWYsfOSY9vY].m4a  took  92.5  seconds
-------------------------------------------------------
Processing file: C:\projects\mrbeast\Face Your Biggest Fear To Win $800,000 [KOEfDvr4DcQ].m4a

Detected language 'en' with probability 1.000000

Begin transcription and creating subtitle file:
-------------------------------------------------------
C:\projects\mrbeast\Face Your Biggest Fear To Win $800,000 [KOEfDvr4DcQ].m4a  took  112.3  seconds
-------------------------------------------------------
Processing file: C:\projects\mrbeast\$1 vs $250,000,000 Private Island! [krsBRQbOPQ4].m4a

Detected language 'en' with probability 1.000000

Begin transcription and creating subtitle file:
-------------------------------------------------------
C:\projects\mrbeast\$1 vs $250,000,000 Private Island! [krsBRQbOPQ4].m4a  took  84.6  seconds
-------------------------------------------------------
Processing file: C:\projects\mrbeast\Protect $500,000 Keep It! [7ESeQBeikKs].m4a

Detected language 'en' with probability 1.000000

Begin transcription and creating subtitle file:
-------------------------------------------------------
C:\projects\mrbeast\Protect $500,000 Keep It! [7ESeQBeikKs].m4a  took  81.1  seconds
-------------------------------------------------------
Processing file: C:\projects\mrbeast\I Spent 7 Days In Solitary Confinement [K_CbgLpvH9E].m4a

Detected language 'en' with probability 1.000000

Begin transcription and creating subtitle file:
-------------------------------------------------------
C:\projects\mrbeast\I Spent 7 Days In Solitary Confinement [K_CbgLpvH9E].m4a  took  97.5  seconds
-------------------------------------------------------
Processing file: C:\projects\mrbeast\I Saved 100 Dogs From Dying [lOKASgtr6kU].m4a

Detected language 'en' with probability 1.000000

Begin transcription and creating subtitle file:
-------------------------------------------------------
C:\projects\mrbeast\I Saved 100 Dogs From Dying [lOKASgtr6kU].m4a  took  96.0  seconds
-------------------------------------------------------
Processing file: C:\projects\mrbeast\Survive 100 Days Trapped, Win $500,000 [9RhWXPcKBI8].m4a

Detected language 'en' with probability 1.000000

Begin transcription and creating subtitle file:
-------------------------------------------------------
C:\projects\mrbeast\Survive 100 Days Trapped, Win $500,000 [9RhWXPcKBI8].m4a  took  121.3  seconds
-------------------------------------------------------
Processing file: C:\projects\mrbeast\$10,000 Every Day You Survive In A Grocery Store [tnTPaLOaHz8].m4a

Detected language 'en' with probability 1.000000

Begin transcription and creating subtitle file:
-------------------------------------------------------
C:\projects\mrbeast\$10,000 Every Day You Survive In A Grocery Store [tnTPaLOaHz8].m4a  took  77.1  seconds
-------------------------------------------------------
```
</details>

```
Done.
```
Now check the `results` directory and if necessary, verify that the speech within the audio matches the subtitles. Experiment with beam size, precision and model size. 

## Usage
### Local Files
Usage on GPUs with defaults

```python
# default device is CUDA using nVidia GPU, CUDA dNN and Compute
python whisper-gpu.py -f path-to-a-media-file

# Test with CPU in case you have no CUDA device
python whisper-gpu.py -f path-to-a-media-file -d cpu

# Test using the original whisper package from OpenAI
python whisper-og.py -f path-to-a-media-file
```

If you want to transcribe videos inside a specific directory then provide an input path like so

```python
# Subtitle outputs will be placed in the same directory as the input directory
python whisper-gpu.py -i C:\projects\Videos

Found  18  files

Settings as follows:
-------------------------------------------------------
input_dir        C:\projects\Videos
filename         None
output_dir       C:\projects\Videos
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
python whisper-gpu.py -f https://www.youtube.com/watch?v=jAa58N4Jlos
```
Even youtube videos from a particular channel can be downloaded and the entire set of files transcribed by the script:
```
python whisper-gpu.py -f https://www.youtube.com/@MrBeast/videos
```
I usually place a maximum number of videos to transcribe for testing and to save time: 
```
python whisper-gpu.py -f https://www.youtube.com/@MrBeast/videos --playlist_end 10
```
Above, only 10 videos will be downloaded in audio format and transcribed. 

But wait! There's MORE

And it doesn't have to be from youtube. Youtube Downloader gets better over time and has its own reporsitory. Here it uses a soundcloud link to download a song
```
python whisper-gpu.py -f https://soundcloud.com/prznt/prznt-x-2scratch-stay
```

## Manual Downloading

### Youtube Downloader

In case you want to test a script standalone before using the whisper package. Here's the command
```bash
# not using the whisper AI or CUDA script here

# download manually the necessary file(s) and put them into a directory if needed
# -o is output filename
python download_best.py -l https://soundcloud.com/prznt/prznt-x-2scratch-stay -o projects/sick_beat

# then specify the local path into the rest of the scripts
python whisper-gpu.py -f projects/sick_beat.m4a
```

### Clarity of Recording

Checkout the various formats and quality of the files avaiallable before downloading, since this step may or may not have an impact on the performance of transcription due to level of clarity in the speech. 

For e.g. many artifacts in the audio from an old recording may impact transcription

```bash
python download_best.py -l https://soundcloud.com/prznt/prznt-x-2scratch-stay -F
```
<details>
  <summary>More Output</summary>
  
```python
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
```
</details>

```python
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

```python
# here I choose the last option which seems to have a higher TBR
python download_best.py -l https://soundcloud.com/prznt/prznt-x-2scratch-stay -f http_mp3_128

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

# transcribe this song or a recording
python whisper-gpu.py -f 'Prznt x 2Scratch - Stay [715263370].mp3'

# try different settings 
python whisper-gpu.py -f 'Prznt x 2Scratch - Stay [715263370].mp3' --model_size large
```

### Increase Robustness and Accuracy (List Supported Sizes)

Consider using a larger `beam_size` hyper-parameter, which as you may be aware increases the time to complete the transcoding. This will probably rectify any issues with spoken languages with an accent that the tiny model stsuggles with. To get supported model sizes of faster-whisper issue the command `-s` or `--model_size`. 

```python
# Call the faster-whisper API to get supported sizes in that version number
python whisper-gpu.py -s

Supported size in faster-whisper
-------------------------------------------------------
*  tiny.en
*  tiny
*  base.en
*  base
*  small.en
*  small
*  medium.en
*  medium
*  large-v1
*  large-v2
*  large-v3
*  large
*  distil-large-v2
*  distil-medium.en
*  distil-small.en
```

## Setup
### Faster-whisper
More information can be found at https://github.com/SYSTRAN/faster-whisper?tab=readme-ov-file#installation To install dependencies for whisper-gpu
<br />
<br />`pip install -r requirements.txt`

### Open-AI's whisper
More information can be found at https://github.com/openai/whisper?tab=readme-ov-file#setup. To install dependencies for whisper-og
<br />
<br />`pip install git+https://github.com/openai/whisper.git ffmpeg`



