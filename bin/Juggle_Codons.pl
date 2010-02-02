#!/usr/bin/perl
use strict;
use warnings;

use Getopt::Long;
use File::Basename qw(fileparse);
use File::Path qw(make_path);
use Perl6::Slurp;
use GeneDesign;
use GD::Graph::lines;


$| = 1;

my %ALGORITHMS = ("r" => 0, "o" => 1, "p" => 2, "m" => 3, "l" => 4);
my %ALGNAME	 = (r => "random", o => "optimization", p => "less optimization", 
				m => "most different sequence", l => "least different RSCU");
my %ALGSHORT = (r => "6 rand", o => "2 opti", p => "3 lopt", 
				m => "4 msdf", l => "5 lsdf");
my @COLORS = qw(black green gray red orange yellow);
my %ORGNAME = %ORGANISMS;
my $CODON_TABLE = define_codon_table(1);

##Get Arguments
my %config = ();
GetOptions (
			'input=s'		=> \$config{INPUT},
			'rscu=s'		=> \$config{RSCU_FILE},
			'organism=i'	=> \$config{ORGANISM},
			'algorithm=s'	=> \$config{ALGORITHMS},
			'align!'		=> \$config{ALIGNS},
#			'stats!'		=> \$config{STATISTICS},
			'graph!'		=> \$config{GRAPHS},
			'help'			=> \$config{HELP}
		   );


##Respond to cries of help, if applicable
if ($config{HELP})
{
	print "
Codon_Juggling.pl
	
    Given at least one protein-coding gene as input, the Codon_Juggling script
    can use several algorithms to modify the sequence without altering its
    translation. It is thus possible to generate a sequence that is optimized
    for expression, as different as possible from the original sequence, or some
    combination of the two.

	If no algorithm is specified, the optimization algorithm will be used.
	
    Output will be named according to the name of the FASTA input file, and will
    be tagged with the gdCJ suffix and the number of the organism used (or 0 if
    a custom RSCU table was provided).

  Algorithms:
    o: The optimized algorithm replaces every codon in the input sequence with
        the most translationally optimal codon as specified by the input RSCU
        tables or known RSCU tables (if organism is specified). If the codon is
        already the ideal codon it is left alone.
    p: The less optimized algorithm uses the same data to replace the original
        codon with the most optimal codon that is not the original codon; that
        is, if the current codon is not the most optimal it becomes the most
        optimal, and if it is the most optimal it becomes the next most optimal.
    m: The most different sequence algorithm attempts to change as many bases as
        possible within the codon, preferably transversions.
    l: The least different RSCU algorithm attempts to replace as many codons as
        possible while minimizing disruption of the original average RSCU value
        for the sequence.
    r: The random algorithm makes random replacements.
	
  Usage examples:
    perl Codon_Juggling.pl -i=Test_YAR000W.FASTA -o=13 --algorithm=om
    ./Codon_Juggling.pl --input=Test_YAR000W.FASTA -r=Test_TY1_RSCU.txt --align

  Required arguments:
    -i,   --input : a FASTA file containing nucleotide sequences.
    -r,   --rscu : a txt file with an RSCU table from Generate_RSCU_Table.pl
    -o,   --organism : at least one organism number.
        Each organism given represents another iteration the algorithm must run.
        (1 = S.cerevisiae,  2 = E.coli,         3 = H.sapiens,
         4 = C.elegans,     5 = D.melanogaster, 6 = B.subtilis)
    -r OR -o must be provided. If both are given the table will be treated as
        another organism, named after the table's filename.

  Optional arguments:
    -alg, --algorithm : which algorithms to use.
        (o = optimization,            p = less optimization,
         m = most different sequence, l = least different RSCU, r = random)
    -ali, --align: output alignments of the juggled sequences
    -g,   --graph: output a graph of the RSCU curves for juggled sequences
    -h,   --help : display this message

";
#   -s,   --stats: output statistics (identy, AT%, et al.) for juggled sequences
	exit;
}

##Check the consistency of arguments
die "\n ERROR: Neither an organism nor an RSCU table were supplied.\n"
	if (! $config{ORGANISM} && ! $config{RSCU_FILE});
die "\n ERROR: $config{INPUT} does not exist.\n"
	if (! -e $config{INPUT});
die "\n ERROR: $config{RSCU_FILE} does not exist.\n"
	if ($config{RSCU_FILE} && ! -e $config{RSCU_FILE});
warn "\n WARNING: $_ is not a recognized organism and will be ignored.\n"
	foreach (grep {! exists($ORGANISMS{$_})} split ("", $config{ORGANISM}) );
if ($config{ALGORITHMS})
{	warn "\n WARNING: $_ is not a recognized algorithm and will be ignored.\n"
		foreach (grep { ! exists( $ALGORITHMS{$_} ) } 
				 split ("", $config{ALGORITHMS}) );}

##Fetch input sequences, RSCU table, organisms, algorithms
my $filename	  = fileparse( $config{INPUT}, qr/\.[^.]*/);
make_path($filename . "_gdCJ");
my $input		  = slurp( $config{INPUT} );
my $ORIG_SEQUENCE = fasta_parser( $input );
warn "\n WARNING: $_ is not the right length for an ORF and will be ignored.\n"
	foreach (grep {length($$ORIG_SEQUENCE{$_}) % 3} keys %$ORIG_SEQUENCE );
my @goodkeys = grep {length($$ORIG_SEQUENCE{$_}) % 3 == 0} keys %$ORIG_SEQUENCE;

my $rscu		= $config{RSCU_FILE}	?	slurp( $config{RSCU_FILE} )	:	0;
my $RSCU_DEFN	= $rscu					?	rscu_parser( $rscu )		:	{};
my @ORGSDO		= grep { exists $ORGANISMS{$_} }
					split( "", $config{ORGANISM} );
push @ORGSDO, 0	if ($rscu);
$ORGNAME{0}		= fileparse( $config{RSCU_FILE}, qr/\.[^.]*/) if ($rscu);
my %ALGSDO		= $config{ALGORITHMS}
					?	map { $_ => 1 }
						grep { exists $ALGNAME{$_} }
						split( "", $config{ALGORITHMS} )
					:	("o" => 1); 
print "\n";

##Juggle!
foreach my $org (@ORGSDO)
{
	my $OUTPUT = {};
	my $ALIGNS = {};
	my $GRAPHS = {};
	my $RSCU_VALUES = $org	?	define_RSCU_values( $org )	:	$RSCU_DEFN;
	foreach my $seqkey (@goodkeys)
	{
		foreach my $alg (sort keys %ALGSDO)
		{
			my $new_seq = change_codons( $$ORIG_SEQUENCE{$seqkey}, $CODON_TABLE, $RSCU_VALUES, $ALGORITHMS{$alg} );
			my $new_key = $seqkey . " after the $ALGNAME{$alg} codon juggling algorithm, using $ORGNAME{$org} RSCU values";
			$$OUTPUT{$new_key} = $new_seq;
			$$ALIGNS{"$seqkey $ALGSHORT{$alg}"} = $new_key if ($config{ALIGNS});
			$$GRAPHS{"$seqkey $ALGSHORT{$alg}"} = $new_key if ($config{GRAPHS});
		}
	}
	open (my $fh, ">" . $filename . "_gdCJ/" . $filename. "_gdCJ_$org.FASTA") || die "can't create output file, $!";
	print $fh fasta_writer($OUTPUT);
	close $fh;
	print $filename . "_gdCJ_$org.FASTA has been written.\n";
	
	if ($config{ALIGNS})
	{
		my $alnpath = $filename . '_gdCJ/Alignments';
		make_path($alnpath);
		foreach my $seqkey (@goodkeys)
		{
			my $ALIGNOUT = {"1 orig" => $$ORIG_SEQUENCE{$seqkey}};
			my $aaseq = translate($$ORIG_SEQUENCE{$seqkey}, 1, $CODON_TABLE);
			foreach my $newkey ( grep {$_ =~ /$seqkey /} sort keys %$ALIGNS)
			{
				my $short =  $1 if ($newkey =~ /$seqkey (\d \w+)/);
				$$ALIGNOUT{$short} = $$OUTPUT{$$ALIGNS{$newkey}};
			}
			my $alnname = $seqkey;
			$alnname =~ s/>//;
			open (my $fh, ">$alnpath/$alnname" . "_gdCJ_$org.txt") || die "can't create alignment file, $!";
			print $fh print_alignment($ALIGNOUT, 120, 0, $aaseq);
			close $fh;
			print "\t$alnpath/$alnname"."_gdCJ_$org.txt has been written.\n";
		}
	}
	
	if ($config{GRAPHS})
	{
		my $graphpath = $filename . '_gdCJ/Graphs';
		make_path($graphpath);
		foreach my $seqkey (@goodkeys)
		{
			my $window = length($$ORIG_SEQUENCE{$seqkey}) > 1000	
				?	20 * (int(length($$ORIG_SEQUENCE{$seqkey})/1000))	
				:	length($$ORIG_SEQUENCE{$seqkey}) > 500	
					?	20	
					:	10; #$query->param('WINDOW');
			my $CODON_PERCENTAGE_TABLE = define_codon_percentages($CODON_TABLE, $RSCU_VALUES);
			my @data = index_codon_percentages($$ORIG_SEQUENCE{$seqkey}, $window, $CODON_PERCENTAGE_TABLE);
			my @legend = ("1 orig");
			foreach my $newkey (sort grep {$_ =~ /$seqkey /} keys %$GRAPHS)
			{
				my ($tempx, $tempy) = index_codon_percentages($$OUTPUT{$$GRAPHS{$newkey}}, $window, $CODON_PERCENTAGE_TABLE);
				push @data, $tempy;
				push @legend, $1 if ($newkey =~ /$seqkey (\d \w+)/);
			}
			my $graph = GD::Graph::lines->new(800, 600);
			$graph->set( 
				x_label           => 'Window Position (Codon Offset)',
				y_label           => 'Average Relative Synonymous Codon Usage Value',
				title             => "Sliding window of $window using RSCU values from $ORGNAME{$org}",
				y_max_value       => 1,
				y_min_value       => 0,
				tick_length       => 3,
				y_tick_number     => 1,
				x_label_position  => 0.5,
				y_label_skip      => 0.1,
				x_label_skip      => int(length($$ORIG_SEQUENCE{$seqkey})/50),
				markers           => [1], 
				line_width		  => 2,
				marker_size		  => 2,
				dclrs			  => \@COLORS,
			) or die $graph->error;
			$graph->set_legend(@legend);
			my $gifname = $seqkey;
			$gifname =~ s/>//;			
			my $format = $graph->export_format;
			open   (IMG, ">$graphpath/$gifname" . "_$org.$format") or die "can't create graph file, $!";
			binmode IMG;
			print   IMG $graph->plot(\@data)->$format();
			close   IMG;
			print "\t$graphpath/$gifname"."_$org.$format has been written.\n";
		}
	}
}

print "\n";
exit;