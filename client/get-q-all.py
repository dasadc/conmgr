#!/usr/bin/env python
# -*- coding: utf-8 ; mode: python -*-
#
# すべてのデQータをダウンロードする。
#
#

from adcclient import ADCClient
import re

cli = ADCClient()
cli.read_config()

def get_q(qnum):
    resx = cli.get_q([qnum])
    res = resx[0]
    text = res[6]['msg']
    return text


res = cli.get_q([])
qlist = res[6]['msg']
lines = qlist.splitlines()
regexp = re.compile('Q([0-9]+)')
for line in lines:
    line = line.strip() # 先頭と末尾の空白文字を抜く
    m = regexp.match(line)
    if m is not None:
        qnum = int(m.group(1))
        #print "adccli get-q %d" % (qnum)
        text = get_q(qnum)
        file = "Q%02d.txt" % qnum
        with open(file, "w") as f:
            f.write(text)
        print file
