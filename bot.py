import telebot
import os
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import TELEGRAM_BOT_TOKEN, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
subscribers_file = 'subscribers.json'

# Load subscribers from file
def load_subscribers():
    if os.path.exists(subscribers_file):
        with open(subscribers_file, 'r') as file:
            return json.load(file)
    return {}

# Save subscribers to file
def save_subscribers(subscribers):
    with open(subscribers_file, 'w') as file:
        json.dump(subscribers, file, indent=4)

# Spotify authentication handler
def get_spotify_oauth(chat_id):
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope="user-library-read user-top-read",
        state=str(chat_id)  # Pass the chat ID as state
    )

# Start command to welcome users
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to Liked Artists Concert Notifier! Use /subscribe to link your Spotify account.")

# Subscribe command to initiate OAuth flow
@bot.message_handler(commands=['subscribe'])
def subscribe(message):
    chat_id = message.chat.id

    # Generate the Spotify OAuth URL with chat ID as state
    spotify_oauth = get_spotify_oauth(chat_id)
    auth_url = spotify_oauth.get_authorize_url()

    # Send the auth link to the user
    bot.reply_to(message, f"Please authorize the app using the following link:\n{auth_url}")

# Start polling the bot
bot.polling()
