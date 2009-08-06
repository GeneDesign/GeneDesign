#!/usr/bin/perl

use PRISM;
use CGI;
use RESite;
use PMLol;
$query = new CGI;
print $query->header;
	print ("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">\n");
	print ("<html>\n<head>\n<meta http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\">\n");
	print ("<link href=\"../../gd/acss/re.css\" rel=\"stylesheet\" type=\"text/css\">\n");	
	print ("<link href=\"../../gd/acss/", cssbrowser(), ".css\" rel=\"stylesheet\" type=\"text/css\">\n") if (cssbrowser() ne '');
	print ("<script src=\"../../gd/scripts.js\" type=\"text/javascript\" language=\"Javascript\"></script>\n");
	print ("<META NAME=\"robots\" CONTENT=\"noindex, nofollow, noarchive\">\n");
	print ("<title>GeneDesign: Silent Site Removal</title></head>\n");
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
	print ("<a class=\"headli\">Silent Site Removal</a></div>");
	print $query->startform(-method=>'post', -action=>'./gdSSRem.cgi', -name=>"form1");

if ($query->param('org') eq '')
{
	print ("<div id=\"notes\">");
	print ("<strong>To use this module you need a nucleotide sequence.  An organism name is optional.</strong><br>\n");
	print ("Your nucleotide sequence will be searched for restriction sites and you will be prompted to choose as many as you want for removal.<br>");
	print ("Sites will be removed without changing the amino acid sequence by changing whole codons.<br><em>Please Note:</em><br> ");
	print space(2), ("&bull;If you select an organism, targeted codons will be replaced with the codon that enjoys the most optimal expression in that organism.<br>");
	print space(2), ("&bull;If you select no optimization, targeted codons will be replaced with a random codon.<br>\n");
	print ("See the <a href=\"../../gd/Guide/ssr.html\" target=\"blank\">manual</a> for more information.\n");
	print ("</div>");
	$nucseq = $query->param('passnucseq') if ($query->param('passnucseq') ne '');
	$nucseq = $query->param('nucseq') if ($query->param('passnucseq') eq '');
	%organism = (0=> 'No Optimization', 1 => 'H. sapiens', 2 => 'S. cerevisiae', 3 => 'E. coli', 5 => 'C. elegans' );# 4 => 'M. musculus');
	print ("<div id=\"gridgroup0\">\nYour nucleotide sequence:<br>\n");
	print $query->textarea(-name=>'nuseq', -rows=>6, -columns=>100, -default=>$nucseq), break(1);
	print "Target Organism: ", $query->popup_menu(-name=>'org', -values=>\%organism, -default=>0), "\n", space(3);
	print ("<div id=\"gridgroup1\" align =\"center\" style=\"position:absolute; top:150; \">\n");
	print $query->submit(-value=>" Next Step: which sites are present? ");
	print ("</div>\n</div>\n");
	print $query->endform, $query->end_html;
}
elsif ($query->param('org') ne '' && $query->param('removeme') eq '')
{
	$nucseq = $query->param('passnucseq') if ($query->param('passnucseq') ne '');
	$nucseq = cleanup($query->param('nuseq')) if ($query->param('passnucseq') eq '');
	$nucseq = $query->param('nucseq') if (!$query->param('passnucseq') && !$query->param('nuseq'));

	$org = $query->param('org');
	print ("<div id=\"notes\">");
	print ("Below are your nucleotide sequence and all of the restriction sites that I recognized. Your current organism is ");
	print organism($org), "<br>";
	print ("Check as many as you like for removal.<br>\n");
	print ("See the <a href=\"../../gd/Guide/ssr.html\" target=\"blank\">manual</a> for more information.\n");

	print ("</div>");
	$organism = $query->param('org');
	@presentnames = sort(siterunner(3, $nucseq));
	foreach $r (@presentnames)
	{
		$presents{$r} = (siteseeker($r, $nucseq)-0);
	}
	$num = @presentnames-0;
	$curpos = 0;  $starta = 0; $xpos = 0; $ypos = 0;
	print ("<div id=\"gridgroup0\">\nThis is your nucleotide sequence:<br>\n");
	print $query->textarea(-name=>'nucseq', -rows=>6, -columns=>120, -default=>$nucseq, -readonly=>'true'), break(2);
	print "Present Restriction Sites:<br>";
	print "<div id=\"gridgroup2\">\n";
	for ($x = 0; $x <= int($num/10); $x++)
	{
		while ($curpos != 10 && $starta < $num)
		{
			print ("<div id = \"brubox\" style = \"top:$ypos; left:$xpos;\">");
			print ("<input type=\"checkbox\" name=\"removeme\" value=\"$presentnames[$starta]\">");
			print ("<a href=\"http://rebase.neb.com/rebase/enz/", $presentnames[$starta], ".html\" target=\"blank\">");

			print $presentnames[$starta], "</a> (", $presents{$presentnames[$starta]}, ")</div>\n";
			$curpos++; $starta++; $xpos+=95;
		}
		$curpos = 0; $ypos +=20; $xpos = 0;
	}
	print "</div>";
	print break (25);
	print $query->hidden(-name=>'starta', -value=>$starta), $query->hidden(-name=>'org', -value=>$organism);
	print $query->submit(-value=>" Next Step: Remove these sites ");
	$query->hidden(-name=>'org', value=>$org);
	print ("</div></div>\n\n", $query->endform, $query->end_html);
}
else
{

	$nucseq = cleanup($query->param('nucseq'), 0);
	$oldnuc = $nucseq;
	$len = length($nucseq);
	@aa = split('', translate($nucseq));
	@nuc = split('', $nucseq);
	$org = $query->param('org');
	@removees = $query->param('removeme');
	for ($tcv = 0; $tcv <= 2; $tcv++)
	{
		foreach $t (@removees)
		{	
			push @Error2, $t;
			@$t = siteseeker($t, $nucseq);
			foreach $v (@$t)
			{
				$remaa = ''; $remnt = '';
				$start = $v-1; 
				while (($start % 3) != 0)
				{ 						
					$start--;
				}
				$stop = $start + sitelength($t)-1;
				for ($b = ($start/3); $b <= ($stop/3); $b++)
				{
					$remaa .= $aa[$b];
				}
				for ($b = $start; $b <= $stop; $b++)
				{
					$remnt .= $nuc[$b];
				}
				while (length($remnt) % 3 != 0 )
				{
					#$b++;
					$remnt .= $nuc[$b];	##-make sure you have nucs in threes
					$b++;
				}
		#		print " FLAG " if ($remaa ne translate($remnt));
				$rmseq = changeup($remnt, 2, $org);
		#		print "$t, $v, $remnt, $rmseq, $remaa<br>";
				$changeit{$start} = $rmseq;
			}
			$curpos = 0; $newnuc = ''; 		
			foreach $c (sort {$a <=> $b }keys %changeit)
			{
				$newnuc .= substr ( $nucseq, $curpos, ($c-$curpos)) . $changeit{$c};
				$curpos = length($newnuc);
			}	
			$newnuc .= substr ($nucseq, $curpos);	
			$nucseq = $newnuc; %changeit = undef;	
		}
	}

	foreach $y (@removees)
	{
		push @Error4, $y if (siteseeker($y, $newnuc)-0 != 0);
	#h	print "$y, ", siteseeker($y, $newnuc), "<br>";
	}
	print ("<div id=\"notes\">");
	print "\nI was asked to remove ";
	foreach $e (@removees)
	{
		print "$e (", (siteseeker($e, $oldnuc)-0), ") ";
	}
	print break(1);
	if (@Error4-0 >0)
	{ 
		print "\n<br>But after three iterations, I couldn't remove ";
		foreach $e (@Error4)
		{
			print "$e (", (siteseeker($e, $newnuc)-0), ") ";
		}
		print break(1);
	}
	print "\There were no problems kicking sites out." if (@Error4-0 == 0);
	print "</div>"; 
	print break(1);
	print ("<div id=\"gridgroup0\">Your altered nucleotide sequence:\n");
	print $query->textarea(-name=>'nuseq', -rows=>6, -columns=>120, -default=>$newnuc), break(1);
	@newal = ezalign($oldnuc, $newnuc);
		@bcou = count($newnuc); 
	$GC = int(((($bcou[3]+$bcou[2])/$bcou[8])*100)+.5);
	$AT = int(((($bcou[0]+$bcou[1])/$bcou[8])*100)+.5);

	print "Your new sequence has $newal[0] identites, $newal[1] changes, and is $newal[4]% identical to the original sequence.<br>Composition : $GC% GC, $AT% AT</div>", break(3);
		print ("<div id=\"gridgroup1\" align =\"center\" style=\"position:relative \">\n");
	print $query->hidden(-name=>'passnucseq', value=>$newnuc);
	print $query->hidden(-name=>'org', value=>$org);
	print ("<div id=\"notes\" style=\"text-align:center;\">");
	print ("You can take this nucleotide sequence to another module now.");
	print ("</div>");	
	print break(1), "<strong>Take this sequence to</strong>";
	print break(1), $query->submit(-value=>'Silent Site Insertion', -onclick=>'SSIns();'), "<-- to insert restriction sites";
	print break(1), $query->submit(-value=>'Silent Site Removal', -onclick=>'SSRem();'), "<-- to remove restriction sites";
	print break(1), $query->submit(-value=>'Oligo Design', -onclick=>'OligoDesign();'), "<-- to get a list of oligos for assembly";
	print break(1). $query->submit(-value=>'Sequence Analysis', -onclick=>'SeqAna();'), "<-- for information about this sequence";
	print $query->endform, $query->end_html;
}
