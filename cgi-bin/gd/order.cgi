#!/usr/bin/perl

use CGI;
use GeneDesign;
my $query = new CGI;
use Text::Wrap qw($columns &wrap);

my $switch = $query->param('swit');
if ($switch eq "1")
{
	print $query->header(-type=>'text/plain');
	@olarray = split(" ", $query->param('olarray'));

	$ch = "\11" if ($query->param('sepchar') eq 'tab');
	$ch = ','	if ($query->param('sepchar') eq 'comma');
	$ch = ' '	if ($query->param('sepchar') eq 'space');
	$ch = '_'	if ($query->param('sepchar') eq 'underscore');

	for ($y = 0; $y < @olarray-0; $y++)
	{
		$x = $y+1;
		$x = '0' . $x while (length($x) < length(@olarray-0));
		print $query->param('oldesig'), $x, $ch, $olarray[$y], "\n";
	}
}
elsif ($switch eq "2" || $switch eq "5")
{
	print $query->header(-type=>'text/plain') if ($switch == 2);	
	if ($switch == 5)
	{
		print $query->header();
		print "<table style=\"font-family: Courier, monospace; font-size: 10;\">\n";
		print "\t<tr><td>&nbsp;&nbsp;#&nbsp;&nbsp;&nbsp;&nbsp;</td><td>Sequence 5'-3'</td><td>bp</td></tr>\n";
	}
	@olarray = split(" ", $query->param('alloligos'));
	@olnums = split(" ", $query->param('bbnums'));
	push @olnums, undef if (scalar(@olnums) == 1);
	my %switchkeys = map {$_ => 1} @olnums;
	$name = $query->param('name');
	$bbname = $query->param('bbname');
	$startnum = $query->param('startnum');
	$x = $startnum-1;
	$z = 1;
	for my $y (0..scalar(@olarray - 1))
	{
		if (exists $switchkeys{$y})
		{
			$num = $switchkeys{$y};
			$x++;
			$z = 1;
		}
		$te = $x;
		$te = '0' . $te while (length($te) < length(@olnums-0) || length($te) < 2);
		$ze = $z;
		$ze = '0' . $ze while (length($ze) < length((int(@olarray/(@olnums-1)))));
		if ($name)
		{	
			print ">$name.$te.o$ze ", length($olarray[$y]), "bp\n", $olarray[$y], "\n" if ($switch == 2);
			print "\t<tr><td>$name.$te.o$ze</td><td>", $olarray[$y], "</td><td>", length($olarray[$y]), "</td></tr>\n" if ($switch == 5);
		}
		else
		{	
			print ">$bbname.$te.o$ze ", length($olarray[$y]), "bp\n", $olarray[$y], "\n" if ($switch == 2);
			print "\t<tr><td>$bbname.$te.o$ze</td><td>", $olarray[$y], "</td><td>", length($olarray[$y]), "</td></tr>\n" if ($switch == 5);
		}		
		$z++;
	}
	if ($switch == 5)
	{
		print "</table>";
	}
}
elsif ($switch eq "3" || $switch eq "6")
{
	print $query->header(-type=>'text/plain') if ($switch == 3);
	if ($switch == 6)
	{
		print $query->header();
		print "<table style=\"font-family: Courier, monospace; font-size: 10;\">\n";
		print "<tr><td>&nbsp;&nbsp;#&nbsp;&nbsp;&nbsp;&nbsp;</td><td>Sequence 5'-3'</td></tr>\n";
	}
	@userarray = split(" ", $query->param('allusers'));
	$name = $query->param('name');
	my %useroliname = (1 => "LT", 2 => "LU", 3 => "RT", 0 => "RU");
	$x = 1; $z = 1;
	foreach (@userarray)
	{
		$te = $x; $te = '0' . $te while (length($te) < length((@userarray-0)/4) || length($te) < 2);
		print ">$name.$te.u", $useroliname{$z%4}, " ", length($_), "bp\n", $_, "\n" if ($_ ne '-' && $switch == 3);
		print "\t<tr><td>$name.$te.u", $useroliname{$z%4}, "</td><td>$_</td></tr>\n" if ($switch == 6);
		$x++ if ($z % 4 == 0);
		$z++;
	}
}
elsif ($switch eq "4")
{
	print $query->header(-type=>'text/plain');
	@bbarray = split(" ", $query->param('allbbs'));
	@coords = split(" ", $query->param('coords'));
	$name = $query->param('name');
	$startnum = $query->param('startnum');
	$x = $startnum;
	$columns = 81;
	for ($y = 0; $y < @bbarray - 0; $y++)
	{
		$te = $x; $te = '0' . $te while (length($te) < length(@bbarray-0) || length($te) < 2);
		print ">$name.$te ", length($bbarray[$y]), "bp $coords[$y]\n";
		print wrap("","", $bbarray[$y]), "\n";
		$x++;
	}
}



elsif ($switch eq "12")
{
	print $query->header(-type=>'text/plain');
	@batch = split(" ", $query->param('batch'));
	foreach $data (@batch)
	{
		@bb = split("-", $data);
		$name = shift @bb;
		$number = shift @bb;
		$z = 1;
		foreach (@bb)
		{
			$ze = $z; $ze = '0' . $ze while (length($ze) < length((int(@olarray/(@olnums-1)))));
			print ">$name.$te", "o$ze ", length($_), "bp\n$_\n";
			$z++;
		}
		print "\n";
	}
}