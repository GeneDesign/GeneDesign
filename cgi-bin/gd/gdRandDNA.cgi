#!/usr/bin/perl
use strict;
use GeneDesign;
use GeneDesignML;
use CGI;

my $query = new CGI;
print $query->header;

my $CODON_TABLE	 = define_codon_table(1);

my @styles = qw(re);
gdheader("Random DNA Generator", "gdRandDNA.cgi", \@styles);

if ($query->param('ATCONTENT') == 0)
{
print <<EOM;
				<div id="notes">
					<strong>This module is for the generation of random sequences of DNA.</strong>
					You can specify A+T content, length, and the number of sequences you wish to have returned.<br>
					&nbsp;&nbsp;&bull;If you give me ridiculous numbers it will take forever and may crash your browser.<br>
					See the <a href="$docpath/Guide/randna.html">manual</a> for more information.
				</div><br><br><br>
				<div id="gridgroup0">
					A+T content:
					<input type="text" name="ATCONTENT" value="50" size="5" maxlength="3" />%<br>				
					Sequence length:
					<input type="text" name="SEQLENG" value="100" size="5" maxlength="4" />bp<br>
					Number to Generate:
					<input type="text" name="GENNUM" value="5" size="5" maxlength="3" /><br><br><br>	
					<input type="checkbox" name="STOPS" value="1" />Allow stop codons in first frame<br><br><br>	
					<div id="gridgroup1" align ="center" style="position:absolute;top:150;">
						<input type="submit" name=".submit" value=" Next Step: Results " /><br><br><br><br><br>
					</div>
				</div>
EOM
	closer();
}

else
{
	my $atcont = $query->param('ATCONTENT');
	my $tarlen = $query->param('SEQLENG');
	my $gennum = $query->param('GENNUM');
	my $stopal = $query->param('STOPS')	?	$query->param('STOPS')	:	2;
	my $stopallow = $stopal == 1	?	"were"	:	"were not";
	
	my @temparr;
	for my $x (1..$gennum)
	{
		$temparr[$x] = "$x: " . randDNA($tarlen, $atcont, $stopal, $CODON_TABLE) . "<br><br>\n\t\t\t\t\t";
	}

print <<EOM;
				<div id="notes">
					I have generated $gennum sequences of $tarlen bp that are $atcont % A+T.<br>
					Stop codons $stopallow allowed in the first frame.<br>
					&nbsp;&nbsp;&bull;Simply refresh this page for another $gennum random sequences with the same properties.<br>
				</div>
				<div id="wrapper">
					@temparr
				</div>
EOM
	closer();
}