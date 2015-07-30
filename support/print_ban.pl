sub print_ban {
    my ($ban, $fp) = @_;

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

    print $fp $ymax+1 . "\n";
    print $fp $xmax+1 . "\n";
    for ( my $y = 0; $y <= $ymax; $y ++ ) {
	for ( my $x = 0; $x <= $xmax; $x ++ ) {
	    if ( !defined $ban->[$x][$y] ||
		 $ban->[$x][$y] eq " " ||
		 $ban->[$x][$y] eq "-" ) {
		print $fp " - ";
	    } else {
		printf $fp sprintf("%2d ", $ban->[$x][$y]);
	    }
	}
	print $fp "\n";
    }
}

sub print_ban_csv {
    my ($ban, $fp) = @_;

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

    print $fp $ymax+1 . "\n";
    print $fp $xmax+1 . "\n";
    for ( my $y = 0; $y <= $ymax; $y ++ ) {
	for ( my $x = 0; $x <= $xmax; $x ++ ) {
	    if ( !defined $ban->[$x][$y] ||
		 $ban->[$x][$y] eq " " ||
		 $ban->[$x][$y] eq "-" ) {
		print $fp "   ,";
	    } else {
		printf $fp sprintf("%2d ,", $ban->[$x][$y]);
	    }
	}
	print $fp "\n";
    }
}

1;
