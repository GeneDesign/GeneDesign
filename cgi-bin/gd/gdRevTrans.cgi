#!/usr/bin/perl
use strict;
use warnings;
use CGI qw(:standard);
use GeneDesign;
use GeneDesignML;
use Text::Wrap qw($columns &wrap);

my $query = new CGI;
print $query->header;

my $CODON_TABLE	 = define_codon_table(1);
my $REV_CODON_TABLE = define_reverse_codon_table($CODON_TABLE);

my @styles		= qw(re mg);
my @nexts		= qw(SSIns SSRem toCodJug SeqAna REBB UserBB OlBB);

gdheader("Reverse Translation", "gdRevTrans.cgi", \@styles);

if (!$query->param('AASEQUENCE'))
{
	my $AASELECT = '';
	foreach my $i (sort keys %$REV_CODON_TABLE)
	{
		$AASELECT .= "$AA_NAMES{$i}\t($i)\n". tab(8) . "<select name=\"$i\">\n";
		$AASELECT .= tab(9) . "<option value=\"$_\">$_</option>\n" foreach (sort @{$$REV_CODON_TABLE{$i}});
		$AASELECT .= tab(8) . "</select><br>";
		$AASELECT .= "\n" . tab(7) . "</div>\n". tab(7) . "<div id=\"col2\" class=\"samewidth\">" if ($i eq "L");
	}
	my $orgchoice = organism_selecter();
print <<EOM;
				<div id="notes">
					<strong>To use this module you need at least one amino acid sequence and an organism name or codon table.</strong><br>
					You can paste in FASTA amino acid sequences.
					All amino acid sequences will be reverse translated to nucleotides using the codon definitions that you specify.<br>
					<em>Please Note:</em><br>
					&nbsp;&nbsp;&bull;The default codon in each pulldown menu is the most optimal codon for expression in the organism you select.<br>
					&nbsp;&nbsp;&bull;If you input a codon table the pulldowns will be ignored.<br>
					&nbsp;&nbsp;&bull;Please use T instead of U in the codon table.<br>
					See the <a href="$docpath/Guide/revtrans.html" target="blank">manual</a> for more information.
				</div>
				<div id="gridgroup0">
					Enter your  amino acid sequence:<br>
					<textarea name="AASEQUENCE" rows="10" cols="118" wrap="virtual"></textarea>
					<div id="gridgroup3">
						<div id="swappers">
							<div id="head">
								$orgchoice
							</div>
							<div id="col1" class="samewidth">
								$AASELECT
							</div>
						</div>
						<div id="pasters">
							<div id="head">
								Or paste a table of codons here <br>(example: A  GCT):
							</div>
							<div id="col3">
								<textarea name="TABLEINPUT" rows="21" cols="15"></textarea>
							</div>
						</div>
					</div>
					<div id="gridgroup1" align ="center" style="position:relative;top:320;">
						<input type="submit" name=".submit" value="Reverse Translate" />
					</div>
				</div>
EOM
	closer();
}

else
{
	my $nextsteps	= next_stepper(\@nexts, 5);
	my $fastaswit	= -1;
	my ($hiddenhash, $seqhsh)	= ({}, {});
	my $table = $query->param('TABLEINPUT');
	my $org = $query->param('MODORG');
	my %codon_scheme;
	
	if (! $table)
	{
		%codon_scheme = map { $_ => $query->param($_) } keys %$REV_CODON_TABLE;
 	}
	else
	{
		$table =~ tr/[a-z]/[A-Z]/;
		$table =~ tr/U/T/;
		$table .="\nB XXX\nJ XXX\nO XXX\nU XXX\nX XXX\nZ XXX";
		foreach (split(/[\n\r]/, $table))	
		{	
			$codon_scheme{$1} = $2	if ($_ =~ /([\w])\W*\s([\w]{3})/);
		}
		$org = 0;
	}
	$$hiddenhash{"MODORG"} = $org;
##Check content of $aaseq
	if ($query->param('AASEQUENCE') =~ /\>/)
	{
		$fastaswit++;
		$seqhsh = fasta_parser($query->param('AASEQUENCE'));
	}
	else
	{
		$seqhsh = {" " => cleanup($query->param('AASEQUENCE'), 2)};
	}
	my ($stats, $nucseq) = ("", "");
	$columns = 81;
	foreach my $id (keys %$seqhsh)
	{
		if ($fastaswit >= 0)
		{
			$nucseq .= $id . " (reverse translated)\n";
			$nucseq .= wrap("","",	reverse_translate(cleanup($$seqhsh{$id}, 2), \%codon_scheme)) . "\n";
			$fastaswit++;
		}
		else
		{
		####-PREERROR CHECKING - did they include everything in the codon table? If not same length, alarm and allow them to go back.
			$$hiddenhash{"AASEQUENCE"} = $$seqhsh{$id};
			$nucseq = reverse_translate($$seqhsh{$id}, \%codon_scheme);
			if (length($$seqhsh{$id}) < length($nucseq)/3 || $$seqhsh{$id} ne translate($nucseq, 1, $CODON_TABLE))
			{
				my $errout = "<br>" . $$seqhsh{$id} . "<br>" . translate($nucseq, 1, $CODON_TABLE) . "<br>Codons:<br>";
				$errout .= " $_, $codon_scheme{$_}<br>" foreach (sort keys %codon_scheme);
				take_exception("I was unable to reverse translate your sequence.  Perhaps you left something out of your codon table?<br>$errout<br><br>");
				closer();
			}
			my $bcou = count($nucseq);
			my $GC = int(((($$bcou{'G'}+$$bcou{'C'})/$$bcou{'length'})*100)+.5);
			$stats  = "&nbsp;_Base Count  : $$bcou{'length'} bp ($$bcou{'A'} A, $$bcou{'T'} T, $$bcou{'C'} C, $$bcou{'G'} G)<br>\n";
			$stats .= tab(5) . "&nbsp;_Composition : $GC% GC<br><br><br><br><br>";
		}
	}
	
	$nextsteps = "" if ($fastaswit > 1);
	my $hiddenstring = hidden_fielder($hiddenhash);
print <<EOM;
				<div id="notes" style="text-align:center;">
					Your amino acid sequences have been successfully reverse translated to nucleotides.<br>
					See the <a href="$docpath/Guide/revtrans.html" target="blank">manual</a> for more information.
				</div>
				<div id="gridgroup0"><br>
					Your reverse translated nucleotide sequences:
					<textarea name="PASSNUCSEQUENCE" rows="20" cols="120" readonly="true">$nucseq</textarea><br>
					$stats
				</div>
				<div id="gridgroup1" align ="center" style="position:relative;top:60">
					$nextsteps
				</div>
				$hiddenstring
EOM
		closer();
}