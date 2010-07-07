#!/usr/bin/perl -w
use strict;
use warnings;

use Getopt::Long;
use File::Basename qw(fileparse);
use File::Path qw(make_path);
use Perl6::Slurp;
use GeneDesign;

my %ORGNAME = %ORGANISMS;
my $CODON_TABLE = define_codon_table(1);
my $RE_DATA = define_sites($enzfile);


##Get Arguments
my %config = ();
GetOptions (
  	'input=s'		=> \$config{INPUT},
	'organism=i'    	=> \$config{ORGANISM},
        'rscu=s'                => \$config{RSCU_FILE},
	'sites=s'		=> \$config{RESTRICTION_SITES},
        'times=i'               => \$config{ITERATIONS},
 	'help'			=> \$config{HELP},
   );

##Respond to cries for help
if ($config{HELP}) {
    print "
Restriction_Site_Subtraction.pl
    
    Given at least one nucleotide sequence as input, the
    Restriction_Site_Subtraction script searches through the sequence for
    targeted restriction enzymes and attempts to remove the sites from the
    sequence without changing the amino acid sequence by changing whole codons.
    
    The targeted codons may be replaced with random codons, using a user-defined
    codon table, or using the default codon table for a user-selected organism.
    
    Output will be named according to the name of the FASTA input file and will
    be tagged with the gdRSS suffix and the number of the organism used (or 0 if
    a custom RSCU table was provided or 7 if codons were replaced randomly).
    
  Usage examples:
   perl Restriction_Site_Subtraction.pl -i Test_YAR000W.FASTA -o 13 -s sites.txt
    ./ Restriction_Site_Subtraction.pl --input Test_YAR000W.FASTA --rscu Test_
TY1_RSCU.txt --times 6 --sites sites.txt

 Required arguments:
    -i,   --input : a FASTA file containing protein sequences.
    -s,   --sites : the restriction enzymes sites that will be silently removed

  Optional arguments:
    -h,   --help : Display this message
    -t,   --times : the number of iterations you want the algorithm to run
    -r,   --rscu : a txt file containing an RSCU table from gen_RSCU.pl
    -o,   --organism : at least one organism number.
        Each organism given represents another iteration the algorithm must run.
        (1 = S.cerevisiae,  2 = E.coli,         3 = H.sapiens,
         4 = C.elegans,     5 = D.melanogaster, 6 = B.subtilis)
    Note:
    -r and/or -o may be provided. If both are given the table will be treated as
    another organism, named after the table's filename. If neither are given,
    then the script will replace the sites with random codons.
    
    
";
    exit;
}

##Check the consistency of arguments
die "\n ERROR: The input file does not exist!\n"
    if (! -e $config{INPUT});
die "\n ERROR: You did not provide a restriction sites file!\n"
    if (! -e $config{RESTRICTION_SITES});

warn "\n ERROR: Your RSCU file does not exist! Your target codons will be replaced by random codons.\n"
    if ($config{RSCU_FILE} && ! -e $config{RSCU_FILE});
warn "\n ERROR: Neither an organism nor an RSCU table were supplied. Your target codons will be replaced by random codons.\n"
    if (! $config{ORGANISM} && ! $config{RSCU_FILE});
warn "\n ERROR: Number of iterations was not supplied. The default number of 3 will be used.\n"
    if (! $config{ITERATIONS});
warn "\n WARNING: $_ is not a recognized organism and will be ignored.\n"
    foreach (grep {! exists($ORGANISMS{$_})} split ("", $config{ORGANISM}) );


##Fetch input nucleotide sequences, organisms, RSCU file, iterations, and restriction site file

my $filename  	  	= fileparse( $config{INPUT}, qr/\.[^.]*/);
make_path($filename . "_gdRSS");

my $input    	  	= slurp( $config{INPUT} );
my $nucseq 	        = fasta_parser( $input );

my $rscu                = $config{RSCU_FILE}    ?   $config{RSCU_FILE}      : 0;
my $RSCU_DEFN           = $rscu                 ?   rscu_parser( $rscu )    : {};

my @ORGSDO		= grep { exists $ORGANISMS{$_} } split( "", $config{ORGANISM} );

push @ORGSDO, 0     if ($rscu);
$ORGNAME{0}         = fileparse ( $config{RSCU_FILE} , qr/\.[^.]*/)     if ($rscu);

if (! $config{ORGANISM} && ! $config{RSCU_FILE}) {
    push @ORGSDO, 7;
    $ORGNAME{7}         = 'random codons';
}

my @remove_RE           = slurp( $config{RESTRICTION_SITES} ) ;
chomp (@remove_RE);

my $iter                = $config{ITERATIONS}   ?   $config{ITERATIONS}     : 3;

print "\n";


##Finally subtracts restriction enzymes

foreach my $org (@ORGSDO)
{
    my $OUTPUT = {};
    my $RSCU_VALUES = $org  ?   define_RSCU_values( $org )  :   $RSCU_DEFN;
    
    foreach my $seqkey (sort {$a cmp $b} keys %$nucseq)
    {
        
        my $newnuc = $$nucseq{$seqkey};
        my ($Error4, $Error0, $Error5) = ("", "", "");
        my @success_enz = ();
        my @fail_enz = ();
        my @none_enz = ();
      
    	for (1..$iter) ##Where the magic happens
	{
            foreach my $enz (@remove_RE)
            {	
                my $temphash = siteseeker($newnuc, $enz, $$RE_DATA{REGEX}->{$enz});
                foreach my $grabbedpos (keys %$temphash)
                {
                    my $grabbedseq = $$temphash{$grabbedpos};
                    my $framestart = ($grabbedpos) % 3;
                    my $critseg = substr($newnuc, $grabbedpos - $framestart, ((int(length($grabbedseq)/3 + 2))*3));
                    my $newcritseg;
                    if (%$RSCU_VALUES) {
                        $newcritseg = pattern_remover($critseg, $$RE_DATA{CLEAN}->{$enz}, $CODON_TABLE, $RSCU_VALUES);
                    }
                    elsif (!%$RSCU_VALUES) {
                        $newcritseg = random_pattern_remover($critseg, $$RE_DATA{CLEAN}->{$enz}, $CODON_TABLE);
                    }
                    substr($newnuc, $grabbedpos - $framestart, length($newcritseg)) = $newcritseg if (scalar( keys %{siteseeker($newcritseg, $enz, $$RE_DATA{REGEX}->{$enz})}) == 0);
                }
            }
	}
        my $new_key = $seqkey . " after the restriction site subtraction algorithm for $ORGNAME{$org}";
        $$OUTPUT{$new_key} = $newnuc;
        
	foreach my $enz (@remove_RE) #Stores successfully and unsuccessfully removed enzymes in respective arrays
	{
            my $oldcheckpres = siteseeker($$nucseq{$seqkey}, $enz, $$RE_DATA{REGEX}->{$enz});
            my $newcheckpres = siteseeker($newnuc, $enz, $$RE_DATA{REGEX}->{$enz});
            push @none_enz, $enz if scalar(keys %$oldcheckpres == 0);
            push @fail_enz, $enz if (scalar(keys %$newcheckpres) != 0);
            push @success_enz, $enz if (scalar (keys %$newcheckpres) == 0 && scalar (keys %$oldcheckpres != 0));
	}
        
        $Error4 = "I was unable to remove @fail_enz after $iter iterations." if @fail_enz;
        $Error0 = "I successfully removed @success_enz from your sequence." if @success_enz;
        $Error5 = "There were no instances of @none_enz present in your sequence." if @none_enz;
        
        my $newal = compare_sequences($$nucseq{$seqkey}, $newnuc);
	my $bcou = count($newnuc);
        
        print "
For the sequence $new_key:
    I was asked to remove: @remove_RE.
    $Error5
    $Error4
    $Error0
        Base Count: $$bcou{length} bp ($$bcou{A} A, $$bcou{T} T, $$bcou{C} C, $$bcou{G} G)
        Composition : $$bcou{GCp}% GC, $$bcou{ATp}% AT
        $$newal{'I'} Identities, $$newal{'D'} Changes ($$newal{'T'} transitions, $$newal{'V'} transversions), $$newal{'P'}% Identity
        
"
    }
            
    open (my $fh, ">" . $filename . "_gdRSS/" . $filename . "_gdRSS_$org.FASTA") || die "Cannot create output file, $!";
    print $fh fasta_writer($OUTPUT);
    close $fh;
    print $filename . "_gdRSS_$org.FASTA has been written.\n"
}

print "\n";

exit;
