#!/usr/bin/env perl
#
# $Rev: $
#
# Excelファイル(.xls|.xlsx)で作成したパズルの問題データを、
# ソルバー用のテキストデータ形式へ、変換して、出力する。
# アルゴリズムデザインコンテスト(ADC)形式も出力する。
# 複数のワークシートが存在してもよい。
#
# usage: ./nlconv.pl INPUTFILE.xls ...
#
#
#
# Copyright (c) 2014,2015,2016 dasadc, Fujitsu
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#


use strict;
use warnings;
use utf8;
use Spreadsheet::ParseExcel;
use Spreadsheet::XLSX;
use Encode qw(encode decode);

use FindBin;
use lib "$FindBin::Bin";
use File::Basename;

require 'get_ban_size.pl';
require 'print_ban.pl';
require 'print_ban_adc.pl';

#binmode(STDOUT, ":utf8"); # UTF-8の文字列をprintするため

sub find_via {
    my ($vias, $x, $y, $layer) = @_;
    for my $via (sort keys %$vias) {
	if ( $vias->{$via}->{x} == $x &&
	     $vias->{$via}->{y} == $y &&
	     $vias->{$via}->{z} == $layer ) {
	    return $via;
	}
    }
    return "";
}

# リンク途中の余計な数字を消して、リンクの端点のみを残す
sub clear_number {
    my ($ban) = @_;

    my @tmp = @{$ban};
    my $xmax = $#tmp;
    my @tmp2 = @{$ban->[0]};
    my $ymax = $#tmp2;
    #print "clear_number: xmax = $xmax, ymax=$ymax\n";
    #print_ban( $ban, \*STDOUT );

    # まずは、消す候補を数え上げる
    my $clear = ();
    for ( my $y = 0; $y <= $ymax; $y ++ ) {
	for ( my $x = 0; $x <= $xmax; $x ++ ) {
	    my $num = $ban->[$x][$y];
	    if ( $num eq "-" || $num eq " " ) {
		next;
	    }

	    # 四方に隣接するマスと、一致する個数が２以上なら、消してよい？
	    my $count = 0;
	    #上のマスと同じ値か？ …文字列比較で？？ 数値, " ", "-"
	    if ( 0 <= $y-1 && $ban->[$x][$y-1] eq $num ) {
		$count = $count + 1;
	    }
	    #左のマスと同じ値か？
	    if ( 0 <= $x-1 && $ban->[$x-1][$y] eq $num ) {
		$count = $count + 1;
	    }
	    #下のマスと同じ値か？ 
	    if ( $y+1 <= $ymax && $ban->[$x][$y+1] eq $num ) {
		$count = $count + 1;
	    }
	    #右のマスと同じ値か？
	    if ( $x+1 <= $xmax && $ban->[$x+1][$y] eq $num ) {
		$count = $count + 1;
	    }
	    if ( 2 <= $count ) {
		$clear->[$x][$y] = 1; # 消す
	    } else {
		$clear->[$x][$y] = 0; # 消さない
	    }
	    #print "$x $y  $count\n";
	}
    }
    #print "clear=\n"; print_ban( $clear, \*STDOUT ); # \*って何だ？

    #本当に消す
    for ( my $y = 0; $y <= $ymax; $y ++ ) {
	for ( my $x = 0; $x <= $xmax; $x ++ ) {
	    if (defined $clear->[$x][$y]) {
		if ( $clear->[$x][$y] == 1 ) {
		    $ban->[$x][$y] = " ";
		}
	    }
	}
    }
    #print_ban( $ban );
}

# 番号を数え上げる
sub enumerate_numbers {
    my ($ban, $xmax, $ymax) = @_;
    #print "3: ban=" . $ban . "\n";
    my %numbers = ();
    my @pos0 = ();
    my @pos1 = ();
    my $maxNum = -1;
    for ( my $y = 0; $y <= $ymax; $y ++ ) {
	for ( my $x = 0; $x <= $xmax; $x ++ ) {
	    if ( defined $ban->[$x][$y] &&
		 $ban->[$x][$y] =~ /^\d+$/ ) {
		my $num = $ban->[$x][$y];
		if ($num == 0) {
		    next;
		}
		if ( $maxNum <= $num ) { $maxNum = $num; }
		if ( !defined $numbers{$num} ) {
		    $numbers{$num} = 0;
		    $pos0[$num] = sprintf("(%d,%d)", $x,$y);
		}
		if ( $numbers{$num} == 1 ) {
		    $pos1[$num] = sprintf("(%d,%d)", $x,$y);
		}
		if ( $numbers{$num} >= 2 ) {
		    printf("ERROR: duplicated number %d (%d)\n",
			   $num, $numbers{$num}+1);
		}
		$numbers{$num} ++;
	    }
	}
    }
    return { numbers => \%numbers, pos0 => \@pos0, pos1 => \@pos1, maxNum => $maxNum};
}

# ADC形式の出題ファイルを書き出す
sub print_Q_adc {
    my ( $ban, $fp ) = @_;

    #print "2: ban=" . $ban . "\n";
    my ($xmax, $ymax) = get_ban_size( $ban );
    print $fp sprintf("SIZE %dX%d\r\n", $xmax+1, $ymax+1);

    # 番号を数え上げる
    my $en = enumerate_numbers($ban, $xmax, $ymax);
    my %numbers = %{$en->{numbers}};
    my @pos0    = @{$en->{pos0}};
    my @pos1    = @{$en->{pos1}};
    my $maxNum  = $en->{maxNum};

    # 出力する
    print $fp sprintf("LINE_NUM %d\r\n", $maxNum);
    for ( my $i = 1; $i <= $maxNum; $i ++ ) { # 1から始まる
	if ( !defined $numbers{$i} ) {
	    print $fp sprintf("ERROR: cannot find number %d\n", $i);
	    printf("ERROR: cannot find number %d\n", $i);
	} else {
	    if ( !defined $pos1[$i] ) {
		printf("ERROR: cannot find second number %d\n", $i);
	    }
	    print $fp sprintf("LINE#%d %s-%s\r\n", $i, $pos0[$i], $pos1[$i]);
	}
    }
}

# 2016年版 問題データ出力
sub print_Q_adc2016 {
    my ( $data, $fp ) = @_;
    my @tmp = @{$data};
    my $nlayers = $#tmp;
    my ($xmax0, $ymax0);
    my $maxNum = 0;
    my @enum_num = ();
    for ( my $i = 1; $i <= $nlayers; $i ++ ) {
	my $ban  = $data->[$i]->{ban};
	my ($xmax, $ymax) = get_ban_size( $ban );
	clear_number( $ban ); # 2回以上実行しても問題ない
	if ( $i == 1 ) {
	    $xmax0 = $xmax;
	    $ymax0 = $ymax;
	} else {
	    # 盤面サイズが一致していることを確認
	    if ($xmax0 != $xmax || $ymax0 != $ymax) {
		printf("ERROR: ban size must be same: %dX%d != %dX%d\n",
		       $xmax0+1, $ymax0+1, $xmax+1, $ymax+1);
	    }
	}
	# 番号を数え上げる
	my $en = enumerate_numbers($ban, $xmax, $ymax);
	if ($maxNum < $en->{maxNum}) { $maxNum = $en->{maxNum}; }
	$enum_num[$i] = $en;
    }
    my @numbers0 = ();
    my @lines = ();
    my @endpoints = ();
    my %viaList = ();
    print $fp sprintf("SIZE %dX%dX%d\r\n", $xmax0+1, $ymax0+1, $nlayers);
    print $fp sprintf("LINE_NUM %d\r\n", $maxNum);
    for ( my $layer = 1; $layer <= $nlayers; $layer ++ ) {
	my $en = $enum_num[$layer];
	my %numbers = %{$en->{numbers}};
	my @pos0    = @{$en->{pos0}};
	my @pos1    = @{$en->{pos1}};
	for ( my $line = 1; $line <= $maxNum; $line ++ ) {
	    if (defined $numbers{$line}) {
		if (defined $numbers0[$line]) {
		    $numbers0[$line] += $numbers{$line};
		} else {
		    $numbers0[$line] = $numbers{$line};
		}
	    }
	    if (defined $pos0[$line]) {
		if (!defined $pos1[$line]) {
		    printf("ERROR: cannot find second number of LINE %d\n", $line);
		    continue;
		}
		my ($x0, $y0, $x1, $y1);
		if ($pos0[$line] =~ /\((\d+),(\d+)\)/ ) {
		    ($x0, $y0) = ($1, $2);
		} else {
		    printf("BUG: format error: LINE %d pos0=%s\n", $line, $pos0[$line]);
		    continue;
		}
		if ($pos1[$line] =~ /\((\d+),(\d+)\)/ ) {
		    ($x1, $y1) = ($1, $2);
		} else {
		    printf("BUG: format error: LINE %d pos1=%s\n", $line, $pos1[$line]);
		    continue;
		}
		my $via0 = find_via($data->[$layer]->{via}, $x0, $y0, $layer);
		my $via1 = find_via($data->[$layer]->{via}, $x1, $y1, $layer);
		if ($via0 eq "") {
		    if (!defined $lines[$line]) { $lines[$line] = {}; }
		    if (defined($lines[$line]->{pos0})) {
			if(defined($lines[$line]->{pos1})) {
			    # 複数のlayerで、個別に、同じ番号の線が引かれているとき
			    printf("ERROR: too many number %d: %s and (%d,%d,%d)\n", $line, $lines[$line]->{pos0}, $x0, $y0, $layer);
			} else {
			    # pos0がすでに決まっていたので、pos1に登録
			    $lines[$line]->{pos1} = sprintf("(%d,%d,%d)", $x0, $y0, $layer);
			}
		    } else {
			$lines[$line]->{pos0} = sprintf("(%d,%d,%d)", $x0, $y0, $layer);
		    }
		} else {
		    #printf("VIA0 (%d,%d,%d) for LINE#%d\n", $x0, $y0, $layer, $line);
		    if (!defined $viaList{$via0}) { $viaList{$via0} = ""; }
		    $viaList{$via0} .= sprintf(" (%d,%d,%d)", $x0, $y0, $layer);
		}
		if ($via1 eq "") {
		    if (!defined $lines[$line]) { $lines[$line] = {}; }
		    if (defined($lines[$line]->{pos1})) {
			if (defined($lines[$line]->{pos0})) {
			    # 複数のlayerで、個別に、同じ番号の線が引かれているとき
			    printf("ERROR: too many number %d: %s and (%d,%d,%d)\n", $line, $lines[$line]->{pos1}, $x1, $y1, $layer);
			} else {
			    # pos1がすでに決まっていたので、pos0に登録
			    $lines[$line]->{pos0} = sprintf("(%d,%d,%d)", $x1, $y1, $layer);
			}
		    } else {
			$lines[$line]->{pos1} = sprintf("(%d,%d,%d)", $x1, $y1, $layer);
		    }
		} else {
		    #printf("VIA1 (%d,%d,%d) for LINE#%d\n", $x1, $y1, $layer, $line);
		    if (!defined $viaList{$via1}) { $viaList{$via1} = (); }
		    #push $viaList{$via1}, sprintf("%d,%d,%d", $x1, $y1, $layer);
		    $viaList{$via1} .= sprintf(" (%d,%d,%d)", $x1, $y1, $layer);
		}
		#printf("LINE %d (%d,%d,%d)-(%d,%d,%d) \n", $line, $x0, $y0, $layer, $x1, $y1, $layer);
	    }
	}
    }
    for ( my $line = 1; $line <= $maxNum; $line ++ ) {
	if (defined $numbers0[$line]) {
	    #printf("numbers0[%d] = %d\n", $line, $numbers0[$line]);
	    print $fp sprintf("LINE#%d %s %s\r\n", $line, $lines[$line]->{pos0}, $lines[$line]->{pos1});
	} else {
	    print $fp sprintf("ERROR: cannot find number %d\r\n", $line);
	    printf("ERROR: cannot find number %d\n", $line);
	}
    }
    foreach my $viaName (sort keys %viaList) {
	print $fp sprintf("VIA#%s%s\r\n", $viaName, $viaList{$viaName});
    }
}

# ワークシート、1枚を読み込む
sub read_sheet1 {
    my ($worksheet) = @_;
    my $ban = ();
    my ( $row_min, $row_max ) = $worksheet->row_range();
    my ( $col_min, $col_max ) = $worksheet->col_range();
    #print "row_min=$row_min, col_min=$col_min\n";
    #print "row_max=$row_max, col_max=$col_max\n";
    
    for my $row ( $row_min .. $row_max ) {
	for my $col ( $col_min .. $col_max ) {
	    
	    my $cell = $worksheet->get_cell( $row, $col );
	    next unless $cell;
	    my $cell_in = $cell->value();
	    
	    #print "[$row][$col] : $cell_in", "\n";
	    $ban->[$col][$row] = $cell_in;
	}
    }
    return $ban;
}

sub dump_vias {
    my ($vias) = @_;
    for my $via (sort keys %$vias) {
	printf("%s (%d,%d,%d)\n",
	       $via,
	       $vias->{$via}->{x},
	       $vias->{$via}->{y},
	       $vias->{$via}->{z});
    }
}

# viaの(X,Y)座標が一致するかチェックする。
# 中間のLAYERでviaが置かれているかチェックする。
# viaだけがあって、数字マスと接続していない場合は…？  別のチェック条件で検出されるはず
sub check_via {
    my ($data) = @_;
    my @tmp = @{$data};
    my $nlayers = $#tmp;
    my %found_name = ();
    my %found_xyz = ();
    my $err = 0;
    for ( my $i = 1; $i <= $nlayers; $i ++ ) {
	my $vias = $data->[$i]->{via};
	for my $via (sort keys %$vias) {
	    my $x = $vias->{$via}->{x};
	    my $y = $vias->{$via}->{y};
	    my $z = $vias->{$via}->{z};
	    my $xy  = sprintf("x=%d,y=%d", $x, $y);
	    my $xyz = sprintf("x=%d,y=%d,z=%d", $x, $y, $z);
	    # (X,Y)座標が一致すること
	    if ( defined($found_name{$via}) ) {
		if ( $found_name{$via} eq $xy ) {
		    # (X,Y)が一致したのでOK
		} else {
		    printf("ERROR: VIA#%s X,Y mismatch: %s and %s",
			   $via, $found_name{$via}, $xy);
		    $err ++;
		}
	    } else {
		# 初登場
		$found_name{$via} = $xy;
	    }
	    # 中間のLAYERでviaが置かれていること
	    if ( defined($found_xyz{$xyz}) ) {
		if ( $found_xyz{$xyz} == $i-1 ) { # layerが連続している
		    # ok
		} else {
		    printf("ERROR: VIA#%s(%d,%d,%d) is missing\n",
			   $via, $x, $y, $i-1);
		    $err ++;
		}
	    } else {
		# 初登場
		$found_xyz{$xyz} = $i;
	    }
	}
    }
    return $err;
}

sub get_ban_data {
    my ($ban, $nrows, $ncols, $layer) = @_;
    my $xmax = 1 + $ncols - 1;  # 盤のデータは第1列から始まる(列0からスタート)
    my $ymax = 3 + $nrows - 1;  # 盤のデータは第3行から始まる(行0からスタート)
    #print "xmax=$xmax, ymax=$ymax\n";
    #print_ban_OLD( $ban );
    my $ban2 = [];
    my $vias = {};
    # 第2行は列の番号
    # 第3行からデータ
    for ( my $y = 3; $y <= $ymax; $y ++ ) {
	# 第0列は行の番号
	# 第1列からデータ
	for ( my $x = 1; $x <= $xmax; $x ++ ) {
	    my $val = $ban->[$x][$y];
	    if ( defined $val ) {
		$val =~ s/ //g; # 余分なスペースを削除
		my @tmp = split(/=/, $val);
		if ($#tmp == 1) {
		    $vias->{$tmp[0]} = {x => ($x-1), y => ($y-3), z => $layer};
		    $val = $tmp[1];
		}
		$ban2->[$x-1][$y-3] = $val;
	    } else {
		$ban2->[$x-1][$y-3] = '-';
	    }
	}
    }
    return ($ban2, $vias);
}

sub is_completed {
    my ($multiData, $worksheetbase, $nlayers) = @_;
    my $complete = 0;
    for ( my $i = 1; $i <= $nlayers; $i ++ ) {
	if (defined($multiData->{$worksheetbase}->[$i])) {
	    $complete ++;
	}
    }
    #print "is_completed: $worksheetbase, nlayers=$nlayers compete=$complete\n";
    return ($complete == $nlayers);
}

sub write_file {
    my ($multiData, $basefile, $worksheetbase, $dataA) = @_;
    my @tmp = @{$multiData->{$worksheetbase}};
    my $nlayers = $#tmp;
    #print "nlayers=$nlayers\n";
    #print "1:" . $multiData->{$worksheetbase}->[1] . "\n";
    my $ban  = $multiData->{$worksheetbase}->[1]->{ban};
    my $via  = $multiData->{$worksheetbase}->[1]->{via};
    my $data = $multiData->{$worksheetbase};

    if ( $dataA != 0 ) {
	# 解答ファイルを作る(ソルバで解けなかったとき用)
	my $sfilename = sprintf("%s_%s_adc_sol.txt", $basefile, $worksheetbase);
	open( my $fp0, ">$sfilename") || die "ERROR: open $sfilename";
	if ( $nlayers == 1 ) {
	    print_ban_adc( $ban, 1, $fp0 );
	} else {
	    print_ban_adc2016( $data, $fp0 );
	}
	close $fp0
    }
    # 線を消して、端点のみを残す
    clear_number( $ban );

    my $ofilename = sprintf("%s_%s.txt", $basefile, $worksheetbase);
    print $ofilename . "\n";
    open( my $fp, ">$ofilename") || die "ERROR: open $ofilename";
    if ( $nlayers == 1 ) {
	print_ban( $ban, $fp );
    } else {
	print_ban2016( $data, $fp );
    }
    close $fp;

    $ofilename = sprintf("%s_%s.csv", $basefile, $worksheetbase);
    print $ofilename . "\n";
    open( my $fp1, ">$ofilename") || die "ERROR: open $ofilename";
    if ( $nlayers == 1 ) {
	#print_ban_csv( $ban, $fp1 );
	#print "1: ban=" . $ban . "\n";
	print_ban( $ban, $fp1, 1 );
    } else {
	print_ban2016( $data, $fp1, 1);
    }
    close $fp1;

    my $ofilename_adc = sprintf("%s_%s_adc.txt", $basefile, $worksheetbase);
    print $ofilename_adc . "\n";
    open( my $fp2, ">$ofilename_adc") || die "ERROR: open $ofilename_adc";
    if ( $nlayers == 1 ) {
	print_Q_adc( $ban, $fp2 );
    } else {
	print_Q_adc2016( $data, $fp2 );
    }
    close $fp2;
}

sub proc1_sheet {
    my ($basefile, $worksheet, $multiData) = @_;
    my $worksheetname = $worksheet->get_name();
    my $worksheetbase = $worksheetname;
    my $dataA = 0; # Aファイル（回答データ）を生成するか？ セルC1にAと書く
    my $ban = read_sheet1($worksheet);
    my $nrows   = $ban->[0][0]; # 行数  "0000","行"  セルA1
    my $ncols   = $ban->[0][1]; # 列数  "0000","列"  セルA2
    my $layer   = $ban->[3][0]; # 層の番号           セルD1
    my $nlayers = $ban->[5][0]; # 層数               セルF1
    if ( !(defined($nrows) && defined($ncols)) ) {
	next;
    }
    if (defined($layer) && defined($nlayers)) {
	my @tmp = split(/\./, $worksheetname); # '.'で分割
	if ($#tmp != 1) {
	    printf("ERROR: check worksheet name format: worksheet name=%s\n",
		   $worksheetname);
	    return -1;
	}
	$worksheetbase = $tmp[0];
	if ($tmp[1] != $layer) {
	    printf("ERROR: check layer numer: worksheet name=%s, layer=%d\n",
		   $worksheetname, $layer);
	    return -1;
	}
	if ( $layer <= 0 || $nlayers < $layer ) {
	    printf("ERROR: layer %d is out of range\n", $layer);
	    return -1;
	}
    } elsif (defined($layer) && !defined($nlayers)) {
	printf("ERROR: missing number of layer. check cell F1\n");
	return -1;
    } elsif (!defined($layer) && defined($nlayers)) {
	printf("ERROR: missing layer. check cell D1\n");
	return -1;
    } else {
	$layer = 1;
	$nlayers = 1;
    }
    if ( $nrows <= 0 || $ncols <= 0 ) {
	print "SKIP: sheet $worksheetname\n";
	next;
    }
    #print "nrows=$nrows, ncols=$ncols\n";
    if (defined($ban->[2][0]) && $ban->[2][0] eq 'A') { # セルC1
	$dataA = 1;
    }
    my ($ban2, $vias) = get_ban_data( $ban, $nrows, $ncols, $layer);
    #print_ban( $ban2, \*STDOUT );
    #dump_vias($vias);
    $multiData->{$worksheetbase}->[$layer] = { ban => $ban2, via => $vias };
    my $complete = is_completed($multiData, $worksheetbase, $nlayers);
    
    if ( $complete ) {
	check_via($multiData->{$worksheetbase});
	write_file($multiData, $basefile, $worksheetbase, $dataA);
    }
}

sub proc1 {
    my ($input_file) = @_;
    my $basefile;
    my $workbook;
    my $xlsx = 0;

    if ( $input_file =~ /.xls$/i ) {
	$basefile = basename($input_file, ".xls");
	my $parser   = Spreadsheet::ParseExcel->new();
	$workbook = $parser->parse($input_file);
    } elsif ( $input_file =~ /.xlsx$/i ) {
	$basefile = basename($input_file, ".xlsx");
	$workbook   = Spreadsheet::XLSX->new($input_file);
	$xlsx = 1;
    } else {
	die "ERROR: cannot parse $input_file";
    }

    my $multiData = {};
    for my $worksheet ( $workbook->worksheets() ) {
	proc1_sheet( $basefile, $worksheet, $multiData );
    }
}

#-----------------------------------------------------------------------

for ( my $i = 0; $i <= $#ARGV; $i ++ ) {
    my $input_file = $ARGV[$i];
    print "input_file = $input_file\n";
    proc1( $input_file );
}
