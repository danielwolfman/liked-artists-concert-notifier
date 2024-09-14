import logging
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy import SpotifyException
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SpotifyClient:
    def __init__(self, access_token, refresh_token):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.sp = spotipy.Spotify(auth=self.access_token)

    # Fetch user's favorite artists (liked songs and top artists)
    def get_favorite_artists(self):
        try:
            artist_counts = {}

            # Get liked songs
            results = self.sp.current_user_saved_tracks(limit=50)
            while results:
                for item in results['items']:
                    for artist in item['track']['artists']:
                        name = artist['name']
                        artist_counts[name] = artist_counts.get(name, 0) + 1
                if results['next']:
                    results = self.sp.next(results)
                else:
                    break

            # Get top artists
            results = self.sp.current_user_top_artists(limit=50)
            for artist in results['items']:
                name = artist['name']
                artist_counts[name] = artist_counts.get(name, 0) + 1

            # Sort artists by count and return them
            sorted_artists = sorted(artist_counts.items(), key=lambda x: x[1], reverse=True)
            favorite_artists = [artist for artist, _ in sorted_artists]
            return favorite_artists

        # Catch expired token and handle refresh token process
        except SpotifyException as e:
            if e.http_status == 401:
                logger.debug("Access token expired, refresh needed")
                return self.refresh_token_and_retry()
            else:
                raise

       # Handle token refresh if access token has expired
    def refresh_token_and_retry(self):
        try:
            # Use app-level credentials to refresh the token
            spotify_oauth = SpotifyOAuth(
                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET,
                redirect_uri=SPOTIFY_REDIRECT_URI,
                scope="user-library-read user-top-read",
            )

            # Refresh the access token
            token_info = spotify_oauth.refresh_access_token(self.refresh_token)

            if token_info:
                self.access_token = token_info['access_token']
                # Update Spotify client with the new access token
                self.sp = spotipy.Spotify(auth=self.access_token)
                logger.debug("Access token refreshed successfully.")
                # Retry the original operation (get favorite artists)
                return self.get_favorite_artists()
            else:
                logger.error("Failed to refresh access token.")
                return None

        except Exception as e:
            logger.error(f"Error refreshing access token: {e}")
            return None
