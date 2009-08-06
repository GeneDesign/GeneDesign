#!/usr/bin/perl

use PRISM;
use CGI;
use PMLol;
$query = new CGI;
print $query->header;

	print ("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">\n");
	print ("<html>\n<head>\n<meta http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\">\n");
	print ("<link href=\"$docpath/acss/re.css\" rel=\"stylesheet\" type=\"text/css\">\n");	
	print ("<link href=\"$docpath/acss/tm.css\" rel=\"stylesheet\" type=\"text/css\">\n");	
	print ("<link href=\"$docpath/acss/", cssbrowser(), ".css\" rel=\"stylesheet\" type=\"text/css\">\n") if (cssbrowser() ne '');
	print ("<script src=\"$docpath/scripts.js\" type=\"text/javascript\" language=\"Javascript\"></script>\n");
	print ("<META NAME=\"robots\" CONTENT=\"noindex, nofollow, noarchive\">\n");
	print ("<title>GeneDesign: Sequence Analysis</title></head>\n");
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
	print ("<a class=\"headli\">Sequence Analysis</a></div>");
	print $query->startform(-method=>'post', -action=>'./gdSeqAna.cgi', -name=>"form1");

if ($query->param('nucseq') eq '' && $query->param('passnucseq') eq '')
{
	print ("<div id=\"notes\">");
	print ("<strong>To use this module you need at least one nucleotide sequence.</strong><br>\n");
	print ("This module is for the analysis of nucleotide sequences. Your nucleotide sequence(s) will be analyzed for base content, Tm, the presence ");
	print ("of restriction sites, and open reading frames.<br>");
	print space(2), ("&bull;If you wish to compare a list of sequences, make sure they are all on separate lines and check 'oligo list'.<br>\n");
	print ("See the <a href=\"$docpath/Guide/seqana.html\" target=\"blank\">manual</a> for more information.\n");
	print ("</div>");

	print ("<div id=\"gridgroup0\">\nEnter your nucleotide sequence(s):<br>\n");
	print $query->textarea(-name=>'nucseq', -rows=>6, -columns=>100), break(1);
	print $query->radio_group(-name=>'kind', -values=>['oligo list', 'single sequence'], -default=>'single sequence');
	print ("<div id=\"gridgroup1\" align =\"center\" style=\"position:absolute; top:150; \">\n");
	print $query->submit(-value=>" Analyze ");
	print ("</div>\n</div>\n");
	print $query->endform, $query->end_html;
} 
else
{
$kind = $query->param('kind');
if ($kind ne 'oligo list')
{
	print ("<div id=\"notes\">");
	print ("For a description of the formulas used, see the manual.<br>");
	print space(2), ("&bull;You don't have to go back to put in a new sequence.  Simply type or paste the new sequence into the box and hit 'Analyze Again'.\n");
	print ("</div>");

	$benchstart = (times)[0];
	$nucseq = $query->param('passnucseq') if ($query->param('passnucseq') ne '');
	$nucseq = $query->param('nucseq') if ($query->param('passnucseq') eq '');
	$nucseq = cleanup($nucseq);
	@bcou = count($nucseq); 
	$GC = int(((($bcou[3]+$bcou[2])/$bcou[8])*100)+.5);
	$AT = int(((($bcou[0]+$bcou[1])/$bcou[8])*100)+.5);
	@melty  = (melt($nucseq, 1), melt($nucseq, 2), melt($nucseq, 3), melt($nucseq, 4), melt($nucseq, 5), melt($nucseq, 6));
	@thermy = nntherm($nucseq);
	print "<br>Your sequence:<br>";
	print $query->textarea(-name=>'passnucseq', -rows=>6, -columns=>100, -default=>$nucseq, -wrap=>'hard'), break(2);
#print count and comp
	print "_Base Count  : $bcou[8] bp ($bcou[0] A, $bcou[1] T, $bcou[2] C, $bcou[3] G)<br>";
	print "_Composition : $GC% GC, $AT% AT", space(10), $query->submit(-value=>" Analyze Again "), break(2);

#print melts if less than 100bp
	if (length($nucseq) < 50)
	{
		print "_&Delta;H: $thermy[0]<br>";
		print "_&Delta;S: $thermy[1]<br>";
		print "_&Delta;G: $thermy[2]<br><br>";
	}
	if (length($nucseq) < 100)
	{
		print "_Simple: $melty[0]<br>" if (length($nucseq) <=22);
		print "_Bolton: $melty[1]<br>" if (length($nucseq) >=7);
		print "_Primer: $melty[2]<br>" if (length($nucseq) >=10);
		print "_NNTher: $melty[3]<br>" if (length($nucseq) >=10);
		print "_GDAvg : $melty[5]<br><br>";
	}
	if (length($nucseq) > 10)
	{
#figure out uniques and absents
	foreach $t (sort (siterunner(2, $nucseq)))
	{	
		@temp = siteseeker($t, $nucseq);
		$borders{$temp[0]} = $t;
	}
	@abss = sort (siterunner(1, $nucseq));
	print ("<div id=\"reswrap\">");
	print ("<div id=\"abssite\"><strong>Absent Sites</strong><br>@abss</div>");
	print ("<div id=\"seqwrap\"><strong>Unique Sites</strong>");
	print ("<div id=\"genecol\">");
	foreach $r (sort {$a <=> $b} keys %borders)
	{
		$pos = int(($r/$bcou[8])*500);
		print ("<div id=\"uniline\" style=\"top: $pos;\"></div>");
	}
	for ($e = 0; $e <= 39; $e++)
	{
		print "<div id = \"namebox\" style=\"top:", $e*12.5, ";\">";
		foreach $r (sort {$a <=> $b} keys %borders)
		{
			$pos = int(($r/$bcou[8])*500);
			print "$borders{$r} ($r) " if (($pos <= ($e+1)*12.5) && $pos > $e*12.5);
		}
		print "</div>\n";
	}
	print ("</div></div>");
#figure out ORFs and stops
	print ("<div id =\"orfwrap\"><strong>ORFs</strong><br>");
	print ("<div id=\"orfcol\">\n");
	for ($g = 0; $g < 3; $g++)
	{
		foreach $r (orffinder($nucseq, $g+1))
		{
			$top = $1 if ($r =~ /([0-9]+)V[0-9]+/);			$hei = $1 if ($r =~ /[0-9]+V([0-9]+)/);
			$post = int(((($top*3)-2)/$bcou[8])*500);		$posh = int(((($hei*3))/$bcou[8])*500);
			$tiff = $post - 0;	$post = 0 if ($top == 1);	$posh += $tiff if ($top == 1);
			$posh = 500-$post+$diff if ($hei == 500);	
			print "<div id=\"orfbox\" style=\"top:$post; left:", 10*$g, "; height:$posh;\"></div>\n";
		}
		
		foreach $r (stopfinder($nucseq, $g+1))
		{
			$pos = int(((($r*3)-2)/$bcou[8])*500);
			print "<div id=\"stopbox\" style=\"top:$pos; left:", 10*$g, ";\"></div>\n";
		}
	}
	print "</div></div></div>\n", break(40), space(40);
	}
	print ("<div id=\"gridgroup1\" align =\"center\" style=\"position:relative;\">\n");
	print ("<div id=\"notes\" style=\"text-align:center;\">");
	print ("You can take this nucleotide sequence to another module.");
	print ("</div>");	
	print break(1), "<strong>Take this sequence to</strong>";
	print break(1), $query->submit(-value=>'Codon Juggling', -onclick=>'toCodJug();'), "<-- to codon juggling";
	print break(1), $query->submit(-value=>'Silent Site Insertion', -onclick=>'SSIns();'), "<-- to insert restriction sites";
	print break(1), $query->submit(-value=>'Silent Site Removal', -onclick=>'SSRem();'), "<-- to remove restriction sites";
	print break(1), $query->submit(-value=>'Oligo Design', -onclick=>'OligoDesign();'), "<-- to get a list of oligos for assembly";
	print ("<input type=\"hidden\" name=\"passnucseq\" value=\"$nucseq\">");

	print $query->endform, $query->end_html;
}
else
{
	print ("<div id=\"notes\">");
	print ("For a description of the formulas used, see the manual.<br>");
	print ("</div>");

	$r = 0;
	$benchstart = (times)[0];
	$nucseq = $query->param('nucseq');
	@nucarr = split('\n', $nucseq);
	foreach $t (@nucarr)
	{
		$h = $r+1;
		$h = '0' . $h while(length($h) < (length(@nucarr-0)));
		$m = cleanup($t, 1);
		@bcou = count($m); 
		$GC = int(((($bcou[3]+$bcou[2])/$bcou[8])*100)+.5);
		$AT = int(((($bcou[0]+$bcou[1])/$bcou[8])*100)+.5);
		@melty  = (melt($m, 1), melt($m, 2), melt($m, 3), melt($m, 4), melt($m, 5));
		@thermy = nntherm($m);
		print "$m, \#$h ", space(1), "$bcou[8] bp", space(3);
		print "$GC% GC", space(2), "$AT% AT", space(3);
		print "b ", int($melty[1]+.5);
		print space(2), "p ", int($melty[2]+.5);
		print space(2), "n ", int($melty[3]+.5);
		print break(1);
		$r++;
	}
}
}
