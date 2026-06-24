import os
import asyncio
import uuid
import yt_dlp
from config import DOWNLOADS_DIR

if not os.path.exists(DOWNLOADS_DIR):
    os.makedirs(DOWNLOADS_DIR)

def download_audio_sync(query: str):
    file_id = str(uuid.uuid4())
    output_template = os.path.join(DOWNLOADS_DIR, f"{file_id}.%(ext)s")
    
    # Faqat qidirish uchun (download=False)
    search_opts = {
        'extract_flat': True,
        'quiet': True,
        'extractor_args': {'youtube': ['player_client=android']},
    }
    
    # Yuklash uchun
    dl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': output_template,
        'noplaylist': True,
        'quiet': True,
        'extractor_args': {'youtube': ['player_client=android']},
    }

    # YouTube'dan 3 ta, SoundCloud'dan 5 ta natija qidiramiz
    search_queries = [f"ytsearch3:{query}", f"scsearch5:{query}"]
    
    with yt_dlp.YoutubeDL(search_opts) as ydl_search:
        with yt_dlp.YoutubeDL(dl_opts) as ydl_dl:
            for sq in search_queries:
                try:
                    search_result = ydl_search.extract_info(sq, download=False)
                    if not search_result or 'entries' not in search_result:
                        continue
                        
                    for entry in search_result['entries']:
                        url = entry.get('url')
                        if not url:
                            continue
                            
                        try:
                            # Har bir topilgan manzilni yuklab ko'rish
                            print(f"Trying to download: {url}")
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
                            continue # Agar DRM yoki bot protection bo'lsa, keyingisiga o'tadi
                except Exception as e:
                    print(f"Search failed for {sq}: {e}")
                    continue
                    
    return None

async def download_audio(query: str):
    """Sinxron yuklash funksiyasini asinxron holda chaqiradi"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, download_audio_sync, query)
