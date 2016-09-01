#!/usr/bin/env python
# -*- coding: utf-8 ; mode: python -*-
#
# py-gdで絵を描く
#
# Copyright (C) 2015 Fujitsu

import gd
import sys
from nlcheck import NLCheck
from os.path import basename
import re
import nlclean

unit = 20 # 描画するときの、升目1つのサイズ

def test():
    img = gd.image((640,480))
    white = img.colorAllocate((255,255,255))
    black = img.colorAllocate((0,0,0))
    red = img.colorAllocate((255,0,0))
    blue = img.colorAllocate((0,0,255))
    green = img.colorAllocate((0,255,0))

    img.filledRectangle((0,0),(640,480),white)
    img.line((0,0),(640,480),red)

    img.string( gd.gdFontLarge, (20,240), "Hello World", black )
    img.rectangle( (20-2,240-2),(20+20,240+20), blue)

    img.writeGif("test.gif")

def xy(x,y):
    return (x*unit, y*unit)
    
def newImage(size):
    x,y,z = size
    img = gd.image( ((x+1)*unit, (y+1)*unit) )
    colors = { 'white': img.colorAllocate((255,255,255)),
               'black': img.colorAllocate((0,0,0)),
               'red': img.colorAllocate((255,0,0)),
               'blue': img.colorAllocate((0,0,255)),
               'green': img.colorAllocate((0,255,0)),
               'gray': img.colorAllocate((200,200,200)),
    }
    img.filledRectangle((0,0),(x*unit,y*unit), colors['white'])
    return img, colors

def drawGrid(img, colors, size):
    x,y,z = size
    cgray = colors['gray']
    for x0 in range(0,x):
        for y0 in range(0,y):
            #print x0,y0
            xx = x0*unit
            yy = y0*unit
            #print x0,y0,xx,yy
            img.rectangle( (xx,yy), (xx+unit,yy+unit), cgray )
            
def drawNumbers(img, colors, size, line_num, line_mat, layer):
    #print "line_mat shape =", line_mat.shape
    x,y,z = size
    cblue = colors['blue']
    cblack = colors['black']
    # ますの座標を描画
    for i in range(0,x):
        img.string( gd.gdFontLarge, (i*unit,y*unit), str(i), cblue )
    for i in range(0,y):
        img.string( gd.gdFontLarge, (x*unit,i*unit), str(i), cblue )
    # 数字
    for i in range(0, line_num):
        p = line_mat[i]
        #print "p=", p
        num = str(i+1)
        if p[2] == layer:
            img.string( gd.gdFontLarge, xy(p[0],p[1]), num, cblack )
        if p[5] == layer:
            img.string( gd.gdFontLarge, xy(p[3],p[4]), num, cblack )

def drawViaNumbers(img, colors, size, via_mat, via_dic, drawlayer):
    via_num = len(via_dic)
    layer_num = size[2]
    cblue = colors['blue']
    for via in range(0, via_num):
        for key,val in via_dic.items():
            if val == via+1:
                via_name = key
        for layer in range(0, layer_num):
            x = via_mat[via, layer*3+0]
            y = via_mat[via, layer*3+1]
            z = via_mat[via, layer*3+2]
            if drawlayer == z:
                s = via_name
                img.string( gd.gdFontLarge, xy(x,y), s, cblue )

def is_connected(xmat, x, y):
    "N,E,W,S方向と、番号が同じか？"
    x1 = 1 + x  # xmatでは、座標が1ずつずれるので
    y1 = 1 + y
    try:
        num = xmat[y1,x1]
    except IndexError, e:
        print "IndexError:", e
        return (False,False,False,False) # ???
    # n ■    上と同じ番号か？
    #   □
    n = (xmat[y1-1,x1] == num)
    # e   
    #   □■  右と同じ番号か？
    e = (xmat[y1,x1+1] == num)
    # w   
    # ■□    左と同じ番号か？
    w = (xmat[y1,x1-1] == num)
    #   □
    # s ■    下と同じ番号か？
    s = (xmat[y1+1,x1] == num)
    return (n,e,w,s)
    
def drawLines(img, colors, size, xmat):
    cblack = colors['black']
    cgray = colors['gray']
    for y in range(0, size[1]):
        for x in range(0, size[0]):
            x1 = 1 + x  # xmatでは、座標が1ずつずれるので
            y1 = 1 + y
            x0 = x*unit
            y0 = y*unit
            cx = x0 + unit/2
            cy = y0 + unit/2
            try:
                num = xmat[y1,x1]
            except IndexError, e:
                print "IndexError:", e
                num = -1
            if num == 0:
                img.filledRectangle((x0,y0),(x0+unit,y0+unit),cgray)
                continue
            n,e,w,s = is_connected(xmat, x, y) # x,yでOK
            if n:
                img.line( (cx,cy),(cx,y0), cblack)
            if e:
                img.line( (cx,cy),(x0+unit,cy), cblack)
            if w:
                img.line( (cx,cy),(x0,cy), cblack)
            if s:
                img.line( (cx,cy),(cx,y0+unit), cblack)
                
                
        
def draw(q, a, nlc):
    an = 0
    images = []
    for i in range(0, len(a)):
        mat = a[i]
        if mat.sum() == 0: # ログファイルを読み込んだとき、ゼロ行列がついてくるので、それを除外する
            continue
        xmat = nlc.extend_matrix(mat)
        #print "xmat.shape=", xmat.shape
        #print "xmat=", xmat
        for j in range(1, xmat.shape[0]-1):
            # Z軸方向でループ。0番とラストは、extendしたカラッポの層
            #print "j=%d\n" % j, xmat[j]
            img, colors = newImage(q[0])
            drawGrid(img, colors, q[0])
            drawNumbers(img, colors, q[0], q[1], q[2], j)
            drawViaNumbers(img, colors, q[0], q[3], q[4], j)
            drawLines(img, colors, q[0], xmat[j])
            #file = "nldraw.%d.gif" % an
            #img.writeGif(file)
            images.append(img)
            an += 1
    return images

def main():
    qfile, afile = sys.argv[1:]
    afile = sys.argv[2]
    print qfile,afile
    nlc = NLCheck()
    q = nlc.read_input_file(qfile)
    a = nlc.read_target_file(afile)
    #print "q=",q
    #print "a=",a
    #a = nlc.clean_a(q, a)
    # 回答をチェックする
    nlc.verbose = True
    judges = nlc.check( q, a )
    print "judges = ", judges
    # 描画する
    images = draw(q,a,nlc)
    bfile = basename(qfile)
    bfile = re.sub("\.txt", "", bfile)
    num = 0
    for img in images:
        ifile = "%s.%d.gif" % (bfile, num)
        img.writeGif(ifile)
        print ifile
        num += 1
    

if __name__ == "__main__":
    main()
