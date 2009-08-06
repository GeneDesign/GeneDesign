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
	print ("<link href=\"../../gd/acss/fn.css\" rel=\"stylesheet\" type=\"text/css\">\n");
	print ("<link href=\"../../gd/acss/mg.css\" rel=\"stylesheet\" type=\"text/css\">\n");
	print ("<link href=\"../../gd/acss/", cssbrowser(), ".css\" rel=\"stylesheet\" type=\"text/css\">\n") if (cssbrowser() ne '');
	print ("<script src=\"../../gd/scripts.js\" type=\"text/javascript\" language=\"Javascript\"></script>\n");
	print ("<META NAME=\"robots\" CONTENT=\"noindex, nofollow, noarchive\">\n");
	print ("<title>GeneDesign: Enzyme Chooser</title></head>\n");
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
	print ("<a class=\"headli\">Enzyme Chooser</a></div>");
	print $query->startform(-method=>'post', -name=>'form1', -action=>'./gdEnzChooser.cgi');

if ($query->param('first') == 0)
{
	print ("<div id=\"notes\">");
	print ("This module is for the critical selection of restriction enzymes. The next screen will present a sorted \n");
	print ("and annotated list of enzymes that match the criteria you specify.<br>");
	print space(2), ("&bull;GeneDesign uses a non-redundant list of restriction enzymes (one isoschizomer per site).<br>\n");
	print space(2), ("&bull;Price is measured in 2004 US dollars from the NEB catalog.<br>\n");
	print ("See the <a href=\"../../gd/Guide/enzcho.html\">manual</a> for more information.\n");
	print ("</div>");
	print ("\n<div id=\"gridgroup0\"> What sort of thing do you like to see in an enzyme?<div id=\"critbox\">\n ");
	enzmenu();	
	print "</div></div>", break(2);
	print $query->defaults('Defaults');
	print $query->submit(-value=>"Show me the Enzymes"), break(5);
	print $query->hidden(-name=>'first', -value=>1);
	$query->endform;
	$query->end_html;
}
else
{
##-Get Selection Variables
	@ends   = $query->param('crEnds');
	push @ends, $query->param('crEndss');
	@cuts   = $query->param('crCuts');
	push @cuts, $query->param('crCutss');
	@leng   = $query->param('crLeng');
	push @leng, $query->param('crLengs');
	@ambi   = $query->param('crAmbi');
	push @ambi, $query->param('crAmbis');
	@pric	= ($query->param('crPrlo'), $query->param('crPrhi'));
	push @pric, $query->param('crPrir');
	$diss	= $query->param('crDisa'); $diss =~ s/\s//g;
	@disa	= split ",", $diss;
	$alls	= $query->param('crAllo'); $alls =~ s/\s//g;
	@allo	= split ",", $alls;
	@meth   = $query->param('crMeths');
	push @meth, $query->param('crMeth');
	
#	print "@ends<br>@leng<br>@pric<br>@disa<br>@allo<br>@cuts<br>@meth<br>";
	undef @SitArr;
	@cutters = siteload();
	$topper = (new RESite())->TableHeader;
	$y = 0;
	foreach $n (@cutters)## make new objects, fill out data
	{
		$SitArr[$y] = new RESite();
		$SitArr[$y]->CutterName($n);
		$SitArr[$y]->LoadInfo();
		$y++;
	}
	@SitArr = grep {$_->Sticky ne ''} @SitArr;
	@SitArr = grep {$_->CompareEnds  (\@ends)} @SitArr;
	@SitArr = grep {$_->CompareLength(\@leng)} @SitArr;
	@SitArr = grep {$_->CompareCut	 (\@cuts)} @SitArr;
	@SitArr = grep {$_->CompareAmbig (\@ambi)} @SitArr;
	@SitArr = grep {$_->ComparePrice (\@pric)} @SitArr;
	@SitArr = grep {$_->CompareMeth  (\@meth)} @SitArr;
	@SitArr = grep {$_->SeqFilter (\@disa, 1)} @SitArr;
	@SitArr = grep {$_->SeqFilter (\@allo, 2)} @SitArr;
	@SitArr = sort {$a->UPrice <=> $b->UPrice} @SitArr;
	@SitArr = map  ($_->friendly(), @SitArr);
	@finarr = map  ($_->CutterName, @SitArr);
	my $num = (@finarr-0);
	
	unshift @SitArr, $topper;
	
	print ("<div id=\"notes\">");
	print ("There are $num enzymes that fit your criteria.<br>\n");
	print ("See the <a href=\"../../gd/Guide/enzcho.html\">manual</a> for more information.\n");
	print ("</div>");

	print ("<div id=\"gridgroup0\">\n");
	print ("Ranked Summary: <br><textarea name=\"list\" rows=\"5\" cols=\"116\" readonly>@finarr</textarea>\n<br><br>");

	$j = 0;
	foreach $m (@SitArr)
	{
		$currname = $m->CutterName;
		$color = "ABC" if ($j % 2 == 0);
		$color = "CDE" if ($j % 2);
		$color = "9AB" if ($j == 0);
		print ("\n<div id = \"gridgroup1\" style = \"background-color: \43$color;\">\n");
		print (" <span id = \"cuNum\"  >", $j, "</span>\n") if ($j != 0);
		print (" <span id = \"cuName\" >", $currname, "</span>\n") if $j == 0;		
		print (" <span id = \"cuName\" ><a href=\"http://rebase.neb.com/rebase/enz/$currname.html\" target=\"blank\">$currname $cautio{$m}</a></span>\n") if $j != 0;
		print (" <span id = \"cuRecog\">", $m->CutsAt, $m->StarAct, "</span>\n");
		print (" <span id = \"cuStick\">", $m->Sticky, "</span>\n");
		print (" <span id = \"cuRxnTe\">", $m->RxnTemp,"</span>\n");
		print (" <span id = \"cuMethb\">", $m->Methyb, "</span>\n");
		print (" <span id = \"cuMethi\">", $m->Methyi, "</span>\n");
		print (" <span id = \"cuVendr\">", $m->Vendor, "</span>\n");
		print (" <span id = \"cuUpric\">", $m->UPrice, "</span>\n");
		print ("&nbsp;<br>&nbsp;</div>\n");
		$j++;
	}
	print ("\n<div id = \"gridgroup1\" style = \"background-color: \439AB;\">\n");
	print ("\n");
	print ("<br> * This enzyme exhibits star activity under certain conditions.");
	print ("<br>&laquo; This enzyme has a 1bp overhang and may be very difficult to ligate.");
	print ("&nbsp;<br>&nbsp;</div>\n");
	print ("<br><br>&nbsp;");
	print ("</div>\n</body>\n</html>\n");
}
