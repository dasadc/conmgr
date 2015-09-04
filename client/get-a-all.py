#!/usr/bin/env python
# -*- coding: utf-8 ; mode: python -*-
#
# すべてのAデータをダウンロードする。administratorでログインして実行すること。
#
#

from adcclient import ADCClient
import re

cli = ADCClient()
cli.read_config()

crlf = "\r\n" # DOSの改行コード

def get_a(user, anum):
    cli.username = user
    resx = cli.get_a([anum])
    res = resx[0]
    text = res[6]['msg']
    # 1行めは、「GET A1」みたいな文字列なので、取り除く。冗長だなw
    tmp = text.splitlines()
    text2 = crlf.join(tmp[1:]) # 2行め以降から
    text2 += crlf # 末尾にも改行
    return text2


res = cli.get_admin_a_all([])
alist = res[6]['msg']

lines = alist.splitlines()
n = 0  # 行番号
na = 0 # データ数

# A01 (ADC-1) 2015-08-27 13:34:49 JST+0900
#  ^^  ^^^^^
regexp = re.compile('A([0-9]+)\s\((.*)\)\s.*')

for line in lines:
    line = line.strip() # 先頭と末尾の空白文字を抜く
    n += 1
    if n == 1: # 1行めはデータ数
        na = int(line)
        #print "na=",na
        continue
    m = regexp.match(line)
    if m is not None:
        #print m.group(1), m.group(2)
        anum = int(m.group(1))
        user = m.group(2)
        #print "adccli --user %s get-a %d" % (user, anum)
        text = get_a( user, anum)
        file = "%s_A%02d.txt" % (user, anum)
        with open(file, "w") as f:
            f.write(text)
        print file
