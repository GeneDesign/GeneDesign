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
	print ("<link href=\"$docpath/acss/mg.css\" rel=\"stylesheet\" type=\"text/css\">\n");	
	print ("<link href=\"$docpath/acss/pd.css\" rel=\"stylesheet\" type=\"text/css\">\n");
	print ("<link href=\"$docpath/acss/fn.css\" rel=\"stylesheet\" type=\"text/css\">\n");		
	print ("<link href=\"$docpath/acss/", cssbrowser(), ".css\" rel=\"stylesheet\" type=\"text/css\">\n") if (cssbrowser() ne '');
	print ("<script src=\"$docpath/scripts.js\" type=\"text/javascript\" language=\"Javascript\"></script>\n");
	print ("<META NAME=\"robots\" CONTENT=\"noindex, nofollow, noarchive\">\n");
	print ("<title>GeneDesign: Short Sequence Insertion</title></head>\n");
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
	print ("<a class=\"headli\">Short Sequence Insertion</a></div>");
	print $query->startform(-method=>'POST', -action=>'./gdOliIns.cgi', -name=>"form1");
if ($query->param('swit') eq '' && $query->param('remseq') eq '')
{
	print ("<div id=\"notes\">");
	print ("<strong>To use this module you need two nucleotide sequences, large and small.  An organism name is optional.</strong><br>\n");
	print ("Your nucleotide sequence will be searched for the short sequence you provide and as many iterations as possible will be inserted by changing whole codons ");
	print ("without changing the amino acid sequence.<br><br> ");
#	print ("See the <a href=\"$docpath/Guide/shortr.html\">manual</a> for more information.\n");
	print ("</div>");
	$nucseq = $query->param('passnucseq') if ($query->param('passnucseq') ne '');
	$nucseq = $query->param('nucseq') if ($query->param('passnucseq') eq '');
	print ("<div id=\"gridgroup0\">\nYour nucleotide sequence:<br>\n");
	print $query->textarea(-name=>'nuseq', -rows=>6, -columns=>100, -default=>$nucseq), break(1);
	print "Sequence to be Inserted: ", $query->textfield(-name=>'remseq', -columns=>20), break(2);
	print ("<div id=\"gridgroup1\" align =\"center\" style=\"position:absolute; top:170; \">\n");
	print $query->submit(-value=>" Insert short sequences ");
	print ("</div>\n</div>\n");
	print $query->endform, $query->end_html;
}
elsif ($query->param('swit') eq '' && ($query->param('nuseq') eq '' || length($query->param('remseq')) >= length($query->param('nuseq')) || length($query->param('remseq')) < 2 ))
{
	print ("<div id=\"notes\">");
	print ("You need a nucleotide sequence.<br>") if ($query->param('nuseq') eq '');
	print ("You need a short sequence to be inserted (at least two bp) <br> ") if ($query->param('remseq') eq '');
	print ("Your short sequence should be shorter than your nucleotide sequence.<br>\n") if ($query->param('remseq') >= length($query->param('nuseq')));
	print break(2), ("<input type=\"button\" value=\"Back\" onClick=\"history.go(-1)\">");
	print ("</div>");
}
elsif ($query->param('firstaround') ne 'no')
{
	my %inshash; my %therehash;
	$remseq = cleanup($query->param('remseq'), 0);
	$nucseq = cleanup($query->param('nuseq'), 0);
	$oldnuc = $nucseq;
	$aaseq  = translate($nucseq);
	@aaarr  = split('', $aaseq);
	my @answer;
	@allpos = transregex($remseq);	
	foreach $rg (@allpos)
	{	
		$rh = regres($rg, 2);
		while ($aaseq =~ /(?=$rh)/ig)
		{
			$sitsta = (pos $aaseq) +1;
			$currstring = "$sitsta: $remseq $rg";
			$inshash{$sitsta} = $currstring if ($sitsta != '');
		}
	}
	push @thisfreakyarr, $remseq;
	while ($nucseq =~ /(?=$remseq)/ig)
	{
		$sitsta = int(((pos $nucseq)) / 3)+1;
		$currstring = "$sitsta: $remseq";
		push @answer2, $currstring if ($sitsta != '');
		$therehash{$sitsta} = $currstring if ($sitsta != '');
	}
	foreach $treg (sort {$a <=> $b} keys %inshash)	{	push @answer, $inshash{$treg} unless (exists($therehash{$treg}));	}
	$len = length($nucseq);
	@aa = split('', translate($nucseq));
	@nuc = split('', $nucseq);
	$organism = $query->param('org');
#	print ("$nucseq, ", translate($nucseq), ", $remseq, $organism<br>\n@answer\n<br>@answer2<br>");
	print ("<div id=\"notes\">");
	print "\nI was asked to insert the sequence $remseq. ", (@answer2-0), " instances are already present and will not be annotated here. ";
	print @answer-0, " possible insertion sites have been found.";
	print ("  <input type=\"submit\" value=\" Just insert the instances I have selected \" onClick=\"OliISum(0);\">\n");
	print ("  <input type=\"submit\" value=\" Insert all possible instances \" onClick=\"OliISum(1);\">\n");
	print break(1);
	print "</div>"; 

	print ("<div id=\"gridgroup0\">\n");
	@hits = 	annpsite(\@aaarr, 1, \@answer, \@thisfreakyarr); 
	$top += 500;
	foreach $trep (@answer)
	{
		$tempstr = $trep . "\n";
		push @answer3, $tempstr;
	}
	print ("   <input type=\"hidden\" name=\"org\" value=\"", $query->param('org'), "\">\n");
	print ("   <input type=\"hidden\" name=\"swit\" value=\"some\">\n");
	print ("   <input type=\"hidden\" name=\"remseq\" value=\"$remseq\">\n");
	print ("   <input type=\"hidden\" name=\"nucseq\" value=\"$nucseq\">\n");
	print ("   <input type=\"hidden\" name=\"allsites\" value=\"@answer3\">\n");
	print ("   <input type=\"hidden\" name=\"firstaround\" value=\"no\">\n");
	print (" </div>");
}
if ($query->param('swit') eq 'all' || $query->param('swit') eq 'some')
{
	$org = $query->param('org');
	$nucseq = $query->param('nucseq');
	$aaseq = translate($nucseq);
	$remseq = $query->param('remseq');
	undef @newarr;
	$rh = regres($remseq);
	@aa = split('', translate($nucseq));
	@nt = split('', $nucseq);	$nstring = 'NNNNNNNN';
	if ($query->param('swit') eq 'all')
	{
		@newarr = split('\n', $query->param('allsites')); 
	}
	elsif ($query->param('swit') eq 'some')
	{
		@array = split('\n', $query->param('allsites'));
		for ($m = 1; $m <(@aa+1); $m++)
		{
			$curstr = 'site' . $m;
			$box = $query->param($curstr);
			$box = $1 if ($box =~ /\W([A-Za-z0-9]*)/);
			if($box ne '' && $box ne '-')
			{
				$aapos = $m;
				foreach $l (@array)
				{
					$t = ' ' . $l;
					$o = $aapos;
					$aarecogniz = $1 if ($t =~ / $o: $box ([A-Z*]+)/);
				}
				$currstring = "$aapos: $box $aarecogniz";
				push @newarr, $currstring;
			}
		}
	}
	foreach $instance (@newarr)
	{
		if ($instance =~ /([0-9]+)\: [A-Z]+ ([A-Z]+)/)
		{	
			$curraapos = $1 - 1; $curraaseq = $2;  $currnucpos = ($curraapos *3); 
			$matchers = ''; $diff = (length($curraaseq)*3) - length($remseq);
			@reccedstr = split('', substr($aaseq, $curraapos, length($curraaseq)));
			for ($i = 0; $i <= $diff; $i++)
			{
				$matchers = ((substr $nstring, 0, $i) . $remseq);
				$matchers = $matchers . 'N' while (length($matchers) != length($curraaseq)*3);
				$check ='';
				$offset = 0;
				for ($j = 0; $j < (int(length($matchers) / 3)); $j++)
				{
					@checker = getaaa(substr($matchers, $offset, 3));
					for ($g = 0; $g < (@checker-0); $g++)	{	$check .= $checker[$g] if ($reccedstr[$j] eq $checker[$g]);	}
					$offset += 3;
				}
				last if ($check eq substr($aaseq, $curraapos, length($curraaseq)));
			}
			$offset = 0; $newseq = '';
			for ($i = 0; $i < (length( substr($nucseq, $currnucpos, length($curraaseq)*3)) / 3); $i++)
			{
				$curcod = substr  substr($nucseq, $currnucpos, length($curraaseq)*3), $offset, 3;
				$curtar = substr $matchers, $offset, 3;
				@workaal = getaaa($curcod);
				foreach $g (@workaal)
				{
					@workcod = getcods($g);
					if ($curcod ne $curtar && $curtar ne 'NNN')
					{
						foreach $l (@workcod)
						{
							$tot = compareseqs($curtar, $l);
							$newseq .= $l if ($tot == 1);
							last if ($tot == 1);
						}
					}
					else
					{
						$newseq .= $curcod;
					}					
				}
				$offset += 3;
			}		
		}
	#	print "$currnucpos, $curraapos, aaseq ", substr($aaseq, $curraapos, length($curraaseq)), " nucseq ", substr($nucseq, $currnucpos, length($curraaseq)*3), " $matchers, $newseq, ", translate ($newseq), "<br>";
		$newcurrstr = "$currnucpos..$newseq";
		push @tobeinsarr, $newcurrstr;
	}
	$newnuc = ''; $curpos = 0; print "<br>"; $cannotdo = 0; $cananddid= 0;
	foreach $treeeg (@tobeinsarr)
	{
		if ($treeeg =~ /([0-9]+)\.\.([A-Z]+)/) { $thispos = $1; $thisnew = $2; }
		unless ($thispos <= $curpos)
		{
			$newnuc .= substr ( $nucseq, $curpos, (($thispos)-$curpos));
			$newnuc .= $thisnew;
			$curpos = length ($newnuc);
#			print "..$thispos, $curpos<br>";
			$cananddid++;
		}
		else
		{
			$cannotdo++;
		}
	}
	$newnuc .= substr ($nucseq, $curpos, (length($nucseq)-$curpos));
print "Translation error! please notify admin<br>" if (translate($nucseq) ne translate($newnuc));
	if ($cannotdo > 0)
	{
		print "$cannotdo possible instance(s) of $remseq could not be inserted because they overlapped with other insertions that were made.\n";
		print break(1);
	}
	print "$cananddid instance(s) of $remseq were inserted.\n";
	print "</div>"; 
	print break(1);
	print ("<div id=\"gridgroup0\">Your altered nucleotide sequence:\n");
	print $query->textarea(-name=>'nusseq', -rows=>6, -columns=>120, -default=>$newnuc), break(1);
	@newal = ezalign($nucseq, $newnuc);
		@bcou = count($newnuc); 
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
