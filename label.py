"""

bug报告请联系微信“”
"""

import cv2

from tkinter import *
import os, argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from functools import partial
winW = 1920
winH = 1080
pypath = os.path.dirname(__file__)
global img, tkwin
global point2, labels, txtfile, labelBox, origin_img, path
point1 = []
width = 960
height = 540
lastLabel = 'bird'

text_size = 10
font = ImageFont.truetype("{}/bdata.TTF".format(pypath), text_size, encoding="utf-8")

def on_mouse(event, x, y, flags, param):
    global img, point1, point2, labelBox
    img2 = img.copy()
    if event == cv2.EVENT_LBUTTONDOWN:         #左键点击
        point1 = (x,y)
        cv2.circle(img2, point1, 10, (0,255,0), 2)
        cv2.imshow(winname, img2)
    elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON):               #按住左键拖曳
        cv2.rectangle(img2, point1, (x,y), (255,0,0), 2)
        cv2.imshow(winname, img2)
    elif event == cv2.EVENT_LBUTTONUP:         #左键释放
        point2 = (x,y)
        min_x = min(point1[0],point2[0])     
        min_y = min(point1[1],point2[1])
        width = abs(point1[0] - point2[0])
        height = abs(point1[1] -point2[1])
        if width < 5:
            return
        cv2.rectangle(img2, point1, point2, (0,0,255), 2) 
        cv2.imshow(winname, img2)
        x1, x2, y1, y2 = min_x, min_y, min_x + width, min_y + height
        labelBox = [x1, x2, y1, y2]
        # threading.Thread(target=openMenu, args=(), daemon=True).start()
        openMenu()
def selectValue(value):
    # print(value)
    global lastLabel, img
    value = value.strip('\n')
    lastLabel = value
    # print(labels, lastLabel)
    valIndex = labels.index(lastLabel)
    tkwin.destroy()
    lines = [x.strip() for x in open(txtfile, 'r').readlines()]
    newLines = []
    for line in lines:
        points = line.split(' ')
        w = width * float(points[3])
        h = height * float(points[4])
        x1 = float(points[1]) * width - w / 2
        y1 = float(points[2]) * height - h / 2
        x2 = x1 + w
        y2 = y1 + h
        x1, x2, y1, y2 = int(x1), int(x2), int(y1), int(y2)
        centerX = x1 + w/2
        centerY = y1 + h/2
        if centerX > labelBox[0] and centerX < labelBox[2] and centerY > labelBox[1] and centerY < labelBox[3]:
            points[0] = str(valIndex)
        newLines.append(' '.join(points))
    # print('\n'.join(newLines))
    open(txtfile, 'w').write('\n'.join(newLines))
    img = drawImg(origin_img)
    cv2.imshow(winname, img)

def openMenu():
    global lastLabel, tkwin
    tkwin = Tk()
    # variable = StringVar(tkwin)
    for label in labels:
        menu = Button(tkwin, text=label, command=partial(selectValue, label))
        menu.pack(padx=5, pady=10, side=LEFT)
    # variable.set(lastLabel)
    mainloop()

def drawImg(img):
    lines = [x.strip() for x in open(txtfile, 'r').readlines()] 
    for line in lines:
        points = line.split(' ')
        w = width * float(points[3])
        h = height * float(points[4])
        x1 = float(points[1]) * width - w / 2
        y1 = float(points[2]) * height - h / 2
        x2 = x1 + w
        y2 = y1 + h
        x1, x2, y1, y2 = int(x1), int(x2), int(y1), int(y2)
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 255), 1)
    
    pil_img = Image.fromarray(img)
    draw = ImageDraw.Draw(pil_img)
    for line in lines:
        points = line.split(' ')
        w = width * float(points[3])
        h = height * float(points[4])
        x1 = float(points[1]) * width - w / 2
        y1 = float(points[2]) * height - h / 2
        x2 = x1 + w
        y2 = y1 + h
        x1, x2, y1, y2 = int(x1), int(x2), int(y1), int(y2)
        draw.text((x1, y1 - text_size - 10), labels[int(points[0])], (255, 255, 255), font=font)

    return np.array(pil_img)

import threading
def main():
    global img, labels, txtfile, winname, origin_img, path
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, default='', help='source')
    args = parser.parse_args()
    path = args.path


    # path = '{}'.format(path)
    # path = './'
    file = open('{}/classes.txt'.format(pypath), "r")
    labels = [x.strip() for x in file.readlines()]
    files = os.listdir(path)
    # threading.Thread(target=openMenu, args=(), daemon=True).start()
    # return
    for file in files:
        if '.txt' in file:
            continue
        # img = cv2.imread('{}/{}'.format(path, file))
        img = cv2.imdecode(np.fromfile('{}/{}'.format(path, file), dtype=np.uint8),-1)
        origin_img = img.copy()
        winname = file
        cv2.namedWindow(winname)

        txtfile = '{}/{}'.format(path, file).replace('.jpg', '.txt')
        img = drawImg(img)
        cv2.moveWindow(winname, int((winW - 960) / 2), int((winH - 540) / 2))
        cv2.setMouseCallback(winname, on_mouse)
        cv2.imshow(winname, img)

        key = cv2.waitKey(0)
        if key & 0xff == ord("n"):
            cv2.destroyWindow(winname)
            continue
        if key & 0xff == ord("q"):
            break
 
if __name__ == '__main__':
    main()

