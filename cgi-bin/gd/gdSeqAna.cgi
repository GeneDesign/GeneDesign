#!/usr/bin/perl
use strict;
use CGI;
use List::Util qw(first);
use GeneDesign;
use GeneDesignML;

my $CODON_TABLE = define_codon_table(1);
my $RE_DATA = define_sites($enzfile);

my $query = new CGI;
print $query->header;

my @styles = qw(re tm);
my @nexts  = qw(SSIns SSRem toCodJug REBB UserBB OlBB);
gdheader("Sequence Analysis", "gdSeqAna.cgi", \@styles);
my $nextsteps = next_stepper(\@nexts, 5);

if ($query->param('nucseq') eq '' && $query->param('PASSNUCSEQUENCE') eq '')
{
print <<EOM;
				<div id="notes">
					<strong>To use this module you need at least one nucleotide sequence.</strong><br>
					This module is for the analysis of nucleotide sequences. Your nucleotide sequence(s) will be analyzed for base content, 
					Tm, the presence of restriction sites, and open reading frames.<br>
					<em>Please Note:</em><br>
					&nbsp;&nbsp;&bull;If you wish to compare a list of sequences, make sure they are all on separate lines and check 'oligo list'.<br>
					See the <a href="$linkpath/Guide/seqana.html" target="blank">manual</a> for more information.
				</div>
				<div id="gridgroup0">
					Enter your nucleotide sequence(s):<br>
					<textarea name="nucseq" rows="6" cols="100"></textarea><br>
					<input type="radio" name="kind" value="oligo list">List of Oligos
					<input type="radio" name="kind" value="single sequence" checked="true">Single Sequence
					<div id="gridgroup1" align ="center" style="position:absolute;top:150;">
						<input type="submit" name=".submit" value=" Analyze " />
					</div>
				</div>
EOM
	closer();
}

else
{
	my $kind = $query->param('kind');
	if ($kind ne 'oligo list')
	{
		my $nucseq = $query->param('PASSNUCSEQUENCE') ?	cleanup($query->param('PASSNUCSEQUENCE'), 0)	:	cleanup($query->param('nucseq'), 0);
		my $bcou = count($nucseq);
		my @melt_data  = (melt($nucseq, 1), melt($nucseq, 2), melt($nucseq, 3), melt($nucseq, 4));
		my @therm_data = ntherm($nucseq);
		my (@results, @abss, @lines, @names, @orfs, @stops) = ((), (), (), (), (), (), ());
		my $spacer = break(40);
		my $scale = 500;
		if (length($nucseq) < 50)
		{
			push @results, "_&Delta;H: $therm_data[0]<br>_&Delta;S: $therm_data[1]<br>_&Delta;G: $therm_data[2]<br><br>";
		}
		if (length($nucseq) < 100)
		{
			push @results, "_Simple: $melt_data[0]<br>" if (length($nucseq) <=22);
			push @results, "_Bolton: $melt_data[1]<br>" if (length($nucseq) >=7);
			push @results, "_Primer: $melt_data[2]<br>" if (length($nucseq) >=10);
			push @results, "_NNTher: $melt_data[3]<br>" if (length($nucseq) >=10);
		}
		if (length($nucseq) > 10)
		{
		#figure out uniques and absents
			my $SITES_STATUS = define_site_status($nucseq, $$RE_DATA{REGEX});
			my %borders;
			foreach my $enz (grep {$$SITES_STATUS{$_} == 1}	keys %$SITES_STATUS)
			{	
				my $temphash = siteseeker($nucseq, $enz, $$RE_DATA{REGEX}->{$enz});
				my $pos = first {1} keys %$temphash;
				$borders{$pos} = $enz;
			}
			@abss = sort (grep {$$SITES_STATUS{$_}  == 0} keys %$SITES_STATUS);

			my $preline = "\t\t\t\t\t\t\t<div id=\"uniline\" style=\"top:";
			@lines = map { $preline . int(($_/$$bcou{'length'})*$scale) . ";\"></div>\n" } keys %borders;
			for my $e (0..39)
			{
				push @names, "\t\t\t\t\t\t\t<div id = \"namebox\" style=\"top:", $e*12.5, ";\">";
				foreach my $r (sort {$a <=> $b} keys %borders)
				{
					my $pos = int(($r/$$bcou{'length'})*$scale);
					push @names, "$borders{$r} ($r)" if (($pos <= ($e+1)*12.5) && $pos > $e*12.5);
				}
				push @names, "</div>\n";
			}
		#figure out ORFs and stops
			foreach my $orf (grep{$_->[0] > 0} @{orf_finder($nucseq, $CODON_TABLE)})
			{
				my $frame = 10 * ($orf->[0] - 1);
				my $top = (3 * $orf->[1]) - 1;
				my $hei = 3 * ($orf->[2] + 1);
				my $post = int( ($top / $$bcou{"length"}) * $scale );
				my $posh = int( ($hei / $$bcou{"length"}) * $scale );
				push @orfs, "\t\t\t\t\t\t\t<div id=\"orfbox\" style=\"top:$post;left:$frame;height:$posh;\"></div>\n";
			}
			for my $frame (0..2)
			{
				foreach my $stop (pattern_finder($nucseq, "*", 2, $frame+1, $CODON_TABLE))
				{
					my $pos = int((((($stop+1)*3)-2)/$$bcou{"length"})*$scale);
					push @stops, "\t\t\t\t\t\t\t<div id=\"stopbox\" style=\"top:$pos;left:", 10*$frame, ";\"></div>\n";
				}
			}
		}
print <<EOM;
				<div id="notes">
					For a description of the formulas used, see the manual.<br>
					<em>Please Note:</em><br>
					&nbsp;&nbsp;&bull;You do not have to go back to put in a new sequence.  Simply type or paste the new sequence into the box and hit 'Analyze Again'.<br>
				</div>
				<br>Your sequence:<br>
				<textarea name="PASSNUCSEQUENCE" rows="6" cols="100" -wrap="hard">$nucseq</textarea><br><br>
				&nbsp;_Base Count  : $$bcou{'length'} bp ($$bcou{'A'} A, $$bcou{'T'} T, $$bcou{'C'} C, $$bcou{'G'} G)<br>
				&nbsp;_Composition : $$bcou{GCp}% GC, $$bcou{ATp}% AT<br><br>
				@results
				<input type="submit" name=".submit" value=" Analyze Again" />
				<div id="reswrap">
					<div id="abssite">
						<strong>Absent Sites</strong><br>
						@abss
					</div>
					<div id="seqwrap">
						<strong>Unique Sites</strong>
						<div id="genecol">
							@lines
							@names
						</div>
					</div>
					<div id ="orfwrap">
						<strong>ORFs</strong><br>
						<div id="orfcol">
							@orfs
							@stops
						</div>
					</div>
				</div>
				$spacer
				<div id="gridgroup1" align ="center" style="position:relative;">
					$nextsteps
				</div>
			</form>
EOM
	closer();
	}
	
	
	else
	{
		my $r = 0;
		my $max = 0;
		my @report;
		my @nucarr = split('\n', $query->param('nucseq'));
		foreach (@nucarr)
		{
			$max = length($_) if (length($_) > $max);
		}
		foreach my $oligo (@nucarr)
		{
			my $num = $r+1;
			$num = '0' . $num while( length($num) < length(scalar(@nucarr)) );
			my $oligo = cleanup($oligo, 1);
			my $bcou = count($oligo);
			my @melt_data  = (melt($oligo, 1), melt($oligo, 2), melt($oligo, 3), melt($oligo, 4));
			my @therm_data = ntherm($oligo);
			my $answer = $num . space(2) . "\t"  . $oligo . space($max - length($oligo) + 2) . "\t"   . $$bcou{length} . space(2). "\t" ;
			$answer .= $$bcou{GCp} . space(2). "\t"  . $$bcou{ATp} . space(2). "\t"  . int($melt_data[1]+.5);
			$answer .= space(2) . "\t"  . int($melt_data[2]+.5) . space(2).  "\t" . int($melt_data[3]+.5) . "<br>";
			$r++;
			push @report, $answer;
		}
		my $header = "\#" . space(length(scalar(@nucarr))+1) . "\t" . "oligo" . space($max - 3). "\t" . "bp" . space(2) . "\t" ;
		$header .= "GC" . space(2) . "\t"  . "AT" . space(2) . "\t"  . "_b" . space(2) . "\t" .  "_p" . space(2) .  "\t" . "_n" . "<br>";
		unshift @report, $header;
print <<EOM;
				<div id="notes">
					For a description of the formulas used, see the manual.<br>
				</div>
				<br>
				<code>
					@report
				</code>
			</form>
EOM
		closer();
	}
}
