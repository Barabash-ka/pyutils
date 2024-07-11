# https://pypi.org/project/exif/
from exif import Image as ExifImage
import logging
import warnings

import modules.shared.mylog as mylog
import modules.shared.mydate as mydate

logger = logging.getLogger(__name__)
exif_datetime_fmts = [
    '%Y:%m:%d %H:%M:%S',
    # '%Y:%m:%d',
]

def degrees_to_decimal(degrees, minutes, seconds):
    return degrees + (minutes / 60.0) + (seconds / 3600.0)
                               
def get_image_metadata(img_path):
    exif_tags = None
    lat = lon = None
    lat_ref = lon_ref = None
    result = {}

    with open(img_path, 'rb') as f:
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore")
                exif_img = ExifImage(f)
                #if exif_img.has_exif():
                exif_tags = exif_img.get_all()
        except Exception as e:
            logger.error("elif package failed to initialize image object")
            return result
        
    if not exif_tags:
        logger.debug(f"could not retrieve exif tags")
        return result
            
    logger.debug(f"retrieved {len(exif_tags)} exif tags as {type(exif_tags)}")
    tag_num = 0
    dates = []
    for tag in exif_tags:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            value = exif_img.get(tag)
            tag_num += 1
            if 'JPEGThumbnail' not in tag:
                logger.debug(f"{tag_num}: tag={tag}, value={str(value)}, type={type(value)}")
            if 'description' in tag:   
                if len(value):
                    result['descr'] = value
                    logger.debug(f"Collected description: {value}")
            elif 'datetime' in tag:
                dt = mydate.datetime_from_string(value, exif_datetime_fmts)
                if dt:
                    dates.append(dt)
                    logger.debug(f"Collected datetime: {dt} type: {type(dt)}")
            elif "sub_sec_time_original" in tag:
                if value:
                    result['subsec'] = value
                    logger.debug(f"Collected subsec")
            elif 'gps_latitude' in tag:
                if 'gps_latitude_ref' in tag:
                    lat_ref = value
                    logger.debug(f"Collected lat_ref")
                else:
                    lat = degrees_to_decimal(value[0], value[1], value[2])
                    logger.debug(f"Collected lat")
            elif 'gps_longitude' in tag:
                if 'gps_longitude_ref' in tag:
                    lon_ref = value
                    logger.debug(f"Collected lon_ref")
                else:
                    lon = degrees_to_decimal(value[0], value[1], value[2])
                    logger.debug(f"Collected lon")         

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

    date = mydate.pick_earliest_date(dates)
    if date:
        result['datetime'] = date
        
    logger.debug(f"returning extracted exif metada: = {result}")
    return result

########################################################################

tests = [
    "D:\\tmp\\test\\bath.jpg",
]

testdir = "D:\\tmp\\test\\"
shutup_modules= [
    ("tzlocal",logging.ERROR),
    ("PIL",logging.ERROR),
    ("exif",logging.ERROR),
    #("modules.shared.mydate",logging.WARNING),
    ("modules.shared.mydate",logging.DEBUG),
    #("modules.shared.mydate",logging.INFO),
]

import os
#import os.path
if __name__ == "__main__":
    mylog.setup_logging(log_level=logging.DEBUG, shutup_modules=shutup_modules)
    logger = logging.getLogger("img_exif")

    tests = os.listdir(testdir)
    for test in tests:
        test = os.path.join(testdir, test)
        logger.info(f"TEST IMAGE: {test}")
        metadata = get_image_metadata(test)
        logger.info(f"RESULT    : {metadata}")