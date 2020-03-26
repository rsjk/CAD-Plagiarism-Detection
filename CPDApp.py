from PIL import ImageTk, Image
from pdf2image import convert_from_path
from random import randint
from tkinter import Button, filedialog, Frame, Label, Listbox, Tk
import cv2
import filetype
import math
import numpy as np
import os
import shutil
import time

class CPDApp(Tk):

    def __init__(self):
        Tk.__init__(self)
        self.title('CAD Plagiarism Detetction')
        self.geometry('400x400')
        frame = Frame(self)
        frame.pack()

        sus_label = Label(frame, text='Suspicious Pairs')
        sus_label.grid(row=0, column=0)
        #images_label = Label(frame, text='Files')
        #images_label.grid(row=0, column=1, columnspan=2)

        self.sus_listbox = Listbox(frame, width=30, height=20, selectmode='single')
        self.sus_listbox.grid(row=1, column=0)
        self.sus_listbox.bind('<<ListboxSelect>>', self.displayImage)

        #self.canvas1 = Canvas(frame, width = 300, height = 300, bg='gray')
        #self.canvas1.grid(row=1, column=1)

        #self.canvas2 = Canvas(frame, width = 300, height = 300, bg = 'gray')
        #self.canvas2.grid(row=1, column=2)

        self.folder_button = Button(frame, text='Choose Folder', command = self.chooseFolder)
        self.folder_button.grid(row=2, column=0)

        self.images_path = ''

        self.protocol("WM_DELETE_WINDOW", self.close)


    def close(self):
        # Delete images folder
        if self.images_path:
            shutil.rmtree(self.images_path) 
        self.destroy()

    def chooseFolder(self):
        # Delete old images if they exist
        if self.images_path:
            shutil.rmtree(self.images_path)
            self.sus_listbox.delete(0, 'end')
        
        self.folder_path = filedialog.askdirectory()

        # Make path to images folder. Tag on date and time for uniqueness.
        self.images_path = self.folder_path + '/images_' + time.strftime("%Y-%m-%d-%H-%M-%S")
        os.mkdir(self.images_path)

        # Convert PDFs to images if needed
        self.convertToImages()

        # Compare the images
        self.compareImages()

    def displayImage(self, event):
        w = event.widget
        index = w.curselection()[0]
        value = w.get(index)
        path1 = self.images_path + '/' + value[0] + '.jpg'
        path2 = self.images_path + '/' + value[2] + '.jpg'
        image = Image.open(path1)
        image.show()
        image2 = Image.open(path2)
        image2.show()

        '''
        img = Image.open(path)
        self.canvas1.image = ImageTk.PhotoImage(img)
        self.canvas1.create_image(0,0,image=self.canvas1.image, anchor = 'nw')
        #print(self.images_path)
        path = self.images_path + '/' + value[0]
        img = ImageTk.PhotoImage('ball.jpg')
        self.canvas1.create_image(20,20, anchor=NW, image = img)
        '''

    def checkFileType(self, path):
        # Check file type
        kind = filetype.guess(path)
        # print('kind: ' + str(kind.extension))
        if kind is None:
            print('Cannot use file type')
            return
        return kind.extension

    def convertToImage(self, pdf):
        # Must convert to jpg
        pages = convert_from_path(self.folder_path + "/" + pdf)
    
        image = pdf.replace('PDF', 'jpg')
        image_path = self.images_path + "/" + image

        for page in pages:   
            page.save(image_path, 'JPEG')

    def convertToImages(self):
        # Loop through directory, converting PDFs to JPGs
        for entry in os.listdir(self.folder_path):
            path = os.path.join(self.folder_path, entry)
            if os.path.isfile(path):
                # Check file type
                if self.checkFileType(path) == 'jpg':
                    shutil.copy2(path, self.images_path)
                elif  self.checkFileType(path) == 'pdf':
                    # Must convert to jpg
                    self.convertToImage(entry)
                else:
                    print('File type not supported')

    def Nmaxelements(self, list1, N): 
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

    def compareSubimages(self, image1, image2):
        im = cv2.imread(self.images_path + "/" + image1)
        im2 = cv2.imread(self.images_path + "/" + image2)
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
    
        BiggestContours = self.Nmaxelements(contourArea, 10)
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

    def compareImages(self):
        # To keep track of processed images
        processed = []
        # Create log file
        #logFile = open("log_" + time.strftime("%Y-%m-%d-%H-%M-%S") + ".csv", "a")
        for entry in os.listdir(self.images_path):
            if os.path.isfile(os.path.join(self.images_path, entry)):
                for entry2 in os.listdir(self.images_path):
                    if os.path.isfile(os.path.join(self.images_path, entry2)) and entry != entry2 and frozenset((entry, entry2)) not in processed:
                        average_similarity =self.compareSubimages(entry, entry2)

                        # Print average similarity
                        #print(entry, entry2, 'comparison: ', average_similarity)    

                        # Write to log file    
                        #logFile.write(entry + ',' + entry2 + ',' + str(average_similarity) + '\n')
                        #logFile.flush()

                        # Add to average similarity list
                        inner_list = []
                        #entry = entry.replace('jpg', '')
                        #entry2 = entry2.replace('jpg', '')
                        inner_list.append(entry.replace('.jpg', ''))
                        inner_list.append('and')
                        inner_list.append(entry2.replace('.jpg', ''))
                        
                        if average_similarity >= 0.774:
                            self.sus_listbox.insert('end', inner_list)

                        # Mark as processed
                        processed.append(frozenset((entry, entry2)))
         
        # Close log file
        #logFile.close()


if __name__ == '__main__':
    '''
    root = Tk() 
    root.geometry('500x400')
    root.title('CAD Plagiarism Detection')
    CPDApp(root)
    root.mainloop()
    '''
    CPDApp().mainloop()