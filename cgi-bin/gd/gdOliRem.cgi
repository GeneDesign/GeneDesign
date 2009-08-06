#!/usr/bin/perl

use PRISM;
use CGI;
use RESite;
use PMLol;
$query = new CGI;
print $query->header;
	print ("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">\n");
	print ("<html>\n<head>\n<meta http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\">\n");
	print ("<link href=\"$docpath/acss/re.css\" rel=\"stylesheet\" type=\"text/css\">\n");	
	print ("<link href=\"$docpath/acss/", cssbrowser(), ".css\" rel=\"stylesheet\" type=\"text/css\">\n") if (cssbrowser() ne '');
	print ("<script src=\"$docpath/scripts.js\" type=\"text/javascript\" language=\"Javascript\"></script>\n");
	print ("<META NAME=\"robots\" CONTENT=\"noindex, nofollow, noarchive\">\n");
	print ("<title>GeneDesign: Short Sequence Removal</title></head>\n");
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
	print ("<div id=\"toppa\"><a href=\"$docpath/index.html\"><img src=\"$docpath/img/gdlogobanner.gif\" align = \"absmiddle\"></a>\n");
	print ("<a class=\"headli\">Short Sequence Removal</a></div>");
	print $query->startform(-method=>'post', -action=>'./gdOliRem.cgi', -name=>"form1");

if ($query->param('org') eq '')
{
	print ("<div id=\"notes\">");
	print ("<strong>To use this module you need two nucleotide sequences, large and small.  An organism name is optional.</strong><br>\n");
	print ("Your nucleotide sequence will be searched for the short sequence you provide and as many iterations as possible will be removed by changing whole codons ");
	print ("without changing the amino acid sequence.<br><em>Please Note:</em><br> ");
	print space(2), ("&bull;If you select an organism, targeted codons will be replaced with the codon that enjoys the most optimal expression in that organism.<br>");
	print space(2), ("&bull;If you select no optimization, targeted codons will be replaced with a random codon.<br>\n");
	print ("See the <a href=\"$docpath/Guide/shortr.html\">manual</a> for more information.\n");
	print ("</div>");
	$nucseq = $query->param('passnucseq') if ($query->param('passnucseq') ne '');
	$nucseq = $query->param('nucseq') if ($query->param('passnucseq') eq '');
	%organism = (0=> 'No Optimization', 1 => 'H. sapiens', 2 => 'S. cerevisiae', 3 => 'E. coli', 5 => 'C. elegans' );# 4 => 'M. musculus');
	print ("<div id=\"gridgroup0\">\nYour nucleotide sequence:<br>\n");
	print $query->textarea(-name=>'nuseq', -rows=>6, -columns=>100, -default=>$nucseq), break(1);
	print "Target Organism: ", $query->popup_menu(-name=>'org', -values=>\%organism, -default=>0), "\n", space(3), break(2);
	print "Sequence to be Removed: ", $query->textfield(-name=>'remseq', -columns=>20), break(2);
	print ("<div id=\"gridgroup1\" align =\"center\" style=\"position:absolute; top:170; \">\n");
	print $query->submit(-value=>" Remove short sequences ");
	print ("</div>\n</div>\n");
	print $query->endform, $query->end_html;
}
elsif ($query->param('org') ne '' && ($query->param('nuseq') eq '' || length($query->param('remseq')) >= length($query->param('nuseq')) || length($query->param('remseq')) < 2 ))
{
	print ("<div id=\"notes\">");
	print ("You need a nucleotide sequence.<br>") if ($query->param('nuseq') eq '');
	print ("You need a short sequence to be removed (at least two bp) <br> ") if ($query->param('remseq') eq '');
	print ("Your short sequence should be shorter than your nucleotide sequence.<br>\n") if ($query->param('remseq') >= length($query->param('nuseq')));
	print break(2), ("<input type=\"button\" value=\"Back\" onClick=\"history.go(-1)\">");
	print ("</div>");
}
else
{
	$remseq = cleanup($query->param('remseq'), 0);
	$nucseq = cleanup($query->param('nuseq'), 0);
	$oldnuc = $nucseq;
	$len = length($nucseq);
	@aa = split('', translate($nucseq));
	@nuc = split('', $nucseq);
	$organism = $query->param('org');
	undef %changeit;
	@t = siteseeker($remseq, $nucseq, 2);
	$starnum = @t-0;
	for ($tcv = 0; $tcv <= 3; $tcv++)
	{
		@t = siteseeker($remseq, $nucseq, 2);
		foreach $v (@t)
		{
			$remaa = ''; $remnt = '';
			$start = $v-1; 
			while (($start % 3) != 0)
			{ 						
				$start--;
			}
			$stop = $start + length($remseq)-1;
			for ($b = $start; $b <= $stop; $b++)
			{
				$remnt .= $nuc[$b];
			}
			while (length($remnt) % 3 != 0 )#|| $remnt !~ $remseq)
			{
				#$b++;
				$remnt .= $nuc[$b];	##-make sure you have nucs in threes
				$b++;
			}
			$remaa = translate($remnt);
			$rmseq = changeup($remnt, 2, $organism, $remseq) if (length($remseq) <= 3);
			$rmseq = changeup($remnt, 2, $organism)			 if (length($remseq) > 3);
#			print " FLAG " if ($remaa ne translate($remnt));
#			print "$v, $remnt, $rmseq, $remaa, $remseq<br>";
			$changeit{$start} = $rmseq;
		}
		$curpos = 0; $newnuc = '';
		foreach $c (sort {$a <=> $b }keys %changeit)
		{
			$newnuc .= substr ( $nucseq, $curpos, ($c-$curpos)) . $changeit{$c};
			$curpos = length($newnuc);
#			print length($newnuc), "<br>";
		}	
		$newnuc .= substr ($nucseq, $curpos);	
		#	print "$newnuc<br><br>";
		$nucseq = $newnuc; %changeit = undef;	
	}

	@t = siteseeker($remseq, $nucseq, 2);
	print ("<div id=\"notes\">");
	print "\nI was asked to remove $starnum occurences of the sequence $remseq.";
	print break(1);
	if (@t-0 > 0)
	{
		print "\n<br>But after three iterations, I couldn't remove ", @t-0, " instances of it.\n";
		print "You might try again from the top with this sequence and random codon replacement.";
		print break(1);
	}
	print "\There were no problems kicking the sequences out.<br>\n" if (@t-0 == 0);
	print ("See the <a href=\"$docpath/Guide/ssr.html\">manual</a> for more information.\n");
print "</div>"; 
	print break(1);
	print ("<div id=\"gridgroup0\">Your altered nucleotide sequence:\n");
	print $query->textarea(-name=>'nusseq', -rows=>6, -columns=>120, -default=>$nucseq), break(1);
	@newal = ezalign($oldnuc, $nucseq);
		@bcou = count($nucseq); 
	$GC = int(((($bcou[3]+$bcou[2])/$bcou[8])*100)+.5);
	$AT = int(((($bcou[0]+$bcou[1])/$bcou[8])*100)+.5);

	print "Your new sequence has $newal[0] identites, $newal[1] changes, and is $newal[4]% identical to the original sequence.<br>Composition : $GC% GC, $AT% AT</div>", break(3);
		print ("<div id=\"gridgroup1\" align =\"center\" style=\"position:relative \">\n");
	print $query->hidden(-name=>'passnucseq', value=>$nucseq);
	
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
