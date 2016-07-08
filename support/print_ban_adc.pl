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

sub print_ban_adc2016 {
    my ($data, $fp) = @_;

    my @tmp = @{$data};
    my $nlayers = $#tmp;
    my ($xmax0, $ymax0);
    for ( my $i = 1; $i <= $nlayers; $i ++ ) {
	my $ban = $data->[$i]->{ban};
	my $via = $data->[$i]->{via};
	
	my ($xmax, $ymax) = get_ban_size( $ban );
	if ( $i == 1 ) {
	    print $fp sprintf("SIZE %dX%dX%d\r\n", $xmax+1, $ymax+1, $nlayers);
	    $xmax0 = $xmax;
	    $ymax0 = $ymax;
	} else {
	    if ($xmax0 != $xmax || $ymax0 != $ymax) {
		printf("ERROR: ban size must be same: %dX%d != %dX%d\n",
		       $xmax0+1, $ymax0+1, $xmax+1, $ymax+1);
	    }
	}
	print $fp sprintf("LAYER %d\r\n", $i);
	# 盤面データを出力する
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
}

1;
