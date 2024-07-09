import exifread
from datetime import datetime
import logging
import sys

logger = logging.getLogger(__name__)
exif_datetime_fmt = '%Y:%m:%d %H:%M:%S'

def convert_to_degrees(value):
    # logger.debug(f"{value.values[0]}, {float(value.values[0].num)}, {float(value.values[0].den)}")
    # logger.debug(f"{value.values[1]}, {float(value.values[1].num)}, {float(value.values[1].den)}")
    # logger.debug(f"{value.values[2]}, {float(value.values[2].num)}, {float(value.values[2].den)}")
    d = float(value.values[0].num) / float(value.values[0].den)
    m = float(value.values[1].num) / float(value.values[1].den)
    s = float(value.values[2].num) / float(value.values[2].den)
    return d + (m / 60.0) + (s / 3600.0)

def get_image_metadata(image_path):
    tags = None
    lat = lon = None
    lat_ref = lon_ref = None
    result = {}

    with open(image_path, 'rb') as f:
        tags = exifread.process_file(f)
    
    if not tags:
        logger.debug(f"could not retrieve metadata with exifread")
        return result
    
    logger.debug(f"get_image_metadata: retrieved {len(tags)} exif tags as {type(tags)}")
    for tag, tag_value in tags.items():
        value = str(tag_value)
        logger.debug(f"get_image_metadata: {tag}: {value[:50]}...")

        if 'ImageDescription' in tag:   
            result['descr'] = value
        elif 'EXIF DateTimeOriginal' in tag:
            date_taken = datetime.strptime(value, exif_datetime_fmt)
            result['date_taken'] = date_taken
            # result['year'] = date_taken.strftime('%Y')
            # result['datetime'] = date_taken.strftime('%Y%m%d_%H%M%S')
        elif "SubSecTimeOriginal" in tag:
            result['subsec'] = value
        elif 'GPS GPSLatitude' in tag:
            if 'GPS GPSLatitudeRef' in tag:
                lat_ref = value
            else:
                lat = convert_to_degrees(tag_value)
        elif 'GPS GPSLongitude' in tag:
            if 'GPS GPSLongitudeRef' in tag:
                lon_ref = value
            else:
                lon = convert_to_degrees(tag_value)

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

    logger.debug(f"get_image_metadata: result = {result}")
    return result