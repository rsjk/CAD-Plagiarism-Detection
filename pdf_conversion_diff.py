from PIL import Image
import math
import os
import tkinter
from tkinter.filedialog import askdirectory
from pdf2image import convert_from_path
import filetype
import shutil

def checkFileType(path):
    # Check file type
    kind = filetype.guess(path)
    #print('kind: ' + str(kind.extension))
    if kind is None:
        print('Cannot use file type')
        return
    return kind.extension

def convertToImage(basepath, save_path, pdf):
    # Must convert to jpg
    pages = convert_from_path(basepath + "/" + pdf)
    
    image = pdf.replace('PDF', 'jpg')
    new_path = save_path + "/" + image
    #print('new path: ' + new_path)

    for page in pages:   
        page.save(new_path, 'JPEG')

def comparePixels(px1, px2, num):
    same = True
    for i in range(3):
        #print(px1[i], px2[i])
        #print((px1[i] - px2[i]))
        if(abs(px1[i] - px2[i]) > num):
            same = False
    return same

def compareImages(basepath, image1, image2, fuzz):
    print("Computing difference between", image1, "and", image2)
    #Open first image
    im = Image.open(basepath + "/" + image1)
    #print(im.format, im.size, im.mode)

    #Open second image
    im2 = Image.open(basepath + "/" + image2)
    #print(im2.format, im2.size, im2.mode)

    #load the images for pixel access
    px = im.load()
    px2 = im2.load()

    #initialize a counter for tracking number of pixels differing
    diffpixelcount = 0

    #Check if the dimensions of the images match
    if im.size != im2.size:
        print("Error: Size of images do not match")
        exit()

    #iterate through the pixels and check for similarity
    for i in range(im.size[0]):
        for j in range(im.size[1]):
            #print(px[i,j], px2[i,j])
            if(not comparePixels(px[i,j], px2[i,j], 255*fuzz/100)):
                px[i,j] = (255,0,0)
                diffpixelcount = diffpixelcount + 1
            else:
                px[i,j] = (math.floor(px[i,j][0]*.75),
                           math.floor(px[i,j][1]*.75),
                           math.floor(px[i,j][2]*.75))
                
    print("        Number of pixels that differ:", diffpixelcount)
    total_pixels = im.size[0]*im.size[1]
    print("        Ratio of different pixels to total pixels:", diffpixelcount/total_pixels)
    print("        Ratio of similarity:", ((im.size[0]*im.size[1]) - diffpixelcount)/total_pixels)

    # Make diff directory
    try:
        os.mkdir(basepath + '/diff')
    except FileExistsError:
        pass # error checking l8ter

    im.save(basepath + "/diff/" + image1 + " " + image2 + " - diff.jpg")
    #diff = Image.open(basepath + "/diff/" + image1 + " " + image2 + " - diff.jpg")
    #diff.show()

root = tkinter.Tk()
root.withdraw()

# Open Folder
folderpath = askdirectory()
print(folderpath)

# Make images folder
images_path = folderpath + '/images'
try:
    os.mkdir(images_path)
except FileExistsError:
    pass # error checking l8ter

# Loop through directory, converting PDFs to JPGs
for entry in os.listdir(folderpath):
    path = os.path.join(folderpath, entry)
    if os.path.isfile(path):
        # Check file type
        if checkFileType(path) == 'jpg':
            shutil.copy2(path, images_path)
        elif  checkFileType(path) == 'pdf':
            # Must convert to jpg
            convertToImage(folderpath, images_path, entry)
        else:
            print('File type not supported')

# Fuzz input
fuzz = int(input("Enter fuzz: "))
processed = []

# Compare the images
for entry in os.listdir(images_path):
    if os.path.isfile(os.path.join(images_path, entry)):
        for entry2 in os.listdir(images_path):
            #print("Entry 1:", entry, "    Entry 2:", entry2)
            if os.path.isfile(os.path.join(images_path, entry2)) and entry != entry2 and frozenset((entry, entry2)) not in processed:
                compareImages(images_path, entry, entry2, fuzz)
                processed.append(frozenset((entry, entry2)))
                #print("Processed pairs:", processed)