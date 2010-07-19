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

##Get Arguments
my %config = ();
GetOptions (
  	'input=s'		=> \$config{INPUT},
	'organism=i'    	=> \$config{ORGANISM},
        'rscu=s'                => \$config{RSCU_FILE},
	'sequences=s'		=> \$config{SHORT_SEQUENCE},
        'times=i'               => \$config{ITERATIONS},
	'lock=s'		=> \$config{LOCK},
 	'help'			=> \$config{HELP},
   );

##Respond to cries for help
if ($config{HELP}) {
    print "   
Short_Sequence_Subtraction.pl

     Given at least one nucleotide sequence as input, the
    Short_Sequence_Subtraction script searches through the sequence for
    targeted short sequences and attempts to remove the target sites from the
    sequence without changing the amino acid sequence by changing whole codons.
    
    The targeted codons may be replaced with random codons, using a user-defined
    codon table, or using the default codon table for a user-selected organism.
    
    Sites to remove can be provided one of two ways, following the formats of
    the provided sample files short_sequences.txt and short_sequences2.txt. The
    format of short_sequences.txt removes the same short sequences from all of
    nucleotide sequences, while the format of short_sequences2.txt allows for
    the removal of different short sequences from different sequences.
    
    Output will be named according to the name of the FASTA input file and will
    be tagged with the gdSSS suffix and the number of the organism used (or 0 if
    a custom RSCU table was provided or 7 if codons were replaced randomly).
    
  Usage examples:
   perl Short_Sequence_Subtraction.pl -i Test_YAR000W.FASTA -o 13 -s short_sequences.txt
    ./ Short_Sequence_Subtraction.pl --input Test_YAR000W.FASTA --rscu Test_
TY1_RSCU.txt --times 6 --sites short_sequences2.txt

 Required arguments:
    -i,   --input : a FASTA file containing nucleotide sequences.
    -s,   --sequences : the short sequences that will be silently removed

  Optional arguments:
    -h,   --help : Display this message
    -t,   --times : the number of iterations you want the algorithm to run
    -r,   --rscu : a txt file containing an RSCU table from gen_RSCU.pl
    -o,   --organism : at least one organism number.
    -l,   --lock : lock codons in the nucleotide sequence by their positions.
		   You may choose to do so by providing a file in a similar
		   format to the sample file or using the format
		   'num-num,num-num' when using this argument
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
die "\n ERROR: You did not provide a short sequence file!\n"
    if (! -e $config{SHORT_SEQUENCE});

warn "\n ERROR: Your RSCU file does not exist! Your target codons will be replaced by random codons.\n"
    if ($config{RSCU_FILE} && ! -e $config{RSCU_FILE});
warn "\n ERROR: Neither an organism nor an RSCU table were supplied. Your target codons will be replaced by random codons.\n"
    if (! $config{ORGANISM} && ! $config{RSCU_FILE});
warn "\n ERROR: Number of iterations was not supplied. The default number of 3 will be used.\n"
    if (! $config{ITERATIONS});
warn "\n WARNING: $_ is not a recognized organism and will be ignored.\n"
    foreach (grep {! exists($ORGANISMS{$_})} split ("", $config{ORGANISM}) );
    

##Fetch input nucleotide sequences, organisms, RSCU file, iterations, and short sequences file

my $filename  	  	= fileparse( $config{INPUT}, qr/\.[^.]*/);
make_path($filename . "_gdSSS");

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

$input           = slurp( $config{SHORT_SEQUENCE} ) ;
my %shortseq;
if (substr($input, 0, 1) eq '>'){
    %shortseq      = input_parser( $input );
}
else {
    my @temp_seq = split(/\n/, $input);
    foreach my $seqkey (keys %$nucseq) {
        $shortseq{$seqkey} = \@temp_seq;
    }
}

my $iter                = $config{ITERATIONS}   ?   $config{ITERATIONS}     : 3;

my $lock 		= $config{LOCK}		?   $config{LOCK}	    : 0;
my %lockseq;
if ($config{LOCK}) {
    if (my $ext = ($lock =~ m/([^.]+)$/)[0] eq 'txt') {
	$input = slurp( $config{LOCK} );
	%lockseq = input_parser( $input );
    }
    else {
	my @lockarr = split(/,/, $lock);
	foreach my $seqkey (keys %$nucseq) {
	    $lockseq{$seqkey} = \@lockarr;
	    print @{$lockseq{$seqkey}};
	}  
    }
}

## More consistency checking
foreach my $seqkey (keys %$nucseq) {
    foreach my $seq (@{$shortseq{$seqkey}}) {
	die "\n ERROR: You need a short sequence to be removed (at least 2 bp).\n" 
	    if (length($seq) < 2);
    }
}

print "\n";

#Finally removes short sequences
foreach my $org (@ORGSDO)
{
    my $OUTPUT = {};
    my $RSCU_VALUES = $org  ?   define_RSCU_values( $org )  :   $RSCU_DEFN;
    
    foreach my $seqkey (sort {$a cmp $b} keys %$nucseq)
    {
        
        my $oldnuc = $$nucseq{$seqkey};
        my $newnuc = $oldnuc;
        my ($Error4, $Error0, $Error5, $Error6, $Error7) = ("", "", "", "", "");
        my @success_seq = ();
        my @fail_seq = ();
        my @none_seq = ();
      
    	for (1..$iter) ##Where the magic happens
	{
	    my $warncount = 0;
            foreach my $remseq (@{$shortseq{$seqkey}})
            {
		if (length($remseq) >= length($newnuc)) { ## And yet more consistency checking
		    warn "\n ERROR: Your short sequence should be shorter than your nucleotide sequence!\n" if ($warncount == 0);
		    $warncount++;
		    last;
		}
		$remseq = cleanup($remseq, 0);
                my $arr = [ regres($remseq, 1) ];
                my $temphash = siteseeker($newnuc, $remseq, $arr);
                foreach my $grabbedpos (keys %$temphash)
                {
                    my $grabbedseq = $$temphash{$grabbedpos};
                    my $framestart = ($grabbedpos) % 3;
                    my $critseg = substr($newnuc, $grabbedpos - $framestart, ((int(length($grabbedseq)/3 + 2))*3));
                    my $newcritseg;
                    if (%$RSCU_VALUES) {
                        $newcritseg = pattern_remover($critseg, $arr, $CODON_TABLE, $RSCU_VALUES);
                    }
                    elsif (!%$RSCU_VALUES) {
                        $newcritseg = random_pattern_remover($critseg, $arr, $CODON_TABLE);
                    }
                    substr($newnuc, $grabbedpos - $framestart, length($newcritseg)) = $newcritseg if (scalar( keys %{siteseeker($newcritseg, $remseq, $arr)}) == 0);
                }
            }
	    if ($config{LOCK}) {
		$newnuc = check_lock($oldnuc, $newnuc, $CODON_TABLE, @{$lockseq{$seqkey}});
	    }
	}
        my $new_key = $seqkey . " after the short sequence subtraction algorithm for $ORGNAME{$org}";
        $$OUTPUT{$new_key} = $newnuc;
        
	foreach my $remseq (@{$shortseq{$seqkey}}) #Stores successfully and unsuccessfully removed sequences in respective arrays
	{
            my $arr = [ regres($remseq, 1) ];
            my $oldcheckpres = siteseeker($$nucseq{$seqkey}, $remseq, $arr);
            my $newcheckpres = siteseeker($newnuc, $remseq, $arr);
            push @none_seq, $remseq if scalar(keys %$oldcheckpres == 0);
            push @fail_seq, $remseq if (scalar(keys %$newcheckpres) != 0);
            push @success_seq, $remseq if (scalar (keys %$newcheckpres) == 0 && scalar (keys %$oldcheckpres != 0));
	}
        
        $Error6 = "The translation has changed!" if (translate($oldnuc, 1, $CODON_TABLE) ne translate($newnuc, 1, $CODON_TABLE));        
        $Error4 = "I was unable to remove @fail_seq after $iter iterations." if @fail_seq;
        $Error0 = "I successfully removed @success_seq from your sequence." if @success_seq;
        $Error5 = "There were no instances of @none_seq present in your sequence." if @none_seq;
        
        my $newal = compare_sequences($$nucseq{$seqkey}, $newnuc);
	my $bcou = count($newnuc);
        
        print "
For the sequence $new_key:
    I was asked to remove: @{$shortseq{$seqkey}}.
    $Error5
    $Error4
    $Error0
    $Error6
        Base Count: $$bcou{length} bp ($$bcou{A} A, $$bcou{T} T, $$bcou{C} C, $$bcou{G} G)
        Composition : $$bcou{GCp}% GC, $$bcou{ATp}% AT
        $$newal{'I'} Identities, $$newal{'D'} Changes ($$newal{'T'} transitions, $$newal{'V'} transversions), $$newal{'P'}% Identity
        
"
    }
            
    open (my $fh, ">" . $filename . "_gdSSS/" . $filename . "_gdSSS_$org.FASTA") || die "Cannot create output file, $!";
    print $fh fasta_writer($OUTPUT);
    close $fh;
    print $filename . "_gdSSS_$org.FASTA has been written.\n"
}

print "\n";

exit;
