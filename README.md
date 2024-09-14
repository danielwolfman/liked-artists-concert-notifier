# 🎵 Spotify Favorite Artists Concert Notifier Bot 🎵

This bot, [@LikedArtistsConcertNotifierBot](https://t.me/LikedArtistsConcertNotifierBot), helps users track concerts for their favorite artists based on their Spotify library and sends personalized notifications via Telegram.

## Key Features:
- **Spotify Integration**: Automatically retrieves users' favorite artists based on their Spotify liked songs and top artists.
- **Concert Data**: Fetches real-time event data using the Ticketmaster API.
- **Precise Artist Matching**: Uses Spotify `attractionId` to ensure event searches return only the specific artists, not tribute bands or loosely related events.
- **Telegram Notifications**: Sends concert notifications directly to users via [@LikedArtistsConcertNotifierBot](https://t.me/LikedArtistsConcertNotifierBot).
- **Duplicate Prevention**: Keeps track of previously notified concerts to avoid sending repeat notifications.
- **User-Specific OAuth Authentication**: Each user authenticates with their own Spotify account, and their tokens are securely managed.

## How It Works:
1. **Spotify Authentication**: Users interact with the bot to enter their Spotify API credentials via OAuth.
2. **Subscribed Notifications**: The bot periodically checks for upcoming concerts for users' favorite artists and notifies them via Telegram.
3. **Precise Search**: The bot uses the Spotify `attractionId` to ensure only exact matches are found for concerts.

---

## Getting Started

### 1. Spotify Developer App Setup:
To use Spotify's API, you must create an app on the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications).

- **Create an App** and note down your **Client ID** and **Client Secret**.
- Add a **Redirect URI**: For example, `http://localhost:8888/callback` (you'll need this for OAuth).

### 2. Ticketmaster API Setup:
Go to the [Ticketmaster Developer Portal](https://developer.ticketmaster.com/) and sign up for an account.

- Create an application from the dashboard to get your **API Key**.
- You'll use this API key to fetch concerts for specific artists.

### 3. Telegram Bot Setup:
- Open [BotFather](https://telegram.me/botfather) on Telegram and create a new bot.
- Use the following bot name: **[@LikedArtistsConcertNotifierBot](https://t.me/LikedArtistsConcertNotifierBot)**.
- Get your **Telegram Bot Token** and use it to configure the bot in the project.

---

## Configuration

### Environment Variables:

Create a `.env` file or set the following environment variables for the project:

```plaintext
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TICKETMASTER_API_KEY=your_ticketmaster_api_key
