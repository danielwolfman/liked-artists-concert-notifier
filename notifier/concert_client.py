import logging
import requests
from config import TICKETMASTER_API_KEY

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConcertClient:
    def __init__(self):
        self.api_key = TICKETMASTER_API_KEY
        self.base_url = "https://app.ticketmaster.com/discovery/v2"

    # Find the artist's attractionId using the Ticketmaster attractions API
    def get_artist_attraction_id(self, artist_name):
        url = f"{self.base_url}/attractions.json"
        params = {
            "apikey": self.api_key,
            "keyword": artist_name,
        }
        response = requests.get(url, params=params)

        if response.status_code == 200:
            attractions = response.json().get('_embedded', {}).get('attractions', [])
            if len(attractions) > 0:
                # Return the first matching attraction (you can further filter if necessary)
                return attractions[0]['id']
            else:
                logger.debug(f"No attractions found for artist {artist_name}")
                return None
        else:
            logger.error(f"Error fetching attractions for {artist_name}: {response.status_code}")
            return None

    # Fetch concerts for the given artist using the artist's attractionId
    def get_concerts(self, artist_name):
        attraction_id = self.get_artist_attraction_id(artist_name)
        if not attraction_id:
            return []

        url = f"{self.base_url}/events.json"
        params = {
            "apikey": self.api_key,
            "attractionId": attraction_id,  # Use the exact attractionId to search for concerts
        }
        response = requests.get(url, params=params)

        if response.status_code == 200:
            events = response.json().get('_embedded', {}).get('events', [])
            return events
        else:
            logger.error(f"Error fetching events for artist {artist_name}: {response.status_code}")
            return []
