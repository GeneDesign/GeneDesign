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
	print ("<title>GeneDesign: Vector Chooser</title></head>\n");
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
	print ("<a class=\"headli\">Vector Chooser</a></div>");
	print $query->startform(-method=>'post', -name=>'form1', -action=>'./gdVecChooser.cgi');

if ($query->param('first') == 0)
{
	print ("<div id=\"notes\">");
	print ("This module allows you to select a vector by restriction characteristics or size.  This search is limited to the ");
	print ("(currently 39) vectors that GeneDesign knows.<br>");
	print space(2), ("&bull;GeneDesign uses a non-redundant list of restriction enzymes (one isoschizomer per site).<br>\n");
	print space(2), ("&bull;This search may take some time.  Please be patient.<br>\n");
	print ("See the <a href=\"../../gd/Guide/veccho.html\">manual</a> for more information.\n");
	print ("</div>");

	@cut = siteload();

	print ("\n<div id=\"gridgroup0\"> What sort of thing do you want to see in a vector?");
	print ("<div id=\"critbox\">\n");
	print ("<div id=\"critsep\">\n <span id=\"critlabel\">Size</span> <span id=\"criteria\">\n");
	print ("    <input type=\"radio\" name=\"crSize\" value=\"a\" checked> Any Size\n<br>");
	print ("    <input type=\"radio\" name=\"crSize\" value=\"g\"> Greater Than\n");
	print $query->textfield(-name=>'crsg', -default=>'6', -size=> 3, -maxlength=>2), "kb ";
	print ("<br><input type=\"radio\" name=\"crSize\" value=\"l\"> Less Than \n");
	print $query->textfield(-name=>'crsl', -default=>'4', -size=>3, -maxlength=>2), " kb\n";
	print ("  </span>\n  </div>", break(5), "\n  ");
	
	print ("<div id=\"critsep\">\n <span id=\"critlabel\">Number of Absent Sites</span> <span id=\"criteria\">\n");
	print ("<input type=\"radio\" name=\"crNabs\" value=\"a\" checked> Any<br>\n");
	print ("<input type=\"radio\" name=\"crNabs\" value=\"r\"> At Least\n");
	print $query->textfield(-name=>'crna', -default=>'10', -size=>3, -maxlength=>2);
	print ("  </span>\n  </div>", break(4), "\n  ");
	
	print ("<div id=\"critsep\">\n <span id=\"critlabel\">Restriction Sites</span><span id=\"criteria\">\n");
	print ("<input type=\"radio\" name=\"crResp\" value=\"a\" checked> Any<br>\n");
	print (" <div id=\"column1\" style=\"top:20;\">\n<input type=\"radio\" name=\"crResp\" value=\"r\"> Specify\n");
	print ($query->scrolling_list(-name=>'list', -values=>\@cut, -size=>8, -multiple=>'true'));
	print ("\n  \n", $query->button(-name=>'button', -value=>'> abs', -onClick=>'vpicka()'));
	print  $query->button(-name=>'button', -value=>'> uni', -onClick=>'vpickp()'), ("</div>\n");
	print (" <div id=\"column2\" style=\"top:22;\">\n   Must be Absent<br>", $query->scrolling_list(-name=>'absents', -size=>8, -multiple=>'true'));
	print ("\n  <div id=\"but\">\n", $query->button(-name=>'button', -value=>' <-- ', -onClick=>'vabandona()'), "</div></div>");
	print (" <div id=\"column3\" style=\"top:22; left:220;\">\n   Must be Unique<br>", $query->scrolling_list(-name=>'uniques', -size=>8, -multiple=>'true'));
	print ("\n  <div id=\"but\">\n", $query->button(-name=>'button', -value=>' <-- ', -onClick=>'vabandonp()'), "</div></div>");
	print "&nbsp;</span></div>\n", break(16);
	
	print $query->defaults('Defaults'), space(2), $query->button(-name=>'ShowAll', -onClick=>"VecMostPerm();", -label=>"Most Permissive Settings");
	print break(2);
	print $query->submit(-value=>"Show me the Vectors", -onClick=>"vselect()"), break(5);
	print $query->hidden(-name=>'first', -value=>1);
	
	print (" <script language=\"JavaScript\">\n");
	print ("  var v1 = document.form1.list;\n  var v2 = document.form1.absents;\n");
	print ("  var v3 = document.form1.uniques;\n");
	print ("  </script>\n");
	
	$query->endform;
	$query->end_html;
}
else
{
##-Get Selection Variables
	@absents  = $query->param('absents');
	@uniques = $query->param('uniques');
	$wsize = $query->param('crSize');
	$wsizemin = $query->param('crsg') if ($wsize eq 'g');
	$wsizemax = $query->param('crsl') if ($wsize eq 'l');
	$wnabs = $query->param('crNabs');
	$wnabsmin = $query->param('crna') if($wnabs eq 'r' );
	$wresc = $query->param('crResp');
#	print "@absents<br>@uniques<br>$wsize<br>$wsizemin<br>$wsizemax<br>$wnabs<br>$wnabsmin<br>";
	
	opendir(FOLDER, "vectors"); @vec = readdir(FOLDER); closedir(FOLDER);
	@vec = map {$_ =~/(p[A-Za-z0-9]+\s*[A-Za-z0-9]*)\.txt/} @vec;

	unless ($wsize eq 'a' && $wresc eq 'a' && $wnabs eq 'a')
	{
		@tcv = 0;
		foreach $v (@vec)
		{
			$allow = 1;
			$locstr = 'vectors/' . $v . '.txt';
			open IN, '<', $locstr;
			while (<IN>)
			{
				$vecseq = $1 if ($_ =~ /([ATCG]*)/ig);
			}
			close IN;
			$lenvec = length($vecseq);
		#exclude by size of vector
			$allow = 0 unless ($wsize eq 'a' || ($wsize eq 'g' && $lenvec >= ($wsizemin*1000)) || ($wsize eq 'l' && $lenvec <= ($wsizemax*1000)));
		#exclude by number of absent sites
			my @vabs = siterunner(1, $vecseq);
			$allow = 0 unless ($wnabs eq 'a' || ($wnabs eq 'r' && (@vabs-0) >= $wnabsmin));
		#exclude by site names
			foreach $t (@uniques)
			{
				@tempsite = siteseeker($t, $vecseq);
				$allow = 0 if ((@tempsite-0) != 1);
			}
			foreach $t (@absents)
			{
				@tempsite = siteseeker($t, $vecseq);
				$allow = 0 if ((@tempsite-0) > 0);
			}
			if ($allow == 1)
			{
				@answer[$tcv] = ([$v, $lenvec, $vecseq]);
				$tcv++;
				push @finarr, $v;
			}
		}
		print ("<div id=\"notes\">");
		print ("There are $tcv vectors that fit your criteria.<br>\n");
		print ("</div>");
	}

	else
	{
		
		foreach $v (@vec)
		{
			$locstr = 'vectors/' . $v . '.txt';
			open IN, '<', $locstr;
			while (<IN>)
			{
				$vecseq = $1 if ($_ =~ /([ATCG]*)/ig);
			}
			close IN;
			$lenvec = length($vecseq);
			@answer[$tcv] = ([$v, $lenvec, $vecseq]);
			$tcv++;
			push @finarr, $v;
		}
			print ("<div id=\"notes\">");
		print ("All of the vectors fit your criteria.<br>\n");
		print ("Did you mean to be more selective?<br>");
		print ("</div>");
	
	}
	
	
	
	print ("<div id=\"gridgroup0\">\n");
	print ("Summary: <br><textarea name=\"list\" rows=\"5\" cols=\"116\" readonly>@finarr</textarea>\n<br><br>");

	print ("\n<div id = \"gridgroup1\" style = \"background-color: \439AB;\">\n");
		print (" <span id = \"vNum\" style=\"height:20px; font-size:10px\" > # </span>\n");
		print (" <span id = \"vName\" style=\"height:20px; font-size:10px\" > vector name </span>\n");
		print (" <span id = \"vLength\" style=\"height:20px; font-size:10px\"> size (bp) </span>\n");
		print (" <span id = \"vAbs\" style=\"height:20px; font-size:10px\"> absent sites </span>\n");
		print (" <span id = \"vUni\" style=\"height:20px; font-size:10px\"> unique sites </span>\n");
	print break(2), "</div>";
	$j = 1;
	for ($r = 0; $r < $tcv; $r++)
	{
		@savedab = siterunner(1, $answer[$r][2]);
		@savedun = siterunner(2, $answer[$r][2]);
		$color = "ABC" if ($j % 2 == 0);
		$color = "CDE" if ($j % 2);
		print ("\n<div id = \"gridgroup1\" style = \"background-color: \43$color;\">\n");
		print (" <span id = \"vNum\"  >", $j, "</span>\n");
		print (" <span id = \"vName\" >", $answer[$r][0], "</span>\n");
		print (" <span id = \"vLength\">", $answer[$r][1], "</span>\n");
		print (" <span id = \"vAbs\"> @savedab </span>\n");
		print (" <span id = \"vUni\"> @savedun </span>\n");
		print break(10), ("&nbsp;<br>&nbsp;</div>\n");
		$j++;
	}
	print ("\n<div id = \"gridgroup1\" style = \"background-color: \439AB;\">\n");
	print ("&nbsp;<br>&nbsp;</div>\n");
	print ("<br><br>&nbsp;");
	print ("</div>\n</body>\n</html>\n");
}
