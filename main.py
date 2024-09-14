from notifier.spotify_client import SpotifyClient
from notifier.concert_client import ConcertClient
from notifier.storage import Storage
from geo import get_country_city_from_gps
import json
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

subscribers_file = 'subscribers.json'

# Load subscribers from file
def load_subscribers():
    if os.path.exists(subscribers_file):
        with open(subscribers_file, 'r') as file:
            return json.load(file)
    return {}

# Notify all subscribers of concerts
def notify_all_subscribers():
    logger.info("Starting the notifier")

    # Load subscribers and initialize clients
    subscribers = load_subscribers()
    concert_client = ConcertClient()
    storage = Storage()  # Initialize the storage for notified concerts

    # Loop through each subscriber
    for chat_id, tokens in subscribers.items():
        logger.info(f"Processing subscriber with chat ID {chat_id}")

        # Initialize Spotify client with each subscriber's tokens
        spotify_client = SpotifyClient(
            access_token=tokens['access_token'],
            refresh_token=tokens['refresh_token']
        )

        # Fetch favorite artists for this subscriber
        favorite_artists = spotify_client.get_favorite_artists()
        logger.info(f"Found {len(favorite_artists)} favorite artists for chat {chat_id}")

        # Fetch concerts for each artist and notify the subscriber
        for artist in favorite_artists:
            concerts = concert_client.get_concerts(artist)
            for concert in concerts:
                # Sanity check - ensure the concert is the correct artist
                if concert['_embedded']['attractions'][0]['name'].lower() != artist.lower():
                    logger.warning(f"Concert {concert['name']} does not match artist {artist}")
                    continue

                concert_id = concert['id']

                # Check if the concert has already been notified
                if storage.is_concert_notified(chat_id, concert_id):
                    logger.info(f"Concert {concert['name']} has already been notified to chat {chat_id}")
                    continue  # Skip this concert if already notified

                # Get city and country from the venue
                city = concert['_embedded']['venues'][0].get('city', {}).get('name')
                country = concert['_embedded']['venues'][0].get('country', {}).get('name')
                if not city or not country:
                    # Get the location from geographical coordinates
                    lat = concert['_embedded']['venues'][0]['location']['latitude']
                    lon = concert['_embedded']['venues'][0]['location']['longitude']
                    venue_location = get_country_city_from_gps(lat, lon)
                    city = venue_location['city']
                    country = venue_location['country']
                
                venue_name = concert['_embedded']['venues'][0].get('name', '')

                # Send notification for new concerts
                message = (
                    f"🎤 *Concert Alert!*\n\n"
                    f"🎶 *Artist:* {artist}\n"
                    f"🌍 *Location:* {city}, {country}\n"
                    f"📅 *Date:* {concert['dates']['start']['localDate']}"
                )

                if venue_name:
                    message += f"\n🏟️ *Venue:* {venue_name}"

                if concert['url']:
                    message += f"\n\n🎟️ [Get Tickets]({concert['url']})"
                # notification_service.send_notification("Concert Alert", message, chat_id)

                # Mark the concert as notified
                storage.mark_concert_as_notified(chat_id, concert_id)
                logger.info(f"Concert {concert['name']} has been notified to chat {chat_id}")

if __name__ == "__main__":
    notify_all_subscribers()
