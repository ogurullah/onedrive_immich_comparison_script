import os
import directories

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

def folders_match(folders1, folders2, matchingFolders):
    for folder1 in folders1:
        for folder2 in folders2:
            if os.path.basename(folder1) == os.path.basename(folder2):
                matchingFolders.append((folder1, folder2))
    return matchingFolders

def has_subfolders(folder):
    if any(os.path.isdir(os.path.join(folder, subfolder)) for subfolder in os.listdir(folder)):
         folder.append(folder)

def remove_subfolders(folderList, subfolderList):
    for folder in folderList:
        if any(os.path.commonpath([folder, subfolder]) == folder for subfolder in subfolderList):
            folderList.remove(folder)

# Script

onedriveFolderNames = collect_folders(onedriveDir, [])
immichFolderNames = collect_folders(immichDir, [])

print(onedriveFolderNames)
print(immichFolderNames)

#hasSubfoldersOnedrive = []
#hasSubfoldersImmich = []

#hasSubfoldersOnedrive = has_subfolders(onedriveFolderNames)
#hasSubfoldersImmich = has_subfolders(immichFolderNames)

#remove_subfolders(onedriveFolderNames, hasSubfoldersOnedrive)
#remove_subfolders(immichFolderNames, hasSubfoldersImmich)

#matchingFolders = []
#matchingFolders = folders_match(onedriveFolderNames, immichFolderNames, matchingFolders)

#for folderOnedrive, folderimmich in matchingFolders:
#    for root, dirs, files in os.walk(folderOnedrive):
#        for fileName in files:
#            onedriveFilePath = os.path.join(root, fileName)
#            immichFilePath = os.path.join(folderimmich, fileName)
#
#            if os.path.exists(immichFilePath):
#                print(f"File already exists in Immich: {immichFilePath}")