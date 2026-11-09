import os
import directories
from pathlib import Path
import shutil

onedriveDir = directories.onedriveDir
immichDir = directories.immichDir
sharedDir = directories.sharedDir

# Functions

def collect_folders(directory, folderNames):
    for root, dirs, files in os.walk(directory):
        for folderName in dirs:
                if os.path.isdir(os.path.join(root, folderName)):
                        folderNames.append(os.path.join(root, folderName))
    folderNames.sort()
    return folderNames

def collect_subfolders(folder):
    folderPath = Path(folder)
    subfolders = [item for item in folderPath.iterdir() if item.is_dir()]
    return subfolders

def collect_months(years):
    months = []
    for year in years:
        months.extend(collect_subfolders(year))
    months.sort()
    return months

def folders_match(folders1, folders2):
    matchingFolders = []
    for folder1 in folders1:
        for folder2 in folders2:
            if os.path.basename(folder1) == os.path.basename(folder2):
                matchingFolders.append((folder1, folder2))
    return matchingFolders

def files_match(matchingFolders):
    matchingFiles = []

    for onedriveMonth, immichMonth in matchingFolders:

        immichFiles = {}

        for root, dirs, files in os.walk(immichMonth):
            for file in files:
                normalizedName = file.casefold()

                immichFilePath = os.path.join(root, file)

                immichFiles.setdefault(normalizedName, []).append(immichFilePath)

        for root, dirs, files in os.walk(onedriveMonth):
            for file in files:
                normalizedName = file.casefold()

                onedriveFilePath = os.path.join(root, file)

                if normalizedName in immichFiles:
                    for immichFilePath in immichFiles[normalizedName]:
                        matchingFiles.append(
                            (onedriveFilePath, immichFilePath)
                        )

    print(len(matchingFiles))
    return matchingFiles

def quarantine_matching_files(matchingFiles):
    onedriveRoot = Path(directories.onedriveDir)
    quarantineDir = Path(directories.sharedDir) / "movedWithScript"

    for onedriveFile, immichFile in matchingFiles:
        source = Path(onedriveFile)

        relativePath = source.relative_to(onedriveRoot)
        destination = quarantineDir / relativePath

        destination.parent.mkdir(parents=True, exist_ok=True)

        try:
            shutil.copy2(source, destination)
            print(f"Copied: {source}")

        except OSError as error:
            print(f"\nFAILED SOURCE: {source}")
            print(f"FAILED DESTINATION: {destination}")
            print(f"ERROR: {error}")
            raise
        
        print(f"Copied: {onedriveFile}")

    print(f"Copied {len(matchingFiles)} matching files to {quarantineDir}")
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
