import os
import asyncio
import uuid
import yt_dlp
from config import DOWNLOADS_DIR
from pytubefix import Search

if not os.path.exists(DOWNLOADS_DIR):
    os.makedirs(DOWNLOADS_DIR)

def download_audio_sync(query: str):
    file_id = str(uuid.uuid4())
    
    # 1. Try PyTubeFix for YouTube (Primary)
    try:
        print(f"Searching YouTube via pytubefix for: {query}")
        s = Search(query)
        if s.videos:
            for yt in s.videos[:3]:  # Try top 3 videos
                try:
                    audio = yt.streams.get_audio_only()
                    file_path = audio.download(output_path=DOWNLOADS_DIR, filename=f"{file_id}.m4a")
                    return {
                        "file_path": file_path,
                        "title": yt.title,
                        "uploader": yt.author,
                        "thumbnail": yt.thumbnail_url,
                        "duration": int(yt.length or 0)
                    }
                except Exception as e:
                    print(f"PyTubeFix failed for {yt.title}: {e}")
                    continue
    except Exception as e:
        print(f"PyTubeFix search failed: {e}")

    # 2. Try SoundCloud via yt-dlp (Fallback)
    output_template = os.path.join(DOWNLOADS_DIR, f"{file_id}.%(ext)s")
    dl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': output_template,
        'noplaylist': True,
        'quiet': True,
    }
    
    with yt_dlp.YoutubeDL(dl_opts) as ydl_dl:
        try:
            print(f"Falling back to SoundCloud for: {query}")
            search_result = ydl_dl.extract_info(f"scsearch5:{query}", download=False)
            if search_result and 'entries' in search_result:
                for entry in search_result['entries']:
                    url = entry.get('url')
                    if not url:
                        continue
                    try:
                        info = ydl_dl.extract_info(url, download=True)
                        if not info:
                            continue
                        ext = info.get('ext', 'm4a')
                        file_path = os.path.join(DOWNLOADS_DIR, f"{file_id}.{ext}")
                        if os.path.exists(file_path):
                            return {
                                "file_path": file_path,
                                "title": info.get('title', 'Unknown Title'),
                                "uploader": info.get('uploader', 'Unknown Artist'),
                                "thumbnail": info.get('thumbnail', None),
                                "duration": int(float(info.get('duration') or 0))
                            }
                    except Exception as e:
                        print(f"Failed to download {url}: {e}")
                        continue
        except Exception as e:
            print(f"SoundCloud fallback failed: {e}")

    return None

async def download_audio(query: str):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, download_audio_sync, query)
