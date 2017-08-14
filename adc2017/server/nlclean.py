# -*- coding: utf-8 ; mode: python -*-
#
# 冗長な線を削除する
#
# Copyright (C) 2017 Fujitsu


from nlcheck import NLCheck
import numpy as np




def xmat_range(xmat_shape, p):
    if ( (0 < p[0] < xmat_shape[0] - 1) and
         (0 < p[1] < xmat_shape[1] - 1) and
         (0 < p[2] < xmat_shape[2] - 1) ) :
        return(True)
    return(False)

def neighbor_cells(z, y, x):
    return( (z,y-1,x), (z,y,x+1), (z,y,x-1), (z,y+1,x), (z+1,y,x), (z-1,y,x) )

def distance(line_mat, xmat):
    "距離を数え上げる"
    xd = np.zeros( xmat.shape, np.integer ) # 距離の行列。初期値0
    # 始点の距離を0とする
    for i in range(0, line_mat.shape[0]):
        (x0,y0,z0, x1,y1,z1) = line_mat[i]
        if( xmat_range(xd.shape, (z0,y0+1,x0+1)) ):
            xd[z0,y0+1,x0+1] = 1                 # 座標が+1ずれる
    # 変更のあったマスの隣接マスのみを次回の探索対象とする
    spmax = 6 * xd.shape[0] * xd.shape[1] * xd.shape[2]
    spmat = np.zeros((spmax,3), np.integer)
    spmatc = np.zeros((spmax,3), np.integer)
    spcnt = 0
    for i in range(0, line_mat.shape[0]):
        (x0,y0,z0, x1,y1,z1) = line_mat[i]
        (z,y,x) = (z0,y0+1,x0+1)
        for p in ( neighbor_cells(z,y,x) ):
            if ( xmat_range(xmat.shape, p) ):
                if (xmat[p] > 0):
                    spmat[spcnt] = p
                    spcnt = spcnt + 1
    while spcnt > 0:
        spcntc = spcnt
        spcnt = 0
        for sppnt in range(0, spcntc):
            spmatc[sppnt] = spmat[sppnt]
        for sppnt in range(0, spcntc):
            (z,y,x) = spmatc[sppnt]
            num = xmat[z,y,x]
            for q in ( neighbor_cells(z,y,x) ):
                if num == xmat[q]: # 隣接セルが同じ数字
                    if xd[q] == 0: continue
                    dnew = xd[q] + 1
                    if (xd[z,y,x] == 0) or (dnew < xd[z,y,x]):
                        xd[z,y,x] = dnew # 距離を更新
                        for p in ( neighbor_cells(z,y,x) ):
                            if (xmat[p] != num): continue
                            if ( xmat_range(xmat.shape, p) ):
                                spmat[spcnt] = p
                                spcnt = spcnt + 1
    return xd

def distance1(num, line_mat, xmat):
    "1本の線について、空き地を通ることを許して、距離を数え上げる"
    xd = np.zeros( xmat.shape, np.integer ) # 距離の行列。初期値0
    # 始点の距離を0とする
    (x0,y0,z0, x1,y1,z1) = line_mat[num-1]   # 線の番号は1から始まる
    if( xmat_range(xd.shape, (z0,y0+1,x0+1)) ):
        xd[z0,y0+1,x0+1] = 1                 # 座標が+1ずれる
    # 変更のあったマスの隣接マスのみを次回の探索対象とする
    spmax = 6 * xd.shape[0] * xd.shape[1] * xd.shape[2]
    spmat = np.zeros((spmax,3), np.integer)
    spmatc = np.zeros((spmax,3), np.integer)
    spcnt = 0
    (z,y,x) = (z0,y0+1,x0+1)
    for p in ( neighbor_cells(z,y,x) ):
        if ( xmat_range(xmat.shape, p) ):
            if (xmat[p] in (num, 0)):
                spmat[spcnt] = p
                spcnt = spcnt + 1
    while spcnt > 0:
        spcntc = spcnt
        spcnt = 0
        for sppnt in range(0, spcntc):
            spmatc[sppnt] = spmat[sppnt]
        for sppnt in range(0, spcntc):
            (z,y,x) = spmatc[sppnt]
            for q in ( neighbor_cells(z,y,x) ):
                if xd[q] == 0: continue
                dnew = xd[q] + 1
                if (xd[z,y,x] == 0) or (dnew < xd[z,y,x]):
                    xd[z,y,x] = dnew # 距離を更新
                    for p in ( neighbor_cells(z,y,x) ):
                        if not (xmat[p] in (num, 0)): continue
                        if ( xmat_range(xmat.shape, p) ):
                            spmat[spcnt] = p
                            spcnt = spcnt + 1
    return xd

def min_route(line_mat, xmat, xd):
    # 終点から最短距離をたどって始点に戻る
    xkeep = np.zeros( xd.shape, np.integer )
    # foundは、線ごとの、今までに見つかった最短距離
    found = np.zeros( line_mat.shape[0]+1, np.integer ) # 線の番号は1から始まるので+1
    for i in range(0, line_mat.shape[0]):
        (x0,y0,z0, x1,y1,z1) = line_mat[i]
        if( xmat_range(xd.shape, (z1,y1+1,x1+1)) ):
            xkeep[z1,y1+1,x1+1] = 1                  # 座標が+1ずれる
            found[i+1] = xd[z1,y1+1,x1+1]            # 初期値
    # 変更のあったマスの隣接マスのみを次回の探索対象とする
    spmax = 6 * xd.shape[0] * xd.shape[1] * xd.shape[2]
    spmat = np.zeros((spmax,3), np.integer)
    spmatc = np.zeros((spmax,3), np.integer)
    spcnt = 0
    for i in range(0, line_mat.shape[0]):
        (x0,y0,z0, x1,y1,z1) = line_mat[i]
        (z,y,x) = (z1,y1+1,x1+1)
        if( xmat_range(xmat.shape, (z,y,x)) ):
            if(xmat[z,y,x] > 0):
                spmat[spcnt] = (z,y,x)
                spcnt = spcnt + 1
    while spcnt > 0:
        spcntc = spcnt
        spcnt = 0
        for sppnt in range(0, spcntc):
            spmatc[sppnt] = spmat[sppnt]
        for sppnt in range(0, spcntc):
            (z,y,x) = spmatc[sppnt]
            #今いるのは、keepセル
            #最短経路となるセルを探す
            pmin = None
            xdmin = found[xmat[z,y,x]] # 初期値は、現時点での最短距離
            for p in ( neighbor_cells(z,y,x) ):
                if xmat[z,y,x] != xmat[p]: continue
                # 隣接セルは同じ数値である
                if xkeep[p] == 0 and xd[p] < xdmin:
                    xdmin = xd[p]
                    pmin = p
            if pmin is not None:
                xkeep[pmin] = 1
                found[xmat[pmin]] = xd[pmin]
                if(xd[pmin] > 1):
                    spmat[spcnt] = pmin
                    spcnt = spcnt + 1
    return xkeep

def min_route1(num, line_mat, xmat, xd):
    # 終点から最短距離をたどって始点に戻る
    xkeep = np.zeros( xd.shape, np.integer )
    # foundは、線ごとの、今までに見つかった最短距離
    found = np.zeros( line_mat.shape[0]+1, np.integer ) # 線の番号は1から始まるので+1
    (x0,y0,z0, x1,y1,z1) = line_mat[num-1]
    if( xmat_range(xd.shape, (z1,y1+1,x1+1)) ):
        xkeep[z1,y1+1,x1+1] = 1                  # 座標が+1ずれる
        found[num] = xd[z1,y1+1,x1+1]            # 初期値
    # 変更のあったマスの隣接マスのみを次回の探索対象とする
    spmax = 6 * xd.shape[0] * xd.shape[1] * xd.shape[2]
    spmat = np.zeros((spmax,3), np.integer)
    spmatc = np.zeros((spmax,3), np.integer)
    spcnt = 0
    (z,y,x) = (z1,y1+1,x1+1)
    if ( xmat_range(xmat.shape, (z,y,x)) ):
        spmat[spcnt] = (z,y,x)
        spcnt = spcnt + 1
    while spcnt > 0:
        spcntc = spcnt
        spcnt = 0
        for sppnt in range(0, spcntc):
            spmatc[sppnt] = spmat[sppnt]
        for sppnt in range(0, spcntc):
            (z,y,x) = spmatc[sppnt]
            #今いるのは、keepセル
            #最短経路となるセルを探す
            pmin = None
            xdmin = found[num] # 初期値は、現時点での最短距離
            for p in ( neighbor_cells(z,y,x) ):
                if not (xmat[p] in (num, 0)): continue
                # 隣接セルは同じ数値か、空き地である
                if xkeep[p] == 0 and xd[p] != 0 and xd[p] < xdmin:
                    xdmin = xd[p]
                    pmin = p
            if pmin is not None:
                xkeep[pmin] = 1
                found[num] = xd[pmin]
                if(xd[pmin] > 1):
                    spmat[spcnt] = pmin
                    spcnt = spcnt + 1
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
