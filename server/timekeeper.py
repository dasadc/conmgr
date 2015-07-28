# -*- coding: utf-8 -*-
#
# 時計の時刻に基づいて、状態遷移させる

from google.appengine.ext import ndb
import datetime
from datastore import TimeKeeper

def transition( prev, now, prev_state ):
    "時刻に基づいて、状態遷移"
    if (prev.year == now.year and
        prev.month == now.month and
        prev.day == now.day and
        prev.hour == now.hour):
        same_slot = True
    else:
        same_slot = False
    m = now.minute
    mQup = 3
    mim1 = 15
    mAup = 20
    mim2 = 55
    if 0 <= m and m < mQup:
        new_state = 'im0'
    elif mQup <= m and m < mim1:
        new_state = 'Qup'
    elif mim1 <= m and m < mAup:
        new_state = 'im1'
    elif mAup <= m and m < mim2:
        new_state = 'Aup'
    elif mim2 <= m and m <= 59:
        new_state = 'im2'
    else: # ありえない
        print "transition: BUG" 
        new_state = 'BUG'
    #print "same_slot=%s, prev_state=%s, new_state=%s" % (same_slot, prev_state, new_state)
    return same_slot, new_state


@ndb.transactional
def check():
    clk = TimeKeeper.get_or_insert('CLOCK')
    #                               ^^^^^ Key Name
    #print "clk=", clk
    if clk.state is None:
        clk.state = "init"
        clk.lastUpdate = datetime.datetime.now()
        clk.put()
    now = datetime.datetime.now()
    same_slot, new_state = transition(clk.lastUpdate, now, clk.state)
    old_state = clk.state
    if not same_slot or clk.state != new_state:
        clk.state = new_state
        clk.lastUpdate = now
        clk.put()
        print "TK: state change", clk
    return new_state, old_state
