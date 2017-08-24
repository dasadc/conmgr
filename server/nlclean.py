# -*- coding: utf-8 ; mode: python -*-
#
# 冗長な線を削除する
#
# Copyright (C) 2015 Fujitsu
# Copyright (C) 2017 DA Symposium


from nlcheck import NLCheck
import numpy as np




def distance(line_mat, xmat):
    "距離を数え上げる"
    xd = np.full( xmat.shape, -1, np.integer ) # 距離の行列。初期値-1
    # 始点の距離を0とする
    for i in range(0, line_mat.shape[0]):
        (x0,y0,z0, x1,y1,z1) = line_mat[i]
        xd[y0+1,x0+1] = 0                 # 座標が+1ずれる
    update = True
    while update:
        update = False
        for y in range(1, xd.shape[0]-1):     # 座標が+1ずれる
            for x in range(1, xd.shape[1]-1): # 座標が+1ずれる
                num = xmat[y,x]
                for p in ( (y-1,x), (y,x+1), (y,x-1), (y+1,x) ):
                    if num == xmat[p]: # 隣接セルが同じ数字
                        if xd[p] == -1: continue
                        dnew = xd[p] + 1
                        if (xd[y,x] == -1) or (dnew < xd[y,x]):
                            xd[y,x] = dnew # 距離を更新
                            update = True
    return xd

def distance1(num, line_mat, xmat):
    "1本の線について、空き地を通ることを許して、距離を数え上げる"
    xd = np.full( xmat.shape, -1, np.integer ) # 距離の行列。初期値-1
    # 始点の距離を0とする
    (x0,y0,z0, x1,y1,z1) = line_mat[num-1]   # 線の番号は1から始まる
    xd[y0+1,x0+1] = 0                 # 座標が+1ずれる
    update = True
    while update:
        update = False
        for y in range(1, xd.shape[0]-1):     # 座標が+1ずれる
            for x in range(1, xd.shape[1]-1): # 座標が+1ずれる
                if not (xmat[y,x] in (num, 0)): continue
                for p in ( (y-1,x), (y,x+1), (y,x-1), (y+1,x) ):
                    dnew = xd[p] + 1
                    if xmat[p] == num or True: #???
                        if xd[p] == -1: continue
                        dnew = xd[p] + 1
                        if (xd[y,x] == -1) or (dnew < xd[y,x]):
                            xd[y,x] = dnew # 距離を更新
                            update = True
    return xd

def min_route(line_mat, xmat, xd):
    # 終点から最短距離をたどって始点に戻る
    xkeep = np.zeros( xd.shape, np.integer )
    # foundは、線ごとの、今までに見つかった最短距離
    found = np.zeros( line_mat.shape[0]+1, np.integer ) # 線の番号は1から始まるので+1
    for i in range(0, line_mat.shape[0]):
        (x0,y0,z0, x1,y1,z1) = line_mat[i]
        xkeep[y1+1,x1+1] = 1                  # 座標が+1ずれる
        found[i+1] = xd[y1+1,x1+1]            # 初期値
    update = True
    while update:
        update = False
        for y in range(1, xd.shape[0]-1):     # 座標が+1ずれる
            for x in range(1, xd.shape[1]-1): # 座標が+1ずれる
                if xkeep[y,x] == 0: continue
                #今いるのは、keepセル
                #最短経路となるセルを探す
                pmin = None
                xdmin = found[xmat[y,x]] # 初期値は、現時点での最短距離
                for p in ( (y-1,x), (y,x+1), (y,x-1), (y+1,x) ):
                    if xmat[y,x] != xmat[p]: continue
                    # 隣接セルは同じ数値である
                    if xkeep[p] == 0 and xd[p] < xdmin:
                        xdmin = xd[p]
                        pmin = p
                if pmin is not None:
                    xkeep[pmin] = 1
                    found[xmat[pmin]] = xd[pmin]
                    update = True
    return xkeep

def min_route1(num, line_mat, xmat, xd):
    # 終点から最短距離をたどって始点に戻る
    xkeep = np.zeros( xd.shape, np.integer )
    # foundは、線ごとの、今までに見つかった最短距離
    found = np.zeros( line_mat.shape[0]+1, np.integer ) # 線の番号は1から始まるので+1
    (x0,y0,z0, x1,y1,z1) = line_mat[num-1]
    xkeep[y1+1,x1+1] = 1                  # 座標が+1ずれる
    found[num] = xd[y1+1,x1+1]            # 初期値
    update = True
    while update:
        update = False
        for y in range(1, xd.shape[0]-1):     # 座標が+1ずれる
            for x in range(1, xd.shape[1]-1): # 座標が+1ずれる
                if xkeep[y,x] == 0: continue
                #今いるのは、keepセル
                #最短経路となるセルを探す
                pmin = None
                xdmin = found[num] # 初期値は、現時点での最短距離
                for p in ( (y-1,x), (y,x+1), (y,x-1), (y+1,x) ):
                    if not (xmat[p] in (num, 0)): continue
                    # 隣接セルは同じ数値か、空き地である
                    if xkeep[p] == 0 and xd[p] != -1 and xd[p] < xdmin:
                        xdmin = xd[p]
                        pmin = p
                if pmin is not None:
                    xkeep[pmin] = 1
                    found[num] = xd[pmin]
                    update = True
    return xkeep

def clean(line_mat, xmat):
    "枝分かれしている、冗長部分を削除"
    xd = distance(line_mat, xmat)
    xkeep = min_route(line_mat, xmat, xd)
    xmat2 = xmat * xkeep
    return xmat2

def short_cut(line_mat, xmat2):
    "迂回している個所を、より短い経路になるように、引き直す"
    xmat3 = np.array(xmat2) # コピーする
    for num0 in range(0, line_mat.shape[0]):
        num = num0 + 1
        xd2 = distance1(num, line_mat, xmat3)
        xkeep2 = min_route1(num, line_mat, xmat3, xd2)
        # もともとnumのセルを空白にして、
        xmat3[xmat3==num] = 0
        # xkeep2の位置に、numの線を引き直す
        xmat3 += xkeep2*(num)
    return xmat3
