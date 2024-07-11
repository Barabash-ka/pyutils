import argparse
import logging
import os
import shutil


#parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#print(parent_dir)
#import sys
#sys.path.append(parent_dir)

from modules.shared.mylog import setup_logging
from modules.shared.myfile import extract_totemp, isimage, isarchive, get_hash_from_contents, count_files_in_folder
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
dest_folder = None
non_image_folder = None
keep_temp_folders = False
total_files = 0
image_files = 0
non_image_files = 0
copied_files = 0
duplicate_files = 0

def process_folder(folder_path):
    global total_files
    logger.debug(f"start processing folder {folder_path}")
    folder_files = 0
    for root, _, files in os.walk(folder_path):
        folder_files = len(files)
        logger.debug(f"there are {folder_files} files in the folder")
        for file in files:
            path = os.path.join(root, file)
            process_file(path)
        total_files += folder_files
    logger.debug(f"done processing {folder_files} entries in folder {folder_path}")

def process_file(file_path):
    global image_files
    global non_image_files
    global copied_files
    global duplicate_files
    dest_path = None

    logger.debug(f"start processing file {file_path}")
    if isimage(file_path) :
        logger.debug(f"will process as image")
        dest_path = process_image(file_path)
        image_files += 1
    elif isarchive(file_path):
        logger.debug(f"will process as archive")
        temp_dir = extract_totemp(file_path)
        keep_temp = keep_temp_folders
        logger.debug(f"extracted to {temp_dir}, will process as folder")
        try:
            process_folder(temp_dir)
        except Exception as e:
            logger.error(f"error processing extracted files, keeping temp folder {temp_dir}", e)
            keep_temp = True
        if not keep_temp:
            logger.debug(f"processed extracted files, removing temp folder {temp_dir}")
            shutil.rmtree(temp_dir)
        return
    else:
        logger.debug(f"the file is neither image nor archive, saving for later")
        non_image_files += 1
        dest_path = os.path.join(non_image_folder, os.path.basename(file_path))

    if os.path.isfile(dest_path):
        dest_path = handle_duplicate(file_path, dest_path)
    if dest_path:
        shutil.copy2(file_path, dest_path)
        copied_files += 1
        logger.info(f"copied {file_path} to {dest_path}")
    else:
        duplicate_files += 1

def handle_duplicate(file_path, dest_path):
    result = None

    logger.warning(f"possible duplicate: src={file_path}, dest={dest_path}")
    src_hash = get_hash_from_contents(file_path)
    dest_hash = get_hash_from_contents(dest_path)
    if src_hash == dest_hash: 
        logger.warning(f"duplicate confirmed, will not be copied")
    else :
        name, extension = os.path.splitext(dest_path)
        result = f"{name}-DUP{extension}"
        logger.warning(f"duplicate not confirmed, will be copied as {result}")

    return result

def process_image(image_path):
    NO_YEAR = "NoYear"
    NO_DATE = "NoDate"
    NO_LOC = "NoLoc"

    image_filename = os.path.basename(image_path)
    image_basename, image_extension = os.path.splitext(image_filename)
    image_metadata = get_image_metadata(image_path)
    year = image_metadata.get('year')
    if year:
        date = image_metadata.get('datetime')+image_metadata.get('subsec','')
        dest_file = date
    else:
        year = NO_YEAR
        date = NO_DATE
        dest_file = image_basename
     
    lat = image_metadata.get('lat')
    lon = image_metadata.get('lon')
    if lat and lon:
        location = geocache.get_location_name((lat, lon))
    else:
        location = NO_LOC

    dest_subdir = os.path.join(dest_folder, year)
    os.makedirs(dest_subdir, exist_ok=True)
    dest_file = f"{dest_file}_{location}{image_extension}"
    dest_path = os.path.join(dest_subdir, dest_file)
    logger.info(f"computed image destination: {dest_path}")
    return dest_path

def main(src):
    setup_logging(f"{program_name}.log")

    logger.debug(f"Geolocations cache contains {geocache.get_size()} entries")
    if os.path.isdir(src):
        logger.info(f"Will process images in {src} folder and copy results to {dest_folder}.")
        process_folder(src)
    elif os.path.isfile(src):
        logger.info(f"Will process {src} file and copy results to {dest_folder}.")
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

    dest_folder = args.dest
    os.makedirs(dest_folder, exist_ok=True)
    non_image_folder = f"{dest_folder}{os.sep}Other"
    os.makedirs(non_image_folder, exist_ok=True)
    keep_temp_folders = args.keep_temp
    geocache = GeolocationCache()

    files_at_dest_before = count_files_in_folder(dest_folder)
    main(args.src)
    files_at_dest_after = count_files_in_folder(dest_folder)
    logger.info(f"\nFinished processing: \
                \n\ttotal files in source: {total_files}, \
                \n\timage files in source: {image_files}, \
                \n\tother files in source: {non_image_files}, \
                \n\tcopied files: {copied_files}, skipped duplicate files {duplicate_files}, \
                \n\tfiles at destination folder before: {files_at_dest_before} \
                \n\tfiles at destination after: {files_at_dest_after}")