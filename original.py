import os

onedriveDir = "/Volumes/Storage/OneDrive/Resimler/Film Rulosu"
immichDir = "/Volumes/Storage/immich/library/admin/Photos"

onedriveFolderNames = []
immichFolderNames = []

for root, dirs, files in os.walk(onedriveDir):
    for folderName in dirs:
        if os.path.isdir(os.path.join(root, folderName)):
            onedriveFolderNames.append(os.path.join(root, folderName))
            

for root, dirs, files in os.walk(immichDir):
    for folderName in dirs:
        if os.path.isdir(os.path.join(root, folderName)):
            immichFolderNames.append(os.path.join(root, folderName))

onedriveFolderNames.sort()
immichFolderNames.sort()

for folder in onedriveFolderNames:
    for subfolder in os.listdir(folder):
        if os.path.isdir(os.path.join(folder, subfolder)):
            onedriveFolderNames.remove(folder)
            break



matchingFolders = []

for folderOnedrive in onedriveFolderNames:
    for folderimmich in immichFolderNames:
        if os.path.basename(folderOnedrive) == os.path.basename(folderimmich):
            matchingFolders.append((folderOnedrive, folderimmich))
#            print(f"Matching folders: {folderOnedrive} and {folderimmich}")

for folderOnedrive, folderimmich in matchingFolders:
    for root, dirs, files in os.walk(folderOnedrive):
        for fileName in files:
            onedriveFilePath = os.path.join(root, fileName)
            immichFilePath = os.path.join(folderimmich, fileName)

            if os.path.exists(immichFilePath):
                print(f"File already exists in Immich: {immichFilePath}")