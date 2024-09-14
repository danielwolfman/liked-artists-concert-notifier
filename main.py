import time
from notifier.spotify_client import SpotifyClient
from notifier.concert_client import ConcertClient, DailyQuotaReachedException
from notifier.notification_service import NotificationService
from notifier.storage import Storage
from geo import get_country_city_from_gps
import json
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

subscribers_file = 'subscribers.json'

notification_service = NotificationService()
concert_client = ConcertClient()

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
            try:
                concerts = concert_client.get_concerts(artist)
            except DailyQuotaReachedException:
                logger.error(f"Daily API quota reached for chat {chat_id}")
                return
            except Exception as e:
                logger.error(f"Error fetching concerts for artist {artist}: {e}")
                continue
            for concert in concerts:
                # Sanity check - ensure the concert is the correct artist
                if concert['_embedded']['attractions'][0]['name'].lower() != artist.lower():
                    logger.debug(f"Concert {concert['name']} does not match artist {artist}")
                    continue

                concert_id = concert['id']

                # Check if the concert has already been notified
                if storage.is_concert_notified(chat_id, concert_id):
                    logger.debug(f"Concert {concert['name']} has already been notified to chat {chat_id}")
                    continue  # Skip this concert if already notified

                # Get city and country from the venue
                venue = concert['_embedded'].get('venues', [{}])[0]
                city = venue.get('city', {}).get('name')
                country = venue.get('country', {}).get('name')
                if not city or not country:
                    # Get the location from geographical coordinates
                    lat = venue['location']['latitude']
                    lon = venue['location']['longitude']
                    venue_location = get_country_city_from_gps(lat, lon)
                    city = venue_location['city']
                    country = venue_location['country']
                
                venue_name = venue.get('name', '')

                # Send notification for new concerts
                message = (
                    f"🎤 *Concert Alert!*\n\n"
                    f"🎶 *Artist:* {artist}\n"
                    f"📅 *Date:* {concert['dates']['start']['localDate']}"
                )

                if city and country:
                    message += f"\n🌍 *Location:* {city}, {country}"

                if venue_name:
                    message += f"\n🏟️ *Venue:* {venue_name}"

                if concert['url']:
                    message += f"\n\n🎟️ [Get Tickets]({concert['url']})"
                notification_service.send_notification(message, chat_id)

                # Mark the concert as notified
                storage.mark_concert_as_notified(chat_id, concert_id)
                logger.info(f"Concert {concert['name']} has been notified to chat {chat_id}")

if __name__ == "__main__":
    while True:
        try:
            notify_all_subscribers()
            logger.info("Sleeping for 1 hour...")
            time.sleep(3600)  # Sleep for 1 hour (3600 seconds)
        except Exception as e:
            logger.fatal(f"Error occurred: {e}")
            time.sleep(60)  # In case of an error, wait 1 minute before retrying
