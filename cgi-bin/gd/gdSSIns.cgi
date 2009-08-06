#!/usr/bin/perl

use File::Find;
use PRISM;
use RESite;
use PMLol;
use CGI;
$query = new CGI;
print $query->header;
##- Open it up - css, javascript, and header.  open form
	print ("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">\n");
	print ("<html>\n<head>\n<meta http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\">\n");
	print ("<link href=\"$docpath/acss/re.css\" rel=\"stylesheet\" type=\"text/css\">\n");
	print ("<link href=\"$docpath/acss/mg.css\" rel=\"stylesheet\" type=\"text/css\">\n");	
	print ("<link href=\"$docpath/acss/pd.css\" rel=\"stylesheet\" type=\"text/css\">\n");
	print ("<link href=\"$docpath/acss/fn.css\" rel=\"stylesheet\" type=\"text/css\">\n");	
	print ("<link href=\"$docpath/acss/", cssbrowser(), ".css\" rel=\"stylesheet\" type=\"text/css\">\n") if (cssbrowser() ne '');
	print ("<script src=\"$docpath/scripts.js\" type=\"text/javascript\" language=\"Javascript\"></script>\n");
	print ("<META NAME=\"robots\" CONTENT=\"noindex, nofollow, noarchive\">\n");
	print ("<title>GeneDesign: Silent Site Insertion</title></head>\n");
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
	print ("<a class=\"headli\">Silent Site Insertion</a></div>");
	print $query->startform(-method=>'post', -action=>'./gdSSIns.cgi', -enctype=>'application/x-www-form-urlencoded', -name=>"form1");

##- notes on using Silent Site Insertion
if ($query->param('swit') eq '' && $query->param('nextrem') eq '')
{
	print ("<div id=\"notes\">");
	print ("<strong>To use this module you need a coding nucleotide sequence. <em>Don't Panic!</em> This page is simpler than it looks.</strong><br>\n");
	print ("Your nucleotide sequence will be searched for possible silent, unique insertions and you will be prompted to choose as many as you like for insertion.<br>");
	print ("It is recommended that you only use ORFs with this module because sites will be inserted without changing the first frame amino acid sequence. ");
	print ("If your coding sequence is not in the first frame it will be changed.  <br><em>Please Note:</em><br> ");
	print space(2), ("&bull;You can only choose <em>one</em> of the \"Sites to be Inserted\" options.  These options define which possible \n");
	print ("insertions are the most pertinent (i.e., those that are absent from a vector are more interesting than those that are not.)<br>");
	print space(2), ("&bull;If you want the program to consider all possible insertions as equally important, without defining a vector or picking enzymes, use the default (blank vector sequence).<br>");
	print space(2), ("&bull;Some vectors are better choices than others! If you pick a vector with very few absent sites, you will have a much more difficult time in automated selection.<br>");
	print space(2), ("&bull;You do not have to select any \"Forbidden Sites\".  If you do, these sites will not be considered for insertion, and if they appear in the sequence after editing they ");
	print ("will be removed.<br>\n");
	print space(2), ("&bull;The Enzyme Selection criteria  only apply if you are planning to let the program pick the sites to be inserted. If you will be picking manually you can ignore this section.<br>");
	print space(2), ("&bull;The looser the enzyme criteria you provide, the better the results.  If you are getting poor return in automated selection, try allowing a broader spectrum of enzymes.<br>\n");
	print ("See the <a href=\"$docpath/Guide/ssi.html\" target=\"blank\">manual</a> for more information.\n");
	print ("</div>");
##-carry organism
	$org = $query->param('org');

##-load up the cutters, get all the vector names from directory 'vectors' and list into array @vec
	@cut = siteload();
	opendir(FOLDER, "vectors"); @vec = readdir(FOLDER); closedir(FOLDER);
	@vec = map {$_ =~/(p[A-Za-z0-9]+\s*[A-Za-z0-9]*)\.txt/} @vec;

	$aaseq = $query->param('1aaseq');
	$nucseq = $query->param('passnucseq') if ($query->param('passnucseq') ne '');
	$nucseq = $query->param('nucseq') if ($query->param('passnucseq') eq '');
	$aaseq = translate($nucseq);
##-print nucleotide and amino acid sequences, allow for browser differences.  Check if new into SSI or if passed from other module
	$rows = 10; $columns = 60;
	$rows = 9 if (cssbrowser() eq 'ff' || cssbrowser() eq 'wie'); $columns = 54 if (cssbrowser() eq 'ff' || cssbrowser() eq 'wie');
	print ("<div id=\"gridgroup0\">\n<div id = \"gridgroup1\">\n");
	if( $aaseq eq "" && $nucseq eq "")
	{
		print ("<div id =\"ntseq\">Enter a nucleotide sequence:<br>\n");
		print $query->textarea(-name=>'nucseq', -rows=>$rows, -columns=>$columns, -default=>$nucseq) if cssbrowser() eq '';
		print ("\n</div>\n<div id = \"aaseq\">Your amino acid Sequence:<br>\n");
		print $query->textarea(-name=>'aaseq', -rows=>$rows, -columns=>$columns, -readonly=>'true', -default=>'No sequence yet: Starting with nucleotides');
		print ("\n</div>\n", $query->hidden(-name=>'skipopt', value=>'yes'));
	}
	elsif ( $aaseq ne "")
	{
		print ("<div id =\"ntseq\">Your nucleotide sequence (", length($nucseq), " bp):<br>\n");
		print $query->textarea(-name=>'nucseq', -rows=>$rows, -columns=>$columns, -readonly=>'true', -default=>$nucseq);
		print ("</div>\n<div id = \"aaseq\">Your amino acid sequence from the first frame (", length($aaseq), " aa):<br>\n");
		print $query->textarea(-name=>'aaseq', -rows=>$rows, -columns=>$columns, -readonly=>'true', -default=>$aaseq);
		print ("</div>\n");
	}
	
##-SITES TO BE ADDED
	print ("<div id=\"gridgroup2\" style=\"top:180; width:100%;\">\n");
	print ("<center><strong>Sites to be Inserted</strong>: choose one of the following three options.</center>\n");
	print ("<div id=\"gridgroup2\" style=\"top:10;\">\n");
##-user can pick sites to be considered absent one by one
	print (" <div id=\"pickers\">\n  <div id=\"head1\">\n   <input type=\"radio\" name=\"vecpic\" value=\"picked\">\n");
	print ("  Create a list of enzymes to be considered for insertion\n  </div>\n");
	print ("  <div id=\"column1\">\nCutters<br>",   $query->scrolling_list(-name=>'cutters', -values=>\@cut, -size=>8, -multiple=>'true'));
	print ("   <div id=\"but\">\n", $query->button(-name=>'button', -value=>' --> ', -onClick=>'pick()'), "\n   </div>\n  </div>\n");
	print ("  <div id=\"column2\">\nTo Insert<br>", $query->scrolling_list(-name=>'absentsites', -size=>8, -multiple=>'true'));
	print ("\n   <div id=\"but\">\n", $query->button(-name=>'button', -value=>' <-- ', -onClick=>'abandon()'),"\n   </div>\n  </div>\n");
	print break(14), ("&nbsp;</div>\n");
##-user can select a vector from pulldown
	print (" <div id=\"vectors\">\n  <div id=\"head2\">\n   <input type=\"radio\" name=\"vecpic\" value=\"chosen\">\n");
	print ("  Select a vector from the following list and have the absent sites determined\n  </div>\n");
	print ("  <div id=\"column3\">\n", $query->popup_menu(-name=>'vector', -values=>\@vec));
	print ("\n  </div>\n", break(14), "&nbsp;</div>\n");
##-user can provide nuc sequence and absent sites will be determined
	print (" <div id=\"dunnos\">\n  <div id=\"head3\">\n   <input type=\"radio\" name=\"vecpic\" value=\"unknown\" checked>\n");
	print ("  Provide the name and nucleotide sequence of a vector and have the absent sites determined\n  </div>\n");
	print ("  <div id=\"column3\">\n");
	$rows = 10; $columns = 39; 
	$rows = 8 if (cssbrowser() eq 'ff' || cssbrowser() eq 'wie'); $columns = 30 if (cssbrowser() eq 'ff' || cssbrowser() eq 'wie');
	print ("   Name:", $query->textfield(-name=>"vecname", -size=>20, -maxlength=>20), "<br>\n");
	print ("   ", $query->textarea(-name=>"vecseq", -class=>monospace, -rows=>$rows, -columns=>$columns));
	print "\n  </div>\n", break(14), "&nbsp;</div>\n</div></div>\n";

##-SITES TO BE REMOVED
	print ("<div id=\"gridgroup2\" style=\"top:420;\">\n");
	print ("<div id=\"gridgroup2\" style=\"top:10;\">\n");
##-pick the sites that must not appear
	print (" <div id=\"pickers\">\n  <div id=\"head1\">\n");
	print ("<strong>Forbidden Sites</strong>\n  </div>\n");
	print ("  <div id=\"column1\">\n   Cutters<br>", $query->scrolling_list(-name=>'cuttersnono', -values=>\@cut, -size=>8, -multiple=>'true'));
	print ("   \n<div id=\"but\">\n", $query->button(-name=>'button', -value=>' --> ', -onClick=>'pickn()'));
	print ("\n   </div>\n  </div>\n  <div id=\"column2\">\n   To Remove<br>", $query->scrolling_list(-name=>'absentsnono', -size=>8, -multiple=>'true'));
	print ("\n   <div id=\"but\">\n", $query->button(-name=>'button', -value=>' <-- ', -onClick=>'abandonn()'), ", \n   </div>\n  </div>\n");
	print break(14), "&nbsp;</div>\n";
	
##-ENZYME CRITERIA
	print (" <div id=\"crits\">\n  <div id=\"head4\">\n");
	print (" <strong>How do you want me to evaluate sites for automated insertion?</strong>\n  </div>\n");
	print ("  <div id=\"critbox\">\n");
	enzmenu();
	print"&nbsp;</div></div></div></div>\n\n\n";
	
##-wrap it up - submit and javascripts
	print ("<div id=\"gridgroup1\" style = \"position:absolute; top: 800;left:75;\">\n");
	print ($query->submit(-value=>" Next Step: Site Selection ", -onClick=>"selectem()"), break(7), "&nbsp;\n");
	print $query->hidden(-name=>'codons', -value=>join (' ', @array));
	print $query->hidden(-name=>'swit', -value=>'pd');
	print ("<input type=\"hidden\" name=\"org\" value=\"$org\">");
	print (" <script language=\"JavaScript\">\n");
	print ("  var menu1 = document.form1.cutters;\n  var menu2 = document.form1.absentsites;\n");
	print ("  var menn1 = document.form1.cuttersnono;\n  var menn2 = document.form1.absentsnono;\n");
	print ("  var flag1 = document.form1.vecpic[0];\n  var flag2 = document.form1.vecpic[1];\n  var flag3 = document.form1.vecpic[2];\n");
	print ("  </script>\n");
	print ("</div>\n</div>\n", $query->endform, $query->end_html);
}
##check for blank entry
if ($query->param('swit') ne '' && $query->param('nucseq') eq '')
{
	{
		print ("<div id=\"notes\" style=\"text-align:center;background-color: yellow\">");
		print ("<strong>You didn't provide a nucleotide sequence.</strong><br>");
		print break(1), ("<input type=\"button\" value=\"Back\" onClick=\"history.go(-1)\">");
		print ("</div>");
	}
}
###all runs with pulldown menus
if ($query->param('swit') eq "pd" || $query->param('swit') eq 'ih' || $query->param('nextrem') ne '')
{
	$org = $query->param('org');
	$aaseq  = $query->param('aaseq');
	$nucseq = cleanup($query->param('nucseq'), 1);
	$nucseq = $query->param('oldnucseq') if ($query->param('nextrem') ne '');
	$skipopt = $query->param('skipopt');
	$aaseq = translate($nucseq) if ($skipopt eq "yes");
	$aaseq  = cleanup($aaseq, 2);
	@aa = split('', $aaseq);
	$size   = length($aaseq);
	$actual = 0;

	if ($query->param('nextrem') eq '')
	{
	#check for orf.  if orf is not first frame and uninterrupted, print an alarm.
		$war1 = 1 if (substr($nucseq, 0, 3) ne 'ATG');
		@war2 = stopfinder($nucseq, 1); $war3 = 1 if (@war2 && ((@war2-0 > 1 ) || (($war2[0]*3) != length($nucseq))));
		if (($war1 || $war3) && $nucseq)
		{
			print ("<div id = \"notes\" style = \"background-color: yellow\">\n");
			print "<strong>Warning:</strong> Your sequence is not a simple coding sequence.<br>";
			print "Your sequence does not begin with ATG.<br>" if ($war1);
			print "Your sequence has at least one internal stop codon in the first frame.<br>" if ($war3);
			print "It is still possible to insert landmarks into this sequence but you should check to be sure that crucial features are not compromised.";
			print ("</div>");
		}
		print ("<div id=\"notes\">");
		print ("<em>What am I looking at?</em><br>");
		print ("Your sequence is presented in amino acid form.  Every dot and line connect to a pulldown menu that contains enzymes.  Every enzyme ");
		print ("represents a possible unique silent site introduction.  Where there are no dots or lines, there are no possible unique introductions. Pulldown menus ");
		print ("connected in red contain one or more enzymes that are absent from the vector you defined.  Within those pulldown menus, the ");
		print ("absent enzymes are prefaced with asterisks *. Pulldown menus connected in black contain no enzymes that are absent from the vector. Pulldown ");
		print ("menus connected in blue contain an enzyme that has been selected for insertion by the program.  Within those pulldown menus, the selected ");
		print ("enzyme is prefaced with a dot ·. There is an asterisk under every tenth amino acid, for placekeeping purposes.<br>");
		print space(2), "&bull;You will only see blue dots and lines if you have selected \"Pick Sites For Me\"!<br><br>";
		print ("You can select as many enzymes as you like from the pulldown menus.  Or you can have the program select sites for you.  For automated selection, define ");
		print ("an amino acid interval and hit \"Pick Sites For Me\".  The program will select enzymes on that interval using the criteria you defined on the last screen. ");
		print ("You will be given an opportunity to review and edit the program's choices before modifications are made.<br><br>");
		print ("When you are satisfied with your choices or the program's selections, hit \"Continue\". Your sequence will be modified and you will be given a summary of changes.<br>\n");
		print ("See the <a href=\"$docpath/Guide/ssi.html\" target=\"blank\">manual</a> for more information.\n<br>");
		print space(2), "&bull;Please wait for the page to load completely before hitting \"Continue\" or \"Pick Sites For Me\"!";
		print ("</div>");
	}
}
###first run
if ($query->param('swit') eq "pd")
{
	##-get ranking information for site selection
	@ends   = $query->param('crEnds');
	push @ends, $query->param('crEndss');	
	@cuts   = $query->param('crCuts');
	push @cuts, $query->param('crCutss');
	push @leng, $query->param('crLengs');
	@ambi   = $query->param('crAmbi');
	push @ambi, $query->param('crAmbis');
	@pric	= ($query->param('crPrlo'), $query->param('crPrhi'));
	push @pric, $query->param('crPrir');
	$diss	= $query->param('crDisa'); $diss =~ s/\s//g;
	@disa	= split ",", $diss;
	$alls	= $query->param('crAllo'); $alls =~ s/\s//g;
	@allo	= split ",", $alls;
	$enzcrit  = (join "", @ends) . "x" . (join "", @cuts) . "x" . (join "", @leng) . "x" . (join "", @ambi) . "x" . (join ",", @pric);
	undef @SitArr;
	@cutters = siteload();
	$y = 0;
	foreach $n (@cutters)
	{
		$SitArr[$y] = new RESite();
		$SitArr[$y]->CutterName($n);
		$SitArr[$y]->LoadInfo();
		$y++;
	}
	@SitArr = grep {$_->Sticky ne ''} @SitArr;
	@SitArr = grep {$_->CompareEnds  (\@ends)  } @SitArr;
	@SitArr = grep {$_->CompareLength(\@leng)} @SitArr;
	@SitArr = grep {$_->CompareCut	 (\@cuts)} @SitArr;
	@SitArr = grep {$_->CompareAmbig (\@ambi)} @SitArr;
	@SitArr = grep {$_->ComparePrice(\@pric) } @SitArr;
	@SitArr = grep {$_->SeqFilter (\@disa, 1)} @SitArr;
	@SitArr = grep {$_->SeqFilter (\@allo, 2)} @SitArr;
	@SitArr = sort {$a->UPrice <=> $b->UPrice} @SitArr;
	@finarr = map ($_->CutterName, @SitArr);
	$first = 1;
	$result = `./findsites $nucseq $aaseq`;
	$vecpic = $query->param('vecpic');
	undef @absents;
	@array  = split("\n", $result);
	$s        = 0;
##-get banned information
	@nonos = $query->param('absentsnono');
	unshift @nonos, "";
	%banned = map { $_ => 1 } @nonos;
##-get vector information		
	if ($vecpic eq "picked")
	{
		@absents = $query->param('absentsites');
		$vecname = "(no vector selected)";
	}
	elsif ($vecpic eq "chosen")
	{
		$vecname = $query->param('vector');
		$locstr = 'vectors/' . $vecname . '.txt';
		open IN, '<', $locstr;
		while (<IN>)
		{
			$vecseq = $1 if ($_ =~ /([ATCG]*)/ig);
		}
		close IN;
		@absents = siterunner(1, $vecseq, %banned);
	}
	elsif ($vecpic eq "unknown")
	{
		$vecname = $query->param('vecname');
		$vecname = "(vector not named)" if ($vecname eq '');
		$vecseq = $query->param('vecseq');
		@absents = siterunner(1, $vecseq, %banned);
	}
	$vecseq = cleanup($vecseq, 1);
	print ("<div id=\"notes\">");
	print ("You can specify sites to flank the sequence.  I will remove them from the synthetic sequence (if possible). ");
	print ("If no sites are available, you did not select any sites to be considered forbidden in the last screen.<br>\n");
	print "5\':", $query->popup_menu(-name=>'5puni', -values=>\@nonos, -default=>''), space(2);
	print "3\':", $query->popup_menu(-name=>'3puni', -values=>\@nonos, -default=>''), break(1);
	print "</div>", break(1);
}

###Second+ Time Around, the choosing
if ($query->param('swit') eq 'ih' || $query->param('nextrem') ne '')
{
	@Nomogo = $query->param('nextrem');
	$first    = 0;
	$vecname   = $query->param('vector');
	$result   = $query->param('results');
	$uni5     = $query->param('5puni');
	$uni3     = $query->param('3puni');
	@nonos    = split(" ", $query->param('banned'));
	foreach $t (@Nomogo)
	{
		push @nonos, $t;
	}
	%used     = map {$_ => -3} @nonos; 
	@absents  = split(" ", $query->param('absentsites'));
	@rant	  = split(" ", $query->param('rant'));
	@array   = split("\n", $result);
	$enzcrit = $query->param('enzcrit');
	$r        = 0;
	$curaa    = 0;
	$pos1     = 0;
	@count;
	%counta;
	%countb;
	if (@Nomogo)
	{
		for ($be = 0; $be < (@absents-0); $be++)
		{
			foreach $t (@Nomogo)
			{
				splice @absents, $be, 1 if ($absents[$be] eq $t);
			}
		}
	}
##-puts every hit into arrays @good1(site) and @good2(name) 
	@hits    = split(" ", $query->param('hits'));
	@good1   = map { $_ =~/([0-9]+)\./}         @hits;
	@good2   = map { $_ =~/\.([A-Za-z0-9]+)\:/} @hits;
##-counts the occurence of each absent cutter(into hash %counta), determines how many cuts per chunk (@count)
	$r = 0;
	$num      = $query->param('number');
	$asmany   = int((@aa-0)/$num);
	for($i = 0; $i < $asmany; $i++)
	{
		while ($r != $num)
		{
			$curaa++;
			$r++;
		}
		for ($j = 0; $j < (@good2-0); $j++)
		{
			if ($good1[$j] < $curaa && $good1[$j] > $pos1)
			{
				$count[$i]++;
				$counta{$good2[$j]}++;
			}
		}
		$r = 0;
		$pos1 = $curaa-1;	
	}
##-all cutters that cut at least once are put into the hash %countb
	while (($key, $value) = each %counta)
	{
		$countb{$key} = $value if ($value != 0);
	}
##-cutters are @ord(ered) in %countb by number of cuts, %counta initialized
	@ord = (sort {$countb{$a} <=> $countb{$b}} keys %countb);
	undef %counta;
##-loads the contents of @count into %counta, then figures out @working order by sorting %counta
	$r=0;
	foreach (@count)
	{
		$counta{$r} = $_;
		$r++;
	}
	@working = (sort {$counta{$a} <=> $counta{$b}} keys %counta);
	undef %counta; undef %countb;
	shift @working;
##-the relative values of the cutters, as defined by ze user
	undef %rank;
	$r = 0;
	foreach (@rant)
	{
		$rank{$_} =  $r;
		$r++;
	}

##-check to make sure that absents from vector are absent from sequence- otherwise, write to %used
##-fix for problem with c code???
	@pres = siterunner(3, $nucseq);
	@pres = sort @pres;
	@abn  = sort @absents;
	foreach $item (@pres)
	{
		foreach $gtem (@abn)
		{
			if ($item eq $gtem)
			{
				$used{$item} = -3;
				last;
			}
		}
	}
	$actual = 0;
##-goes through the cutters present in each chunk, and picks them approximately $num
##-amino acids apart.  puts used cutters into %used to prevent duplications. puts selected cutters 
##-and sites into hash $selly{name} = site.  uses the same modular swing as the oligo chooser
	foreach $i (@working)
	{
		$i++;
		$n     = 1;
		$start = ((($i-1)*$num)+1);
		$end   = (($i)*$num);
		$sum   = 0;
		$m     = 0;
		$cuts  = $count[$i-1];
		while ($m < $i)
		{
			$sum += $count[$m];
			$m++;
		}
		$hitstart = ($sum-$cuts);
		$hitend = ($sum);
		$ask = 0;
		$gotcha = 0;
		unless ($cuts == 0)
		{ 
			for ($j = $hitstart; $j <= $hitend; $j++)
			{
				%used = mutexclu(%used);			
				$target = $end;
				$n = 0;
				while ($gotcha != 1)
				{
					$target = ($target + $n) if ($n %2 == 0);
					$target = ($target - $n) if ($n %2 != 0);
					last if ($target < 0 || $n > (.5*$num) || $n < (0-(.5*$num)) || $target > $size);
					$n++;
					undef @rate;
					undef @rate2;
					$m = $hitstart;
					while ($m <= $hitend)
					{
						$r=0;
						if (exists $rank{$good2[$m]} && $good1[$m] == $target)
						{
							$rate[$m] = $good2[$m]; 
							$rate2[$m] = $rank{$rate[$m]}+1;
							$r++;
						}
						$m++;
					}
					$m = $#rate-$r;
					$curlo = (@rant-1);
					while ($m <= $#rate)
					{
						$ask = 1 if (exists $used{$good2[$m]} && $good1[$m] == $target);
						if ( $good1[$m] == $target && $ask == 0 && $rate2[$m] < $curlo && $rate2[$m] > 0)
						{
							$actual++ unless (exists $selly{$good2[$m]});
							$selly{$good2[$m]} = $good1[$m];
							$used{$good2[$m]} = $good1[$m];
							$rate2[$m] = $curlo;
							$diff = (($end-$good1[$m])+1) if ($lastc == undef);
							$lastc = $good1[$m];
							$gotcha = 1;
							$n = 1;
							last if ($gotcha == 1);
						}
						$ask = 0;	
						$m++;
					}		
				}
				last if ($gotcha == 1);
			}	
		}
		else
		{
		}		
	}
##-@ord is unused cutters
	@ord = grep {! exists $selly{$_}} @ord;
	$remsize = @ord;
	$perc = int(($actual/(($size/$num)-1))*100);
	$perf = int($size/$num);

	print ("<div id=\"notes\">");
	print ("In this $size aa sequence I chose $actual cutters on the interval $num, leaving unused $remsize absent cutters.<br>\n");
	print ("This represents an efficiency of $perc% (perfect number is $perf)<br> \n");
	print space(2), ("&bull;Remember that the fewer sites absent from your vector, the lower the efficiency is likely to be.<br>");
	print ("I will place $uni5 at the 5' end and $uni3 at the 3' end of the gene.<br>\n") if ($uni5 || $uni3);
	print ("Make any changes you like and select continue, or have me do it again.<br>\n");
	print ("</div>");	
	if ((@Nomogo-0) != 0)
	{
		print ("<div id = \"notes\">\n");
		print "<strong>Reconsideration</strong><br>";
		print "Enzyme(s) @Nomogo are no longer eligible for automated introduction.";
		print ("</div>");
	}
}	

###begin global pd output
if ($query->param('swit') eq 'pd' || $query->param('swit') eq 'ih' || $query->param('nextrem') ne '')
{
	print ("  <input type=\"submit\" value=\" Continue to Summary \" onClick=\"SSISum(0);\">\n");

	print ("  <strong>or</strong> <input type=\"submit\" value=\"Pick Sites For Me\" onClick=\"SSISum(1);\">\n");
	print ("  on the amino acid interval of \n <input name=\"number\" type=\"text\" size=\"5\" maxlength=\"4\" value=\"50\">\n");
	print ("<div id=\"gridgroup0\">\n");
	 @hits = annpsite(\@aa, 1, \@array, \@absents) if ($first == 1);
	annpsite(\@aa, 0, \@array, \@absents, \%selly) if ($first != 1);

	$top += 500;
	print (" </div>");
	print (" <div id = \"gridgoup1\">\n");
	print ("  <input type=\"hidden\" name=\"swit\" value=\"ih\">\n");
	print ("  <input type=\"hidden\" name=\"results\" value=\"$result\">\n");
	print ("  <input type=\"hidden\" name=\"nucseq\" value=\"$nucseq\">\n");	
	print ("  <input type=\"hidden\" name=\"aaseq\" value=\"$aaseq\">\n");
	print ("  <input type=\"hidden\" name=\"banned\" value=\"@nonos\">\n");
	print ("<input type=\"hidden\" name=\"org\" value=\"$org\">");
	print ("  <input type=\"hidden\" name=\"codons\" value=\"", $query->param('codons'), "\">\n");
	print ("  <input type=\"hidden\" name=\"enzcrit\" value=\"$enzcrit\">\n");
	print ("  <input type=\"hidden\" name=\"hits\" value=\"@hits\">\n");
	print ("  <input type=\"hidden\" name=\"absentsites\" value=\"@absents\">\n");
	if ($first == 1)
	{
		print ("  <input type=\"hidden\" name=\"rant\" value=\"@finarr\">\n");
		print ("  <input type=\"hidden\" name=\"vector\" value=\"$vecname\">\n");
	}
	if ($first == 0)
	{
		print ("  <input type=\"hidden\" name=\"rant\" value=\"@rant\">\n");
		print ("  <input type=\"hidden\" name=\"vecname\" value=\"$vecname\">\n");
		print ("  <input type=\"hidden\" name=\"5puni\" value=\"$uni5\">\n");
		print ("  <input type=\"hidden\" name=\"3puni\" value=\"$uni3\">\n");
		print ("  <input type=\"hidden\" name=\"inte\" value=\"$num\">\n");
	}
#	print (" <script language=\"JavaScript\">\n  var hidfld = document.form1.swit;\n</script>\n");

	print (" </div>\n</form>\n</body>\n</html>\n");
}

if ($query->param('swit') eq 'wu')
{
	$org     = $query->param('org');
	$aaseq   = $query->param('aaseq');
	$nucseq  = $query->param('nucseq');
	$vecpic  = $query->param('vector');
	$uni5    = $query->param('5puni');
	$uni3    = $query->param('3puni');
	$nonos   = $query->param('banned');
	$num	 = $query->param('inte');
	undef @Error1; undef @Error2; undef @Error3; undef @Error4; undef @Error5;
	$nstring = 'NNNNNNNN';
	@array  = split("\n", $query->param('results'));
	@aa     = split('', $aaseq);
	@nt	    = split('', $nucseq);
	@nonos  = split(" ", $nonos);
	$size   = length($aaseq);
	$nsize  = length($nucseq);
	$nend   = $nsize+2;
	undef @SitArr; undef @posarr;
	%banned = map{$_ => 0} @nonos;


##-pick out the sites to be introduced, create new Objects in RESite for them
	$y = 0;
	for ($m = 1; $m <(@aa+1); $m++)
	{
		$curstr = 'site' . $m;
		$box = $query->param($curstr);
		$box = $1 if ($box =~ /\W([A-Za-z0-9]*)/);
		if($box ne '' && $box ne '-')
		{
			$SitArr[$y] = new RESite();
			$SitArr[$y]->SiteNumber($m);
			$SitArr[$y]->CutterName($box);
			$y++;
		}
	}
	
	@Error1 = map  ($_->CutterName, @SitArr);
##-process each site to be introduced
	foreach $m (@SitArr)
	{
		$n = $m->CutterName;
		$m->LoadInfo();
	##-figure out what amino acids the enzyme is recognizing
		foreach $l (@array)
		{
			$t = ' ' . $l;
			$o = $m->SiteNumber;
			$m->AARecogniz($1) if ($t =~ / $o: $n ([A-Z*]*)/);
			undef $t;
		}
	##-figure out the starting position in the nuc sequence
		$m->NtPosition((($m->SiteNumber)*3)-2);
		push @posarr, $m->NtPosition;
	##-figure out the exact bit of nuc sequence to be fiddled with
		undef $tobech;
		$len = length($m->AARecogniz);
		for ( $i = (($m->NtPosition) - 1); $i <= (($m->NtPosition) + (($len*3) - 2)); $i++ )
		{
			$tobech .= $nt[$i];
		}
		$m->MustChange($tobech);
		$tobechlen = length($m->MustChange);
		$recsitlen = length($m->NtRecogniz);
		$diff = $tobechlen - $recsitlen;
		@reccedstr = split('', $m->AARecogniz);
	##-find out which frame the cutter wants in
		$matchers = '';
		for ($i = 0; $i <= $diff; $i++)
		{
			$matchers = ((substr $nstring, 0, $i) . $m->NtRecogniz);
			$matchers = $matchers . 'N' while (length($matchers) != $tobechlen);
			$check ='';
			$offset = 0;
			for ($j = 0; $j < (int(length($matchers) / 3)); $j++)
			{
				@checker = getaaa(substr($matchers, $offset, 3));
				for ($g = 0; $g < (@checker-0); $g++)
				{
					$check .= $checker[$g] if ($reccedstr[$j] eq $checker[$g]);
				}
				$offset += 3;
			}
			last if ($check eq $m->AARecogniz);
		}
	##-now that target and current are the same size, process
		$offset = 0;
		$newseq = '';
		for ($i = 0; $i < ($tobechlen / 3); $i++)
		{
			$curcod = substr $m->MustChange, $offset, 3;
			$curtar = substr $matchers, $offset, 3;
			$tarreg = regres($curtar);
			@workaal = getaaa($curcod);
			foreach $g (@workaal)
			{
				@workcod = getcods($g);
#				if ($curcod ne $curtar && $curtar ne 'NNN')
				if ($curcod !~ /$tarreg/)
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
		$m->NewSequenc($newseq);
		#print $m->CutterName, ", ", $m->NtPosition, ", ", $m->NewSequenc, ", ", $m->NtRecogniz, ", ", $m->AARecogniz, break(2);# if ($n eq 'PvuI' || $n eq 'ClaI');
	}
##-Create the Post-Silent Insertion Sequence
	$newnuc = '';
	$curpos = 0;
	foreach $m (@SitArr)
	{
		$newnuc .= substr ( $nucseq, $curpos, (($m->NtPosition)-$curpos-1));
		$newnuc .= $m->NewSequenc;
		$curpos = length ($newnuc);
	}
	$newnuc .= substr ($nucseq, $curpos, (length($nucseq)-$curpos));
	@new = split('', $newnuc);
##-Diagnostic - make sure the sites all made it in.  
	foreach $t (@Error1)
	{
		push @Error0, $t if ((siteseeker($t, $newnuc, 1))-0 > 1);
		push @Error3, $t if ((siteseeker($t, $newnuc, 1))-0 < 1);
	}
##- REMOVE BANNED from sequence (including flankers of course)
	foreach $t (sort keys %banned)
	{	
		push @Error2, $t;
		@$t = siteseeker($t, $newnuc);
		#print "@$t";
		if ((@$t-0) != 0)
		{
			foreach $v (@$t)
			{
				$remaa = ''; $remnt = '';
				$start = $v; 
				while (($start % 3) != 0)
				{ 						
					$start--;
				}
				$stop = $start + sitelength($t) - 1;
				for ($b = ($start/3); $b <= ($stop/3); $b++)
				{
					$remaa .= $aa[$b];
				}
				for ($b = $start; $b <= $stop; $b++)
				{
					$remnt .= $new[$b];
				}
				while (length($remnt) % 3 != 0)
				{
					$b++;
					$remnt .= $new[$b];	##-make sure you have nucs in threes
				}
				print " FLAG " if ($remaa ne translate($remnt));
				$rmseq = changeup($remnt, 2);
				print "$rmseq, $remnt<br>";
				$changeit{$start} = $rmseq;
			}	
		}
	}
##-Create the Post SilentRemoval Sequence
	$lasnuc = '';
	$curpos = 0;
	foreach $v (sort {$changeit{$a} <=> $changeit{$b} }keys %changeit)
	{
		$lasnuc .= substr ( $newnuc, $curpos, ($v-$curpos));
		$lasnuc .= $changeit{$v};
		$curpos = length($lasnuc);
	}
	$lasnuc .= substr ($newnuc, $curpos, (length($newnuc)-$curpos));
##-Diagnostic - make sure the sites all made it out.
	foreach $t (@Error2)
	{
		push @Error4, $t if ((siteseeker($t, $lasnuc, 1)-0) !=0);
	}
##-Diagnostic - make sure the inserted sites are still in.  
	foreach $t (@Error1)
	{
		push @Error5, $t if ((siteseeker($t, $lasnuc, 1)-0) == 0);
	}
##-Fill Out Flanker Information, if Flankers were selected, and Flank That Sequence!
	if ($uni5 ne "")
	{
		$fla5 = new RESite();
		$fla5->CutterName($uni5);
		$fla5->LoadInfo();
		$fla5->NtPosition('5p');
		unshift @SitArr, $fla5;
		$lasnuc = $fla5->NtRecogniz . $lasnuc;
	}
	if ($uni3 ne "")
	{
		$fla3 = new RESite();
		$fla3->CutterName($uni3);
		$fla3->LoadInfo();
		$fla3->NtPosition($nend);
		push @SitArr, $fla3;
		$lasnuc = $lasnuc . $fla3->NtRecogniz;
	}
	@finarr = map  ($_->CutterName, @SitArr);
	$topper = (new RESite())->TableHeader;
	unshift @SitArr, $topper;
	undef @avgpos;
	$avgpos[0] = @posarr[0];
	for($q = 1; $q < (@posarr-0)-1; $q++)
	{
		$avgpos[$q] = $posarr[$q+1]- $posarr[$q];
	}
	push @avgpos, ($nsize-$posarr[$q]);
	undef $avg;
	foreach $q (@avgpos)
	{
		$avg += $q;
	}
	$avg = int(($avg / (@avgpos-0))+.5);
	$avp = int(($avg / 3)+.5);

##-begin output
	print ("<div id=\"notes\">");
	print ("Below is a summary of the sites that have been added to your sequence.<br>");
	if ((@Error3-0) == 0 && (@Error4-0) == 0 && (@Error5-0) == 0 && (@Error0-0) == 0)
	{
		print ("All sites have been inserted or removed as requested.<br>");
	}
	print ("I'm sorry, but enzyme(s) @Error0 are present more than once in the sequence.  This is most likely due to the introduction of a site with a common recognition site, although there is the offchance that a separate introduction introduced a previously absent site.<br>\n") if ((@Error0-0) !=0);
	print ("I'm sorry, but enzyme(s) @Error3 were not inserted. This is probably a programmer error.<br>\n") if ((@Error3-0) >= 1);
	print ("I'm sorry, but enzyme(s) @Error4 were not removed. This is probably a programmer error.<br>\n") if ((@Error4-0) != 0);
	print ("There is a possible overlap or incompatibility - enzyme(s) @Error5 were removed when one or more of @Error2 were removed.<br>\n") if ((@Error5-0) != 0); 
	print ("<br>The average distance between inserted sites is $avg nucleotides ($avp amino acids).");
	print ("</div>");	

	print ("<div id=\"gridgroup0\">\n");
	print ("Your nucleotide sequence:<br>");
	print ("<textarea name=\"passnucseq\" rows=\"5\" cols=\"116\">$lasnuc</textarea>", break(2));

	print ("<div id=\"notes\" style=\"text-align:center\">");
	print ("You can take this sequence to another module now. ");
	print ("</div>");	
	print break(1), "<strong>Take this sequence to</strong>";
	print break(1), $query->submit(-value=>'Oligo Design', -onclick=>'OligoDesign();'), "<-- to get a list of oligos for assembly... the next step of the \"Design a Gene\" path!";
	print break(2), $query->submit(-value=>'Silent Site Insertion', -onclick=>'SSIns();'), "<-- to insert restriction sites";
	print break(1), $query->submit(-value=>'Silent Site Removal', -onclick=>'SSRem();'), "<-- to remove restriction sites";
	print break(1). $query->submit(-value=>'Sequence Analysis', -onclick=>'SeqAna();'), "<-- for information about this sequence";
	print ("<div id=\"notes\" style=\"text-align:center\">");
	print ("Or you can have me reconsider the insertions.  Check the box next to an enzyme name and hit \"Reconsider\" ");
	print ("to have the sequence re-evaluated and that enzyme removed from consideration for automatic insertion.");
	print ("</div>");	
	print break(1), $query->submit(-value=>'Reconsider', -onclick=>'SSIns();');
	
	$j = 0;
	print break(2), space(1);
	foreach $m (@SitArr)
	{
		$m->friendly() if ($j != 0);
		$currname = $m->CutterName;
		$color = "ABC" if ($j % 2 == 0);
		$color = "CDE" if ($j % 2);
		$color = "9AB" if ($j == 0);
		print ("\n<div id = \"gridgroup1\" style = \"background-color: \43$color;\">\n");
		print (" <span id = \"cuNum\"  >", $query->checkbox(-name=>'nextrem', -label=>'', -value=>$currname), "</span>\n") if ($j != 0);
		print (" <span id = \"cuName\" >", $currname, "</span>\n") if $j == 0;		
		print (" <span id = \"cuName\" ><a href=\"http://rebase.neb.com/rebase/enz/$currname.html\" target=\"blank\">$currname $cautio{$m}</a></span>\n") if $j != 0;
		print (" <span id = \"cuRecog\">", $m->CutsAt, $m->StarAct, "</span>\n");
		print (" <span id = \"cuSite\" >", $m->NtPosition+sitelength($uni5), "</span>\n") if ($m->NtPosition ne '5p' && $j!=0);
		print (" <span id = \"cuSite\" >", 1         , "</span>\n")                       if ($m->NtPosition eq '5p' && $j!=0);
		print (" <span id = \"cuSite\" >", $m->NtPosition, "</span>\n")					  if ($m->NtPosition ne '5p' && $j==0);
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
	print ("<br> * This enzyme may exhibit star activity under certain conditions.");
	print ("<br>&laquo; This enzyme has a 1bp overhang and may be very difficult to ligate.");
	print ("&nbsp;<br>&nbsp;</div>\n");
	print ("  <div id=\"gridgroup1\">\n");
	print ("  <input type =\"hidden\" name=\"codons\" value=\"", $query->param('codons'), "\">\n");
	print ("   <input type=\"hidden\" name=\"enzcrit\" value=\"", $query->param('enzcrit'), "\">\n");
	print ("  <input type =\"hidden\" name=\"vector\" value=\"", $query->param('vecname'), "\">\n");
	print ("  <input type =\"hidden\" name=\"absentsites\" value=\"", $query->param('absentsites'), "\">\n");
	print ("  <input type =\"hidden\" name=\"number\" value=\"", $query->param('inte'), "\">\n");
	print ("  <input type =\"hidden\" name=\"results\" value=\"", $query->param('results'), "\">\n");
	print ("  <input type =\"hidden\" name=\"rant\" value=\"", $query->param('rant'), "\">\n");
	print ("  <input type =\"hidden\" name=\"5puni\" value=\"", $query->param('5puni'), "\">\n");
	print ("  <input type =\"hidden\" name=\"3puni\" value=\"", $query->param('3puni'), "\">\n");
	print ("  <input type =\"hidden\" name=\"banned\" value=\"", $query->param('banned'), "\">\n");
	print ("  <input type =\"hidden\" name=\"hits\" value=\"", $query->param('hits'), "\">\n");
	
	print ("<input type=\"hidden\" name=\"org\" value=\"$org\">");
	print ("  <input type =\"hidden\" name=\"actu\" value=\"$avp\">\n");
	print ("  <input type =\"hidden\" name=\"insert\" value=\"@Error1\">\n");
	print ("  <input type =\"hidden\" name=\"remove\" value=\"@Error2\">\n");
	print ("   <input type=\"hidden\" name=\"oldnucseq\" value=\"$nucseq\">\n");
	print ("   <input type=\"hidden\" name=\"nucseq\" value=\"$lasnuc\">\n");
	print ("   <input type=\"hidden\" name=\"aaseq\" value=\"$aaseq\">\n");
	print (" </form>\n</div>\n</body>\n</html>\n");
}
exit;
