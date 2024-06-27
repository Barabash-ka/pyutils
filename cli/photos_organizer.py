import argparse
import logging
import os
import shutil


#parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#print(parent_dir)
#import sys
#sys.path.append(parent_dir)

from modules.shared.logging import setup_logging
from modules.shared.files import extract_totemp, isimage, isarchive, get_hash_from_contents
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
other_dir = None
keep_temp_folders = False
processed_files = 0
processed_images = 0
processed_other = 0
copied_files = 0
duplicate_files = 0

def process_folder(folder_path):
    global processed_files
    logger.debug(f"start processing folder{folder_path}")
    for root, _, folder_files in os.walk(folder_path):
        logger.debug(f"there are {len(folder_files)} files in the folder")
        processed_folder_files = 0
        for file in folder_files:
            file_path = os.path.join(root, file)
            process_file(file_path)
            processed_folder_files += 1
    processed_files += processed_folder_files


def process_file(file_path):
    global processed_images
    global processed_other
    global copied_files
    global duplicate_files
    dest_path = None

    logger.debug(f"start processing file {file_path}")
    if isimage(file_path) :
        logger.debug(f"will process as image")
        dest_path = process_image(file_path)
        processed_images += 1
    
    elif isarchive(file_path):
        logger.debug(f"will process_file as archive")
        temp_dir = extract_totemp(file_path)
        logger.debug(f"extracted to {temp_dir}, will process as folder")
        process_folder(temp_dir)
        if not keep_temp_folders:
            logger.debug(f"finished processing extracted files, removing temp folder")
            shutil.rmtree(temp_dir)
        return

    else:
        logger.debug(f"the file is neither image or archive, saving for later")
        processed_other += 1
        dest_path = os.path.join(other_dir, os.path.basename(file_path))

    if dest_path:
        if os.path.isfile(dest_path):
            logger.warning(f"File {dest_path} exists, copying as duplicate")
            src_hash = get_hash_from_contents(file_path)
            dest_hash = get_hash_from_contents(dest_path)
            logger.warning(f"Posible duplicate: src_hash={src_hash}, dest_hash={dest_hash}")
            if src_hash == dest_hash: 
                logger.warning(f"Confirmed duplicate, will not copy")
                duplicate_files += 1
                return
            else :
                dest_path = f"{dest_path}-dup"
                logger.warning(f"Duplicate not confirmed, copying as {dest_path}")
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
    setup_logging(f"{program_name}.log")

    logger.debug(f"Geolocations cache contains {geocache.get_size()} entries")
    if os.path.isdir(src):
        logger.info(f"Will process images in {src} folder and copy results to {dest_dir}.")
        process_folder(src)
    elif os.path.isfile(src):
        logger.info(f"Will process {src} file and copy results to {dest_dir}.")
        process_file(src)
    else:
        logger.warning(f"Bad arguments: {src} should be either file or folder.")
    
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
    os.makedirs(dest_dir, exist_ok=True)
    other_dir = f"{dest_dir}{os.sep}Other"
    os.makedirs(other_dir, exist_ok=True)
    keep_temp_folders = args.keep_temp
    geocache = GeolocationCache()
    main(args.src)
    logger.info(f"Finished processing:\n\tprocessed_files={processed_files}, \
                \n\tprocessed_images={processed_images}, \
                \n\tprocessed_other={processed_other}, \
                \n\tcopied_files={copied_files}, \
                \n\tduplicate_files={duplicate_files}")