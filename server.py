from flask import Flask, request, redirect
import telebot
import os
import json
from spotipy.oauth2 import SpotifyOAuth
from config import TELEGRAM_BOT_TOKEN, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
subscribers_file = 'subscribers.json'
app = Flask(__name__)

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

# Route to handle the Spotify OAuth callback
@app.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')  # We can pass the user's chat ID as 'state'

    if not code:
        return "Error: no code returned from Spotify", 400

    if not state:
        return "Error: no state (chat ID) returned", 400

    chat_id = state  # Use the 'state' parameter to get the user's chat ID
    spotify_oauth = SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope="user-library-read user-top-read"
    )

    # Exchange the authorization code for access and refresh tokens
    token_info = spotify_oauth.get_access_token(code)

    if token_info:
        access_token = token_info['access_token']
        refresh_token = token_info['refresh_token']

        # Load subscribers and save the tokens for the user
        subscribers = load_subscribers()
        subscribers[chat_id] = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        save_subscribers(subscribers)

        # Notify the user via Telegram that they've successfully subscribed
        bot.send_message(chat_id, "You have successfully subscribed with your Spotify account!")
        return redirect("https://t.me/LikedArtistsConcertNotifierBot", code=302)
    else:
        return "Error during token exchange", 400

if __name__ == "__main__":
    app.run(port=8888)
