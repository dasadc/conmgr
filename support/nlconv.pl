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
# Copyright (c) 2014,2015 dasadc, Fujitsu
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

require 'print_ban.pl';
require 'print_ban_adc.pl';

#binmode(STDOUT, ":utf8"); # UTF-8の文字列をprintするため





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

# ADC形式の出題ファイルを書き出す
sub print_Q_adc {
    my ( $ban, $fp ) = @_;

    my ($xmax, $ymax) = get_ban_size( $ban );
    print $fp sprintf("SIZE %dX%d\r\n", $xmax+1, $ymax+1);

    # 番号を数え上げる
    my %numbers = ();
    my @pos0 = ();
    my @pos1 = ();
    my $maxNum = -1;
    for ( my $y = 0; $y <= $ymax; $y ++ ) {
	for ( my $x = 0; $x <= $xmax; $x ++ ) {
	    if ( defined $ban->[$x][$y] &&
		 $ban->[$x][$y] =~ /^\d+$/ ) {
		my $num = $ban->[$x][$y];
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

    for my $worksheet ( $workbook->worksheets() ) {
	
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

	# ワークシート、1枚を読み込み終わったところ。
	if ( !(defined($ban->[0][0]) && defined($ban->[0][1])) ) {
	    next;
	}
	my $nrows = $ban->[0][0]; # 行数  "0000","行"
	my $ncols = $ban->[0][1]; # 列数  "0000","列"
	#print "nrows=$nrows, ncols=$ncols\n";

	my $xmax = 1 + $ncols - 1;
	my $ymax = 3 + $nrows - 1;
	#print "xmax=$xmax, ymax=$ymax\n";


	#print_ban_OLD( $ban );

	my $ban2;

	# 第2行は列の番号
	# 第3行からデータ
	for ( my $y = 3; $y <= $ymax; $y ++ ) {
	    # 第0列は行の番号
	    # 第1列からデータ
	    for ( my $x = 1; $x <= $xmax; $x ++ ) {
		if ( defined $ban->[$x][$y] ) {
		    $ban2->[$x-1][$y-3] = $ban->[$x][$y];
		} else {
		    $ban2->[$x-1][$y-3] = "-";
		}
	    }
	}
	#print_ban( $ban2, \*STDOUT );
	# 解答ファイルを作る(ソルバで解けなかったとき用)
	if ( 0 ) {
	    my $sheetname = $worksheet->get_name();
	    my $sfilename = sprintf("%s_%s_adc_sol.txt", $basefile, $sheetname);
	    open( my $fp0, ">$sfilename") || die "ERROR: open $sfilename";
	    print_ban_adc( $ban2, 1, $fp0 );
	    close $fp0
	}

	# 線を消して、端点のみを残す
	clear_number( $ban2 );

	my $sheetname = $worksheet->get_name();
	my $ofilename = sprintf("%s_%s.txt", $basefile, $sheetname);
	print $ofilename . "\n";
	open( my $fp, ">$ofilename") || die "ERROR: open $ofilename";
	print_ban( $ban2, $fp );
	close $fp;

	$ofilename = sprintf("%s_%s.csv", $basefile, $sheetname);
	print $ofilename . "\n";
	open( my $fp1, ">$ofilename") || die "ERROR: open $ofilename";
	print_ban_csv( $ban2, $fp1 );
	close $fp1;

	my $ofilename_adc = sprintf("%s_%s_adc.txt", $basefile, $sheetname);
	print $ofilename_adc . "\n";
	open( my $fp2, ">$ofilename_adc") || die "ERROR: open $ofilename_adc";
	print_Q_adc( $ban2, $fp2 );
	close $fp2;
    }
}

#-----------------------------------------------------------------------

for ( my $i = 0; $i <= $#ARGV; $i ++ ) {
    my $input_file = $ARGV[$i];
    print "input = $input_file\n";
    proc1( $input_file );
}

