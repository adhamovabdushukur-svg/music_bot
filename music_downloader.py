import os
import asyncio
import uuid
import yt_dlp
from config import DOWNLOADS_DIR

if not os.path.exists(DOWNLOADS_DIR):
    os.makedirs(DOWNLOADS_DIR)

def download_audio_sync(query: str):
    """
    Qidiruv so'rovi orqali YouTube'dan audioni qidiradi va yuklaydi.
    Yangi fayl yo'li, video sarlavhasi, kanali, va rasmi qaytariladi.
    """
    file_id = str(uuid.uuid4())
    output_template = os.path.join(DOWNLOADS_DIR, f"{file_id}.%(ext)s")
    
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': output_template,
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch1',
        'extract_flat': False,
        'extractor_args': {'youtube': ['player_client=android']},
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=True)
            if 'entries' in info:
                # Agar qidiruv natijasi bo'lsa
                info = info['entries'][0]
            
            # Haqiqiy kengaytmani olish
            ext = info.get('ext', 'm4a')
            file_path = os.path.join(DOWNLOADS_DIR, f"{file_id}.{ext}")
            
            return {
                "file_path": file_path,
                "title": info.get('title', 'Unknown Title'),
                "uploader": info.get('uploader', 'Unknown Artist'),
                "thumbnail": info.get('thumbnail', None),
                "duration": info.get('duration', 0)
            }
        except Exception as e:
            print(f"Error downloading {query}: {e}")
            return None

async def download_audio(query: str):
    """Sinxron yuklash funksiyasini asinxron holda chaqiradi"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, download_audio_sync, query)
