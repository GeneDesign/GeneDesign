#!/usr/bin/perl

use File::Find;
use CGI;
use PRISM;
use RESite;
use PMLol;

$query = new CGI;
print $query->header;
	print ("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">\n");
	print ("<html>\n<head>\n<meta http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\">\n");
	print ("<link href=\"../../gd/acss/re.css\" rel=\"stylesheet\" type=\"text/css\">\n");	
	print ("<link href=\"../../gd/acss/ol.css\" rel=\"stylesheet\" type=\"text/css\">\n");	
	print ("<link href=\"../../gd/acss/", cssbrowser(), ".css\" rel=\"stylesheet\" type=\"text/css\">\n") if (cssbrowser() ne '');
	print ("<script src=\"../../gd/scripts.js\" type=\"text/javascript\" language=\"Javascript\"></script>\n");
	print ("<META NAME=\"robots\" CONTENT=\"noindex, nofollow, noarchive\">\n");
	print ("<title>GeneDesign: Oligo Design</title></head>\n");
print <<EOM;
<script type="text/javascript">
var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
</script>
<script type="text/javascript">
try {
var pageTracker = _gat._getTracker("UA-9136796-1");
pageTracker._trackPageview();
} catch(err) {}</script>
EOM
	print ("<body><div id=\"bigbox\">\n");
	print ("<div id=\"toppa\"><a href=\"../../gd/index.html\"><img src=\"../../gd/img/gdlogobanner.gif\" align = \"absmiddle\"></a>\n");
	print ("<a class=\"headli\">Oligo Design</a></div>");
	print $query->startform(-method=>'post', -action=>'./gdOlides.cgi', -name=>"form1");


if ($query->param('ovmel') eq '')
{
	print ("<div id=\"notes\">");
	print ("<strong>To use this module you need a nucleotide sequence at least 60bp long, a target melting temperature, and a target oligo length.</strong><br>\n");
	print ("Your nucleotide sequence will be searched for unique restriction sites, which will be used to divide the sequence into chunks of approximately 500bp.<br>");
	print ("If your sequence is less than 600 bp, there will only be one chunk.<br><em>Please Note:</em><br> ");
	print space(2), ("&bull;Chunk overlap refers to how many bp will be shared in adjacent chunks.  For instance, with a 20bp chunk overlap, if a 6bp cutter \n");
	print ("is chosen as a joint it will be padded by 7bp on either side.  Those twenty bp will be in each chunk. <br>");
	print space(2), ("&bull;The melting temperature you define is the most important criteria.  Oligo lengths in practice will decrease or increase to match. <br>\n");
	print ("See the <a href=\"../../gd/Guide/olides.html\" target=\"blank\">manual</a> for more information.\n");
	print ("</div>");
	$nucseq = $query->param('passnucseq') if ($query->param('passnucseq') ne '');
	$nucseq = $query->param('nucseq') if ($query->param('passnucseq') eq '');
	print ("<div id=\"gridgroup0\">\nYour nucleotide sequence:<br>\n");
	print $query->textarea(-name=>'newnucseq', -rows=>6, -columns=>100, -default=>$nucseq), break(1);
	print "Target Oligo Length: ", $query->popup_menu(-name=>'ollen', -values=>[qw/40 50 60 80 100/], -default=>'60'), "bp\n", space(3);
	print "Overlap Melting Temperature: ", $query->textfield(-name=>'ovmel', -default=>'56', -size=>2, -maxlength=>2), "&deg;\n", space(3);
	print "Chunk Overlap ", $query->textfield(-name=>'whflank', -default=>'20', -size=>2, -maxlength=>2), "bp\n";
	print ("<div id=\"gridgroup1\" align =\"center\" style=\"position:absolute; top:150; \">\n");
	print $query->submit(-value=>" Design Oligos ");
	print ("<input type=\"hidden\" name=\"skipall\" value=\"yes\">\n</div>\n</div>\n");
	print $query->endform, $query->end_html;
} 
elsif($query->param('newnucseq') ne '')
{
	$newnuc  = cleanup($query->param('newnucseq'), 1);
	$aaseq   = $query->param('aaseq') if ($query->param('skipall') == '');
	$aaseq   = translate($newnuc) if ($query->param('skipall') eq 'yes');
	$cuslen  = $query->param('ollen');	#default is 60bp
	$cusmel  = $query->param('ovmel');	#default is 60û
	$mform   = 6;
	$flank   = .5 * $query->param('whflank');
	$nsize   = length($newnuc);

####PRE ERROR CHECK - pass only if sequence to be oligo-ed is an appropriate length
	if ( $nsize < 60)
	{
		print ("<div id=\"notes\">");
		print ("Your nucleotide sequence is only $nsize bp.<br>");
		print "A sequence of this length (less than 60bp) can be ordered as a single oligo.<br>";
		print $query->hidden(-name=>'passnucseq', value=>$newnuc);
		print break(1), "Take this sequence to ", $query->submit(-value=>'Sequnce Analysis', -onclick=>'SeqAna();');
		print break(2), ("<input type=\"button\" value=\"Back\" onClick=\"history.go(-1)\">");
		print ("</div></form>\n</div>\n</body>\n</html>\n");
	}
	elsif ($nsize > 17000)
	{
		print ("<div id=\"notes\">");
		print ("Your nucleotide sequence is $nsize bp.<br>");
		print "We will run out of unique restriction sites before we are able to finish this design.<br>";
		print "It is recommended that you break this sequence up further yourself before oligo design.<br>";
		print $query->hidden(-name=>'passnucseq', value=>$newnuc);
		print break(1), "Take this sequence to ", $query->submit(-value=>'Sequnce Analysis', -onclick=>'SeqAna();');
		print break(2), ("<input type=\"button\" value=\"Back\" onClick=\"history.go(-1)\">");
		print ("</div></form>\n</div>\n</body>\n</html>\n");
	}
	else
	{
		undef %chunk;
		$defchunk = 500;
		$tarchunk  = $defchunk; #this is for the magic oligo end numbers
		$tarchunk = ($nsize/2) if ($nsize <= 800);#($tarchunk+(.6*$tarchunk)));
		$tarchunk = $nsize     if ($nsize < 501);#($tarchunk+(.2*$tarchunk)));
		$tarmult   = .96*$tarchunk;  #ditto
		$limit    = int ($nsize/$tarmult)+1;
##-load up the enzymes, exclude blunts, 1bp overhangs and outside cutters
		@cutters = siteload();
		$y = 0;
		foreach $n (@cutters)
		{
			$SitArr[$y] = new RESite();
			$SitArr[$y]->CutterName($n);
			$SitArr[$y]->LoadInfo();
			$y++;
		}
		@SitArr = grep {$_->Sticky ne '' } @SitArr;
		@SitArr = grep {$_->CompareEnds()} @SitArr;
		@SitArr = grep {$_->CompareCut ()} @SitArr;
		@finarr = map ($_->CutterName, @SitArr);
	##-Figure out what the unique sites are
		foreach $f (@finarr)
		{
			@temp = siteseeker($f, $newnuc);
			$site = $temp[0] + sitelength($f) + $flank;
			$borders{$f} = $site if (@temp-0 == 1);
			$sredrob{$site} = $f if (@temp-0 == 1);
		}

####PRE ERROR CHECK - pass only if sequence to be oligo-ed contains a decent number of spaced unique sites
		@sredkeys = keys %sredrob;
		@sredvals = values %sredrob;
	if (@sredkeys-0 < $limit)
	{
		print ("<div id=\"notes\">");
		print ("Your nucleotide sequence doesn't seem to contain enough unique sites.<br> I can only find @sredvals<br>");
		print "There are ", @sredvals-0, ", and I need at least $limit.<br>";
		print "I suggest taking this sequence through Silent Site Insertion.  An interval of 167 amino acids is usually sufficient to populate a sequence for oligo design.";
		print $query->hidden(-name=>'passnucseq', value=>$newnuc);
		print break(1), "Take this sequence to ", $query->submit(-value=>'Silent Site Insertion', -onclick=>'SSIns();');
		print break(2), ("<input type=\"button\" value=\"Back\" onClick=\"history.go(-1)\">");
		print ("</div></form>\n</div>\n</body>\n</html>\n");
	}
else
{

##-Pick sites on the target chunk interval (modular swing)
	if ($nsize > ($tarchunk+(.2*$tarchunk)))
	{
		$n = 0;
		$target = $tarchunk;
		$tcv = 0;
		while ($target < ($limit*$tarmult))
		{
			$target = ($target + $n) if ($n % 2 == 0);
			$target = ($target - $n) if ($n % 2 != 0);
			$n++;
			if (exists ($sredrob{$target}))
			{
				$chosen{$sredrob{$target}} = $target;
				$oldtarget = $target;
				$tcv++;
				$target = $target - $flank - $flank - sitelength($sredrob{$target}) + $tarchunk;
				$n = 0;
			}
			last if ($tarchunk < $defchunk && $tcv == 1);
			last if ($nsize - $target <= ($tarchunk-(.5*$tarchunk)));
		}
	}
	$y = 0;
	$start = 0;
##-Actually make the chunks, including the left over chunk
	foreach $t (sort {$chosen{$a} <=> $chosen{$b}}keys %chosen)
	{
		$chunk{$y} = substr($newnuc, $start, $chosen{$t} - $start-1);
		$len = length($chunk{$y});
		$start = $chosen{$t} - 2*$flank - 1 - sitelength{$t};
		$lastpos = $chosen{$t};
		@joint[$y] = ([$y, $t, $chosen{$t}, $len]);
		push @joenz, $t;
		$y++; 
	}
	$chunk{$y} = substr($newnuc, $start);
#	for ($r = $i; $r < $y; $r++)
#	{
#		print "$joint[$r][0], $joint[$r][1], $joint[$r][2], $joint[$r][3]<br>";
#	}
##-Fill out Master, make the oligos out of each chunk
	foreach $m (sort {$a <=> $b} keys %chunk)
	{	
		$tarchunk = $defchunk;
		$tarlap	= 20;					# these are the defaults, 12 60mers with 20bp overlaps and 20bp gaps
		$tarlen	= $cuslen;				
		$targap	= $tarlen-(2*$tarlap);				        # length = 2*(overlap) + gap
		$tarnum = ($tarchunk-$tarlap) / ($tarlen-$tarlap);	# num = ( (chunk-overlap) / (length-overlap) )
	##-figure out the length difference between chunk and ideal chunk
		$lenchunk = length($chunk{$m});
		$diff = $lenchunk-$tarchunk;
	##-if that difference is bigger than what it takes to add another pair of oligos, increment number and renew difference
		$num = $tarnum;
		while (abs($diff) >= ($tarlen+$targap))
		{
			$mult = int($diff/($tarlen+$targap));
			$num = $tarnum + (2*$mult);
			$tarchunk = $tarchunk + ($mult*($tarlen+$targap));
			$diff = $lenchunk - $tarchunk;
		}
	##-if that difference can be spread equally across the oligos, increase length and renew difference
		$len = $tarlen;
		if (abs($diff) >= $num)
		{
			$len = $tarlen + int($diff/$num);
			$diff = $diff - ($num * (int($diff/$num)));
		}
	##-that difference should now be between 0 and abs(number-1) - so figure out the oligos and add one to the length appropriately
	##-then extend overlaps for melting temperature
		$start = 0;
		undef @olbps;
		undef @oltes;
		for ($w = 1; $w <= $num; $w++)
		{
			$lap = $tarlap;
			$strlen = $len;
			$strlen++ if ( $w % 12 < abs($diff) && $diff > 0);
			$strlen-- if ( $w % 12 < abs($diff) && $diff < 0);
			if ($w != $num)
			{
				$olbp = substr($chunk{$m}, $start+$strlen-$lap, $lap);
				push @oltes, $olbp;
			}
			$start =  $start+$strlen-$lap;
		}
		$start = 0;
		@tree = map (melt($_, $mform), @oltes);
		$avg = 0;
		foreach (@tree)
		{
			$avg += $_;
		}
		$avg = int($avg / (@tree-0));
		$curmel = $cusmel;
		$curmel = $cusmel - .2*($cusmel-$avg) if ($avg < ($cusmel-10) && $mform == 6);
		$allow = 2; 
		my @olaps;
	#variables for overlap checking:
		undef @begs; undef @ends; undef @long;
		$tempy = 0; $longa = 0; $short = 200; $longe = 0;
		for ($w = 1; $w <= $num; $w++)
		{
			$lap = $tarlap;
			$strlen = $len;
			$strlen++ if ( $w % 12 < abs($diff) && $diff > 0);
			$strlen-- if ( $w % 12 < abs($diff) && $diff < 0);
			$lap-- if ($strlen < $cuslen && $cuslen < 60);
			if ($w != $num)
			{
				$olap = substr($chunk{$m}, $start+$strlen-$lap, $lap);
				$temp = melt($olap, $mform);
				while ($temp >= ($curmel + $allow) && $cuslen >= 60)
				{
					$lap--;
					$strlen--;
					$olap = substr($chunk{$m}, $start+$strlen-$lap, $lap);
					$temp = melt($olap, $mform);
				}
				while ($temp <= ($curmel - $allow) && $cuslen >= 60)
				{
					$lap++;
					$strlen++;
					$olap = substr($chunk{$m}, $start+$strlen-$lap, $lap);
					$temp = melt($olap, $mform);
				}				
				push @olaps, $olap;
				$tempy += $temp;
			}
			$avtemp = int(($tempy /((@olaps)-0))+.5);
			$oligo = substr($chunk{$m}, $start, $strlen);
			push @$m, $oligo;
			push @begs, $start;
			push @ends, $start+length($oligo);
			push @long, length($oligo);
			$longa += length($oligo);
			$short = length($oligo) if length($oligo) < $short;
			$longe = length($oligo) if length($oligo) > $longe;
			$start =  $start+$strlen-$lap;
		}
		$avlen = int(($longa / ((@long)-0))+.5);
	#check for collisions
		my $colli = 0; my @colly;
		for ($w = 0; $w <= $num-3; $w++)
		{
			$colli++ if ($ends[$w] > $begs[$w+2]);
			push @colly, $w+1 if ($ends[$w] > $begs[$w+2]);
			push @coamt, $ends[$w]-$begs[$w+2] if ($ends[$w] > $begs[$w+2]);
		}
		
		my @ero = @$m;
		@master[$m] = ([$m, $num, $len, $diff, $chunk{$m}, \@olaps, \@ero, $avtemp, \@coamt, \@colly, $avlen, $short, $longe]);
					#   0     1    2        3    4            5         6       7     8        9	   10		11		12
	}
	print ("<div id=\"notes\">");
	print ("Your sequence has been broken into ", $y+1, " chunk(s) of approximately 500bp (each).<br>");
	print ("<br><em>What am I looking at?</em><br> ");
	print ("<div><div style=\"position:absolute; width:50%;\"><img src=\"../../gd/img/olkey1.gif\" align=\"left\";>"), break(1);
	print ("<-- chunk number<br><-- length of chunk<br><-- average Tm of oligo overlaps in chunk<br><-- number of oligos in chunk<br>");
	print ("<-- average oligo length, length of shortest and longest oligos<br><br><-- restriction site at 3' end (Rebase link)<br><br></div>");
	print ("<div style=\"position:relative; text-align: right; left:40%; width:50%;\"><img src=\"../../gd/img/olkey2.gif\" align=\"right\";>"), break(1);
	print ("sense strand 5' to 3' --><br>sense (5' to 3') and antisense (3' to 5') oligos --><br>antisense strand 3' to 5' --></div></div>");
	
	
	print break(5), space(2), ("&bull;In the table, all oligos are 5' to 3'.  They are output 5' to 3' as well.<br>");
	print space(2), ("&bull;The three Tms in the table represent the results of three different formulas.<br>\n");
	print ("See the <a href=\"../../gd/Guide/olides.html\" target=\"blank\">manual</a> for more information.\n");
	print ("</div>");	
	
##-Now for pretty output
	print ("<div>\n");
	undef @oligomain;
	print (" <form name=\"form2\" method=\"post\" action=\"./order.cgi\">\n");
##-draw the chunk box
	$start = 1;
	for ($r = 0; $r <= $y; $r++)
	{
		$j = 0;
		$to = 0;
	##-chunk warnings - oligo collisions? (maybe later: significant deviations in length from user input?)
		my @collided = @{$master[$r][9]}; my @comt = @{$master[$r][8]}; my %colled;
		if (@collided-0 != 0)
		{
		for ($he = 0; $he <= @collided-0; $he++)
		{
			$colled{$collided[$he]-1} = $comt[$he];
		} 
			#convert two arrays into hash for coloring the actual oligos later
			print ("<div id = \"warn\">\n");
			if (@collided-0 == 1)
			{
				print ("<strong>Warning:</strong> in the following chunk, there is a collision.  Oligo \43@collided collides with its downstream neighbor.");
			}
			else
			{
				print ("<strong>Warning:</strong> in the following chunk, there are ", @collided-0, " collisions. Oligos ");
				while ($to < (@collided-1))
				{
				print "$collided[$to], "; $to++ ;
				}
				print "and $collided[$to] collide with their downstream neighbors.";  
			}
			print " Overlapping bases are printed in red.";
			print ("</div>");
		}
	##-chunk information
		@tolap = @{$master[$r][5]};
		@tolig = @{$master[$r][6]};
		print ("<div id = \"gridgroup0\">\n");
		print ("<div id = \"chnum\"><strong>", $r+1, "</strong><br>");
		print length($master[$r][4]), " bp", break(1), $master[$r][7], "&deg;", break(1), @tolig-0, break(1), "$master[$r][10].$master[$r][11].$master[$r][12]", break((2*$master[$r][1]));
		print break(1) if ($r == $y);
		print break(1) if (cssbrowser() eq 'ff');
		print break(4) if (cssbrowser() eq 'wie');
		print ("<a href=\"http://rebase.neb.com/rebase/enz/$joint[$r][1].html\" target=\"blank\">");
		print ("$joint[$r][1]</a></div>\n");
	##-lineups of DNA for visual confirmation
		print ("<div id = \"oligo\">$master[$r][4]<br>\n\n");

		$len = $master[$r][2];
		for ($w = 0; $w <= ($master[$r][1]); $w+=2)
		{
			if (!exists($colled{$w}) && !exists($colled{$w-2}))
			{
				print $tolig[$w], space(length($tolig[$w+1])-(length($tolap[$w])+length($tolap[$w+1])));
			}
			else
			{
				$prev = 0; $foll = $colled{$w};
				if (exists($colled{$w-2}) && $w != 0) #previous one collided - draw first bases in red
				{
					print "<font color =\"\43FF0000\">", substr($tolig[$w-2], length($tolig[$w-2])-$colled{$w-2}), "</font>";
					$prev = $colled{$w-2};
				}
				print substr($tolig[$w], $prev, (length($tolig[$w])-$foll-$prev));
				print space(length($tolig[$w+1])-(length($tolap[$w])+length($tolap[$w+1]))) if (!exists($colled{$w}) && $w != $master[r][1]-1);
			}
		}
		print break(1), space(length($tolig[0])-length($tolap[0]));
		for ($w = 1; $w <= ($master[$r][1]); $w+=2)
		{
			if (!exists($colled{$w}) && !exists($colled{$w-2}))
			{
				print complement($tolig[$w]), space(length($tolig[$w+1])-(length($tolap[$w])+length($tolap[$w+1])));
			}
			else
			{
				$prev = 0; $foll = $colled{$w};
				if (exists($colled{$w-2}) && $w != 1) #previous one collided - draw first bases in red
				{
					print "<font color =\"\43FF0000\">", complement(substr($tolig[$w-2], length($tolig[$w-2])-$colled{$w-2})), "</font>";
					$prev = $colled{$w-2};
				}
				print complement(substr($tolig[$w], $prev, (length($tolig[$w])-$foll-$prev)));
				print space(length($tolig[$w+1])-(length($tolap[$w])+length($tolap[$w+1]))) if (!exists($colled{$w}))
			}
		}
		print break(1), "\n\n", complement($master[$r][4]), "</div>", break(3);
		print break(1) if (cssbrowser() eq 'ff' || cssbrowser() eq 'wie');
	##-oligos in rows for melt temperature array and length
		print ("\n<div id = \"olgroup1\" style = \"background-color: \439AB;\" width = \"1000\"><strong>\n");
		print ("<span id = \"olnum\">#</span>              <span id = \"ollen\">length</span>\n");
		print ("<span id = \"olcos\">start</span>               <span id = \"olcoe\">stop</span>\n");
		print ("<span id = \"olsen\">sense</span>               <span id = \"ol5le\">5' overlap<br>length</span>\n");
		print ("<span id = \"ol5me\">5' overlap<br>melt</span>  <span id = \"ol3le\">3' overlap<br>length</span>\n");
		print ("<span id = \"ol3me\">3' overlap<br>melt</span>  <span id = \"olseq\">sequence 5' to 3'</span>\n");
		print ("<br>&nbsp;</strong></div>\n");
		for ($w = 0; $w < ($master[$r][1]); $w++)
		{
			$olnum = $w+1;
			$ollen = length($tolig[$w]);
			$olstr = $start;
			$olend = $start + length($tolig[$w]);
			if ($w == 0)
			{
				$olfol = 0; @olfme = undef;
			}
			else
			{
				$olfol = length($tolap[$w-1]);
				@olfme = melt($tolap[$w-1]);
			}
			if ($w == $master[$r][1]-1)
			{
				$oltol = 0; @oltme = undef;
			}
			else
			{
				$oltol = length($tolap[$w]);
				@oltme = melt($tolap[$w]);
			}
			if ($w % 2 == 0)
			{
				$olseq = $tolig[$w];
				$olsen = "+";
			}
			elsif ($w % 2 == 1)
			{
				$olseq = complement($tolig[$w], 1);
				$olsen = "-";
				$oltemp = $olstr;
				$olstr = $olend;
				$olend = $oltemp;
			}
			$start = $start + length($tolig[$w]) - length($tolap[$w]);
			$color = "ABC" if ($j % 2 );
			$color = "CDE" if ($j % 2 == 0);
			print ("\n<div id = \"olgroup1\" style = \"background-color: \43$color;\">\n");
			print ("<span id = \"olnum\">$olnum</span>  <span id = \"ollen\">$ollen</span>\n");
			print ("<span id = \"olcos\">$olstr</span>  <span id = \"olcoe\">$olend</span>\n");
			print ("<span id = \"olsen\">$olsen</span>  <span id = \"ol5le\">$olfol</span>\n");
			print ("<span id = \"ol5me\">@olfme</span>  <span id = \"ol3le\">$oltol</span>\n");
			print ("<span id = \"ol3me\">@oltme</span>  <span id = \"olseq\">$olseq</span>\n");
			print ("&nbsp;&nbsp;<br>&nbsp;</div>\n");
			$j++;
			push @oligomain, $olseq;
		}
		$start = $start - ( $joint[$r][2] - ($joint[$r+1][2] - $joint[$r+1][3]));
	print "</div>", break(2);	
	}
	print "<br></div><br>";
	print ("<div id=\"notes\">");
	print ("Now you can see an order form containing the oligos or view a full report on the design process.<br>");
	print "Designation string for oligos: \n ", $query->textfield(-name=>'oldesig', -size=>10, -maxlength=>10), space(3);
	print "Separation character:\n", $query->popup_menu(-name=>'sepchar', -values=>[qw/tab comma space underscore/], -default=>'tab'), "<br>";
	print ("<br><input type=\"submit\" value=\"&nbsp;An Order Form, Please&nbsp;\" onClick=\"OrderForm()\">\n  <-- Just the Oligos in a text file\n");
	print ("<br><input type=\"submit\" value=\"&nbsp;Full Report&nbsp;\" onClick=\"ReportForm()\">\n  <-- Complete Report on Sequence and Modifications<br>&nbsp;<br>\n");
	print ("</div>");
	print ("  <div id=\"gridgroup1\" align =\"center\" style=\"position:absolute; top:$top; \">\n");
	print ("  <input type =\"hidden\" name=\"codons\" value=\"", $query->param('codons'), "\">\n");
	print ("   <input type=\"hidden\" name=\"enzcrit\" value=\"", $query->param('enzcrit'), "\">\n");
	print ("  <input type =\"hidden\" name=\"vecname\" value=\"", $query->param('vecname'), "\">\n");
	print ("  <input type =\"hidden\" name=\"absents\" value=\"", $query->param('absents'), "\">\n");
	print ("  <input type =\"hidden\" name=\"inte\" value=\"", $query->param('inte'), "\">\n");
	print ("  <input type =\"hidden\" name=\"actu\" value=\"", $query->param('actu'), "\">\n");
	print ("  <input type =\"hidden\" name=\"insert\" value=\"", $query->param('insert'), "\">\n");
	print ("  <input type =\"hidden\" name=\"remove\" value=\"", $query->param('remove'), "\">\n");
	print ("   <input type=\"hidden\" name=\"nucseq\" value=\"$newnuc\">\n");
	print ("   <input type=\"hidden\" name=\"olarray\" value=\"@oligomain\">\n");
	print ("   <input type=\"hidden\" name=\"joenz\" value=\"@joenz\">\n");
	print ("   <input type=\"hidden\" name=\"aaseq\" value=\"$aaseq\">\n");
	print ("  <input type =\"hidden\" name=\"ollen\" value=\"", $query->param('ollen'), "\">\n");
	print ("  <input type =\"hidden\" name=\"ovmel\" value=\"", $query->param('ovmel'), "\">\n");
	print ("  <input type =\"hidden\" name=\"whtemp\" value=\"", $query->param('whtemp'), "\">\n");
	print ("  <input type =\"hidden\" name=\"whflank\" value=\"", $query->param('whflank'), "\">\n");
	print (" </form>\n</div>\n</body>\n</html>\n");
}
}
}
