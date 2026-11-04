import os
import directories
from pathlib import Path

onedriveDir = directories.onedriveDir
immichDir = directories.immichDir

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
        for root, dirs, files in os.walk(onedriveMonth):
            for file in files:
                for immichRoot, immichDirs, immichFiles in os.walk(immichMonth):
                    if file in immichFiles:
                        onedriveFilePath = os.path.join(root, file)
                        immichFilePath = os.path.join(immichRoot, file)
                        matchingFiles.append((onedriveFilePath, immichFilePath))
    print(matchingFiles)
    return matchingFiles
# Script

onedriveFolderNames = collect_folders(onedriveDir, [])
immichFolderNames = collect_folders(immichDir, [])

onedriveYears = collect_subfolders(onedriveDir)
immichYears = collect_subfolders(immichDir)

onedriveMonths = collect_months(onedriveYears)
immichMonths = collect_months(immichYears)

matchingFolders = folders_match(onedriveMonths, immichMonths)

matchingFiles = files_match(matchingFolders)

#for folderOnedrive, folderimmich in matchingFolders:
#    for root, dirs, files in os.walk(folderOnedrive):
#        for fileName in files:
#            onedriveFilePath = os.path.join(root, fileName)
#            immichFilePath = os.path.join(folderimmich, fileName)
#
#            if os.path.exists(immichFilePath):
#                print(f"File already exists in Immich: {immichFilePath}")