#!/usr/bin/env python
# -*- coding: utf-8 ; mode: python -*-
#
# Aファイルを読み込んで、空白マスの割合を計算する
# 
# 
# 実行例 ./space.py ../../ADC2015_QA/A/*txt

import os, sys, re
sys.path.insert(1, '../server')

from nlcheck import NLCheck
nlc = NLCheck()

pat = re.compile('(.*)_A([0-9]+)\.txt')

print "user,A,area,zeros,rate"

for file in sys.argv[1:]:
    res = nlc.read_target_file(file)
    for i in res:
        y,x = i.shape
        area = y*x
        nzeros = len(i[i==0]) # 値が0の個数
        rate = float(nzeros) / (float(area))
        f1 = os.path.basename(file)
        m = pat.match(f1)
        user = '?'
        anum = '?'
        if m is not None:
            user = m.group(1)
            anum = m.group(2)
        print "%s,%d,%d,%d,%f" % (user, int(anum), area, nzeros, rate)
