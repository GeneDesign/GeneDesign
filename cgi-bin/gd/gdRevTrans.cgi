#!/usr/bin/perl

use File::Find;
use CGI;
use PMLol;
use PRISM;
use RESite;
$query = new CGI;
print $query->header;

	print ("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">\n");
	print ("<html>\n<head>\n<meta http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\">\n");
	print ("<link href=\"$docpath/acss/re.css\" rel=\"stylesheet\" type=\"text/css\">\n");	
	print ("<link href=\"$docpath/acss/mg.css\" rel=\"stylesheet\" type=\"text/css\">\n");		
	print ("<link href=\"$docpath/acss/", cssbrowser(), ".css\" rel=\"stylesheet\" type=\"text/css\">\n") if (cssbrowser() ne '');
	print ("<script src=\"$docpath/scripts.js\" type=\"text/javascript\" language=\"Javascript\"></script>\n");
	print ("<META NAME=\"robots\" CONTENT=\"noindex, nofollow, noarchive\">\n");
	print ("<title>GeneDesign: Reverse Translation</title></head>\n");
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
	print ("<a class=\"headli\">Reverse Translation</a></div>");
	print $query->startform(-method=>'post', -action=>'./gdRevTrans.cgi', -enctype=>'application/x-www-form-urlencoded', -name=>"form1");
if ($query->param('1aaseq') eq '')
{
	print ("<div id=\"notes\">");
	print ("<strong>To use this module you need an amino acid sequence and an organism name or codon table.</strong><br>\n");
	print ("Your amino acid sequence will be reverse translated to nucleotides using the codon definitions that you specify.<br><em>Please Note:</em><br> ");
	print space(2), ("&bull;The default codon in each pulldown menu is the most optimal codon for expression in the selected organism.<br>");
	print space(2), ("&bull;If you input a codon table the pulldowns will be ignored.<br>\n");
	print ("See the <a href=\"$docpath/Guide/revtrans.html\" target=\"blank\">manual</a> for more information.\n");

	print ("</div>");
	print ("\n<div id=\"gridgroup0\">\n");
	print ("Enter your  amino acid sequence:<br>\n", $query->textarea(-name=>'1aaseq', -rows=>6, -columns=>80, -wrap=>'virtual'));
	print ("\n<div id=\"gridgroup3\">\n<div id=\"swappers\">\n<div id=\"head\">\n");
	print ("Select Your Organism: <br>\n");
	print (" <input type=\"radio\" name=\"org\" value=\"1\" checked onClick=\"organism=1;SWMarkOptimal(form1);\">H. sapiens\n");
	print (" <input type=\"radio\" name=\"org\" value=\"2\" onClick=\"organism=2;SWMarkOptimal(form1);\">S. cerevisiae\n");
	print (" <input type=\"radio\" name=\"org\" value=\"3\" onClick=\"organism=3;SWMarkOptimal(form1);\">E. coli");
#	print (" <input type=\"radio\" name=\"org\" value=\"4\" onClick=\"organism=4;SWMarkOptimal(form1);\">M. musculus");
	print (" <input type=\"radio\" name=\"org\" value=\"5\" onClick=\"organism=5;SWMarkOptimal(form1);\">C. elegans");
	print ("\n</div>\n     <div id=\"col1\" class=\"samewidth\">");
	print "    \n Ala (A)", $query->popup_menu(-name=>'A', -values=>[getcods('A')], -default=>'GCC');
	print "<br>\n Cys (C)", $query->popup_menu(-name=>'C', -values=>[getcods('C')], -default=>'TGC');
	print "<br>\n Asp (D)", $query->popup_menu(-name=>'D', -values=>[getcods('D')], -default=>'GAC');
	print "<br>\n Glu (E)", $query->popup_menu(-name=>'E', -values=>[getcods('E')], -default=>'GAG');
	print "<br>\n Phe (F)", $query->popup_menu(-name=>'F', -values=>[getcods('F')], -default=>'TTC');
	print "<br>\n Gly (G)", $query->popup_menu(-name=>'G', -values=>[getcods('G')], -default=>'GGC');
	print "<br>\n His (H)", $query->popup_menu(-name=>'H', -values=>[getcods('H')], -default=>'CAC');
	print "<br>\n Ile (I)", $query->popup_menu(-name=>'I', -values=>[getcods('I')], -default=>'ATC');
	print "<br>\n Lys (K)", $query->popup_menu(-name=>'K', -values=>[getcods('K')], -default=>'AAG');
	print "<br>\n Leu (L)", $query->popup_menu(-name=>'L', -values=>[getcods('L')], -default=>'CTG');
	print "<br>\n Met (M)", $query->popup_menu(-name=>'M', -values=>[getcods('M')], -default=>'ATG');
	print ("\n</div>\n     <div id=\"col2\" class=\"samewidth\">\n");
	print "    \n Asn (N)", $query->popup_menu(-name=>'N', -values=>[getcods('N')], -default=>'AAC');
	print "<br>\n Pro (P)", $query->popup_menu(-name=>'P', -values=>[getcods('P')], -default=>'CCC');
	print "<br>\n Gln (Q)", $query->popup_menu(-name=>'Q', -values=>[getcods('Q')], -default=>'CAG');
	print "<br>\n Arg (R)", $query->popup_menu(-name=>'R', -values=>[getcods('R')], -default=>'CGC');
	print "<br>\n Ser (S)", $query->popup_menu(-name=>'S', -values=>[getcods('S')], -default=>'AGC');
	print "<br>\n Thr (T)", $query->popup_menu(-name=>'T', -values=>[getcods('T')], -default=>'ACC');
	print "<br>\n Val (V)", $query->popup_menu(-name=>'V', -values=>[getcods('V')], -default=>'GTG');
	print "<br>\n Trp (W)", $query->popup_menu(-name=>'W', -values=>[getcods('W')], -default=>'TGG');
	print "<br>\n Tyr (Y)", $query->popup_menu(-name=>'Y', -values=>[getcods('Y')], -default=>'TAC');
	print "<br>\n Stop(*)", $query->popup_menu(-name=>'*', -values=>[getcods('*')], -default=>'TGA');
	print ("      </select><br>\n     </div>\n    </div>\n   <div id=\"pasters\">\n    <div id=\"head\">");
	print ("Or paste a table of codons here <br>\(example: A  GCT\):\n    </div>\n    <div id=\"col3\">\n");
	print $query->textarea(-name=>'tableinput', -rows=>21, -columns=>15);
	print ("\n</div>\n</div>\n</div>\n<div id=\"gridgroup1\" align =\"center\" style=\"position:absolute; top:450; \">\n");
	print $query->submit(-value=>'Reverse Translate');
	print "\n</div>\n</div>\n", $query->endform, $query->end_html;
}
else
{
	$seq2 = cleanup($query->param('1aaseq'), 2);
	undef $nucseq; undef @array;
##-make the nucleotide sequence
	if ($query->param('tableinput') eq "")
	{
		push @array, ('* ' . $query->param('*')); 
		for ($i='A'; $i ne 'Z'; $i++)
		{
			push @array, ($i . " " . $query->param($i)) unless ($i eq 'B' || $i eq 'J' || $i eq 'O' || $i eq 'U' || $i eq 'X' || $i eq 'Z');
			push @array, ($i . " XXX")						if ($i eq 'B' || $i eq 'J' || $i eq 'O' || $i eq 'U' || $i eq 'X' || $i eq 'Z');
		}
		$org = $query->param('org');
 	}
	else
	{
		$table = $query->param('tableinput');
		$table =~ tr/[a-z]/[A-Z]/;
		$table =~ tr/U/T/;
		$table .="\nB XXX\nJ XXX\nO XXX\nU XXX\nX XXX\nZ XXX";
		@array = sort(split('\n', $table));
		$org = 0;
	}
	$nucseq = revtrans($seq2, @array);
####-PREERROR CHECKING - did they include everything in the codon table? If not same length, alarm and allow them to go back.
	if (length($seq2) < length($nucseq)/3)
	{
		print ("<div id=\"notes\" style=\"text-align:center;\">");
		print ("I was unable to reverse translate your sequence.  Perhaps you left something out of your codon table?<br>");
		foreach $r (@array)
		{
			print "$r<br>";
		}
		print break(2), ("<input type=\"button\" value=\"Back\" onClick=\"history.go(-1)\">");
		print ("</div>");
	}
	else
	{
		@bcou = count($nucseq); 
		$GC = int(((($bcou[3]+$bcou[2])/$bcou[8])*100)+.5);
		$AT = int(((($bcou[0]+$bcou[1])/$bcou[8])*100)+.5);
		
		print ("<div id=\"notes\" style=\"text-align:center;\">");
		print ("Your amino acid sequence has been successfully reverse translated to nucleotides.<br>\n");
	print ("See the <a href=\"$docpath/Guide/revtrans.html\" target=\"blank\">manual</a> for more information.\n");
		print ("</div>");
		print ("<input type=\"hidden\" name=\"1aaseq\" value=\"$seq2\">");
		print ("<input type=\"hidden\" name=\"org\" value=\"$org\">");
		print ("<div id=\"gridgroup0\"><br>\n");
		print ("Your reverse translated nucleotide sequence:");
		print $query->textarea(-name=>'passnucseq', -rows=>6, -columns=>100, -default=>$nucseq, -readonly=>'true'), break(1);
		print "&nbsp;_Base Count  : $bcou[8] bp ($bcou[0] A, $bcou[1] T, $bcou[2] C, $bcou[3] G)<br>";
		print "&nbsp;_Composition : $GC% GC, $AT% AT<br>";
		print break(4);
		print ("</div>");
		print ("<div id=\"gridgroup1\" align =\"center\" style=\"position:relative;\">\n");
		print ("<div id=\"notes\" style=\"text-align:center;\">");
		print ("You can take this nucleotide sequence to another module now.");
		print ("</div>");	
		print break(1), "<strong>Take this sequence to</strong>";
		print break(1), $query->submit(-value=>'Silent Site Insertion', -onclick=>'SSIns();'), "<-- to insert restriction sites... this is the next step of the \"Design a Gene\" path!  ";
		print break(2), $query->submit(-value=>'Silent Site Removal', -onclick=>'SSRem();'), "<-- to remove restriction sites";
		print break(1), $query->submit(-value=>'Codon Juggling', -onclick=>'toCodJug();'), "<-- to codon juggling";
		print break(1), $query->submit(-value=>'Oligo Design', -onclick=>'OligoDesign();'), "<-- to get a list of oligos for assembly";
		print break(1). $query->submit(-value=>'Sequence Analysis', -onclick=>'SeqAna();'), "<-- for information about this sequence";
		print $query->endform, $query->end_html;
	}
}
