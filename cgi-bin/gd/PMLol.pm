## Sequence Display and Annotation Functions. Really Dependent on CSS files.
##    This is all Perl that outputs HTML.  PML is short for Prism Markup Language.  Ha, ha. 

package PMLol;
use 5.006;
use POSIX qw(log10);
use RESite;
require Exporter;

@ISA = qw(Exporter);
@EXPORT = qw(break space cssbrowser platform enzmenu annpsite);
			
###### Functions for Making Life Easier
##-break		: makes the passed number of html line breaks.
##
##-space		: makes the passed number of non-braking spaces.
##
##-cssbrowser	: detects browser from $ENV and translates for the benefit of CSS stylesheet selection.
##					returns the appropriate stylesheet link
##-platform		: detects OS from $ENV and translates for the benefit of CSS stylesheet selection.
##					returns the appropriate st
##-enzmenu		: prints out the menu for enzyme selection.  This is just full of ugly form code that no one wants to look at everyday.
##
##-annpsite		: annotates an amino acid sequence with site data.  Takes: an aa array, a scalar switch,  
##					an array of results (42: BamHI ASP\n), an array of criteria and a hash criteria.
##					The array criteria is for broad strokes (all absents, all uniques, etc).  The hash
##					criteria is for specific sites, with pos(value) and site name(key). Output rows of 
##					40 aa residues annotated with HTML popup boxes
##					containing the result array data.  Site names that match array one will be one color, 
##					those that match array two will be a different color.  Those that are neither will be black.
##					This function returns true or hits by switch.

sub break
{
	my ($num) = @_;
	my $string = '';
	for ($x = 0; $x < $num; $x++)
	{
		$string .= "<br>";
	}
	return $string;
}
sub space
{
	my($num) = @_;
	my $string = '';
	for ($x = 0; $x < $num; $x++)
	{
		$string .= "&nbsp;";
	}
	return $string;
}

sub cssbrowser
{
	my $browstring = $ENV{'HTTP_USER_AGENT'};
	$brow = ''		if ($browstring =~ /Safari/);
	$brow = 'ff'	if ($browstring =~ /Firefox/);
	$brow = 'wie'	if ($browstring =~ /MSIE/ && $browstring =~ /Windows/);
	return $brow;
}

sub platform
{
	my $browstring = $ENV{'HTTP_USER_AGENT'};
	$plat = 'win'	if ($browstring =~ /Windows/);
	$plat = 'mac'	if ($browstring =~ /Macintosh/);
	return $plat;
}

sub enzmenu
{
	$emenu = new CGI;
	@crEndsV = ValueUp(1); @crLengV = ValueUp(2); @crCutV = ValueUp(3); @crBuffV = ValueUp(4); @crAmbiV = ValueUp(6); @crMethV = ValueUp(7);
	%crEnds  = LabelUp(1); %crLeng  = LabelUp(2); %crCut  = LabelUp(3); %crBuff  = LabelUp(4); %crAmbi  = LabelUp(6); %crMeth  = LabelUp(7);
	print ("<div id=\"critsep\">\n  <span id=\"critlabel\">Ends</span>\n  <span id=\"criteria\">\n");
	print ("<input type=\"radio\" name=\"crEndss\" value=\"a\"> All Ends<br>\n<input type=\"radio\" name=\"crEndss\" value=\"r\" checked> Only \n");	
	print $emenu->checkbox_group(-name=>'crEnds', -values=>\@crEndsV, -default=>['5', '3'], -labels=>\%crEnds);
	print ("  </span>\n  </div>", break(3), "\n  <div id=\"critsep\">\n  <span id=\"critlabel\">Cut</span>\n  <span id=\"criteria\">\n");
	print ("<input type=\"radio\" name=\"crCutss\" value=\"a\"> All Cuts<br>\n<input type=\"radio\" name=\"crCutss\" value=\"r\" checked> Only \n");	
	print $emenu->checkbox_group(-name=>'crCuts', -values=>\@crCutV,  -default=>["1"], -labels=>\%crCut);
	print ("  </span>\n  </div>", break(3), "\n  <div id=\"critsep\">\n   <span id=\"critlabel\">Site Length</span><span id=\"criteria\">\n");	
	print ("<input type=\"radio\" name=\"crLengs\" value=\"a\" checked> All Lengths<br>\n    <input type=\"radio\" name=\"crLengs\" value=\"r\"> Only Lengths of \n");
	print $emenu->checkbox_group(-name=>'crLeng', -values=>\@crLengV, -labels=>\%crLeng);
	print ("  </span>\n  </div>", break(3), "\n  <div id=\"critsep\">\n   <span id=\"critlabel\">Allow Ambiguous Bases?</span><span id=\"criteria\">\n");	
	print ("<input type=\"radio\" name=\"crAmbis\" value=\"a\" checked> Allow Any Base<br>\n    <input type=\"radio\" name=\"crAmbis\" value=\"r\"> Allow Only \n");
	print $emenu->checkbox_group(-name=>'crAmbi', -values=>\@crAmbiV, -default=>['1', '2'], -labels=>\%crAmbi);
	print ("  </span>\n  </div>", break(3), "\n  <div id=\"critsep\">\n   <span id=\"critlabel\">Methylation Sensitivity</span><span id=\"criteria\">\n");
	print ("<input type=\"radio\" name=\"crMeths\" value=\"a\" checked> Allow Any Sensitivity<br>\n    <input type=\"radio\" name=\"crMeths\" value=\"r\"> Allow No Sensitivity<br>\n");
	print ("    <input type=\"radio\" name=\"crMeths\" value=\"o\">Allow Only (b= blocked, i= impaired)\n");
	print $emenu->checkbox_group(-name=>'crMeth', -values=>\@crMethV, -labels=>\%crMeth), "<br>";
	print ("  </span><br>\n  </div>", break(4), "\n  <div id=\"critsep\">\n   <span id=\"critlabel\">Price Range</span><span id=\"criteria\">\n");
	print ("<input type=\"radio\" name=\"crPrir\" value=\"a\" checked> Any (\$.00424 to \$2.304 per unit)<br>\n    <input type=\"radio\" name=\"crPrir\" value=\"r\"> Must Be between \n");
	print "\$", $emenu->textfield(-name=>'crPrlo', -default=>'.00424', -size=> 7, -maxlength=>6), "and ";
	print "\$", $emenu->textfield(-name=>'crPrhi', -default=>'.504', -size=>7, -maxlength=>6), " per unit\n";
	print ("  </span>\n  </div>", break(3), "\n  <div id=\"critsep\">\n   <span id=\"critlabel\" style=\"width:200;\">Disallow sites with: (boolean OR, separate by comma)</span>\n");
	print ("<span id=\"criteria\" style=\"left:200;\">\n", $emenu->textfield(-name=>'crDisa', -size=> 20));
	print ("  </span>\n  </div>", break(3), "\n  <div id=\"critsep\">\n   <span id=\"critlabel\" style=\"width:200;\">Allow only sites with: (boolean OR, separate by comma)</span>\n");
	print ("<span id=\"criteria\" style=\"left:200;\">\n", $emenu->textfield(-name=>'crAllo', -size=> 20));
	print ("\n   </span>\n  </div>", break(5), "\n");
	print $emenu->button(-name=>'ShowAll', -onClick=>"EnzMostPerm();", -label=>"Most Permissive Settings");

	return (1);
}


sub annpsite
{
	my ($aaseq, $swit, $refresarr, $cref1, $cref2) = @_;
	@resarr = @$refresarr;
	my %crit2  = %$cref2;
	my %crit1 = map {$_ => 1 } @$cref1;
	my @aa = @$aaseq;
	my $size = @aa;
	$times = int($size/40)+1;
	my @hits;
	$s = 0;
	$curpos = 0; $starta = 0; $startc = 0; $start = 0;
		$lininc = 28; $dotinc = 25;
		$lininc = 30 if (platform() eq 'mac' && cssbrowser() eq 'ff');
		$dotinc = 27 if (platform() eq 'mac' && cssbrowser() eq 'ff');
	for ($j = 0; $j < $times; $j++)
	{
	##-decides what color the background will be and where the top of the row div is
		$top = $j*230;
		$bgcolor = "ABC" unless ($j % 2);
		$bgcolor = "CDE" if     ($j % 2);
		print (" &nbsp;<br><div id = \"gridgoup1\" style = \"background-color: \43$bgcolor; position: absolute; top: $top; \">\n");
	##-prints up to 40 amino acids, asterisks under every 10th, and resets $curpos
		print ("  <p id = \"aaline\">");
		while ($curpos != 40 && $starta < $size)
		{
			print ("$aa[$starta]");
			$starta++; $curpos++;
		}
		$curpos = 0;
		print ("<$starta<br>");
		while ($curpos != 40 && $startc < $size)
		{
			print "&nbsp;" if (($curpos+1) % 10 != 0);
			print "*"	   if (($curpos+1) % 10 == 0);
			$startc++; $curpos++;
		}
		print ("</p>\n");
		$curpos = 0;
	##-start drawing select boxes
		for ($i = $start; $i < (@resarr-0); $i++)
		{
		##-splits resarr into @little(site) and @little2(name)
			@little  = split(":", $resarr[$i]);
			@little2 = split(" ", $little[1] );
		##-if we have changed position and need a new select box
			if ($little[0] != ($curpos + ($j*40)))
			{
			##-determine the current position, last position, and left coordinates of previous and current lines and dots
				$oldcur = $curpos;
				$olelin = (($oldcur*17)+$lininc);
				$oledot = (($oldcur*17)+$dotinc);
				$curpos = ($little[0]-($j*40));
				$lelin  = (($curpos*17)+$lininc);
				$ledot  = (($curpos*17)+$dotinc);
				if ($curpos != 41 && $curpos < 42)
				{
					print "  </select>\n" if ($curpos > 1);
				##-if last site was crit1, overprint last line and dot in red (z-index 325 or 175)
					if ($happened != 0)
					{
						print("  <img id=\"dot$oldcur\" style=\"left:$oledot; z-index:325;\" src=\"../../gd/img/dred.gif\">\n");
						print("  <img id=\"line$oldcur\" style=\"left:$olelin; z-index:175;\" src=\"../../gd/img/lred.gif\">\n");
					}
				##-if last site was a cutter, overprint last line and dot in blue (z-index 425 or 200)
					if ($happenedc != 0)
					{
						print("  <img id=\"dot$oldcur\" style=\"left:$oledot; z-index:425;\" src=\"../../gd/img/dblue.gif\">\n");
						print("  <img id=\"line$oldcur\" style=\"left:$olelin; z-index:200;\" src=\"../../gd/img/lblue.gif\">\n");
					}
					$happened = 0; $happenedc = 0;
				##-check to see if this is a crit1 or crit2 site
					$flag  = 1 if (exists $crit1{$little2[0]} );
					$flagc = 2 if (exists $crit2{$little2[0]} && $crit2{$little2[0]} == $little[0]);
				##-if it's an crit1 site print line and dot in red
					if ($flag == 1 && $flagc == 0) 
					{
						print("  <img id=\"dot$curpos\" style=\"left:$ledot; z-index:325\" src=\"../../gd/img/dred.gif\">\n");
						print("  <img id=\"line$curpos\" style=\"left:$lelin; z-index:175\" src=\"../../gd/img/lred.gif\">\n");
						print("  <select id =\"box$curpos\" name=\"site$little[0]\">\n");
						print("    <option>  -  </option>\n");
						print("    <option>*$little2[0]</option>\n");	
						$hits[$s] = "$little[0].$little2[0]:";
						$s++;
					}
				##-if it's a crit2 cutter print line and dot in blue
					elsif ($flag == 1 && $flagc == 2)
					{
						print("  <img id=\"dot$curpos\" style=\"left:$ledot; z-index:425\" src=\"../../gd/img/dblue.gif\">\n");
						print("  <img id=\"line$curpos\" style=\"left:$lelin; z-index:200\" src=\"../../gd/img/lblue.gif\">\n");
						print("  <select id =\"box$curpos\" name=\"site$little[0]\">\n");
						print("    <option>  -  </option>\n");
						print("    <option selected>·$little2[0]</option>\n");
					}
				##-if it's not, print in black
					elsif ($flag == 0 && $flagc == 0)
					{
						print("  <img id=\"dot$curpos\" style=\"left:$ledot;\" src=\"../../gd/img/dblack.gif\">\n");
						print("  <img id=\"line$curpos\" style=\"left:$lelin;\" src=\"../../gd/img/lblack.gif\">\n");
						print("  <select id =\"box$curpos\" name=\"site$little[0]\">\n");
						print("    <option>  -  </option>\n");
						print("    <option>$little2[0]</option>\n");	
					}
					$flag  = 0;
					$flagc = 0;	
				}
				else
				{
					last;
				}
			}
		#-elsif we're still writing to the same select box
			elsif ($little[0] == ($curpos + ($j*40)))
			{
			##-check to see if this is a crit1 or crit2 site
				$flag  = 1 if (exists $crit1{$little2[0]});
				$flagc = 2 if (exists $crit2{$little2[0]} && $crit2{$little2[0]} == $little[0]);
			##-if it's an crit1 site mark and set flag $happened
				if ($flag == 1 && $flagc == 0) 
				{
					print("    <option>*$little2[0]</option>\n");
					$hits[$s] = "$little[0].$little2[0]:";
					$s++;
					$happened = $curpos;
				}
			##-if it's a crit2 cutter mark, select, and set flag $happenedc
				elsif ($flag == 1 && $flagc == 2)
				{
					print("    <option selected>·$little2[0]</option>\n");
					$happenedc = $curpos;	
				}
			##-if it's not, print in black
				elsif ($flag == 0 && $flagc == 0)
				{
					print("    <option>$little2[0]</option>\n");
				}
				$flag  = 0;
				$flagc = 0;
			}
			last if ($curpos == 41);
		}
		print ("  </select>\n");
				$oldcur = ($curpos-1);
		$olelin = (($oldcur*17)+$lininc);
		$oledot = (($oldcur*17)+$dotinc);
	##-check to see if need to overprint a line in red
		if ($happened != 0)
		{
			$olelin = (($happened*17)+$lininc);
			$oledot = (($happened*17)+$dotinc);
			print("  <img id=\"dot$happened\" style=\"left:$oledot; z-index:325\" src=\"../../gd/img/dred.gif\">\n");
			print("  <img id=\"line$happened\" style=\"left:$olelin; z-index:175\" src=\"../../gd/img/lred.gif\">\n");
		}
	##-check to see if need to overprint a line in blue
		if ($happenedc != 0)
		{
			$olelin = (($happenedc*17)+$lininc);
			$oledot = (($happenedc*17)+$dotinc);
			print("  <img id=\"dot$happenedc\" style=\"left:$oledot; z-index:425\" src=\"../../gd/img/dblue.gif\">\n");
			print("  <img id=\"line$happenedc\" style=\"left:$olelin; z-index:200\" src=\"../../gd/img/lblue.gif\">\n");
		}
		$happened  = 0;
		$happenedc = 0;
		$start     = $i--;
		$curpos    = 0;
 		print ("  ", break(14), "&nbsp;");
		print ("\n",  space(200), ".</div>\n");
	}
	return @hits if ($swit == 1);
	return 1 if ($swit != 1);
}
