#!/usr/bin/perl
use strict;
use warnings;
use CGI;
use GeneDesign;
use GeneDesignML;

my $query = new CGI;
print $query->header;

my $CODON_TABLE = define_codon_table(1);
my %aas =  map {$_ => 1} values %$CODON_TABLE;
my @styles = qw(re fn);

gdheader("Generate RSCU Values", "gdRSCUGen.cgi", \@styles);
if (! $query->param('nseq') && ! $query->param('PASSNUCSEQUENCE'))
{
print <<EOM;
				<div id="notes">
					<strong>To use this module you need at least one in-frame coding portion of an ORF.</strong><br>
					This module will calculate the relative synonymous codon usage values for every codon in all ORFs you provide.<br>
					See the <a href="$docpath/Guide/index.html" target="blank">manual</a> for more information.
				</div>
				<div id="gridgroup0">
					Your nucleotide sequence(s):<br>
					<textarea name="nseq" rows="10" cols="120"></textarea><br><br>
					<div id="gridgroup1" align ="center" style="position:absolute; top:300;">
						<input type="submit" name=".submit" value=" Next Step: Results " />
					</div>
				</div>

EOM
	closer();
}

else
{	
	my $nucseq = $query->param('PASSNUCSEQUENCE')	?	$query->param('PASSNUCSEQUENCE')	:	$query->param('nseq');
	take_exception("You didn't provide a nucleotide sequence.<br>") if ( ! $nucseq);
	my $seqhsh = $nucseq =~ /\>/	?	fasta_parser($nucseq)	:	{" " => cleanup($nucseq)};
	
	my @values = values %$seqhsh;
	my $codcount = codon_count(\@values, $CODON_TABLE);
	my $RSCUVal = generate_RSCU_values($codcount, $CODON_TABLE);
	
	my $out = "<code>\n";
	foreach my $aa (sort keys %aas)
	{
		my ($max, $cod) = (0, undef);
		foreach (grep {$$CODON_TABLE{$_} eq $aa} keys %$RSCUVal)
		{
			($max, $cod) = ($$RSCUVal{$_}, $_) if ($$RSCUVal{$_} > $max);
		}
		$out .= tab(6) . "$aa: $cod<br>\n";
	}
	$out .= tab(5) . "</code>";
print <<EOM;
				<div id="notes" style ="position:relative;text-align:center">
					Here are the codons with the highest RSCU values for each codon family.  You can paste this directly into the reverse translate module.<br>
					$out
				</div>
				<div id="notes" style ="position:relative;text-align:center">
					Here is the RSCU table.<br>
EOM
	print print_RSCU_table($RSCUVal, $CODON_TABLE, 5);
	print "				</div>\n";
	closer();
}