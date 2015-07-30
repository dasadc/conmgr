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


class NLCheck:
    "アルゴリズムデザインコンテスト（ナンバーリンクパズル）の回答チェック"

    def __init__(self):
        self.debug = False
        self.verbose = False


    def read_input_file(self, file):
        """問題ファイルを読み込む
        Args:
            file: ファイルのパス名
        """
        # "U" universal newline, \n, \r\n, \r
        with open(file, "rU") as f:
            return self.read_input_data(f)
        #str = open(file).read()
        #return self.read_input_str(str)


    def read_input_str(self, str):
        """問題データ（テキスト文字列）を読み込む
        Args:
            str: 文字列

        """
        str = unicode(str)
        f = io.StringIO(str, newline=None)
        ret = self.read_input_data(f)
        f.close()
        return ret


    def read_input_data(self, f):
        """問題データを読み込む
        Args:
            f: fileオブジェクト
        """
        size = None
        line_num = 0
        line_mat = None
        pSIZE = re.compile('SIZE +([0-9]+)X([0-9]+)', re.IGNORECASE)
        pLINE_NUM = re.compile('LINE_NUM +([0-9]+)', re.IGNORECASE)
        pLINE = re.compile('LINE#(\d+) +\((\d+),(\d+)\)-\((\d+),(\d+)\)', re.IGNORECASE)
        while True:
            line = f.readline()
            if line == "": break # EOFのとき
            line = line.rstrip() # chompみたいに、改行コードを抜く
            if line == "": continue # 空行のとき
            if self.debug: print "line=|%s|" % str(line)
            m = pSIZE.match(line)
            if m is not None:
                size = (int(m.group(1)), int(m.group(2)))
                continue
            m = pLINE_NUM.match(line)
            if m is not None:
                line_num = int(m.group(1))
                # line_num行、4列の行列
                line_mat = np.zeros((line_num,4), dtype=np.integer)
                continue
            m = pLINE.match(line)
            if m is not None:
                num = int(m.group(1)) # LINE#番号
                if num <= 0 or line_num < num:
                    print "ERROR: LINE# range: ", str(line)
                    break
                for i in range(0,4):
                    line_mat[num-1, i] = int(m.group(2+i))
                continue
            print "WARNING: unknown: ", str(line)
        #print "size=",size
        #print "line_num=",line_num
        #print line_mat
        return (size, line_num, line_mat)


    def read_target_file(self, file):
        "チェック対象ファイルを読み込む"
        # "U" universal newline, \n, \r\n, \r
        with open(file, "rU") as f:
            return self.read_target_data(f)
        #str = open(file).read()
        #return self.read_target_str(str)


    def read_target_str(self, str):
        "チェック対象を文字列から読み込む"
        str = unicode(str)
        f = io.StringIO(str, newline=None)
        ret = self.read_target_data(f)
        f.close()
        return ret


    def read_target_data(self, f):
        "チェック対象データを読み込む"
        size = None
        mat = None
        line_cnt = 0
        results = []
        pSIZE = re.compile('SIZE +([0-9]+)X([0-9]+)', re.IGNORECASE)
        # "U" universal newline, \n, \r\n, \r
        while True:
            line = f.readline()
            eof = (line == "")
            line = line.rstrip() # chompみたいに、改行コードを抜く
            if line == "":       # 空行 or EOFのとき
                if mat is not None:
                    results.append(mat) # 解を追加
                    mat = None
                    line_cnt = 0
                    if self.debug: print ""
                if eof:
                    break
                else:
                    continue
            if self.debug: print "line=|%s|" % str(line)
            # まず SIZE行があるはず
            m = pSIZE.match(line)
            if m is not None:
                # SIZE行が現れた
                if size is not None:
                    print "WARNING: too many SIZE"
                size = (int(m.group(1)), int(m.group(2)))
                continue
            else:
                if size is None:
                    # まだSIZE行が現れていない
                    print "WARNING: unknown: ", str(line)
                    continue
            # matを初期化
            if mat is None:
                if size is None:
                    print "ERROR: no SIZE"
                    break
                mat = np.zeros((size[1],size[0]), dtype=np.integer)
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
                mat[line_cnt, i] = val
            line_cnt += 1
        return results


    def extend_matrix(self, mat):
        "行列の上下左右を1行/列ずつ拡大する"
        xmat = np.zeros( (mat.shape[0]+2, mat.shape[1]+2), mat.dtype )
        xmat[1:(mat.shape[0]+1):1, 1:(mat.shape[1]+1):1] = mat
        return xmat


    def is_terminal(self, xmat, x, y):
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
        num = xmat[y1,x1] # 注目点の数字
        eastEq     = (xmat[y1,x1+1] == num)
        northEq    = (xmat[y1-1,x1] == num)
        westEq     = (xmat[y1,x1-1] == num)
        southEq    = (xmat[y1+1,x1] == num)
        eastNotEq  = (xmat[y1,x1+1] != num)
        northNotEq = (xmat[y1-1,x1] != num)
        westNotEq  = (xmat[y1,x1-1] != num)
        southNotEq = (xmat[y1+1,x1] != num)
        #print "num=%d xpos=(%d,%d)" % (num, x1,y1)
        #print eastEq,northEq,westEq,southEq
        #print eastNotEq,northNotEq,westNotEq,southNotEq
        if ( eastEq    and northNotEq and westNotEq and southNotEq or
             eastNotEq and northEq    and westNotEq and southNotEq or
             eastNotEq and northNotEq and westEq    and southNotEq or
             eastNotEq and northNotEq and westNotEq and southEq ) :
            return True
        else:
            return False

    def is_branched(self, xmat, x, y):
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
        num = xmat[y1,x1] # 注目点の数字
        eastEq     = 1 if (xmat[y1,  x1+1] == num) else 0
        northEq    = 1 if (xmat[y1-1,x1  ] == num) else 0
        westEq     = 1 if (xmat[y1,  x1-1] == num) else 0
        southEq    = 1 if (xmat[y1+1,x1  ] == num) else 0
        #print "(%d,%d) %d %d %d %d  %d" % (x,y,eastEq,northEq,westEq,southEq,(eastEq + northEq + westEq + southEq))
        if ( 3 <= eastEq + northEq + westEq + southEq ):
            return True
        else:
            return False


    def clearConnectedLine(self, xmat, clear, x1, y1):
        "線を１本消してみる"
        #print x1,y1
        num = xmat[y1,x1]
        clear[y1,x1] = 0
        # 線が連続しているなら、消す
        neighbors = [[y1,x1+1], [y1-1,x1], [y1,x1-1], [y1+1,x1]]
        for [ny,nx] in neighbors:
            if xmat[ny,nx] == num and clear[ny,nx] != 0:
                self.clearConnectedLine(xmat, clear, nx,ny) # 再帰


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
        (y,x) = mat.shape
        if size[0] == x and size[1] == y:
            return True
        else:
            return False


    def check_1(self, input_data, mat):
        "チェック1. 問題の数字の位置と、同じである。"
        (size, line_num, line_mat) = input_data
        judge = True
        if self.check_size(size, mat) == False:
            print "check_1: mismatch matrix size"
            judge = False
        else:
            for line in range(1, line_num+1):
                (x0,y0,x1,y1) = line_mat[line-1]
                #print "LINE#%d (%d,%d)-(%d,%d)" % (line,x0,y0,x1,y1)
                #print "mat=", mat[y0,x0], "mat=", mat[y1,x1]
                if mat[y0,x0] == line and mat[y1,x1] == line:
                    #print "OK"
                    pass
                else:
                    judge = False
                    print "check_1: mismatch line number:", line
                    print "  LINE#%d (%d,%d)-(%d,%d)" % (line,x0,y0,x1,y1)
                    print "  mat=", mat[y0,x0], "mat=", mat[y1,x1]
        return judge


    def check_2(self, input_data, mat):
        "チェック2. 問題にはない数字があってはいけない。"
        (size, line_num, line_mat) = input_data
        judge = True
        # 1からline_numまでの数字が出現するはず。または空きマス＝0
        (sx,sy) = size
        for y in range(0,sy):
            for x in range(0,sx):
                num = mat[y,x]
                if num < 0 or line_num < num:
                    print "check_2: strange number %d at (%d,%d)" % (num,x,y)
                    judge = False
        return judge


    def check_3(self, input_data, xmat):
        "チェック3. 問題の数字の位置が、線の端点である。"
        (size, line_num, line_mat) = input_data
        judge = True
        for line in range(1, line_num+1):
            (x0,y0,x1,y1) = line_mat[line-1]
            if self.is_terminal(xmat, x0,y0) == False:
                print "check_3: not terminal (%d,%d) #%02d" % (x0,y0,xmat[y0+1,x0+1])
                judge = False
            if self.is_terminal(xmat, x1,y1) == False:
                print "check_3: not terminal (%d,%d) #%02d" % (x1,y1,xmat[y1+1,x1+1])
                judge = False
        return judge


    def check_4(self, xmat):
        "チェック4. 線は枝分かれしない。"
        judge = True
        for y in range(0, xmat.shape[0]-2):
            for x in range(0, xmat.shape[1]-2):
                if xmat[y+1,x+1] == 0: continue # 0は空き地
                if self.is_branched(xmat, x,y) == True:
                    print "check_4: found branch (%d,%d) #%02d" % (x,y,xmat[y+1,x+1]) # 座標が1だけずれている
                    judge = False
        return judge


    def check_5(self, input_data, xmat):
        "チェック5. 線はつながっている。"
        (size, line_num, line_mat) = input_data
        judge = True
        clear = xmat.copy()
        for line in range(1, line_num+1):
            (x0,y0,x1,y1) = line_mat[line-1]
            # 始点から線をたどって、消していく
            self.clearConnectedLine(xmat, clear, x0+1, y0+1)
            #print clear[1:clear.shape[0]-1,1:clear.shape[1]-1]
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
            mat = target_data[i] # 解答の行列
            r1 = self.check_1(input_data, mat)
            if self.verbose: print "check_1", r1
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
            judges.append(res)
        # 複数解があるときに、同一の解が含まれていたら、２つめ以降は不正解
        r6 = self.check_6(target_data, judges)
        if self.verbose: print "check_6", r6
        #
        return judges
                

    def usage(self):
        print "usage:",sys.argv[0],
        print """
-h|--help
-d|--debug
-v|--verbose
-i|--input=FILE
-t|--target=FILE
"""

    def main(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hdvi:t:", ["help","debug","verbose","input=","target="])
        except getopt.GetoptError:
            self.usage()
            sys.exit(2)
        input_data  = None  # 問題データ
        target_data = None  # チェック対象とする解答データ
        input_file = None
        target_file = None
        for o,a in opts:
            if o in ("-h","--help"):
                self.usage()
                sys.exit()
            elif o in ("-d","--debug"):
                self.debug = True 
            elif o in ("-v","--verbose"):
                self.verbose = True
            elif o in ("-i","--input"):
                input_data = self.read_input_file(a)
                input_file = a
                if self.verbose: print "input=", input_data
            elif o in ("-t","--target"):
                target_data = self.read_target_file(a)
                target_file = a
                if self.verbose: print "target=\n", target_data
        if input_data is not None and target_data is not None:
            judges = self.check( input_data, target_data )
            print "judges = ", judges
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
