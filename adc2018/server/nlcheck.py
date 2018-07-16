#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# ナンバーリンクの回答チェック・プログラム
#     for アルゴリズムデザインコンテスト in DAシンポジウム2017
#
# 書式: nlcheck.py --input FILE1 --target FILE2
#
# 引数:
#       -h|--help
#       -d|--debug
#       -v|--verbose
#       -i|--input FILE1  : 問題ファイル(入力)
#       -t|--target FILE2 : 回答ファイル(入力)
#       -c|--clean FILE3  : 最短経路で線を引き直した回答ファイル(出力)
#       -p|--png FILE4    : 回答のグラフィックデータファイル(出力、PNG形式)
#       -g|--gif FILE5    : 回答のグラフィックデータファイル(出力、GIF形式)
#
# 実行例:
#      % nlcheck.py --input Q1.txt --target A1.txt 
#      judge =  [True, 0.0070921985815602835]
#
#      % nlcheck.py --input Q1.txt --target A1_ng.txt
#      check_5: found disjoint line(s)
#      judge =  [False, 0.0]
#
#      Trueなら正解、Falseなら不正解。
#      数値は解の品質の値(不正解の場合0.0)
#
# 解説:
#      ナンバーリンクパズルのルールにしたがって、正解かチェックしています。
#      詳細は、コード中のコメントをご覧下さい。
#
#      このプログラムを実行するためには、PythonとNumPyが必要です。
#      また、回答のグラフィックファイルを出力するにはpython-gdが必要です。
#      Python、NumPy、python-gdのインストール方法は、ネット検索してみて
#      ください。
#
#
#
# Copyright (c) 2017 DA Symposium 2017
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#


import numpy as np
import sys
import getopt
import re
import io
from os.path import basename

""" ADC2017 constraints
C2017_1. 問題フォーマットにて、盤面平面のサイズは最大で72X72
C2017_2. 問題フォーマットにて、層数は最大で8
C2017_3. 問題フォーマットにて、各LINEの端点は2個（分岐しない）
"""
" C2017_1. 問題フォーマットにて、盤面平面のサイズは最大で72X72"
XSIZE_MAX=72
YSIZE_MAX=72
" C2017_2. 問題フォーマットにて、層数は最大で8"
LAYER_MAX=8
" C2017_3. 問題フォーマットにて、各LINEの端点は2個（分岐しない）"
LINE_TERMINAL_MAX=2

class NLCheck:
    "アルゴリズムデザインコンテスト（ナンバーリンクパズル）の回答チェック"

    def __init__(self):
        self.debug = False
        self.verbose = False
        np.set_printoptions(linewidth=255)

    def read_input_file(self, file):
        """問題ファイルを読み込む
           （CLIから使用時のエントリポイント）
        Args:
            file: ファイルのパス名
        """
        # "U" universal newline, \n, \r\n, \r
        with open(file, "rU") as f:
            s = f.read()
            return self.read_input_str(s)


    def read_input_str(self, str):
        """問題データ（テキスト文字列）を読み込む
           （WebUIから使用時のエントリポイント）
        Args:
            str: 文字列

        """
        str = unicode(str, encoding='utf-8-sig', errors='strict') # get unicode without BOM
        f = io.StringIO(str, newline=None)
        ret = self.read_input_data(f)
        f.close()
        return ret


    def read_input_data(self, f):
        """問題データを読み込む
        Args:
            f: fileオブジェクト
        """
        size = None # (x,y,z): z means number of layers
        line_num = 0
        line_mat = None
        via_mat = None

        pSIZE3D = re.compile('SIZE +([0-9]+)X([0-9]+)X([0-9]+)', re.IGNORECASE)
        pLINE_NUM = re.compile('LINE_NUM +([0-9]+)', re.IGNORECASE)

        pLINE3D_name = re.compile('LINE#(\d+) +\((\d+),(\d+),(\d+)\)', re.IGNORECASE)
        pLINE3D_pos  = re.compile('[- ]\((\d+),(\d+),(\d+)\)', re.IGNORECASE)

        while True:
            line = f.readline().encode('ascii')
            if line == "": break # EOFのとき
            line = line.rstrip() # chompみたいに、改行コードを抜く
            if line == "": continue # 空行のとき
            if self.debug: print "line=|%s|" % str(line)

            m = pSIZE3D.match(line)
            if m is not None:
                sizex, sizey, sizez = m.groups()
                size = (int(sizex), int(sizey), int(sizez))
                sizex, sizey, sizez = size
                assert(1 <= sizex <= XSIZE_MAX)
                assert(1 <= sizey <= YSIZE_MAX)
                assert(1 <= sizez <= LAYER_MAX)
                layer_num = int(sizez)
                if self.debug: print "#layer=%d, size= %d x %d" % (layer_num, size[0], size[1])
                continue

            m = pLINE_NUM.match(line)
            if m is not None:
                line_num = int(m.group(1))
                # line_num行、6列の行列
                line_mat = np.zeros((line_num,6), dtype=np.integer)
                continue

            m = pLINE3D_name.match(line)
            if m is not None:
                num = m.groups()[0]
                num = int(num)
                assert(1 <= num <= line_num)
                positer = 0
                for m in pLINE3D_pos.finditer(line):
                    x,y,z = m.groups()
                    x = int(x)
                    y = int(y)
                    z = int(z)
                    size_x, size_y, layer_num = size
                    assert(0 <= x < size_x)
                    assert(0 <= y < size_y)
                    assert(1 <= z <= layer_num)
                    line_mat[num-1, positer*3+0] = x
                    line_mat[num-1, positer*3+1] = y
                    line_mat[num-1, positer*3+2] = z
                    positer+=1
                assert(positer <= LINE_TERMINAL_MAX)
                continue

            print "WARNING: unknown: ", str(line)
        if self.debug:
            print "@read_input_data: line_mat = "
            print "\tline_mat = "
            print line_mat
        return (size, line_num, line_mat)


    def read_target_file(self, file):
        "チェック対象ファイルを読み込む"
        # "U" universal newline, \n, \r\n, \r
        with open(file, "rU") as f:
            s = f.read()
            return self.read_target_str(s)


    def read_target_str(self, str):
        "チェック対象を文字列から読み込む"
        str = unicode(str, encoding='utf-8-sig', errors='strict') # get unicode without BOM
        f = io.StringIO(str, newline=None)
        ret = self.read_target_data(f)
        f.close()
        return ret


    def read_target_data(self, f):
        "チェック対象データを読み込む"
        size = None
        mat = None
        line_cnt = 0
        layer_cur_num = 1
        result = None
        pSIZE3D = re.compile('SIZE +([0-9]+)X([0-9]+)X([0-9]+)', re.IGNORECASE)
        pLAYER = re.compile('LAYER +([0-9]+)', re.IGNORECASE)
        # "U" universal newline, \n, \r\n, \r
        while True:
            line = f.readline().encode('ascii')
            eof = (line == "")
            line = line.rstrip() # chompみたいに、改行コードを抜く
            if line == "":       # 空行 or EOFのとき
                if mat is not None:
                    if result is None:
                        result = mat # 解を登録
                    mat = None
                    line_cnt = 0
                    if self.debug: print ""
                if eof:
                    break
                else:
                    continue
            if self.debug: print "line=|%s|" % str(line)

            # まず 3D SIZE行があるはず
            m = pSIZE3D.match(line)
            if m is not None:
                # 3D SIZE行が現れた
                if size is not None:
                    # ２度め以降のSIZEに対してはWarning
                    print "WARNING: too many SIZE"
                size = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
                if self.debug: print "SIZE 3D = ", size
                continue
            else:
                if size is None:
                    # まだSIZE行が現れていない
                    print "WARNING: unknown: ", str(line)
                    continue

            # 次にLAYER指定があるはず。
            m = pLAYER.match(line)
            if m is not None:
                # LAYER行が現れた
                layer_cur_num = int(m.group(1))
                line_cnt = 0
                continue

            # matを初期化
            if mat is None:
                if size is None:
                    print "ERROR: no SIZE"
                    break
                mat = np.zeros((size[2],size[1],size[0]), dtype=np.integer)
            # カンマ区切りの数値の行のはず
            data = line.split(",")
            if len(data) == 1:
                print "ERROR: unknown: ", str(line)
                continue
            if size[1] <= line_cnt:
                print "ERROR: too many lines: size=", size
                continue
            # データを格納
            for i in range(0,len(data)):
                val = -1
                try:
                    val = int(data[i])
                except ValueError:
                    print "ERROR: illegal value: ", str(data[i])
                mat[layer_cur_num-1, line_cnt, i] = val
            line_cnt += 1
        return result


    def extend_matrix(self, mat):
        "行列の上下左右を1行/列ずつ拡大する"
        xmat = np.zeros( (mat.shape[0]+2, mat.shape[1]+2, mat.shape[2]+2), mat.dtype )
        xmat[1:(mat.shape[0]+1):1, 1:(mat.shape[1]+1):1, 1:(mat.shape[2]+1):1] = mat
        return xmat

    def neighbors_Eq(self, xmat, x, y, z):
        """
        East,North,West,South,Upper,Lowerの6つの隣接マスの数字が等しいか調べる
        @param x,y,z 注目点の座標(xmatの座標系ではなくて、元の座標系)
        """
        x1 = 1 + x  # xmatでは、座標が1ずつずれるので
        y1 = 1 + y
        num = xmat[z,y1,x1] # 注目点の数字
        eastEq     = 1 if (xmat[z,   y1,  x1+1] == num) else 0
        northEq    = 1 if (xmat[z,   y1-1,x1  ] == num) else 0
        westEq     = 1 if (xmat[z,   y1,  x1-1] == num) else 0
        southEq    = 1 if (xmat[z,   y1+1,x1  ] == num) else 0
        upperEq    = 1 if (xmat[z+1, y1  ,x1  ] == num) else 0
        lowerEq    = 1 if (xmat[z-1, y1  ,x1  ] == num) else 0
        return eastEq, northEq, westEq, southEq, upperEq, lowerEq

    def is_terminal(self, xmat, x, y, z):
        "線の端点か？"
        # 端点とは? (ADC2017では３次元に拡張)
        # 
        # □…注目点
        # 
        #   Ｘ
        # Ｘ□■
        #   Ｘ
        # 
        #   ■
        # Ｘ□Ｘ
        #   Ｘ
        # 
        #   Ｘ
        # ■□Ｘ
        #   Ｘ
        # 
        #   Ｘ
        # Ｘ□Ｘ
        #   ■
        #
        eastEq, northEq, westEq, southEq, upperEq, lowerEq = self.neighbors_Eq(xmat, x, y, z)
        if ( 1 == eastEq + northEq + westEq + southEq + upperEq + lowerEq ):
            return True
        else:
            return False

    def is_alone(self, xmat, x, y, z):
        " 孤立点か？"
        eastEq, northEq, westEq, southEq, upperEq, lowerEq = self.neighbors_Eq(xmat, x, y, z)
        if ( 0 == eastEq + northEq + westEq + southEq + upperEq + lowerEq ):
            return True
        else:
            return False

    def is_branched(self, xmat, x, y, z):
        "線が枝分かれしているか？"
        # 枝分かれとは? (ADC2017では３次元に拡張)
        # 
        # ■
        # □■
        # ■
        # 
        #   ■
        # ■□■
        # 
        #   ■
        # ■□
        #   ■
        # 
        # ■□■
        #   ■
        #
        eastEq, northEq, westEq, southEq, upperEq, lowerEq = self.neighbors_Eq(xmat, x, y, z)
        if ( 3 <= eastEq + northEq + westEq + southEq + upperEq + lowerEq ):
            return True
        else:
            return False

    def is_corner(self, xmat, x, y, z):
        "線が折れ曲がった角の場所か？"
        # 折れ曲がり、コーナー、とは? (ADC2017では３次元に拡張)
        # 
        # ■
        # □■
        # 
        # 
        #   ■
        # ■□
        # 
        #   
        # ■□
        #   ■
        # 
        #   □■
        #   ■
        #
        eastEq, northEq, westEq, southEq, upperEq, lowerEq = self.neighbors_Eq(xmat, x, y, z)
        # 以下の判定では、枝分かれ個所も、折れ曲がりだと見なしている。枝分かれは不正解なので、このままでOK
        if (((eastEq or westEq) and (northEq or southEq)) or
            ((upperEq or lowerEq) and (eastEq or northEq or westEq or southEq))):
            return True
        else:
            return False


    def clearConnectedLine(self, xmat, clear, x1, y1, z):
        "線を１本消してみる"
        num = xmat[z,y1,x1]
        clear[z,y1,x1] = 0
        # 線が連続しているなら、消す
        neighbors = [(z,y1,x1+1), (z,y1-1,x1), (z,y1,x1-1), (z,y1+1,x1),
                     (z+1,y1,x1), (z-1,y1,x1)]
        # first check terminal
        for nz,ny,nx in neighbors:
            if xmat[nz,ny,nx] == num and clear[nz,ny,nx] != 0:
                self.clearConnectedLine(xmat, clear, nx,ny,nz) # 再帰

    def check_size(self, size, mat):
        "行列の大きさチェック"
        if size is None:
            print "ERROR: SIZE is none"
            return False
        (z,y,x) = mat.shape
        if size == (x,y,z):
            return True
        else:
            return False


    def check_1(self, input_data, mat):
        "チェック1. 問題の数字の位置と、同じである。"
        (size, line_num, line_mat) = input_data
        judge = True
        if self.check_size(size, mat) == False:
            print "check_1: mismatch matrix size: SIZE=", size, "matrix=", mat.shape
            judge = False
        else:
            for line in range(1, line_num+1):
                (x0,y0,z0,x1,y1,z1) = line_mat[line-1]
                if mat[z0-1,y0,x0] == line and mat[z1-1,y1,x1] == line:
                    pass
                else:
                    judge = False
                    print "check_1: mismatch line number:", line
                    print "  LINE#%d (%d,%d,%d)-(%d,%d,%d)" % (line,x0,y0,z0,x1,y1,z1)
                    print "  mat=", mat[z0-1,y0,x0], "mat=", mat[z1-1,y1,x1]
        return judge


    def check_2(self, input_data, mat):
        "チェック2. 問題にはない数字があってはいけない。"
        (size, line_num, line_mat) = input_data
        judge = True
        # 1からline_numまでの数字が出現するはず。または空きマス＝0
        (sx,sy,sz) = size
        for z in range(0,sz):
            for y in range(0,sy):
                for x in range(0,sx):
                    num = mat[z,y,x]
                    if num < 0 or line_num < num:
                        print "check_2: strange number %d at (%d,%d)" % (num,x,y)
                        judge = False
        return judge


    def check_3(self, input_data, xmat):
        "チェック3. 問題の数字の位置が、線の端点である。"
        (size, line_num, line_mat) = input_data
        judge = True
        for line in range(1, line_num+1):
            (x0,y0,z0,x1,y1,z1) = line_mat[line-1]
            if self.is_terminal(xmat, x0,y0,z0) == False:
                print "check_3: not terminal (%d,%d,%d) #%d" % (x0,y0,z0,xmat[z0,y0+1,x0+1])
                judge = False
            if self.is_terminal(xmat, x1,y1,z1) == False:
                print "check_3: not terminal (%d,%d,%d) #%d" % (x1,y1,z1,xmat[z1,y1+1,x1+1])
                judge = False
        return judge


    def check_4(self, xmat):
        "チェック4. 線は枝分かれしない。"
        judge = True
        for z in range(0, xmat.shape[0]-1):
            for y in range(0, xmat.shape[1]-2):
                for x in range(0, xmat.shape[2]-2):
                    if xmat[z, y+1,x+1] == 0: continue # 0は空き地。xmatのズレ補正必要
                    if self.is_branched(xmat, x,y,z) == True:
                        print "check_4: found branch (%d,%d,%d) #%02d" % (x,y,z,xmat[z,y+1,x+1]) # 座標が1だけずれている
                        judge = False
        return judge


    def check_5(self, input_data, xmat):
        "チェック5. 線はつながっている。"
        (size, line_num, line_mat) = input_data
        judge = True
        clear = xmat.copy()
        for line in range(1, line_num+1):
            (x0,y0,z0,x1,y1,z1) = line_mat[line-1]
            # 始点から線をたどって、消していく
            self.clearConnectedLine(xmat, clear, x0+1, y0+1, z0)

        if clear.sum() == 0:
            # すべて消えた
            judge = True
        else:
            judge = False
            print "check_5: found disjoint line(s)"
            if self.verbose: print clear[1:clear.shape[0]-1,1:clear.shape[1]-1]
        return judge

    def line_length(self, nlines, mat):
        "線の長さを計算する"
        length = np.zeros(nlines+1, dtype=np.integer)
        for z in range(0, mat.shape[0]):
            for y in range(0, mat.shape[1]):
                for x in range(0, mat.shape[2]):
                    num = mat[z,y,x]
                    if num == 0: continue
                    length[num] += 1
        if self.verbose: print "length=", ["#%d:%d" % (i, c) for (i, c) in zip(range(nlines+1), length)[1:]] # 線ごとの線長
        return length.sum()

    def count_corners(self, nlines, xmat):
        "折れ曲がり回数を計算する"
        corner = np.zeros(nlines+1, dtype=np.integer)
        for z in range(0, xmat.shape[0]-1):
            for y in range(0, xmat.shape[1]-2):
                for x in range(0, xmat.shape[2]-2):
                    num = xmat[z,y+1,x+1]
                    if num == 0: continue
                    if self.is_corner(xmat, x, y, z) == True:
                        corner[num] += 1
        if self.verbose: print "corner=", ["#%d:%d" % (i, c) for (i, c) in zip(range(nlines+1), corner)[1:]] # 線ごとの角の数
        return corner.sum()
    
    def quality(self, input_data, mat, xmat):
        "解の品質を計算する"
        total_length = self.line_length(input_data[1], mat)
        total_corner = self.count_corners(input_data[1], xmat)
        q = 1.0 / float(total_length + total_corner)
        if self.verbose: print "quality=",q
        return q

    def check(self, input_data, target_data):
        "回答が正しいかチェックする"
        ok = 0
        ng = 0
        r1 = False
        r2 = False
        r3 = False
        r4 = False
        r5 = False
        mat = target_data # 解答の行列
        if mat.sum() == 0:
            print "ERROR: Zero Matrix"
        else:
            r1 = self.check_1(input_data, mat)
            if self.verbose: print "check_1", r1
        if r1:
            try:
                r2 = self.check_2(input_data, mat)
            except IndexError, e:
                print "IndexError:", e
            if self.verbose: print "check_2", r2
            try:
                xmat = self.extend_matrix(mat)
                r3 = self.check_3(input_data, xmat)
            except IndexError, e:
                print "IndexError:", e
            if self.verbose: print "check_3", r3
            try:
                r4 = self.check_4(xmat)
            except IndexError, e:
                print "IndexError:", e
            if self.verbose: print "check_4", r4
            try:
                r5 = self.check_5(input_data, xmat)
            except IndexError, e:
                print "IndexError:", e
            if self.verbose: print "check_5", r5
        #
        res = r1 and r2 and r3 and r4 and r5
        if res:
            q = self.quality(input_data, mat, xmat)
        else:
            q = 0.0
        return [res,q]
               
    def clean_a(self, q, a):
        "solverが出力する解が変なので、ちゃちゃっときれいにする"
        import nlclean
        mat = a
        if mat.sum() == 0:
            print "ERROR: Zero Matrix"
        else:
            line_mat = q[2]
            xmat = self.extend_matrix(mat)
            xmat2 = nlclean.clean(line_mat, xmat)
            xmat3 = nlclean.short_cut(line_mat, xmat2)
            mat = xmat3[1:(mat.shape[0]+1):1, 1:(mat.shape[1]+1):1, 1:(mat.shape[2]+1):1]
        return mat

    def generate_A_data(self, a2):
        "clean_aを通したあとの、回答データを、ADC形式に変換する"
        crlf = "\r\n" # DOSの改行コード
        out = None
        zz,yy,xx = a2.shape
        out = "SIZE %dX%dX%d" % (xx, yy, zz) + crlf
        for z in range(0, zz):
            out += "LAYER %d" % (z + 1) + crlf
            for y in range(0, yy):
                for x in range(0, xx):
                    out += "%02d" % a2[z,y,x]
                    if x == xx-1:
                        out += crlf
                    else:
                        out += ","
        return out

    def graphic_png(self, q, a, filename):
        "回答データをグラフィックとして描画"
        import nldraw
        images = nldraw.draw(q, a, self)
        base = re.sub("\.png", "", filename)
        num = 1
        res = []
        for img in images:
            file = "%s.%d.png" % (base, num)
            img.writePng(file)
            res.append(file)
            num += 1
        return res
        
    def graphic_gif(self, q, a, filename):
        "回答データをグラフィックとして描画"
        import nldraw
        images = nldraw.draw(q, a, self)
        base = re.sub("\.gif", "", filename)
        num = 1
        res = []
        for img in images:
            file = "%s.%d.gif" % (base, num)
            img.writeGif(file)
            res.append(file)
            num += 1
        return res
    
    def usage(self):
        print "usage:",sys.argv[0],
        print """
-h|--help
-d|--debug
-v|--verbose
-i|--input FILE
-t|--target FILE
-c|--clean FILE
-p|--png FILE
-g|--gif FILE
"""

    def main(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hdvi:t:c:p:g:", ["help","debug","verbose","input=","target=","clean=","png=","gif="])
        except getopt.GetoptError:
            self.usage()
            sys.exit(2)
        input_data  = None  # 問題データ
        target_data = None  # チェック対象とする解答データ
        input_file = None
        target_file = None
        clean = None
        gif = None
        png = None
        for o,a in opts:
            if o in ("-h","--help"):
                self.usage()
                sys.exit()
            elif o in ("-d","--debug"):
                self.debug = True 
            elif o in ("-v","--verbose"):
                self.verbose = True
            elif o in ("-i","--input"):
                input_file = a
            elif o in ("-t","--target"):
                target_file = a
            elif o in ("-c", "--clean"):
                clean = a
            elif o in ("-p", "--png"):
                png = a
            elif o in ("-g", "--gif"):
                gif = a
        if input_file :
            input_data = self.read_input_file(input_file)
            if self.verbose: print "input=", input_data
        if target_file:
            target_data = self.read_target_file(target_file)
            if self.verbose: print "target=\n", target_data
        if input_data is not None and target_data is not None:
            if clean is not None:
                target_data = self.clean_a(input_data, target_data)
                atext = self.generate_A_data(target_data)
                with open(clean, "w") as f:
                    f.write(atext)
            judge = self.check( input_data, target_data )
            print "judge = ", judge
            if gif is not None:
                self.graphic_gif(input_data, target_data, gif)
            if png is not None:
                self.graphic_png(input_data, target_data, png)



if __name__ == "__main__":
    o = NLCheck()
    o.main()


# Local Variables:
# mode: python
# coding: utf-8    
# End:             
