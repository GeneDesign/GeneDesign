## GeneDesign
#  Sarah Richardson
#  Paul Nunley
package GeneDesign;
use 5.006;
require Exporter;
use POSIX(log10);
use List::Util qw(shuffle min first);
use List::MoreUtils qw(uniq);
use Class::Struct;
use Perl6::Slurp;

@ISA = qw(Exporter);
@EXPORT = qw(define_sites overhang define_site_status siteseeker filter_sites mutexclu first_base report_RE
			define_aa_names define_aa_defaults  define_codon_table define_reverse_codon_table define_RSCU_values 
			define_codon_percentages index_codon_percentages
			pattern_remover pattern_adder pattern_aligner pattern_finder compare_sequences change_codons randDNA
			count ntherm compareseqs reverse_translate amb_transcription amb_translation degcodon_to_aas translate regres complement melt cleanup
			oligocruncher orf_finder define_oligos fasta_parser cons_seq print_alignment
			codon_count generate_RSCU_values rscu_parser
			%AA_NAMES $IIA $IIA2 $IIA3 $IIP $IIP2 $ambnt %ORGANISMS $treehit $strcodon $docpath $linkpath $enzfile
			);
			
struct REnz => { map { $_ => '$' } qw(SiteNumber CutterName AARecogniz NtRecogniz NtPosition MustChange NewSequenc Sticky RxnTemp StarAct 
					UPrice Methyb Methyi CutsAt Dirt Vendor) };

struct Oligo => { map { $_ => '$' } qw(ChunkNumber OligoNumber OligoLength OligoStart OligoStop OligoSense FpOlapLeng TpOlapLeng OligoSeq) };

struct Chunk => { map { $_ => '$' } qw(Parameters ChunkNumber NumberofOligos ChunkLength AvgOligoLength ChunkStart ChunkStop Collisions AvgGapLeng AvgOlapLeng 
					AvgOlapMelt ChunkSeq Oligos Olaps Users FivePrimeEnz ThreePrimeEnz ShrtOligo LongOligo ThreePrimeOlap Mask Name) };

struct USERsite => { map { $_ => '$' } qw(Start nNumber Sequence) };

our $docpath = "../../Documents/gd";
our $linkpath = "http://localhost/gd";
our $enzfile = "bs_enzymes.txt";

my %NTIDES = (A => "A", B => "[BCGKSTY]", C => "C", D => "[ADGKRTW]", G => "G", H => "[ACHMTWY]", K => "[GKT]", M => "[ACM]", 
				   N => "[ABCDGHKMNRSTVWY]", R => "[AGR]", S => "[CGS]", T => "T", V => "[ACGMRSV]", W => "[ATW]", Y => "[CTY]", );
our @NTS = qw(A T C G);
our @NTSG = qw(B D H K M N R S V W Y);

my %AACIDS = map { $_, $_ } qw(A C D E F G H I K L M N P Q R S T V W Y);
$AACIDS{"*"} = "[\*]";

our %AA_NAMES = (A => "Ala", B => "Unk", C => "Cys", D => "Asp", E => "Glu", F => "Phe", G => "Gly", H => "His", I => "Ile",  
				 J => "Unk", K => "Lys", L => "Leu", M => "Met", N => "Asn", O => "Unk", P => "Pro", Q => "Gln", R => "Arg", 
				 S => "Ser", T => "Thr", U => "Unk", V => "Val", W => "Trp", X => "Unk", Y => "Tyr", Z => "Unk","*" => "Stp");

# entropy, enthalpy, and free energy of paired bases ÆHû   ÆSû  ÆGû
my %TEEFE = ("TC" => ([ 8.8, 23.5, 1.5]), "GA" => ([ 8.8, 23.5, 1.5]), "CT" => ([ 6.6, 16.4, 1.5]), "AG" => ([ 6.6, 16.4, 1.5]),
			 "GG" => ([10.9, 28.4, 2.1]), "CC" => ([10.9, 28.4, 2.1]), "AA" => ([ 8.0, 21.9, 1.2]), "TT" => ([ 8.0, 21.9, 1.2]),
			 "AT" => ([ 5.6, 15.2, 0.9]), "TA" => ([ 6.6, 18.4, 0.9]), "CG" => ([11.8, 29.0, 2.8]), "GC" => ([10.5, 26.4, 2.3]),
			 "CA" => ([ 8.2, 21.0, 1.7]), "TG" => ([ 8.2, 21.0, 1.7]), "GT" => ([ 9.4, 25.5, 1.5]), "AC" => ([ 9.4, 25.5, 1.5]));

our %ORGANISMS = (0 => "(no organism defined)", 1 => "Saccharomyces cerevisiae", 2 => "E. coli", 3 => "Homo sapiens", 4 => "C. elegans", 5 => "Drosophila melanogaster", 6 => "Bacillus subtilis");
	
our $IIA		= qr/ \( (    \d+) \/ (   \d+) \)	/x;
our $IIA2		= qr/ \( (    \d+) \/ (\- \d+) \)	/x;
our $IIA3		= qr/ \( (\-  \d+) \/ (\- \d+) \)	/x;
our $IIP		= qr/    ([A-Z]+) \^ [A-Z]*			/x;
our $IIP2		= qr/ \^ ([A-Z]+)					/x;
our $treehit	= qr/(\d+): ([A-Z0-9a-z]+) ([A-Z]+)/;
my $nonawords	= qr/[^\w*]*/;
my $nonwords	= qr/\W*/;
my $fastaline	= qr/\A>[\S\ ]*[\n\r]{1}/;
my $nonaa		= qr/[BJOUX]{1}/;
our $ambnt		= qr/[RYWSKMBDHVN]+/;
our $strcodon	= qr/[ATCG]{3}/;


use strict;
	
#### count ####
# takes a nucleotide sequence and returns a base count.  Looks for total length, purines, pyrimidines, and degenerate bases.   
#  If degenerate bases are present assumes their substitution for non degenerate bases is totally random for percentage estimation. 
# in: nucleotide sequence (string),
# out: base count (hash)
# 0 cleanup
sub count
{
	my ($strand) = @_;
	return if (!$strand);
	my $BC = {};
	$$BC{'length'} = length($strand);
	foreach (@NTS, @NTSG)	{	$$BC{$_}   = ($strand =~ s/$_//ig || 0);	};
	foreach (@NTS)			{	$$BC{'d'} += $$BC{$_};			};
	foreach (@NTSG)			{	$$BC{'n'} += $$BC{$_};			};
	$$BC{'?'} = ($$BC{'d'} + $$BC{'n'}) - $$BC{'length'};
	$$BC{'U'} = ($strand =~ s/U//ig || 0);
	my $split = .5*$$BC{'R'}    + .5*$$BC{'Y'}    + .5*$$BC{'K'}    + .5*$$BC{'M'}    + .5*$$BC{'N'};
	my $trip  = (2/3)*$$BC{'B'} + (2/3)*$$BC{'V'} + (1/3)*$$BC{'D'} + (1/3)*$$BC{'H'};
	$$BC{'GCp'} = int(((($$BC{'S'}+$$BC{'G'}+$$BC{'C'}+$split + $trip)/$$BC{'length'})*100)+.5);
	$$BC{'ATp'} = int(((($$BC{'W'}+$$BC{'A'}+$$BC{'T'}+$split + (.9-$trip))/$$BC{'length'})*100)+.5);
	return $BC;
}

#### melt ####
# takes a nucleotide sequence and returns a melting temperature.  Has four different formulas.   
# in: nucleotide sequence (string), formula number (1 simple, 2 baldwin, 3 primer3, or 4 nntherm), 
#   salt concentration (string, opt, def =.05), oligo concentration (string, opt, def = .0000001)
# out: temperature (string)
sub melt
{
	my ($strand, $swit, $salt, $conc) = @_;
	return if (!$strand);
	$swit = $swit || 3;
	$salt = $salt || .05;
	$conc = $conc || .0000001;
	my $mgc = 1.987;
	my $BC = count($strand);
	if ($swit == 1) #simple
	{
		return ((4 * ($$BC{'C'} + $$BC{'G'})) + (2 * ($$BC{'A'} + $$BC{'T'})));
	}
	if ($swit == 2 || $swit == 3) #baldwin, primer3
	{
		my $base = 81.5 + 16.6*log10($salt) + 41*(($$BC{'C'}+$$BC{'G'})/length($strand));
		return $base - (675/length($strand)) if ($swit == 2);
		return $base - (600/length($strand)) if ($swit == 3);
	}
	if ($swit == 4) ##nntherm
	{
		my ($dH, $dS, $dG) = ntherm($strand);
		return  ((($dH-3.4) / (($dS+($mgc*abs(log($conc/4))))/1000))-273.15) + (16.6*log10($salt));
	}
	return undef;
}

#### ntherm ####
# takes a nucleotide sequence and returns entropy, enthalpy, and free energy.   
# in: nucleotide sequence (string) 
# out: entropy, enthalpy, and free energy (array of integers)
sub ntherm
{
	my ($strand) = @_;
	my ($dH, $dS, $dG) = (0, 0, 0);
	foreach my $w (keys %TEEFE)
	{	
		while ($strand =~ /(?=$w)/ig)
		{
			$dH += $TEEFE{$w}->[0];
			$dS += $TEEFE{$w}->[1];
			$dG += $TEEFE{$w}->[2];
		}
	}
	return ($dH, $dS, $dG);
}

#### complement ####
# takes a nucleotide sequence and returns its complement or reverse complement.
# in: nucleotide sequence (string), switch for reverse complement (1 or null)
# out: nucleotide sequence (string)
sub complement
{
	my ($strand, $swit) = @_;
	return undef if (!$strand);
	$strand = scalar reverse($strand) if ($swit);
	$strand =~ tr/ACGTRYKMSWBDHV/TGCAYRMKSWVHDB/;
	return $strand;
}

#### regres ####
# takes a  sequence that may be degenerate and returns a string that is prepped for use in a regular expression.
# in: sequence (string), switch for aa or nt sequence (1 or null)
# out: regexp string (string)
# 0 cleanup
sub regres
{
	my ($sequence, $swit) = @_;
	return if (!$sequence);
	$swit = 1 if (!$swit);
	my $comp = "";
	foreach my $char (split('', $sequence))
	{
		if ($swit == 1)
		{
			$comp .= exists $NTIDES{$char}	?	$NTIDES{$char}	:	"[X]";
		}
		elsif ($swit == 2)
		{
			$comp .= exists $AACIDS{$char}	?	$AACIDS{$char}	:	"[X]";
		}	
	}
	return $comp;
}

#### compareseqs ####
# takes nucleotide sequences and returns 1 if either could be said to be a perfect or degenerate copy of the other
# in: 2x nucleotide sequence (string)
# out: 1 OR 0
sub compareseqs
{
	my ($cur, $tar) = @_;
	return 1 if ($tar =~ regres($cur, 1) || $cur =~ regres($tar, 1));
	return 0;
}

#### translate ####
# takes a nucleotide sequence, a frame, and a codon table and returns that frame translated into amino acids.
# in: nucleotide sequence (string), switch for frame (±1, ±2, or ±3), codon table (hash reference)
# out: amino acid sequence (string)
sub translate
{
	my ($nucseq, $swit, $CODON_TABLE) = @_;
#	return if ( ! $nucseq	||	$nucseq =~ $ambnt);
	$nucseq = complement($nucseq, 1) if ($swit < 0);
	my $peptide = "";
	for (my $offset = abs($swit)-1; $offset < length($nucseq); $offset += 3)
	{
		my $codon = substr($nucseq, $offset, 3);
		$peptide .= $$CODON_TABLE{$codon} if (exists $$CODON_TABLE{$codon});
	}
	return $peptide;
}

#### reverse_translate ####
# takes an amino acid sequence and a specific codon table and returns that frame translated into amino acids.  See gdRevTrans.cgi for use.
# in: nucleotide sequence (string), switch for frame (1, 2, or 3), codon table (hash reference)
# out: amino acid sequence (string)
# 0 cleanup
sub reverse_translate
{
	my($aaseq, $codonhash) = @_;
	my $newseq = "";
	$newseq .= $$codonhash{$_} foreach (split('', $aaseq));
	return $newseq;
}

#### degcodon_to_aas ####
# takes a codon that may be degenerate and a codon table and returns a list of all amino acids that codon could represent.
# in: codon (string), codon table (hash reference)
# out: amino acid list (vector)
sub degcodon_to_aas 
{
	my ($codon, $CODON_TABLE) = @_;	
	return if ( ! $codon	||	length($codon) != 3);
	my $reg = regres($codon, 1);
	return uniq map { $$CODON_TABLE{$_} } grep { $_ =~ $reg } keys %$CODON_TABLE;
}

#### amb_translation ####
# takes a nucleotide that may be degenerate and a codon table and returns a list of all amino acid sequences that nucleotide sequence could be translated into.
# in: nucleotide sequence (string), codon table (hash reference)
# out: amino acid sequence list (vector)
# 0 cleanup
sub amb_translation
{
	my ($site, $CODON_TABLE, $swit) = @_;
	$site = 'NN' . $site if (!$swit);
	my (@RES, @SEED, @NEW);
	for (my $j = 0; $j < 3; $j++)
	{
		my $gothrough = 0;
		for (my $offset = $j; $offset < (int(length($site))); $offset +=3)
		{
			my $tempcodon = substr($site, $offset, 3);
			if (!$swit)
			{
				$tempcodon .= 'N' while (length($tempcodon) < 3);
			}
			if ($gothrough == 0)
			{
				@SEED = degcodon_to_aas($tempcodon, $CODON_TABLE) ;
			}
			else
			{
				@NEW  = degcodon_to_aas($tempcodon, $CODON_TABLE);
				@SEED = combine(\@SEED, \@NEW);
			}
			$gothrough++;
		}
		push @RES, @SEED;
	}
	return uniq @RES;
}

#### amb_transcription ####
# takes an ambiguous nucleotide sequence and returns a list of all possible non ambiguous nucleotide sequences it could represent
# in: nucleotide sequence (string), codon table (hash reference), reverse codon table (hash reference)
# out: nucleotide sequence list (vector)
# 0 cleanup
sub amb_transcription
{
	my ($ntseq, $CODON_TABLE, $pepseq) = @_;
	my (@SEED, @NEW) = ((), ());
	my $offset = 0;
	if ( !$pepseq )
	{
		while ($offset < length($ntseq))
		{
			my $template = substr($ntseq, $offset, 3);
			my $regtemp = regres($template);
			if ($template !~ $ambnt)
			{
				@SEED = ( $template ) if ($offset == 0);
				@NEW  = ( $template ) if ($offset >  0);
			}
			else
			{
				@SEED = grep { $_ =~ $regtemp } keys %$CODON_TABLE if ($offset == 0);
				@NEW  = grep { $_ =~ $regtemp } keys %$CODON_TABLE if ($offset >  0);
			}
			unless ($offset == 0) 
			{
				@SEED = combine(\@SEED, \@NEW);
			}
			$offset += 3;
		}
	}
	else
	{
		my $REV_CODON = define_reverse_codon_table($CODON_TABLE);
		my @each = split("", $pepseq);
		my $regnt = regres($ntseq, 1);
		while ($offset < scalar(@each))
		{
			@SEED = @{$$REV_CODON{$each[$offset]}} if ($offset == 0);
			@NEW  = @{$$REV_CODON{$each[$offset]}} if ($offset >  0);
			unless ($offset == 0) 
			{
				@SEED = combine(\@SEED, \@NEW);
			}
			$offset++;
		}
		@SEED =  grep { $_ =~ $regnt } @SEED;
	}
	return uniq @SEED;
#	return grep {translate($_, 1, $hashref) eq $pepseq} keys %SEED_TOTAL if ($pepseq);
}

#### combine ####
# meant to work with the amb_trans* functions.  Basically builds a list of tree nodes.
# in: 2 x peptide lists (array reference)
# out: combined list of peptides (vector)
sub combine
{
	my ($arr1ref, $arr2ref) = @_;
	my @arr3 = ();
	foreach my $do (@$arr1ref)
	{
		push @arr3, $do . $_ foreach (@$arr2ref)
	}
	return @arr3;
}

#### cleanup ####
# takes a sequence and attempts to remove extraneous information.
# in: nucleotide sequence (string), switch for sequence type (0 strict nt, 1 degenerate nt, or 2 aa)
# out: nucleotide sequence  (string)
sub cleanup
{
	my ($sequence, $swit) = @_;
	$swit = 0 if (!$swit);
	$sequence =~ s/$fastaline//;						#remove FASTA info line
	$sequence = uc $sequence;							#capitalize everything
	$sequence =~ s/$nonawords//g	if ($swit == 2);	#remove every nonword except *
	$sequence =~ s/$nonwords//g		if ($swit != 2);	#remove every nonword
	if ($swit < 2)	{	$sequence =~ s/$_//g foreach ( qw(E F I J L O P Q U X Z) );	}	#strict nucleotide editing
	if ($swit == 0)	{	$sequence =~ s/$_//g foreach (	@NTSG					 );	}	#degenerate nucleotide editing
	if ($swit == 2)	{	$sequence =~ s/$_//g foreach ( qw(B J O U X Z)			 );	}	#amino acid editing
	return $sequence;
}

#### randDNA ####
# takes a target length and an AT percentage and generates a random nucleotide sequence, with or without stops in the first frame
# in: nucleotide sequence length (scalar), AT percentage (0 ² scalar ² 100), stop codon prevention(0 stops, 1 no stops), codon table (hash reference)
# out: nucleotide sequence (string)
# 0 cleanup
sub randDNA
{
	my ($length, $ATperc, $stopswit, $CODON_TABLE) = @_;
	my $ATtotal = int( ( $ATperc * $length / 100 )  + .5) ;
	my $Acount  = int( rand( $ATtotal ) + .5 );
	my $Tcount  = $ATtotal - $Acount;
	my $GCtotal = $length - $ATtotal;
	my $Gcount  = int( rand( $GCtotal ) + .5 );
	my $Ccount  = $GCtotal - $Gcount;	
	my @randomarray = shuffle( split( '', ('A' x $Acount) . ('T' x $Tcount) . ('C' x $Ccount) . ('G' x $Gcount) ) );
	if ($stopswit == 2)
	{
		my $randDNA = join('', @randomarray);
		foreach (pattern_finder($randDNA, "*", 2, 1, $CODON_TABLE))
		{
			substr($randDNA, (($_+1)*3) - 3, 3) = scalar reverse(substr($randDNA, (($_+1)*3) - 3, 3));
			substr($randDNA, (($_+1)*3) - 2, 2) = scalar reverse(substr($randDNA, (($_+1)*3) - 2, 2)) if (int(rand(1)+.5) == 1);
		}
		return $randDNA;
	}
	else
	{
		return join("", @randomarray);
	}
}

#### pattern_finder ####
sub pattern_finder
{
	my ($strand, $pattern, $swit, $frame, $CODON_TABLE) = @_;
	my @positions = ();
	if ($swit == 2)
	{
		return if (! $frame || ! $CODON_TABLE);
		$strand = translate($strand, $frame, $CODON_TABLE)
	}
	my $exp = regres($pattern, $swit);
	while ($strand =~ /(?=$exp)/ig)
	{
		push @positions, (pos $strand);
	}
	return @positions;
}

#### pattern_remover ####
# takes a nucleotide sequence, a nucleotide "pattern" to be removed, and a few codon tables, and returns an edited nucleotide sequence that is missing the pattern (if possible).
# in: nucleotide sequence (string), nucleotide pattern (string), codon table (hash reference), RSCU value table (hash reference)
# out: nucleotide sequence (string) OR null
# 0 cleanup
sub pattern_remover
{
	my ($critseg, $pattern, $CODON_TABLE, $RSCU_VALUES) = @_;
	my $REV_CODON_TABLE = define_reverse_codon_table($CODON_TABLE); 
	my @wholecodonarr;
	my @rankings;
	my ($tcv, $tcv2, $sflag) = (0, 0, 0);
	my $copy;
	for (my $offset = 0; $offset < (length($critseg)); $offset+=3)	# for each codon position, get array of synonymous codons
	{
		push @wholecodonarr, $$REV_CODON_TABLE{$$CODON_TABLE{substr($critseg, $offset, 3)}};
	}
	foreach my $itc (@wholecodonarr) # create rankings array of RSCU differences for each possible single codon change
	{
		foreach my $itc2 (@$itc)
		{
			push @rankings, abs($$RSCU_VALUES{$itc2} - $$RSCU_VALUES{substr($critseg, $tcv, 3)}) . " $tcv2 $itc2\n" if (substr($critseg, $tcv, 3) ne $itc2);	
		}
		$tcv += 3;
		$tcv2++;
	}
	foreach my $itp (@rankings)
	{
		my ($RSCU, $codonpos, $codonreplace) = ($1, $2, $3) if ($itp =~ /([0-9\.]+) ([0-9]+) ([GCTA]+)/);
		$copy = $critseg;
		substr($copy, $codonpos * 3, 3) = $codonreplace;
		next if ($copy =~ regres($pattern));
		if ($copy !~ regres($pattern) && complement($copy, 1) !~ regres($pattern)) {	$sflag = 1; last;	}
	}
	return $sflag == 1	?	$copy	:	0;
}


#### pattern_adder ####
# takes a nucleotide sequence, a nucleotide "pattern" to be interpolated, and the codon table, and returns 
#  an edited nucleotide sequence that contains the pattern (if possible).
# in: nucleotide sequence (string), nucleotide pattern (string), codon table (hash reference), 
#  RSCU value table (hash reference)
# out: nucleotide sequence (string) OR null
# 0 cleanup
sub pattern_adder	#assume that critseg and pattern come in as complete codons  (ran through pattern_aligner)
{
	my ($oldpatt, $newpatt, $CODON_TABLE) = @_;
	my $REV_CODON_TABLE = define_reverse_codon_table($CODON_TABLE);
	my ($offset, $copy) = (0, "");
	while ($offset < length($oldpatt))
	{
		my $curcod = substr($oldpatt, $offset, 3);
		my $curtar = substr($newpatt, $offset, 3);
		foreach my $g (degcodon_to_aas($curcod, $CODON_TABLE))
		{
			$copy .= $curcod =~ regres($curtar)	
				   ? $curcod
				   : first { compareseqs($curtar, $_) } @{$$REV_CODON_TABLE{$g}};
		}
		$offset +=3;
	}
	return length($copy) == length($oldpatt)	?	$copy	:	0;
}

#### pattern_aligner ####
# takes a nucleotide sequence, a pattern, a peptide sequence, and a codon table and inserts Ns before the pattern until they align properly.  
#  This is so a pattern can be inserted out of frame.
# in: nucleotide sequence (string), nucleotide pattern (string), amino acid sequence (string), codon table (hash reference)
# out: nucleotide pattern (string)
# 0 cleanup
sub pattern_aligner
{
	my ($critseg, $pattern, $peptide, $CODON_TABLE, $swit) = @_;
	$swit = 0 if (!$swit);
	my ($newpatt, $nstring, $rounds, $check) = ("", "N" x 2, 0, "");
	while ($rounds <= (length($critseg) - length($pattern))*2 + 1 && $check ne $peptide)
	{
		$newpatt = $rounds <= (length($critseg) - length($pattern))	
			?	substr($nstring, 0, $rounds) . $pattern	
			:	substr($nstring, 0, ($rounds-3)) . complement($pattern, 1);
		$newpatt .=  "N" while (length($newpatt) != length($critseg));
		my ($noff, $poff) = (0, 0);
		$check = "";
		while ($poff < (int(length($newpatt) / 3)))
		{
			$check .= $_ foreach( grep { substr($peptide, $poff, 1) eq $_ }
					 degcodon_to_aas( substr($newpatt, $noff, 3), $CODON_TABLE ));
			$noff += 3;
			$poff ++;
		}
		$rounds++;
	}
	$newpatt = "0" if ($check ne $peptide);
	return $swit == 1	?	($newpatt, $rounds-1)	:	$newpatt;
}

#### compare_sequences ####
# takes two nucleotide sequences that are assumed to be perfectly aligned and roughly equivalent and returns similarity metrics.
# in: 2x nucleotide sequence (string)
# out: similarity metrics (hash)
# 0 cleanup
# another one that should be twwweeeaaakkkeeeddd
sub compare_sequences
{
	my ($topseq, $botseq) = @_;
	return if (!$botseq || length($botseq) != length($topseq));
	my ($tsit, $tver, $len) = (0, 0, length($topseq));
	my $alresults;
	while (length($topseq) > 0)
	{
		my ($topbit, $botbit) = (chop($topseq), chop ($botseq));
		if ($topbit ne $botbit)
		{
			$topbit = $topbit =~ $NTIDES{R}	?	1	:	0;
			$botbit = $botbit =~ $NTIDES{R}	?	1	:	0;
			$tsit++ if ($topbit == $botbit);
			$tver++ if ($topbit != $botbit);
		}
	}
	$$alresults{'D'} = $tsit + $tver;										#changes
	$$alresults{'I'} = $len - $$alresults{'D'};								#identities
	$$alresults{'T'} = $tsit;												#transitions
	$$alresults{'V'} = $tver;												#transversions
	$$alresults{'P'} = int((100 - (($$alresults{'D'} / $len) * 100)) + .5);	#percent identity
	return $alresults;
}

#### cons_seq ####
sub cons_seq
{
	my ($arrref) = @_;
	my $cons = '';
	for my $x (0..length($$arrref[0]))
	{
		my $flag = 0;
		my $init = substr($$arrref[0], $x, 1);
		for my $y (1..scalar(@$arrref)-1)
		{
			$flag++ if ($init ne substr($$arrref[$y], $x, 1));
		}
		$cons .=  $flag == 0	?	substr($$arrref[0], $x, 1)	:	'_';
	}
	return $cons;
}

#### sitver ####
sub sitver
{
	my ($base, $swit) = @_;
	$swit = 0 if (!$swit);
	if ($swit == 1) #return set of transversions
	{
		return $base =~ $NTIDES{Y}	?	$NTIDES{R}	:	$NTIDES{Y};
	}
	else			#return set of transitions
	{
		return $base =~ $NTIDES{Y}	?	$NTIDES{Y}	:	$NTIDES{R};
	}
}

#### change_codons ####
# takes a nucleotide sequence and a few codon tables and tries to recode the nucleotide sequence to one of four algorithms, provided as a trailing switch.
# in: nucleotide sequence (string), codon table (hash reference), reverse codon table (hash reference), 
#     RSCU value table (hash reference), algorithm number (0 random, 1 most optimal, 2 next most optimal, 3 most different, 4 least different)
# out: nucleotide sequence (string)
# 0 cleanup
sub change_codons
{
	my ($oldseq, $CODON_TABLE, $RSCU_VALUES, $swit) = @_;
	my $REV_CODON_TABLE = define_reverse_codon_table($CODON_TABLE);	
	my ($offset, $newcod, $curcod, $newseq, $aa) = (0, undef, undef, undef, undef);
	while ($offset < length($oldseq))
	{
		$curcod = substr($oldseq, $offset, 3);
		$newcod = $curcod;
		$aa = translate($curcod, 1, $CODON_TABLE);
		my @posarr = sort { $$RSCU_VALUES{$b} <=> $$RSCU_VALUES{$a} } @{$$REV_CODON_TABLE{$aa}};
		if (scalar(@posarr) != 1 && $aa ne '*')
		{	
			if    ($swit == 0)	#Random
			{
				$newcod = first { $_ ne $curcod } shuffle @posarr;
			}
			elsif ($swit == 1)	#Optimal
			{
				$newcod = first {		1		} @posarr;
			}
			elsif ($swit == 2)	#Less Optimal
			{
				$newcod = first { $_ ne $curcod } @posarr;
			}
			elsif ($swit == 3)	#Most Different
			{
				my $lastbase = substr $curcod, 2, 1;	
				my $frstbase = substr $curcod, 0, 1;
				if	(scalar(@posarr) == 2)		
				{	
					$newcod = first { $_ ne $curcod } @posarr;	
				}
				elsif	(scalar(@posarr) == 4 || scalar(@posarr) == 3)
				{
					$newcod = first { (substr $_, 2, 1) =~ sitver($lastbase, 1) } @posarr;	
				}
				elsif	(scalar(@posarr) == 6)
				{	
					$newcod = first { ((substr $_, 2) !~ sitver($lastbase, 0) ) && ((substr $_, 0, 1) ne $frstbase)} @posarr;
					if (!$newcod)
					{
						$newcod = first { ((substr $_, 2) ne $lastbase ) && ((substr $_, 0, 1) ne $frstbase)} @posarr;
					}
				}
			}
			elsif ($swit == 4)	#Least Different
			{
				my @sorarr = sort {abs($$RSCU_VALUES{$a} - $$RSCU_VALUES{$curcod}) <=> abs($$RSCU_VALUES{$b} - $$RSCU_VALUES{$curcod})} @posarr;
				$newcod = first { $_ ne $curcod } @sorarr;
				$newcod = $curcod if (abs($$RSCU_VALUES{$newcod} - $$RSCU_VALUES{$curcod}) > 1);
			}
		}
		$newseq .= $newcod;
		$offset += 3;
	}
	return $newseq;
}

#### fasta_parser ####
#
#
#
sub fasta_parser
{
	my ($instr) = @_;
	my $seqhsh = {};
	my @pre = split(">", $instr);
	shift @pre;
	foreach my $preseq (@pre)
	{
		my @pair = split(/[\n\r]/g, $preseq);
		my $id = shift @pair;
		$$seqhsh{">" . $id} = join("", @pair);
	}
	return $seqhsh;
}

#### rscu_parser ####
# takes the form AAA (K) 0.540
#
#
sub rscu_parser
{
	my ($instr) = @_;
	my $rscuhsh = {};
	foreach my $pre (split(/[\n\r]/g, $instr))
	{
		my @trip = split(/ /g, $pre);
		my $id = $trip[0];
		my $val = $trip[2];
		$$rscuhsh{$id} = $val;
	}
	return $rscuhsh;
}

#### print_alignment ####
#
# $swit = 1 for html, 0 for text
#
sub print_alignment
{
	my ($nuchshref, $width, $swit, $aaseq) = @_;
	my ($space, $break, $times) = $swit == 0	?	(" ", "\n", "x")	:	("&nbsp;", "<br>", "&times;");
	my $start = 0;
	my $output = $break;
	while ($start < length($$nuchshref{first {1} keys %$nuchshref}))
	{
		my $count = 0;
		my $iter = 1;
		if ($aaseq)
		{
			my $rt;
			$output.= $break . "0 tran" . $space;
			for ($rt = ($start / 3); $rt < ($start / 3) + ($width / 3); $rt++)
			{
				$output .= substr($aaseq, $rt, 1) . $space x 2 if ($rt < length($aaseq));
				$output .= $space x 3 if ($rt >= length($aaseq));
			}
			$output .= $space . $rt;
		}
		foreach (sort keys %$nuchshref)
		{
			$output .= $break . $_ . $space . substr($$nuchshref{$_}, $start, $width);
			$output .= $space . ($start+$width)*$iter if ($count == 0 && ($start+$width)*$iter < length($$nuchshref{$_}));
			$output .= ($space x (($start+$width)*$iter - length($$nuchshref{$_})+1)) . ($start+$width)*$iter if ($count == 0 && ($start+$width)*$iter >= length($$nuchshref{$_}));
			$count++;
		}
		$iter++;
		$output .= $break . $space x 5 . (($space x 9 . $times) x ($width / 10));
		$output .= $break x 2;
		$start += $width;
	}
	return $output;
}


#### define_codon_table ####
# Generates a hash.  KEYS: codons (string)  VALUES: amino acids (string)
# in: switch for codon table (1)
# out: codon table (hash)
sub define_codon_table
{
	my ($swit) = @_;
	return if (!$swit);
	my $CODON_TABLE = {};
	if ($swit == 1)
	{
		$$CODON_TABLE{"TTT"} = "F";	$$CODON_TABLE{"TTC"} = "F";	$$CODON_TABLE{"TTA"} = "L";	$$CODON_TABLE{"TTG"} = "L";	
		$$CODON_TABLE{"CTT"} = "L";	$$CODON_TABLE{"CTC"} = "L";	$$CODON_TABLE{"CTA"} = "L";	$$CODON_TABLE{"CTG"} = "L";
		$$CODON_TABLE{"ATT"} = "I";	$$CODON_TABLE{"ATC"} = "I";	$$CODON_TABLE{"ATA"} = "I";	$$CODON_TABLE{"ATG"} = "M";	
		$$CODON_TABLE{"GTT"} = "V";	$$CODON_TABLE{"GTC"} = "V";	$$CODON_TABLE{"GTA"} = "V";	$$CODON_TABLE{"GTG"} = "V";	
		$$CODON_TABLE{"TCT"} = "S";	$$CODON_TABLE{"TCC"} = "S";	$$CODON_TABLE{"TCA"} = "S";	$$CODON_TABLE{"TCG"} = "S";	
		$$CODON_TABLE{"CCT"} = "P";	$$CODON_TABLE{"CCC"} = "P";	$$CODON_TABLE{"CCA"} = "P";	$$CODON_TABLE{"CCG"} = "P";
		$$CODON_TABLE{"ACT"} = "T";	$$CODON_TABLE{"ACC"} = "T";	$$CODON_TABLE{"ACA"} = "T";	$$CODON_TABLE{"ACG"} = "T";	
		$$CODON_TABLE{"GCT"} = "A";	$$CODON_TABLE{"GCC"} = "A";	$$CODON_TABLE{"GCA"} = "A";	$$CODON_TABLE{"GCG"} = "A";	
		$$CODON_TABLE{"TAT"} = "Y";	$$CODON_TABLE{"TAC"} = "Y";	$$CODON_TABLE{"TAA"} = "*";	$$CODON_TABLE{"TAG"} = "*";	
		$$CODON_TABLE{"CAT"} = "H";	$$CODON_TABLE{"CAC"} = "H";	$$CODON_TABLE{"CAA"} = "Q";	$$CODON_TABLE{"CAG"} = "Q";
		$$CODON_TABLE{"AAT"} = "N";	$$CODON_TABLE{"AAC"} = "N";	$$CODON_TABLE{"AAA"} = "K";	$$CODON_TABLE{"AAG"} = "K";	
		$$CODON_TABLE{"GAT"} = "D";	$$CODON_TABLE{"GAC"} = "D";	$$CODON_TABLE{"GAA"} = "E";	$$CODON_TABLE{"GAG"} = "E";	
		$$CODON_TABLE{"TGT"} = "C";	$$CODON_TABLE{"TGC"} = "C";	$$CODON_TABLE{"TGA"} = "*";	$$CODON_TABLE{"TGG"} = "W";	
		$$CODON_TABLE{"CGT"} = "R";	$$CODON_TABLE{"CGC"} = "R";	$$CODON_TABLE{"CGA"} = "R";	$$CODON_TABLE{"CGG"} = "R";	
		$$CODON_TABLE{"AGT"} = "S";	$$CODON_TABLE{"AGC"} = "S";	$$CODON_TABLE{"AGA"} = "R";	$$CODON_TABLE{"AGG"} = "R";	
		$$CODON_TABLE{"GGT"} = "G";	$$CODON_TABLE{"GGC"} = "G";	$$CODON_TABLE{"GGA"} = "G";	$$CODON_TABLE{"GGG"} = "G";
	}
	return $CODON_TABLE;
}

#### define_reverse_codon_table ####
# Generates a reference to a hash.  KEYS: amino acids (string)  VALUES: codon list (array reference)
# in: codon table (hash reference)
# out: reverse codon table (hash)
sub define_reverse_codon_table
{
	my ($CODON_TABLE) = @_;
	my $REV_CODON_TABLE = {};
	foreach my $codon (keys %$CODON_TABLE)
	{
		my $aa = $$CODON_TABLE{$codon};
		$$REV_CODON_TABLE{$aa} = [] if ( ! exists $$REV_CODON_TABLE{$aa} );
		push @{$$REV_CODON_TABLE{$aa}}, $codon;
	}
	return $REV_CODON_TABLE;
}

#### define_RSCU_values ####
# Generates a hash.  KEYS: codons (string)  VALUES: RSCU value (float)
# in: switch for reverse codon table (1 s.cer, 2 e.col, 3 h.sap, 4 c.ele, 5 d.mel)
# out: RSCU value table (hash)
sub define_RSCU_values
{
	my ($swit) = @_;
	return if (!$swit);
	my %RSCU_TABLE;
	if ($swit == 1)		#Saccharomyces cerevisiae
	{
		$RSCU_TABLE{"TTT"} = 0.19;	$RSCU_TABLE{"TTC"} = 1.81;	$RSCU_TABLE{"TTA"} = 0.49;	$RSCU_TABLE{"TTG"} = 5.34;	
		$RSCU_TABLE{"CTT"} = 0.02;	$RSCU_TABLE{"CTC"} = 0.00;	$RSCU_TABLE{"CTA"} = 0.15;	$RSCU_TABLE{"CTG"} = 0.02;
		$RSCU_TABLE{"ATT"} = 1.26;	$RSCU_TABLE{"ATC"} = 1.74;	$RSCU_TABLE{"ATA"} = 0.00;	$RSCU_TABLE{"ATG"} = 1.00;	
		$RSCU_TABLE{"GTT"} = 2.07;	$RSCU_TABLE{"GTC"} = 1.91;	$RSCU_TABLE{"GTA"} = 0.00;	$RSCU_TABLE{"GTG"} = 0.02;	
		$RSCU_TABLE{"TCT"} = 3.26;	$RSCU_TABLE{"TCC"} = 2.42;	$RSCU_TABLE{"TCA"} = 0.08;	$RSCU_TABLE{"TCG"} = 0.02;	
		$RSCU_TABLE{"CCT"} = 0.21;	$RSCU_TABLE{"CCC"} = 0.02;	$RSCU_TABLE{"CCA"} = 3.77;	$RSCU_TABLE{"CCG"} = 0.00;
		$RSCU_TABLE{"ACT"} = 1.83;	$RSCU_TABLE{"ACC"} = 2.15;	$RSCU_TABLE{"ACA"} = 0.00;	$RSCU_TABLE{"ACG"} = 0.01;	
		$RSCU_TABLE{"GCT"} = 3.09;	$RSCU_TABLE{"GCC"} = 0.89;	$RSCU_TABLE{"GCA"} = 0.03;	$RSCU_TABLE{"GCG"} = 0.00;	
		$RSCU_TABLE{"TAT"} = 0.06;	$RSCU_TABLE{"TAC"} = 1.94;	$RSCU_TABLE{"TAA"} = 1.00;	$RSCU_TABLE{"TAG"} = 0.00;	
		$RSCU_TABLE{"CAT"} = 0.32;	$RSCU_TABLE{"CAC"} = 1.68;	$RSCU_TABLE{"CAA"} = 1.98;	$RSCU_TABLE{"CAG"} = 0.02;
		$RSCU_TABLE{"AAT"} = 0.06;	$RSCU_TABLE{"AAC"} = 1.94;	$RSCU_TABLE{"AAA"} = 0.16;	$RSCU_TABLE{"AAG"} = 1.84;	
		$RSCU_TABLE{"GAT"} = 0.70;	$RSCU_TABLE{"GAC"} = 1.30;	$RSCU_TABLE{"GAA"} = 1.98;	$RSCU_TABLE{"GAG"} = 0.02;	
		$RSCU_TABLE{"TGT"} = 1.80;	$RSCU_TABLE{"TGC"} = 0.20;	$RSCU_TABLE{"TGA"} = 0.00;	$RSCU_TABLE{"TGG"} = 1.00;	
		$RSCU_TABLE{"CGT"} = 0.63;	$RSCU_TABLE{"CGC"} = 0.00;	$RSCU_TABLE{"CGA"} = 0.00;	$RSCU_TABLE{"CGG"} = 0.00;	
		$RSCU_TABLE{"AGT"} = 0.06;	$RSCU_TABLE{"AGC"} = 0.16;	$RSCU_TABLE{"AGA"} = 5.37;	$RSCU_TABLE{"AGG"} = 0.00;	
		$RSCU_TABLE{"GGT"} = 3.92;	$RSCU_TABLE{"GGC"} = 0.06;	$RSCU_TABLE{"GGA"} = 0.00;	$RSCU_TABLE{"GGG"} = 0.02;
	}
	elsif ($swit == 2)	#Escherichia coli
	{
		$RSCU_TABLE{"TTT"} = 0.34;	$RSCU_TABLE{"TTC"} = 1.66;	$RSCU_TABLE{"TTA"} = 0.06;	$RSCU_TABLE{"TTG"} = 0.07;	
		$RSCU_TABLE{"CTT"} = 0.13;	$RSCU_TABLE{"CTC"} = 0.17;	$RSCU_TABLE{"CTA"} = 0.04;	$RSCU_TABLE{"CTG"} = 5.54;
		$RSCU_TABLE{"ATT"} = 0.48;	$RSCU_TABLE{"ATC"} = 2.51;	$RSCU_TABLE{"ATA"} = 0.01;	$RSCU_TABLE{"ATG"} = 1.00;	
		$RSCU_TABLE{"GTT"} = 2.41;	$RSCU_TABLE{"GTC"} = 0.08;	$RSCU_TABLE{"GTA"} = 1.12;	$RSCU_TABLE{"GTG"} = 0.40;	
		$RSCU_TABLE{"TCT"} = 2.81;	$RSCU_TABLE{"TCC"} = 2.07;	$RSCU_TABLE{"TCA"} = 0.06;	$RSCU_TABLE{"TCG"} = 0.00;	
		$RSCU_TABLE{"CCT"} = 0.15;	$RSCU_TABLE{"CCC"} = 0.02;	$RSCU_TABLE{"CCA"} = 0.42;	$RSCU_TABLE{"CCG"} = 3.41;
		$RSCU_TABLE{"ACT"} = 1.87;	$RSCU_TABLE{"ACC"} = 1.91;	$RSCU_TABLE{"ACA"} = 0.10;	$RSCU_TABLE{"ACG"} = 0.12;	
		$RSCU_TABLE{"GCT"} = 2.02;	$RSCU_TABLE{"GCC"} = 0.18;	$RSCU_TABLE{"GCA"} = 1.09;	$RSCU_TABLE{"GCG"} = 0.71;	
		$RSCU_TABLE{"TAT"} = 0.38;	$RSCU_TABLE{"TAC"} = 1.63;	$RSCU_TABLE{"TAA"} = 0.00;	$RSCU_TABLE{"TAG"} = 0.00;	
		$RSCU_TABLE{"CAT"} = 0.45;	$RSCU_TABLE{"CAC"} = 1.55;	$RSCU_TABLE{"CAA"} = 0.12;	$RSCU_TABLE{"CAG"} = 1.88;
		$RSCU_TABLE{"AAT"} = 0.02;	$RSCU_TABLE{"AAC"} = 1.98;	$RSCU_TABLE{"AAA"} = 1.63;	$RSCU_TABLE{"AAG"} = 0.37;	
		$RSCU_TABLE{"GAT"} = 0.51;	$RSCU_TABLE{"GAC"} = 1.49;	$RSCU_TABLE{"GAA"} = 1.64;	$RSCU_TABLE{"GAG"} = 0.36;	
		$RSCU_TABLE{"TGT"} = 0.60;	$RSCU_TABLE{"TGC"} = 1.40;	$RSCU_TABLE{"TGA"} = 0.00;	$RSCU_TABLE{"TGG"} = 1.00;	
		$RSCU_TABLE{"CGT"} = 4.47;	$RSCU_TABLE{"CGC"} = 1.53;	$RSCU_TABLE{"CGA"} = 0.00;	$RSCU_TABLE{"CGG"} = 0.00;	
		$RSCU_TABLE{"AGT"} = 0.13;	$RSCU_TABLE{"AGC"} = 0.93;	$RSCU_TABLE{"AGA"} = 0.00;	$RSCU_TABLE{"AGG"} = 0.00;	
		$RSCU_TABLE{"GGT"} = 2.27;	$RSCU_TABLE{"GGC"} = 1.68;	$RSCU_TABLE{"GGA"} = 0.00;	$RSCU_TABLE{"GGG"} = 0.04;
	}
	elsif ($swit == 3)	#H.sapiens
	{
		$RSCU_TABLE{"TTT"} = 0.27;	$RSCU_TABLE{"TTC"} = 1.73;	$RSCU_TABLE{"TTA"} = 0.05;	$RSCU_TABLE{"TTG"} = 0.31;	
		$RSCU_TABLE{"CTT"} = 0.20;	$RSCU_TABLE{"CTC"} = 1.42;	$RSCU_TABLE{"CTA"} = 0.15;	$RSCU_TABLE{"CTG"} = 3.88;
		$RSCU_TABLE{"ATT"} = 0.45;	$RSCU_TABLE{"ATC"} = 2.43;	$RSCU_TABLE{"ATA"} = 0.12;	$RSCU_TABLE{"ATG"} = 1.00;	
		$RSCU_TABLE{"GTT"} = 0.09;	$RSCU_TABLE{"GTC"} = 1.03;	$RSCU_TABLE{"GTA"} = 0.11;	$RSCU_TABLE{"GTG"} = 2.78;	
		$RSCU_TABLE{"TCT"} = 0.45;	$RSCU_TABLE{"TCC"} = 2.09;	$RSCU_TABLE{"TCA"} = 0.26;	$RSCU_TABLE{"TCG"} = 0.68;	
		$RSCU_TABLE{"CCT"} = 0.58;	$RSCU_TABLE{"CCC"} = 2.02;	$RSCU_TABLE{"CCA"} = 0.36;	$RSCU_TABLE{"CCG"} = 1.04;
		$RSCU_TABLE{"ACT"} = 0.36;	$RSCU_TABLE{"ACC"} = 2.37;	$RSCU_TABLE{"ACA"} = 0.36;	$RSCU_TABLE{"ACG"} = 0.92;	
		$RSCU_TABLE{"GCT"} = 0.45;	$RSCU_TABLE{"GCC"} = 2.38;	$RSCU_TABLE{"GCA"} = 0.36;	$RSCU_TABLE{"GCG"} = 0.82;
		$RSCU_TABLE{"TAT"} = 0.34;	$RSCU_TABLE{"TAC"} = 1.66;	$RSCU_TABLE{"TAA"} = 0.00;	$RSCU_TABLE{"TAG"} = 0.00;	
		$RSCU_TABLE{"CAT"} = 0.30;	$RSCU_TABLE{"CAC"} = 1.70;	$RSCU_TABLE{"CAA"} = 0.21;	$RSCU_TABLE{"CAG"} = 1.79;
		$RSCU_TABLE{"AAT"} = 0.33;	$RSCU_TABLE{"AAC"} = 1.67;	$RSCU_TABLE{"AAA"} = 0.34;	$RSCU_TABLE{"AAG"} = 1.66;	
		$RSCU_TABLE{"GAT"} = 0.36;	$RSCU_TABLE{"GAC"} = 1.64;	$RSCU_TABLE{"GAA"} = 0.26;	$RSCU_TABLE{"GAG"} = 1.74;
		$RSCU_TABLE{"TGT"} = 0.42;	$RSCU_TABLE{"TGC"} = 1.58;	$RSCU_TABLE{"TGA"} = 0.00;	$RSCU_TABLE{"TGG"} = 1.00;
		$RSCU_TABLE{"CGT"} = 0.38;	$RSCU_TABLE{"CGC"} = 2.72;	$RSCU_TABLE{"CGA"} = 0.31;	$RSCU_TABLE{"CGG"} = 1.53;	
		$RSCU_TABLE{"AGT"} = 0.31;	$RSCU_TABLE{"AGC"} = 2.22;	$RSCU_TABLE{"AGA"} = 0.22;	$RSCU_TABLE{"AGG"} = 0.84;	
		$RSCU_TABLE{"GGT"} = 0.34;	$RSCU_TABLE{"GGC"} = 2.32;	$RSCU_TABLE{"GGA"} = 0.29;	$RSCU_TABLE{"GGG"} = 1.05;
	}
	elsif ($swit == 4)	#Caenorhabditis elegans
	{
		$RSCU_TABLE{"TTT"} = 0.72;	$RSCU_TABLE{"TTC"} = 1.28;	$RSCU_TABLE{"TTA"} = 0.45;	$RSCU_TABLE{"TTG"} = 1.35;	
		$RSCU_TABLE{"CTT"} = 1.86;	$RSCU_TABLE{"CTC"} = 1.38;	$RSCU_TABLE{"CTA"} = 0.34;	$RSCU_TABLE{"CTG"} = 0.63;
		$RSCU_TABLE{"ATT"} = 1.52;	$RSCU_TABLE{"ATC"} = 1.23;	$RSCU_TABLE{"ATA"} = 0.25;	$RSCU_TABLE{"ATG"} = 1.00;	
		$RSCU_TABLE{"GTT"} = 1.67;	$RSCU_TABLE{"GTC"} = 1.11;	$RSCU_TABLE{"GTA"} = 0.52;	$RSCU_TABLE{"GTG"} = 0.70;
		$RSCU_TABLE{"TCT"} = 1.47;	$RSCU_TABLE{"TCC"} = 0.98;	$RSCU_TABLE{"TCA"} = 1.44;	$RSCU_TABLE{"TCG"} = 0.83;	
		$RSCU_TABLE{"CCT"} = 0.52;	$RSCU_TABLE{"CCC"} = 0.23;	$RSCU_TABLE{"CCA"} = 2.75;	$RSCU_TABLE{"CCG"} = 0.51;
		$RSCU_TABLE{"ACT"} = 1.34;	$RSCU_TABLE{"ACC"} = 1.02;	$RSCU_TABLE{"ACA"} = 1.15;	$RSCU_TABLE{"ACG"} = 0.49;	
		$RSCU_TABLE{"GCT"} = 1.64;	$RSCU_TABLE{"GCC"} = 1.06;	$RSCU_TABLE{"GCA"} = 0.99;	$RSCU_TABLE{"GCG"} = 0.31;
		$RSCU_TABLE{"TAT"} = 0.97;	$RSCU_TABLE{"TAC"} = 1.03;	$RSCU_TABLE{"TAA"} = 0.00;	$RSCU_TABLE{"TAG"} = 0.00;	
		$RSCU_TABLE{"CAT"} = 1.13;	$RSCU_TABLE{"CAC"} = 0.87;	$RSCU_TABLE{"CAA"} = 1.39;	$RSCU_TABLE{"CAG"} = 0.61;
		$RSCU_TABLE{"AAT"} = 1.10;	$RSCU_TABLE{"AAC"} = 0.90;	$RSCU_TABLE{"AAA"} = 0.84;	$RSCU_TABLE{"AAG"} = 1.16;	
		$RSCU_TABLE{"GAT"} = 1.36;	$RSCU_TABLE{"GAC"} = 0.64;	$RSCU_TABLE{"GAA"} = 1.15;	$RSCU_TABLE{"GAG"} = 0.85;			
		$RSCU_TABLE{"TGT"} = 1.14;	$RSCU_TABLE{"TGC"} = 0.86;	$RSCU_TABLE{"TGA"} = 0.00;	$RSCU_TABLE{"TGG"} = 1.00;	
		$RSCU_TABLE{"CGT"} = 1.84;	$RSCU_TABLE{"CGC"} = 0.73;	$RSCU_TABLE{"CGA"} = 1.07;	$RSCU_TABLE{"CGG"} = 0.31;	
		$RSCU_TABLE{"AGT"} = 0.76;	$RSCU_TABLE{"AGC"} = 0.52;	$RSCU_TABLE{"AGA"} = 1.79;	$RSCU_TABLE{"AGG"} = 0.26;	
		$RSCU_TABLE{"GGT"} = 0.70;	$RSCU_TABLE{"GGC"} = 0.28;	$RSCU_TABLE{"GGA"} = 2.85;	$RSCU_TABLE{"GGG"} = 0.16;
	}
	elsif ($swit == 5)	#Drosophila melanogaster
	{
		$RSCU_TABLE{"TTT"} = 0.12;	$RSCU_TABLE{"TTC"} = 1.88;	$RSCU_TABLE{"TTA"} = 0.03;	$RSCU_TABLE{"TTG"} = 0.69;	
		$RSCU_TABLE{"CTT"} = 0.25;	$RSCU_TABLE{"CTC"} = 0.72;	$RSCU_TABLE{"CTA"} = 0.06;	$RSCU_TABLE{"CTG"} = 4.25;
		$RSCU_TABLE{"ATT"} = 0.74;	$RSCU_TABLE{"ATC"} = 2.26;	$RSCU_TABLE{"ATA"} = 0.00;	$RSCU_TABLE{"ATG"} = 1.00;	
		$RSCU_TABLE{"GTT"} = 0.56;	$RSCU_TABLE{"GTC"} = 1.59;	$RSCU_TABLE{"GTA"} = 0.06;	$RSCU_TABLE{"GTG"} = 1.79;
		$RSCU_TABLE{"TCT"} = 0.87;	$RSCU_TABLE{"TCC"} = 2.74;	$RSCU_TABLE{"TCA"} = 0.04;	$RSCU_TABLE{"TCG"} = 1.17;	
		$RSCU_TABLE{"CCT"} = 0.42;	$RSCU_TABLE{"CCC"} = 2.73;	$RSCU_TABLE{"CCA"} = 0.62;	$RSCU_TABLE{"CCG"} = 0.23;
		$RSCU_TABLE{"ACT"} = 0.65;	$RSCU_TABLE{"ACC"} = 3.04;	$RSCU_TABLE{"ACA"} = 0.10;	$RSCU_TABLE{"ACG"} = 0.21;	
		$RSCU_TABLE{"GCT"} = 0.95;	$RSCU_TABLE{"GCC"} = 2.82;	$RSCU_TABLE{"GCA"} = 0.09;	$RSCU_TABLE{"GCG"} = 0.14;
		$RSCU_TABLE{"TAT"} = 0.23;	$RSCU_TABLE{"TAC"} = 1.77;	$RSCU_TABLE{"TAA"} = 0.00;	$RSCU_TABLE{"TAG"} = 0.00;	
		$RSCU_TABLE{"CAT"} = 0.29;	$RSCU_TABLE{"CAC"} = 1.71;	$RSCU_TABLE{"CAA"} = 0.03;	$RSCU_TABLE{"CAG"} = 1.97;
		$RSCU_TABLE{"AAT"} = 0.13;	$RSCU_TABLE{"AAC"} = 1.87;	$RSCU_TABLE{"AAA"} = 0.06;	$RSCU_TABLE{"AAG"} = 1.94;	
		$RSCU_TABLE{"GAT"} = 0.90;	$RSCU_TABLE{"GAC"} = 1.10;	$RSCU_TABLE{"GAA"} = 0.19;	$RSCU_TABLE{"GAG"} = 1.81;
		$RSCU_TABLE{"TGT"} = 0.07;	$RSCU_TABLE{"TGC"} = 1.93;	$RSCU_TABLE{"TGA"} = 0.00;	$RSCU_TABLE{"TGG"} = 1.00;	
		$RSCU_TABLE{"CGT"} = 2.65;	$RSCU_TABLE{"CGC"} = 3.07;	$RSCU_TABLE{"CGA"} = 0.07;	$RSCU_TABLE{"CGG"} = 0.00;	
		$RSCU_TABLE{"AGT"} = 0.04;	$RSCU_TABLE{"AGC"} = 1.13;	$RSCU_TABLE{"AGA"} = 0.00;	$RSCU_TABLE{"AGG"} = 0.21;	
		$RSCU_TABLE{"GGT"} = 1.34;	$RSCU_TABLE{"GGC"} = 1.66;	$RSCU_TABLE{"GGA"} = 0.99;	$RSCU_TABLE{"GGG"} = 0.00;
	}
	elsif ($swit == 6)	#Bacillus subtilis
	{
		$RSCU_TABLE{"TTT"} = 0.70;	$RSCU_TABLE{"TTC"} = 1.30;	$RSCU_TABLE{"TTA"} = 2.71;	$RSCU_TABLE{"TTG"} = 0.00;	
		$RSCU_TABLE{"CTT"} = 2.13;	$RSCU_TABLE{"CTC"} = 0.00;	$RSCU_TABLE{"CTA"} = 1.16;	$RSCU_TABLE{"CTG"} = 0.00;
		$RSCU_TABLE{"ATT"} = 0.91;	$RSCU_TABLE{"ATC"} = 1.96;	$RSCU_TABLE{"ATA"} = 0.13;	$RSCU_TABLE{"ATG"} = 1.00;	
		$RSCU_TABLE{"GTT"} = 1.88;	$RSCU_TABLE{"GTC"} = 0.25;	$RSCU_TABLE{"GTA"} = 1.38;	$RSCU_TABLE{"GTG"} = 0.50;
		$RSCU_TABLE{"TCT"} = 3.45;	$RSCU_TABLE{"TCC"} = 0.00;	$RSCU_TABLE{"TCA"} = 1.50;	$RSCU_TABLE{"TCG"} = 0.00;	
		$RSCU_TABLE{"CCT"} = 2.29;	$RSCU_TABLE{"CCC"} = 0.00;	$RSCU_TABLE{"CCA"} = 1.14;	$RSCU_TABLE{"CCG"} = 0.57;
		$RSCU_TABLE{"ACT"} = 2.21;	$RSCU_TABLE{"ACC"} = 0.00;	$RSCU_TABLE{"ACA"} = 1.38;	$RSCU_TABLE{"ACG"} = 0.41;	
		$RSCU_TABLE{"GCT"} = 2.94;	$RSCU_TABLE{"GCC"} = 0.08;	$RSCU_TABLE{"GCA"} = 0.60;	$RSCU_TABLE{"GCG"} = 0.38;
		$RSCU_TABLE{"TAT"} = 0.50;	$RSCU_TABLE{"TAC"} = 1.50;	$RSCU_TABLE{"TAA"} = 0.00;	$RSCU_TABLE{"TAG"} = 0.00;	
		$RSCU_TABLE{"CAT"} = 2.00;	$RSCU_TABLE{"CAC"} = 0.00;	$RSCU_TABLE{"CAA"} = 1.71;	$RSCU_TABLE{"CAG"} = 0.29;
		$RSCU_TABLE{"AAT"} = 0.47;	$RSCU_TABLE{"AAC"} = 1.53;	$RSCU_TABLE{"AAA"} = 1.83;	$RSCU_TABLE{"AAG"} = 0.17;	
		$RSCU_TABLE{"GAT"} = 0.53;	$RSCU_TABLE{"GAC"} = 1.47;	$RSCU_TABLE{"GAA"} = 1.40;	$RSCU_TABLE{"GAG"} = 0.60;
		$RSCU_TABLE{"TGT"} = 0.00;	$RSCU_TABLE{"TGC"} = 2.00;	$RSCU_TABLE{"TGA"} = 0.00;	$RSCU_TABLE{"TGG"} = 1.00;	
		$RSCU_TABLE{"CGT"} = 3.11;	$RSCU_TABLE{"CGC"} = 1.78;	$RSCU_TABLE{"CGA"} = 0.00;	$RSCU_TABLE{"CGG"} = 0.00;	
		$RSCU_TABLE{"AGT"} = 0.45;	$RSCU_TABLE{"AGC"} = 0.60;	$RSCU_TABLE{"AGA"} = 1.11;	$RSCU_TABLE{"AGG"} = 0.00;	
		$RSCU_TABLE{"GGT"} = 1.38;	$RSCU_TABLE{"GGC"} = 0.97;	$RSCU_TABLE{"GGA"} = 1.66;	$RSCU_TABLE{"GGG"} = 0.00;	
	}
	return \%RSCU_TABLE;
}

#### define_codon_percentages ####
# Generates a hash.  KEYS: codons (string)  VALUES: RSCU value over codon family size (float)
# in: codon table (hash reference), RSCU value table (hash reference)
# out: codon percentage table (hash)
sub define_codon_percentages
{
	my ($CODON_TABLE, $RSCU_VALUES) = @_;
	my %AA_cod_count;
	$AA_cod_count{$$CODON_TABLE{$_}}++	foreach keys %$CODON_TABLE;
	my %CODON_PERC_TABLE = map { $_ => $$RSCU_VALUES{$_} / $AA_cod_count{$$CODON_TABLE{$_}} } keys %$CODON_TABLE; 
	return \%CODON_PERC_TABLE;
}

#### index_codon_percentages ####
# Generates two arrays for x and y values of a graph of codon percentage values.
# in: dna sequence (string), window size (integer), codon percentage table (hash reference)
# out: x values (array reference), y values (array reference)
sub index_codon_percentages
{
	my ($ntseq, $window, $cpthashref) = @_;
	my @xvalues; my @yvalues;
	my %CODON_PERCENTAGE_TABLE = %$cpthashref;
	my $index; my $sum;
	for (my $x = int($window *(3/2))-3; $x < (length($ntseq) - 3*(int($window *(3/2))-3)); $x+=3)
	{
		$sum = 0;
		for(my $y = $x; $y < 3*$window + $x; $y += 3)
		{
			$sum += $CODON_PERCENTAGE_TABLE{substr($ntseq, $y, 3)};
	#		$sum += $RSCU_TABLE{substr($nucseq, $y, 3)};
		}
		$sum = $sum / $window;
		$index = ($x / 3) + 1;
		push @xvalues, $index;
		push @yvalues, $sum;
	}
	return (\@xvalues, \@yvalues);
}

#### codon_count ####
# Paul Nunley
# takes a reference to an array of sequences and returns a hash with codons as keys and the number of times the codon occurs as a value.
# in: gene sequence (array reference)
# out: codon count (hash reference)
sub codon_count
{
	my ($arrayref, $CODON_TABLE) = @_;
	my %codoncount = map {$_ => 0} keys %$CODON_TABLE;
	foreach my $seq (@$arrayref)
	{
		my $offset = 0;
		while ( $offset < length($seq) )
		{
			my $codon = substr($seq, $offset, 3);
			if ($codon =~ $strcodon)
			{
				$codoncount{$codon} ++;
			}
			else
			{
				$codoncount{"XXX"} ++;
			}
			$offset += 3;
		}
	}
	return \%codoncount;
}

#### get_rscu ####
# Paul Nunley
# takes a hash reference with keys as codons and values as number of times those codons occur (it helps to use codon_count) and returns a hash with the each codon and its RSCU value
# in: codon count (hash reference), reverse codon table (hash reference)
# out: RSCU values (hash reference)
sub generate_RSCU_values
{
	my ($codon_count, $CODON_TABLE) = @_;
	my $REV_CODON_TABLE = define_reverse_codon_table($CODON_TABLE);
	my $RSCU_hash = {}; 
	foreach (sort keys %$codon_count)
	{
		my $x_j = 0;
		my $x = $$codon_count{$_};
		my $family = $$REV_CODON_TABLE{$$CODON_TABLE{$_}};
		my $family_size = scalar(@$family);
		$x_j += $$codon_count{$_} foreach (grep {exists $$codon_count{$_}} @$family);
		$$RSCU_hash{$_} = sprintf("%.3f",  $x / ($x_j / $family_size) ) ;#+ 0;
	}
	return $RSCU_hash;
}

#### define_aa_defaults ####
# Generates a hash.  KEYS: one letter amino acid code (string)  VALUES: most highly expressed codon for that amino acid (string)
# in: reverse codon table (hash reference), RSCU value table (hash reference)
# out: amino acid default table (hash)
sub define_aa_defaults
{
	my ($CODON_TABLE, $RSCU_VALUES) = @_;
	my $REV_CODON_TABLE = define_reverse_codon_table($CODON_TABLE);
	my %aa_defaults = ();
	foreach my $aa (keys %AACIDS)
	{
		my $myrscu = 0;
		foreach my $codon (@{$$REV_CODON_TABLE{$aa}})	
		{	
			if ($$RSCU_VALUES{$codon} > $myrscu)	
			{
				$aa_defaults{$aa} = $codon;
				$myrscu = $$RSCU_VALUES{$codon};
			}
		}
	}
	return %aa_defaults;
}

#### oligocruncher ####
# takes a nucleotide sequence from a Chunk object and breaks it into oligos.  
#   A hash reference provides all of the options, like target subchunk length, oligo number, oligo length, etc   
# in: Chunk (struct), Options (hash reference)
# out: nothing (modifies Chunk (struct))
# 0 cleanup
sub oligocruncher
{
	my ($tov, $hashref) = @_;
	my ($tar_chn_len, $tar_cur_dif, $cur_oli_num, $cur_oli_lap, $cur_oli_len, $cur_chn_mel, $cur_oli_gap, $avg_chn_mel, $avg_oli_len, $start, $starte, $starto, $avg) = 0;
	my (@Overlaps, @tree, @begs, @ends, @Oligos);
	my %pa = %$hashref;	
	my %Collisions;
	$tar_chn_len = $pa{per_chn_len};	
	$cur_oli_num = $pa{tar_oli_num};	
	$cur_oli_len = $pa{tar_oli_len};
	$cur_oli_gap = $pa{tar_oli_gap};	
	$cur_oli_lap = $pa{tar_oli_lap};	
	$tar_cur_dif = $tov->ChunkLength - $tar_chn_len;
#print "\n<br><br>\nrev 0 ", $tov->ChunkNumber, ", $tar_chn_len bp, dif $tar_cur_dif, num $cur_oli_num, len $cur_oli_len, lap $cur_oli_lap, mel $pa{tar_chn_mel}<br>";
	if (abs($tar_cur_dif) >= ($pa{tar_oli_len}+$pa{tar_oli_gap}))	##-if difference btw perfect and current is bigger than another pair of oligos, increment oli_num
	{
		$cur_oli_num = $pa{tar_oli_num} + (2 * int(($tar_cur_dif / ($pa{tar_oli_len} + $pa{tar_oli_gap})) + .5 ));
		$tar_chn_len = ($cur_oli_num * ($pa{tar_oli_gap} + $pa{tar_oli_lap})) + $pa{tar_oli_lap};
		$tar_cur_dif = $tov->ChunkLength - $tar_chn_len;
	}
	$tov->ShrtOligo(2*$pa{max_oli_len});	$tov->LongOligo(0);	
#print "rev 1 ", $tov->ChunkNumber, ", per $tar_chn_len, dif $tar_cur_dif, num $cur_oli_num, len $cur_oli_len, lap $cur_oli_lap, mel $pa{tar_chn_mel}, tol $pa{chn_mel_tol}, <br>";	
	if ($pa{gapswit} == 1)
	{
		##-if difference can be spread equally across oligos, increase length
		if (abs($tar_cur_dif) >= $cur_oli_num)					
		{
			$cur_oli_len = $pa{tar_oli_len} + int($tar_cur_dif / $cur_oli_num);
			$tar_cur_dif = $tar_cur_dif - ($cur_oli_num * (int($tar_cur_dif / $cur_oli_num)));	
		}
		##-if the length is violating max_len, increase num by 2, decrease len by 10, recalc
		if ( ($cur_oli_len >= $pa{max_oli_len}) || ($cur_oli_len == $pa{max_oli_len} && $tar_cur_dif > 0) )		
		{
			$cur_oli_len = $pa{tar_oli_len}-10; 
			$cur_oli_num += 2; 
			$tar_chn_len = $cur_oli_num*($cur_oli_len - $pa{tar_oli_lap}) + $pa{tar_oli_lap};
			$tar_cur_dif = $tov->ChunkLength - $tar_chn_len;
			if (abs($tar_cur_dif) >= $cur_oli_num)
			{
				$cur_oli_len = $cur_oli_len + int($tar_cur_dif / $cur_oli_num);
				$tar_cur_dif = $tar_cur_dif - ($cur_oli_num * (int($tar_cur_dif / $cur_oli_num)));					
			}
		}			
		if ($cur_oli_len >= $pa{max_oli_len} && $tar_cur_dif > 0)
		{
			print "oh no, after rev1, current target is >= the max! $pa{max_oli_len} --- please tell Sarah the following string.<br> ";
			print "&nbsp;&nbsp;cur_oli_len $cur_oli_len, cur_oli_num $cur_oli_num, tar_cur_dif $tar_cur_dif, tar_chn_len $tar_chn_len, chunk length ", $tov->ChunkLength, "<br><br>";
		}
		my $start = 0;			
		for (my $w = 1; $w <= $cur_oli_num; $w++)					##-difference now be between 0 and abs(oli_num-1) - so in/decrement individual overlap lengths
		{
			my $strlen = $cur_oli_len;
			$strlen++ if ( $w <= abs($tar_cur_dif) && $tar_cur_dif > 0);
			$strlen-- if ( $w <= abs($tar_cur_dif) && $tar_cur_dif < 0);
			push @Overlaps, substr($tov->ChunkSeq, $start + $strlen - $cur_oli_lap, $cur_oli_lap) if ($w != $cur_oli_num);
			$start =  $start + $strlen - $cur_oli_lap;
		}
		@tree = map (melt($_, $pa{melform} , .05, .0000001), @Overlaps);
		foreach (@tree)	{	$avg += $_;	}	$avg = int(($avg / scalar(@tree))+.5);
		$cur_chn_mel = ($avg < ($pa{tar_chn_mel}-10))	?	$pa{tar_chn_mel} - .2*($pa{tar_chn_mel}-$avg) :	$pa{tar_chn_mel};	#Adjust target melting temp for reality.
#print "rev 3 ", $tov->ChunkNumber, ", per $tar_chn_len, dif $tar_cur_dif, num $cur_oli_num, len $cur_oli_len, lap $cur_oli_lap, mel $cur_chn_mel, tol $pa{chn_mel_tol}, <br>";	

		$start = 0;
		@Overlaps = ();
		for (my $w = 1; $w <= $cur_oli_num; $w++)					##-then make oligos, changing overlaps for melting temperature if appropriate
		{
			my $laplen = $cur_oli_lap;
			my $strlen = $cur_oli_len;
			$strlen++ if ( $w <= abs($tar_cur_dif) && $tar_cur_dif > 0);
			$strlen-- if ( $w <= abs($tar_cur_dif) && $tar_cur_dif < 0);
			$laplen-- if ($strlen < $pa{tar_oli_len} && $cur_oli_len < 60);#
			if ($w != $cur_oli_num)
			{
#		print ".rev3. ", $tov->ChunkNumber, ", $w strlen $strlen, laplen $laplen, num $cur_oli_num, len $cur_oli_len, mel $cur_chn_mel, tol $pa{chn_mel_tol}, max $pa{max_oli_len}, <br>";
				while (melt(substr($tov->ChunkSeq, $start + $strlen - $laplen, $laplen), $pa{melform}, .05, .0000001) >= ($cur_chn_mel + $pa{chn_mel_tol}) && $strlen > $cur_oli_len)
				{
#			print "...deccing<br>";
					$laplen--;	$strlen--;
				}
				while (melt(substr($tov->ChunkSeq, $start + $strlen - $laplen, $laplen), $pa{melform}, .05, .0000001) <= ($cur_chn_mel - $pa{chn_mel_tol}) && $strlen < $pa{max_oli_len})
				{
#			print "...inccing<br>";
					$laplen++;	$strlen++;
				}				
				push @Overlaps, substr($tov->ChunkSeq, $start + $strlen - $laplen, $laplen);
#			print "&nbsp;&nbsp;$Overlaps[-1]<Br>";
				$avg_chn_mel += melt(substr($tov->ChunkSeq, $start + $strlen - $laplen, $laplen), $pa{melform}, .05, .0000001);
			}
			push @Oligos, substr($tov->ChunkSeq, $start, $strlen);
			push @begs, $start;
			push @ends, $start + length($Oligos[-1]);
			$tov->ShrtOligo(length($Oligos[-1])) if length($Oligos[-1]) <= $tov->ShrtOligo;
			$tov->LongOligo(length($Oligos[-1])) if length($Oligos[-1]) >= $tov->LongOligo;
			$avg_oli_len += length($Oligos[-1]);
			$start =  $start + $strlen - $laplen;
		}
		for (my $w = 0; $w <= $cur_oli_num - 3; $w++)	{	$Collisions{$w} = $ends[$w] - $begs[$w+2]	if ($ends[$w] > $begs[$w+2]);	}
	}
	elsif ($pa{gapswit} == 0)
	{
		$cur_oli_len = int((2* $tov->ChunkLength) / ((2*$tar_chn_len) / $pa{tar_oli_len}));
		$cur_oli_lap = int($cur_oli_len * .5);
		$tar_cur_dif = $tov->ChunkLength - ($cur_oli_num * $cur_oli_len * .5 + $cur_oli_lap);
	
		$starto = $cur_oli_lap + 1;
		for (my $w = 1; $w <= $cur_oli_num; $w++)					##-difference should now be between 0 and abs(oli_num-1) - so in/decrement individual overlap lengths
		{			
			my $strlen = $cur_oli_len;
			if ( $w <= abs(2 * $tar_cur_dif) && $tar_cur_dif > 0)	{$strlen++;}
			if ( $w <= abs(2 * $tar_cur_dif) && $tar_cur_dif < 0)	{$strlen--;}
			if ($w % 2 == 1)
			{
				push @Oligos, substr($tov->ChunkSeq, $starte, $strlen);
				$starte = $starte + $strlen;
				push @Overlaps, substr($tov->ChunkSeq, $starto, $starte - $starto);
				$avg_chn_mel += melt(substr($tov->ChunkSeq, $starto, $starte - $starto), $pa{melform}, .05, .0000001);
			}
			if ($w % 2 == 0)
			{
				push @Oligos, substr($tov->ChunkSeq, $starto, $strlen);
				$starto = $starto + $strlen;
				push @Overlaps, substr($tov->ChunkSeq, $starte, $starto - $starte);
				$avg_chn_mel += melt(substr($tov->ChunkSeq, $starte, $starto - $starte), $pa{melform}, .05, .0000001);
			}
			$tov->ShrtOligo(length($Oligos[-1])) if length($Oligos[-1]) <= $tov->ShrtOligo;
			$tov->LongOligo(length($Oligos[-1])) if length($Oligos[-1]) >= $tov->LongOligo;
			$avg_oli_len += length($Oligos[-1]);
		}
	}
	$tov->Collisions(\%Collisions);	
	$tov->AvgOlapMelt(int(($avg_chn_mel / scalar(@Overlaps))+.5));
	$tov->AvgOligoLength(int(($avg_oli_len / scalar(@Oligos))+.5));
	$tov->Oligos(\@Oligos);
	$tov->Olaps(\@Overlaps);
	return;
}

sub orf_finder
{
	my ($strand, $hashref) = @_;
	my $answer = [];
	for my $frame (qw(1 2 3 -1 -2 -3))
	{
		my $strandaa = translate($strand, $frame, $hashref);
		my $leng = length($strandaa);
		my $curpos = 0; 
		my $orflength = 0; 
		my $onnaorf = 0; 
		my $orfstart = 0; 
		while ($curpos <= $leng)
		{
			my $aa = substr($strandaa, $curpos, 1);
			if ($aa eq 'M' && $onnaorf eq '0')
			{
				$onnaorf = 1;
				$orfstart = $curpos;
			}
			if ($aa eq '*' || ($curpos == $leng && $onnaorf == 1))
			{
				$onnaorf= 0;
				push @$answer, [$frame, $orfstart, $orflength] if ($orflength >= .1*($leng));
				$orflength = 0;
			}
			$curpos++;
			$orflength++ if ($onnaorf == 1);
		}
	}
	return $answer;
}


sub define_oligos
{
	my ($ollist_ref, $revcompswit) = @_;
	my %OL_DATA;
	( $OL_DATA{REGEX},	$OL_DATA{CLEAN} ) = ( {}, {} );
	foreach my $oligo (@$ollist_ref)
	{
		$OL_DATA{CLEAN}->{$oligo}	= $oligo;		#recognition site
	#regular expression array	
		my @arr = ( $revcompswit == 1 && complement($oligo, 1) ne $oligo)	?	
				  ( regres($oligo, 1), regres(complement($oligo, 1), 1) )	:	
				  ( regres($oligo, 1) );
		$OL_DATA{REGEX}->{$oligo} = \@arr;						
	}
	close IN;
	return \%OL_DATA;
}


##											##
#		Restriction Enzyme Functions		 #
##	                                        ##


#### define_sites ####
# Generates a set of hash references containing information about the restriction enzyme library. All have the enzyme name as a key. 
#  REGEX : ref to array containing regex-ready representations of enzyme recognition site
#  CLEAN : the recognition site as a string
#  TABLE : the recognition site with cleavage annotation
#  SCORE : usually the price
#  TYPE  : whether the enzyme leaves 5', 3', or blunt ends, and whether or not the enzyme leaves a 1bp overhang
#  METHB : which methylation pattern blocks cleavage
#  METHI : which methylation pattern inhibits cleavage
#  STAR  : whether or not the enzyme has star activity
#  TEMP  : optimal operating temperature for cleavage
#  VEND  : which vendors supply the enzyme
# in: enzyme list as a file path
# out: hash of hash references

sub define_sites
{
	my ($file) = @_;
	my @data = split(/\n/, slurp($file));
	my $swit = $data[0] =~ /^name/ ? 1	:	0;
	shift @data if ($swit == 1);
	my %RE_DATA;
	($RE_DATA{REGEX},	$RE_DATA{CLEAN},	$RE_DATA{TABLE},	$RE_DATA{SCORE},	$RE_DATA{TYPE},  
	 $RE_DATA{DAM},		$RE_DATA{DCM},		$RE_DATA{CPG},		$RE_DATA{VEND} ,	$RE_DATA{STAR},	$RE_DATA{TEMP},
	 $RE_DATA{BUF1},	$RE_DATA{BUF2},		$RE_DATA{BUF3} ,	$RE_DATA{BUF4} ,	$RE_DATA{BUFU}, $RE_DATA{INACT}    ) = 
	(	{}, {}, {},		{}, {}, {},			{}, {}, {},			{}, {}, {},			{},	{}, {},		{}, {});
	foreach my $line (@data)
	{
		my ($name, $site, $temp, $inact, $buf1, $buf2, $buf3, $buf4, $bufu, $dam, $dcm, $cpg, $score, $star, $vendor) = split("\t", $line);
		$RE_DATA{TABLE}->{$name}	= $site;		#annotated cleavage site
		$site =~ s/\W*\d*//g;
		$RE_DATA{CLEAN}->{$name}	= $site;		#recognition site
		$RE_DATA{TEMP} ->{$name}	= $temp;		#optimal temperature 
		$RE_DATA{INACT}->{$name}	= $inact;		#inactivation formula 
		$RE_DATA{BUF1} ->{$name}	= $buf1; 
		$RE_DATA{BUF2} ->{$name}	= $buf2; 
		$RE_DATA{BUF3} ->{$name}	= $buf3; 
		$RE_DATA{BUF4} ->{$name}	= $buf4; 
		$RE_DATA{BUFU} ->{$name}	= $bufu;
		$RE_DATA{DAM}  ->{$name}	= $dam; 
		$RE_DATA{DCM}  ->{$name}	= $dcm; 
		$RE_DATA{CPG}  ->{$name}	= $cpg;	
		$RE_DATA{SCORE}->{$name}	= $score;		#price of the enzyme
		$RE_DATA{STAR} ->{$name}	= $star;		#star activity?
		$RE_DATA{VEND} ->{$name}	= $vendor;		#vendors provided by
	#	$RE_DATA{METHB}->{$name}	= $block;		#blocked by methylation?
	#	$RE_DATA{METHI}->{$name}	= $inhibit;		#inhibited by methylation?
		my $sitelen = length($site);
		my ($lef, $rig) = ("", "");
		if ($RE_DATA{TABLE}->{$name} =~ $IIP)
		{
			$lef = length($1); 
			$rig = $sitelen - $lef;
		}
		elsif ($RE_DATA{TABLE}->{$name} =~ $IIP2)
		{
			$lef = 0-$sitelen; 
			$rig = $sitelen;
		}
		elsif ($RE_DATA{TABLE}->{$name} =~ $IIA || $RE_DATA{TABLE}->{$name} =~ $IIA2 || $RE_DATA{TABLE}->{$name} =~ $IIA3)
		{
			$lef = int($1); 
			$rig = int($2);
		}
	#stickiness
		$RE_DATA{TYPE}->{$name} .= ($lef < $rig)	?	"5'"	:	($lef > $rig)	?	"3'"	:	($lef == $rig)	?	"b"	:	"?";
		$RE_DATA{TYPE}->{$name} .= "1" if (abs($lef - $rig) == 1);
	#regular expression array	
		my $arr = ( complement($site, 1) ne $site )						?	
				  [ regres($site, 1), regres(complement($site, 1), 1) ]	:	
				  [ regres($site, 1) ];
		$RE_DATA{REGEX}->{$name} = $arr;						
	}
	return \%RE_DATA;
}

sub report_RE
{
	my ($name, $RE_DATA) = @_;
	my $string = "$name: ", ;
	$string .= $$RE_DATA{TABLE}->{$name} . " (" . $$RE_DATA{CLEAN}->{$name} . 
			"), type = " . $$RE_DATA{TYPE}->{$name} ;
	return $string;
}

#### define_site_status ####  
# Generates a hash describing a restriction count of a nucleotide sequence.
# in: nucleotide sequence as a string and a reference to a hash containing enzyme names as keys and 
#   regular expressions in a reference to an array as values (usually SITE_REGEX from define_sites)
# out: reference to a hash where the keys are enzyme names and the value is a count of their occurence in the nucleotide sequence
sub define_site_status
{
	my($seq, $SITE_REGEX) = @_;
	my $SITE_STATUS = {};
	foreach my $pattern (keys %$SITE_REGEX)
	{ 
		my $count = 0;
		foreach my $sit (@{$$SITE_REGEX{$pattern}})
		{		
			$count++ while ($seq =~ /(?=$sit)/ig);
		}
		$$SITE_STATUS{$pattern} = $count;
	}
	return $SITE_STATUS;	
}

#### siteseeker ####
# Generates a hash describing the positions of a particular enzyme's recognition sites in a nucleotide sequence.
# in: nucleotide sequence as a string, an enzyme recognition site as a string, and a reference to an array containing enzyme regular expressions
#   (usually gotten from SITE_REGEX from define_sites)
# out: reference to a hash where the keys are positions and the value is the recognition site from that position as a string.
sub siteseeker
{
	my ($seq, $pass, $SITE_REGEX_arrref) = @_;
	my $total = {};
	foreach my $sit (@$SITE_REGEX_arrref)
	{
		while ($seq =~ /(?=$sit)/ig)
		{
			$$total{pos $seq} = substr($seq, pos $seq, length($pass));
		}
	}
	return $total;
}

sub first_base
{
	my ($relev, $index, $orient) = @_;
	my $term = (($index -($relev %3))%3);
	if ($orient eq "+")
	{
		return $index - $term;
	}
	else
	{
		return $term != 0	?	$index + (3-$term)	:	$index;
	}
}

sub overhang
{
	my ($dna, $pos, $grabbedseq, $table, $clean, $swit) = @_;
	my ($lef, $rig, $mattersbit, $cutoff) = (0, 0, undef, 0);
	my $orient = $grabbedseq =~ regres($clean)	? "+"	:	"-";
	$swit = 0 if (!$swit);
	if ($table =~ $IIA || $table =~ $IIA2 || $table =~ $IIA3)
	{
		my ($lef, $rig) = ($1, $2);
		($rig, $lef) = ($lef, $rig) if ($rig < $lef);
		$mattersbit = substr($dna, $pos + length($clean) + $lef, $rig - $lef) if ($orient eq "+");
		$mattersbit = substr($dna, $pos - $rig, $rig - $lef) if ($orient eq "-");
		$lef = length($grabbedseq) + $lef if ($lef < 0);
		return $swit != 1	?	$mattersbit	:	[$mattersbit, $lef];
	}
	elsif ($table =~ $IIP || $table =~ $IIP2)
	{
		$cutoff = length($1);
		if ($cutoff > (.5 * length($clean))) { $cutoff = length($clean) - $cutoff;} 
		$mattersbit = substr($grabbedseq, $cutoff, length($grabbedseq)-(2*$cutoff));
		return $swit != 1	?	$mattersbit	:	[$mattersbit, $cutoff];
	}
}

sub filter_sites
{
	my ($pa_ref, $RE_DATA, $list_ref) = @_;
	my %pa = %$pa_ref;
	my @cutters = $list_ref	?	@{$list_ref} : keys %{$$RE_DATA{CLEAN}};
	
	if ( $pa{check_stickiness} )
	{
		my %temp;
		my $regres = "[" . join("", split(" ", $pa{stickiness})) . "]";
		@cutters = grep {$$RE_DATA{TYPE}->{$_} =~ $regres} @cutters;
	}
	if ( $pa{check_cleavage_site} )
	{
		@cutters = grep { ($pa{cleavage_site} =~ /P/ && ($$RE_DATA{TABLE}->{$_} =~ $IIP || $$RE_DATA{TABLE}->{$_} =~ $IIP2))
						||($pa{cleavage_site} =~ /A/ && ($$RE_DATA{TABLE}->{$_} =~ $IIA || $$RE_DATA{TABLE}->{$_} =~ $IIA2 || $$RE_DATA{TABLE}->{$_} =~ $IIA3)) }	@cutters;
	}
	if ( $pa{check_overhang} )
	{
		my %temp = map {$_ => 0} grep {$$RE_DATA{TYPE}->{$_} !~ /[1b]/} @cutters;
		foreach (keys %temp)
		{
			if ($$RE_DATA{TABLE}->{$_} =~ $IIP || $$RE_DATA{TABLE}->{$_} =~ $IIP2)
			{
				my $cutoff = length($1);
				my $clean = $$RE_DATA{CLEAN}->{$_};
				$cutoff = length($clean) - $cutoff if ($cutoff > (.5 * length($clean))); 
				my $mattersbit = substr($clean, $cutoff, length($clean)-(2*$cutoff));
				if ($mattersbit =~ $ambnt && length($mattersbit) % 2 == 0)
				{
					$temp{$_}++ if ($pa{overhang} =~ 'A');
				}
				else
				{
					$temp{$_}++ if (($mattersbit eq complement($mattersbit, 1) && length($mattersbit) % 2 == 0) && $pa{overhang} =~ 'P');
					$temp{$_}++ if (($mattersbit ne complement($mattersbit, 1) || length($mattersbit) % 2 == 1) && $pa{overhang} =~ 'N');
				}
			}
			$temp{$_}++ if (($$RE_DATA{TABLE}->{$_} =~ $IIA || $$RE_DATA{TABLE}->{$_} =~ $IIA2 || $$RE_DATA{TABLE}->{$_} =~ $IIA3) && $pa{overhang} =~ 'A');
		}
		@cutters = grep {$temp{$_} != 0} keys %temp;
	}
	if ( $pa{check_ambiguity} )
	{
		@cutters = grep {  ($pa{ambiguity} =~ /1/ && $$RE_DATA{CLEAN}->{$_} !~ /N/)
						|| ($pa{ambiguity} =~ /2/ && $$RE_DATA{CLEAN}->{$_} !~ $ambnt) } @cutters;
	}
	if ( $pa{check_buffers})
	{
		if ($pa{buffer_bool} eq "OR")
		{
			my %temp;
			foreach my $b (split(" ", $pa{buffers}))
			{
				$temp{$_}++ foreach( grep { $$RE_DATA{"BUF".$b}->{$_} >= $pa{buffer_activity} } @cutters);
			}
			@cutters = keys %temp;
		}
		else
		{
			foreach my $b (split(" ", $pa{buffers}))
			{
				@cutters = grep { $$RE_DATA{"BUF".$b}->{$_} >= $pa{buffer_activity} } @cutters;
			}
		}
	}
	if ( $pa{check_heat})
	{
		my %temp;
		foreach my $h (split(" ", $pa{heat}))
		{
			$temp{$_}++ foreach( grep {$$RE_DATA{INACT}->{$_} =~ /\@$h/} @cutters);
		}
		@cutters = keys %temp;
	}
	if ( $pa{check_temperature})
	{
		my %temp;
		foreach my $t (split(" ", $pa{temperature}))
		{
			$temp{$_}++ foreach( grep {$$RE_DATA{TEMP}->{$_} == $t} @cutters);
		}
		@cutters = keys %temp;
	}
	if ( $pa{check_star} )
	{
		@cutters = grep {  ($pa{check_star} =~ /1/ && $$RE_DATA{STAR}->{$_} eq "y")
						|| ($pa{check_star} =~ /2/ && !$$RE_DATA{STAR}->{$_}) } @cutters;
	}
	if ( $pa{check_price} )
	{
		@cutters = grep { $$RE_DATA{SCORE}->{$_} >= $pa{low_price} && $$RE_DATA{SCORE}->{$_} <= $pa{high_price} } @cutters;
	}
	if ( $pa{check_site_length} )
	{
		my %lenged;
		foreach my $len ( split " ", $pa{site_length} )
		{
			if ($len ne 'b')
			{
				$lenged{$_}++ foreach ( grep {length($$RE_DATA{CLEAN}->{$_}) == $len} @cutters);
			}
			else
			{
				$lenged{$_}++ foreach ( grep {length($$RE_DATA{CLEAN}->{$_}) > 8} @cutters);
			}
		}
		@cutters = keys %lenged;
	}
	if ( $pa{check_meth_status} )
	{
		if ($pa{check_meth_status} == 1)
		{
			my %methed;
			$methed{$_}++ foreach ( grep { ! $$RE_DATA{DAM}->{$_} &&  ! $$RE_DATA{CPG}->{$_}  && ! $$RE_DATA{DCM}->{$_} } @cutters);
			@cutters = keys %methed;
		}
		elsif ($pa{check_meth_status} == 2)
		{
			if ($pa{meth_bool} eq "OR")
			{
				my %temp;
				foreach my $methstat (split " ", $pa{meth_status})
				{
					my ($type, $way) = ($1, uc $2) if ($methstat =~ /(\w)\.(\w+)/);
					$temp{$_}++ foreach( grep { $$RE_DATA{$way}->{$_} eq $type || ($type eq "f" && ! $$RE_DATA{$way}->{$_}) } @cutters);
				}
				@cutters = keys %temp;
			}
			else
			{
				foreach my $methstat (split " ", $pa{meth_status})
				{
					my ($type, $way) = ($1, uc $2) if ($methstat =~ /(\w)\.(\w+)/);
					@cutters = grep { $$RE_DATA{$way}->{$_} eq $type || ($type eq "f" && ! $$RE_DATA{$way}->{$_}) } @cutters;
				}
			}
		}
	}
	foreach my $forbid (split " ", $pa{disallowed_seq})
	{
		@cutters = grep { $$RE_DATA{CLEAN}->{$_}	!~ regres($forbid) } @cutters;
	}
	my %forced;
	foreach my $force (split " ", $pa{required_seq})
	{
		$forced{$_}++ foreach (grep { $$RE_DATA{CLEAN}->{$_}	=~ regres($force) } @cutters);
		@cutters = keys %forced;
	}

	return @cutters;
}

sub mutexclu
{
	my ($used_ref, $allsites_ref) = @_;
	#don't want second degree exclusion - only exclude if it's not a -2 site
	foreach my $c ( grep {$$used_ref{$_} != -2} keys %{$used_ref})
	{
		my $te = regres($$allsites_ref{$c});
		foreach my $d ( grep {$c ne $_} keys %{$allsites_ref})
		{
			my $ue = regres($$allsites_ref{$d});
			$$used_ref{$d} = -2	if ($$used_ref{$c} =~ $ue || $$allsites_ref{$d} =~ $te);
		}
	}
	return $used_ref;
}


1;
__END__