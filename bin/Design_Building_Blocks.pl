#!/usr/bin/perl
use strict;

use Getopt::Long;
use File::Basename qw(fileparse);
use File::Path qw(make_path);
use Perl6::Slurp;
use Text::Wrap qw($columns &wrap);
use GeneDesign;


$| = 1;

my %ALGORITHM = (0 => "Restriction Enzyme Overlap",
				 1 => "Length Overlap", 
				 2 => "USER Overlap");
my $CODON_TABLE = define_codon_table(1);
$columns = 81;

##Get Arguments
my %config = ();
GetOptions (
			'input=s'		=> \$config{INPUT},
			'rscu=s'		=> \$config{RSCU_FILE},
			'algorithm=i'	=> \$config{ALGORITHM},
			'oligolen=i'	=> \$config{OLIGOLEN},
			'ungapped'		=> \$config{OLIGOGAP},
			'help'			=> \$config{HELP}
		   );


##Respond to cries of help, if applicable
if ($config{HELP})
{
	print "
Design_Building_Blocks.pl

    The Design_Building_Blocks script will break each nucleotide sequence it is 
    given into evenly sized Building Blocks, which are composed of sets of 
    overlapping oligos, or Building Blocks.

    Output will be named by the FASTA identification line, and will be tagged
    with the gdBB suffix, as well as the number of the algorithm used. Default
    values are assumed for every parameter not provided.

  Algorithms:
    0: Restriction Enzyme Overlap: Building Blocks will overlap on unique 
        restriction enzyme recognition sites. An overlap parameter may be 
        defined to determine how much sequence overlaps, including the 
        restriction enzyme recognition site itself. This algorithm makes use of
        existing sites only and does not add or modify sites. If there are not
        enough evenly spaced, unique RE sites the algorithm will fault.
    1: Length Overlap: Building Blocks will overlap by a user-defined overlap
        length parameter.
    2: USER Overlap: Building Blocks will overlap on A(N)xT sequences, so as to 
        be compatible with a uracil exicision (USER) assembly protocol. The 
        width of overlap is user definable, and a melting temperature may be 
        defined for USER oligos.

  Usage examples:
    perl Design_Building_Blocks.pl -i Test_YCLBB.FASTA -a 2 -oligolen 60
    ./Design_Building_Blocks.pl --input Test_YCLBB.FASTA -a 1 -lap 40 --ungapped

  Required arguments:
    -i,  --input : a FASTA file containing protein sequences.
    -a,  --algorithm : at least one algorithm number to determine overlap type.
        (0 = Restriction Enzyme,  1 = Sequence Length,  2 = USER)

  Optional arguments:
    -un, --ungapped: will make ungapped oligos
        (default is gapped)
    -le, --length: the target length in bp of building blocks.
        (default is 740)
    -la, --lap: the target overlap between building blocks.  This parameter is
	
    -o,  --oligolen: the target length in bp of assembly oligos. Best results in 
        steps of 10 bp between 40 and 100 (default = 60)
    -m,  --maxoligolen: the maximum length of assembly oligos permitted
        (default is 80)
    -te, --temp: the melting temperature in degrees C of assembly oligos
        (default is 56)
    -to, --tolerance: the allowable amount of ± variation in melting temperature
        (default is 2.5˚)
    -ut, --utemp: the target temperature in degrees C of user oligos (USER ONLY)
        (default is 56)
    -ul, --ulength: the target length of unique sequence in user oligos. This
        refers to the number of Ns in the sequence A(N)xT.  More than one may be
        provided seperated by commas from the set 5, 7, 9, or 11.
        (default is 5,7,9,11)


";
	exit;
}


##Check the consistency of arguments
die "\n ERROR: No input file was supplied.\n"
	if (! $config{INPUT});
die "\n ERROR: $config{INPUT} does not exist.\n"
	if (! -e $config{INPUT});
warn "\n ERROR: No such algorithm as $_ - ignoring.\n"
	foreach ( grep{! exists $ALGORITHM{$_}} split("", $config{ALGORITHM}));
die "\n ERROR: No algorithm was supplied.\n"
	unless (scalar( grep{exists $ALGORITHM{$_}} split("",$config{ALGORITHM})));


##Fetch input sequences, RSCU table, organisms, algorithms
my $filename	  = fileparse( $config{INPUT}, qr/\.[^.]*/);
make_path($filename . "_gdRT");
my $input		  = slurp( $config{INPUT} );
my $ORIG_SEQUENCE = fasta_parser( $input );

print "\n";
exit;