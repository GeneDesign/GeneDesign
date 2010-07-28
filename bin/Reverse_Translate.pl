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

##Get Arguments
my %config = ();
GetOptions (
			'input=s'		=> \$config{INPUT},
			'rscu=s'		=> \$config{RSCU_FILE},
			'organism=i'		=> \$config{ORGANISM},
			'help'			=> \$config{HELP},
			'table=s'		=> \$config{TABLE},
			'write=s'		=> \$config{WRITE},
		   );


##Respond to cries of help, if applicable
if ($config{HELP})
{
	print "
Reverse_Translation.pl
	
    Given at least one protein sequence as input, the Reverse_Translation script
    generates synonymous nucleotide sequences using either a user-defined codon
    table or the most optimal codons for expression in a user-selected organism.
	
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
    -t,   --table : a table of codons
    -r, -t, OR -o must be provided. If any combinations of these are given,the
	codon table and/or rscu table will be treated as another organism, named
	after the filename(s).

  Optional arguments:
    -h,   --help : Display this message
    -w,   --write : Write to another path


";
	exit;
}


##Check the consistency of arguments
die "\n ERROR: Neither an organism, an RSCU table, nor a codon table were supplied.\n"
	if (! $config{ORGANISM} && ! $config{RSCU_FILE} && ! $config{TABLE});
die "\n ERROR: $config{INPUT} does not exist.\n"
	if (! -e $config{INPUT});
die "\n ERROR: $config{RSCU_FILE} does not exist.\n"
	if ($config{RSCU_FILE} && ! -e $config{RSCU_FILE});
die "\n ERROR: $config{TABLE} does not exist.\n"
	if ($config{TABLE} && ! -e $config{TABLE});
warn "\n WARNING: $_ is not a recognized organism and will be ignored.\n"
	foreach (grep {! exists($ORGANISMS{$_})} split ("", $config{ORGANISM}) );


##Fetch input sequences, RSCU table, organisms
my ($name, $path) = fileparse($config{INPUT}, qr/\.[^.]*/);
my $filename	  = $path . "/" . $name;
make_path($filename . "_gdRT");
my $input	  = slurp( $config{INPUT} );
my $ORIG_SEQUENCE = fasta_parser( $input );

my $rscu	  = $config{RSCU_FILE}	?	slurp( $config{RSCU_FILE} )	:	0;
my $RSCU_DEFN	  = $rscu		?	rscu_parser( $rscu )		:	{};

my $table	  = $config{TABLE}	?	slurp( $config{TABLE} )	:	0;
my %codon_scheme;
if ($table)
{
	my @pair = split(/[\n]/g, $table);
	foreach my $entry (@pair) {
		my $id = shift @pair;
		$codon_scheme{$id} = shift @pair;
	}
}
else
{
	%codon_scheme = ();
}
	
my @ORGSDO	  = grep { exists $ORGANISMS{$_} } split( "", $config{ORGANISM} );
push @ORGSDO, 0	  if ($rscu);
push @ORGSDO, 8   if ($table);
$ORGNAME{0}	  = fileparse( $config{RSCU_FILE}, qr/\.[^.]*/) if ($rscu);
$ORGNAME{8}	  = fileparse( $config{TABLE}, qr/\.[^.]*/) if ($table);

print "\n";

##Reverse Translate!
foreach my $org (@ORGSDO)
{
	my $OUTPUT = {};
	my $RSCU_VALUES = $org	?	define_RSCU_values( $org )	:	$RSCU_DEFN;
	%codon_scheme = $table 	? 	%codon_scheme 			:       define_aa_defaults($CODON_TABLE, $RSCU_VALUES);
	
	my $ERROR1 = "";
	open (my $eh, ">" . $filename . "_gdRT/error.txt");
	foreach my $seqkey (keys %$ORIG_SEQUENCE)
	{
		my $new_seq = reverse_translate( $$ORIG_SEQUENCE{$seqkey}, \%codon_scheme );
		my $new_key = $seqkey . " after the reverse translate algorithm, using $ORGNAME{$org} RSCU values";
		$$OUTPUT{$new_key} = $new_seq;
		if (length($$ORIG_SEQUENCE{$seqkey}) < length($new_seq)/3 || $$ORIG_SEQUENCE{$seqkey} ne translate($new_seq, 1, $CODON_TABLE))
		{
			my $errout = "\n" . $$ORIG_SEQUENCE{$seqkey} . "\n" . translate($new_seq, 1, $CODON_TABLE) . "\nCodons:\n";
			$errout .= " $_, $codon_scheme{$_}\n" foreach (sort keys %codon_scheme);
			print $eh "\nI was unable to reverse translate your sequence.  Perhaps you left something out of your codon table?\n$errout\n\n";
		}
	}
	open (my $fh, ">" . $filename . "_gdRT/" . $name. "_gdRT_$org.FASTA") || die "can't create output file, $!";
	print $fh fasta_writer($OUTPUT);
	close $fh;
	close $eh;
	print $filename . "_gdRT_$org.FASTA has been written.\n";
}

print "\n";
exit;