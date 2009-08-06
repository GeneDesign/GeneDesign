#!/usr/bin/perl

use PRISM;
use CGI;
use PMLol;
$query = new CGI;
print $query->header;
	print ("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">\n");
	print ("<html>\n<head>\n<meta http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\">\n");
	print ("<link href=\"../../gd/acss/re.css\" rel=\"stylesheet\" type=\"text/css\">\n");	
	print ("<link href=\"../../gd/acss/fn.css\" rel=\"stylesheet\" type=\"text/css\">\n");
	print ("<link href=\"../../gd/acss/", cssbrowser(), ".css\" rel=\"stylesheet\" type=\"text/css\">\n") if (cssbrowser() ne '');
	print ("<script src=\"../../gd/scripts.js\" type=\"text/javascript\" language=\"Javascript\"></script>\n");
	print ("<META NAME=\"robots\" CONTENT=\"noindex, nofollow, noarchive\">\n");
	print ("<title>GeneDesign: Codon Juggling</title></head>\n");
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
	print ("<a class=\"headli\">Codon Juggling</a></div>");
	print $query->startform(-method=>'post', -action=>'./gdCodJug.cgi', -name=>"form1");

if ($query->param('nseq') eq '' && $query->param('passnucseq') eq '')
{
	print ("<div id=\"notes\">");
	print ("<strong>To use this module you need a coding nucleotide sequence and an organism name.</strong><br>\n");	
	print ("It is recommended that you only use ORFs with this module because codons will be altered without changing the first frame amino acid sequence. ");
	print ("If your coding sequence is not in the first frame it will be changed.  ");
	print ("Four different algorithms will be applied to your sequence.  Each will change the nucleotide sequence without changing the ");
	print ("translated amino acid sequence. You will be presented with the four new sequences and an alignment at the next screen.<br><em>Please Note:</em><br> ");
	print space(2), ("&bull;The only frame that is considered inviolable is frame 1, which will be determined by the first three nucleotides of your sequence.<br>");
	print space(2), ("&bull;Ambiguous nucleotides and non-nucleotide characters will be removed.<br>\n");
	print ("See the <a href=\"../../gd/Guide/codjug.html\" target=\"blank\">manual</a> for more information.\n");
	print ("</div>");
	%organism = (0=> "No Optimization", 1 => 'H. sapiens', 2 => 'S. cerevisiae', 3 => 'E. coli', 5 => 'C. elegans' );# 4 => 'M. musculus');
	print ("<div id=\"gridgroup0\">\nYour nucleotide sequence:<br>\n");
	print $query->textarea(-name=>'nseq', -rows=>6, -columns=>100), break(1);
	print "Target Organism: ", $query->popup_menu(-name=>'org', -values=>\%organism, -default=>2), "\n", space(3);
	print ("<div id=\"gridgroup1\" align =\"center\" style=\"position:absolute; top:150; \">\n");
	print $query->submit(-value=>" Next Step: Results ");
	print ("</div>\n</div>\n");
	print $query->endform, $query->end_html;
}
else
{	
	$nucseq = $query->param('passnucseq') if ($query->param('passnucseq') ne '');
	$nucseq = $query->param('nseq') if ($query->param('passnucseq') eq '');

	$nucseq = cleanup($nucseq, 0);
	
	$war1 = 1 if (substr($nucseq, 0, 3) ne 'ATG');
	@war2 = stopfinder($nucseq, 1); $war3 = 1 if (@war2 && ((@war2-0 > 1 ) || (($war2[0]*3) != length($nucseq))));
	if (($war1 || $war3) && $nucseq)
	{
		print ("<div id = \"warn\">\n");
		print "<strong>Warning:</strong> Your sequence is not a simple coding sequence.<br>";
		print "Your sequence does not begin with ATG.<br>" if ($war1);
		print "Your sequence has at least one internal stop codon in the first frame.<br>" if ($war3);
		print "It is still possible to insert landmarks into this sequence but you should check to be sure that crucial features are not compromised.";
		print ("</div>");
	}
	$org = $query->param('org');
	if ($org == 0)
	{
		print ("<div id = \"warn\">\n");
		print "<strong>Warning:</strong> You have not defined an organism that is recognized by GeneDesign.<br>";
		print "The optimized and next most optimized algorithms will not be carried out.  The most different algorithm will not be deterministic.";
		print ("</div>");
	}
	print ("<div id=\"notes\">");
	print ("Your nucleotide sequence has been successfully juggled.  Each of the following sequences translate to the same amino acid sequence. \n");
	print "The reference organism for optimal codons is ", organism($org), ".<br><br>";
	print ("The <strong>Optimized</strong> sequence replaces each codon in the original sequence with the most optimal codon as determined by expressivity in the organism you chose.");
	print (" This algorithm will not be applied if organism is undefined.<br>");
	print ("The <strong>Most Different</strong> sequence has as many base changes as possible, with transversions being the most preferred change.  It uses the more optimal codon when possible.<br><br>\n");
	print ("The <strong>Next Most Optimized</strong> sequence uses the most optimal codon that is not the original codon. This algorithm will not be applied if organism is undefined.<br> \n");
	print ("The <strong>Random</strong> sequence uses a random codon that is not the original codon. No optimization is applied.<br><br>\n");
	print ("You can take any one of these sequences to another module by clicking the appropriate button.<br>\n");
	print ("See the <a href=\"../../gd/Guide/codjug.html\" target=\"blank\">manual</a> for more information.\n");
	print ("</div>\n\n");


	$aaseq = translate($nucseq);
	$len = length($nucseq);
	$opted  = optimize($nucseq, $org) if ($org != 0);
	@optal  = ezalign($nucseq, $opted); $optal[4] = int($optal[4]+.5) if ($org !=0);
	$randy  = changeup($nucseq);
	@randal = ezalign($nucseq, $randy); $randal[4] = int($randal[4]+.5);
	$nxmty = changeup($nucseq, 2, $org) if ($org !=0);
	@nxmtal = ezalign($nucseq, $nxmty); $nxmtal[4] = int($nxmtal[4]+.5) if ($org !=0);
	$mstdy = changeup($nucseq, 3, $org);
	@mstdal = ezalign($nucseq, $mstdy); $mstdal[4] = int($mstdal[4]+.5);

	print ("<div id=\"gridgroup0\">\n");
	print $query->textarea(-name=>'oldnucseq', -rows=>6, -columns=>150, -default=>$nucseq, -readonly=>'true'), break(1);
	@bcou = count($nucseq); 
	$GC = int(((($bcou[3]+$bcou[2])/$bcou[8])*100)+.5);
	$AT = int(((($bcou[0]+$bcou[1])/$bcou[8])*100)+.5);
	print ("<strong>Original Sequence<br></strong>");
	print "&nbsp;_Base Count  : $bcou[8] bp ($bcou[0] A, $bcou[1] T, $bcou[2] C, $bcou[3] G)<br>";
	print "&nbsp;_Composition : $GC% GC, $AT% AT<br><br>";
	
print "<div style =\"position: relative\">";
	print ("<div style=\"position: absolute; top: 0;left : 0;\">");
if ($org !=0)
{
	print $query->textarea(-name=>'optnucseq', -rows=>6, -columns=>65, -default=>$opted, -readonly=>'true');
	@bcou = count($opted); 
	$GC = int(((($bcou[3]+$bcou[2])/$bcou[8])*100)+.5);
	$AT = int(((($bcou[0]+$bcou[1])/$bcou[8])*100)+.5);
	print break(1), "\n<strong>Optimized</strong><br>\n";
	print "&nbsp;_Base Count  : $bcou[8] bp ($bcou[0] A, $bcou[1] T, $bcou[2] C, $bcou[3] G)<br>";
	print "&nbsp;_Composition : $GC% GC, $AT% AT<br>";
	print "$optal[0] Identites, $optal[1] Changes ($optal[2] transitions $optal[3] transversions), $optal[4]% Identity<br>";
	print "Take this to:";
	print $query->submit(-value=>'Silent Site Insertion', -onclick=>'CodJug(0, 0);'), space(1);
	print $query->submit(-value=>'Silent Site Removal', -onclick=>'CodJug(0, 1);'), space(1);
	print $query->submit(-value=>'Oligo Design', -onclick=>'CodJug(0, 2);'), space(1);
	print $query->submit(-value=>'Analysis', -onclick=>'CodJug(0, 3);'), space(1);
}
	print ("</div>\n");

	print ("<div style=\"position: absolute; top: 0;left : 550;\">");
	print $query->textarea(-name=>'mdfnucseq', -rows=>6, -columns=>65, -default=>$mstdy, -readonly=>'true');
	@bcou = count($mstdy); 
	$GC = int(((($bcou[3]+$bcou[2])/$bcou[8])*100)+.5);
	$AT = int(((($bcou[0]+$bcou[1])/$bcou[8])*100)+.5);
	print break(1), "\n<strong>Most Different</strong><br>\n"; 
	print "&nbsp;_Base Count  : $bcou[8] bp ($bcou[0] A, $bcou[1] T, $bcou[2] C, $bcou[3] G)<br>";
	print "&nbsp;_Composition : $GC% GC, $AT% AT<br>";
	print "$mstdal[0] Identites, $mstdal[1] Changes ($mstdal[2] transitions $mstdal[3] transversions), $mstdal[4]% Identity<br>";
	print "Take this to:";
	print $query->submit(-value=>'Silent Site Insertion', -onclick=>'CodJug(2, 0);'), space(1);
	print $query->submit(-value=>'Silent Site Removal', -onclick=>'CodJug(2, 1);'), space(1);
	print $query->submit(-value=>'Oligo Design', -onclick=>'CodJug(2, 2);'), space(1);
	print $query->submit(-value=>'Analysis', -onclick=>'CodJug(2, 3);'), space(1);
	print ("</div>\n");
	
print "</div>", break(13);
print break(2) if (platform() eq 'win');
print "<div style =\"position: relative\">";

	print ("<div style=\"position: absolute; top:0;left : 0;width:600;\">");
if ($org != 0)
{
	print $query->textarea(-name=>'nxtnucseq', -rows=>6, -columns=>65, -value=>$nxmty, -readonly=>'true');
	@bcou = count($nxmty); 
	$GC = int(((($bcou[3]+$bcou[2])/$bcou[8])*100)+.5);
	$AT = int(((($bcou[0]+$bcou[1])/$bcou[8])*100)+.5);
	print break(1), "\n<strong>Next Most Optimized</strong> (For the experimentalists)<br>\n";
	print "&nbsp;_Base Count  : $bcou[8] bp ($bcou[0] A, $bcou[1] T, $bcou[2] C, $bcou[3] G)<br>";
	print "&nbsp;_Composition : $GC% GC, $AT% AT<br>";
	print "$nxmtal[0] Identites, $nxmtal[1] Changes ($nxmtal[2] transitions $nxmtal[3] transversions), $nxmtal[4]% Identity<br>";
	print "Take this to:";
	print $query->submit(-value=>'Silent Site Insertion', -onclick=>'CodJug(1, 0);'), space(1);
	print $query->submit(-value=>'Silent Site Removal', -onclick=>'CodJug(1, 1);'), space(1);
	print $query->submit(-value=>'Oligo Design', -onclick=>'CodJug(1, 2);'), space(1);
	print $query->submit(-value=>'Analysis', -onclick=>'CodJug(1, 3);'), space(1);
}
	print ("</div>\n");
	
	
	print ("<div style=\"position: absolute; top:0;left : 550;width:600;\">");
	print $query->textarea(-name=>'rdmnucseq', -rows=>6, -columns=>65, -default=>$randy, -readonly=>'true');
	@bcou = count($randy); 
	$GC = int(((($bcou[3]+$bcou[2])/$bcou[8])*100)+.5);
	$AT = int(((($bcou[0]+$bcou[1])/$bcou[8])*100)+.5);
	print break(1), "\n<strong>Random</strong> (For the experimentalists)<br>\n";
	print "&nbsp;_Base Count  : $bcou[8] bp ($bcou[0] A, $bcou[1] T, $bcou[2] C, $bcou[3] G)<br>";
	print "&nbsp;_Composition : $GC% GC, $AT% AT<br>";
	print "$randal[0] Identites, $randal[1] Changes ($randal[2] transitions $randal[3] transversions), $randal[4]% Identity<br>";
	print "Take this to:";
	print $query->submit(-value=>'Silent Site Insertion', -onclick=>'CodJug(3, 0);'), space(1);
	print $query->submit(-value=>'Silent Site Removal', -onclick=>'CodJug(3, 1);'), space(1);
	print $query->submit(-value=>'Oligo Design', -onclick=>'CodJug(3, 2);'), space(1);
	print $query->submit(-value=>'Analysis', -onclick=>'CodJug(3, 3);'), space(1);
	print ("</div>\n");	

	print ("  <input type=\"hidden\" name=\"nucseq\" value=\"\">\n");
	print ("  <input type=\"hidden\" name=\"1aaseq\" value=\"$aaseq\">\n");
	print ("<input type=\"hidden\" name=\"org\" value=\"$org\">");

print "</div></div>", break(14);
print break(2) if (platform() eq 'win');
if ($org !=0)
{
	print ("<div id=\"notes\">");
	print ("An alignment is presented below.  'cons'  is the consensus sequence - these are the bases that are non-negotiable across algorithms. ");
	print ("There is an asterisk under every tenth nucleotide.");
	print ("</div>\n");	


	print ("<div class=\"samewidth\">");
@nuc = split('', $nucseq);
@opt = split('', $opted);
@mst = split('', $mstdy);
for ($x = 0; $x < $len; $x++)
{
	$new = '_';
	$new = $nuc[$x] if ( ($nuc[$x] eq $opt[$x]) && ($nuc[$x] eq $mst[$x]) && $org != 0);
	$new = $nuc[$x] if ( ($nuc[$x] eq $mst[$x]) && $org == 0);
	$con .= $new;
}
@sen = split('', $con);
$times = $len / 150;
for ($b = 0; $b < $times; $b++)
{
	print "<br>tran&nbsp;";
	for ($rt = ($oldpos/3); $rt < ($oldpos/3)+50; $rt++)
	{
		print substr($aaseq, $rt, 1), space(2);
	}
	print space(1), $rt;
	print "<br>orig&nbsp;";
	while (($curpos+1) % 150 != 0)
	{
		print ("$nuc[$curpos]");
		$curpos++;
	}
	print $nuc[$curpos], space(1), $curpos+1;
	print $nuc[$curpos+1] if ($b == $times-1);
	$curpos = $oldpos;
if ($org != 0)
{
	print "<br>opti&nbsp;";
	while (($curpos+1) % 150 != 0)
	{
		print ("$opt[$curpos]");
		$curpos++;
	}
	print $opt[$curpos];
	print $opt[$curpos+1] if ($b == $times-1);
	$curpos = $oldpos;
}
	print "<br>mtdf&nbsp;";
	while (($curpos+1) % 150 != 0)
	{
		print ("$mst[$curpos]");
		$curpos++;
	}
	print $mst[$curpos];
	print $mst[$curpos+1] if ($b == $times-1);
	$curpos = $oldpos;
	
	print "<br>cons&nbsp;";
	while (($curpos+1) % 150 != 0)
	{
		print ("$sen[$curpos]");
		$curpos++;
	}
	print $sen[$curpos];
	print $sen[$curpos+1] if ($b == $times-1);
	print break(1), space(5);
	for ($rt = 1; $rt <= 150; $rt+=10)
	{
		print space(9), "*";
		last if ($rt+$oldpos > $len);
	}
	print break(2);
	$curpos++;
	$oldpos = $curpos;
}
	print ("<br><br>&nbsp;</div>\n");
}
	print $query->endform, $query->end_html;
}
