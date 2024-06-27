## Working with Image files

### References
https://learnpython.com/blog/how-to-rename-files-python/
https://learnpython.com/blog/argparse-module/
- [auth0-blog](https://auth0.com/blog/read-edit-exif-metadata-in-photos-with-python)
```
python3 -m pip install --upgrade exif
python3 -m pip install --upgrade reverse_geocoder
python3 -m pip install --upgrade pycountry
```

### Libraries for accessing image metadata

[`exif`](https://pypi.org/project/exif/) v1.6.0 2023-01-30 v0.1.0 2018-12-23
[`exifread`](https://pypi.org/project/ExifRead/) v3.0.0 2022-05-08 v.3.0 2013.06.27 (chatGPT)
[`exifreader`](https://pypi.org/project/ExifReader/) v0.1.1 2020-05-11 0.1.0 2020-05-10 fork of `exifread` 



Below is a Python program that accomplishes this task. The program will:

1. Traverse directories to find image files.
2. Extract metadata from each image file to obtain the date taken and location.
3. Organize the images into a new directory structure based on the year and rename the files using the snapshot date and location.

To achieve this, we'll use the `os` and `shutil` modules for file operations, and the `Pillow` and `exifread` libraries for image metadata extraction.

First, ensure you have the necessary libraries installed. You can install them using pip:

```bash
pip install Pillow exifread
```
Yes, the program can be modified to work with a zip file that holds the input directory. The updated program will:

Extract the zip file to a temporary directory.
Process the images in the extracted directory as before.
Clean up by removing the temporary directory after processing.
To achieve this, we'll use the zipfile module to handle the zip file and tempfile module to create a temporary directory.

To replace the GPS coordinates with the country name and nearest city, you can use a geocoding service like Nominatim, which is part of the OpenStreetMap (OSM) project. Nominatim provides an API that allows you to convert GPS coordinates into human-readable addresses.

Here's how you can integrate Nominatim with the script to replace coordinates with country names and nearest cities. You'll need the requests library to make HTTP requests to the Nominatim API. Install it using pip:

bash
Copy code
pip install requests
Then, update the script to include a function for reverse geocoding and modify the get_date_and_location function to use this new function.

Absolutely! Caching already identified locations can significantly reduce the number of requests sent to the Nominatim API. You can use a dictionary to store the locations that have already been looked up. Here's how you can modify the script to include caching:

Create a dictionary to store the cache.
Check the cache before making an API request.
Store the results in the cache after making an API request.

The error you are encountering (403 Client Error: Forbidden) indicates that your requests to the Nominatim API are being blocked. This could be due to rate limiting or usage restrictions imposed by the Nominatim API.

To handle this, you can implement a few strategies:

Rate Limiting: Add a delay between requests to avoid hitting rate limits.
Retry Mechanism: Implement retries with exponential backoff for failed requests.
Error Handling: Gracefully handle the situation when the API request fails, for example, by using a placeholder for the location.

To make the location cache persistent across program invocations, you can save the cache to a file and load it when the program starts. This way, you only need to request location data for coordinates that haven't been cached yet.

A common format for saving such cache data is JSON, as it's both human-readable and easy to work with in Python.

Here’s how you can update the script to use a persistent cache:

Load the cache from a file at the start of the program.
Save the cache to a file at the end of the program.

### Explanation

1. **get_exif_data(image_path):** This function extracts the EXIF metadata from an image file.
2. **get_date_and_location(exif_data):** This function extracts the date and GPS location (latitude and longitude) from the EXIF data.
3. **convert_to_degrees(value):** This helper function converts the GPS coordinates from degrees, minutes, and seconds to a decimal format.
4. **process_images(source_dir, dest_dir):** This function processes the images in the source directory, extracts metadata, and organizes them into the destination directory based on the year and renames them using the date and location.

extract_zip(zip_path): This function extracts the contents of a zip file to a temporary directory.
Temporary Directory Handling: The program extracts the zip file to a temporary directory, processes the images, and then removes the temporary directory.
Main Program: The main program sets the path to the zip file and the destination directory. It then extracts the zip file, processes the images, and ensures the temporary directory is cleaned up.

Explanation
argparse Module: This module is used to handle command line arguments.
Argument Parsing: The ArgumentParser is set up with two arguments: zip_file_path and destination_directory.
Main Program: The script reads the command line arguments and uses them to set the paths for the zip file and the destination directory.


Explanation
setup_logging(): Configures the logging module to log messages to both a file (image_organizer.log) and the console.
Logging Statements: Added logging statements throughout the script to log important events and debugging information:
DEBUG level logs for detailed information about the processing of each image.
INFO level logs for general information about the program's progress, such as extracting the zip file and copying images.
WARNING level logs for cases where an image is skipped due to missing EXIF data.
Logging Initialization: The setup_logging() function is called at the beginning of the __main__ block to set up logging before any other operations are performed.

Explanation
get_location_name(lat, lon): This function uses the Nominatim API to reverse geocode the GPS coordinates and return the nearest city and country name.
get_date_and_location(exif_data): This function is updated to call get_location_name instead of directly using the coordinates.
Logging: Added debug logs to track the reverse geocoding process and error logs to handle exceptions during API calls.

Explanation
Location Cache: A dictionary location_cache is introduced to store the locations.
Check Cache: Before making an API request in get_location_name, the script checks if the coordinates are already in the cache.
Store in Cache: After retrieving the location from the API, it stores the result in the cache.
Pass Cache: The location_cache is passed to the functions that need it (get_date_and_location and process_images).

Explanation
Rate Limiting and Exponential Backoff: The get_location_name function now includes a retry mechanism with exponential backoff to handle rate limiting or transient errors. It will retry the request up to 5 times, doubling the delay each time.

Error Handling: If all attempts to get the location name fail, the function returns a placeholder based on the coordinates.

Logging: Improved logging for retries and failures in the get_location_name function.

Explanation
Load Cache: The load_cache function reads the location_cache.json file at the start of the program to populate the location cache.
Save Cache: The save_cache function writes the location cache to location_cache.json when the program completes.
Cache Key: Changed the cache key format to a string representation of latitude and longitude for simplicity.

### Usage

1. Set `source_directory` to the path of the directory containing your images.
2. Set `destination_directory` to the path where you want the organized images to be copied.
3. Run the script.

This script will traverse through the `source_directory`, process each image, extract metadata, and copy the images to the `destination_directory` with the appropriate structure and naming convention.


---

not only zip
duplicate photos
command line
name format
+ structure into modules
+ exif
requests debugger
github
