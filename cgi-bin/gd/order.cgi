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
		if ($name != undef)
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
		$te = $x; $te = '0' . $te while (length($te) < length((@userarray-0)/4));
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








## Master order sheets
elsif ( $switch eq "7" )
{
	use Spreadsheet::WriteExcel;
	use Spreadsheet::ParseExcel;
	
	@la = qw(A B C D E F G H I);
	@allplates;
	$name = $query->param('name');
	$startnum = $query->param('startnum');
	@olarray = split(" ", $query->param('alloligos'));
	@olnums = split(" ", $query->param('bbnums'));
	push @olnums, undef if (@olnums-0 == 1);
	@aonums = split(" ", $query->param('aonums'));

	my $templ = new Spreadsheet::ParseExcel;
	foreach (@olnums)	{$switchkeys{$_} = 1;}
	$x = $startnum-1; $z = 1; $row = 1; $let = 0; $col = 1; $platenum = 1; $oldx = 1;
	$drow = 2; $dcol = 1;
	$totallength = 0;
	$platename = $name . ".p" . $platenum;
	$xls = "$docpath/tmp/" . $name . "_masters.xls";
	my $order = Spreadsheet::WriteExcel->new($xls);
	my $currsheet = $order->add_worksheet("$name.oligos");
	my $diagsheet = $order->add_worksheet("$name.diagrams");
	$diagsheet->write(0, 0, "$name Plate $platenum");
	for ($tcv = 1; $tcv <= 12; $tcv++)
	{
		$diagsheet->write(1, $tcv, "$tcv");
	}
	for ($tcv = 0; $tcv <= 7; $tcv++)
	{
		$diagsheet->write(2 + $tcv, 0, $la[$tcv]);
	}
	my $indigo = $order->set_custom_color(55, 51, 51, 153);
	my $gray25 = $order->set_custom_color(15, 192, 192, 192);
	%font1 = (font => 'Tahoma', size => 11, color => 'black', bold => 1);
	%font2 = (font => 'Tahoma', size => 11, color => 'white', bold => 1);
	$format1 = $order->add_format(%font2, bg_color=>$indigo);
	$format2 = $order->add_format(%font1, bg_color=>$gray25);
	$format3 = $order->add_format(%font1, bg_color=>'white');
	$format1->set_border(2);
	$format1->set_align('center');
	$format2->set_border(2);
	$format2->set_align('center');
	$format3->set_border(2);
	$currsheet->set_column(0, 0, 16);
	$currsheet->write(0, 0, "plate and well");
	$currsheet->set_column(1, 1, 8);
	$currsheet->write(0, 1, "oligo");
	$currsheet->set_column(2, 2, 100);
	$currsheet->write(0, 2, "sequence");
	$currsheet->write(0, 3, "Tm");
	$currsheet->write(0, 4, "length (bp)");
	$wellcount = 0;
	for ($y = 0; $y < @olarray - 0; $y++)
	{
		if (exists $switchkeys{$y})
		{
			$num = $switchkeys{$y};
			$x++;
			$z = 1;
			$currformat = $x % 2	?	$format1	:	$format2;
		}
		$te = $x; $te = "0" . $te while (length($te) < length(@olnums-0) || length($te) < 2);
		$ze = $z; $ze = "0" . $ze while (length($ze) < length((int((@olarray-0)/(@olnums-1)))));
		if ( $x != $oldx)
		{
			if ($aonums[$oldx] < (96 - $wellcount))
			{
				while ($col % 6 != 1)
				{
					$wellcount++;
					$diagsheet->write($drow, $dcol, "", $format3);
					$let = $col < 12	?	$let		:	$let + 1;
					$col = $col < 12	?	$col + 1	:	1;
					$drow = $dcol < 12	?	$drow		:	$drow + 1;
					$dcol = $dcol < 12	?	$dcol + 1	:	1;
				}
			}
			else
			{
				while ($la[$let] ne "I")
				{
					$wellcount++;
					$diagsheet->write($drow, $dcol, "", $format3);
					$drow = $dcol < 12	?	$drow		:	$drow + 1;
					$dcol = $dcol < 12	?	$dcol + 1	:	1;
					$let = $col < 12	?	$let		:	$let + 1;
					$col = $col < 12	?	$col + 1	:	1;
				}
				$platenum++;
				$drow++; $drow++;
				$diagsheet->write($drow, 0, "$name Plate $platenum");
				$drow++; 
				for ($tcv = 1; $tcv <= 12; $tcv++)
				{
					$diagsheet->write($drow, $tcv, "$tcv");
				}
				for ($tcv = 0; $tcv <= 7; $tcv++)
				{
					$diagsheet->write($drow + 1 + $tcv, 0, $la[$tcv]);
				}
				$drow++; $dcol = 1;
				$wellcount = 0;
				$let = 0;
				$col = 1;
			}
		}
		$currsheet->write($row, 0, "$name.p" . $platenum . "." . $la[$let] . $col);
		$diagsheet->write_string($drow, $dcol, "$te.$ze", $currformat);
		$drow = $dcol < 12	?	$drow		:	$drow + 1;
		$dcol = $dcol < 12	?	$dcol + 1	:	1;
		$currsheet->write_string($row, 1,  "$te.$ze");
		$currsheet->write($row, 2, $olarray[$y]);
		$currsheet->write($row, 3, int(melt($olarray[$y], 3) + .5));
		$currsheet->write($row, 4, length($olarray[$y]));
		$totallength += length($olarray[$y]);
		$wellcount++;
		$row++;
		$let = $col < 12	?	$let		:	$let + 1;
		$col = $col < 12	?	$col + 1	:	1;
		if ($la[$let] eq 'I')
		{
			$platenum++;
			$drow++; $drow++;
			$diagsheet->write($drow, 0, "$name Plate $platenum");
			$drow++; 
			for ($tcv = 1; $tcv <= 12; $tcv++)
			{
				$diagsheet->write($drow, $tcv, "$tcv");
			}
			for ($tcv = 0; $tcv <= 7; $tcv++)
			{
				$diagsheet->write($drow + 1 + $tcv, 0, $la[$tcv]);
			}
			$drow++; $dcol = 1;
			$wellcount = 0;
			$let = 0;
			$col = 1;
		}
		$z++;
		$oldx = $x;
	}
	while ($la[$let] ne "I")
	{
		$diagsheet->write($drow, $dcol, "", $format3);
		$drow = $dcol < 12	?	$drow		:	$drow + 1;
		$dcol = $dcol < 12	?	$dcol + 1	:	1;
		$let = $col < 12	?	$let		:	$let + 1;
		$col = $col < 12	?	$col + 1	:	1;
	}
	$currsheet->write($row+1, 4, "# nt syn:");
	$currsheet->write($row+2, 4, "$totallength");
	$order->close();
	$url = "$linkpath/tmp/" . $name . "_masters.xls";
	print "Location:$url\n\n";</html>
}








## Individual order sheets, as excel files or zipped
elsif ($switch eq "8" || $switch eq "9")
{
	use Spreadsheet::WriteExcel;
	use Spreadsheet::ParseExcel;
	
	@la = qw(A B C D E F G H I);
	@allplates;
	$name = $query->param('name');
	$bbname = $query->param('bbname');
	$startnum = $query->param('startnum');
	@olarray = split(" ", $query->param('alloligos'));
	@olnums = split(" ", $query->param('bbnums'));
	push @olnums, undef if (@olnums-0 == 1);
	@aonums = split(" ", $query->param('aonums'));

	my $templ = new Spreadsheet::ParseExcel;
	my $book = $templ->Parse('Order_Template.xls');	
	

	foreach (@olnums)	{$switchkeys{$_} = 1;}
	$x = $startnum-1; $z = 1; $row = 53; $let = 0; $col = 1; $platenum = 1; $oldx = 1;
	if ($name != undef)
	{
		$platename = $name . ".p" . $platenum;
	}
	else
	{
		$platename = $bbname . ".p" . $platenum;
	}
	$xls = "$docpath/tmp/" . $platename . ".xls";
	push @allplates, $platename;
	my $order = Spreadsheet::WriteExcel->new($xls);
	my $currsheet = $order->add_worksheet($platename);
	printtemp($book, $order, $currsheet, $platename);
	$wellcount = 0;
	for ($y = 0; $y < @olarray - 0; $y++)
	{
		if (exists $switchkeys{$y})
		{
			$num = $switchkeys{$y};
			$x++;
			$z = 1;
		}
		$te = $x; $te = '0' . $te while (length($te) < length(@olnums-0) || length($te) < 2);
		$ze = $z; $ze = '0' . $ze while (length($ze) < length((int(@olarray/(@olnums-1)))));
		if ( $x != $oldx)
		{
			if ($aonums[$oldx] < (96 - $wellcount))
			{
				while ($col % 6 != 1)
				{
					$currsheet->write($row, 0, $la[$let] . $col);
					$wellcount++;
					$row++;
					$let = $col < 12	?	$let		:	$let + 1;
					$col = $col < 12	?	$col + 1	:	1;
				}
			}
			else
			{
				while ($la[$let] ne "I")
				{
					$currsheet->write($row, 0, $la[$let] . $col);
					$wellcount++;
					$row++;
					$let = $col < 12	?	$let		:	$let + 1;
					$col = $col < 12	?	$col + 1	:	1;
				}
				$platenum++;
				$wellcount = 0;
				if ($name != undef)
				{
					$platename = $name . ".p" . $platenum;
				}
				else
				{
					$platename = $bbname . ".p" . $platenum;
				}
				$xls = "$docpath/tmp/" . $platename . ".xls";
				$order = Spreadsheet::WriteExcel->new($xls);
				push @allplates, $platename;
				$currsheet = $order->add_worksheet($platename);
				printtemp($book, $order, $currsheet, $platename);
				$let = 0;
				$col = 1;
				$row = 53;
			}
		}
		$currsheet->write($row, 0, $la[$let] . $col);
		if ($name != undef)
		{
			$currsheet->write($row, 1, "$name.$te.o$ze");
		}
		else
		{
			$currsheet->write($row, 1, "$bbname.o$ze");
		}
		$currsheet->write($row, 2, $olarray[$y]);
		$wellcount++;
		$row++;
		$let = $col < 12	?	$let		:	$let + 1;
		$col = $col < 12	?	$col + 1	:	1;
		if ($la[$let] eq 'I')
		{
			$platenum++;
			$wellcount = 0;
			$platename = $name . ".p" . $platenum;
			$xls = "$docpath/tmp/" . $platename . ".xls";
			$order = Spreadsheet::WriteExcel->new($xls);
			push @allplates, $platename;
			$currsheet = $order->add_worksheet($platename);
			printtemp($book, $order, $currsheet, $platename);
			$let = 0;
			$col = 1;
			$row = 0;
		}
		$z++;
		$oldx = $x;
	}
	while ($la[$let] ne "I")
	{
		$currsheet->write($row, 0, $la[$let] . $col);
		$row++;
		$let = $col < 12	?	$let		:	$let + 1;
		$col = $col < 12	?	$col + 1	:	1;
	}
	$order->close();
	if ($switch == 9)
	{
		print $query->header;
		my @args = ("zip", "$docpath/tmp/$name.zip");
		foreach $t (@allplates)
		{
			push @args, "$docpath/tmp/" . $t . ".xls";
		}
		print "<!--";
		print system(@args);
		print "-->";
		$url = "$linkpath/tmp/" . $name . ".zip";
		print "<a href=\"$url\"> $name order sheets </a><br>";	
	}
	else
	{
		print $query->header;
		$count  = 1;
		foreach $t (@allplates)
		{
			print "$name order <a href=\"$linkpath/tmp/" . $t . ".xls\"> sheet $count</a><br>";
			$count++;
		}
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

elsif ($switch eq "13")
{
	print $query->header;

	$ordername = $query->param('ordername');
	use Spreadsheet::WriteExcel;
	use Spreadsheet::ParseExcel;
	my $templ = new Spreadsheet::ParseExcel;
	my $book = $templ->Parse('Order_Template.xls');	
	$xls = "$docpath/tmp/" . $ordername . ".xls";
	$platenum= 1;
	@truelist;
	$name = $query->param('ordername');
	$platename = $ordername . ".p$platenum";
#	print "boog1.  $platename<br>";
	@la = qw(A B C D E F G H);
	@allplates;
	@olnums = (0);
	@batch = split(" ", $query->param('batch'));
	my $order = Spreadsheet::WriteExcel->new($xls);
##Diagram stuff
	my $diagsheet = $order->add_worksheet("$ordername.diagrams");
	my $currsheet = $order->add_worksheet($platename);
	printtemp($book, $order, $currsheet, $platename);
	$diagsheet->write(0, 0, "$platename");
	
	for ($tcv = 1; $tcv <= 12; $tcv++)	{	$diagsheet->write(1, $tcv, "$tcv");	$diagsheet->set_column($tcv, $tcv, 12);		}
	for ($tcv = 0; $tcv <= 7; $tcv++)	{	$diagsheet->write(2 + $tcv, 0, $la[$tcv]);	}
	my $indigo = $order->set_custom_color(55, 51, 51, 153);
	my $gray25 = $order->set_custom_color(15, 192, 192, 192);
	%font1 = (font => 'Tahoma', size => 8, color => 'black', bold => 1);
	%font2 = (font => 'Tahoma', size => 8, color => 'white', bold => 1);
	my $format1 = $order->add_format(%font2, bg_color=>$indigo);
	my $format2 = $order->add_format(%font1, bg_color=>$gray25);
	my $format3 = $order->add_format(%font1, bg_color=>'white');
	$format1->set_border(2);
	$format1->set_align('center');
	$format2->set_border(2);
	$format2->set_align('center');
	$format3->set_border(2);
	$format3->set_align('center');

	$let = 0; $col = 1; $row = 53;	$drow = 2; $dcol = 1; $x = 0;
	foreach $data (@batch)
	{
		$x++;
		$currformat = $x % 2	?	$format1	:	$format2;
		@bb = split("-", $data);
		$name = shift @bb;
		push @aonums, shift @bb;
		push @olnums, $olnums[-1] + $aonums[-1];
		$z = 1;
		if ($aonums[-1] > ((8-$let)*12) - ($col-1))
		{
			while($let != 0)
			{
#				print "$la[$let]$col\n";
				$currsheet->write($row, 0, $la[$let] . $col);
				$diagsheet->write($drow, $dcol, "x", $format3);
				$let = $col < 12	?	$let		:	$let <= 6	?	$let + 1	:	0;
				$col = $col < 12	?	$col + 1	:	1;
				$drow = $dcol < 12	?	$drow		:	$drow + 1;
				$dcol = $dcol < 12	?	$dcol + 1	:	1;
				$row++;
			}
			$col = 1;
			$platenum++; $drow++; $drow++;
			$platename = $ordername . ".p$platenum";
			$diagsheet->write($drow, 0, "$platename");
			$drow++;
			for ($tcv = 1; $tcv <= 12; $tcv++)	{	$diagsheet->write($drow, $tcv, "$tcv");	}
			for ($tcv = 0; $tcv <= 7; $tcv++)	{	$diagsheet->write($drow + 1 + $tcv, 0, $la[$tcv]);	}
			$drow++; $dcol = 1;
#			print "boog2.  $platename<br>";
			$currsheet = $order->add_worksheet($platename);
			printtemp($book, $order, $currsheet, $platename);
			$row = 53;
		}
#		print "\n" if ($let == 0);
		foreach (@bb)
		{
			$ze = $z; $ze = '0' . $ze while (length($ze) < length((int(@olarray/(@olnums-1)))));
#			print "$la[$let]$col\t$name", ".o$ze\t$_\n";
			$currsheet->write($row, 0, $la[$let] . $col);
			$currsheet->write($row, 1, $name . ".o$ze");
			$currsheet->write($row, 2,  "$_");
			@namebits = split(/\./, $name);
			push @truelist, $platename . "." . $la[$let] . $col ."\t" . $name . ".o$ze" . "\t" . $_;
			$diagsheet->write_string($drow, $dcol, $namebits[-1].".o$ze", $currformat) if ($z % 5 != 0);
			$diagsheet->write_string($drow, $dcol, $name.".o$ze", $currformat) if ($z % 5 == 0 || $z == 1);
			$let = $col < 12	?	$let		:	$let <=6	?	$let + 1	:	0;
			$col = $col < 12	?	$col + 1	:	1;
			$drow = $dcol < 12	?	$drow		:	$drow + 1;
			$dcol = $dcol < 12	?	$dcol + 1	:	1;
			$z++;
			$row++;
		}
		if ($col != 1 && $col != 7)
		{
			while ($col < 6)
			{
#				print "$la[$let]$col\n";
				$currsheet->write($row, 0, $la[$let] . $col);
				$col++;
				$row++;
				$diagsheet->write($drow, $dcol, "x", $format3);
				$drow = $dcol < 12	?	$drow		:	$drow + 1;
				$dcol = $dcol < 12	?	$dcol + 1	:	1;
			}
			if ($col == 1)
			{
				$let = $let <= 6	?	$let + 1	:	0;
			}
		}
		if ($let == 0)
		{
			$platenum++; $drow++;
			$platename = $ordername . ".p$platenum";
			$diagsheet->write($drow, 0, "$platename");
			$drow++;
			for ($tcv = 1; $tcv <= 12; $tcv++)	{	$diagsheet->write($drow, $tcv, "$tcv");	}
			for ($tcv = 0; $tcv <= 7; $tcv++)	{	$diagsheet->write($drow + 1 + $tcv, 0, $la[$tcv]);	}
			$drow++; $dcol = 1;
#			print "boog3.  $platename<br>";
			$currsheet = $order->add_worksheet($platename);
			printtemp($book, $order, $currsheet, $platename);
			$row = 53;
		}
	}			
	while($let != 0)
	{
#		print "$la[$let]$col\n";
		$currsheet->write($row, 0, $la[$let] . $col);
		$diagsheet->write($drow, $dcol, "x", $format3);
		$let = $col < 12	?	$let		:	$let <=6	?	$let + 1	:	0;
		$col = $col < 12	?	$col + 1	:	1;
		$drow = $dcol < 12	?	$drow		:	$drow + 1;
		$dcol = $dcol < 12	?	$dcol + 1	:	1;
		$row++;
	}
	$biglist = $order->add_worksheet("alloligos");
	$biglist->set_column(0, 0, 16);
	$biglist->write(0, 0, "plate and well");
	$biglist->set_column(1, 1, 16);
	$biglist->write(0, 1, "oligo");
	$biglist->set_column(2, 2, 100);
	$biglist->write(0, 2, "sequence");
	$tcv = 1;
	foreach (@truelist)
	{
		@boo = split("\t", $_);
		$biglist->write($tcv, 0, $boo[0]);
		$biglist->write($tcv, 1, $boo[1]);
		$biglist->write($tcv, 2, $boo[2]);
		$tcv++;
	}
	$biglist->write($tcv+1, 4, "# nt syn:");
	$biglist->write($tcv+2, 4, "$totallength");

	print "order <a href=\"$linkpath/tmp/" . $ordername . ".xls\"> sheets</a><br>";

}






sub printtemp
{
	my ($book, $order, $shee, $platename) = @_;
###OH MY GOD THIS SUCKS SO HARD
	my $indigo = $order->set_custom_color(55, 51, 51, 153);
	my $gray25 = $order->set_custom_color(15, 192, 192, 192);
	%font1 = (font => 'Tahoma', size => 16, color => 'white', bold => 1); 
	%font2 = (font => 'Tahoma', size => 11, color => 'black', bold => 1);
	%font3 = (font => 'Arial', size => 10, color => 'white', bold =>1);
	%font4 = (font => 'Arial', size => 10, color => 'black', bold =>1);
	%font5 = (font => 'Arial', size => 10, color => 'black');
	%font6 = (font => 'Tahoma', size => 14, color => 'black', bold => 1);
	$format1 = $order->add_format(%font1, bg_color=>$indigo);
	$format2 = $order->add_format(%font2, bg_color=>$gray25);
	$format3 = $order->add_format(%font3, bg_color=>$indigo);
	$format4 = $order->add_format(%font4, bg_color=>'white');
	$format5 = $order->add_format(%font5, bg_color=>'white');
	$format6 = $order->add_format(%font6, bg_color=>$gray25);
	$bookws = $book->{Worksheet}[0];
	for (my $x = $bookws->{MinRow}; defined $bookws->{MaxRow} && $x <= $bookws->{MaxRow}; $x++)
	{
		$shee->set_row($x, $bookws->{RowHeight}[$x]);
		for(my $y = $bookws->{MinCol}; defined $bookws->{MaxCol} && $y <= $bookws->{MaxCol}; $y++)
		{
			$shee->set_column($y, $y, $bookws->{ColWidth}[$y]);
			$cell = $bookws->{Cells}[$x][$y];
			$shee->write($x, $y, $cell->{Val}, $format1) if ($cell && ($x == 0));
			$shee->write($x, $y, $cell->{Val}, $format2) if ($cell && ($x == 1 || $x == 16 || $x == 29 || $x == 51));
			$shee->write($x, $y, $cell->{Val}, $format6) if ($cell && $x == 52);
			$shee->write($x, $y, $cell->{Val}, $format3) if ($cell && ($x >= 17 && $x <= 28));
			$shee->write($x, $y, $cell->{Val}, $format4) if ($cell && (($x >= 2 && $x <= 15) || ( $x >= 30 && $x <= 50 && $y == 0)));	
			$shee->write($x, $y, $cell->{Val}, $format5) if ($cell && ($x >= 30 && $x <= 50 && $y > 0));		
		}
	}
	$shee->write(51, 0, "Plate name: " . $platename, $format2);
}