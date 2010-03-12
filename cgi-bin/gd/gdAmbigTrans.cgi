#!/usr/bin/perl
use strict;
use warnings;
use CGI;
use GeneDesign;
use GeneDesignML;

my $query = new CGI;
print $query->header;

my $CODON_TABLE = define_codon_table(1);

my @styles = qw(re);

gdheader("Ambiguous Translation", "gdAmbigTrans.cgi", \@styles);

if (! $query->param('nseq'))
{
print <<EOM;
				<div id="notes">
					<strong>To use this module you need a nucleotide sequence.</strong><br>
					This module is for the translation of DNA sequences that may include ambiguous bases.<br>
					See the <a href="$linkpath/Guide/AmbTrans.html" target="blank">manual</a> for more information.
				</div>
				<div id="gridgroup0">
					Your nucleotide sequence:<br>
					<textarea name="nseq" rows="6" cols="100"></textarea><br>
					<div id="gridgroup1" align ="center" style="position:absolute; top:150;">
						<input type="submit" name=".submit" value=" Generate Amino Acid Sequences " />
					</div>
				</div>
EOM
	closer();
}

else
{
	my $nucseq		= cleanup($query->param('nseq'), 2);
	my @sortarr		= sort(amb_translation($nucseq, $CODON_TABLE, 1));
	my @sortarr2	= sort(amb_translation($nucseq, $CODON_TABLE));
	my $number		= scalar(@sortarr);
	my $number2		= scalar(@sortarr2);
print <<EOM;
				<div id="notes">
					There are $number possible peptides if we force the first base of your oligo to be the sense frame.<br>
				</div><br><br>
				Oligo: <code>$nucseq</code><br><br>
				Summary: <br><textarea name="list" rows="10" cols="120" readonly>@sortarr</textarea><br><br>
				<div id="notes">
					There are $number2 possible peptides from the three sense frames in your oligo.<br>
				</div><br><br>
				Oligo: <code>(NN)$nucseq(NN)</code><br><br>
				Summary: <br><textarea name="list" rows="10" cols="120" readonly>@sortarr2</textarea><br><br>
			</form>
EOM
	closer();
}