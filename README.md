I recently built myself a home server for storing my media. I used to store them on OneDrive before.
While moving my files from OneDrive to my local server I thought everything was going great, until I
just recently started backing up my media from my phone directly into my Immich server.

Immich did not detect duplicate files between my OneDrive and internal library of itself because I
added my OneDrive folder into Immich as an external library.

I tried using several programs to detect duplicate images and videos between these folders. Some of them
detected files wrong, some of them selected files with same names from different dates. Only way for
me to do this task was creating a script for this task. So,

This script is for detecting duplicate files between my OneDrive folders and local Immich server folders,
moving the detected duplicates out of OneDrive. I use the same folder structure for both, which is
    
{YYYY}/{YYYYMM__}

basically the folders are named after years, and their subfolders are named after their months.

I also never changed the names of the files, using these two to my advantage, I succesfully protected
the integrity of my dear archive.
