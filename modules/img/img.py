#TODO extending for other image types
# https://gist.github.com/AdamDimech/6c83e43c1a70a82e10778b279b3917e5
# https://code.adonline.id.au/reading-exif-data-in-python/

from datetime import datetime
import logging
import os

from PIL import Image

from modules.shared.logging import setup_logging
import modules.img.img_exif as img_exif
import modules.img.img_exifread as img_exifread
import modules.img.img_png as img_png
from modules.geoloc.geoloc_cache import GeolocationCache

logger = logging.getLogger(__name__)
NO_YEAR = "NoYear"
NO_DATE = "NoDate"
NO_LOC = "NoLoc"

IMG_TYPE_PNG = 'PNG'
IMG_TYPE_JPEG = 'JPEG'
IMG_TYPE_TIF = 'TIF'
IMG_TYPE_RAW = 'RAW'
IMG_TYPES = [
    IMG_TYPE_PNG,
    IMG_TYPE_JPEG,
    IMG_TYPE_TIF,
    IMG_TYPE_RAW,
]

def isimage(file) :
    type = get_img_type(file)
    if type in IMG_TYPES:
        return True
    else:
        return False
    
def get_img_type(file):
    with Image.open(file) as pil:
        type = pil.format
    return type

def extract_date(str, fmt) :
    result = None
    logger.debug(f"extracting date from {str} as {fmt}")
    try: 
        #date = parse(test_str, fuzzy = True, fuzzy_with_tokens=True, dayfirst=True)
        result = datetime.strptime(str, fmt)
    except Exception as e:
        logger.debug(f"extaction failed: {e}")
    return result

def get_date_from_os(file):
    result = None
    
    os_times = []
    ctime = datetime.fromtimestamp(os.path.getctime(file))
    os_times.append(ctime)
    atime = datetime.fromtimestamp(os.path.getatime(file))
    os_times.append(atime)
    mtime = datetime.fromtimestamp(os.path.getmtime(file))
    os_times.append(mtime)
    
    if len(os_times):
        os_times.sort()
        result = os_times[0]

    return result

date_formats = [
    {'8' : ['%d%m%Y', '%Y%m%d', '%m%d%Y']},
    {'6' : ['%d%m%Y', '%Y%m%d', '%m%d%Y']},
]
earliest_date = datetime.strptime("2000-01-01", '%Y-%m-%d')
def get_dates_from_string(str, date_len):
    result = []

    str_len = len(str)
    if(str_len < date_len) :
        return result
    
    fmts = date_formats[str(date_len)]
    logger.debug(f"looking for dates in {str}: str_len={str_len}, date_len={date_len}, fmts={fmts}")
    i = 0
    while i <= str_len-date_len:
        test_str = str[i:i+date_len]
        i += 1

        if not test_str.isdigit():
            continue
        
        for fmt in fmts:
            date = extract_date(test_str, fmt)  
            if date and date < datetime.now() and date > earliest_date:
                logger.debug(f"extracted date {date} of type {type(date)}")
                result.append(date)
                continue   

    return result.sort()

def get_date_from_name(file):
    filename_dates = []

    filename, _ = os.path.splitext(os.path.basename(file))
    filename = ''.join(filename.split('_'))
    filename = ''.join(filename.split('-'))
    filename = ''.join(filename.split(' '))
    filename_len = len(filename)
    logger.debug(f"name_str={filename}, name_len={filename_len}")
    
    date_len = 8
    fmts = ['%d%m%Y', '%Y%m%d', '%m%d%Y']
    i = 0
    while i <= filename_len-date_len:
        test_str = filename[i:i+date_len]
        i += 1

        if not test_str.isdigit():
            continue
        
        for fmt in fmts:
            date = extract_date(test_str, fmt)  
            if date and date < datetime.now() and date > earliest_date:
                logger.debug(f"extracted date {date} of type {type(date)}")
                filename_dates.append(date)
                continue   
            
    filename_dates.sort()
    return filename_dates

def get_image_metadata(image_path, geocache):
    year_taken = NO_YEAR
    date_taken = NO_DATE
    date_fmt = '%Y%m%d_%H%M%S'
    loc_taken = NO_LOC

    type = get_img_type(image_path)
    date = None
    if type == IMG_TYPE_PNG:
        md = img_png.get_png_metadata(image_path)
    else:
        md = img_exif.get_image_metadata(image_path)
        if not md:
            md = img_exifread.get_image_metadata(image_path)        
    if md:
        logger.info(f"metadata by exifread: {md}")
        date = md.get('date_taken')
        lat = md.get('lat')
        lon = md.get('lon') 
        if lat and lon:
            loc_taken = geocache.get_location_name((lat, lon))
        if date:
            date_taken = date.strftime(date_fmt)+md.get('subsec','')
    if not date:
        logger.debug(f"failed to extract date from EXIF metadata, extracting from name and os")
        filename_dates = get_date_from_name(image_path)
        logger.debug(f"filename_dates: {filename_dates}")
        os_date = get_date_from_os(image_path)
        logger.debug(f"os_date: {os_date}")
        if len(filename_dates) and filename_dates[0] < os_date:
            date = filename_dates[0]
        else:
            date = os_date
        date_taken = date.strftime(date_fmt)
        logger.debug(f"selected the earliest date: {date}, date_taken={date_taken}")
        
    if date:
        year_taken = date.year
        
    logger.debug(f"year_taken={year_taken}, date_taken={date_taken}, loc_taken={loc_taken}")
    return year_taken, date_taken, loc_taken

#############################################################

test_imgs = [
    # "../tmp/419248_2852448345863_1099141566_32183751_1900628845_n_NoLoc.jpg",
    # "../tmp/oath2_23012014.jpg",
    # "../tmp/20110131_104433_IL_ElFureidis.jpg",
    # "../tmp/fromPicLib_by_year/NoYear/aug2017 1554_LT_Zarasai.jpg",
    # "D:\\tmp\\fromPicLib_by_year\\NoYear\\aug2017 2143_IL_Nesher.jpg",
    " D:\\tmp\\fromPicLib_by_year\\NoYear\\001_NoLoc.png",
]

if __name__ == "__main__":
    setup_logging(log_level=logging.DEBUG)
    logger = logging.getLogger("img_md")

    geocache = GeolocationCache()
    logger.info(f"Initialized geolocation cache with {geocache.get_size()} entries")

    for img in test_imgs:
        logger.info(f"IMAGE: {img}")
        year_taken, date_taken, loc_taken = get_image_metadata(img, geocache)
        logger.info(f"RESULT: year_taken={year_taken}, date_taken={date_taken}, loc_taken={loc_taken}")
