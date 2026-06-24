import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile
from config import BOT_TOKEN
from music_downloader import download_audio
from keep_alive import keep_alive

# Loglashni yoqish
logging.basicConfig(level=logging.INFO)

# Bot va dispetcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Salom! Men Musiqa Botiman.\n"
        "Menga istalgan musiqa nomini yozing, men uni topib sizga jo'nataman!\n\n"
        "Misol uchun: <i>Yulduz Usmonova Muhabbat</i>",
        parse_mode="HTML"
    )

@dp.message(F.text)
async def handle_music_query(message: types.Message):
    query = message.text
    
    # Juda uzun so'rovlarni bloklash
    if len(query) > 100:
        await message.reply("❌ So'rov juda uzun. Iltimos, qisqaroq yozing.")
        return
        
    status_msg = await message.reply("🔎 Musiqa qidirilmoqda... Iltimos kuting.")
    
    # Yuklash
    result = await download_audio(query)
    
    if result and os.path.exists(result['file_path']):
        await status_msg.edit_text("⏳ Yuklab olinmoqda... Telegramga jo'natilyapti.")
        
        file_path = result['file_path']
        title = result['title']
        uploader = result['uploader']
        duration = result['duration']
        
        try:
            # Faylni yuborish
            audio = FSInputFile(file_path, filename=f"{title}.{file_path.split('.')[-1]}")
            
            await message.reply_audio(
                audio=audio,
                caption=f"🎵 <b>{title}</b>\n👤 {uploader}",
                title=title,
                performer=uploader,
                duration=duration,
                parse_mode="HTML"
            )
            
            # Yuborib bo'lgach status xabarni o'chirish
            await status_msg.delete()
            
        except Exception as e:
            logging.error(f"Xato yuz berdi: {e}")
            await status_msg.edit_text("❌ Faylni yuborishda xatolik yuz berdi. Balki fayl hajmi juda kattadir (50MB+).")
        finally:
            # Lokal faylni o'chirish
            if os.path.exists(file_path):
                os.remove(file_path)
    else:
        await status_msg.edit_text("❌ Kechirasiz, siz izlagan musiqa topilmadi yoki yuklashda xatolik yuz berdi.")

async def main():
    print("Bot ishga tushmoqda...")
    keep_alive()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
