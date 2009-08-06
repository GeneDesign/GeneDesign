#!/usr/bin/perl

use PRISM;
use CGI;
use PMLol;
use RESite;
$query = new CGI;
print $query->header;

	print ("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">\n");
	print ("<html>\n<head>\n<meta http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\">\n");
	print ("<link href=\"../../gd/acss/re.css\" rel=\"stylesheet\" type=\"text/css\">\n");	
	print ("<link href=\"../../gd/acss/", cssbrowser(), ".css\" rel=\"stylesheet\" type=\"text/css\">\n") if (cssbrowser() ne '');
	print ("<META NAME=\"robots\" CONTENT=\"noindex, nofollow, noarchive\">\n");
	print ("<title>GeneDesign: Random DNA Generator</title></head>\n");
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
	print ("<a class=\"headli\">Random DNA Generator</a></div>");
	print $query->startform(-method=>'post', -action=>'./gdRandDNA.cgi');

if ($query->param('atcontent') == 0)
{
	print ("<div id=\"notes\">");
	print ("This module is for the generation of random sequences of DNA. You can specify A+T content, length, and the number of ");
	print ("sequences you wish to have returned.<br>");
	print space(2), ("&bull;If you give me ridiculous numbers it will take forever and may crash your browser.<br>\n");
	print ("See the <a href=\"../../gd/Guide/randna.html\">manual</a> for more information.\n");
	print ("</div>");
	print break(3);
	
	print "A+T content:", $query->textfield(-name=>'atcontent', -default=>'50', -size=> 5, -maxlength=>3), "%<br>";
	print "Sequence length:", $query->textfield(-name=>'seqleng', -default=>'100', -size=>5, -maxlength=>4), "bp<br>";
	print "Number to Generate:", $query->textfield(-name=>'gennum', -default=>'5', -size=>5, -maxlength=>3), "<br>";
	print break(2);
	print $query->checkbox(-name=>'stops', -value=>"1", -label=>"Allow stop codons in first frame");
	print break(3);
	print $query->submit(-value=>"Generate Sequences"), break(5);
	$query->endform;
	$query->end_html;
}
else
{
##-Get Selection Variables
	$atcont = $query->param('atcontent');
	$tarlen = $query->param('seqleng');
	$gennum = $query->param('gennum');
	$stopal = $query->param('stops');
	$stopal = 2 if !($query->param('stops'));
	for ($x = 0; $x < $gennum; $x++)
	{
		$temparr[$x] = randDNA($tarlen, $atcont, $stopal);
	}
	
	print ("<div id=\"notes\">");
	print ("I have generated $gennum sequences of $tarlen bp that are $atcont % A+T.<br>");
	print ("Stop codons were not allowed in the first frame.<br>") if $stopal ne "yes";
	print space(2), ("&bull;Simply refresh this page for another $gennum random sequences with the same properties.<br>\n");
	print ("</div>");

	print ("<div id=\"wrapper\">\n");
	$j = 1;
	foreach $m (@temparr)
	{
		print "$j: ", $m, "<br><br>\n";
		$j++;
	}
	print ("</div>\n</body>\n</html>\n");
}
