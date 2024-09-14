import requests
import time
import logging
from config import TICKETMASTER_API_KEY

# Constants for rate limiting and API quota
REQUEST_LIMIT_PER_SECOND = 5
DAILY_API_QUOTA = 5000

class DailyQuotaReachedException(Exception):
    pass


class ConcertClient:
    def __init__(self):
        self.api_key = TICKETMASTER_API_KEY
        self.base_url = "https://app.ticketmaster.com/discovery/v2"
        self.logger = logging.getLogger(__name__)

        # Track API calls for rate limiting
        self.requests_made_in_second = 0
        self.last_request_time = time.time()

        # Track API calls for daily quota
        self.api_calls_made_today = 0
        self.daily_quota_reset_time = time.time() + 86400  # Reset quota in 24 hours

    def get_concerts(self, artist_name):
        """
        Fetches concerts for the given artist, ensuring that rate limits and daily quota are respected.
        """
        # First, check if we've reached the daily API quota
        if self._check_daily_quota():
            self.logger.warning(f"Daily API quota of {DAILY_API_QUOTA} reached.")
            raise DailyQuotaReachedException()

        # Prepare request parameters
        params = {
            "apikey": self.api_key,
            "keyword": artist_name,
        }

        # Check and enforce rate limit before making the request
        self._check_rate_limit()

        try:
            response = self._make_api_call("events", params)
            if response:
                events = response.get('_embedded', {}).get('events', [])
                return events
            else:
                return []
        except Exception as e:
            if e.args and str(e.args[0]).startswith('429'):
                self.logger.error(f"Rate limit exceeded: {e}")
                self.api_calls_made_today = DAILY_API_QUOTA  # Set to max to avoid further requests
            else:
                self.logger.error(f"Error fetching concerts for artist {artist_name}: {e}")
            return []

    def _make_api_call(self, endpoint, params):
        """
        Makes a synchronous API call to the Ticketmaster API.
        """
        url = f"{self.base_url}/{endpoint}.json"
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        # Increment the daily API call counter after a successful request
        self.api_calls_made_today += 1
        return response.json()

    def _check_rate_limit(self):
        """
        Ensures that no more than 5 requests are made per second by enforcing rate limiting.
        """
        current_time = time.time()
        if current_time - self.last_request_time >= 1:
            # Reset the request counter and the timer after 1 second has passed
            self.requests_made_in_second = 0
            self.last_request_time = current_time

        if self.requests_made_in_second >= REQUEST_LIMIT_PER_SECOND:
            # Sleep until we are allowed to make requests again
            sleep_time = 1 - (current_time - self.last_request_time)
            if sleep_time > 0:
                self.logger.info(f"Rate limit reached: sleeping for {sleep_time:.2f} seconds.")
                time.sleep(sleep_time)

            # Reset after sleeping
            self.requests_made_in_second = 0
            self.last_request_time = time.time()

        # Increment the request counter
        self.requests_made_in_second += 1

    def _check_daily_quota(self):
        """
        Checks if the daily API quota has been reached, and resets the quota counter if needed.
        """
        current_time = time.time()

        # Check if 24 hours have passed since the last reset
        if current_time > self.daily_quota_reset_time:
            self.api_calls_made_today = 0
            self.daily_quota_reset_time = current_time + 86400  # Reset quota in 24 hours
            self.logger.info("Daily API quota reset for a new day.")

        # Return True if the quota has been reached, otherwise False
        return self.api_calls_made_today >= DAILY_API_QUOTA
