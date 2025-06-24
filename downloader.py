from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import os

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a Facebook, TikTok, or Instagram video link and I'll try to download it for you!")

def is_supported_link(url):
    return any(domain in url for domain in ["facebook.com", "fb.watch", "tiktok.com", "instagram.com", "instagr.am"])

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not is_supported_link(url):
        await update.message.reply_text("Please send a valid Facebook, TikTok, or Instagram video link.")
        return

    await update.message.reply_text("Downloading your video, please wait...")

    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'mp4/best',
        'quiet': True,
        'noplaylist': True,
        'merge_output_format': 'mp4',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if not filename.endswith('.mp4'):
                # Try to find the mp4 file
                for ext in ['mp4', 'mkv', 'webm']:
                    alt_filename = f"video.{ext}"
                    if os.path.exists(alt_filename):
                        filename = alt_filename
                        break

        if os.path.getsize(filename) > 49 * 1024 * 1024:
            await update.message.reply_text("Sorry, the downloaded video is too large to send via Telegram.")
            os.remove(filename)
            return

        with open(filename, 'rb') as video_file:
            await update.message.reply_video(video=video_file)

        os.remove(filename)
    except Exception as e:
        await update.message.reply_text(f"Failed to download video: {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token("YOURBOTTOKEN").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    app.run_polling()



