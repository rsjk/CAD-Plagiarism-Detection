from pdf2image import convert_from_path
from random import randint
from tkinter import Button, filedialog, Entry, Frame, Label, Listbox, messagebox, Scale, Scrollbar, Tk
from tkinter.ttk import Progressbar
import cv2
import filetype
import math
import numpy as np
import os
import shutil
import subprocess
import threading
import time


class CPDApp(Tk):
    def __init__(self):
        # Poppler setup
        path = "poppler-0.68.0\\bin"
        os.environ["PATH"] += os.pathsep + path
        
        # Initialize
        Tk.__init__(self)
        self.title('CAD Plagiarism Detetctor')
        
        h = 490
        w = 400

        # Get screen height and width
        hs = self.winfo_screenheight() # height of the screen
        ws = self.winfo_screenwidth() # width of the screen

        # Calculate x and y coordinates
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)

        # Set window in the middle of the screen
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))

        # Set GUI elements
        frame = Frame(self)
        frame.pack()

        sus_label = Label(frame, text='Suspicious Pairs')
        sus_label.grid(row=0, column=1)

        self.progress_bar = Progressbar(frame, orient='horizontal', length=100, mode='determinate')
        self.progress_bar.grid(row=1, column=1, pady=(0,3))
        self.progress_bar.grid_remove()

        listbox_frame = Frame(frame)
        listbox_frame.grid(row=2, column=0, columnspan=3)

        self.sus_listbox = Listbox(listbox_frame, width=40, height=15, selectmode='single')
        self.sus_listbox.pack(side='left', fill='y')
        self.sus_listbox.bind('<<ListboxSelect>>', self.displayFile)
        scrollbar = Scrollbar(listbox_frame, orient='vertical')
        scrollbar.config(command=self.sus_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.sus_listbox.config(yscrollcommand=scrollbar.set)

        self.mask_button = Button(frame, text='Mask', width=12, command=self.chooseMask)
        self.mask_button.grid(row=3, column=0, pady=(3,0))

        self.input_button = Button(frame, text='Input Folder', width=12, command=self.chooseInputFolder)
        self.input_button.grid(row=3, column=1, pady=(3,0))

        self.output_button = Button(frame, text='Output Folder', width=12, command=self.chooseOutputFolder)
        self.output_button.grid(row=3, column=2, pady=(3,0))

        subsection_label = Label(frame, text='Subsections:')
        subsection_label.grid(row=4, column=0, columnspan=2, pady=(3,0))

        self.subsection_entry = Entry(frame, width=12)
        self.subsection_entry.grid(row=4, column=1, columnspan=2, pady=(3,0))

        log_name_label = Label(frame, text='Output File Name:')
        log_name_label.grid(row=5, column=0, columnspan=2, pady=(3,0))

        self.log_name_entry = Entry(frame, width=12)
        self.log_name_entry.grid(row=5, column=1, columnspan=2, pady=(3,0))

        slider_label = Label(frame, text='Sensitivity')
        slider_label.grid(row=6, column=1, pady=(3,0))

        lenient_label = Label(frame, text='Lenient')
        lenient_label.grid(row=7, column=0, pady=(3,0), sticky='e')

        strict_label = Label(frame, text='Strict  ')
        strict_label.grid(row=7, column=2, pady=(3,0), sticky='w')

        self.slider = Scale(frame, from_=0.7, to=0.848, orient='horizontal', resolution=0.001, showvalue=0)
        self.slider.set(0.774)
        self.slider.grid(row=7, column=1, pady=(3,0))

        self.reset_button = Button(frame, text='Reset Sensitivity', width=12, command=self.resetSensitivity)
        self.reset_button.grid(row=8, column=1, pady=(3,0))

        self.start_button = Button(frame, text='Start', width=12, command=self.start)
        self.start_button.grid(row=9, column=1, pady=(10,0))

        self.mask_path = ''   # Path to mask file
        self.output_path = '' # Path to where the log will be placed
        self.input_path = ''  # Path to input files
        self.images_path = '' # Path to converted files

        self.image_folder_list = [] # List of image folders

        self.file_names = {} # Dictionary of the PDF names

        self.file_count = 0 # Number of files

        self.num_subsections = 7 # Number of subsections within the images

        self.sensitivity = self.slider.get() # Sensitivity when determining plagiarism

        # What to do on close
        self.protocol("WM_DELETE_WINDOW", self.close)

    def start(self):
        # Clear listbox
        self.sus_listbox.delete(0, 'end')

        # Check that user provided input
        if (self.subsection_entry.get() == '') or (self.log_name_entry.get() == '')  or (not self.mask_path) or (not self.output_path) or (not self.input_path):
            messagebox.showinfo('CAD Plagiarism Detector', 'Please provide input needed for processing.')
            return

        # Check that subsections is a number
        try:
            self.num_subsections = int(self.subsection_entry.get())
        except ValueError:
            messagebox.showerror('CAD Plagiarism Detector', 'Subsections must be a number.')
            return

        # Disable input
        self.toggleInputState()

        # Show progress bar
        self.progress_bar.grid()

        # Make path to images folder. Tag on date and time for uniqueness.
        self.images_path = self.input_path + '/images_' + time.strftime("%Y-%m-%d-%H-%M-%S")
        os.mkdir(self.images_path)

        # Add to image folder list
        self.image_folder_list.append(self.images_path)

        # Compare the images
        self.processing_thread = threading.Thread(target=self.compareImages, name='processing_thread', daemon=True)
        self.processing_thread.start()


    def close(self):
        # Delete image folders if it still exists
        for i in self.image_folder_list:
            try:
                shutil.rmtree(i) 
            except PermissionError:
                messagebox.showerror('CAD Plagiarism Detector', 'Unable to delete images folder.')
        self.destroy()


    def toggleInputState(self):
        # Toggle button state to 'normal' or 'disabled'
        if self.mask_button['state'] == 'normal':
            self.mask_button['state'] = 'disabled'
        else:
            self.mask_button['state'] = 'normal'
        if self.output_button['state'] == 'normal':
            self.output_button['state'] = 'disabled'
        else:
            self.output_button['state'] = 'normal'
        if self.input_button['state'] == 'normal':
            self.input_button['state'] = 'disabled'
        else:
            self.input_button['state'] = 'normal'
        if self.start_button['state'] == 'normal':
            self.start_button['state'] = 'disabled'
        else:
            self.start_button['state'] = 'normal'
        if self.subsection_entry['state'] == 'normal':
            self.subsection_entry['state'] = 'disabled'
        else:
            self.subsection_entry['state'] = 'normal'
        if self.log_name_entry['state'] == 'normal':
            self.log_name_entry['state'] = 'disabled'
        else:
            self.log_name_entry['state'] = 'normal'
        if self.slider['state'] == 'normal':
            self.slider['state'] = 'disabled'
        else:
            self.slider['state'] = 'normal'
        if self.reset_button['state'] == 'normal':
            self.reset_button['state'] = 'disabled'
        else:
            self.reset_button['state'] = 'normal'


    def chooseMask(self):
        self.mask_path = filedialog.askopenfilename()


    def chooseOutputFolder(self):
        self.output_path = filedialog.askdirectory()


    def chooseInputFolder(self):
        self.input_path = filedialog.askdirectory()

    
    def resetSensitivity(self):
        # Reset sensitivity slider to default
        self.slider.set(0.774)


    def displayFile(self, event):
        # Display selected files from the listbox
        w = event.widget
        try:
            index = w.curselection()[0]
            value = w.get(index)

            path1 = ''
            path2 = ''
            try:
                path1 = self.input_path + '/' + value[0] + '_' + self.file_names[value[0]]
                path2 = self.input_path + '/' + value[2] + '_' + self.file_names[value[2]]
            except KeyError:
                # Listbox just contains file names
                path1 = self.input_path + '/' + value[0]
                path2 = self.input_path + '/' + value[2]

            subprocess.Popen([path1], shell=True)
            subprocess.Popen([path2], shell=True)

        except IndexError: # If user clicks the listbox before anything is in it 
            pass


    def checkFileType(self, path):
        # Check file type
        kind = filetype.guess(path)
        if kind is None:
            messagebox.showerror('CAD Plagiarism Detector', 'Unable to determine file type.')
            return
        return kind.extension


    def convertToImage(self, pdf):
        # Must convert to jpg
        pages = convert_from_path(self.input_path + "/" + pdf)
    
        image = pdf.replace('PDF', 'jpg')
        image_path = self.images_path + "/" + image

        for page in pages:   
            page.save(image_path, 'JPEG')


    def convertToImages(self):
        self.file_count = 0
        valid = False

        # Loop through directory, converting PDFs to JPGs
        for entry in os.listdir(self.input_path):
            path = os.path.join(self.input_path, entry)
            if os.path.isfile(path):
                # Check file type
                if self.checkFileType(path) == 'pdf':
                    self.convertToImage(entry)  # Must convert to jpg
                    self.file_count += 1 # Need a file count for the progress bar
                    
                    # Make a dictionary mapping student names to the rest of the file names
                    # Needed for displaying the PDFs upon clicking a pair in the listbox
                    entry_split = entry.split('_', 1)
                    try:
                        self.file_names[entry_split[0]] = entry_split[1]
                    except IndexError: 
                        # File name might not be formatted in expected way with name_number.. etc.
                        # In this case, there's no need to make a dictionary, listbox will just have the file name
                        pass

                    valid = True # Set to valid
                # Not a PDF
                else:
                    messagebox.showerror('CAD Plagiarism Detector', 'File type is not PDF.')

        # Need to have a pair to compare
        if self.file_count < 2:
            valid = False
        return valid


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
        mask = cv2.imread(self.mask_path, 0)
        res = cv2.bitwise_and(im, im, mask = mask)

        imgray = cv2.cvtColor(res,cv2.COLOR_BGR2GRAY)
        ret,thresh = cv2.threshold(imgray,127,255,0)

        contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        num = 0
        contourArea = []
        for i in contours:
            contourArea.append((num, cv2.contourArea(i)))
            num = num + 1
    
        #We add 3 to the number of contours we're looking for since we need to account for the popping of the largest contour from the mask
        #and to ensure we catch all subsections that need to be compared
        BiggestContours = self.Nmaxelements(contourArea, self.num_subsections + 3)
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
        # Convert to images if needed
        valid = self.convertToImages()
        if not valid: # If there are no valid files, return
            # Tell user
            messagebox.showerror('CAD Plagiarism Detector', 'Files not valid for processing.')

            # Enable buttons and entry again
            self.toggleInputState()
            return

        # Number of files in self.file_count
        # Find number of possible pairs
        num_pairs = math.factorial(self.file_count) / (math.factorial(2)*math.factorial(self.file_count - 2))

        # To keep track of processed images
        processed = []

        # Create log file
        log_file_path = self.output_path + '/' + str(self.log_name_entry.get()) + '_' + time.strftime('%Y-%m-%d-%H-%M-%S') + '.csv'
        log_file = open(log_file_path, 'a')
        
        # Process the files
        count = 0
        for entry in os.listdir(self.images_path):
            if os.path.isfile(os.path.join(self.images_path, entry)):
                for entry2 in os.listdir(self.images_path):
                    if os.path.isfile(os.path.join(self.images_path, entry2)) and entry != entry2 and frozenset((entry, entry2)) not in processed:
                        count += 1

                        # Find average similarity
                        average_similarity =self.compareSubimages(entry, entry2)

                        # Get sensitivity
                        self.sensitivity = self.slider.get() 
                        
                        # Make list to go in listbox
                        inner_list = []
                        
                        # Return the first chunk of student name, up to the first underscore (_)
                        entry_split = entry.split('_', 1) 
                        first_name = entry_split[0]
                        entry2_split = entry2.split('_', 1)
                        second_name = entry2_split[0]

                        # If input isn't formatted in the expected way -- name_number_... etc, put file name in the listbox
                        if '.jpg' in first_name:
                            first_name = first_name.replace('.jpg', '.pdf')
                        if '.jpg' in second_name:
                            second_name = second_name.replace('.jpg', '.pdf')

                        # Add names to list
                        inner_list.append(first_name)
                        inner_list.append('and')
                        inner_list.append(second_name)
                        
                        if average_similarity >= self.sensitivity and average_similarity <= 0.98:
                            # Write to log file 
                            log_file.write(entry + ',' + entry2 + ',' + ', Suspicious\n')
                            log_file.flush()
                            # Add list to listbox
                            self.sus_listbox.insert('end', inner_list)
                            self.update()
                        elif average_similarity > 0.98:
                            # Write to log file 
                            log_file.write(entry + ',' + entry2 + ',' + ', Very Suspicious\n')
                            log_file.flush()
                            # Add list to listbox
                            self.sus_listbox.insert('end', inner_list)
                            self.update()

                        # Mark as processed
                        processed.append(frozenset((entry, entry2)))

                        # Update progress bar
                        self.progress_bar['value'] = (count/num_pairs)*100
                        self.update()
                        time.sleep(1)

        # Show that comparisons are complete
        messagebox.showinfo('CAD Plagiarism Detector', 'Done processing files.')
        
        # Enable buttons and entry again
        self.toggleInputState()

        # Make progress bar invisible and reset to 0
        self.progress_bar['value'] = 0
        self.progress_bar.grid_remove()
        
        # Close log file
        log_file.close()


if __name__ == '__main__':
    CPDApp().mainloop()
