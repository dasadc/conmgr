#!/usr/bin/env python
# -*- coding: utf-8 ; mode: python -*-
#
# adccli score-dumpで取得したスコアデータをデコードして、
# CSV形式で保存するなど。
# 
#

import sys
import cPickle as pickle
import base64
import datetime, time

file = sys.argv[1]
txt = open(file).read()
bin = base64.b64decode(txt)
res = pickle.loads(bin)
score_board, ok_point, q_point, bonus_point, q_factors, result, misc = res
#print res
#print "q_point=\n", q_point
#print misc; exit()

# adccli get-admin-q-list で取り出した出題リストより
# 出題番号は、1..36、全36問
Q_all = range(1,36+1)

# 参加チーム
users = ['ADC-1', 'ADC-2', 'ADC-3', 'ADC-4', 'ADC-5', 'ADC-6', 'ADC-7']

import csv

f = open("score.csv", "w")
writer = csv.writer(f)
row_data = ['A number', 'Team', 'Ok point', 'Bonus point', 'Q factor', 'Q point', 'Point']
writer.writerow(row_data)

# スコアボード
f2 = open("scoreboard.csv", "w")
writer2 = csv.writer(f2)
row_data = ["-"]
for q in Q_all:
    row_data.append( 'A%02d' % q )
row_data.append( 'Total' )
n = len(row_data)
writer2.writerow(row_data)
scbd = {}
for user in users:
    tmp = [0]*n
    tmp[0] = user
    scbd[user] = tmp

# ログメッセージ
f3 = open("result.csv", "w")
writer3 = csv.writer(f3)

    
# 結果を詳細に出力
for q in Q_all:
    q00 = 'Q%02d' % q
    a00 = 'A%02d' % q
    #print a00
    for user in users:
        #print "user=%s" % user
        ok = 'NA'
        if a00 in ok_point:
            if user in ok_point[a00]:
                ok = ok_point[a00][user]
        bonus = 'NA'
        if a00 in bonus_point:
            if user in bonus_point[a00]:
                bonus = bonus_point[a00][user]
        q_factor = 'NA'
        if a00 in q_factors:
            if user in q_factors[a00]:
                q_factor = q_factors[a00][user]
        q_pt = 'NA'
        if a00 in q_point:
            if user in q_point[a00]:
                q_pt = q_point[a00][user]
        log = ''
        if a00 in result:
            if user in result[a00]:
                log = result[a00][user]
        pt = 0
        try:
            i = score_board['/header/'].index(a00)
            pt = score_board[user][i]
            scbd[user][q] = pt
        except ValueError:
            pass
        #
        row_data = [a00, user, ok, bonus, q_factor, q_pt, pt]
        writer.writerow(row_data)
        #
        row_data = [a00, user, log]
        writer3.writerow(row_data)


for user in users:
    scbd[user][-1] = sum(scbd[user][1:-1])
    writer2.writerow(scbd[user])

# その他のデータ date, cpu_sec, mem_byte, misc_text
f4 = open("misc.csv", "w")
writer4 = csv.writer(f4)
row_data = ['unixtime', 'datetime', 'user', 'Anum', 'cpu_sec', 'mem_byte', 'misc_text']
writer4.writerow(row_data)
for anum, info1 in misc.iteritems():
    for user, info2 in info1.iteritems():
        date, cpu_sec, mem_byte, misc_text = info2
        unixtime = time.mktime(date.timetuple())
        row_data = [unixtime, date, user, anum, cpu_sec, mem_byte, misc_text]
        writer4.writerow(row_data)
