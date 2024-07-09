#TODO extending for other image types
# https://gist.github.com/AdamDimech/6c83e43c1a70a82e10778b279b3917e5
# https://code.adonline.id.au/reading-exif-data-in-python/
from datetime import datetime
import logging
import warnings
import re 

from modules.shared.logging import setup_logging
import modules.img.img_exif as img_exif
import modules.img.img_exifread as img_exifread

from PIL import Image, ExifTags
import imageio.v2 as imageio

from dateutil.parser import parse

import os

#test_img = "../tmp/419248_2852448345863_1099141566_32183751_1900628845_n_NoLoc.jpg"
test_img = "../tmp/oath2_23012014.jpg"

def extract_date(str, fmt) :
    result = None
    logger.info(f"extracting date from {str} as {fmt}")
    try: 
        #date = parse(test_str, fuzzy = True, fuzzy_with_tokens=True, dayfirst=True)
        result = datetime.strptime(str, fmt)
    except Exception as e:
        logger.info(f"extaction failed: {e}")
    return result

if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger("img_elif_test")

    # img_imageio = imageio.imread(test_img)
    # bit_depth_type = img_imageio.dtype
    # bit_depth = re.sub(r'[a-z]', '', str(bit_depth_type)) 
    # logger.debug(f"img_imageio={img_imageio}")
    # logger.debug(f"bit_depth_type: {bit_depth_type}")

    # image_pil = Image.open(test_img)
    # megapixels = (image_pil.size[0]*image_pil.size[1]/1000000) # Megapixels
    # num_channels = len(Image.Image.getbands(image_pil)) 

    # logger.info(f"Image data:")
    # logger.info(f"image_pil.filename: {image_pil.filename}")
    # logger.info(f"image_pil.format: {image_pil.format}")
    # logger.info(f"image_pil.mode: {image_pil.mode}")
    # logger.info(f"image_pil.palette: {image_pil.palette}")

    # logger.info(f"Megapixels: {megapixels}")
    # logger.info(f"image_pil.size[0] (Width): {image_pil.size[0]}")
    # logger.info(f"image_pil.size[1] (Height): {image_pil.size[1]}")
    # logger.info(f"Bit Depth (per Channel): {bit_depth}")
    # logger.info(f"Bit Depth (per Pixel): {int(bit_depth)*int(num_channels)}")

    exif_md = img_exif.get_image_metadata(test_img)
    if exif_md:
        logger.info(f"exif_md={exif_md}")
    else:
        logger.warning(f"Failed to extract metadata with exif library")

    exifread_md = img_exifread.get_image_metadata(test_img)
    if exifread_md:
        logger.info(f"exifread_md={exifread_md}")
    else:
        logger.warning(f"Failed to extract metadata with exifread_ library")

    os_times = []
    os_ctime = os.path.getctime(test_img)
    ctime = datetime.fromtimestamp(os_ctime)
    logger.debug(f"os_ctime={os_ctime} of type {type(os_ctime)}, ctime={ctime} of type {type(ctime)}")
    os_times.append(ctime)
    os_atime = os.path.getatime(test_img)
    atime = datetime.fromtimestamp(os_atime)
    logger.debug(f"os_atime={os_atime} of type {type(os_atime)}, atime={atime} of type {type(atime)}")
    os_times.append(atime)
    os_mtime = os.path.getmtime(test_img)
    mtime = datetime.fromtimestamp(os_mtime)
    logger.debug(f"os_mtime={os_mtime} of type {type(os_mtime)}, ctime={mtime} of type {type(mtime)}")
    os_times.append(mtime)
    os_times.sort()
    time_taken = os_times[0]
    year_taken = time_taken.year
    datetime_taken = time_taken.strftime('%Y%m%d_%H%M%S')
    logger.info(f"Metadatda from OS: year_taken={year_taken}, datetime_taken={datetime_taken}")

    filename_dates = []
    name_str, _ = os.path.splitext(os.path.basename(test_img))
    logger.info(f"name_str={name_str}")
    name_str = ''.join(name_str.split('_'))
    name_str = ''.join(name_str.split('-'))
    name_str = ''.join(name_str.split(' '))
    name_len = len(name_str)
    logger.info(f"name_str={name_str}, name_len={name_len}")
    
    # try: 
    #     date = parse(name_str, fuzzy_with_tokens=True, dayfirst=True)
    #     logger.info(f"filename_date={date} of type {type(date)}")
    #     filename_dates.append(date)
    # except Exception as e:
    #     logger.info(f"failed to parse: {e}")

    #str = "24052017"
    # str = "23012014"
    # str_date = datetime.strptime(str, '%d%m%Y')
    # logger.info(f"str={str}, str_date={str_date}")

    date_len = 8
    fmts = ['%d%m%Y', '%Y%m%d', '%m%d%Y']
    i = 0
    while i <= name_len-date_len:
        test_str = name_str[i:i+date_len]
        i += 1

        if not test_str.isdigit():
            continue
        
        for fmt in fmts:
            date = extract_date(test_str, fmt)  
            if date and date < datetime.now():
                logger.info(f"extracted date {date} of type {type(date)}")
                filename_dates.append(date)
                continue   

    filename_dates.sort()
    print(filename_dates)