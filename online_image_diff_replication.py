from PIL import Image
import math

def comparePixels(px1, px2, num):
    same = True
    for i in range(3):
        #print(px1[i], px2[i])
        #print((px1[i] - px2[i]))
        if(abs(px1[i] - px2[i]) > num):
            same = False
    return same

#Open first image
im = Image.open("sample_image.jpg")
#print(im.format, im.size, im.mode)

#Open second image
im2 = Image.open("sample_image_2.jpg")
#print(im2.format, im2.size, im2.mode)

#fuzz input
fuzz = int(input("Enter fuzz: "))

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
            
print("Number of pixels that differ:", diffpixelcount)
print("Ratio of different pixels to total pixels:", diffpixelcount/(im.size[0]*im.size[1]))
im.save("diff.jpg")
diff = Image.open("diff.jpg")
diff.show()
            
