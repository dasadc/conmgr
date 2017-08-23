#!/usr/bin/env python
# -*- coding: utf-8 ; mode: python -*-
#
# Copyright (C) 2017 DA Symposium 2017


"""
python pillowで絵を描く
"""

from __future__ import print_function
from PIL import Image, ImageDraw, ImageFont
import sys
import os
from nlcheck import NLCheck


unit = 20 # 描画するときの、升目1つのサイズ

# 色, color
white = (255,255,255)
black = (0,0,0)
red = (255,0,0)
blue = (0,0,255)
green = (0,192,0)
gray = (200,200,200)
lightgray = (240,240,240)

# TrueTypeフォントファイル, font
ttf_font = './Ricty-Regular.ttf'

def get_font():
    if os.path.exists(ttf_font):
        font = ImageFont.truetype(ttf_font, size=14, encoding='unic')
    else:
        font = ImageFont.load_default()
    return font

def test():
    "ただの動作確認"

    img = Image.new('RGB', (640,480))
    d = ImageDraw.Draw(img)
    font = get_font()
    d.rectangle(xy=[(0,0),(640,480)], fill=white)
    d.line(xy=[(0,0),(640,480)], fill=red)
    text = u"こんにちは世界"
    #text = "Hello World 0123"
    size = font.getsize(text)
    xy = (20,240)
    d.text(xy=xy, text=text, fill=black, font=font)
    d.rectangle(xy=[(xy[0]-2, xy[1]-2),(xy[0]+size[0]+2, xy[1]+size[1]+2)], outline=blue)
    img.save("test.gif", 'gif')

def xy(x,y):
    "テキストを描画するときの座標を返す"
    #return (x*unit, y*unit)
    return (x*unit+1, y*unit+1)
    
def newImage(size):
    "PIL.ImageとPIL.ImageDrawを新しく作る"
    x,y,z = size
    img = Image.new('RGB', size=((x+1)*unit, (y+1)*unit), color=lightgray)
    d = ImageDraw.Draw(img)
    d.rectangle(xy=[(0,0),(x*unit,y*unit)], fill=white)
    return img, d

def drawGrid(d, size):
    "盤のマス目を描く"

    x,y,z = size
    for x0 in range(0,x):
        for y0 in range(0,y):
            #print(x0,y0)
            xx = x0*unit
            yy = y0*unit
            #print(x0,y0,xx,yy)
            d.rectangle( xy=[(xx,yy), (xx+unit,yy+unit)], outline=gray)
            
def drawNumbers(d, size, line_num, line_mat, layer):
    "盤の中の、マスの数字を描く"

    #print("line_mat shape =", line_mat.shape)
    x,y,z = size
    font = get_font()
    # ますの座標を描画
    for i in range(0,x):
        d.text(xy=xy(i, y), text=str(i), fill=blue, font=font)
    for i in range(0,y):
        d.text(xy=xy(x, i), text=str(i), fill=blue, font=font)
    # 数字
    for i in range(0, line_num):
        p = line_mat[i]
        #print("p=", p)
        num = str(i+1)
        if p[2] == layer:
            d.text(xy=xy(p[0],p[1]), text=num, fill=black, font=font)
        if p[5] == layer:
            d.text(xy=xy(p[3],p[4]), text=num, fill=black, font=font)

def drawViaNumbers(d, size, via_mat, via_dic, drawlayer):
    "viaの名前を描く"

    via_num = len(via_dic)
    layer_num = size[2]
    font = get_font()
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
                d.text(xy=xy(x,y), text=s, fill=green, font=font)

def is_connected(xmat, x, y):
    "N,E,W,S方向と、番号が同じか？"

    x1 = 1 + x  # xmatでは、座標が1ずつずれるので
    y1 = 1 + y
    try:
        num = xmat[y1,x1]
    except IndexError as e:
        print("IndexError:", e)
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
    
def drawLines(d, size, xmat):
    """
    線を描く。

    (x0,y0)
    .---------------+
    |               |
    |               |
    |       .(cx,cy)|
    |               |
    |               |
    +---------------+
    """

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
            except IndexError as e:
                print("IndexError:", e)
                num = -1
            if num == 0:
                d.rectangle(xy=[(x0,y0),(x0+unit,y0+unit)], fill=gray)
                continue
            n,e,w,s = is_connected(xmat, x, y) # x,yでOK
            if n:
                d.line(xy=[(cx,cy),(cx,y0)], fill=black)
            if e:
                d.line(xy=[(cx,cy),(x0+unit,cy)], fill=black)
            if w:
                d.line(xy=[(cx,cy),(x0,cy)], fill=black)
            if s:
                d.line(xy=[(cx,cy),(cx,y0+unit)], fill=black)

def draw(q, a, nlc):
    "ナンバーリンクの盤面を描く"
    images = []
    for i in range(0, len(a)):
        mat = a[i]
        if mat.sum() == 0: # ログファイルを読み込んだとき、ゼロ行列がついてくるので、それを除外する
            continue
        xmat = nlc.extend_matrix(mat)
        #print("xmat.shape=", xmat.shape)
        #print("xmat=", xmat)
        for j in range(1, xmat.shape[0]-1):
            # Z軸方向でループ。0番とラストは、extendしたカラッポの層
            #print("j=%d\n" % j, xmat[j])
            img, d = newImage(q[0])
            drawGrid(d, q[0])
            drawNumbers(d, q[0], q[1], q[2], j)
            drawViaNumbers(d, q[0], q[3], q[4], j)
            drawLines(d, q[0], xmat[j])
            images.append(img)
    return images

def merge_images(images):
    "imagesを横に並べて、1枚の画像にする"
    width, height = images[0].size
    img = Image.new('RGB', size=(width*len(images), height))
    for j, im in enumerate(images):
        img.paste(im=im, box=(width*j, 0))
    return img

def main():
    import argparse
    parser = argparse.ArgumentParser(description='NumberLink check and drawing tool')
    parser.add_argument('qfile', metavar='Q-FILE', help='input file (Q-file)')
    parser.add_argument('afile', metavar='A-FILE', help='target file (A-file)')
    args = parser.parse_args()
    qfile = args.qfile
    afile = args.afile
    print(qfile, afile)
    nlc = NLCheck()
    q = nlc.read_input_file(qfile)
    a = nlc.read_target_file(afile)
    #print("q=",q)
    #print("a=",a)
    #a = nlc.clean_a(q, a)
    # 回答をチェックする
    nlc.verbose = True
    judges = nlc.check( q, a )
    print("judges = ", judges)
    # 描画する
    images = draw(q, a, nlc)
    bfile = os.path.basename(qfile)
    bfile = os.path.splitext(bfile)[0] # 拡張子をトル
    for num, img in enumerate(images):
        ifile = "%s.%d.gif" % (bfile, num+1) # 層の番号は1から始まる
        img.save(ifile, 'gif')
        print(ifile)
    if 1 < len(images):
        merge_images(images).save(bfile+'.gif', 'gif')


if __name__ == "__main__":
    main()
    #test()
