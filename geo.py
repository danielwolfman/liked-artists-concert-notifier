# Import the necessary modules from geopy
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

def get_country_city_from_gps(latitude, longitude):
    """
    Get the country and city from GPS coordinates.

    Parameters:
    latitude (float): The latitude of the GPS coordinate.
    longitude (float): The longitude of the GPS coordinate.

    Returns:
    dict: A dictionary containing the country and city.
    """
    try:
        # Initialize the Nominatim geocoder
        geolocator = Nominatim(user_agent="geoapiExercises")
        
        # Get the location details
        location = geolocator.reverse((latitude, longitude), language='en')
        
        if location and location.raw.get('address'):
            address = location.raw['address']
            country = address.get('country', 'Unknown')
            city = address.get('city', address.get('town', 'Unknown'))
            return {'country': country, 'city': city}
        else:
            return {'country': 'Unknown', 'city': 'Unknown'}
    
    except GeocoderTimedOut:
        return {'country': 'Unknown', 'city': 'Unknown'}
