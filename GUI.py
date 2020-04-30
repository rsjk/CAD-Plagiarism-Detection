# importing tkinter module 
from tkinter import *
from tkinter.ttk import *
import time 
   
# Progress bar widget 


class GUI(Tk):

    def __init__(self):
        Tk.__init__(self)
        self.title('CAD Plagiarism Detetction')
        self.geometry('400x400')
        frame = Frame(self)
        frame.pack()
        
        #loadLabel = (frame, text='0/200')
        self.progress = Progressbar(frame, orient = HORIZONTAL, 
              length = 100, mode = 'determinate')
        self.progress.pack(pady = 10)
        self.startButton = Button(frame, text = 'Start', command = self.bar)
        self.startButton.pack(pady = 10)
        
    # Function responsible for the updation 
    # of the progress bar value 
    def bar(self):
        done = 0
        tot = 200
        for done in range(tot):
            self.progress['value'] = (done/tot)*100
            self.update() 
            time.sleep(1)  
  
# This button will initialize 
# the progress bar 
 
  
# infinite loop 
if __name__ == '__main__':
    GUI().mainloop()



