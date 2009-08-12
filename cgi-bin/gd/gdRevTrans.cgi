#!/usr/bin/perl
use strict;
use CGI qw(:standard);
use PML;
use GeneDesign;

my $query = new CGI;
print $query->header;

my $CODON_TABLE	 = define_codon_table(1);
my $REV_CODON_TABLE = define_reverse_codon_table($CODON_TABLE);

my @styles = qw(re mg);
my @nexts  = qw(SSIns SSRem toCodJug SeqAna OligoDesign);
my $nextsteps = next_stepper(\@nexts, 5);

gdheader("Reverse Translation", "gdRevTrans.cgi", \@styles);

my $AASELECT = '';
foreach my $i (sort keys %$REV_CODON_TABLE)
{
	$AASELECT .= "$AA_NAMES{$i}\t($i)\n\t\t\t\t\t\t\t\t<select name=\"$i\">\n";
	$AASELECT .= "\t\t\t\t\t\t\t\t\t<option value=\"$_\">$_</option>\n" foreach (@{$$REV_CODON_TABLE{$i}});
	$AASELECT .= "\t\t\t\t\t\t\t\t</select><br>";
	$AASELECT .= "\t\t\t\t\t\t\t</div>\n\t\t\t\t\t\t<div id=\"col2\" class=\"samewidth\">" if ($i eq "L");
}
my $orgchoice = organism_selecter();

if ($query->param('AASEQUENCE') eq '')
{
print <<EOM;
				<div id="notes">
					<strong>To use this module you need an amino acid sequence and an organism name or codon table.</strong><br>
					Your amino acid sequence will be reverse translated to nucleotides using the codon definitions that you specify.<br>
					<em>Please Note:</em><br>
					&nbsp;&nbsp;&bull;The default codon in each pulldown menu is the most optimal codon for expression in the organism you select.<br>
					&nbsp;&nbsp;&bull;If you input a codon table the pulldowns will be ignored.<br>
					&nbsp;&nbsp;&bull;Please use T instead of U in the codon table.<br>
					See the <a href="$docpath/Guide/revtrans.html" target="blank">manual</a> for more information.
				</div>
				<div id="gridgroup0">
					Enter your  amino acid sequence:<br>
					<textarea name="AASEQUENCE" rows="6" cols="80" wrap="virtual"></textarea>
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
					<div id="gridgroup1" align ="center" style="position:absolute; top:420;">
						<input type="submit" name=".submit" value="Reverse Translate" />
					</div>
				</div>
EOM
	closer();
}

else
{
	my $seq2  = cleanup($query->param('AASEQUENCE'), 2);
	my $table = $query->param('TABLEINPUT');
	my %codon_scheme;
	my $org = $query->param('MODORG');
	if ($table eq "")
	{
		%codon_scheme = map { $_ => $query->param($_) } keys %$REV_CODON_TABLE;
 	}
	else
	{
		$table =~ tr/[a-z]/[A-Z]/;	
		$table =~ tr/U/T/;	
		$table .="\nB XXX\nJ XXX\nO XXX\nU XXX\nX XXX\nZ XXX";
		foreach (split('\n', $table))	
		{	
			$codon_scheme{$1} = $2	if ($_ =~ /([\w])\s([\w]{3})/);
		}
		$org = 0;
	}
	my $nucseq = reverse_translate($seq2, \%codon_scheme);
	my $bcou = count($nucseq);
	my $GC = int(((($$bcou{'G'}+$$bcou{'C'})/$$bcou{'length'})*100)+.5);
	
####-PREERROR CHECKING - did they include everything in the codon table? If not same length, alarm and allow them to go back.
	if (length($seq2) < length($nucseq)/3 || $seq2 ne translate($nucseq, 1, $CODON_TABLE))
	{
		my $errout = "<br>" . $seq2 . "<br>" . translate($nucseq, 1, $CODON_TABLE) . "<br>Codons:<br>";
		foreach (sort keys %codon_scheme)	{ $errout .= " $_, $codon_scheme{$_}<br>";	}
		take_exception("I was unable to reverse translate your sequence.  Perhaps you left something out of your codon table?<br>$errout<br><br>");
		closer();
	}
	else
	{
		my %hiddenhash = ("AASEQUENCE" => $seq2, "MODORG" => $org);
		my $hiddenstring = hidden_fielder(\%hiddenhash);
print <<EOM;	
				<div id="notes" style="text-align:center;">
					Your amino acid sequence has been successfully reverse translated to nucleotides.<br>
					See the <a href="$docpath/Guide/revtrans.html" target="blank">manual</a> for more information.
				</div>
				<div id="gridgroup0"><br>
					Your reverse translated nucleotide sequence:
					<textarea name="PASSNUCSEQUENCE" rows="6" cols="100" readonly="true">$nucseq</textarea><br>
					&nbsp;_Base Count  : $$bcou{'length'} bp ($$bcou{'A'} A, $$bcou{'T'} T, $$bcou{'C'} C, $$bcou{'G'} G)<br>
					&nbsp;_Composition : $GC% GC<br><br><br><br><br>
				</div>
				<div id="gridgroup1" align ="center" style="position:relative;">
					$nextsteps
				</div>
				$hiddenstring
EOM
		closer();
	}
}