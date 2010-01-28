#!/usr/bin/perl
use strict;
use warnings;

use Getopt::Long;
use File::Basename qw(fileparse);
use File::Path qw(make_path);
use Perl6::Slurp;
use GeneDesign;


$| = 1;

my %ORGNAME = %ORGANISMS;
my $CODON_TABLE = define_codon_table(1);
$columns = 81;

##Get Arguments
my %config = ();
GetOptions (
			'input=s'		=> \$config{INPUT},
			'rscu=s'		=> \$config{RSCU_FILE},
			'organism=i'	=> \$config{ORGANISM},
			'help'			=> \$config{HELP}
		   );


##Respond to cries of help, if applicable
if ($config{HELP})
{
	print "
Reverse_Translation.pl
	
    Given at least one protein sequence as input, the Reverse_Translation script
    ynonymous nucleotide sequence using either a user-defined codon scheme or 
    the most optimal codons for expression in a user-selected organism.
	
    Output will be named according to the name of the FASTA input file, and will
    be tagged with the gdRT suffix and the number of the organism used (or 0 if
    a custom RSCU table was provided).
	
  Usage examples:
    perl Reverse_Translate.pl -i Test_YAR000W_p.FASTA -o 13
    ./Reverse_Translate.pl --input Test_YAR000W_p.FASTA --rscu Test_TY1_RSCU.txt

  Required arguments:
    -i,   --input : a FASTA file containing protein sequences.
    -r,   --rscu : a txt file containing an RSCU table from gen_RSCU.pl
    -o,   --organism : at least one organism number.
        Each organism given represents another iteration the algorithm must run.
        (1 = S.cerevisiae,  2 = E.coli,         3 = H.sapiens,
         4 = C.elegans,     5 = D.melanogaster, 6 = B.subtilis)
    -r OR -o must be provided. If both are given the table will be treated as
        another organism, named after the table's filename.

  Optional arguments:
    -h,   --help : Display this message


";
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


##Fetch input sequences, RSCU table, organisms
my $filename	  = fileparse( $config{INPUT}, qr/\.[^.]*/);
make_path($filename . "_gdRT");
my $input		  = slurp( $config{INPUT} );
my $ORIG_SEQUENCE = fasta_parser( $input );

my $rscu		  = $config{RSCU_FILE}	?	slurp( $config{RSCU_FILE} )	:	0;
my $RSCU_DEFN	  = $rscu				?	rscu_parser( $rscu )		:	{};
	
my @ORGSDO		  = grep { exists $ORGANISMS{$_} }
					split( "", $config{ORGANISM} );
push @ORGSDO, 0	  if ($rscu);
$ORGNAME{0}		  = fileparse( $config{RSCU_FILE}, qr/\.[^.]*/) if ($rscu);

print "\n";

##Reverse Translate!
foreach my $org (@ORGSDO)
{
	my $OUTPUT = {};
	my $RSCU_VALUES = $org	?	define_RSCU_values( $org )	:	$RSCU_DEFN;
	my %defaults = define_aa_defaults($CODON_TABLE, $RSCU_VALUES);
	foreach my $seqkey (keys %$ORIG_SEQUENCE)
	{
		my $new_seq = reverse_translate( $$ORIG_SEQUENCE{$seqkey}, \%defaults );
		my $new_key = $seqkey . " after the reverse translate algorithm, using $ORGNAME{$org} RSCU values";
		$$OUTPUT{$new_key} = $new_seq;
	}
	open (my $fh, ">" . $filename . "_gdRT/" . $filename. "_gdRT_$org.FASTA") || die "can't create output file, $!";
	print $fh fasta_writer($OUTPUT);
	close $fh;
	print $filename . "_gdRT_$org.FASTA has been written.\n";
}

print "\n";
exit;