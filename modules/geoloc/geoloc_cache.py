import json
import os
import logging
import requests
import reverse_geocoder as rg
import pycountry

DEFAULT_GEO_CACHE = 'data/geoloc_cache.json'
logger = logging.getLogger(__name__)

from modules.shared.logging import setup_logging

def get_place(coordinates):
    rg_res = rg.search(coordinates)
    logger.debug(f"get_place for {coordinates}: rg returned {rg_res} [{type(rg_res)}] ")
    location_info = rg_res[0]
    logger.debug(f"get_place: location_info={location_info}")
    country_code = location_info['cc']
    name = location_info['name']
    logger.debug(f"get_place: name={name}, country_code={country_code}")
    #country = pycountry.countries.get(alpha_2=country_code)
    #logger.debug(f"get_place: country={country}, type={type(country)}")
    result = f"{country_code}_{name}".replace(" ", "")
    return result

class GeolocationCache:
    def __init__(self, cache_file=DEFAULT_GEO_CACHE):
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_cache(self):
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=4)

    def get_size(self):
        return len(self.cache)

    def get_location_name(self, location):
        location_name = None
        cache_key = f"{location[0]},{location[1]}"
        logger.info(f"Retrieving location for {cache_key}")

        if cache_key in self.cache:
            location_name = self.cache[cache_key]
            logger.debug(f"Location found in cache: {location_name}")
        else:
            try:
                location_name = self._fetch_location_from_rg(location)
                logger.debug(f"Location found by rg: {location_name}")
            except Exception as e:
                logger.error(f"Offline name resolution failed: {e}")           
                try:
                    location_name = self._fetch_location_from_api(location)
                    logger.debug(f"Location received from API: {location_name}")
                except Exception as e:
                    logging.error(f"Fetching location name from API failed: {e}")
            if location_name:
                self.cache[cache_key] = location_name
                self._save_cache()
        
        return location_name
    
    def _fetch_location_from_rg(self, location):
        location_info = None
        result = None
        
        rg_res = rg.search(location)
        if rg_res:
            results = len(rg_res)
            logger.debug(f"rg returned {results} results: {rg_res}")
            if results:
                location_info = rg_res[0]
                logger.debug(f"location_info={location_info}")
            country_code = location_info['cc']
            place_name = location_info['name']
            logger.debug(f"name={place_name}, country_code={country_code}")
            country = pycountry.countries.get(alpha_2=country_code)
            country_name = country.name
            logger.debug(f"pycountry: country={country}, country_name={country_name}")
            result = f"{country_code}_{place_name}".replace(" ", "")

        if not result:
            raise Exception("Location not found by rg")
        
        return result

    def _fetch_location_from_api(self, location):
        try:
            url = 'https://nominatim.openstreetmap.org/reverse'
            params = {
                'format': 'json',
                'lat': location[0],
                'lon': location[1],
                'zoom': 10,
                'accept-language': 'en'
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('display_name', 'Unknown Location')
        except requests.RequestException as e:
            logging.error(f"Error in reverse geocoding: {e}")
            raise
########################################################################

def test_dec_gps_to_name(geocache, coordinates):
    name = geocache.get_location_name(coordinates)
    return name

test_dec_gps = [
    (32.27772778469444,34.86281227866667),
    (55.75222, 37.61556)
]

if __name__ == "__main__":
    setup_logging(None)
    logger = logging.getLogger("geoloc_test")
    geocache = GeolocationCache()

    for dec_gps in test_dec_gps:
        name = test_dec_gps_to_name(geocache, dec_gps)
        logger.info(f"dec_gps={dec_gps},name={name}")
