sub get_ban_size {
    my ($ban) = @_;

    # $ban�Ρ��ġ��������������Ĥ�����
    my @tmp = @{$ban};
    my $xmax = $#tmp;
    my @tmp2 = @{$ban->[0]};
    my $ymax = $#tmp2; # 0���ܤ������Ƥ����顢�������ʤ�
    for ( my $x = 0; $x <= $xmax; $x ++ ) {
	if ( !defined $ban->[$x] ) { next; }
	#print "x=$x\n";
	my @tmp3 = @{$ban->[$x]};
	if ( $ymax < $#tmp3 ) { $ymax = $#tmp3; }
    }

    return ($xmax, $ymax);
}

1;
