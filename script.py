'''
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
'''

import os
import directories
from pathlib import Path
import shutil
import sys

onedriveDir = directories.onedriveDir
immichDir = directories.immichDir
sharedDir = directories.sharedDir

# Functions

def progress_bar(current, total, label="Processing"):
    barLength = 30

    if total == 0:
        percentage = 100
    else:
        percentage = current / total * 100

    filledLength = int(barLength * percentage / 100)
    bar = "█" * filledLength + "░" * (barLength - filledLength)

    sys.stdout.write(
        f"\r{label}: [{bar}] {percentage:6.2f}% "
        f"{current} / {total}"
    )
    sys.stdout.flush()

    if current >= total:
        print()


# Functions

def collect_folders(directory, folderNames):
    totalFolders = sum(
        len(dirs)
        for root, dirs, files in os.walk(directory)
    )

    processedFolders = 0

    for root, dirs, files in os.walk(directory):
        for folderName in dirs:
            if os.path.isdir(os.path.join(root, folderName)):
                folderNames.append(os.path.join(root, folderName))

            processedFolders += 1
            progress_bar(processedFolders, totalFolders, "Collecting folders")

    folderNames.sort()
    return folderNames


def collect_subfolders(folder):
    folderPath = Path(folder)

    subfolders = [
        item for item in folderPath.iterdir()
        if item.is_dir()
    ]

    for current, subfolder in enumerate(subfolders, start=1):
        progress_bar(current, len(subfolders), "Collecting subfolders")

    return subfolders


def collect_months(years):
    months = []

    for current, year in enumerate(years, start=1):
        months.extend(collect_subfolders(year))
        progress_bar(current, len(years), "Collecting months")

    months.sort()
    return months


def folders_match(folders1, folders2):
    matchingFolders = []

    totalComparisons = len(folders1) * len(folders2)
    processedComparisons = 0

    for folder1 in folders1:
        for folder2 in folders2:
            if os.path.basename(folder1) == os.path.basename(folder2):
                matchingFolders.append((folder1, folder2))

            processedComparisons += 1
            progress_bar(
                processedComparisons,
                totalComparisons,
                "Matching folders"
            )

    return matchingFolders


def files_match(matchingFolders):
    matchingFiles = []

    # Count OneDrive files beforehand for accurate progress
    totalFiles = sum(
        len(files)
        for onedriveMonth, immichMonth in matchingFolders
        for root, dirs, files in os.walk(onedriveMonth)
    )

    processedFiles = 0

    for onedriveMonth, immichMonth in matchingFolders:

        immichFiles = {}

        for root, dirs, files in os.walk(immichMonth):
            for file in files:
                normalizedName = file.casefold()

                immichFilePath = os.path.join(root, file)

                immichFiles.setdefault(normalizedName, []).append(
                    immichFilePath
                )

        for root, dirs, files in os.walk(onedriveMonth):
            for file in files:
                normalizedName = file.casefold()

                onedriveFilePath = os.path.join(root, file)

                if normalizedName in immichFiles:
                    for immichFilePath in immichFiles[normalizedName]:
                        matchingFiles.append(
                            (onedriveFilePath, immichFilePath)
                        )

                processedFiles += 1
                progress_bar(
                    processedFiles,
                    totalFiles,
                    "Matching files"
                )

    print(f"Total matching files: {len(matchingFiles)}")
    return matchingFiles


def quarantine_matching_files(matchingFiles):
    onedriveRoot = Path(directories.onedriveDir)
    quarantineDir = Path(directories.sharedDir) / "movedWithScript"

    totalFiles = len(matchingFiles)

    for current, (onedriveFile, immichFile) in enumerate(
        matchingFiles, start=1
    ):
        source = Path(onedriveFile)

        relativePath = source.relative_to(onedriveRoot)
        destination = quarantineDir / relativePath

        destination.parent.mkdir(parents=True, exist_ok=True)

        try:
            shutil.move(source, destination)

        except OSError as error:
            print(f"\nFAILED SOURCE: {source}")
            print(f"FAILED DESTINATION: {destination}")
            print(f"ERROR: {error}")
            raise

        progress_bar(current, totalFiles, "Quarantining files")

    print(f"Copied {totalFiles} matching files to {quarantineDir}")
# Script

onedriveFolderNames = collect_folders(onedriveDir, [])
immichFolderNames = collect_folders(immichDir, [])

onedriveYears = collect_subfolders(onedriveDir)
immichYears = collect_subfolders(immichDir)

onedriveMonths = collect_months(onedriveYears)
immichMonths = collect_months(immichYears)

matchingFolders = folders_match(onedriveMonths, immichMonths)

matchingFiles = files_match(matchingFolders)

quarantine_matching_files(matchingFiles)
