#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Copyright (C) 2015 Fujitsu

import re
import numpy as np
from nlcheck import NLCheck, LAYER_MAX
import sys
import io

def read_input_data(text):
    nlc = NLCheck()
    ok = True
    msg = ""
    #--------------------------------------
    out = io.BytesIO() # io.StringIO()だとTypeError: unicode argument expected, got 'str'
    backup_stdout = sys.stdout
    sys.stdout = out # 標準出力を付け替える
    ret = None
    try:
        ret = nlc.read_input_str(text)
    except:
        ok = False
        ret = (None, None, None, None, None)
    size, line_num, line_mat, via_mat, via_dic = ret
    msg = out.getvalue()
    out.close()
    sys.stdout = backup_stdout # もとに戻す
    #--------------------------------------
    if "ERROR" in msg:
        ok = False
        print msg
    return (size, line_num, line_mat, via_mat, via_dic, msg, ok)

def generate_Q_data(size, line_num, line_mat, via_mat, via_dic):
    "アルゴリズムデザインコンテスト用の書式の問題テキストデータを作る"
    crlf = "\r\n" # DOSの改行コード
    out = "SIZE %dX%dX%d" % size + crlf
    out += "LINE_NUM %d" % line_num + crlf
    j = 0
    for i in line_mat:
        j += 1
        out += "LINE#%d (%d,%d) (%d,%d)" % (j, i[0],i[1],i[2],i[3]) + crlf

    via_dic_inv = dict()
    for a,i in via_dic.items():
        via_dic_inv[i] = a
    for i in range(len(via_dic)):
        out += "VIA#%s " % via_dic_inv[i+1]
        v = via_mat[i]
        viaiter = 0
        while viaiter < LAYER_MAX:
            vx = v[viaiter*3+0]
            vy = v[viaiter*3+1]
            vz = v[viaiter*3+2]
            if (vx == 0) and (vy == 0) and (vz == 0): break
            out += "(%d,%d,%d) " % (vx, vy, vz)
            viaiter+=1
        out += crlf
    return out

def check_A_data(a_text, q_text):
    """回答データのチェックをする"""
    nlc = NLCheck()
    #nlc.debug = True
    #print "Q=",q_text
    #print "A=",a_text
    q = q_text.encode('utf-8')
    print q #TODO: debug
    print a_text
    #--------------------------------------
    out = io.BytesIO() # io.StringIO()だとTypeError: unicode argument expected, got 'str'
    sys.stdout = out # 標準出力を付け替える
    input_data  = nlc.read_input_str(q) # 問題データ q_text (unicode encoded)
    target_data = nlc.read_target_str(a_text) # 回答データ(string)
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
    size, line_num, line_mat, via_mat, via_dic, msg, ok = res
    if ok:
        q = generate_Q_data(size, line_num, line_mat, via_mat, via_dic)
        print "OK\n",q
        # 問題ファイルを書き出す
        #with open("Q.txt", "w") as f:
        #    f.write(q)
        print q
    else:
        print "NG\n", text, msg
