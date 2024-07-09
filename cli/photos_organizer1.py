import argparse
import logging
import os
import shutil

#parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#print(parent_dir)
#import sys
#sys.path.append(parent_dir)

from modules.shared.logging import setup_logging
from modules.shared.files import extract_totemp, isarchive, get_hash_from_contents
import modules.img.img as img
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
NO_YEAR = "NoYear"
NO_DATE = "NoDate"
NO_LOC = "NoLoc"
SUBDIR_OTHER = "Other"

def all_files_at_path(path, files_at_path, tempdirs_for_path) :
    logger.debug(f"start collecting all the files at {path}")
    if os.path.isdir(path):
        logger.debug(f"{path} is a directory, walk through the entries")
        dirEntries = os.scandir(path)
        for entry in dirEntries :
            all_files_at_path(os.path.join(path, entry.name), files_at_path, tempdirs_for_path)
        dirEntries.close()
    elif os.path.isfile(path):
        logger.debug(f"{path} is a file, see whether it is an archive")
        if isarchive(path):
            logger.debug(f"{path} is an archive")
            temp_dir = extract_totemp(path)
            tempdirs_for_path.append(temp_dir)
            all_files_at_path(temp_dir, files_at_path, tempdirs_for_path)           
        else:
            logger.debug(f"{path} is a simple file, adding")
            files_at_path.append(path)
    else:
        logger.warning(f"{path} is neither a folder nor a file, skipping")

def copy_from_src_to_dst(files_at_scr, files_at_dst, dst_dir):
    images = other = copied = skipped = 0

    for src_path in files_at_scr:
        logger.info(f"start processing: {src_path}")
        subdir, file, extension = compute_dst_name(src_path)
        dst_subdir = os.path.join(dst_dir, subdir)
        os.makedirs(dst_subdir, exist_ok=True)
        dst_path = f"{os.path.join(dst_subdir, file)}{extension}"
        logger.info(f"destination path: {dst_path}")
    
        if dst_path in files_at_dst:
            logger.debug(f"{dst_path} exists in destination")
            src_hash = get_hash_from_contents(src_path)
            dst_hash = get_hash_from_contents(dst_path)
            if src_hash == dst_hash: 
                logger.warning(f"duplicate confirmed by equal hashes, will not be copied")
                skipped += 1
                continue
        
            try :
                dup_number = int(file.split('-')[-1])
            except :
                dup_number = 1

            file = f"{file}-{dup_number}"
            dst_path = f"{os.path.join(dst_subdir, file)}{extension}"
        else:
            #logger.debug(f"{dst_path} does not exists in {files_at_dst}")
            logger.debug(f"{dst_path} does not exists in destination")

        shutil.copy2(src_path, dst_path)
        copied += 1
        if img.isimage(src_path):
            images += 1
        else:
            other += 1
        logger.info(f"copied {src_path} to {dst_path}")
        
    return copied, images, other, skipped

def compute_dst_name(src_path):
    scr_basename = os.path.basename(src_path)
    src_filename, src_extension = os.path.splitext(scr_basename)

    dst_filename = src_filename
    dst_extension = src_extension
    dst_subdir = SUBDIR_OTHER
    if img.isimage(src_path) :
        year_taken, date_taken, loc_taken = img.get_image_metadata(src_path, geocache)
        dst_subdir = str(year_taken)
        dst_filename = f"{date_taken}_{loc_taken}"

    logger.debug(f"\ndst_subdir={dst_subdir} of type {type(dst_subdir)} \
                \ndst_filename={dst_filename} of type {type(dst_filename)}\
                \ndst_extension={dst_extension} of type {type(dst_extension)}")
    return dst_subdir, dst_filename, dst_extension

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
        '--dst',
        type=str, 
        metavar = 'DST',
        default = './photo_organizer_out',
        help="Path to the directory where organized images will be copied")
    
    parser.add_argument(
        '--keep-temp', 
        action='store_true', 
        help="Keep the temporary directory after processing")
    
    args = parser.parse_args()

    setup_logging(f"{program_name}.log", logging.INFO)

    src = os.path.abspath(args.src)
    dst = os.path.abspath(args.dst)
    keep_temp = args.keep_temp
    logger.info(f"Will process files in {src}, renaming and copying them into {dst}; keep_temp = {keep_temp}")
    os.makedirs(dst, exist_ok=True)
    #non_img_subfolder = f"{dst}{os.sep}Other"
    #os.makedirs(non_img_subfolder, exist_ok=True)
    
    files_at_src = []
    tempdirs_for_src = []
    all_files_at_path(src, files_at_src, tempdirs_for_src)
    #logger.debug(f"files_at_scr={files_at_src}")
    #logger.debug(f"tempdirs_for_src={tempdirs_for_src}")

    files_at_dst = []
    tempdirs_for_dst = []
    all_files_at_path(dst, files_at_dst, tempdirs_for_dst)
    #logger.debug(f"files_at_dst={files_at_dst}")
    #logger.debug(f"tempdirs_for_dst={tempdirs_for_dst}")
    if len(tempdirs_for_dst) :
        logger.warning(f"There are {len(tempdirs_for_dst)} archives at destination, resulting structure can be weird")
    logger.info(f"There are {len(files_at_src)} files and {len(tempdirs_for_src)} archives at source and {len(files_at_dst)} files at destination") 
    
    geocache = GeolocationCache()
    logger.info(f"Initialized geolocation cache with {geocache.get_size()} entries")

    # TODO time 
    logger.info(f"Start processing")
    copied, images, other, skipped = copy_from_src_to_dst(files_at_src, files_at_dst, dst)
    
    logger.info(f"Finished adding files to destination: \
                \n\t Total files copied: {copied} \
                \n\t Image files copied: {images} \
                \n\t Other files copied: {other} \
                \n\t Skipped files: {skipped} ") 
