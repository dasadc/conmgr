sub get_ban_size {
    my ($ban) = @_;

    # $banの、縦、横サイズを求める…うーん。
    my @tmp = @{$ban};
    my $xmax = $#tmp;
    my @tmp2 = @{$ban->[0]};
    my $ymax = $#tmp2; # 0列目だけ見ていたら、正しくない
    for ( my $x = 0; $x <= $xmax; $x ++ ) {
	if ( !defined $ban->[$x] ) { next; }
	#print "x=$x\n";
	my @tmp3 = @{$ban->[$x]};
	if ( $ymax < $#tmp3 ) { $ymax = $#tmp3; }
    }

    return ($xmax, $ymax);
}

sub print_ban_adc {
    my ($ban, $num, $fp) = @_;

    my ($xmax, $ymax) = get_ban_size( $ban );
    if ( $num == 1 ) {
	print $fp sprintf("SIZE %dX%d\r\n", $xmax+1, $ymax+1);
    } else {
	print $fp "\r\n";
    }
    for ( my $y = 0; $y <= $ymax; $y ++ ) {
	for ( my $x = 0; $x <= $xmax; $x ++ ) {
	    if ( !defined $ban->[$x][$y] ||
		 $ban->[$x][$y] eq " " ||
		 $ban->[$x][$y] eq "-" ) {
		$ban->[$x][$y] = 0;
	    }
	    printf $fp sprintf("%02d", $ban->[$x][$y]);
	    if ( $x < $xmax ) {
		print $fp ",";
	    }
	}
	print $fp "\r\n";
    }
}

1;
