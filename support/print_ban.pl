sub print_ban {
    my ($ban, $fp, $csv) = @_;
    my ($xmax, $ymax) = get_ban_size( $ban );
    my $spacer = ' ';
    if (defined $csv) {
	$spacer = ',';
    }
    
    print $fp $ymax+1 . "\n";
    print $fp $xmax+1 . "\n";
    for ( my $y = 0; $y <= $ymax; $y ++ ) {
	for ( my $x = 0; $x <= $xmax; $x ++ ) {
	    if ( !defined $ban->[$x][$y] ||
		 $ban->[$x][$y] eq " " ||
		 $ban->[$x][$y] eq "-" ) {
		print $fp " -";
	    } else {
		printf $fp sprintf("%2d", $ban->[$x][$y]);
	    }
	    print $fp $spacer;
	}
	print $fp "\n";
    }
}

sub print_ban2016 {
    my ($data, $fp, $csv) = @_;
    my @tmp = @{$data};
    my $nlayers = $#tmp;
    my ($xmax0, $ymax0);
    my $spacer = ' ';
    if (defined $csv) {
	$spacer = ',';
    }
    for ( my $i = 1; $i <= $nlayers; $i ++ ) {
	my $ban  = $data->[$i]->{ban};
	my $vias = $data->[$i]->{via};
	#dump_vias($vias);
	my ($xmax, $ymax) = get_ban_size( $ban );
	clear_number( $ban ); # 2回以上実行しても問題ない
	if ( $i == 1 ) {
	    print $fp sprintf("%d\r\n%d\r\n", $ymax+1, $xmax+1);
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
		    print $fp " -";
		} else {
		    my $via = find_via($vias, $x, $y, $i);
		    #print "via=$via\n";
		    if ( $via eq "" ) { # 数字マスのとき
			printf $fp sprintf("%02d", $ban->[$x][$y]);
		    } else {
			printf $fp sprintf("%2s", $via);
		    }
		}
		print $fp $spacer;
	    }
	    print $fp "\r\n";
	}
    }
}

# sub print_ban_csv {
#     my ($ban, $fp) = @_;
#     my ($xmax, $ymax) = get_ban_size( $ban );

#     print $fp $ymax+1 . "\n";
#     print $fp $xmax+1 . "\n";
#     for ( my $y = 0; $y <= $ymax; $y ++ ) {
# 	for ( my $x = 0; $x <= $xmax; $x ++ ) {
# 	    if ( !defined $ban->[$x][$y] ||
# 		 $ban->[$x][$y] eq " " ||
# 		 $ban->[$x][$y] eq "-" ) {
# 		print $fp "   ,";
# 	    } else {
# 		printf $fp sprintf("%2d ,", $ban->[$x][$y]);
# 	    }
# 	}
# 	print $fp "\n";
#     }
# }

1;
