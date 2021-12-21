"""
https://github.com/shu681/multiple-label-yolo5
bug报告请联系微信: oo-shu6-oo
"""

import cv2

from tkinter import *
import os, argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from functools import partial
winW = 1920
winH = 1080
pypath = "D:\label-sl"
# pypath = os.path.dirname(__file__)
global img
global point2, labels, txtfile, labelBox, origin_img, path, labels_zh
tkwin = None
point1 = []
width = 960
height = 540

text_size = 18
font = ImageFont.truetype("{}/bdata.TTF".format(pypath), text_size, encoding="utf-8")

def on_mouse(event, x, y, flags, param):
    global img, point1, point2, labelBox, tkwin
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
        x1, y1, x2, y2 = min_x, min_y, min_x + width, min_y + height
        labelBox = [x1, y1, x2, y2]
        # threading.Thread(target=openMenu, args=(), daemon=True).start()
        if tkwin is not None:
            try:
                tkwin.destroy()
            except:
                tkwin = None
            tkwin = None
        openMenu()
def selectValue(value):
    global img, tkwin
    value = value.strip('\n')
    tkwin.destroy()
    tkwin = None
    lines = [x.strip() for x in open(txtfile, 'r').readlines()]
    newLines = []
    selected = 0
    for n, line in enumerate(lines):
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
            # print(value)
            selected += 1
            if value == '删除':
                continue
            else:
                points[0] = str(labels_zh.index(value))
        newLines.append(' '.join(points))
    
    if selected == 0 and value != '删除':
        [ox1, oy1, ox2, oy2] = labelBox
        ow, oh = ox2 - ox1, oy2 - oy1
        centerX, centerY = ow / 2 + ox1, oh / 2 + oy1

        points = [
            str(labels_zh.index(value)),
            str(round(centerX / width, 6)),
            str(round(centerY / height, 6)),
            str(round(ow / width, 6)),
            str(round(oh / height, 6)),
        ]

        newLines.append(' '.join(points))
    open(txtfile, 'w').write('\n'.join(newLines))
    img = drawImg(origin_img)
    cv2.imshow(winname, img)

def openMenu():
    global tkwin
    tkwin = Tk()
    # variable = StringVar(tkwin)
    for label in labels_zh:
        menu = Button(tkwin, text=label, command=partial(selectValue, label))
        menu.pack(padx=5, pady=10, side=LEFT)
    menu = Button(tkwin, text='删除', command=partial(selectValue, '删除'))
    menu.pack(padx=5, pady=10, side=LEFT)
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
        drawY = y1 - text_size - 10
        if drawY < 20:
            drawY = y1 + h
        draw.text((x1, drawY), labels_zh[int(points[0])], (255, 255, 255), font=font)

    return np.array(pil_img)
import json
def main():
    global img, labels, txtfile, winname, origin_img, path, labels_zh
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, default='', help='source')
    args = parser.parse_args()
    path = args.path

    file = open('{}/classes.txt'.format(pypath), "r")
    lastfile = open('{}/last.txt'.format(pypath), "r")
    last = lastfile.read()
    lastfile.close()
    if last == '':
        last = '{}'
    last = json.loads(last)
    
    labels = [x.strip() for x in file.readlines()]
    labels_zh = [x.strip() for x in open('{}/classes_zh.txt'.format(pypath), "r", encoding ='utf-8').readlines()]
    # class_dic_tozh = dict(zip(labels, labels_zh))
    # class_dic_toen = dict(zip(labels_zh, labels))
    
    files = [file for file in os.listdir(path) if file.endswith('.jpg')]
    index = 0
    pathUnicode = path.encode('unicode-escape').decode()
    if pathUnicode in last:
        index = int(last[pathUnicode])
    while index >= 0 and index < len(files):
        file = files[index]
        img = cv2.imdecode(np.fromfile('{}/{}'.format(path, file), dtype=np.uint8),-1)
        origin_img = img.copy()
        winname = '{} {}/{}'.format(file, index + 1, len(files))
        cv2.namedWindow(winname)

        txtfile = '{}/{}'.format(path, file).replace('.jpg', '.txt')
        img = drawImg(img)
        cv2.moveWindow(winname, int((winW - 960) / 2), int((winH - 540) / 2))
        cv2.setMouseCallback(winname, on_mouse)
        cv2.imshow(winname, img)

        last[pathUnicode] = index
        key = cv2.waitKeyEx(0)
        # print(key)
        if key == 2359296:
            cv2.destroyWindow(winname)
            index = 0
            continue
        if key == 2293760:
            cv2.destroyWindow(winname)
            index = len(files) - 1
            continue
        if key & 0xff == ord("n") or key == 2555904:
            cv2.destroyWindow(winname)
            index += 1
            if index == len(files):
                index = 0
            continue
        if key & 0xff == ord("p") or key == 2424832:
            cv2.destroyWindow(winname)
            index -= 1
            if index == -1:
                index = len(files) - 1
            continue
        if key & 0xff == ord("q"):
            break
    lastfile = open('{}/last.txt'.format(pypath), "w")
    lastfile.write(json.dumps(last))
    lastfile.close()
 
if __name__ == '__main__':
    main()

