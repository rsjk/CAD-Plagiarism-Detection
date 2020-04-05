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
from random import randint
import tarfile
import os
from google_drive_downloader import GoogleDriveDownloader as gdd

def setupEnvironment():
    if(not os.path.isdir('C:\poppler-0.68.0')):
        gdd.download_file_from_google_drive(file_id='1aslGtTKrj6iW6sJ2cOnwpG1T_Up8EYxF',
                                    dest_path='C:\poppler.zip',
                                    unzip=True)
        os.remove("poppler.zip")

    path = "C:\poppler-0.68.0\\bin"

    os.environ["PATH"] += os.pathsep + path
    #print(os.environ.get("PATH"))

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

    for page in pages:   
        page.save(new_path, 'JPEG')

def convertToImages(folder_path, images_path):
    # Loop through directory, converting PDFs to JPGs
    for entry in os.listdir(folder_path):
        path = os.path.join(folder_path, entry)
        if os.path.isfile(path):
            # Check file type
            if checkFileType(path) == 'jpg':
                shutil.copy2(path, images_path)
            elif  checkFileType(path) == 'pdf':
                # Must convert to jpg
                convertToImage(folder_path, images_path, entry)
            else:
                print('File type not supported')

def Nmaxelements(list1, N): 
    final_list = []
    
    for i in range(0, N):  
        max1 = 0
        num = 0
          
        for j in range(len(list1)):
            if list1[j][1] > max1: 
                max1 = list1[j][1]
                num = list1[j][0]
                  
        list1.remove((num,max1))
        final_list.append((num,max1))
        
    return final_list

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
        res = cv2.matchTemplate(im2, crop_img, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        average_similarity = average_similarity + max_val
        
    average_similarity = average_similarity/len(BiggestContours)
    return average_similarity

def compareImages(images_path):
    # To keep track of processed images
    processed = []
    # Create log file
    logFile = open("log_" + time.strftime("%Y-%m-%d-%H-%M-%S") + ".csv", "a")
    for entry in os.listdir(images_path):
        if os.path.isfile(os.path.join(images_path, entry)):
            for entry2 in os.listdir(images_path):
                if os.path.isfile(os.path.join(images_path, entry2)) and entry != entry2 and frozenset((entry, entry2)) not in processed:
                    average_similarity = compareSubimages(images_path, entry, entry2)
                    if(average_similarity >= .774):
                        logFile.write(entry + ',' + entry2 + ', Suspicious' + '\n')
                        logFile.flush()
                    print(entry, entry2, 'comparison: ', average_similarity)               
                    #logFile.write(entry + ',' + entry2 + ',' + str(average_similarity) + '\n')
                    #logFile.flush()
                    processed.append(frozenset((entry, entry2)))
    # Delete images folder
    shutil.rmtree(images_path)
    # Close log file
    logFile.close()

if __name__ == '__main__':
    setupEnvironment()
    # Let user to choose a folder
    root = tkinter.Tk()
    root.withdraw()
    folder_path = askdirectory()
    
    # Make path to images folder. Tag on date and time for uniqueness.
    images_path = folder_path + '/images_' + time.strftime("%Y-%m-%d-%H-%M-%S")
    os.mkdir(images_path)

    # Convert PDFs to images if needed
    convertToImages(folder_path, images_path)

    # Compare the images
    compareImages(images_path)
 
