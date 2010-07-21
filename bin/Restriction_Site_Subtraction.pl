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
	'lock=s'		=> \$config{LOCK},
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
    
    Sites can be provided one of two ways, following the formats of the
    provided sample files sites.txt and sites2.txt. The format of sites.txt
    removes the same restriction sites from all of nucleotide sequences, while
    the format of sites2.txt allows for the removal of different restriction
    sites from different sequences.
    
    Output will be named according to the name of the FASTA input file and will
    be tagged with the gdRSS suffix and the number of the organism used (or 0 if
    a custom RSCU table was provided or 7 if codons were replaced randomly).
    
  Usage examples:
   perl Restriction_Site_Subtraction.pl -i Test_YAR000W.FASTA -o 13 -s sites.txt
    ./ Restriction_Site_Subtraction.pl --input Test_YAR000W.FASTA --rscu Test_
TY1_RSCU.txt --times 6 --sites sites2.txt --lock lock.txt

 Required arguments:
    -i,   --input : a FASTA file containing nucleotide sequences.
    -s,   --sites : the restriction enzymes sites that will be silently removed
                    You	may choose to format the input in one of two ways, as
		    shown in the sample files.

  Optional arguments:
    -h,   --help : Display this message
    -t,   --times : the number of iterations you want the algorithm to run
    -r,   --rscu : a txt file containing an RSCU table from gen_RSCU.pl
    -o,   --organism : at least one organism number.
        Each organism given represents another iteration the algorithm must run.
        (1 = S.cerevisiae,  2 = E.coli,         3 = H.sapiens,
         4 = C.elegans,     5 = D.melanogaster, 6 = B.subtilis)
    -l,   --lock : lock codons in the nucleotide sequence by their positions.
               You may choose to do so by providing a file in a similar
               format to the sample file or using the format
               'num-num,num-num' when using this argument
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

if ( !$config{ORGANISM} && ! $config{RSCU_FILE} ) {
    push @ORGSDO, 7;
    $ORGNAME{7}         = 'random codons';
}

$input                 = slurp( $config{RESTRICTION_SITES} ) ; ##Now there are two ways to give restriction site input!
my %remove_RE;
if (substr($input, 0, 1) eq '>'){
    %remove_RE      = input_parser( $input );
}
else {
    my @temp_RE = split(/\n/, $input);
    foreach my $seqkey ( keys %$nucseq ) {
        $remove_RE{$seqkey} = \@temp_RE;
    }
}

my $iter                = $config{ITERATIONS}   ?   $config{ITERATIONS}     : 3;

my $lock 		= $config{LOCK}		?   $config{LOCK}	    : 0;
my %lockseq;
if ( $config{LOCK} ) {
    if ( my $ext = ( $lock =~ m/([^.]+)$/ )[0] eq 'txt' ) {
	$input = slurp( $config{LOCK} );
	%lockseq = input_parser( $input );
    }
    else {
	%lockseq = lock_parser( $lock, $nucseq );
    }
}

print "\n";


##Finally subtracts restriction enzymes

foreach my $org (@ORGSDO)
{
    my $OUTPUT = {};
    my %RE_OUTPUT;
    my $RSCU_VALUES = $org  ?   define_RSCU_values( $org )  :   $RSCU_DEFN;
    
    foreach my $seqkey (sort {$a cmp $b} keys %$nucseq)
    {
        my $oldnuc = $$nucseq{$seqkey};
        my $newnuc = $oldnuc;
        my ($Error4, $Error0, $Error5, $Error6, $Error7, $Error8) = ("", "", "", "", "", "");
        my @success_enz = ();
        my @fail_enz = ();
        my @none_enz = ();
	my @semifail_enz = ();
	my %lock_enz = ();
      
    	for ( 1..$iter ) ##Where the magic happens
	{
            foreach my $enz ( @{ $remove_RE{$seqkey} } )
            {
                my $temphash = siteseeker($newnuc, $enz, $$RE_DATA{REGEX}->{$enz});
                foreach my $grabbedpos ( keys %$temphash )
                {
                    my $grabbedseq = $$temphash{$grabbedpos};
                    my $framestart = ($grabbedpos) % 3;
                    my $critseg = substr($newnuc, $grabbedpos - $framestart, ((int(length($grabbedseq)/3 + 2))*3));
                    my $newcritseg;
                    if ( %$RSCU_VALUES )
                    {
                        $newcritseg = pattern_remover($critseg, $$RE_DATA{CLEAN}->{$enz}, $CODON_TABLE, $RSCU_VALUES);
                    }
                    elsif ( !%$RSCU_VALUES )
                    {
                        $newcritseg = random_pattern_remover($critseg, $$RE_DATA{CLEAN}->{$enz}, $CODON_TABLE);
                    }
                    substr($newnuc, $grabbedpos - $framestart, length($newcritseg)) = $newcritseg if (scalar( keys %{siteseeker($newcritseg, $enz, $$RE_DATA{REGEX}->{$enz})}) == 0);
                }
            }
	    if ( $config{LOCK} ) {
		($newnuc, @{ $lockseq{$seqkey} }) = replace_lock($oldnuc, $newnuc, $CODON_TABLE, @{ $lockseq{$seqkey} });
	    }
	}
        my $new_key = $seqkey . " after the restriction site subtraction algorithm for $ORGNAME{$org}";
        $$OUTPUT{$new_key} = $newnuc;
        
	foreach my $enz (@{ $remove_RE{$seqkey} }) #Stores successfully and unsuccessfully removed enzymes in respective arrays
	{
            my $oldcheckpres = siteseeker($$nucseq{$seqkey}, $enz, $$RE_DATA{REGEX}->{$enz});
            my $newcheckpres = siteseeker($newnuc, $enz, $$RE_DATA{REGEX}->{$enz});
            push @none_enz, $enz if ( scalar( keys %$oldcheckpres ) == 0 );
	    push @success_enz, $enz if (( scalar ( keys %$newcheckpres ) == 0) && (scalar ( keys %$oldcheckpres ) != 0 ));
            push @fail_enz, $enz if ((scalar( keys %$newcheckpres ) != 0) && (scalar( keys %$newcheckpres ) == scalar( keys %$oldcheckpres )));
	    if ( $config{LOCK} && ( scalar ( keys %$newcheckpres ) != 0 ))
	    {
		$lock_enz{$enz} = 0;
		%lock_enz = check_lock($newcheckpres, $enz, \@{ $lockseq{$seqkey} }, %lock_enz);
                print $lock_enz{$enz};
	    }	
            push @semifail_enz, $enz if ((scalar( keys %$newcheckpres ) != 0) && ((exists( $lock_enz{$enz} ) && ( $lock_enz{$enz} < scalar( keys %$oldcheckpres ))) 
					    || (scalar( keys %$newcheckpres ) < scalar( keys %$oldcheckpres ))) && ( !grep { $_ eq $enz} @fail_enz ));
	}
        
        $Error4 = "\n\tI was unable to remove @fail_enz after $iter iterations." if @fail_enz;
        $Error0 = "\n\tI successfully removed @success_enz from your sequence." if @success_enz;
        $Error5 = "\n\tThere were no instances of @none_enz present in your sequence." if @none_enz;
        $Error7 = "\n\tI was unable to remove some instances of @semifail_enz after $iter iterations." if @semifail_enz;
	if ( $config{LOCK} && %lock_enz ) {
	    while ( my ( $k,$v ) = each %lock_enz ) {
	    $Error8 .= "\n\tI was unable to remove $v instance(s) of $k, as all or part of $k was locked." if ($v != 0);
	    }
	}
        
        my $newal = compare_sequences($oldnuc, $newnuc);
	my $bcou = count($newnuc);
        
        print "
For the sequence $new_key:
    I was asked to remove: @{ $remove_RE{$seqkey} }. $Error5 $Error4 $Error0 $Error7 $Error8
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
