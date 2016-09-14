#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# 2016年版ルールの問題を、2015年版ルールに変換して、解く。
# VIAを、線の番号に割り振る、すべての組み合わせを、数え上げている。
#
# solver2016.py -p sample_Q4 --convert sample_Q4_adc.txt

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'server'))
from nlcheck import NLCheck
import cPickle as pickle
import numpy as np
import csv

debug = False
project_dir = "./solver_project"
info = {}
solver_cmd = 'solve6'

def info_file():
    return os.path.join(project_dir, 'info.pickle')

def read_info():
    global info
    f  = info_file()
    if os.path.exists(f):
        with open(f, 'r') as fp:
            info = pickle.load(fp)
    
def write_info():
    global info
    f  = info_file()
    with open(f, 'w') as fp:
        pickle.dump(info, fp)

def show_info():
    global info
    def show_candidates(candidates):
        for idx, c in enumerate(candidates):
            print '  [%d]' % idx, c
    def show_output_info(output_info):
        for idx, info2 in enumerate(output_info):
            print '  [%d]' % idx
            #print info2
            if info2 is None: continue
            for key, val in sorted(info2.items()):
                print '    [%s] ' % key, val
    def show_qs(qs):
        for idx, iqs in enumerate(qs):
            print '  [%d]' % idx
            for key, val in sorted(iqs.items()):
                print '    [%s] ' % key, val
        pass
    for key,val in sorted(info.items()):
        print '[%s]' % key
        if key == 'output_info':
            show_output_info(val)
        elif key == 'candidates':
            show_candidates(val)
        elif key == 'qs':
            show_qs(val)
        else:
            print val
        
def next_list(now, val):
    "リストnowから、valを除いたリストを返す"
    nl = []
    for i in now:
        if i != val: nl.append(i)
    return nl

def assign_via_line(vias, path, candidates):
    "VIAをLINEに割り当てる"
    if len(vias) == 0:
        #print path
        candidates.append(path)
    else:
        for via in vias:
            vias2 = next_list(vias, via)
            path2 = list(path)
            path2.append(via)
            #print "vias2=", vias2
            #print "path2=", path2
            assign_via_line(vias2, path2, candidates) # 再帰呼び出し

def get_via_pos(via_mat, layer_num, viaidx, via, layer):
    for la0 in range(0, layer_num):
        viapos = via_mat[viaidx-1][la0*3:la0*3+3]
        #print "get_via_pos", viapos
        if viapos[2] == layer:
            return viapos
    print "Error: via#%s not found in Layer#%d" % (via, layer)
    return [0,0,0]

def output_q(global_linevia, org_line_num, qs, vias, via_mat, via_dic, qfile, idx):
    global project_dir
    #linevia = qs[0]['linevia'] # 全layerで同じ ★じゃない!
    linevia = global_linevia
    layer_num = len(qs)
    via_num = len(vias)
    output_info = {}
    if debug: print "(%5d)" % idx, vias, linevia
    for layer in range(1,layer_num+1):
        new_line_num = qs[layer-1]['LINE_NUM']
        buf  = 'SIZE %dX%d\r\n' % qs[layer-1]['SIZE']
        buf += 'LINE_NUM %d\r\n' % new_line_num
        map_line_num = [-1] * (1+new_line_num) # (新しい線の番号) → (元の線の番号)
        map_line_num[0] = 0 # 空白マス
        line_pos = [None]*(1+org_line_num) # (線の番号) → (座標)
        for i, via in enumerate(vias):
            line_num = linevia[i]
            viaidx = via_dic[via]
            #viapos = via_mat[viaidx-1][(layer-1)*3:(layer-1)*3+3] # これ正しくない。via_matは、layer番号の位置にデータを格納しているわけではない。
            viapos = get_via_pos(via_mat, layer_num, viaidx, via, layer)
            if debug: print "Layer#%d LINE#%d VIA#%s " % (layer, line_num, via), viapos
            line_pos[line_num] = (viapos[0], viapos[1])
        #print "line_pos=", line_pos
        for i, line in enumerate(qs[layer-1]['LINE']):
            line_num = line['LINE#']
            x0, y0 = line['pos0']
            line_renumbered = i + 1
            map_line_num[line_renumbered] = line_num
            if line['pos1'] is None:
                x1,y1 = line_pos[line_num]
            else:
                x1,y1 = line['pos1']
            buf += 'LINE#%d (%d,%d)-(%d,%d)\r\n' % (line_renumbered, x0,y0, x1,y1)
        ofile = os.path.splitext(os.path.basename(qfile))[0] + ('.%d.L%d.txt' % (idx, layer))
        ofile2 = os.path.join(project_dir, ofile)
        #print ofile2
        #print buf, "map_line_num=", map_line_num
        with open(ofile2, 'w') as f:
            f.write(buf)
        output_info['L'+str(layer)] = {'map_line_num': map_line_num,
                                       'ofile': ofile}
    return output_info

def read_candidates_csv(candidates_csv):
    "candidatesを、CSVファイルから読み込む。assign_via_line()では、組み合わせ爆発するため。"
    candidates = []
    with open(candidates_csv, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            candidates.append(row)
    print candidates
    return candidates

def convert(qfile, candidates=None):
    "2016年版ルールの問題ファイルを、変換する"
    o = NLCheck()
    res = o.read_input_file(qfile)
    if debug:
        label = ['size', 'line_num', 'line_mat', 'via_mat', 'via_dic']
        for i in range(0,5):
            print label[i], '=\n', res[i]

    size, org_line_num, line_mat, via_mat, via_dic = res
    layer_num = size[2]
    qs = []
    found_linevia = {}
    for layer in range(1,layer_num+1):
        line_num1 = 0
        line_num2 = 0
        lineinfo = []
        linevia = []  # このlayerで、線とviaがつながっている
        for line in line_mat:
            line_num1 += 1
            if line[2] == line[5] and line[2] == layer:
                # 1つのレイヤー内で完結している線
                line_num2 += 1
                lineinfo.append({'LINE#': line_num1,
                                 'pos0':  (line[0], line[1]),
                                 'pos1':  (line[3], line[4])})
            elif line[2] == layer:
                line_num2 += 1
                lineinfo.append({'LINE#': line_num1,
                                 'pos0':  (line[0], line[1]),
                                 'pos1':  None})
                linevia.append(line_num1)
                found_linevia[line_num1] = True
            elif line[5] == layer:
                line_num2 += 1
                lineinfo.append({'LINE#': line_num1,
                                 'pos0':  (line[3], line[4]),
                                 'pos1':  None})
                linevia.append(line_num1)
                found_linevia[line_num1] = True
        qs.append({'SIZE': (size[0], size[1]),
                   'LINE_NUM': line_num2,
                   'LINE': lineinfo,
                   'linevia': linevia})

    #print qs
    #print "qs[0]['LINE']=\n", qs[0]['LINE']
    #print "qs[1]['LINE']=\n", qs[1]['LINE']
    global_linevia = sorted(found_linevia)
    if debug: print "global_linevia=", global_linevia

    # エラーチェック: すべてのlayerで、lineviaは一致する ★それは2層の場合だけ
    #for layer in range(1, layer_num):
    #    #print "qs[%d]['linevia']=" % (layer-1), qs[layer-1]['linevia']
    #    #print "qs[%d]['linevia']=" % (layer), qs[layer]['linevia']
    #    if qs[layer-1]['linevia'] != qs[layer]['linevia']:
    #        print "Error in via: layer %d and %d" % (layer, layer+1)
    #    if len(via_dic) != len(qs[layer-1]['linevia']):
    #        print "Error in number of via: layer %d" % layer
    # ★3層以上の場合を考慮
    # エラーチェック: 数字マスはviaを経由してつながっている
    # ＝ 対となるlineviaがあるはず
    # ＝ 2回ずつ出現するはず 
    count_linevia = {}
    for layer in range(1, layer_num+1):
        for n in qs[layer-1]['linevia']:
            if n in count_linevia:
                count_linevia[n] += 1
            else:
                count_linevia[n] =  1
    if debug: print "count_linevia=", count_linevia
    for n in global_linevia:
        if count_linevia[n] != 2:
            print "Error: please check connection between line#%d and via"

    vias = sorted(via_dic.keys())
    if candidates is None:
        candidates = []
        assign_via_line(vias, [], candidates)

    info['size'] = size  # layer_numは、size[2]
    info['org_line_num'] = org_line_num
    info['line_mat'] = line_mat
    info['via_mat'] = via_mat
    info['via_dic'] = via_dic
    info['qs'] = qs
    info['vias'] = vias
    info['global_linevia'] = global_linevia
    info['candidates'] = candidates
    info['output_info'] = [None]*(1+len(candidates))
    idx = 0
    for c in candidates:
        info['output_info'][idx] = output_q(global_linevia, org_line_num, qs, c, via_mat, via_dic, qfile, idx)
        idx += 1


def exec_solver(qfile):
    global solver_cmd
    # afile: 回答ファイルのファイル名。solver_cmdにて決めうちされている
    root, ext = os.path.splitext(os.path.basename(qfile))
    afile = root + '.A.txt'
    cmd = "%s %s" % (solver_cmd, qfile)
    print cmd
    os.system(cmd)
    return afile

def best_target(judges):
    best = None
    qfactor = -1
    for i,j in enumerate(judges):
        if j[0]:
            if qfactor < j[1]:
                qfactor = j[1]
                best = i
    return best, qfactor

def get_via_linenum_mat(info, layer, via_to_line):
    "viaの座標を、強制上書きするためのデータ。viaが貫通するlayerでは、線がなかったことにされているので、この上書き処理が必要になる。"
    via_linenum = np.zeros((info['size'][1], info['size'][0]), dtype=np.integer)
    via_mat = info['via_mat']
    for y in range(0, via_mat.shape[0]):
        for x in range(0, via_mat.shape[1]/3):
            viax,viay,viaz = via_mat[y][x*3:x*3+3]
            if (viax,viay,viaz) == (0,0,0): break
            #print "get_via_linenum_mat: (%d,%d) (%d, %d, %d)" % (x,y, viax,viay,viaz)
            if viaz == layer:
                via_name = info['vias'][y]
                via_linenum[viay,viax] = via_to_line[via_name]
                #print "via_name =", via_name
    #print "layer=%d, via_linenum=\n" % layer, via_linenum
    return via_linenum

def generate_A_data(ai, map_line_num, via_linenum):
    "回答データを、ADC形式に変換する。"
    #print "generate_A_data: ai=\n", ai, "ai.shape=", ai.shape
    zz,yy,xx = ai.shape
    out = ''
    map_line_num[0] = 0 # たぶんOK
    for y in range(0, yy):
        for x in range(0, xx):
            if via_linenum[y,x] != 0:
                num = via_linenum[y,x] # via位置に、線番号を上書き
            else:
                num = map_line_num[ai[0,y,x]]
            out += "%02d" % num
            if x == xx-1:
                out += "\r\n"
            else:
                out += ","
    #print "generate_A_data: out=\n", out
    return out

def get_via_to_line(info, num):
    "viaの名前 → 線の番号"
    candidate = info['candidates'][num]
    global_linevia = info['global_linevia']
    via_to_line = {}
    for i,via in enumerate(candidate):
        via_to_line[via] = global_linevia[i]
    return via_to_line

def solve(num):
    global project_dir
    o = NLCheck()
    output_info = info['output_info'][num]
    via_to_line = get_via_to_line(info, num)
    adata = 'SIZE %dX%dX%d\r\n' % info['size']
    fail = False
    cwd = os.getcwd()
    #---------------------------------------
    os.chdir(project_dir)
    for layer, info2 in sorted(output_info.items()):
        if layer[0]!='L' or not layer[1:].isdigit():
            continue
        qfile = info2['ofile']
        afile = exec_solver(qfile)
        #print layer, qfile, afile
        input_data = o.read_input_file(qfile)
        target_data = o.read_target_file(afile)
        target_data2 = o.clean_a(input_data, target_data)
        judges = o.check(input_data, target_data2)
        best = best_target(judges)
        print "judges = ", judges
        print "best = ", best
        #print "best target_data = ", target_data2[best[0]]
        ilayer = int(layer[1:]) # 1,2,…
        via_linenum = get_via_linenum_mat(info, ilayer, via_to_line)
        adata += 'LAYER %d\r\n' % ilayer
        if best[0] is None:
            fail = True
            break
        else:
            bd = target_data2[best[0]]
            adata += generate_A_data(bd, info2['map_line_num'], via_linenum)
            if 0:
                root, ext = os.path.splitext(afile)
                gfile = root + '.gif'
                gif = o.graphic_gif(input_data, [bd], gfile)
                print "gif = ", gif
    os.chdir(cwd)
    #---------------------------------------
    if fail:
        output_info['judges'] = None
        return None
    else:
        # afile: 2016年版ルールの回答ファイルの名前
        root, ext = os.path.splitext(os.path.basename(info['convert_q']))
        afile = root + ('.%d.A.txt' % num)
        afile2 = os.path.join(project_dir, afile)
        with open(afile2, 'w') as fp:
            fp.write(adata)
        # 2016年版ルールで回答チェック
        input_data = o.read_input_file(info['convert_q'])
        target_data = o.read_target_str(adata)
        judges = o.check(input_data, target_data)
        print "afile = ", afile
        print "judges = ", judges
        output_info['afile'] = afile
        output_info['judges'] = judges
        if judges[0][0]:
            # 正解が出た
            gfile = root + ('.%d.A.gif' % num)
            gfile2 = os.path.join(project_dir, gfile)
            gif = o.graphic_gif(input_data, target_data, gfile2)
            print "gif = ", gif
            
        return afile
    
def usage():
    print "usage:", os.path.basename(sys.argv[0]), "[options]",
    print """
options:
  -h|--help
  -d|--debug
  -i|--info
  -c|--convert=QFILE.txt
  -C|--candidates=FILE.csv
  -s|--solve=NUMBER
  -p|--project-dir=DIR  (default: %s)
""" % (project_dir)

def main():
    global debug
    global project_dir
    global info
    import getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hdic:C:s:p:", ["help","debug","info","convert=","candidates=","solve=","project-dir="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    convert_q = None
    candidates_csv = None
    candidates = None
    solve_num = None
    showinfo = False
    for o,a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(1)
        elif o in ("-d", "--debug"):
            debug = True
        elif o in ("-i", "--info"):
            showinfo = True
        elif o in ("-c", "--convert"):
            if os.path.exists(a):
                convert_q = a
            else:
                print "Error: file not found:", a
        elif o in ("-C", "--candidates"):
            if os.path.exists(a):
                candidates_csv = a
            else:
                print "Error: file not found:", a
        elif o in ("-s", "--solve"):
            solve_num = int(a)
        elif o in ("-p", "--project-dir"):
            project_dir = a
        else:
            print "Error: unknown option", o
    read_info()
    if showinfo:
        show_info()
    if not os.path.isdir(project_dir):
        os.mkdir(project_dir)
    if candidates_csv is not None:
        candidates = read_candidates_csv(candidates_csv)
    if convert_q is not None:
        info['cwd'] = os.getcwd()
        info['convert_q'] = convert_q
        info['candidates_csv'] = candidates_csv
        convert(convert_q, candidates)
    if solve_num is not None:
        solve(solve_num)
    write_info()
        
if __name__ == '__main__':
    main()

    

# Local Variables:
# mode: python
# coding: utf-8    
# End:             
