#!/usr/bin/env python
# -*- coding: utf-8 ; mode: python -*-
#
# Copyright (C) 2015 Fujitsu
# Copyright (C) 2017 DA Symposium


"""
python pillowで絵を描く
"""

from __future__ import print_function
from PIL import Image, ImageDraw, ImageFont
import sys
import os
from nlcheck import NLCheck

# ./lib/ をsys.pathの末尾に追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), './lib')))


unit = 20 # 描画するときの、升目1つのサイズ

# 色, color
white = (255,255,255)
black = (0,0,0)
red = (255,0,0)
blue = (0,0,255)
green = (0,128,0)
gray = (200,200,200)
lightgray = (240,240,240)
col_upstairs = (0,128,0)
col_downstairs = (255,64,192)

# TrueTypeフォントファイル, font
ttf_font = './Ricty-Regular.ttf'

font = None
font_small = None
font_size = 14

def setup_font(font_file):
    "フォントをロードする"
    global font, font_small, font_size
    if os.path.exists(font_file):
        print('use font', font_file)
        font_small_size = int(font_size * 0.666)
        font = ImageFont.truetype(font_file, size=font_size, encoding='unic')
        font_small = ImageFont.truetype(font_file, size=font_small_size, encoding='unic')
    else:
        font = ImageFont.load_default()
        font_small = font

def test():
    "GIFグラフィック出力の動作確認"

    img = Image.new('RGB', (640,480))
    d = ImageDraw.Draw(img)
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
    "盤の座標と、盤の中のマスの数字を描く"

    #print("line_mat shape =", line_mat.shape)
    x,y,z = size
    # マスの座標を描画
    for i in range(0,x):
        d.text(xy=xy(i, y), text=str(i), fill=blue, font=font)
    for i in range(0,y):
        d.text(xy=xy(x, i), text=str(i), fill=blue, font=font)
    # 数字
    for i in range(0, line_num):
        p = line_mat[i]
        #print("p=", p)
        num = i+1
        if num < 100:
            ifont = font
        else:
            ifont = font_small
        if p[2] == layer:
            drawTextInCell(d, xy(p[0],p[1]), str(num), black, ifont, shadow=True)
        if p[5] == layer:
            drawTextInCell(d, xy(p[3],p[4]), str(num), black, ifont, shadow=True)

def number_cells(line_num=None, line_mat=None, layer=None):
    "数字マスの座標のリストを返す"
    res = []
    for i in range(0, line_num):
        p = line_mat[i]
        num = i+1
        if p[2] == layer:
            res.append((p[0],p[1]))
        if p[5] == layer:
            res.append((p[3],p[4]))
    return res

def is_number_cell(x, y, numberPos):
    "数字マスか？　これにはビアは含まれない"
    for pos in numberPos:
        if pos == (x,y):
            return True
    return False

def drawViaName(d, size, via_mat, via_dic, drawlayer):
    "viaの名前を描く"

    via_num = len(via_dic)
    layer_num = size[2]
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

def drawTextInCell(d, xy, text, fill, font, shadow=False):
    """
    マスの中に文字列を描く。できるだけ中央に配置されるようにする。
    @param d PIL.mageDraw.Draw
    @param xy マスの左上の(x,y)座標
    @param text 文字列
    @param fill 色
    @param font フォント
    """
    tsize = font.getsize(text)
    tx = xy[0] + int((unit - tsize[0])/2)
    ty = xy[1] + int((unit - tsize[1])/2)
    if shadow:
        d.text(xy=[tx+1,ty+1], text=text, fill=white, font=font)
    d.text(xy=[tx,ty], text=text, fill=fill, font=font)
    
    
def drawLines(d, size, xmat, layer=None, numberPos=[]):
    """
    線を描く

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
                num = xmat[layer,y1,x1]
            except IndexError as e:
                print("IndexError:", e)
                num = -1
            if num == 0:
                d.rectangle(xy=[(x0,y0),(x0+unit,y0+unit)], fill=gray) # 空白マス
                continue
            n,e,w,s = is_connected(xmat[layer], x, y) # x,yでOK
            if n:
                d.line(xy=[(cx,cy),(cx,y0)], fill=black)
            if e:
                d.line(xy=[(cx,cy),(x0+unit,cy)], fill=black)
            if w:
                d.line(xy=[(cx,cy),(x0,cy)], fill=black)
            if s:
                d.line(xy=[(cx,cy),(cx,y0+unit)], fill=black)
            inews = int(n)+int(e)+int(w)+int(s)
            if is_number_cell(x, y, numberPos): # 始点or終点は、何もしなくてよい
                pass
            else:
                if inews == 0: # 層を貫通するだけのビア
                    d.arc(xy=[(x0,y0), (x0+unit-1,y0+unit-1)], start=0, end=360, fill=black)
                    drawTextInCell(d, [x0,y0], str(num), red, font_small, shadow=True)
                elif inews == 1:
                    if xmat[layer+1, y1, x1] == num:
                        color = col_upstairs
                    else:
                        color = col_downstairs
                    d.arc(xy=[(x0,y0), (x0+unit-1,y0+unit-1)], start=0, end=360, fill=black)
                    drawTextInCell(d, [x0,y0], str(num), color, font_small, shadow=True)

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
            numberPos = number_cells(line_num=q[1], line_mat=q[2], layer=j)
            img, d = newImage(q[0])
            drawGrid(d, q[0])
            #drawNumbers(d, q[0], q[1], q[2], j)
            drawViaName(d, q[0], q[3], q[4], j)
            drawLines(d, q[0], xmat, layer=j, numberPos=numberPos)
            drawNumbers(d, q[0], q[1], q[2], j)
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
    global ttf_font, font_size, unit
    import argparse
    parser = argparse.ArgumentParser(description='NumberLink check and drawing tool')
    parser.add_argument('-f', '--font', default=ttf_font, help='TrueType font file (default: %(default)s)')
    parser.add_argument('--font-size', metavar='N', type=int, default=font_size, help='font size (default: %(default)s)')
    parser.add_argument('--unit', metavar='N', type=int, default=unit, help='unit square size (default: %(default)s)')
    parser.add_argument('--test', action='store_true', help='test GIF output')
    parser.add_argument('qfile', metavar='Q-FILE', help='input file (Q-file)')
    parser.add_argument('afile', metavar='A-FILE', help='target file (A-file)')
    args = parser.parse_args()
    ttf_font = args.font
    font_size = args.font_size
    unit = args.unit
    setup_font(ttf_font)
    if args.test:
        test()
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
