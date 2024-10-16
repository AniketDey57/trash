import os
import asyncio
import ffmpeg
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Function to convert M4A to MP3
def convert_m4a_to_mp3(input_file: str, output_file: str):
    try:
        (
            ffmpeg
            .input(input_file)
            .output(output_file, format='mp3', audio_bitrate='320k')
            .run(overwrite_output=True)
        )
        return True
    except Exception as e:
        print(f"Error during conversion: {e}")
        return False

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Send me an M4A file and I will convert it to MP3 320 kbps!')

# Function to handle M4A file uploads
async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    audio_file = update.message.audio

    if audio_file.mime_type == 'audio/m4a':
        await update.message.reply_text('Converting your M4A file to MP3...')
        input_file = await audio_file.get_file().download()
        output_file = f"{os.path.splitext(input_file)[0]}.mp3"

        if convert_m4a_to_mp3(input_file, output_file):
            with open(output_file, 'rb') as f:
                await context.bot.send_audio(chat_id=update.effective_chat.id, audio=f)
        else:
            await update.message.reply_text('Failed to convert the file.')
        
        # Clean up files
        os.remove(input_file)
        os.remove(output_file)
    else:
        await update.message.reply_text('Please send a valid M4A file.')

# Main function to run the bot
async def main():
    app = ApplicationBuilder().token('YOUR_BOT_TOKEN').build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.AUDIO, handle_audio))

    await app.initialize()  # Initialize the app
    await app.start()  # Start the bot
    await app.run_polling()  # This will keep the bot running and handle updates

# Check if the event loop is already running and handle it
if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        if not loop.is_running():
            loop.run_until_complete(main())
        else:
            asyncio.create_task(main())  # Schedule the main coroutine if the loop is already running
    except RuntimeError:
        # If no event loop exists, create one and run the bot
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
