# -*- coding: utf-8 -*-
#

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
    lines = text.splitlines()
    size = None
    line_num = 0
    line_mat = None
    pSIZE = re.compile('SIZE +([0-9]+)X([0-9]+)', re.IGNORECASE)
    pLINE_NUM = re.compile('LINE_NUM +([0-9]+)', re.IGNORECASE)
    pLINE = re.compile('LINE#(\d+) +\((\d+),(\d+)\)-\((\d+),(\d+)\)', re.IGNORECASE)
    for line in lines:
        #line = line.rstrip() # chompみたいに、改行コードを抜く
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


def check_Q_data(size, line_num, line_mat):
    "問題データが正しいかチェックする"
    #あとで作る
    return True


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
    # 今は2014年版の処理しかしていない。★★★あとで実装する
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
