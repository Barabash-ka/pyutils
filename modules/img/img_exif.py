# https://pypi.org/project/exif/
from exif import Image as ExifImage
from datetime import datetime
import logging

from modules.shared.logging import setup_logging

logger = logging.getLogger(__name__)
exif_datetime_fmt = '%Y:%m:%d %H:%M:%S'

def degrees_to_decimal(degrees, minutes, seconds):
    return degrees + (minutes / 60.0) + (seconds / 3600.0)

def get_image_metadata(img_path):
    exif_tags = None
    lat = lon = None
    lat_ref = lon_ref = None
    result = {}

    with open(img_path, 'rb') as f:
        try:
            exif_img = ExifImage(f)
            #if exif_img.has_exif():
            exif_tags = exif_img.get_all()
        except Exception as e:
            logger.error("elif package failed to initialize image object")
            return result
        
    if not exif_tags:
        logger.info(f"could not retrieve exif tags")
        return result
            
    logger.info(f"retrieved {len(exif_tags)} exif tags as {type(exif_tags)}")
    for tag in exif_tags:
        value = exif_img.get(tag)
        logger.debug(f"{tag}:{str(value)[:50]}..., type={type(value)}")

        if 'image_description' in tag:   
            result['descr'] = value
        elif 'datetime_original' in tag:
            date_taken = datetime.strptime(value, exif_datetime_fmt)
            result['year'] = date_taken.strftime('%Y')
            result['datetime'] = date_taken.strftime('%Y%m%d_%H%M%S')
        elif "sub_sec_time_original" in tag:
            result['subsec'] = value
        elif 'gps_latitude' in tag:
            if 'gps_latitude_ref' in tag:
                lat_ref = value
            else:
                lat = degrees_to_decimal(value[0], value[1], value[2])
        elif 'gps_longitude' in tag:
            if 'gps_longitude_ref' in tag:
                lon_ref = value
            else:
                lon = degrees_to_decimal(value[0], value[1], value[2])

    if lat and lat_ref:
        if 'N' in lat_ref:
            result['lat'] = lat
        else :
            result['lat'] = -lat
    if lon and lon_ref:
        if 'E' in lon_ref:
            result['lon'] = lon
        else:
            result['lon'] = -lon

    logger.info(f"result = {result}")
    return result

########################################################################

test_img = "tmp/image1.png"

if __name__ == "__main__":
    setup_logging(None)
    logger = logging.getLogger("img_elif_test")

    metadata = get_image_metadata(test_img)
    logger.info(f"metadata={metadata}")