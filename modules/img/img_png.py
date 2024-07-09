from PIL.ExifTags import TAGS
from PIL.PngImagePlugin import PngImageFile, PngInfo
from datetime import datetime
import logging
import warnings

from modules.shared.logging import setup_logging

logger = logging.getLogger(__name__)
exif_datetime_fmt = '%Y:%m:%d %H:%M:%S'

def get_png_metadata(img_path):
    
    png_img = PngImageFile(img_path) #via https://stackoverflow.com/a/58399815
    png_info = PngInfo()
    properties = []

    logger.debug(f"image={png_img}, metadata={png_info}, image.text={png_img.text}")   
    # Compile array from tags dict
    for i in png_img.text:
         compile = i, str(png_img.text[i])
         properties.append(compile)

    for property in properties:
        if property[0] != 'JPEGThumbnail':
            logger.debug(': '.join(str(x) for x in property))
    
    if not len(properties):
        return None
    
    header = properties[0][0]
    xml_output = []
    if not header.startswith("XML"):
        return None

    xml = properties[0][1]
    xml_output.extend(xml.splitlines()) # Use splitlines so that you have a list containing each line
    # Remove useless meta tags
    for line in xml.splitlines():
        if "<" not in line:
            if "xmlns" not in line:
                # Remove equal signs, quotation marks, /> characters and leading spaces
                xml_line = re.sub(r'[a-z]*:', '', line).replace('="', ': ')
                xml_line = xml_line.rstrip(' />')
                xml_line = xml_line.rstrip('\"')
                xml_line = xml_line.lstrip(' ')
                print(xml_line)
    return xml
    


########################################################################

test_img = "D:\\tmp\\fromPicLib_by_year\\NoYear\\001_NoLoc.png"

if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger("img_elif_test")

    logger.info(f"image={test_img}")
    metadata = get_png_metadata(test_img)
    logger.info(f"metadata={metadata}")