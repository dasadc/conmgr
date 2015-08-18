#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Copyright (C) 2015 Fujitsu

import re
import numpy as np
from nlcheck import NLCheck
import sys
import io

def read_input_data(text):
    """問題データ(DAS ADC形式)を読み込む
    Args:
        text: テキストデータ
    """
    def X_ok(x):
        "X座標が範囲を越えてたらFalseを返す"
        if x < 0 or size[0] <= x:
            return False
        else:
            return True
    def Y_ok(y):
        "Y座標が範囲を越えてたらFalseを返す"
        if y < 0 or size[1] <= y:
            return False
        else:
            return True

    msg = ''
    ok = True
    lines = text.splitlines() # LF,CRLF,CR どれでも対応できる
    size = None
    line_num = 0
    line_mat = None
    line_found = None
    pSIZE = re.compile('SIZE\s*([0-9]+)\s*X\s*([0-9]+)', re.IGNORECASE)
    pLINE_NUM = re.compile('LINE_NUM\s*([0-9]+)', re.IGNORECASE)
    pLINE = re.compile('LINE\s*#(\d+)\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)\s*-\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)', re.IGNORECASE)
    # 行の途中に、不必要な空白文字が入っていてもOKと見なす ... '\s*'
    for line in lines:
        #line = line.rstrip() # chompみたいに、改行コードを抜く
        line = line.strip() # 先頭と末尾の空白文字を抜く
        if line == "": continue # 空行のとき
        #print "line=|%s|" % str(line)
        m = pSIZE.match(line)
        if m is not None:
            size = (int(m.group(1)), int(m.group(2)))
            continue
        m = pLINE_NUM.match(line)
        if m is not None:
            line_num = int(m.group(1))
            # line_num行、4列の行列
            line_mat = np.zeros((line_num,4), dtype=np.integer)
            line_found = np.zeros(line_num+1, dtype=np.integer) # LINE_NUM 7なら、1..7を数え上げるので、+1
            continue
        m = pLINE.match(line)
        if m is not None:
            num = int(m.group(1)) # LINE#番号
            if num <= 0 or line_num < num:
                msg += "ERROR: LINE_NUM range overflow: %s\n" % str(line)
                ok = False
                break
            line_found[num] += 1
            if 1 < line_found[num]:
                msg += "ERROR: duplicated line number: %s\n" % str(line)
                ok = False
                break
            for i in range(0,4):
                v = int(m.group(2+i))
                line_mat[num-1, i] = v
                # LINEの座標が、範囲を越えていないかチェック
                if i == 0 or i == 2: # X座標
                    if not X_ok(v):
                        msg += "ERROR: X range overflow (%d): %s\n" % (v,str(line))
                        ok = False
                else: # Y座標
                    if not Y_ok(v):
                        msg += "ERROR: Y range overflow (%d): %s\n" % (v,str(line))
                        ok = False
            continue
        msg += "WARNING: skipped unknown line: %s\n" % str(line) 
    #print "size=",size
    #print "line_num=",line_num
    #print line_mat
    # 未定義のLINE#があるか？ LINE#0は元々無い（range checkで引っ掛かる）
    for num in range(1, line_num+1):
        if line_found[num] == 0:
            msg += "ERROR: LINE#%d not found\n" % num
            ok = False
    return (size, line_num, line_mat, msg, ok)

def generate_Q_data(size, line_num, line_mat):
    "アルゴリズムデザインコンテスト用の書式の問題テキストデータを作る"
    crlf = "\r\n" # DOSの改行コード
    out = "SIZE %dX%d" % size + crlf
    out += "LINE_NUM %d" % line_num + crlf
    j = 0
    for i in line_mat:
        j += 1
        out += "LINE#%d (%d,%d)-(%d,%d)" % (j, i[0],i[1],i[2],i[3]) + crlf
    return out

def check_A_data(a_text, q_text):
    """回答データのチェックをする"""
    nlc = NLCheck()
    #nlc.debug = True
    #print "Q=",q_text
    #print "A=",a_text
    out = io.BytesIO() # io.StringIO()だとTypeError: unicode argument expected, got 'str'
    #out = open("/tmp/nlcheck_log.txt","w")
    #--------------------------------------
    sys.stdout = out # 標準出力を付け替える
    input_data  = nlc.read_input_str(q_text)  # 問題データ
    target_data = nlc.read_target_str(a_text) # 回答データ
    nlc.verbose = True
    judges = nlc.check(input_data, target_data)
    print "judges = ", judges
    #results = escape(out.getvalue()) # from xml.sax.saxutils import escape, unescape ここでは不要か？！
    msg = out.getvalue()
    out.close()
    sys.stdout = sys.__stdout__ # もとに戻す
    #--------------------------------------
    return judges, msg

if __name__ == "__main__":
    import sys
    text = open(sys.argv[1], 'r').read()
    res = read_input_data(text)
    if res[4]:
        q = generate_Q_data(res[0], res[1], res[2])
        print "OK\n",q
        # 問題ファイルを書き出す
        with open("Q.txt", "w") as f:
            f.write(q)
    else:
        print "NG\n", text, res[3]
