#!/usr/bin/perl

use PRISM;
use CGI;
use PMLol;
use RESite;
$query = new CGI;
print $query->header;

	print ("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">\n");
	print ("<html>\n<head>\n<meta http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\">\n");
	print ("<link href=\"$docpath/acss/re.css\" rel=\"stylesheet\" type=\"text/css\">\n");	
	print ("<link href=\"$docpath/acss/", cssbrowser(), ".css\" rel=\"stylesheet\" type=\"text/css\">\n") if (cssbrowser() ne '');
	print ("<META NAME=\"robots\" CONTENT=\"noindex, nofollow, noarchive\">\n");
	print ("<title>GeneDesign: Random DNA Generator</title></head>");
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
	print ("<a class=\"headli\">Random DNA Generator</a></div>");
	print $query->startform(-method=>'post', -action=>'./gdAmbigTrans.cgi');

if ($query->param('ntseq') !~ /[ATCG]+/)
{
	print ("<div id=\"notes\">");
	print ("This module is for the translation of DNA sequences that may include ambiguous bases.<br>");
	print space(2), ("&bull;Right now it only works for sequences up to 15nt - we can develop more if there is demand.<br>\n");
#	print ("See the <a href=\"$docpath/Guide/randna.html\">manual</a> for more information.\n");
	print ("</div>");
	print break(3);
	print ("Enter your nucleotide sequence:<br>\n", $query->textfield(-name=>'ntseq', -size=>20, -maxlength=>15));
	print break(2);
	print $query->submit(-value=>"Generate Amino Acid Sequences"), break(5);
	$query->endform;
	$query->end_html;
}
else
{
##-Get Selection Variables
	$nucseq = $query->param('ntseq');
	
	@allarr = transregex($nucseq);
	@sortarr = sort(@allarr);
	$cleanseq = ($nucseq, 1);
	print ("<div id=\"notes\">");
	print ("I have found ", @allarr-0, " possible peptides from the oligo you gave me.<br>");
	print ("</div>");
	print ("<div id=\"wrapper\">\n");
	print ("Oligo: $nucseq<br>");
	print ("Summary: <br><textarea name=\"list\" rows=\"5\" cols=\"116\" readonly>@sortarr</textarea>\n<br><br>");
	print space(2);
	foreach $oll (@sortarr)
	{
		print "$oll<br>";
	}
	print ("</div>\n</body>\n</html>\n");
}
