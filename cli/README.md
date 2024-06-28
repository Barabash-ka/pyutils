## Utilities

Programs should be run in the package's root directory.
By default, programs log progress to the terminal and also save them into `logs/` directory.

### Photo organizer

```
$ python -m cli.photos_organizer -h
usage: photos_organizer [-h] [-s SRC] [-d DEST] [--keep-temp]

        Ogranize your photos for easy storage and browsing!!!
        -----------------------------------------------------
        photos_organizer processes image files located in <source>:
        - retrieves date and location information for each image file,
        - creates new names based on date and location infromation,
        - copies renamed image files into subfolders in <destination> folder, one subfolder for each year.
        -----------------------------------------------------


options:
  -h, --help            show this help message and exit
  -s SRC, --src SRC     Path to the source location
  -d DEST, --dest DEST  Path to the directory where organized images will be copied
  --keep-temp           Keep the temporary directory after processing

Smile and love, always!!! Kathy :-)

ls -latr $LOCALAPPDATA/Temp | grep pyutils
```