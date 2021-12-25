# Streaming Module

**How to stream**  

1. Generate m3u8 and ts files. Can be done using the run.sh script for Linux or mediastreamsegmenter and tsrecompressor Apple commands for Mac.

2. Run the upload.py python script.
	Usage: `python upload.py <path>`
	`<path>`: the directory containing the m3u8 and ts files. Defaults to the current working directory if nothing is given.
	Make sure to only have one m3u8 file.
	To change the streaming_id, go in the file and update the ``streaming_id`` variable. This defaults to `'672ef79b4d0a4805bc529d1ae44bc26b'` on download.

3. Display the video using a <video\> tag. Example in testing/streaming.html. The m3u8 file is located at `https://altoponix-cdn.sfo3.digitaloceanspaces.com/streaming/<streaming_id>/master.m3u8`