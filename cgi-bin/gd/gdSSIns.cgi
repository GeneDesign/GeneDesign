#!/usr/bin/perl

use strict;
use File::Find;
use List::Util qw(first);
use GeneDesign;
use ResSufTree;
use PML;
use CGI qw(:standard);

my $query = new CGI;
print $query->header;

my $CODON_TABLE	 = define_codon_table(1);
my $RE_DATA = define_sites("<newenz.txt");

my @styles = qw(re mg pd fn);
my @nexts  = qw(SSIns SSRem SeqAna OligoDesign);
my $nextsteps = next_stepper(\@nexts, 5);

gdheader("Silent Restriction Site Insertion", "gdSSIns.cgi", \@styles);

if ($query->param('swit') eq '' && $query->param('nextrem') eq '')
{
	my $nucseq		= $query->param('PASSNUCSEQUENCE')	||	$query->param('nucseq');
	my $aaseq		= $query->param('AASEQUENCE')		||	translate($nucseq, 1, $CODON_TABLE);
	my $org			= $query->param('MODORG')			||	0;
	my $codons		= $query->param('codons')			||	" ";
	my $readonly	= $aaseq	?	'readonly = "true"'	:	'';
	
	opendir(VECTORFOLDER, "vectors");		
	my @vec = map {$_ =~/(p[A-Za-z0-9]+\s*[A-Za-z0-9]*)\.txt/} readdir(VECTORFOLDER);		
	closedir(VECTORFOLDER);
	
	my ($REoptions, $Vectors) = ("", "");
	
	$REoptions .= "<option value=\"$_\">$_</option>\n" . tab(10)	foreach (sort keys %{$$RE_DATA{CLEAN}});
	$Vectors .= "<option value=\"$_\">$_</option>\n" . tab(10)		foreach (sort @vec);
	
print <<EOM;
				<div id="notes">
					<strong>To use this module you need a coding nucleotide sequence. <em>Do Not Panic!</em> This page is simpler than it looks.</strong><br>
					Your nucleotide sequence will be searched for possible silent, unique insertions and you will be prompted to choose as many as you like for insertion.<br>
					It is recommended that you only use ORFs with this module because sites will be inserted without changing the first frame amino acid sequence.
					If your coding sequence is not in the first frame it will be changed.<br>
					<em>Please Note:</em><br>
					&nbsp;&nbsp;&bull;You can only choose <em>one</em> of the &quot;Sites to be Inserted&quot; options.  
					These options define which possible insertions are the most pertinent 
					(i.e., those that are absent from a vector are more interesting than those that are not.)<br>
					&nbsp;&nbsp;&bull;If you want the program to consider all possible insertions as equally important, without defining a vector or 
					picking enzymes, use the default (blank vector sequence).<br>
					&nbsp;&nbsp;&bull;Some vectors are better choices than others! If you pick a vector with very few absent sites, 
					you will have a much more difficult time in automated selection.<br>
					&nbsp;&nbsp;&bull;&quot;Forbidden Sites&quot; are not required, but if specified, these sites will not be considered for insertion.<br>
					&nbsp;&nbsp;&bull;The Enzyme Selection criteria  only apply if you are planning to let the program pick the sites to be inserted. 
					If you will be picking manually you can ignore this section.<br>
					&nbsp;&nbsp;&bull;The looser the enzyme criteria you provide, the better the results.  If you are getting poor return in automated selection,
					try allowing a broader spectrum of enzymes.<br>
					See the <a href="$docpath/Guide/ssi.html" target="blank">manual</a> for more information.
				</div>
				<div id="gridgroup0"  style="align:center;">
					<div id = "gridgroup1">
					<div id ="ntseq">
						Your nucleotide sequence:<br>
						<textarea name="nucseq"  rows="9" cols="54" $readonly>$nucseq</textarea>
					</div>
					<div id = "aaseq">
						Amino Acid Seqeuence:<br>
						<textarea name="aaseq"  rows="9" cols="54" $readonly>$aaseq</textarea>
					</div>
					<div id="gridgroup2" style="top:160; width:100%;">
						<center><strong>Sites to be Inserted</strong>: choose one of the following three options.</center>
						<div id="gridgroup2" style="top:10;">
							<div id="pickers">
								<div id="head1">
									<input type="radio" name="vecpic" value="picked">
									Create a list of enzymes to be considered for insertion
								</div>
								<div id="column1">
									Cutters<br>
									<select name="cutters"  size="8" multiple="multiple">
										$REoptions
									</select>
									<div id="but">
										<input type="button"  name="button" value=" --&gt; " onclick="pick()" />
									</div>
								</div>
								<div id="column2">
									Eligible:<br>
									<select name="absentsites"  size="8" multiple="multiple">
									</select>
									<div id="but">
										<input type="button"  name="button" value=" &lt;-- " onclick="abandon()" />
									</div>
								</div><br><br><br><br><br><br><br><br><br><br><br><br><br><br>
							</div>
							<div id="vectors">
								<div id="head2">
									<input type="radio" name="vecpic" value="chosen">
									Select a vector from the following list and have the absent sites determined
								</div>
								<div id="column3">
									<select name="vector" >
										$Vectors
									</select>
								</div><br><br><br><br><br><br><br><br><br><br><br><br><br><br>
							</div>
							<div id="dunnos">
								<div id="head3">
									<input type="radio" name="vecpic" value="unknown" checked>
									Provide the name and nucleotide sequence of a vector and have the absent sites determined
								</div>
								<div id="column3">
									Name:
									<input type="text" name="vecname"  size="20" maxlength="20" /><br>
									<textarea name="vecseq"  rows="8" cols="30" class="monospace"></textarea>
								</div><br><br><br><br><br><br><br><br><br><br><br><br><br><br>
							</div>
						</div>
					</div>
					<div id="gridgroup2" style="top:400;">	
						<div id="gridgroup2" style="top:10;">
							<div id="pickers">
								<div id="head1">
									<strong>Forbidden Sites</strong>
								</div>
								<div id="column1">
									Cutters<br>
									<select name="cuttersnono"  size="8" multiple="multiple">
										$REoptions
									</select>
									<div id="but">
										<input type="button"  name="button" value=" --&gt; " onclick="pickn()" />
									</div>
								</div>
								<div id="column2">
									Ineligible:<br>
									<select name="absentsnono"  size="8" multiple="multiple">
									</select>
									<div id="but">
										<input type="button"  name="button" value=" &lt;-- " onclick="abandonn()" />
									</div>
								</div><br><br><br><br><br><br><br><br><br><br><br><br><br><br>
								<div id="crits">
									<div id="head4">
										<strong>How do you want me to evaluate sites for automated insertion?</strong>
									</div>
EOM
	enzyme_chooser(9);
	my %hiddenhash = ("swit" => "pd", "MODORG" => $org, "codons" => $codons);
	my $hiddenstring = hidden_fielder(\%hiddenhash);
print <<EOM;
									<br><br>
								</div>
							</div>
						</div>
					</div>
					<div id="gridgroup1" style = "position:absolute; top: 800;left:75;">
						<input type="submit" name=".submit" value=" Next Step: Site Selection " onclick="selectem()" /><br><br><br><br><br><br><br>&nbsp;
						<script language="JavaScript">
							var menu1 = document.form1.cutters;
							var menu2 = document.form1.absentsites;
							var menn1 = document.form1.cuttersnono;
							var menn2 = document.form1.absentsnono;
							var flag1 = document.form1.vecpic[0];
							var flag2 = document.form1.vecpic[1];
							var flag3 = document.form1.vecpic[2];
						</script>
					</div>
				</div>
				$hiddenstring
EOM
	closer();
}


###all runs with pulldown menus
if ($query->param('swit') eq "pd" || $query->param('swit') eq 'ih' || $query->param('nextrem') ne '')
{	
	my $nucseq	= $query->param('redo')		?	$query->param('oldnucseq')	:	cleanup($query->param('nucseq'), 1);
	my $aaseq	= $query->param('aaseq')	||	translate($nucseq, 1, $CODON_TABLE);
	my $codons	= $query->param('codons')	||	" ";

	if ($query->param('nextrem') eq '')
	{
		my @war2 = pattern_finder($nucseq, "*", 2, 1, $CODON_TABLE);
		my $war3 = 1 if (@war2 && ((scalar(@war2) > 1 ) || (($war2[0] + 1) != length($aaseq))));
		if ((substr($nucseq, 0, 3) ne 'ATG' || $war3) && $nucseq)
		{
print <<EOM;
				<div id = "warn">
					<strong>Warning:</strong> Your sequence is not a simple coding sequence.<br>
					Either your sequence does not begin with ATG or your sequence has at least one internal stop codon in the first frame.<br>
					It is still possible to manipulate this sequence but you should check to be sure that crucial features are not compromised.
				</div>
EOM
		}
print <<EOM;
				<div id = "notes">
					<em>What am I looking at?</em><br>
					Your sequence is presented in amino acid form.  Every dot and line connect to a pulldown menu that contains enzymes.  
					Every enzyme represents a possible unique silent site introduction. Where there are no dots or lines, there are no 
					possible unique introductions. Pulldown menus connected in red contain one or more enzymes that are absent from the vector you defined.  
					Within those pulldown menus, the absent enzymes are prefaced with asterisks *. Pulldown menus connected in black contain no enzymes 
					that are absent from the vector. Pulldown menus connected in blue contain an enzyme that has been selected for insertion by the program.
					Within those pulldown menus, the selected enzyme is prefaced with a dot &bull;. There is an asterisk under every tenth amino acid, for placekeeping purposes.<br>
					&nbsp;&nbsp;&bull;You will only see blue dots and lines if you have selected "Pick Sites For Me"!<br><br>  You can select as many enzymes as you like from the 
					pulldown menus.  Or you can have the program select sites for you.  For automated selection, define an amino acid interval and hit &quot;Pick Sites For Me&quot;. 
					The program will select enzymes on that interval using the criteria you defined on the last screen.  You will be given an opportunity to review and edit the 
					selections choices before modifications are made.<br><br> When you are satisfied with your selections, hit &quot;Continue&quot;. Your sequence will be modified 
					and you will be given a summary of changes.<br>
					See the <a href="$docpath/Guide/ssi.html" target="blank">manual</a> for more information.<br>
					&nbsp;&nbsp;&bull;Please wait for the page to load completely before hitting "Continue" or "Pick Sites For Me"!
				</div>
EOM
	}
}


if ($query->param('swit') eq "pd")
{
	my $nucseq  = $query->param('redo')	?	$query->param('oldnucseq')	:	cleanup($query->param('nucseq'), 1);
	my $aaseq	 = $query->param('aaseq')	||	translate($nucseq, 1, $CODON_TABLE);
	my $codons		= $query->param('codons')			||	" ";
	my $SITE_STATUS = define_site_status($nucseq, $$RE_DATA{REGEX});
	my %banned = map { $_ => 1 } grep { exists $$RE_DATA{CLEAN}->{$_} } $query->param('absentsnono');
	my ($vecname, $vecseq) = ("vector not named", "");
	if ($query->param('vecpic') eq "picked")
	{
		my @absents = $query->param('absentsites');
		$vecname = "(no vector selected)";
	}
	elsif ($query->param('vecpic') eq "chosen" || $query->param('vecpic') eq "unknown")
	{
		if ($query->param('vecpic') eq "chosen")
		{
			$vecname = $query->param('vector');
			$vecseq = slurp("vectors/$vecname.txt");
		}
		if ($query->param('vecpic') eq "unknown")
		{
			$vecname = $query->param('vecname');
			$vecseq = $query->param('vecseq');
		}
	}
	my $VECTOR_SITES = define_site_status($vecseq, $$RE_DATA{REGEX});
	my %pa;
	$pa{check_price}			=	$query->param('crPrir');
	$pa{low_price}				=	$query->param('crPrlo');
	$pa{high_price}				=	$query->param('crPrhi');
	$pa{check_stickiness}		=	$query->param('crEndss');
	$pa{stickiness}				=	join " ", $query->param('crEnds');
	$pa{check_cleavage_site}	=	$query->param('crCutss');
	$pa{cleavage_site}			=	join " ", $query->param('crCuts');
	$pa{check_ambiguity}		=	$query->param('crAmbis');
	$pa{ambiguity}				=	join " ", $query->param('crAmbi');
	$pa{check_meth_status}		=	$query->param('crMeths');
	$pa{meth_status}			=	join " ", $query->param('crMeth');
	$pa{check_site_length}		=	$query->param('crLengs');
	$pa{site_length}			=	join " ", $query->param('crLeng');
	$pa{disallowed_seq}			=	$query->param('crDisa');
	$pa{required_seq}			=	$query->param('crAllo');

	my @SitArr = sort {$$RE_DATA{SCORE}->{$a} <=> $$RE_DATA{SCORE}->{$b}} filter_sites(\%pa, $RE_DATA);
	@SitArr = grep { ! exists($banned{$_}) && $$SITE_STATUS{$_} == 0 && $$VECTOR_SITES{$_} == 0 } @SitArr;
	
	my $bigfatarr=[];
	foreach my $tiv (@SitArr)	
	{
		push @{$bigfatarr}, map {"$_ . $tiv"} amb_translation($$RE_DATA{CLEAN}->{$tiv}, $CODON_TABLE);	
	}
	my $hashref = {};
	my $trnrentree = new_aa ResSufTree();	
	$trnrentree->add_aa_paths($_, $hashref) foreach (@{$bigfatarr});
	my @array = $trnrentree->find_aa_paths($aaseq); #looks like ("1: MlyI MSH", "1: PleI MSH"...)
	my @hits = map { $_ . " . " } @array;

print <<EOM;
				<input type="submit" value=" Continue to Summary " onClick="SSISum(0);"> <strong>or</strong> 
				<input type="submit" value="Pick Sites For Me" onClick="SSISum(1);"> on the amino acid interval of
				<input name="number" type="text" size="5" maxlength="4" value="50">
				<div id="gridgroup0"><br>
EOM
	annpsite($aaseq, \@array);
	my %hiddenhash = (swit => "ih", nucseq => $nucseq, aaseq => $aaseq, hits => join("", @hits), absentsites => join(" ", @SitArr),
						vector=> $vecname, vecseq => $vecseq, banned => join(" ", keys %banned), MODORG => $query->param('MODORG'), codons => $codons);
	my $hiddenstring = hidden_fielder(\%hiddenhash);
print <<EOM;
				</div>
				$hiddenstring
EOM
	closer();
}


###Second+ Time Around, the choosing
if ($query->param('swit') eq 'ih' || $query->param('nextrem') ne '')
{
	my $nucseq  = $query->param('redo')	?	$query->param('oldnucseq')	:	$query->param('nucseq');
	my $aaseq	 = $query->param('aaseq')	||	translate($nucseq, 1, $CODON_TABLE);
	my @Nomogo		= $query->param('nextrem') if ($query->param('nextrem'));
	my @nonos		= split(" ", $query->param('banned'));
	push @nonos, @Nomogo if ($query->param('nextrem'));
	my $num		= $query->param('num') || $query->param('number');
	my $aasize = length($aaseq);
	my %used		= map {$_ => -3} @nonos;
	my @absents	= split(" ", $query->param('absentsites'));
#	print "hello, the choosing<br>";
#	print "@Nomogo<br>";
	if (@Nomogo)
	{
		for (my $be = 0; $be < scalar(@absents); $be++)	
		{	
			foreach my $t (@Nomogo)	
			{	
				splice @absents, $be, 1 if ($absents[$be] eq $t);	
			}	
		}
	}
#	print "@Nomogo<br>";
	my %hitsite;
	foreach my $tiv (split(" . ", $query->param('hits')))	
	{	
		if ($tiv =~ $treehit)	
		{
			$hitsite{$1} = [] if (! exists($hitsite{$1}));
			push @{$hitsite{$1}}, [$2, $3];
		}	
	}
	my %countr;
	for my $i (1..int($aasize/$num))				##-determines how many cuts are possible in each chunk
	{
		$countr{$i} += scalar(@{$hitsite{$_}}) foreach (grep { $_ <= $i*$num && $_ > ($i-1)*$num }  keys %hitsite);
	}
	my @selly;
	foreach my $i (sort{$countr{$a} <=> $countr{$b}} keys %countr)
	{
		my $lowbound = (($i*$num)+($num/4));		
		my $highbound = ((($i-1)*$num)+((3*$num)/4));
		my %allhits;
		foreach my $hit (grep { $_ <= $lowbound && $_ > $highbound } keys %hitsite)
		{
			$allhits{$$_[0]} = [$hit, $$_[1]] foreach (@{$hitsite{$hit}});
		}
		my $picked = first	{ ! exists( $used{$_} ) } 
				  sort	{ $$RE_DATA{SCORE}->{$a} <=> $$RE_DATA{SCORE}->{$b} }
				  keys	%allhits;
		$used{$picked} = 1;
#	foreach (sort keys %used)	{print "\t\tUSED $_<br>";}
		$picked = $picked	?	"$allhits{$picked}->[0]: $picked $allhits{$picked}->[1]" :	0;	
#	print "I PICKED $picked<Br>";
		push @selly, $picked if ($picked);
		%used = %{mutexclu(\%used, $$RE_DATA{CLEAN})};
	}
	my $actual = scalar(@selly);
	my $perc = int(($actual/(($aasize/$num)-1))+.5)*100;
	my $perf = int($aasize/$num);
print <<EOM;
				<div id="notes">
					In this $aasize aa sequence I chose $actual cutters approximately $num residues apart.<br>
					This represents an efficiency of $perc% (perfect number is $perf)<br>
					&nbsp;&nbsp;&bull;Remember that the fewer sites found to be absent from your vector, the lower the efficiency is likely to be.<br>
					If there are few enzymes chosen, it may be because the ones chosen first cut at recognition sites of other absent enzymes,
					which causes the latter to be excluded from consideration.<br>
					Make any changes you like and select continue, or have me do it again.<br>
				</div>
EOM
	if (scalar(@Nomogo) != 0)
	{
print <<EOM;
				<div id = "notes">\n
					<strong>Reconsideration</strong><br>
					Enzyme(s) not eligible for automated introduction: @nonos 
				</div>
EOM
	}
print <<EOM;
				<input type="submit" value=" Continue to Summary " onClick="SSISum(0);"> <strong>or</strong> 
				<input type="submit" value="Pick Sites For Me" onClick="SSISum(1);"> on the amino acid interval of
				<input name="number" type="text" size="5" maxlength="4" value="50">
				<div id="gridgroup0">
EOM
	my @hits    = split(" . ", $query->param('hits'));
	annpsite($aaseq, \@hits, \@selly);
	my %hiddenhash = (swit => "wu", nucseq => $nucseq, aaseq=> $aaseq, banned => join(" ", @nonos), 
					MODORG => $query->param('MODORG'), codons => $query->param('codons'),
					hits => $query->param('hits'), 
					absentsites => join(" ", @absents), vector=> $query->param('vector'), 
					vecseq => $query->param('vecseq'), number => $num, "redo" => $query->param('redo') );
	my $hiddenstring = hidden_fielder(\%hiddenhash);
print <<EOM;
				</div>
				$hiddenstring
EOM
	closer();
}	



if ($query->param('swit') eq 'wu')
{
	my $aaseq   = $query->param('aaseq');
	my $nucseq  = $query->param('nucseq');
	my @nonos  = split(" ", $query->param('banned'));
	my $result = qr/[\W ]*([A-Za-z0-9]+) ([A-Z]+)/;
	
	my @Error0;	my @Error2; my @Error1;	my @Error3;
	my $newnuc = $nucseq;	my $errorflag = 0; my $avg = 1;
	
	$$RE_DATA{POST} = {};
	for (my $m = 1; $m < length($aaseq); $m++)
	{
		my ($box, $seq) = ($1, $2) if ($query->param('site' . $m) =~ $result);
		if($box ne '' && $box ne '-')
		{
#	print "GOT $box ($$RE_DATA{CLEAN}->{$box}) at $m with $seq<br>";
			my $critseg = substr($nucseq, ($m*3) - 3, length($seq)*3);
			my $peptide = translate($critseg, 1, $CODON_TABLE);
			my $newpatt = pattern_aligner($critseg, $$RE_DATA{CLEAN}->{$box}, $peptide, $CODON_TABLE);
			my $newcritseg = pattern_adder($critseg, $newpatt, $CODON_TABLE);
#	print "pattern ", $$RE_DATA{CLEAN}->{$box}, ", peptide $peptide, critseg $critseg, newcritseg $newcritseg<br>";
			substr($newnuc, $m*3 - 3, length($newcritseg)) = $newcritseg;
			push @Error1, $box;
			$$RE_DATA{POST}->{$box} = $m*3 - 3;
			$avg += (($m*3-3) - $avg);
		}
	}
	$avg += (length($newnuc) - $avg);
	$avg = int(($avg / (@Error1 + 1)) + .5);
	my $avp = int(($avg / 3) + .5);	
	foreach my $t (@Error1)			##-Diagnostic - make sure the sites all made it in.  
	{
		my $positions_ref = siteseeker($newnuc, $t, $$RE_DATA{REGEX}->{$t});
		if (scalar (keys %{$positions_ref}) > 1)	{	push @Error0, $t;	$errorflag++;}
		if (scalar (keys %{$positions_ref}) < 1)	{	push @Error3, $t;	$errorflag++;}
	}
	foreach my $t (@nonos)
	{
		if (scalar (keys %{siteseeker($newnuc, $t, $$RE_DATA{REGEX}->{$t})}) != 0)	{	push @Error2, $t;	$errorflag++;}
	}
	my $errorstring = "All sites have been inserted or removed as requested.<br>\n" if ($errorflag == 0);
	if (scalar(@Error0) != 0)	{	$errorstring .= tab(5) . "I am sorry, but enzyme(s) @Error0 are present more than once in the sequence.  
				This is most likely due to the introduction of a site with a common recognition site, although there is the offchance that a separate 
					introduction introduced a previously absent site.<br>\n";	}
	if (scalar(@Error2) >= 1)	{	$errorstring .= tab(5) . "@Error2 recognition sites were banned from introduction, but are present in the sequence.<br>\n";	}
	if (scalar(@Error3) >= 1)	{	$errorstring .= tab(5) . "I am sorry, but enzyme(s) @Error3 were not inserted - a 3&rsquo; introduction might have overwritten it.<br>\n";	}
print <<EOM;
				<div id="notes">
					Below is a summary of the sites that have been added to your sequence.<br>
					$errorstring
					The average distance between inserted sites is $avg nucleotides ($avp amino acids).
				</div>
				<div id="gridgroup0">
					Your nucleotide sequence:<br>
					<textarea name="PASSNUCSEQUENCE" rows="5" cols="116">$newnuc</textarea><br><br>
					$nextsteps
					<div id="notes" style="text-align:center">
						Or you can have me reconsider the insertions.  Check the box next to an enzyme name and hit &quot;Reconsider&quot;
						to have the sequence re-evaluated and that enzyme removed from consideration for automatic insertion. 
						<input type="submit" name=".submit" value="Reconsider" onclick="SSIns();" />
					</div><br><br>
EOM
	print_enzyme_table(\@Error1, $RE_DATA, 5);
	my %hiddenhash = (	nucseq => $newnuc,					oldnucseq => $nucseq,				aaseq => $aaseq,					banned => $query->param('banned'),	
						MODORG => $query->param('MODORG'),	codons => $query->param('codons'),	hits => $query->param('hits'),		absentsites => $query->param('absentsites'), 
						"redo" => 1,						swit => "ih",						vector => $query->param('vector'),	vecseq => $query->param('vecseq'), 
						insert => join(" ", @Error1),		"num" => $query->param('number'));
	my $hiddenstring = hidden_fielder(\%hiddenhash);
print <<EOM;
				</div>
				$hiddenstring
EOM
	closer();
}