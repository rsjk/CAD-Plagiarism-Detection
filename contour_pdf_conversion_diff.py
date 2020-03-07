from PIL import Image
import math
import os
import tkinter
from tkinter.filedialog import askdirectory
from pdf2image import convert_from_path
import filetype
import shutil
import numpy as np
import cv2
import time

def Nmaxelements(list1, N): 
    final_list = []
    
    for i in range(0, N):  
        max1 = 0
        num = 0
          
        for j in range(len(list1)):
            if list1[j][1] > max1: 
                max1 = list1[j][1]
                num = list1[j][0]
                  
        list1.remove((num,max1)); 
        final_list.append((num,max1))
        
    return final_list

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
    print("        Ratio of different pixels to total pixels:", diffpixelcount/(im.size[0]*im.size[1]))

    # Make diff directory
    try:
        os.mkdir(basepath + '/diff')
    except FileExistsError:
        pass # error checking l8ter

    im.save(basepath + "/diff/" + image1 + " " + image2 + " - diff.jpg")
    #diff = Image.open(basepath + "/diff/" + image1 + " " + image2 + " - diff.jpg")
    #diff.show()

def compareSubimages(basepath, image1, image2):
    im = cv2.imread(basepath + "/" + image1)
    im2 = cv2.imread(basepath + "/" + image2)
    mask = cv2.imread('mask.jpg', 0)
    res = cv2.bitwise_and(im, im, mask = mask)

    imgray = cv2.cvtColor(res,cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(imgray,127,255,0)

    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    num = 0
    contourArea = []
    for i in contours:
        contourArea.append((num, cv2.contourArea(i)))
        num = num + 1
    
    BiggestContours = Nmaxelements(contourArea, 10)
    #pop the biggest contour which would the outline of the mask
    BiggestContours.pop(0)

    average_similarity = 0
    
    for i in BiggestContours:
        x,y,w,h = cv2.boundingRect(contours[i[0]])
        crop_img = im[y:y+h, x:x+w]
        #res = cv2.matchTemplate(im2, crop_img, cv2.TM_CCOEFF_NORMED)
        #res = cv2.matchTemplate(im2, crop_img, cv2.TM_CCORR_NORMED)
        res = cv2.matchTemplate(im2, crop_img, cv2.TM_SQDIFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        #print(min_val, max_val, min_loc, max_loc)
        #average_similarity = average_similarity + max_val
        average_similarity = average_similarity + (1.0 - min_val)
        
    average_similarity = average_similarity/len(BiggestContours)
    return average_similarity

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
#fuzz = int(input("Enter fuzz: "))
processed = []

# Compare the images
logFile = open("log_" + time.strftime("%Y-%m-%d-%H-%M-%S") + ".csv", "a")
for entry in os.listdir(images_path):
    if os.path.isfile(os.path.join(images_path, entry)):
        for entry2 in os.listdir(images_path):
            #print("Entry 1:", entry, "    Entry 2:", entry2)
            if os.path.isfile(os.path.join(images_path, entry2)) and entry != entry2 and frozenset((entry, entry2)) not in processed:
                #compareImages(images_path, entry, entry2, fuzz)
                print(entry, entry2, 'comparision: ', compareSubimages(images_path, entry, entry2))               
                logFile.write(entry + ',' + entry2 + ',' + str(compareSubimages(images_path, entry, entry2)) + '\n')
                logFile.flush()
                processed.append(frozenset((entry, entry2)))
                #print("Processed pairs:", processed)
logFile.close()
