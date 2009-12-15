#!/usr/bin/perl
use strict;
use warnings;
use CGI;
use GeneDesign;
use GeneDesignML;
use GD::Graph::lines;
use GD::Graph::colour qw(sorted_colour_list);

my $query = new CGI;
print $query->header;

my $CODON_TABLE = define_codon_table(1);

my @styles = qw(re fn);

gdheader("Codon Bias Graphing", "gdCodBiGraph.cgi", \@styles);
my $organismstring = organism_selecter();
if (! $query->param('nseq') && ! $query->param('PASSNUCSEQUENCE'))
{
print <<EOM;
				<div id="notes">
					<strong>To use this module you need at least one in-frame coding portion of an ORF and an organism name.</strong><br>
					This module will graph the relative synonymous codon usage averaged in a window size of your choice.<br>
					See the <a href="$docpath/Guide/index.html" target="blank">manual</a> for more information.
				</div>
				<div id="gridgroup0">
					Your nucleotide sequence:<br>
					<textarea name="nseq" rows="6" cols="100"></textarea><br><br>
					Window size:<br>
					<input type="text" name="WINDOW" value="20" size="4" maxlength="3"/><br><br>
					$organismstring
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
	my $org = $query->param('MODORG');
	take_exception("You didn't select an organism.<br>") if ( ! $org);
	my $window = $query->param('WINDOW');
	take_exception("You didn't provide a window size<br>") if ( ! $window);
	

	my $RSCU_TABLE = define_RSCU_values($org);
	my $CODON_PERCENTAGE_TABLE	= define_codon_percentages($CODON_TABLE, $RSCU_TABLE);
	my @colors = reverse sorted_colour_list(29);
	my $seqhsh;
	my $fastaswit;
##Check content of $nucseq
	if ($nucseq =~ /\>/)
	{
		$fastaswit++;
		$seqhsh = fasta_parser($nucseq);
	}
	else
	{
		$seqhsh = {"sequence" => cleanup($nucseq, 0)};
	}
	my $graph = GD::Graph::lines->new(800, 600);
	$graph->set( 
		x_label           => 'Codon Postion',
		y_label           => 'Average Relative Synonymous Codon Usage Value',
		title             => "Sliding window of size $window using RSCU values from $ORGANISMS{$org}",
		y_max_value       => 1,
		y_min_value       => 0,
		line_width		  => 10,
		tick_length       => 5,
		y_tick_number     => 1,
		x_label_position  => 0.5,
		y_label_skip      => 0.1,
		x_label_skip      => int(length($nucseq)/50),
		markers           => [1],
		marker_size       => 5,
		dclrs             => \@colors,
	) or die $graph->error;
	my $first = 0;
	my $data = [];
	my @legend = ();
	my ($nucseqx, $nucseqy) = ([], []);
	foreach my $id (keys %$seqhsh)
	{
		($nucseqx, $nucseqy)		= index_codon_percentages($$seqhsh{$id}, $window, $CODON_PERCENTAGE_TABLE);
		push @$data, $nucseqx if ($first == 0);
		push @$data, $nucseqy;
		$first++;
		push @legend, $id;
	}
	$graph->set_legend(@legend);

## Write Image
	my $filename = int(rand(1234));
	my $format = $graph->export_format;
	open(IMG, ">$docpath/tmp/$filename.$format") or die $!;
	binmode IMG;
	print IMG $graph->plot($data)->$format();
	close IMG;

print <<EOM;
				<div id="notes" style ="position:relative;text-align:center">
					The graph below maps the average RSCU over a sliding window for each of the sequences given.<br><br>
					<img height=600 width=800 src="$linkpath/tmp/$filename.$format">
				</div>
EOM
	print break(6);
	if (scalar(keys %$seqhsh) == 1)
	{
		my (%reshash, %codhash);
		my ($mindex, $maxdex, $min, $max) = (undef, undef, 1, 0);
		@reshash{@$nucseqx} = @$nucseqy;
		$codhash{$_} = substr($nucseq, ($_*3 - 3), 3) foreach(@$nucseqx);
		foreach (@$nucseqx)
		{
			if ($min >= $reshash{$_})
			{
				$mindex = $_;
				$min = $reshash{$_};
			}
			if ($max <= $reshash{$_})
			{
				$maxdex = $_;
				$max = $reshash{$_};
			}
		}
		print "Maximum RSCU value: <code>", substr($nucseq, ($maxdex*3 -3), 3), " (", translate(substr($nucseq, ($maxdex*3 -3), 3), 1, $CODON_TABLE), ")</code> at $maxdex with $reshash{$maxdex}<br>";
		print "Minimum RSCU value: <code>", substr($nucseq, ($mindex*3 -3), 3), " (", translate(substr($nucseq, ($mindex*3 -3), 3), 1, $CODON_TABLE), ")</code> at $mindex with $reshash{$mindex}<br>";

print <<EOM;
					<table style="font-family: Courier, monospace;font-size: 14;" cellspacing="2" border = "1">
						<tr>
							<th>Residue<br>Position</th>
							<th>Residue<br>(Codon)</th>
							<th>Average RSCU Value for <Br>$window residue window centered here</th>
						</tr>
EOM
		foreach my $tiv (sort {$a <=> $b} keys %reshash)
		{
print <<EOM
						<tr>
							<td align="center">$tiv</td>
							<td align="center">$codhash{$tiv}</td>
							<td>$reshash{$tiv}</td>
						</tr>
EOM
		}
print <<EOM;
					</table>
EOM
	}
	closer();
}