#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 DA Symposium 2017
# All rights reserved.
#

"""
アルゴリズムデザインコンテスト2017の問題データと正解データを、ランダムに作成する。
"""

from __future__ import print_function
import numpy as np
import random
import sys
sys.path.insert(0, '../server') # あとで直す
from nlcheck import NLCheck
import nldraw2

_size = (3,3,1) # x,y,z
size = None
nlines = 999
retry = 2
debug = False
verbose = False
newline = '\n' # 改行コード


template_move  = 'newsud'                 # 移動方向(6方向)を表す文字列
template_move0 = 'news'*10 + 'ud'         # 垂直移動よりも、水平移動を(10倍)優先する
template_move1 = template_move0 + 'G'*20  # 直進(G)は(20倍)優先する


class dotdict(dict):
    """
    dot.notation access to dictionary attributes
    https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary
    """
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


unit_vec_xyz = dotdict({ 'n': ( 0, -1,  0),
                         'e': ( 1,  0,  0),
                         'w': (-1,  0,  0),
                         's': ( 0,  1,  0),
                         'u': ( 0,  0,  1),
                         'd': ( 0,  0, -1) })
    
class Ban:
    """
    盤のデータ構造
    """

    def __init__(self, x, y, z):
        self.size = dotdict({'x': x, 'y': y, 'z': z})
        self.xmat = np.zeros((z+2, y+2, x+2), dtype=np.integer)
        
    def get_size(self):
        return self.size

    def get(self, x,y,z):
        return self.xmat[z+1, y+1, x+1]
    
    def get_xyz(self, xyz):
        x,y,z = xyz
        return self.xmat[z+1, y+1, x+1]
    
    def set(self, x,y,z, val):
        self.xmat[z+1, y+1, x+1] = val

    def set_xyz(self, xyz, val):
        x,y,z = xyz
        self.xmat[z+1, y+1, x+1] = val

    def print(self):
        print(self.xmat[1:-1, 1:-1, 1:-1])

    def zyx1_to_xyz(self, zyx1):
        return (zyx1[2]-1, zyx1[1]-1, zyx1[0]-1)
    
    def find_zero_random(self, dont_use=[]):
        "値が0の座標を、ランダムに返す"
        cand = []
        for k1, v in np.ndenumerate(self.xmat):
            if self.inside_zyx1(k1):
                xyz = self.zyx1_to_xyz(k1)
                if (v == 0) and (xyz not in dont_use):
                    cand.append(k1)
        if len(cand) == 0:
            return False
        i = random.randint(0, len(cand)-1)
        return self.zyx1_to_xyz(cand[i])

    def inside(self, xyz):
        "座標xyzが、盤の中にあるか？"
        x, y, z = xyz
        if ((0 <= x and x < self.size.x) and
            (0 <= y and y < self.size.y) and
            (0 <= z and z < self.size.z)):
            return True
        else:
            return False

    def inside_zyx1(self, zyx1):
        "(+1されている)座標zyx1が、盤の中にあるか？"
        z = zyx1[0]-1
        y = zyx1[1]-1
        x = zyx1[2]-1
        return self.inside((x,y,z))

    def move_xyz_to(self, xyz, move):
        "座標xyzから、move(=n,e,w,s,u,d)の方向に移動した座標を返す"
        uv = unit_vec_xyz[move]
        return (xyz[0] + uv[0], xyz[1] + uv[1], xyz[2] + uv[2])

    def rip_line(self, number):
        "線numberを、引き剥がす"
        indexes = np.where(self.xmat == number)
        n = len(indexes[0])
        #print('rip_line', number, n)
        #self.print()
        for j in range(0, n):
            z = indexes[0][j]
            y = indexes[1][j]
            x = indexes[2][j]
            #print(x,y,z)
            self.xmat[z,y,x] = 0
        #self.print()

    def empty_cells(self):
        "空白マスの数を返す"
        indexes = np.where(self.xmat[1:-1, 1:-1, 1:-1] == 0)
        return len(indexes[0])
        
    def neighbors(self, xyz):
        x, y, z = xyz
        return dotdict({ 'n': self.get(x,   y-1, z),     # north
                         'e': self.get(x+1, y,   z),     # east
                         'w': self.get(x-1, y,   z),     # west
                         's': self.get(x,   y+1, z),     # south
                         'u': self.get(x,   y,   z+1),   # upstairs
                         'd': self.get(x,   y,   z-1)})  # downstairs
    def A_data(self):
        out = 'SIZE %dX%dX%d%s' % (self.size.x, self.size.y, self.size.z, newline)
        for z in range(0, self.size.z):
            out += 'LAYER %d%s' % (z+1, newline)
            for y in range(0, self.size.y):
                row = ''
                for x in range(0, self.size.x):
                    num = self.get_xyz((x,y,z))
                    row += '%02d' % num
                    if x < self.size.x -1:
                        row += ','
                out += row + newline
        return out

    
def vector_char(a, b):
    """
    a から bへのベクトルを、n,e,w,s,u,dで求める。aとbは隣接していること。
    """
    ba = (b[0]-a[0], b[1]-a[1], b[2]-a[2])
    for k,v in unit_vec_xyz.iteritems():
        if ba == v:
            return k
    raise Exception('vector not found')


def draw_line_next(ban, number=0, prev=None, curr=None):
    """
    1マスだけ、線を引く。
    #
    #     prev   curr   next_xyz
    #      ●     ●     ○
    #
    #
    """
    neig = ban.neighbors(curr)
    # sは、候補となる方角の文字(n,e,w,s,u,d)で構成された文字列。このあとシャッフルする
    if prev == None:
        s = template_move0
    else:
        s = template_move1
        vec_char = vector_char(prev, curr)
        s = s.replace('G', vec_char)
    if debug: print('0: s=', s)
    # 隣接セル(n,e,w,s,u,d)に、線が引けるか？事前にチェックする
    for i in range(0, len(template_move)):
        vec_char = template_move[i]
        next_xyz = ban.move_xyz_to(curr, vec_char)
        if debug: print('curr=', curr, '  vec_char=', vec_char, '  next_xyz=', next_xyz)
        drawable = True
        if not ban.inside(next_xyz):
            drawable = False
        elif ban.get_xyz(next_xyz) != 0:
            drawable = False
        else:
            # next_xyzの隣接セルで、番号がnumberのセルの個数を数える
            next_neigh = ban.neighbors(next_xyz)
            same_number = 0
            for j in range(0, len(template_move)):
                if next_neigh[template_move[j]] == number:
                    same_number += 1
            if 2 <= same_number:
                # 2以上あるということは、ループができるということ（そのはず）
                drawable = False
        if not drawable:
            s = s.replace(vec_char, '') # 候補から削除
    if debug: print('1: s=', s)

    if len(s) == 0:
        return curr, None # もう線を引けない
    rs = ''.join(random.sample(s, len(s))) # sをシャフルしてrsに
    vec_char = rs[0]
    if debug: print('vec_char=', vec_char)

    next_xyz = ban.move_xyz_to(curr, vec_char)
    ban.set_xyz(next_xyz, number)
    prev = curr
    curr = next_xyz
    return prev, curr


def draw_line(ban, number, max_retry=1, dont_use=[], Q_data={}):
    trial = 0
    if debug: print('number=', number)
    while trial < max_retry:
        trial += 1
        #print('dnot_use=', dont_use)
        start = ban.find_zero_random(dont_use) # 始点をランダムに決定
        end = None
        if debug: print('start=', start)
        if start is False:
            return False
        ban.set_xyz(start, number)
        line_length = 0
        prev = None
        curr = start
        while curr is not None:
            line_length += 1
            if debug: print('prev=', prev, '  curr=', curr)
            if debug: ban.print()
            prev, curr = draw_line_next(ban, prev=prev, curr=curr, number=number)
            if curr != None:
                end = curr
        if line_length == 1:
            # 1マスも引けなかった。1マスだけの線はありえないので、消す。
            # startの値はタプルなので、copyしなくてよいはず
            if debug: print('clear start=', start)
            ban.set_xyz(start, 0)
            dont_use.append(start)
            trial -= 1 # この場合、trial回数は数えないことにする
        elif (line_length <= 2) and (trial < max_retry): # 短い線は、おもしろくないので、引き直す
            if verbose: print('rip LINE#%d' % number)
            ban.rip_line(number)
        else:
            # 線が引けた
            Q_data[number] = {'start': start, 'end': end, 'length': line_length}
            return True
        # リトライする
        if verbose:
            print('retry %d/%d LINE#%d, #dont_use=%d' % (trial, max_retry, number, len(dont_use)))

    # 線が引けなかった
    return False

def generate(x,y,z, num_lines=0, max_retry=1, Q_data={}, dont_use=[]):
    ban = Ban(x,y,z)
    for line in range(1, 1+num_lines):
        if draw_line(ban, line, max_retry=max_retry, dont_use=dont_use, Q_data=Q_data) == False:
            return line-1, ban
    return num_lines, ban

def Q_text(Q_data):
    size = Q_data['size']
    out = 'SIZE %dX%dX%d%s' % (size[0], size[1], size[2], newline)
    num_lines = Q_data['line_num']
    out += 'LINE_NUM %d%s' % (num_lines, newline)
    for j in range(1, 1+num_lines):
        s = Q_data[j]['start']
        e = Q_data[j]['end']
        out += 'LINE#%d (%d,%d,%d) (%d,%d,%d)%s' % (j, s[0],s[1],s[2]+1, e[0],e[1],e[2]+1, newline)
    return out

def run(x,y,z, num_lines=0, max_retry=1, basename=None):
    """
    指定されたサイズ、線数の問題データと正解データを自動生成して、ファイルbasename*.txtに書き出す。
    @param x,y,z 盤のサイズ
    @param num_lines 線の本数
    @param basename 出力先ファイル名。問題ファイルはbasename_adc.txt、正解ファイルはbasename_adc_sol.txtになる。
    """
    Q = {'size': (x, y, z)}
    num_lines, ban = generate(x, y, z, num_lines=num_lines, max_retry=max_retry, Q_data=Q)
    Q['line_num'] = num_lines
    Q['empty_cells'] = ban.empty_cells()
    print('number of lines:', Q['line_num'])
    print('number of empty cells:', Q['empty_cells'])
    #if verbose: ban.print()
    #if verbose: print('Q=', Q)
    txtQ = Q_text(Q)
    txtA = ban.A_data()

    # nlcheckする
    nlc = NLCheck()
    q = nlc.read_input_str(txtQ)
    a = nlc.read_target_str(txtA)
    #nlc.verbose = verbose
    judges = nlc.check( q, a )
    print("judges = ", judges)

    # 描画する
    nldraw2.setup_font('nonexistent') # あとで考える
    images = nldraw2.draw(q, a, nlc)
    for num, img in enumerate(images):
        ifile = "%s.%d.gif" % (basename, num+1) # 層の番号は1から始まる
        img.save(ifile, 'gif')
        print(ifile)
    if 1 < len(images):
        nldraw2.merge_images(images).save(basename+'.gif', 'gif')

    # QとAを出力する
    if basename is None:
        print(txtQ)
        print(txtA)
    else:
        qfile = '%s_adc.txt' % basename
        with open(qfile, 'w') as f:
            f.write(txtQ)
        afile = '%s_adc_sol.txt' % basename
        with open(afile, 'w') as f:
            f.write(txtA)
    

def test1():
    "動作確認"
    x,y,z = _size
    ban = Ban(x,y,z)
    ban.set(0,0,0, 1)
    ban.set(1,0,0, 2)
    ban.set(0,1,0, 3)
    ban.set(x-1, y-1, z-1, 1)
    ban.set(x-2, y-1, z-1, 2)
    ban.set(x-1, y-2, z-1, 3)
    ban.print()
    

def main():
    global size, nlines, debug, verbose
    import argparse
    parser = argparse.ArgumentParser(description='NumberLink Q generator')
    parser.add_argument('-d', '--debug', action='store_true', default=debug, help='enable debug (default: %(default)s)')
    parser.add_argument('-v', '--verbose', action='store_true', default=verbose, help='verbose output (default: %(default)s)')
    parser.add_argument('-x', metavar='X', default=_size[0], type=int, help='size X (default: %(default)s)')
    parser.add_argument('-y', metavar='Y', default=_size[1], type=int, help='size Y (default: %(default)s)')
    parser.add_argument('-z', metavar='Z', default=_size[2], type=int, help='size Z (default: %(default)s)')
    parser.add_argument('-l', '--lines', metavar='N', default=nlines, type=int, help='max number of lines (default: %(default)s)')
    parser.add_argument('-r', '--retry', metavar='N', default=retry, type=int, help='max number of retry (default: %(default)s)')
    parser.add_argument('-o', '--output', metavar='FILE', help='output file')
    #parser.add_argument('--test1', action='store_true', help='run test1')
    args = parser.parse_args()
    debug = args.debug
    verbose = args.verbose
    #if args.test1: test1()
    run(args.x, args.y, args.z, num_lines=args.lines, basename=args.output, max_retry=args.retry)
    
    
if __name__ == "__main__":
    main()
