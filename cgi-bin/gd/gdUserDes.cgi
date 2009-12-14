#!/usr/bin/perl
use warnings;
use strict;
use CGI;
use GeneDesign;
use GeneDesignML;

my $query = new CGI;
print $query->header;

my @styles = qw(re ol);
gdheader("Building Block Design (USER overlap)", "gdUserDes.cgi", \@styles);

my %gapperlen   = (40 => 700, 50 => 740, 60 => 740, 70 => 720, 80 => 740, 90 => 720, 100 => 660);
my %ungapperlen = (40 => 700, 50 => 700, 60 => 750, 70 => 735, 80 => 760, 90 => 765, 100 => 750);
					
my $loxpsym = "ATAACTTCGTATAATGTACATTATACGAAGTTAT";
if (! $query->param('TARBBLLEN'))
{
	my $nucseq = $query->param('PASSNUCSEQ')	?	$query->param('PASSNUCSEQ')	:	cleanup($query->param('nucseq'), 1);	
print <<EOM;
				<div id="notes">
					<strong>To use this module you need a nucleotide sequence at least 5kb long, a target melting temperature, and a target oligo length.</strong><br>
					Your nucleotide sequence will be searched for the sequence AN{x}T, which will be used to divide the sequence into overlapping building blocks of approximately 750bp.<br>
					If your sequence is less than 1000 bp, there will only be one building block.<br>
					Remember to make the maximum assembly oligo length bigger than your assembly oligos.<br><br>
					See the <a href="$docpath/Guide/Userdes.html" target="blank">manual</a> for more information.
				</div>
				<div id="gridgroup0">
					Chunk sequence:<br>
					<textarea name="WHOLESEQ"  rows="6" cols="100"></textarea><br>
					Sequence name: <input type="text" name="CHNNAM" value="" size="50" maxlength="50" /><br><br>
					Begin numbering building blocks from: <input type="text" name="STARTNUM" value="1" size="3" maxlength="3" /><br><br>
					Return USER primers of Tm: <input type="text" name="USRMEL" value="56" size="2" maxlength="2" />&deg;<br>
					Eligible USER unique sequence lengths: 
						<input type="checkbox" name="USRUNILEN" value="5" checked="checked" />5bp
						<input type="checkbox" name="USRUNILEN" value="7" checked="checked" />7bp
						<input type="checkbox" name="USRUNILEN" value="9" checked="checked" />9bp
						<input type="checkbox" name="USRUNILEN" value="11" checked="checked"/>11bp<br><br>
					Average Building Block Length: ~ <input type="text" name="TARBBLLEN" value="740" size="4" maxlength="3" />bp<br><br>
					Generate Gapped Oligos? <input type="checkbox" name="GAPSWIT" value="1" checked="checked" />&nbsp;&nbsp;&nbsp;<br>
					Target Assembly Oligo Length: 
					<select name="TAROLILEN">
						<option value="40">40</option>
						<option value="50">50</option>
						<option selected="selected" value="60">60</option>
						<option value="70">70</option>
						<option value="80">80</option>
						<option value="90">90</option>
						<option value="100">100</option>
					</select>bp<br>
					Maximum Assembly Oligo Length: 
					<input type="text" name="MAXOLILEN" value="80" size="4" maxlength="3" />bp;<br>
					Return Assembly oligos with an overlap of Tm: <input type="text" name="TARCHNMEL" value="56" size="2" maxlength="2" />&deg;&nbsp;
					within ±<input type="text" name="CHNMELTOL" value="2.5" size="3" maxlength="3" />&deg;<br><br><br><br>
					<div id="gridgroup1" align ="center" style="position:absolute;top:405;">
						<input type="submit" name=".submit" value=" Design Building Blocks " />
						<input type="hidden" name="skipall" value="yes">
					</div>
				</div>
EOM
	closer();
}

elsif($query->param('WHOLESEQ'))
{
	my $wholeseq	= cleanup($query->param('WHOLESEQ'), 0);
	my $wholelen	= length($wholeseq);
	my $startnum	= $query->param('STARTNUM');			#default is 1
	my $tar_bbl_len	= $query->param('TARBBLLEN');			#default is 740bp
	my $usr_mel		= $query->param('USRMEL');				#default is 56û
	my @usr_uni_len	= $query->param(-name=>'USRUNILEN');	#default is just 7
	my $chunk_name	= $query->param('CHNNAM');
	
	my %pa;
	$pa{gapswit}		=	$query->param('GAPSWIT');			#default is 1;
	$pa{tar_chn_mel}	=	$query->param(-name=>'TARCHNMEL');	#default is 56û
	$pa{tar_oli_len}	=	$query->param(-name=>'TAROLILEN');						#default is 60
	$pa{per_chn_len}	= $pa{gapswit} == 1	?	$gapperlen{$pa{tar_oli_len}}			:	$ungapperlen{$pa{tar_oli_len}};
	$pa{tar_oli_lap}	= $pa{gapswit} == 1	?	20										:	.5 * $pa{tar_oli_len};# these are the defaults, 12 60mers with 20bp overlaps and 20bp gaps, nongapped oligos overlap by half the oligo length
	$pa{tar_oli_gap}	= $pa{gapswit} == 1	?	$pa{tar_oli_len}-(2*$pa{tar_oli_lap})	:	0;						# length = 2*(overlap) + gap, nongapped oligos have no gaps.
	$pa{tar_oli_num}	=	($pa{per_chn_len} - $pa{tar_oli_lap}) / ($pa{tar_oli_len} - $pa{tar_oli_lap});#18;
	$pa{chn_mel_tol}	=	$query->param(-name=>'CHNMELTOL');						#default is 2.5
	$pa{max_oli_len}	=	$query->param(-name=>'MAXOLILEN');						#default is 80
	$pa{melform}		=	3;
	
	if ($pa{max_oli_len} < $pa{tar_oli_len})
	{
		take_exception("The maximum allowable assembly oligo length ($pa{max_oli_len}) is less than the target assembly oligo length ($pa{tar_oli_len}).  Please go back and change the parameters.");
		exit;
	}
	if ($pa{max_oli_len} == $pa{tar_oli_len})
	{
		take_note("The maximum allowable assembly oligo length is equal to the target assembly oligo length ($pa{tar_oli_len}).  This may cause some weird behavior, especially in terms of overlap melting temperature.");
	}	
	if ($chunk_name !~ /^\d+[RL]\.\d+_\d+\.[A-Z]\d+$/)
	{
		take_note("Your chunk name does not conform to the expected format (chromosome)(arm).(genome version)_(chromosome version).(chunk letter)(chunk section)<br>
					I am producing output with \"$chunk_name\", but you may wish to re-run primer design with a proper name.<br>");
	}
	
	
	my %FoundSite;
	my %FoundSiteCoor;
	my @UniUsers;
	my @Collection;
	my @Chunks;
	my $offset = 0;	
	my $count = $startnum - 1;
	
	my $MASK = "0" x length($wholeseq);
##Mask loxpsym sites
	my $exp = regres($loxpsym, 1);
	while ($wholeseq =~ /($exp)/ig)
	{
		my $sit =  (pos $wholeseq) - length($loxpsym);
		substr($MASK, $sit, length($loxpsym)) = "1" x length($loxpsym) if ($sit ne '');
	}	
	
	if ($wholelen > 1000)
	{
	## Load two hashes with the number of times ANxT is seen and where the last one was seen. Parse the number hash for the unique ones, push into Data structure and store in array.
		foreach my $tiv (@usr_uni_len)
		{
			my @sites;
			$sites[0] = "A" . ("N" x $tiv) . "T";
			$sites[1] = complement($sites[0], 1) if (complement($sites[0], 1) ne $sites[0]);
			foreach my $sit (@sites)
			{
				my $exp = regres($sit, 1);
				while ($wholeseq =~ /($exp)/ig)
				{
					my $sitsta = (pos $wholeseq) + 1;
					if ($sitsta ne '') {	$FoundSite{$1}++;	$FoundSiteCoor{$1} = $sitsta + $offset - length($1);	}
				}
			}
		} 
		foreach my $tiv (keys %FoundSite)
		{
			if ($FoundSite{$tiv} == 1 && !exists($FoundSite{complement($tiv)}))
			{
				my $tno = new USERsite;	$tno->Sequence($tiv);	$tno->nNumber(length($tiv)-2);	$tno->Start($FoundSiteCoor{$tiv});
				push @UniUsers, $tno;
			}
		}

	## Adjust the target building block size so as to avoid outliers.
		my $tarnum = int(length($wholeseq) / $tar_bbl_len);
		my $diff = length($wholeseq) - ($tarnum * $tar_bbl_len);
		$tar_bbl_len = (($diff/$tarnum)*12.5 >= $tar_bbl_len)	?	int(length($wholeseq)/($tarnum+1) + .5)	:	$tar_bbl_len + int($diff/$tarnum);
		
	## Pick the unique sites as close as possible to the requested intervals.
		my %primerrank = ( 9 => 0, 7 => 1, 5 => 2, 3 => 3, 11 => 4);
		my $lasttarget = $offset;
		my $target = 0;
		while ($target < length($wholeseq))
		{
			$target = $tar_bbl_len + $lasttarget;
			my $seen = 0;my $door = 1;my $int = 1;
			while ($seen == 0)
			{
				my @grabbed = grep {$_->Start == $target} @UniUsers;
				if (@grabbed-0 > 0)
				{
					my $currchoice = $grabbed[0];
					foreach my $tov (@grabbed)
					{
						$currchoice = $tov	if ($primerrank{length($tov->Sequence)} < $primerrank{length($currchoice->Sequence)});
					}
					$lasttarget = $target;
					$target = $currchoice->Start + $tar_bbl_len;
					push @Collection, $currchoice;
					$seen = 1;
				}
				$target = $target - $int if ($door == 1);
				$target = $target + $int if ($door == 0);
				$door = abs($door-1);	$int++;
				if ($target <= ($lasttarget + (.4 * $tar_bbl_len)))
				{
					$lasttarget += ($tar_bbl_len * .5);last;
				}
				$seen = 0;	
			}
		}
		
	## Form chunk objects, fill with user primers and oligos
		my $lastfound = 1;
		my $laststart;
		my $lastlength = 0;
		foreach my $tiv (@Collection)
		{
			my $tno = new Chunk;
			my @Users;
		
			$tno->ChunkSeq(substr($wholeseq, $lastfound - 1, $tiv->Start - $lastfound + $tiv->nNumber + 2));
			if (length($tno->ChunkSeq) < length(substr($wholeseq, $lastfound-1)) && $count == int((length($wholeseq) / $tar_bbl_len)+.5) -1)
			{
				$tno->ChunkSeq(substr($wholeseq, $lastfound-1));
			}
			$tno->ChunkLength(length($tno->ChunkSeq));
			$tno->Mask(substr($MASK, $lastfound - 1, $tno->ChunkLength));
			$tno->ChunkStart($lastfound);
			$tno->ChunkStop($tno->ChunkLength + $tno->ChunkStart - 1);
			my $remain = length(substr($wholeseq, $tiv->Start-1));
			if ($remain < $tar_bbl_len / 4)	{	$tno->ChunkSeq(substr($wholeseq, $lastfound - 1));	}
			my $countstr = $count + 1;
			while (length(@Collection-0) > length($countstr))	{	$countstr = "0" . $countstr;}
			$tno->ChunkNumber($countstr);
			my $pri_len = 0;
			if ($count > 0)
			{
				$Users[0] = substr($wholeseq, $laststart, $lastlength + 2);
				until (int(melt($Users[0], 3) + .5) >= $usr_mel)	{$pri_len++;$Users[0] = substr($wholeseq, $laststart, $pri_len)	}
				$Users[1] = substr($Users[0], 0, $lastlength+1) . 'U' . substr($Users[0], $lastlength + 2);
			}
			else
			{
				$Users[0] = substr($wholeseq, 0, 5);
				until (int(melt($Users[0], 3) + .5) >= $usr_mel)	{$pri_len++;$Users[0] = substr($wholeseq, 0, $pri_len)	}
				$Users[1] = "-";
			}
			$pri_len = 0;
			if ($count != (@Collection-1))
			{
				$Users[2] = substr($wholeseq, $tiv->Start - 1, $tiv->nNumber + 2);
				until (int(melt($Users[2], 3) + .5) >= $usr_mel)	{$pri_len++;$Users[2] = substr($wholeseq, $tiv->Start - 1 - $pri_len, $tiv->nNumber + 2 + $pri_len);	}
				$Users[2] = complement($Users[2], 1);
				$Users[3] = substr($Users[2], 0, $tiv->nNumber + 1) . 'U' . substr($Users[2], $tiv->nNumber + 2);
				$laststart = $tiv->Start - 1;
				$lastlength = $tiv->nNumber;
			}
			else
			{
				$Users[2] = substr($wholeseq, -10);
				until (int(melt($Users[2], 3) + .5) >= $usr_mel)	{$pri_len++;$Users[2] = substr($wholeseq, -(10 + $pri_len));	}
				$Users[2] = complement($Users[2], 1);
				$Users[3] = "-";
			}
			$lastfound = $tiv->Start;#$lastseq = $tiv->Sequence;
			$tno->Users(\@Users);
			$count++;
					
			oligocruncher($tno, \%pa);
			push @Chunks, $tno;
		}
		take_note(scalar(@Collection) . " building blocks were generated.<br>");#, int((length($wholeseq) / $tar_bbl_len)+.5), "<br><br>";		
	}
	else
	{
		my $tno = new Chunk;
		my $countstr = $startnum;
		while (2 > length($countstr))	{	$countstr = "0" . $countstr;}
		$tno->ChunkSeq($wholeseq);
		$tno->ChunkLength($wholelen);
		$tno->Mask($MASK);
		$tno->ChunkStart(1);
		$tno->ChunkStop($tno->ChunkLength + $tno->ChunkStart - 1);
		$tno->ChunkNumber($countstr);
		oligocruncher($tno, \%pa);
		push @Chunks, $tno;
		take_note("1 building block was generated.<br>");#, int((length($wholeseq) / $tar_bbl_len)+.5), "<br><br>";
	}
		my $uniquelen = 0;
		my @alloligos;
		my @aonums;
		my @bbnums;
		my @allbbs;
		my @coords;
		my @allusers;
	

## Print Sequence all Pretty for Perusal
	foreach my $tiv (@Chunks)
	{
		print "Building Block $chunk_name.", $tiv->ChunkNumber, "&nbsp;&nbsp;&nbsp;", $tiv->ChunkLength, "bp&nbsp;&nbsp;&nbsp;", $tiv->ChunkStart, "..", $tiv->ChunkStop, "\n<Br>";
		if (@Chunks-0 > 1)
		{
			my $UserArrRef = $tiv->Users;my @userarr = @$UserArrRef;
			while ($userarr[1] =~ /(U)/ig)			{	$uniquelen = pos ($userarr[1]) - 2;	}
			unless ($tiv->ChunkNumber eq "01")
			{
				print "<code>Left&nbsp; - 5' <b>", substr($userarr[0], 0, 1), "</b><u>", substr($userarr[0], 1, $uniquelen), "</u><b>", substr($userarr[0], $uniquelen+1, 1), "</b>", substr($userarr[0], $uniquelen+2), " 3'<br>";
				print "LeftU - 5' <b>", substr($userarr[1], 0, 1), "</b><u>", substr($userarr[1], 1, $uniquelen), "</u><b>", substr($userarr[1], $uniquelen+1, 1), "</b>", substr($userarr[1], $uniquelen+2), " 3'</code><br>";
			}
			else
			{
				print "<code>Left&nbsp; - 5' $userarr[0] 3'</code><br>";
			}
			while ($userarr[3] =~ /(U)/ig)			{	$uniquelen = pos ($userarr[3]) - 2;	}
			unless ($tiv->ChunkNumber == @Collection-0)
			{
				print "<code>Rght&nbsp; - 5' <b>", substr($userarr[2], 0, 1), "</b><u>", substr($userarr[2], 1, $uniquelen), "</u><b>", substr($userarr[2], $uniquelen+1, 1), "</b>", substr($userarr[2], $uniquelen+2), " 3'<br>";				
				print "RghtU - 5' <b>", substr($userarr[3], 0, 1), "</b><u>", substr($userarr[3], 1, $uniquelen), "</u><b>", substr($userarr[3], $uniquelen+1, 1), "</b>", substr($userarr[3], $uniquelen+2), " 3'</code><br>";
			}
			else
			{
				print "<code>Rght&nbsp; - 5' $userarr[2] 3'</code><br>";
			}
		}
		print "Sequence:<br>", $query->textarea(-name=>$chunk_name.$count, -rows=>6, -columns=>150, -value=>$tiv->ChunkSeq, -readonly=>'true');
		push @allbbs, $tiv->ChunkSeq;
		push @coords, $tiv->ChunkStart. "..". $tiv->ChunkStop;
		my @oligoarr = @{$tiv->Oligos};
		my @olaparr = @{$tiv->Olaps};
		my %colhas = %{$tiv->Collisions};
		my @colkeys = keys %colhas;
		my $prev;
		print "<br>Assembly Oligos: average overlap Tm is ", $tiv->AvgOlapMelt, "&deg;;average oligo length is ", $tiv->AvgOligoLength, "bp.<br>";
		if (@colkeys-0 != 0)
		{
			print ("<div id = \"warn\">\n");
			print "<strong>Warning:</strong> in the following building block, there are ", @colkeys-0, " collisions<br>";
			print "Try increasing the Tm tolerance for assembly oligos to remove collisions.";
			print ("</div>");
		}
		if ($pa{tar_chn_mel} - $tiv->AvgOlapMelt > 5)
		{
			print ("<div id = \"warn\">\n");
			print "<strong>Warning:</strong> in the following building block, the average overlap melting temperature is more than 5&deg;from your specified target of $pa{tar_chn_mel}&deg;.<br>";
			print "Try increasing the maximum allowable length for assembly oligos to allow oligo extension for melting temperature uniformity.";
			print ("</div>");
		}
		print_oligos_aligned($tiv, $pa{gapswit}, 4, 1);
		print break(6);	
	}
	
## Offer files
	foreach my $tiv (@Chunks)
	{
		my $UserArrRef = $tiv->Users;
		my $oliarrref = $tiv->Oligos;	my $tcv = 1;
		push @aonums, @$oliarrref - 0;
		push @bbnums, @alloligos - 0;
		foreach (@$UserArrRef)
		{
			push @allusers, $_;
		}
		foreach (@$oliarrref)
		{
			my $seq = $_;	$seq = complement($_, 1) if ($tcv % 2 == 0);chomp($seq);
			push @alloligos, $seq;
			$tcv++;
		}
	}
	
	my %hiddenhash = ("startnum" => $startnum, "bbnums" => join(" ", @bbnums), "coords" => join(" ", @coords), "aonums" => join(" ", @aonums), "alloligos" => join(" ", @alloligos), "allbbs" => join(" ", @allbbs), "allusers" => join(" ", @allusers) );
	my $hiddenstring = hidden_fielder(\%hiddenhash);

print <<EOM;
			</form>
			<form name="form2" method="post" action="./order.cgi">
				<input type="hidden" name="swit" value="2" />
				<input type="hidden" name="name" value="$chunk_name" />
				FASTA format: <input type="submit" value="&nbsp;Assembly Oligos&nbsp;" onClick="FASTArizer(2)" /> <input type="submit" value="&nbsp;USER Oligos&nbsp;" onClick="FASTArizer(3)" /> <input type="submit" value="&nbsp;Building Blocks&nbsp;" onClick="FASTArizer(4)" /><br>
				tabbed format: <input type="submit" value="&nbsp;Assembly Oligos&nbsp;" onClick="FASTArizer(5)" /> <input type="submit" value="&nbsp;USER Oligos&nbsp;" onClick="FASTArizer(6)" /><br>
				Excel file: <input type="submit" value="&nbsp;Master Order Sheet&nbsp;" onClick="FASTArizer(7)" /> <input type="submit" value="&nbsp;Individual Order Sheets&nbsp;" onClick="FASTArizer(8)" /><br>
				zip archive: <input type="submit" value="&nbsp;BB $chunk_name order sheets&nbsp;" onClick="FASTArizer(9)" /><br><br>
				$hiddenstring
EOM
	closer();
}