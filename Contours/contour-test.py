import numpy as np
import cv2

def Nmaxelements(list1, N): 
    final_list = []
    
    for i in range(0, N):  
        max1 = 0
        num = 0
          
        for j in range(len(list1)):
            if list1[j][1] > max1: 
                max1 = list1[j][1];
                num = list1[j][0];
                  
        list1.remove((num,max1)); 
        final_list.append((num,max1))
        
    return final_list

im = cv2.imread('test.jpg')
mask = cv2.imread('mask.jpg', 0)
res = cv2.bitwise_and(im, im, mask = mask)

imgray = cv2.cvtColor(res,cv2.COLOR_BGR2GRAY)
ret,thresh = cv2.threshold(imgray,127,255,0)

cv2.namedWindow('processing', cv2.WINDOW_NORMAL)
cv2.imshow('processing', thresh)

contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
num = 0
contourArea = []
for i in contours:
    #print((num, cv2.contourArea(i)))
    contourArea.append((num, cv2.contourArea(i)))
    num = num + 1
    

BiggestContours = Nmaxelements(contourArea, 10)
print(BiggestContours)

for i in BiggestContours:
    cv2.drawContours(im, contours, i[0], (0,255,0), 3)
    #x,y,w,h = cv2.boundingRect(contours[i[0]])
    #cv2.rectangle(im,(x,y),(x+w,y+h),(0,255,0),2)
                          
cv2.namedWindow('contours', cv2.WINDOW_NORMAL)
cv2.imshow('contours', im)
