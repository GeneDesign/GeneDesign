#!/usr/bin/perl
use strict;
use CGI qw(:standard);
use PML;
use GeneDesign;
use GD::Graph::points;

my $query = new CGI;
print $query->header;

my $CODON_TABLE = define_codon_table(1);

my @styles = qw(re fn);
my @nexts  = qw(SSIns SSRem OligoDesign SeqAna);
gdheader("Codon Bias Graphing", "gdCodBiGraph.cgi", \@styles);
my $organismstring = organism_selecter();
if ($query->param('nseq') eq '' && $query->param('PASSNUCSEQUENCE') eq '')
{
print <<EOM;
				<div id="notes">
					<strong>To use this module you need some coding portion of an ORF.</strong><br>
					See the <a href="$docpath/Guide/index.html" target="blank">manual</a> for more information.
				</div>
				<div id="gridgroup0">
					Your nucleotide sequence:<br>
					<textarea name="nseq" rows="6" cols="100"></textarea><br><br>
					Window size:<br>
					<input type="text" name="WINDOW" value="20" size="4" maxlength="3"/><br><br>
					$organismstring;
					<div id="gridgroup1" align ="center" style="position:absolute; top:300;">
						<input type="submit" name=".submit" value=" Next Step: Results " />
					</div>
				</div>
EOM
	closer();
}

else
{	
	my $nucseq = $query->param('PASSNUCSEQUENCE')	?	$query->param('PASSNUCSEQUENCE')	:	cleanup($query->param('nseq'), 0);					
	take_exception("You didn't provide a nucleotide sequence.<br>") if ( ! $nucseq);
	my $org = $query->param('MODORG');
	take_exception("You didn't select an organism.<br>") if ( ! $org);
	my $window = $query->param('WINDOW');
	take_exception("You didn't provide a window size<br>") if ( ! $window);

	my $RSCU_TABLE = define_RSCU_values($org);
	my $graph = GD::Graph::points->new(1000, 600);
	$graph->set( 
		  x_label           => 'Residue Postion',
		  y_label           => 'Average Codon Usage Value',
		  title             => "Sliding window of size $window using RSCU values from $ORGANISMS{$org}",
		  y_max_value       => 1,
		  y_min_value       => 0,
		  tick_length       => 3,
		  y_tick_number     => 1,
		  y_label_skip      => .1,
		  x_label_skip      => int(length($nucseq)/50),
		  markers           => [1],
		  marker_size		=> 2,
		  dclrs => [ qw(black)],
	  ) or die $graph->error;
	  
	my $CODON_PERCENTAGE_TABLE = define_codon_percentages($CODON_TABLE, $RSCU_TABLE);
	my ($nucseqx, $nucseqy) = index_codon_percentages($nucseq, $window, $CODON_PERCENTAGE_TABLE);
	my %reshash;
	@reshash{@$nucseqx} = @$nucseqy;
	my $format = $graph->export_format;
	open(IMG, ">$docpath/tmp/file.$format") or die $!;
	binmode IMG;
	print IMG $graph->plot([$nucseqx, $nucseqy])->$format();
	close IMG;

print <<EOM;
	<img height=600 width=1000 src="$linkpath/tmp/file.$format">
EOM

	print break(5);
print <<EOM;
					Residue Position and Codon Bias<br>
					<table style="font-family: Courier, monospace; font-size: 14;">
EOM
	foreach my $tiv (sort {$a <=> $b} keys %reshash)
	{
print <<EOM
						<tr>
							<td>$tiv</td>
							<td>$reshash{$tiv}</td>
						</tr>
EOM
	}
print <<EOM;
					</table>
EOM

	closer();
}