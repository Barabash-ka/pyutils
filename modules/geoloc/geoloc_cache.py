import json
import os
import logging
import requests
import reverse_geocoder as rg
import pycountry

DEFAULT_GEO_CACHE = 'data/geoloc_cache.json'
DEFAULT_PRECISION = 2
logger = logging.getLogger(__name__)

from modules.shared.mylog import setup_logging

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
    def __init__(self, cache_file=DEFAULT_GEO_CACHE, precision = DEFAULT_PRECISION):
        self.cache_file = cache_file
        self.precision = precision
        self.cache = self._load_cache()
        logger.info(f"Geocache loaded from {self.cache_file} with {len(self.cache)} entries")
    
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
        cache_key = f"{round(location[0],self.precision)},{round(location[1],self.precision)}"
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
    (55.75222, 37.61556),
    (32.27772778469444,34.86281227866667),
    (32.62912963830556,35.124299479305556),
    (32.62903500663889,35.12445580172222),
    (32.750028655166666,35.071145492805556),
    (32.75025094313889,35.071448498500004),
    (32.073673222222226,34.792636861111106),
    (32.07367705555556,34.792633055555555),
    (32.7836685,35.025943749999996),
    (32.765159583333336,35.015960666666665),
    (32.76512525,35.01596830555555),
    (32.765121444444446,35.0159645),
    (32.76512525,35.015960666666665),
    (32.76514433333333,35.01593780555555),
    (32.76569747222222,35.015205361111114),
    (32.76569747222222,35.01520155555556),
    (32.07087222222223,34.781438888888886),
    (32.78368888888889,35.02619444444444),
    (32.78375833333333,35.026205555555556),
    (32.78372777777778,35.02618888888889),
    (32.78372777777778,35.02621388888889),
    (32.78995555555555,35.008136111111114),
    (32.782980555555554,35.02549166666667),
]

if __name__ == "__main__":
    setup_logging(None)
    logger = logging.getLogger("geoloc_test")
    geocache = GeolocationCache(cache_file="test_cache2.json", precision=2)

    for dec_gps in test_dec_gps:
        name = test_dec_gps_to_name(geocache, dec_gps)
        logger.info(f"dec_gps={dec_gps},name={name}")
