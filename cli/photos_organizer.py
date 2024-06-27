import argparse
import logging
import os
import shutil

#parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#print(parent_dir)
#import sys
#sys.path.append(parent_dir)

from modules.shared.logging import setup_logging
from modules.shared.files import extract_totemp, isimage, isarchive
from modules.img.img_exif import get_image_metadata
from modules.geoloc.geoloc_cache import GeolocationCache

# Globals
program_name = "photos_organizer"
program_abbr = "photos"
program_description = '''\
        Ogranize your photos for easy storage and browsing!!!
        -----------------------------------------------------
        photos_organizer processes image files located in <source>: 
        - retrieves date and location information for each image file, 
        - creates new names based on date and location infromation,
        - copies renamed image files into subfolders in <destination> folder, one subfolder for each year.
        -----------------------------------------------------
        '''
moto = "Smile and love, always!!! Kathy :-)"
logger = logging.getLogger(program_abbr)

geocache = None
dest_dir = None
keep_temp_folders = False
total_files = 0
copied_files = 0
not_img_files = 0
img_files = 0

def process_folder(src_dir):
    global total_files

    for root, _, files in os.walk(src_dir):
        folder_files = len(files)
        logger.debug(f"process_folder: process {folder_files} files in {src_dir}")
        total_files += folder_files
        for file in files:
            file_path = os.path.join(root, file)
            process_file(file_path)

def process_file(file_path):
    global not_img_files
    global img_files
    global copied_files
    dest_path = None

    logger.debug(f"process_file: process {file_path}")

    if isimage(file_path) :
        dest_path = process_image(file_path)
        img_files += 1
    
    elif isarchive(file_path):
        logger.info(f"process_file: {file_path} is archive, extracting to temp to process")
        temp_dir = extract_totemp(file_path)
        logger.info(f"process_file: {file_path} is extracted to {temp_dir}")
        process_folder(temp_dir)
        if not keep_temp_folders:
            shutil.rmtree(temp_dir)
            logger.info(f"process_file: removed processed temp folder {temp_dir}")

    else:
        logger.info(f"process_file: {file_path} is neither image or archive, stopping here ...")
        not_img_files += 1
        file_name = os.path.basename(file_path)
        dest_subdir = os.path.join(dest_dir, "NotImg")
        os.makedirs(dest_subdir, exist_ok=True)
        dest_path = os.path.join(dest_subdir, file_name)

    if dest_path:
        shutil.copy2(file_path, dest_path)
        copied_files += 1
        logger.info(f"copied {file_path} to {dest_path}")

def process_image(image_path):
    image_metadata = get_image_metadata(image_path)
    year = image_metadata.get('year', 'NoYear')
    timestamp = image_metadata.get('datetime', 'NoTime')+image_metadata.get('subsec', str(0))
    lat = image_metadata.get('lat')
    lon = image_metadata.get('lon')
    if lat and lon:
        location = geocache.get_location_name((lat, lon))
    else:
        location = "NoLoc"
    logger.info(f"process_image: year = {year}, timestamp={timestamp}, place = {location}")
    
    dest_subdir = os.path.join(dest_dir, year)
    os.makedirs(dest_subdir, exist_ok=True)
    dest_path = os.path.join(dest_subdir, f"{timestamp}_{location}.jpg")
    return dest_path

def main(src):
    setup_logging(f"{program_abbr}.log")

    if os.path.isdir(src):
        logger.info(f"main: process images in {src} folder and copy results to {dest_dir}")
        process_folder(src)
    elif os.path.isfile(src):
        logger.info(f"main: process {src} file and copy results to {dest_dir}")
        process_file(src)
    else:
        logger.info(f"main: {src} is neither file nore folder, stopping here ...")    
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog = program_name,
        formatter_class = argparse.RawDescriptionHelpFormatter, 
        description=program_description, 
        epilog = moto)
    
    parser.add_argument(
        '-s',
        '--src', 
        type = str, 
        metavar = 'SRC',
        default = '.',
        help= "Path to the source location")
    
    parser.add_argument(
        '-d', 
        '--dest',
        type=str, 
        metavar = 'DEST',
        default = './photo_organizer_out',
        help="Path to the directory where organized images will be copied")
    
    parser.add_argument(
        '--keep-temp', 
        action='store_true', 
        help="Keep the temporary directory after processing")
    
    args = parser.parse_args()

    dest_dir = args.dest
    if os.path.isdir(dest_dir):
        logger.info(f"Destination directory {dest_dir} exists and will be written into.")
    keep_temp_folders = args.keep_temp

    geocache = GeolocationCache()
    logger.info(f"Loaded geolocations cache of {geocache.get_size()} entries")

    main(args.src)
    logger.info(f"Finished processing: total_files={total_files}, img_files={img_files}, not_img_files={not_img_files}, copied_files={copied_files}")