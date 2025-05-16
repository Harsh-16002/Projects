from flask import Flask, render_template, request, jsonify
import yt_dlp
import os
import subprocess
from pytube import Playlist
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# ✅ Check if FFmpeg is installed
def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

# ✅ Extract video links from a YouTube playlist
def extract_video_links(playlist_url):
    try:
        playlist = Playlist(playlist_url)
        return [video_url for video_url in playlist.video_urls]
    except Exception as e:
        return []

# ✅ Get available video qualities for a single video
def get_available_qualities(video_url):
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(video_url, download=False)
            formats = info.get('formats', [])

        quality_set = set()
        for f in formats:
            height = f.get('height')
            if height:
                quality_set.add(f"{height}p")

        return sorted(quality_set, key=lambda x: int(x.replace('p', '')))
    except Exception as e:
        return []

# ✅ Select best format based on quality
def get_best_format(target_height, ffmpeg_available):
    if ffmpeg_available:
        return f'bestvideo[height<={target_height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={target_height}][ext=mp4]/best'
    else:
        return f'best[height<={target_height}][ext=mp4]/best[ext=mp4]/best'

# ✅ Resumable Download Function
def download_video(url, quality, ffmpeg_available, playlist_name):
    download_folder = "static/downloads"
    playlist_folder = os.path.join(download_folder, playlist_name)
    
    if not os.path.exists(playlist_folder):
        os.makedirs(playlist_folder)

    # Get video title before downloading
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(url, download=False)
        video_title = info.get('title', 'video')
        file_path = os.path.join(playlist_folder, f"{video_title}.mp4")

    # ✅ Check if file already exists (resumable downloads)
    if os.path.exists(file_path):
        print(f"Skipping {video_title}, already downloaded.")
        return f"{video_title} (Already Downloaded)"

    ydl_opts = {
        'outtmpl': os.path.join(playlist_folder, '%(title)s.%(ext)s'),
        'format': get_best_format(int(quality.replace('p', '')), ffmpeg_available),
        'noprogress': True,
        'retries': 10,  # ✅ More retries
        'socket_timeout': 60,  # ✅ Increased timeout
        'concurrent-fragments': 10,  # ✅ Faster fragment downloads
        'external_downloader': 'aria2c',  # ✅ Use external downloader
        'external_downloader_args': ['-x', '16', '-s', '16', '-k', '1M'],  # ✅ 16 parallel connections
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return f"{video_title} (Downloaded)"
    except Exception as e:
        return f"{video_title} (Failed: {str(e)})"

@app.route('/')
def index():
    return render_template('index.html')

# ✅ Get available video qualities
@app.route('/get_qualities', methods=['POST'])
def get_qualities():
    data = request.json
    playlist_url = data.get('playlist_url')

    video_links = extract_video_links(playlist_url)
    if not video_links:
        return jsonify({"error": "No videos found in the playlist."})

    qualities = get_available_qualities(video_links[0])
    return jsonify({"qualities": qualities})

# ✅ Download the entire playlist (with resuming support)
@app.route('/download_playlist', methods=['POST'])
def download_playlist():
    data = request.json
    playlist_url = data.get('playlist_url')
    quality = data.get('quality')

    ffmpeg_available = check_ffmpeg()
    video_links = extract_video_links(playlist_url)

    if not video_links:
        return jsonify({"error": "No videos found in the playlist."})

    # ✅ Extract playlist name safely
    playlist_name = Playlist(playlist_url).title.replace(" ", "_").replace("/", "_")

    # ✅ Use multi-threading for faster downloads
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(download_video, url, quality, ffmpeg_available, playlist_name): url for url in video_links}

        results = []
        for future in futures:
            results.append(future.result())  # Wait for all downloads

    return jsonify({"message": "Download complete!", "download_path": f"/static/downloads/{playlist_name}", "results": results})

if __name__ == '__main__':
    app.run(debug=True)
