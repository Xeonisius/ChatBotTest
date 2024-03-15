from telegram import Update
from typing import Final
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackContext, Application
import os
from pydub import AudioSegment
import cv2
from firebase_admin import credentials, initialize_app, storage

TOKEN: Final = 'Bot_Token'
BOT_USERNAME: Final = '@bot_link'
user_audio_counters = {}

# Initialize Firebase Admin
cred = credentials.Certificate("path/to/your/firebase-adminsdk.json")
initialize_app(cred, {'storageBucket': 'your-project-id.appspot.com'})

# Function to upload a file
def upload_file_to_firebase(file_path, bucket_folder, file_name):
    bucket = storage.bucket()
    blob = bucket.blob(f'{bucket_folder}/{file_name}')
    blob.upload_from_filename(file_path)
    os.remove(file_path)
    return blob.public_url

# Function for /start command
async def start_command(update: Update, context: CallbackContext):
    await update.message.reply_text("I'm a bot, please send me an audio message or a photo!")

# Function for converting and uploading audio messages on drive
async def audio_handler(update: Update, context: CallbackContext):
    global user_audio_counters
    user_id = update.message.from_user.id 
    audio_message = update.message.voice
    if audio_message:
        if user_id not in user_audio_counters:
            user_audio_counters[user_id] = 0
        # Get the file associated with the audio message
        audio_file = await context.bot.get_file(audio_message.file_id) 
        # Form the file path using the counter for naming
        ogg_file_path = f"./audio_message_{user_audio_counters[user_id]}.ogg"
        # Download the audio file
        await audio_file.download_to_drive(ogg_file_path)
        # Convert audio to WAV format
        wav_file_path = ogg_file_path.replace('.ogg', '.wav')
        audio = AudioSegment.from_file(ogg_file_path)
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(wav_file_path, format="wav")   
        # Delete the original OGG file as we only want to keep the WAV version
        os.remove(ogg_file_path)
        # Upload the file to the Firebase
        upload_file_to_firebase(wav_file_path, f'audio/{update.message.from_user.id}', f"audio_message_{user_audio_counters[user_id]}.wav")
        await update.message.reply_text(f"Audio saved as audio_message_{user_audio_counters[user_id]}.")
        # Update the counter
        user_audio_counters[user_id] += 1

# Function for recognising faces on photo and uploading it on drive
async def photo_handler(update: Update, context: CallbackContext):
    photo = update.message.photo[-1]
    if photo:
        photo_file = await context.bot.get_file(photo.file_id)
        # Form the file path
        photo_file_path = f"./{update.message.from_user.id}_photo_{update.message.message_id}.jpg"
        # Download the photo
        await photo_file.download_to_drive(photo_file_path)
        # Check for the face in the foto
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        image = cv2.imread(photo_file_path)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray_image, 1.1, 4)
        if len(faces) > 0:
            await update.message.reply_text("Photo with face saved.")
            upload_file_to_firebase(photo_file_path, 'photos', f"{photo.file_id}.jpg")
        else:
            # If no face is detected, delete the photo
            os.remove(photo_file_path)
            await update.message.reply_text("No face detected, photo not saved.")

# Error handling            
async def error(update: Update, context: CallbackContext):
    print(f'Update {update} caused error {context.error}')

# Putting the bot together
if __name__ == '__main__':
    print("Starting bot...")
    app = Application.builder().token(TOKEN).build()
    # Reply to command "start", voice message or photo
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.VOICE, audio_handler))
    
    app.add_error_handler(error)
    
    print("Polling...")
    app.run_polling(poll_interval = 3)
