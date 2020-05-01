from tkinter import *
from tkinter.ttk import *
import time 


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
        self.doneLabel = Label(frame, text='0/200')
        self.startButton = Button(frame, text = 'Start', command = self.bar)
        self.doneLabel.pack()
        self.startButton.pack(pady = 10)
        
    # Function responsible for the updation 
    # of the progress bar value and label
    def bar(self):
        done = 0 #should start at 0
        tot = 10 #whatever number of comparisons are left
        str = "{}/{}".format(done, tot)
        for done in range(tot+1):
            str = "{}/{}".format(done, tot)
            self.progress['value'] = (done/tot)*100
            self.doneLabel['text'] = str
            self.update() 
            time.sleep(1)  
  

if __name__ == '__main__':
    GUI().mainloop()



