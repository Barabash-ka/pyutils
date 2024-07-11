#TODO extending for other image types
# https://gist.github.com/AdamDimech/6c83e43c1a70a82e10778b279b3917e5
# https://code.adonline.id.au/reading-exif-data-in-python/

from datetime import datetime
import logging
import os

from PIL import Image

import modules.shared.mylog as mylog
import modules.shared.mydate as mydate
import modules.img.img_exif as img_exif
import modules.img.img_exifread as img_exifread
import modules.img.img_png as img_png
from modules.geoloc.geoloc_cache import GeolocationCache

logger = logging.getLogger(__name__)
NO_YEAR = "NoYear"
NO_DATE = "NoDate"
NO_LOC = "NoLoc"

IMG_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
IMG_TYPE_PNG = 'PNG'
IMG_TYPE_JPEG = 'JPEG'
IMG_TYPE_TIF = 'TIF'
IMG_TYPE_RAW = 'RAW'
IMG_TYPE_MPO = 'MPO'
IMG_TYPES = [
    IMG_TYPE_PNG,
    IMG_TYPE_JPEG,
    IMG_TYPE_TIF,
    IMG_TYPE_RAW,
    IMG_TYPE_MPO,
]
# IMG_TYPES = [
#     {"pil" : IMG_TYPE_PNG, "ext": ['png']},
#     {"pil" : IMG_TYPE_JPEG, "ext": ['jpg', 'JPG', 'jpeg']},
#     {"pil" : IMG_TYPE_PNG, "ext": ['png']},
#     {"pil" : IMG_TYPE_PNG, "ext": ['png']},
#     (IMG_TYPE_JPEG, 'jpg'),
#     (IMG_TYPE_TIF, 'tif'),
#     (IMG_TYPE_RAW), ,
# ]


def isimage_by_pil(file) :
    try:
        with Image.open(file) as img:
            img.verify()
            return True
    except Exception as e:
        return False
    
def isimage(filename):
    return any(filename.lower().endswith(ext) for ext in IMG_EXTENSIONS)
 
def get_img_type(file):
    try:
        with Image.open(file) as pil:
            return pil.format
    except Exception as e:
        logger.debug(f"failed to open file as image: {e}")
        return None
    
earliest_filedate = datetime.strptime("2000-01-01", '%Y-%m-%d')
def get_image_metadata(image_path, geocache):
    year_taken = NO_YEAR
    date_taken = NO_DATE
    date_fmt = '%Y%m%d_%H%M%S'
    loc_taken = NO_LOC

    filetype = get_img_type(image_path)
    logger.debug(f"get_image_metadata: type={filetype}")

    date = lat = lon = None
    if filetype == IMG_TYPE_PNG:
        md = img_png.get_png_metadata(image_path)
        logger.debug(f"png metadata :{md}")
    else:
        md = img_exif.get_image_metadata(image_path)
        logger.debug(f"exif metadata :{md}")
        if not len(md):
            md = img_exifread.get_image_metadata(image_path)  
            logger.debug(f"exifread metadata :{md}")      
    if len(md):
        date = md.get('datetime')
        lat = md.get('lat')
        lon = md.get('lon') 
    if not date:
        date = mydate.datetime_from_file(image_path, min_date=earliest_filedate, max_date=datetime.now())
        logger.debug(f"date from file: {date}, type={type(date)}")
        
    if date:
        date_taken = date.strftime(date_fmt)+md.get('subsec','')
        year_taken = date.year
    if lat and lon:
            loc_taken = geocache.get_location_name((lat, lon))
            
    logger.debug(f"year_taken={year_taken}, date_taken={date_taken}, loc_taken={loc_taken}")
    return year_taken, date_taken, loc_taken

#############################################################

testdir = "D:\\tmp\\test\\"

shutup_modules= [
    ("tzlocal",logging.ERROR),
    ("PIL",logging.DEBUG),
    ("exif",logging.ERROR),
    ("exifread",logging.ERROR),
    ("modules.img.img_exif",logging.ERROR),
    ("modules.img.img_exifread",logging.ERROR),
    ("modules.shared.mydate",logging.WARNING),
    #("modules.shared.mydate",logging.DEBUG),
]

import os
if __name__ == "__main__":
    mylog.setup_logging(log_level=logging.DEBUG, shutup_modules=shutup_modules)
    logger = logging.getLogger("img")

    geocache = GeolocationCache()
    logger.info(f"Initialized geoloc cache with {geocache.get_size()} entries")

    tests = os.listdir(testdir)
    for test in tests:
        test = os.path.join(testdir, test)
        logger.info(f"TEST IMAGE: {test}")
        if isimage(test) :
            year_taken, date_taken, loc_taken = get_image_metadata(test, geocache)
            logger.info(f"RESULT: year_taken={year_taken}, date_taken={date_taken}, loc_taken={loc_taken}")
        else :
            logger.info(f"RESULT: not an image")
