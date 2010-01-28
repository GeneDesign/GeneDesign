#!/usr/bin/perl
use strict;

use Getopt::Long;
use File::Basename qw(fileparse);
use GeneDesign;
use Perl6::Slurp;

$| = 1;

my $CODON_TABLE = define_codon_table(1);
my %aas =  map {$_ => 1} values %$CODON_TABLE;

##Get Arguments
my %config = ();
GetOptions (
			'input=s'		=> \$config{INPUT},
			'help'			=> \$config{HELP}
		   );

##Respond to cries of help, if applicable
if ($config{HELP})
{
	print "
Generate_RSCU_Table.pl
	
    Given at least one protein-coding gene as input, the Generate_RSCU_Table
    script generates a table of RSCU values that represents the bias in codon 
    usage.

    Output will be named according to the name of the FASTA input file, and will
    be tagged with the gdRSCU suffix.
	
  Usage examples:
    perl Generate_RSCU_Table.pl -i=Test_YAR000W.FASTA
    ./Generate_RSCU_Table.pl --input=Test_YAR000W.FASTA

  Required arguments:
    -i,   --input : a FASTA file containing nucleotide sequences.
  
  Optional arguments:
    -h    --help : Display this message.

";
	exit;
}

##Check the consistency of arguments
die "\n ERROR: $config{INPUT} does not exist.\n"
	if (! -e $config{INPUT});

##Fetch input sequences
my $filename	  = fileparse( $config{INPUT}, qr/\.[^.]*/) . "_RSCU.txt";
my $input		  = slurp( $config{INPUT} );
my $ORIG_SEQUENCE = fasta_parser( $input );
warn "\nWARNING: $_ is not the right length for an ORF and will be ignored.\n"
	foreach (grep {length($$ORIG_SEQUENCE{$_}) % 3} keys %$ORIG_SEQUENCE );
print "\n";

my @values = grep {length($_) % 3 == 0} values %$ORIG_SEQUENCE;
my $codcount = codon_count(\@values, $CODON_TABLE);
my $RSCUVal = generate_RSCU_values($codcount, $CODON_TABLE);

my @out =	map { $_ . " (" . $$CODON_TABLE{$_} . ") ". $$RSCUVal{$_} ."\n"} 
			sort {	$$CODON_TABLE{$a} cmp $$CODON_TABLE{$b} 
				||	$$RSCUVal{$b} <=> $$RSCUVal{$a}} 
			keys %$RSCUVal; 

open (my $fh, ">" . $filename ) || die "can't create output file, $!";
print $fh @out;
close $fh;
print $filename, " has been written.\n";

exit;