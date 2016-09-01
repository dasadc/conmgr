#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# $Rev: 24 $
# ナンバーリンクの回答チェック・プログラム
#     for アルゴリズムデザインコンテスト in DAシンポジウム2014
#
# 書式: nlcheck.py --input FILE1 --target FILE2
#
# 引数:
#       --input FILE1  : 問題ファイル
#       --target FILE2 : 回答ファイル
#       --verbose
#       --debug
#
# 実行例:
#      % ./nlcheck.py --input NL_Q04.txt --target NL_R04.txt 
#      judges =  [True, True, True]
#
#      % ./nlcheck.py --input NL_Q04.txt --target NL_R04_bad1.txt
#      check_6: same data 0 and 3
#      judges =  [True, True, True, False]
#
#      Trueなら正解、Falseなら不正解。
#
# 解説:
#      このプログラムを実行するためには、PythonとNumPyが必要です。
#      PythonとNumPyのインストール方法は、ネット検索してみてください。
#
#      ナンバーリンクパズルのルールにしたがって、正解かチェックしています。
#      詳細は、コード中のコメントをご覧下さい。
#
#
#
# Copyright (c) 2014 DA Symposium 2014
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

VER_2016="ADC2016"
VERSION=VER_2016

LINE_TERMINAL_MAX=9999 # ADC2016 restriction
LAYER_MAX=9999         # ADC2016 restriction
if VERSION == VER_2016:
    """ ADC2016 constraints
    C2016_1. 問題フォーマットにて、各LINEの端点は2個（分岐しない）
    C2016_2. 問題フォーマットにて、LINE数 >= VIA数
    C2016_3. 問題フォーマットにて、各VIAの位置(x,y,z)がSIZE内である
    C2016_4. 問題フォーマットにて、各VIAの各層での位置(x,y)がすべて一致している
    C2016_5. 問題フォーマットにて、無駄なVIAが存在しない = 層をまたぐLINE数とVIA数が同じ
    C2016_6. 回答フォーマット中で、問題のViaの位置に数字がある（アルファベットのままではない）
    C2016_7. 回答フォーマット中で、Viaの端層の数字は、端点である
    C2016_8. 回答フォーマット中で、via途中層の数字は、孤立している
    C2016_9. 回答フォーマット中で、アルファベット同士の接続はナシ
    C2016_10. 問題フォーマットにて、層数は最大で8
    """
    " C2016_1. 問題フォーマットにて、各LINEの端点は2個（分岐しない）"
    LINE_TERMINAL_MAX=2 # ADC2016 restriction
    " C2016_10. 問題フォーマットにて、層数は最大で8"
    LAYER_MAX=8         # ADC2016 restriction

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
        #str = open(file).read()
        #return self.read_input_str(str)


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

        pSIZE = re.compile('SIZE +([0-9]+)X([0-9]+)', re.IGNORECASE)
        pLINE_NUM = re.compile('LINE_NUM +([0-9]+)', re.IGNORECASE)
        pLINE = re.compile('LINE#(\d+) +\((\d+),(\d+)\)-\((\d+),(\d+)\)', re.IGNORECASE)
        first = True

        pSIZE3D = re.compile('SIZE +([0-9]+)X([0-9]+)X([0-9]+)', re.IGNORECASE)

        #pLINE3D = re.compile('LINE#(\d+) +\((\d+),(\d+),(\d+)\)[- ]\((\d+),(\d+),(\d+)\)', re.IGNORECASE)
        pLINE3D_name = re.compile('LINE#(\d+) +\((\d+),(\d+),(\d+)\)', re.IGNORECASE)
        pLINE3D_pos  = re.compile('[- ]\((\d+),(\d+),(\d+)\)', re.IGNORECASE)

        via_number = 1
        pVIA3D_name = re.compile('VIA#([a-z]+) +(\((\d+),(\d+),(\d+)\))+', re.IGNORECASE) # use match
        pVIA3D_pos  = re.compile('[- ]\((\d+),(\d+),(\d+)\)', re.IGNORECASE) # use finditer

        via_dic = dict()

        while True:
            line = f.readline().encode('ascii')
            if line == "": break # EOFのとき
            line = line.rstrip() # chompみたいに、改行コードを抜く
            if line == "": continue # 空行のとき
            if self.debug: print "line=|%s|" % str(line)

            m = pSIZE3D.match(line)
            if m is not None:
                #size = (int(m.group(1)), int(m.group(2)))
                sizex, sizey, sizez = m.groups()
                size = (int(sizex), int(sizey), int(sizez))
                layer_num = int(sizez)
                if self.debug: print "#layer=%d, size= %d x %d" % (layer_num, size[0], size[1])
                continue

            m = pSIZE.match(line)
            l = 0 # default layer number is 0
            if m is not None:
                size = (int(m.group(1)), int(m.group(2)), 1)
                layer_num = 1
                if self.debug: print "#layer is implicitly set to 1, size= %d x %d" % (size[0], size[1])
                continue

            m = pLINE_NUM.match(line)
            if m is not None:
                line_num = int(m.group(1))
                # line_num行、4列の行列
                #line_mat = np.zeros((line_num,4), dtype=np.integer)
                line_mat = np.zeros((line_num,6), dtype=np.integer)
                via_mat = np.zeros((line_num,3*LAYER_MAX), dtype=np.integer)
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

            m = pLINE.match(line)
            if m is not None:
                #num = int(m.group(1)) # LINE#番号
                num, sx, sy, ex, ey = m.groups()
                # layer is implicitly set as 1
                sz = 1
                ez = 1
                num = int(num)
                if num <= 0 or line_num < num:
                    print "ERROR: LINE# range: ", str(line)
                    break
                #for i in range(0,4):
                #    line_mat[num-1, i] = int(m.group(2+i))
                line_mat[num-1, 0] = int(sx) # 
                line_mat[num-1, 1] = int(sy) # 
                line_mat[num-1, 2] = 1       # layer no. of start edge
                line_mat[num-1, 3] = int(ex) #
                line_mat[num-1, 4] = int(ey) #
                line_mat[num-1, 5] = 1       # layer no. of end edge
                continue

            m = pVIA3D_name.match(line)
            if m is not None:
                v = m.groups()[0]
                via_dic[v] = via_number # set lookup table of (via_name, via_number)
                positer = 0
                for m in pVIA3D_pos.finditer(line):
                    x,y,z = m.groups()
                    x = int(x)
                    y = int(y)
                    z = int(z)
                    assert(1 <= z <= layer_num)
                    via_mat[via_number-1, positer*3+0] = x
                    via_mat[via_number-1, positer*3+1] = y
                    via_mat[via_number-1, positer*3+2] = z
                    positer+=1
                if VERSION==VER_2016:
                    assert(positer <= LAYER_MAX)
                via_number += 1
                continue
            print "WARNING: unknown: ", str(line)
        #print "size=",size
        #print "line_num=",line_num
        if self.debug:
            print "@read_input_data: line_mat = "
            print "\tline_mat = "
            print line_mat
            print "\tvia_mat = "
            print via_mat
            print "\tvia_dic = "
            print via_dic
        return (size, line_num, line_mat, via_mat, via_dic)


    def read_target_file(self, file):
        "チェック対象ファイルを読み込む"
        # "U" universal newline, \n, \r\n, \r
        with open(file, "rU") as f:
            s = f.read()
            return self.read_target_str(s)
        #str = open(file).read()
        #return self.read_target_str(str)


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
        results = []
        pSIZE = re.compile('SIZE +([0-9]+)X([0-9]+)', re.IGNORECASE)
        pLAYER = re.compile('LAYER +([0-9]+)', re.IGNORECASE)
        pSIZE3D = re.compile('SIZE +([0-9]+)X([0-9]+)X([0-9]+)', re.IGNORECASE)
        first = True
        # "U" universal newline, \n, \r\n, \r
        while True:
            line = f.readline().encode('ascii')
            eof = (line == "")
            line = line.rstrip() # chompみたいに、改行コードを抜く
            if line == "":       # 空行 or EOFのとき
                if mat is not None:
                    results.append(mat) # 解を追加
                    mat = None
                    line_cnt = 0
                    if self.debug: print ""
                if eof:
                    #results.append(mat) # 解を追加
                    #print "result data = "
                    #print mat
                    #mat = None
                    break
                else:
                    continue
            if self.debug: print "line=|%s|" % str(line)

            # まず SIZE行があるはず
            # 3D SIZE行があるはず
            m = pSIZE3D.match(line)
            if m is not None:
                # 3D SIZE行が現れた
                if size is not None:
                    # ２度め以降のSIZEに対してはWarning
                    print "WARNING: too many SIZE"
                size = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
                if self.debug: print "SIZE 3D = ", size
                continue
            #else:
            #    if size is None:
            #        # まだSIZE行が現れていない
            #        print "WARNING: unknown: ", str(line)
            #        continue
            # 2D SIZE行かも
            m = pSIZE.match(line)
            if m is not None:
                # SIZE行が現れた
                if size is not None:
                    # ２度め以降のSIZEに対してはWarning
                    print "WARNING: too many SIZE"
                size = (int(m.group(1)), int(m.group(2)), 1) # Z軸定義が無いとき、１と仮定する
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
        return results


    def extend_matrix(self, mat):
        "行列の上下左右を1行/列ずつ拡大する"
        xmat = np.zeros( (mat.shape[0]+2, mat.shape[1]+2, mat.shape[2]+2), mat.dtype )
        xmat[1:(mat.shape[0]+1):1, 1:(mat.shape[1]+1):1, 1:(mat.shape[2]+1):1] = mat
        return xmat


    def is_terminal(self, xmat, x, y, z):
        "線の端点か？"
        # 端点とは?
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
        x1 = 1 + x  # xmatでは、座標が1ずつずれるので
        y1 = 1 + y
        num = xmat[z,y1,x1] # 注目点の数字
        eastEq     = (xmat[z,y1,x1+1] == num)
        northEq    = (xmat[z,y1-1,x1] == num)
        westEq     = (xmat[z,y1,x1-1] == num)
        southEq    = (xmat[z,y1+1,x1] == num)
        eastNotEq  = (xmat[z,y1,x1+1] != num)
        northNotEq = (xmat[z,y1-1,x1] != num)
        westNotEq  = (xmat[z,y1,x1-1] != num)
        southNotEq = (xmat[z,y1+1,x1] != num)
        #print "num=%d xpos=(%d,%d)" % (num, x1,y1)
        #print eastEq,northEq,westEq,southEq
        #print eastNotEq,northNotEq,westNotEq,southNotEq
        if ( (eastEq    and northNotEq and westNotEq and southNotEq) or
             (eastNotEq and northEq    and westNotEq and southNotEq) or
             (eastNotEq and northNotEq and westEq    and southNotEq) or
             (eastNotEq and northNotEq and westNotEq and southEq   ) ) :
            return True
        else:
            return False

    def is_alone(self, xmat, x, y, z):
        " 孤立点か？"
        x1 = 1 + x  # xmatでは、座標が1ずつずれるので
        y1 = 1 + y
        num = xmat[z,y1,x1] # 注目点の数字
        eastNotEq  = (xmat[z,y1,  x1+1] != num)
        northNotEq = (xmat[z,y1-1,x1  ] != num)
        westNotEq  = (xmat[z,y1,  x1-1] != num)
        southNotEq = (xmat[z,y1+1,x1  ] != num)
        #print "num=%d xpos=(%d,%d)" % (num, x1,y1)
        #print eastNotEq,northNotEq,westNotEq,southNotEq
        if (eastNotEq and northNotEq and westNotEq and southNotEq):
            return True
        else:
            return False

    def is_branched(self, xmat, x, y, z):
        "線が枝分かれしているか？"
        # 枝分かれとは?
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
        x1 = 1 + x  # xmatでは、座標が1ずつずれるので
        y1 = 1 + y
        num = xmat[z,y1,x1] # 注目点の数字
        eastEq     = 1 if (xmat[z, y1,  x1+1] == num) else 0
        northEq    = 1 if (xmat[z, y1-1,x1  ] == num) else 0
        westEq     = 1 if (xmat[z, y1,  x1-1] == num) else 0
        southEq    = 1 if (xmat[z, y1+1,x1  ] == num) else 0
        #print "(%d,%d) %d %d %d %d  %d" % (x,y,eastEq,northEq,westEq,southEq,(eastEq + northEq + westEq + southEq))
        if ( 3 <= eastEq + northEq + westEq + southEq ):
            return True
        else:
            return False

    def is_corner(self, xmat, x, y, z):
        "線が折れ曲がった角の場所か？"
        # 折れ曲がり、コーナー、とは?
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
        x1 = 1 + x  # xmatでは、座標が1ずつずれるので
        y1 = 1 + y
        num = xmat[z, y1,x1] # 注目点の数字
        eastEq     = 1 if (xmat[z, y1,  x1+1] == num) else 0
        northEq    = 1 if (xmat[z, y1-1,x1  ] == num) else 0
        westEq     = 1 if (xmat[z, y1,  x1-1] == num) else 0
        southEq    = 1 if (xmat[z, y1+1,x1  ] == num) else 0
        #print "(%d,%d) %d %d %d %d  %d" % (x,y,eastEq,northEq,westEq,southEq,(eastEq + northEq + westEq + southEq))
        # 以下の判定では、枝分かれ個所も、折れ曲がりだと見なしている。枝分かれは不正解なので、このままでOK
        if (eastEq  and northEq or
            northEq and westEq or
            westEq  and southEq or
            southEq and eastEq):
            return True
        else:
            return False


    def clearConnectedLine(self, xmat, clear, x1, y1, z, term_set=set()):
        "線を１本消してみる"
        #print x1,y1
        num = xmat[z,y1,x1]
        clear[z,y1,x1] = 0
        # 線が連続しているなら、消す
        neighbors = [(y1,x1+1), (y1-1,x1), (y1,x1-1), (y1+1,x1)]
        # first check terminal
        all_not_eq = True
        for ny,nx in neighbors:
            if xmat[z,ny,nx] == num and clear[z,ny,nx] != 0:
                all_not_eq = False
        if all_not_eq == True:
            term_set.add((x1-1,y1-1,z))
        else:
            for ny,nx in neighbors:
                if xmat[z,ny,nx] == num and clear[z,ny,nx] != 0:
                    self.clearConnectedLine(xmat, clear, nx,ny,z, term_set) # 再帰

    def clearIfAlone(self, xmat, clear, x1, y1, z, term_set=set()):
        "孤立しているなら消す"
        #print x1,y1
        if self.is_alone(xmat,x1-1,y1-1,z):
            clear[z,y1,x1] = 0

    def check_filename(self, absinputf, abstargetf):
        "ファイル名の書式がルール通りかチェック"
        inputf = basename(absinputf) # ディレクトリ名をとりのぞく
        targetf = basename(abstargetf)
        minp = re.match("(NL_Q)([0-9]+)\.(txt)", inputf, re.IGNORECASE)
        mtgt = re.match("(T)([0-9]+)(_A)([0-9]+)\.(txt)", targetf, re.IGNORECASE)
        qinp = None
        qtgt = None
        print "input='%s'" % inputf,
        if minp is None:
            print ", name rule error"
        else:
            print ", prefix='%s', Q-number='%s', ext='%s'" % (minp.group(1), minp.group(2), minp.group(3))
            qinp = minp.group(2)
        print "target='%s'" % targetf,
        if mtgt is None:
            print ", name rule error"
        else:
            print ", prefix='%s', team-number='%s', conj='%s', Q-number='%s', ext='%s'" % (mtgt.group(1), mtgt.group(2), mtgt.group(3), mtgt.group(4), mtgt.group(5))
            qtgt = mtgt.group(4)
        print "Q-number=('%s','%s')" % (qinp, qtgt),
        if qinp is not None and qtgt is not None:
            if qinp == qtgt:
                print "match"
            else:
                print "unmatch"
        else:
            print "NA"

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
        (size, line_num, line_mat, via_mat, via_dic) = input_data
        judge = True
        if self.check_size(size, mat) == False:
            print "check_1: mismatch matrix size: SIZE=", size, "matrix=", mat.shape
            judge = False
        else:
            for line in range(1, line_num+1):
                (x0,y0,z0,x1,y1,z1) = line_mat[line-1]
                #print "LINE#%d (%d,%d)-(%d,%d)" % (line,x0,y0,x1,y1)
                #print "mat=", mat[y0,x0], "mat=", mat[y1,x1]
                if mat[z0-1,y0,x0] == line and mat[z1-1,y1,x1] == line:
                    #print "OK"
                    pass
                else:
                    judge = False
                    print "check_1: mismatch line number:", line
                    print "  LINE#%d (%d,%d,%d)-(%d,%d,%d)" % (line,x0,y0,z0,x1,y1,z1)
                    print "  mat=", mat[z0-1,y0,x0], "mat=", mat[z1-1,y1,x1]
        return judge


    def check_2(self, input_data, mat):
        "チェック2. 問題にはない数字があってはいけない。"
        (size, line_num, line_mat, via_mat, via_dic) = input_data
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
        (size, line_num, line_mat, via_mat, via_dic) = input_data
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
        (size, line_num, line_mat, via_mat, via_dic) = input_data
        judge = True
        clear = xmat.copy()
        for line in range(1, line_num+1):
            (x0,y0,z0,x1,y1,z1) = line_mat[line-1]
            # 始点から線をたどって、消していく
            self.clearConnectedLine(xmat, clear, x0+1, y0+1, z0)
            # 終点から線をたどって、消していく
            self.clearConnectedLine(xmat, clear, x1+1, y1+1, z1)
            #print clear[1:clear.shape[0]-1,1:clear.shape[1]-1]

            # C2016_8: 途中層のビア（数字割当後に孤立しているビア）について
            # ここでは不問とする。正式にチェックするのは
            # self.check_ans_via_is_terminal_or_alone() にて。
            for i in range(len(via_dic)):
                v = via_mat[i]
                viaiter = 0
                while viaiter < LAYER_MAX:
                    vx = v[viaiter*3+0]
                    vy = v[viaiter*3+1]
                    vz = v[viaiter*3+2]
                    if (vx == 0) and (vy == 0) and (vz == 0): break
                    self.clearIfAlone(xmat, clear, vx+1, vy+1, vz)
                    viaiter+=1
        if clear.sum() == 0:
            # すべて消えた
            judge = True
        else:
            judge = False
            print "check_5: found disjoint line(s)"
            if self.verbose: print clear[1:clear.shape[0]-1,1:clear.shape[1]-1]
        return judge


    def check_6(self, target_data, judges):
        "チェック6. 複数解があるときに、同一の解が含まれていたら、２つめ以降は不正解"
        judge = True
        for i in range(0, len(target_data)):
            for j in range(i+1, len(target_data)):
                if judges[i] == True and judges[j] == True:
                    # == で、True,Falseの行列ができて、sum()はTrueの個数
                    matches = (target_data[i] == target_data[j]).sum()
                    if matches == target_data[i].size:
                        # 一致した個数が、行列の要素数に等しい → 同一の行列
                        judge = False
                        judges[j] = False # 正解から不正解へ変更
                        print "check_6: same data, %d and %d" % (i,j)
        return judge

    # check via related constraints
    def check_7(self, input_data, xmat):
        (size, line_num, line_mat, via_mat, via_dic) = input_data

        if self.check_via_num(line_num, via_dic) == False:
            print "check_via_num: line_num = %d, via_num = %d" % (line_num, len(via_dic))
            return False

        if self.check_via_in_size(size, via_mat, via_dic) == False:
            print "check_via_in_size: mismatch SIZE and via: SIZE=", size, "via_matrix="
            print via_mat
            return False

        if self.check_via_same_xy(via_mat, via_dic) == False:
            print "check_via_same_xy: via_mat ="
            print via_mat
            return False

        if self.check_num_of_via_and_interlayerlines(line_num, line_mat, via_mat, via_dic) == False:
            print "check_num_of_via_and_interlayerlines: via_mat ="
            print via_mat
            return False

        if self.check_ans_via_become_num(via_mat, via_dic, xmat) == False:
            print "check_ans_via_become_num: via_mat ="
            print via_mat
            return False

        if self.check_ans_via_is_terminal_or_alone(via_mat, via_dic, xmat) == False:
            print "check_ans_via_is_terminal_or_alone: via_mat ="
            print via_mat
            return False

        if self.check_ans_via_is_connected_to_line(line_num, line_mat, via_mat, via_dic, xmat) == False:
            print "check_ans_via_is_connected_to_line: via_mat ="
            print via_mat
            return False

        return True

    def check_via_num(self, line_num, via_dic):
        " C2016_2. 問題フォーマットにて、LINE数 >= VIA数"
        return (line_num >= len(via_dic))

    def check_via_in_size(self, size, via_mat, via_dic):
        " C2016_3. 問題フォーマットにて、各VIAの位置(x,y,z)がSIZE内である"
        size_x, size_y, size_z = size
        for i in range(len(via_dic)):
            v = via_mat[i]
            viaiter = 0
            while viaiter < LAYER_MAX:
                x = v[viaiter*3+0]
                y = v[viaiter*3+1]
                z = v[viaiter*3+2]
                if (x == 0) and (y == 0) and (z == 0): break
                if not ( (0 <= x < size_x) and (0 <= y < size_y) and (1 <= z <= size_z) ): return False
                viaiter+=1
        return True

    def check_via_same_xy(self, via_mat, via_dic):
        " C2016_4. 問題フォーマットにて、各VIAの各層での位置(x,y)がすべて一致している"
        for i in range(len(via_dic)):
            v = via_mat[i]
            viaiter = 0
            x0 = 0
            y0 = 0
            while viaiter < LAYER_MAX:
                x = v[viaiter*3+0]
                y = v[viaiter*3+1]
                z = v[viaiter*3+2]
                if x == 0 and y == 0 and z == 0: break
                if viaiter == 0:
                    x0 = x
                    y0 = y
                if (x != x0) or (y != y0): return False
                viaiter+=1
        return True

    def check_num_of_via_and_interlayerlines(self, line_num, line_mat, via_mat, via_dic):
        " C2016_5. 問題フォーマットにて、無駄なVIAが存在しない = 層をまたぐLINE数とVIA数が同じ"
        num_interlayer = 0
        for line in range(1, line_num+1):
            (x0,y0,z0,x1,y1,z1) = line_mat[line-1]
            if z0 != z1:
                num_interlayer += 1
        num_via = len(via_dic)
        return (num_interlayer == num_via)

    def check_ans_via_become_num(self, via_mat, via_dic, xmat):
        " C2016_6. 回答フォーマット中で、問題のViaの位置に数字がある (数字しかあえりえないので、!= 0 を確認)"
        for i in range(len(via_dic)):
            v = via_mat[i]
            viaiter = 0
            num0 = 0
            while viaiter < LAYER_MAX:
                x = v[viaiter*3+0]
                y = v[viaiter*3+1]
                z = v[viaiter*3+2]
                if x == 0 and y == 0 and z == 0: break
                num = xmat[z, y+1, x+1]
                if num == 0: return False
                if viaiter == 0:
                    # remember first one. rests should be same
                    num0 = num
                else:
                    if num != num0: return False
                viaiter+=1
        return True

    def separate_via_terminal_and_inter(self, via_mat, via_dic):
        term_via_set = set()
        inter_via_set = set()
        for i in range(len(via_dic)):
            v = via_mat[i]
            viaiter = 0
            l = list()
            while viaiter < LAYER_MAX:
                x = v[viaiter*3+0]
                y = v[viaiter*3+1]
                z = v[viaiter*3+2]
                if x == 0 and y == 0 and z == 0: break
                l.append( (x,y,z) )
                viaiter += 1
            ls = sorted(l, key=lambda s : s[2]) # sort using z
            term_via_min = ls[0]
            term_via_max = ls[-1]
            term_via_set.add(term_via_min)
            term_via_set.add(term_via_max)
            inter_via_set = inter_via_set.union(ls[1:-2])
            assert(term_via_min != None)
            assert(term_via_max != None)
            term_via_set.add(term_via_min)
            term_via_set.add(term_via_max)
        if self.debug:
            print "term_via_set is : ", term_via_set
            print "inter_via_set is: ", inter_via_set
        return (term_via_set, inter_via_set)

    def check_ans_via_is_terminal_or_alone(self, via_mat, via_dic, xmat):
        " C2016_7. 回答フォーマット中で、Viaの端層の数字は、端点である"
        " C2016_8. 回答フォーマット中で、via途中層の数字は、孤立している"
        term_via_set, inter_via_set = self.separate_via_terminal_and_inter(via_mat, via_dic)
        for v in term_via_set:
            x,y,z = v
            if self.is_terminal(xmat, x,y,z) == False:
                if self.debug: print "(%d,%d,%d) is not terminal" % (x,y,z)
                return False
        for v in inter_via_set:
            x,y,z = v
            if self.is_alone(xmat,x,y,z) == False:
                if self.debug: print "(%d,%d,%d) is not alone" % (x,y,z)
                return False
        return True

    def check_ans_via_is_connected_to_line(self, line_num, line_mat, via_mat, via_dic, xmat):
        " C2016_9. 回答フォーマット中で、アルファベット同士の接続はナシ"
        term_via_set, _ = self.separate_via_terminal_and_inter(via_mat, via_dic)
        clear = xmat.copy()
        for x,y,z in term_via_set:
            # 端層のVIA位置から線をたどって、消していく
            term_set = set()
            self.clearConnectedLine(xmat, clear, x+1, y+1, z, term_set)
            if len(term_set) == 0:
                print "Error: VIA on (%d,%d,%d) is not connected to anything..." % (x,y,z)
                return False
            elif len(term_set) >= LINE_TERMINAL_MAX:
                print "Error: VIA on (%d,%d,%d) is connected more than %d points..." % (x,y,z, LINE_TERMINAL_MAX-1)
                return False
            else:
                line_set = self.get_line_set(line_num, line_mat)
                via_set = self.get_via_set(via_mat, via_dic)
                for tx,ty,tz in term_set:
                    if self.debug: print "via", (x,y,z), "is connected to", (tx, ty, tz)
                    if (tx,ty,tz) not in line_set:
                        if self.debug: print "via", (x,y,z), "is not connected to any line"
                        return False
                    elif (tx,ty,tz) in via_set:
                        if self.debug: print "via", (x,y,z), "is connected to other via", (tx, ty, tz)
                        return False
                    else:
                        pass
        return True

    def get_line_set(self, line_num, line_mat):
        line_set = set()
        for line in range(line_num):
            (x0,y0,z0,x1,y1,z1) = line_mat[line]
            line_set.add( (x0,y0,z0) )
            line_set.add( (x1,y1,z1) )
        return line_set
    def get_via_set(self, via_mat, via_dic):
        via_set = set()
        for i in range(len(via_dic)):
            v = via_mat[i]
            viaiter = 0
            while viaiter < LAYER_MAX:
                x = v[viaiter*3+0]
                y = v[viaiter*3+1]
                z = v[viaiter*3+2]
                if (x == 0) and (y == 0) and (z == 0): break
                via_set.add( (x,y,z) )
                viaiter+=1
        return via_set

    def line_length(self, nlines, mat):
        "線の長さを計算する"
        length = np.zeros(nlines+1, dtype=np.integer)
        for z in range(0, mat.shape[0]):
            for y in range(0, mat.shape[1]):
                for x in range(0, mat.shape[2]):
                    num = mat[z,y,x]
                    if num == 0: continue
                    length[num] += 1
                    #print "line_length: (%d,%d) #%02d %d" % (x,y,num,length[num])
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
                        #print "corner: (%d,%d) #%02d %d" % (x,y,num,corner[num])
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
        judges = []
        for i in range(0, len(target_data)):
            if self.verbose: print "i=",i
            r1 = False
            r2 = False
            r3 = False
            r4 = False
            r5 = False
            r7 = False
            mat = target_data[i] # 解答の行列
            if mat.sum() == 0:
                print "ERROR: Zero Matrix"
                continue
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
                try:
                    r7 = self.check_7(input_data, xmat)
                except IndexError, e:
                    print "IndexError:", e
                if self.verbose: print "check_7", r7
            #
            res = r1 and r2 and r3 and r4 and r5 and r7
            print "res=",res
            if res:
                q = self.quality(input_data, mat, xmat)
            else:
                q = 0.0
            judges.append([res,q])
        # 複数解があるときに、同一の解が含まれていたら、２つめ以降は不正解
        r6 = self.check_6(target_data, judges)
        if self.verbose: print "check_6", r6
        #
        return judges
               
    def clean_a(self, q, a):
        "solverが出力する解が変なので、ちゃちゃっときれいにする"
        #print "a=\n", a
        import nlclean
        a2 = []
        for ai in a:
            #print "ai=\n",ai
            mat = ai
            if mat.sum() == 0:
                print "ERROR: Zero Matrix"
                continue
            line_mat = q[2]
            #print "line_mat=\n", line_mat
            #print "clean_a: mat=", mat.shape
            #print "clean_a: mat=\n", mat
            xmat = self.extend_matrix(mat)
            #print "clean_a: xmat=", xmat.shape
            #print "clean_a: xmat=\n", xmat
            #print "clean_a: xmat[1]=\n", xmat[1]
            xmat2 = nlclean.clean(line_mat, xmat[1]) # z=1だけ
            #print "xmat2=\n", xmat2
            #print (xmat==xmat2)
            xmat3 = nlclean.short_cut(line_mat, xmat2)
            #print "clean_a: xmat3=\n", xmat3
            #xmat3 = xmat2
            # xmatをmatに戻す。周囲を1だけ削る
            xmat4 = np.zeros(mat.shape, xmat3.dtype) # Z軸の次元を増やす
            xmat4[0] = xmat3[1:-1, 1:-1]
            #print "clean_a: xmat4=\n", xmat4
            a2.append( xmat4 ) # xmatをmatに戻す。周囲を1だけ削る
        return a2

    def generate_A_data(self, a2):
        "clean_aを通したあとの、回答データを、ADC形式に変換する"
        crlf = "\r\n" # DOSの改行コード
        firsttime = True
        out = None
        for ai in a2:
            zz,yy,xx = ai.shape
            if firsttime:
                firsttime = False
                out = "SIZE %dX%d" % (xx, yy) + crlf
            for y in range(0, yy):
                for x in range(0, xx):
                    out += "%02d" % ai[0,y,x]
                    if x == ai.shape[1]-1:
                        out += crlf
                    else:
                        out += ","
            out += crlf
        return out

    def graphic_png(self, q, a, filename):
        "回答データをグラフィックとして描画"
        import nldraw
        images = nldraw.draw(q, a, self)
        base = re.sub("\.png", "", filename)
        num = 0
        res = []
        for img in images:
            file = "%s.%d.png" % (base, num)
            img.writePng(file)
            #print file
            res.append(file)
            num += 1
        return res
        
    def graphic_gif(self, q, a, filename):
        "回答データをグラフィックとして描画"
        import nldraw
        images = nldraw.draw(q, a, self)
        base = re.sub("\.gif", "", filename)
        num = 0
        res = []
        for img in images:
            file = "%s.%d.gif" % (base, num)
            img.writeGif(file)
            #print file
            res.append(file)
            num += 1
        return res
    
    def usage(self):
        print "usage:",sys.argv[0],
        print """
-h|--help
-d|--debug
-v|--verbose
-i|--input=FILE
-t|--target=FILE
-c|--clean=FILE
-p|--png=FILE
-g|--gif=FILE
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
            judges = self.check( input_data, target_data )
            print "judges = ", judges
            if gif is not None:
                self.graphic_gif(input_data, target_data, gif)
            if png is not None:
                self.graphic_png(input_data, target_data, png)
        if input_file is not None and target_file is not None:
            self.check_filename(input_file, target_file)



if __name__ == "__main__":
    o = NLCheck()
    o.main()
    #o.check_filename("NL_Q04.txt", "NL_R04.txt")
    #o.check_filename("NL_Q04.txt", "T09_A04.txt")
    #o.check_filename("nl_q04.txt", "t09_a04.txt")


# Local Variables:
# mode: python
# coding: utf-8    
# End:             
