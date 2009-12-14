#!/usr/bin/perl

use CGI;
use GeneDesign;
use PML;

my $query = new CGI;
print $query->header;

my %gapperlen   = (40 => 700, 50 => 740, 60 =>740, 80 =>740, 100 => 660);
my %ungapperlen = (40 => 700, 50 => 700, 60 =>750, 80 =>680, 100 => 750);

my @styles = qw(re ol);
gdheader("Oligo Re-Design", "gdOliReDes.cgi", \@styles);

if ($query->param('TARCHNMEL') eq '')
{
	my $nucseq = $query->param('PASSNUCSEQUENCE')	?	$query->param('PASSNUCSEQUENCE')	:	$query->param('nucseq');
	my $LengChoose;
	foreach (sort keys %gapperlen)	{	$LengChoose .= ($_ == 60)	?	"<option selected value=\"$_\">$_</option>\n" . tab(6) :	"<option value=\"$_\">$_</option>\n" . tab(6);}
print <<EOM;
				<div id="notes">
					<strong>To use this module you need a single ~750bp nucleotide sequence that has been previously rendered into oligos, a target melting temperature, and a target oligo length.</strong><br>
					This plugin will recalculate the oligo positions by -20 and +20 bp, so it is important to enter the exact nucleotide sequence from the broken building block.
					Gapped Oligo generation seeks to create chunks of uniform overlap melting temperature; Ungapped Oligo generation seeks to create chunks of uniform oligo length.<br><br>
					<em>Please Note:</em><br>
					&nbsp;&nbsp;&bull;Be sure to provide the same target melting temperature and oligo length from the original calculation!<br>
					&nbsp;&nbsp;&bull;Gapped oligos are generated by default.  Uncheck "Generate Gapped Oligos" to make gapless chunks.<br>
					See the <a href="../../gd2/Guide/olides.html" target="blank">manual</a> for more information.
				</div>
				<div id="gridgroup0">Your nucleotide sequence:<br>
					<textarea name="newnucseq" rows="6" cols="100">$nucseq</textarea><br>
					Building Block name: <input type="text" name="BBNAM" value="" size="50" maxlength="50" /><br><br>
					Target Oligo Length: 
					<select name="TAROLILEN" >
						$LengChoose
					</select>bp
					&nbsp;&nbsp;&nbsp;
					Overlap Melting Temperature: <input type="text" name="TARCHNMEL" value="56" size="2" maxlength="2"/>&deg;<br><br>
					Maximum Allowable Oligo Length <input type="text" name="MAXOLILEN" value="80" size="2" maxlength="2" />bp<br><br>
					Generate Gapped Oligos? <input type="checkbox" name="GAPSWIT" value="1" checked="checked" />&nbsp;&nbsp;&nbsp;
					<div id="gridgroup1" align ="center" style="position:absolute; top:300; ">
						<input type="submit" name=".submit" value=" Design Oligos " />
						<input type="hidden" name="skipall" value="yes">
					</div>
				</div>
EOM
	closer();
}


elsif($query->param('newnucseq') ne '')
{
	my $newnuc  = cleanup($query->param('newnucseq'), 1);
	my $aaseq   = $query->param('skipall')	?	translate($newnuc, 1, $CODON_TABLE)	:	$query->param('aaseq');	
	my $gapswit			= $query->param('GAPSWIT');			#default is 1;
	my $tar_chn_lap	= .5 * $query->param('TARCHNLAP');
	$tar_chn_mel	= $query->param('TARCHNMEL');			#default is 60�
	$tar_oli_len	= $query->param('TAROLILEN');			#default is 60bp
	$per_chn_len	= $gapperlen{$tar_oli_len} if ($gapswit == 1);
	$per_chn_len	= $ungapperlen{$tar_oli_len} if ($gapswit == 0);
	$tar_oli_lap	= 20							if ($gapswit == 1);	# these are the defaults, 12 60mers with 20bp overlaps and 20bp gaps
	$tar_oli_lap	= .5 * $tar_oli_len				if ($gapswit == 0);	# nongapped oligos overlap by half the oligo length	
	$tar_oli_gap	= $tar_oli_len-(2*$tar_oli_lap)	if ($gapswit == 1);	# length = 2*(overlap) + gap	
	$tar_oli_gap	= 0								if ($gapswit == 0);	# nongapped oligos have no gaps.
	$tar_oli_num	= ($per_chn_len - $tar_oli_lap) / ($tar_oli_len - $tar_oli_lap);	# num = ( (chunk-overlap) / (length-overlap) )
	$chn_mel_tol	= 2;
	$max_oli_len	= $query->param('MAXOLILEN');			#default is 80bp
	$mform			= 3;
	$nsize			= length($newnuc);
	$bb_name		= $query->param('BBNAM');

####PRE ERROR CHECK - pass only if sequence to be oligo-ed is an appropriate length
	if ( $nsize < 60)				#TOO SMALL FOR THIS MODULE
	{
print <<EOM;
				<div id="notes">
					Your nucleotide sequence is only $nsize bp.<br>
					A sequence of this length (less than 60bp) can be ordered as a single oligo.<br>
					<input type="hidden" name="passnucseq" value="$newnuc"><br>
					<input type="submit" name=".submit" value="Sequence Analysis" onclick="SeqAna();" /><-- for information about this sequence
					<br><br><input type="button" value="Back" onClick="history.go(-1)">
				</div>
EOM
		closer();
	}
	elsif ($nsize > 17000)			#TOO BIG FOR GENEDESIGN
	{
print <<EOM;
				<div id="notes">
					Your nucleotide sequence is $nsize bp.<br>
					We will run out of unique restriction sites before we are able to finish this design.<br>
					It is recommended that you break this sequence up further yourself before oligo design.<br>
					<input type="hidden" name="passnucseq" value="$newnuc"><br>
					<input type="submit" name=".submit" value="Sequence Analysis" onclick="SeqAna();" /><-- for information about this sequence
					<br><br><input type="button" value="Back" onClick="history.go(-1)">
				</div>
EOM
		closer();
	}
	else
	{
		undef %chunk;
		$tar_chn_len = $per_chn_len; #this is for the magic oligo end numbers
		$tar_chn_len = ($nsize/2) if ($nsize <= 500);#($tar_chn_len+(.6*$tar_chn_len)));
		$tar_chn_len = $nsize     if ($nsize < 700);#($tar_chn_len+(.2*$tar_chn_len)));
		$tarmult   = .96*$tar_chn_len;  #ditto
		$limit    = int ($nsize/$tarmult)+1;

		$ver = -20;
		$start = 0;
	##-Actually make the chunk.  Then copy twice times, each time creating a different version number.
		for($x = 0; $x < 3; $x++)
		{	
			my $tno = new Chunk;
			$tno->ChunkSeq(substr($newnuc, $start));
			$tno->ChunkLength(length($tno->ChunkSeq));
			$tno->ChunkStart($start);
			$tno->ChunkNumber($ver);
			$tno->ChunkStop($nsize + 1);
			push @Chunks, $tno;
			$ver += 20;
		}
	##-Because this is a redo, we should only have one chunk.  	
	##-Actually make the oligos.  
		foreach $tiv (@Chunks)
		{
			$tar_chn_len = $per_chn_len;
			$tar_cur_dif = $tiv->ChunkLength - $tar_chn_len;
			my $cur_oli_num = $tar_oli_num;		my $cur_oli_len = $tar_oli_len;	my $cur_oli_gap = $tar_oli_gap;
			my $cur_oli_lap = $tar_oli_lap;		my $cur_chn_mel = $tar_chn_mel;
#		print "rev 0: tar_chn_len:$tar_chn_len\ttar_cur_dif:$tar_cur_dif\ttar_oli_num:$tar_oli_num\ttar_oli_len:$tar_oli_len\ttar_oli_lap:$tar_oli_lap\ttar_chn_mel:$tar_chn_mel\ttar_oli_gap:$tar_oli_gap\n";
			if (abs($tar_cur_dif) >= ($tar_oli_len+$tar_oli_gap))	##-if difference btw perfect and current is bigger than another pair of oligos, increment oli_num
			{
				$cur_oli_num = $tar_oli_num + (2 * int(($tar_cur_dif / ($tar_oli_len + $tar_oli_gap)) + .5 ));
				$tar_chn_len = ($cur_oli_num * ($tar_oli_gap + $tar_oli_lap)) + $tar_oli_lap;
				$tar_cur_dif = $tiv->ChunkLength - $tar_chn_len;
			}
			if (abs($tar_cur_dif) >= $cur_oli_num)					##-if difference can be spread equally across  oligos, increase length
			{
				$cur_oli_len = $tar_oli_len + int($tar_cur_dif / $cur_oli_num);
				$cur_oli_lap = $tar_oli_lap + int($tar_cur_dif / $cur_oli_num) if ($gapswit == 0);
				$tar_cur_dif = $tar_cur_dif - ($cur_oli_num * (int($tar_cur_dif / $cur_oli_num)));
			}

			if ($gapswit == 0)
			{
				$cur_oli_len = int((2* $tiv->ChunkLength) / ((2*$tar_chn_len) / $tar_oli_len));
				$cur_oli_lap = int($cur_oli_len * .5);
				$tar_cur_dif = $tiv->ChunkLength - ($cur_oli_num * $cur_oli_len * .5 + $cur_oli_lap);
				
			}
#				print "rev x per $tar_chn_len, dif $tar_cur_dif, num $cur_oli_num, len $cur_oli_len, lap $cur_oli_lap, mel $cur_chn_mel, gap $tar_oli_gap<br>";	
			if ($gapswit == 1)
			{
#					print "cur_oli_len: $cur_oli_len\tcur_oli_lap:$cur_oli_lap\ttar_cur_dif:$tar_cur_dif\n";
				$start = 0;
				my @Overlaps;
				for ($w = 1; $w <= $cur_oli_num; $w++)					##-difference now between 0 and abs(oli_num-1) - so in/decrement individual overlap lengths
				{
					$strlen = $w == 1	?	$cur_oli_len + $tiv->ChunkNumber	:	$w == $cur_oli_num	?	$cur_oli_len - $tiv->ChunkNumber	:	$cur_oli_len;
	##				$strlen = $cur_oli_len;
					$strlen++ if ( $w % $cur_oli_num < abs($tar_cur_dif) && $tar_cur_dif > 0);
					$strlen-- if ( $w % $cur_oli_num < abs($tar_cur_dif) && $tar_cur_dif < 0);
					push @Overlaps, substr($tiv->ChunkSeq, $start + $strlen - $cur_oli_lap, $cur_oli_lap) if ($w != $cur_oli_num);
					$start =  $start + $strlen - $cur_oli_lap;
				}
				@tree = map (melt($_, $mform), @Overlaps);
				$avg = 0;	foreach (@tree)	{	$avg += $_;	}	$avg = int(($avg / (@tree-0))+.5);
				$cur_chn_mel = $tar_chn_mel - .2*($tar_chn_mel-$avg) if ($avg < ($tar_chn_mel-10));	#Adjust target melting temp for reality.
				$start = 0;	$avg_chn_mel = 0; $avg_oli_len = 0;	my %Collisions; undef @begs; undef @ends;
				undef @Overlaps; my @Oligos;
				$tiv->ShrtOligo(200);	$tiv->LongOligo(0);	
				for ($w = 1; $w <= $cur_oli_num; $w++)					##-then make oligos, changing overlaps for melting temperature if appropriate
				{
					my $laplen = $cur_oli_lap;
					$strlen = $w == 1	?	$cur_oli_len + $tiv->ChunkNumber	:	$w == $cur_oli_num	?	$cur_oli_len - $tiv->ChunkNumber	:	$cur_oli_len;
					$strlen++ if ( $w % $cur_oli_num < abs($tar_cur_dif) && $tar_cur_dif > 0);
					$strlen-- if ( $w % $cur_oli_num < abs($tar_cur_dif) && $tar_cur_dif < 0);
					$laplen-- if ($strlen < $tar_oli_len && $cur_oli_len < 60);
	##		$strlen = $cur_oli_len + $tiv->ChunkNumber if ($w == 1);
					if ($w != $cur_oli_num)
					{
						$olap = substr($tiv->ChunkSeq, $start + $strlen - $laplen, $laplen);	$temp = melt($olap, $mform);
						while ($temp >= ($cur_chn_mel + $chn_mel_tol) && $strlen > $cur_oli_len)
						{
							$laplen--;	$strlen--;
							$olap = substr($tiv->ChunkSeq, $start + $strlen - $laplen, $laplen);	$temp = melt($olap, $mform);
						}
						while ($temp <= ($cur_chn_mel - $chn_mel_tol) && $strlen < $max_oli_len)
						{
							$laplen++;	$strlen++;
							$olap = substr($tiv->ChunkSeq, $start + $strlen - $laplen, $laplen);	$temp = melt($olap, $mform);
						}				
						push @Overlaps, $olap;
						$avg_chn_mel += $temp;
					}
#					print "w$w. start$start, $strlen, $laplen, ", $tiv->ChunkNumber, "<br>";
					$newoligo = substr($tiv->ChunkSeq, $start, $strlen);
#					print $newoligo, "<br>";
					push @Oligos, $newoligo;
					push @begs, $start;
					push @ends, $start + length($newoligo);
					$tiv->ShrtOligo(length($newoligo)) if length($newoligo) <= $tiv->ShrtOligo;
					$tiv->LongOligo(length($newoligo)) if length($newoligo) >= $tiv->LongOligo;
					$avg_oli_len += length($newoligo);
					$start =  $start + $strlen - $laplen;
#			$start = $start + $strlen - $tiv->ChunkNumber - $laplen, "<br>" if ($w == 3);
				}
				$tiv->AvgOlapMelt(int(($avg_chn_mel / (@Overlaps-0))+.5));
				$tiv->AvgOligoLength(int(($avg_oli_len / (@Oligos-0))+.5));
				for (my $w = 0; $w <= $cur_oli_num - 3; $w++)	{	$Collisions{$w} = $ends[$w] - $begs[$w+2]	if ($ends[$w] > $begs[$w+2]);	}
				$tiv->Collisions(\%Collisions);
				$tiv->Oligos(\@Oligos);
				$tiv->Olaps(\@Overlaps);
			}
			elsif ($gapswit == 0)
			{
				$starte = 0; $starto = $cur_oli_lap + 1 +$tiv->ChunkNumber;	$avg_chn_mel = 0;$avg_oli_len = 0;
				$tiv->ShrtOligo(200);	$tiv->LongOligo(0);	
				my @Overlaps; my @Oligos;
				for ($w = 1; $w <= $cur_oli_num; $w++)					##-difference now be between 0 and abs(oli_num-1) - so in/decrement individual overlap lengths
				{
					$strlen = $w == 1	?	$cur_oli_len + $tiv->ChunkNumber	:	$w == $cur_oli_num	?	$cur_oli_len - $tiv->ChunkNumber	:	$cur_oli_len;					
#					$strlen = $cur_oli_len;
					if ( $w <= abs(2 * $tar_cur_dif) && $tar_cur_dif > 0)	{$strlen++;}
					if ( $w <= abs(2 * $tar_cur_dif) && $tar_cur_dif < 0)	{$strlen--;}
					if ($w % 2 == 1)
					{
						push @Oligos, substr($tiv->ChunkSeq, $starte, $strlen);
						$starte = $starte + $strlen;
						push @Overlaps, substr($tiv->ChunkSeq, $starto, $starte - $starto);
						$avg_chn_mel += melt(substr($tiv->ChunkSeq, $starto, $starte - $starto), $mform);
					}
					if ($w % 2 == 0)
					{
						push @Oligos, substr($tiv->ChunkSeq, $starto, $strlen);
						$starto = $starto + $strlen;
						push @Overlaps, substr($tiv->ChunkSeq, $starte, $starto - $starte);
						$avg_chn_mel += melt(substr($tiv->ChunkSeq, $starte, $starto - $starte), $mform);
					}
					$tiv->ShrtOligo(length($Oligos[-1])) if length($Oligos[-1]) <= $tiv->ShrtOligo;
					$tiv->LongOligo(length($Oligos[-1])) if length($Oligos[-1]) >= $tiv->LongOligo;
					$avg_oli_len += length($Oligos[-1]);
				}
				$tiv->AvgOlapMelt(int(($avg_chn_mel / (@Overlaps-0))+.5));
				$tiv->AvgOligoLength(int(($avg_oli_len / (@Oligos-0))+.5));
				$tiv->Oligos(\@Oligos);
				$tiv->Olaps(\@Overlaps);
			}
		}
	##-Now for pretty output
		undef @oligomain;		
		$start = 1;
print <<EOM;
			<div id="notes">
				Your sequence has been broken into $y chunk(s) of approximately 740bp (each).<br>
				<br><em>What am I looking at?</em><br>
				<div>
					<div style="position:absolute; width:50%;">
						<img src="../../gd2/img/olkey1.gif" align="left";>
						<-- chunk number<br>
						<-- length of chunk<br>
						<-- average Tm of oligo overlaps in chunk<br>
						<-- number of oligos in chunk<br>
						<-- average oligo length, length of shortest and longest oligos<br><br>
						<-- restriction site at 3&lsquo; end (Rebase link)<br><br>
					</div>
					<div style="position:relative; text-align: right; left:40%; width:50%;">
						<img src="../../gd2/img/olkey2.gif" align="right";>
						sense strand 5&lsquo; to 3&lsquo; --><br>
						sense (5&lsquo; to 3&lsquo;) and antisense (3&lsquo; to 5&lsquo;) oligos --><br>
						antisense strand 3&lsquo; to 5&lsquo; -->
					</div>
				</div>
				<br><br><br><br><br>
				&nbsp;&nbsp;&bull;In the table, all oligos are 5&lsquo; to 3&lsquo;.  They are output 5&lsquo; to 3&lsquo; as well.<br>
				&nbsp;&nbsp;&bull;Tm is calculated a la Primer3.<br>
				See the <a href="../../gd2/Guide/olides.html" target="blank">manual</a> for more information.
			</div>
			<div>
				<form name="form2" method="post" action="./order.cgi">
EOM
		
		foreach $tiv (@Chunks)
		{
			$to = 0;		
			my $oliarrref = $tiv->Oligos;	my @oligoarr = @$oliarrref;
			my $olapref   = $tiv->Olaps;    my @olaparr = @$olapref;
			my $colhasref = $tiv->Collisions; my %colhas = %$colhasref; my @colkeys = keys %colhas;
			if (@colkeys-0 != 0)
			{
				print tab(6), "<div id = \"warn\">\n";
				print tab(7), "<strong>Warning:</strong> in the following chunk, there are ", @colkeys-0, " collisions.<br>\n";
				print tab(7), "Try increasing the Tm tolerance for assembly oligos to remove collisions.\n";
				print tab(6), "</div>";
			}
print <<EOM;				
					<div id = "gridgroup0">
						<div id = "chnum">
EOM
			print tab(8), "<strong>", $tiv->ChunkNumber, "</strong><br>\n", tab(8), $tiv->ChunkLength, " bp<br>\n", tab(8),	$tiv->AvgOlapMelt, 
				"&deg;<br>\n", tab(8),	@oligoarr-0, "<br>\n", tab(8), $tiv->AvgOligoLength, ".", $tiv->LongOligo, ".", $tiv->ShrtOligo, "<br>";
			print "\n", tab(8), break(2*(@oligoarr-0));
			print "\n", tab(8), "<a href=\"http://rebase.neb.com/rebase/enz/", $tiv->ThreePrimeEnz, ".html\" target=\"blank\">", $tiv->ThreePrimeEnz, "</a>\n", tab(7), "</div>\n";			
			print_oligos_aligned($tiv, $gapswit, 7);
print <<EOM;
						<br><br><br>
						<div id = "olgroup1" style = "background-color: \439AB;" width = "1000"><strong>
							<span id = "olnum">\43</span>
							<span id = "ollen">length</span>
							<span id = "olcos">start</span>
							<span id = "olcoe">stop</span>
							<span id = "olsen">sense</span>
							<span id = "ol5le">5&lsquo; overlap<br>length</span>
							<span id = "ol5me">5&lsquo; overlap<br>melt</span>
							<span id = "ol3le">3&lsquo; overlap<br>length</span>
							<span id = "ol3me">3&lsquo; overlap<br>melt</span>
							<span id = "olseq">sequence 5&lsquo; to 3&lsquo;</span>
							<br>&nbsp;</strong>
						</div>
EOM
			for (my $j = 0; $j < @oligoarr-0; $j++)
			{
				$olnum = $j+1;
				$ollen = length($oligoarr[$j]);
				$olstr = $start;
				$olend = $start + length($oligoarr[$j]) - 1;
				$olfol = ($j == 0)				?	0		:	length($olaparr[$j-1]);
				$oltol = ($j == @oligoarr-1)	?	0		:	length($olaparr[$j]);
				$olfme = ($j == 0)				?	undef	:	int(melt($olaparr[$j-1], $mform) + .5);
				$oltme = ($j == @oligoarr-1)	?	undef	:	int(melt($olaparr[$j], $mform) + .5);
				if ($j % 2 == 0)		{	$olseq = $oligoarr[$j];					$olsen = "+";										}
				if ($j % 2 == 1)		{	$olseq = complement($oligoarr[$j], 1);	$olsen = "-"; ($olstr, $olend) = ($olend, $olstr);	}
				$color = ($j % 2)	?	"ABC"	:	"CDE"	;
print <<EOM;
						<div id = "olgroup1" style = "background-color: \43$color;">
							<span id = "olnum">$olnum</span>  
							<span id = "ollen">$ollen</span>
							<span id = "olcos">$olstr</span>
							<span id = "olcoe">$olend</span>
							<span id = "olsen">$olsen</span>
							<span id = "ol5le">$olfol</span>
							<span id = "ol5me">$olfme</span>
							<span id = "ol3le">$oltol</span>
							<span id = "ol3me">$oltme</span>
							<span id = "olseq">$olseq</span>
							&nbsp;&nbsp;<br>&nbsp;
						</div>
EOM
				$start = $start + length($oligoarr[$j]) - length($olaparr[$j]);
				push @oligomain, $olseq;
			}
			$start = $start - $tiv->ThreePrimeOlap;
print <<EOM;
					</div>
					<br><br><br>
EOM
		}
	}
}