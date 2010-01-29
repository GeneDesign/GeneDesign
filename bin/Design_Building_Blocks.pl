#!/usr/bin/perl
use strict;

use Getopt::Long;
use File::Basename qw(fileparse);
use File::Path qw(make_path);
use Perl6::Slurp;
use Text::Wrap qw($columns &wrap);
use List::Util qw(first);
use GeneDesign;

$| = 1;

my %ALGORITHM = (0 => "Restriction Enzyme Overlap",
				 1 => "Length Overlap", 
				 2 => "USER Overlap");
my $CODON_TABLE = define_codon_table(1);
my %gapperlen   = (40 => 700, 50 => 740, 60 => 740, 70 => 720, 80 => 740, 90 => 720, 100 => 660);
my %ungapperlen = (40 => 700, 50 => 700, 60 => 750, 70 => 735, 80 => 760, 90 => 765, 100 => 750);
my %primerrank = ( 9 => 0, 7 => 1, 5 => 2, 3 => 3, 11 => 4);
my %useroliname = (1 => "LT", 2 => "LU", 3 => "RT", 0 => "RU");
$columns = 81;

##Get Arguments
my %config = ();
GetOptions (
			'input=s'		=> \$config{INPUT},
			'algorithm=i'	=> \$config{ALGORITHM},
			'ungapped'		=> \$config{GAPSWIT},
#			'formula:i'		=> \$config{MELFORM},
			'length:i'		=> \$config{TARBBLEN},
			'lap:i'			=> \$config{TARBBLAP},
			'oligolen:i'	=> \$config{TAROLILEN},
			'maxoligolen:i'	=> \$config{MAXOLILEN},
			'temp:i'		=> \$config{TARCHNMEL},
			'tolerance:f'	=> \$config{CHNMELTOL},
			'utemp:i'		=> \$config{TARUSRMEL},
			'ulength:s'		=> \$config{USRUNILEN},
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
    values are assumed for every parameter not provided. Oligos are always
    printed 5' to 3'.

    Any sequence provided that is less than one and a half times the target
    building block size will not be divided into building blocks, but will be
    made into oligos.

  Algorithms:
    0: Restriction Enzyme Overlap: Building Blocks will overlap on unique 
        restriction enzyme recognition sites. An overlap parameter may be 
        defined to determine how much sequence overlaps, including the 
        restriction enzyme recognition site itself. This algorithm makes use of
        existing sites only and does not add or modify sites. If there are not
        enough evenly spaced, unique RE sites the algorithm will fault. This
        algorithm is not suitable for dividing sequence over 12000 bp long.
    1: Length Overlap: Building Blocks will overlap by a user-defined overlap
        length parameter. Input sequences must be at least 1000 bp long.
    2: USER Overlap: Building Blocks will overlap on A(N)xT sequences, so as to 
        be compatible with a uracil exicision (USER) assembly protocol. The 
        width of overlap is user definable, and a melting temperature may be 
        defined for USER oligos. Input sequences must be at least 1000 bp long.

  Usage examples:
    perl Design_Building_Blocks.pl -i=Test_YCLBB.FASTA -a=2 --oligolen=60
    ./Design_Building_Blocks.pl --input=Test_YCLBB.FASTA -a=1 --ungapped

  Required arguments:
    -i,  --input : a FASTA file containing protein sequences.
    -a,  --algorithm : at least one algorithm number to determine overlap type.
        (0 = Restriction Enzyme,  1 = Sequence Length,  2 = USER)

  Optional arguments:
    -un, --ungapped: will make ungapped oligos
        (default is gapped)
    -le, --length: the length in bp of building blocks, between 400 and 1000
        (default is 740)
    -la, --lap: the target overlap between building blocks.  This parameter is
        ignored by the USER algorithm
        (default is 20 for RE overlap, 40 for length overlap)
    -o,  --oligolen: the target length in bp of assembly oligos. Best results in
        steps of 10 bp between 40 and 100 (default = 60)
    -m,  --maxoligolen: the maximum length of assembly oligos permitted
        (default is 80)
    -te, --temp: the melting temperature in degrees C of assembly oligos
        (default is 56)
    -to, --tolerance: the allowable amount of ± variation in melting temperature
        (default is 2.5˚)
    -ut, --utemp: the target melting temperature in degrees C of user oligos
        (default is 56, USER overlap only)
    -ul, --ulength: the target length of unique sequence in user oligos. This
        refers to the number of Ns in the sequence A(N)xT.  More than one may be
        provided seperated by commas from the set 5, 7, 9, or 11.
        (default is 5,7,9,11)
    -h,  --help: display this message


";
	exit;
}

##Check the consistency of required arguments
die "\n ERROR: No input file was supplied.\n"
	if (! $config{INPUT});
die "\n ERROR: $config{INPUT} does not exist.\n"
	if (! -e $config{INPUT});
die "\n ERROR: No algorithm was supplied.\n"
	unless ($config{ALGORITHM} >= 0);
die "\n ERROR: No such algorithm as $config{ALGORITHM}.\n"
	if (! exists $ALGORITHM{$config{ALGORITHM}});
	
##Set defaults and check consistency of optional arguments
$config{GAPSWIT} = $config{GAPSWIT}	? $config{GAPSWIT} - 1	:	1;
$config{TARBBLEN} = $config{TARBBLEN}	||	740;
$config{TARBBLAP} = $config{TARBBLAP}	||	$config{ALGORITHM}	?	40	:	20;
$config{TAROLILEN} = $config{TAROLILEN}	||	60;
$config{MAXOLILEN} = $config{MAXOLILEN}	||	80;
$config{TARCHNMEL} = $config{TARCHNMEL}	||	56;
$config{CHNMELTOL} = $config{CHNMELTOL}	||	2.5;
$config{TARUSRMEL} = $config{TARUSRMEL}	||	56;
$config{USRUNILEN} = $config{USRUNILEN}	|| "5,7,9,11";
my @usrlens = split(",", $config{USRUNILEN});
$config{USRUNILEN} = \@usrlens;

die "\n ERROR: The maximum oligo length is less than the target oligo length.\n"
	if ($config{MAXOLILEN} < $config{TAROLILEN});
warn "\n WARNING: Maximum oligo length is equal to the target oligo length.\n"
	if ($config{MAXOLILEN} == $config{TAROLILEN});
die "\n ERROR: building block size is outside of allowable range.\n"
	if ($config{TARBBLEN} < 400 || $config{TARBBLEN} > 1000);

##Fetch input sequences
my $filename	  = fileparse( $config{INPUT}, qr/\.[^.]*/);
make_path($filename . "_gdBB_$config{ALGORITHM}");
my $input		  = slurp( $config{INPUT} );
my $ORIG_SEQUENCE = fasta_parser( $input );
warn "\n WARNING: $_ is too small to be made into oligos.\n"
	foreach(
		grep {   length($$ORIG_SEQUENCE{$_}) < 120}
		keys %$ORIG_SEQUENCE);
warn "\n WARNING: $_ will be a single building block.\n"
	foreach(
		grep {   length($$ORIG_SEQUENCE{$_}) < 1.5 * $config{TARBBLEN}
				&& length($$ORIG_SEQUENCE{$_}) >= 120}
		keys %$ORIG_SEQUENCE);
warn "\n WARNING: $_ is too long to be processed by this algorithm.\n"
	foreach(
		grep { $config{ALGORITHM} == 0 && length($$ORIG_SEQUENCE{$_}) > 12000 }
		keys %$ORIG_SEQUENCE);

print "\n";

foreach my $seqid ( grep {  length($$ORIG_SEQUENCE{$_}) < 1.5 * $config{TARBBLEN} 
						 && length($$ORIG_SEQUENCE{$_}) >= 120} 
					keys %$ORIG_SEQUENCE)
{
	my %pa;
	my $chunk_name		= substr($seqid, 1);
	my $wholeseq		= $$ORIG_SEQUENCE{$seqid};
	my $wholelen		= length($wholeseq);
	
	$pa{gapswit}		= $config{GAPSWIT};
	$pa{tar_chn_mel}	= $config{TARCHNMEL};
	$pa{tar_oli_len}	= $config{TAROLILEN};
	$pa{per_chn_len}	= $pa{gapswit} == 1	?	$gapperlen{$pa{tar_oli_len}}			:	$ungapperlen{$pa{tar_oli_len}};
	$pa{tar_oli_lap}	= $pa{gapswit} == 1	?	20										:	.5 * $pa{tar_oli_len};# these are the defaults, 12 60mers with 20bp overlaps and 20bp gaps, nongapped oligos overlap by half the oligo length
	$pa{tar_oli_gap}	= $pa{gapswit} == 1	?	$pa{tar_oli_len}-(2*$pa{tar_oli_lap})	:	0;						# length = 2*(overlap) + gap, nongapped oligos have no gaps.
	$pa{tar_oli_num}	= ($pa{per_chn_len} - $pa{tar_oli_lap}) / ($pa{tar_oli_len} - $pa{tar_oli_lap});#18;
	$pa{chn_mel_tol}	= $config{CHNMELTOL};
	$pa{max_oli_len}	= $config{MAXOLILEN};
	$pa{melform}		= 3;
	
	my $tno = new Chunk;
	$tno->ChunkNumber("01");
	$tno->ChunkSeq($wholeseq);
	$tno->ChunkLength($wholelen);
	$tno->ChunkStart(1);
	$tno->ChunkStop($tno->ChunkLength + $tno->ChunkStart - 1);
	oligocruncher($tno, \%pa);
	print("1 building block was generated for $chunk_name.\n");
	open (my $bbfh, ">" . $filename . "_gdBB_$config{ALGORITHM}/" . $chunk_name . "_gdBB.FASTA") || die "can't create output file, $!";
	print $bbfh ">$chunk_name.", $tno->ChunkNumber, " (", $tno->ChunkLength, " bp)\n";
	print $bbfh wrap( "", "", $tno->ChunkSeq), "\n";
	close $bbfh;
	print "\t" . $chunk_name . "_gdBB.FASTA has been written.\n";	
	open (my $ofh, ">" . $filename . "_gdBB_$config{ALGORITHM}/" . $chunk_name . "_gdBB_oligos.FASTA") || die "can't create output file, $!";
	my $x = 1;
	foreach my $oligo (@{$tno->Oligos})
	{
		my $te = $x;
		$te = '0' . $te while (length($te) < length(scalar(@{$tno->Oligos})) || length($te) < 2);
		print $ofh ">$chunk_name.", $tno->ChunkNumber, ".o$te (", length($oligo), " bp)\n";
		print $ofh "$oligo\n" if ($x % 2);
		print $ofh complement($oligo, 1), "\n" if ($x % 2 == 0);
		$x++;
	}
	close $ofh;
	print "\t" . $chunk_name . "_gdBB_oligos.FASTA has been written.\n";
}

foreach my $seqid ( grep { length($$ORIG_SEQUENCE{$_}) >= 1.5 * $config{TARBBLEN} } 
					keys %$ORIG_SEQUENCE)
{
	my %pa;
	my @BBlocks;
	my $chunk_name		= substr($seqid, 1);
	my $wholeseq		= $$ORIG_SEQUENCE{$seqid};
	my $wholelen		= length($wholeseq);
	my $tar_bbl_len		= $config{TARBBLEN};
	my $bbl_lap_len		= $config{TARBBLAP};
	
	$pa{gapswit}		= $config{GAPSWIT};
	$pa{tar_chn_mel}	= $config{TARCHNMEL};
	$pa{tar_oli_len}	= $config{TAROLILEN};
	$pa{per_chn_len}	= $pa{gapswit} == 1	?	$gapperlen{$pa{tar_oli_len}}			:	$ungapperlen{$pa{tar_oli_len}};
	$pa{tar_oli_lap}	= $pa{gapswit} == 1	?	20										:	.5 * $pa{tar_oli_len};# these are the defaults, 12 60mers with 20bp overlaps and 20bp gaps, nongapped oligos overlap by half the oligo length
	$pa{tar_oli_gap}	= $pa{gapswit} == 1	?	$pa{tar_oli_len}-(2*$pa{tar_oli_lap})	:	0;						# length = 2*(overlap) + gap, nongapped oligos have no gaps.
	$pa{tar_oli_num}	= ($pa{per_chn_len} - $pa{tar_oli_lap}) / ($pa{tar_oli_len} - $pa{tar_oli_lap});#18;
	$pa{chn_mel_tol}	= $config{CHNMELTOL};
	$pa{max_oli_len}	= $config{MAXOLILEN};
	$pa{melform}		= 3;
		
	if ($config{ALGORITHM} == 0)
	{
		my %chunk;
		my $RE_DATA = define_sites("bs_enzymes.txt");
		my $tar_chn_lap		= .5 * $config{TARBBLAP};
		my $tar_chn_len	= $pa{per_chn_len};					#this is for the magic oligo end numbers
		$tar_chn_len	= ($wholelen/2) if ($wholelen <= 500);	#($tar_chn_len+(.6*$tar_chn_len)));
		$tar_chn_len	= $wholelen     if ($wholelen < 900);	#($tar_chn_len+(.2*$tar_chn_len)));
		my $tarmult		= .96*$tar_chn_len;					#ditto
		my $limit		= int ($wholelen/$tarmult)+1;
	##-Figure out what the unique sites are, ignore blunts and one bp overhangs
		my $SITE_STATUS = define_site_status($wholeseq, $$RE_DATA{REGEX});
		my %borders;
		foreach my $enzyme (grep {$$RE_DATA{TYPE}->{$_} !~ /b/ && $$SITE_STATUS{$_} == 1 && 
								($$RE_DATA{TABLE}->{$_} =~ $IIP || $$RE_DATA{TABLE}->{$_} =~ $IIP2)} 
							keys %{$$RE_DATA{CLEAN}})
		{	
			my $positions = siteseeker($wholeseq, $enzyme, $$RE_DATA{REGEX}->{$enzyme});
			my @temparr = keys %$positions;
			my $site = scalar(shift (@temparr)) + length($$RE_DATA{CLEAN}->{$enzyme}) + $tar_chn_lap;
			$borders{$enzyme} = $site;
		}		
		die ("$chunk_name does not contain enough unique restriction enzyme recognition sites.\n")
				if (scalar(keys %borders) < ($wholelen/$tarmult)+1);
		my %chosen;
		if ($wholelen > ($tar_chn_len+(.2*$tar_chn_len)))
		{
			my $target = $tar_chn_len;
			my $tcv = 0;
			while ($target < ($limit*$tarmult))
			{
				my @potents = sort {abs($borders{$a}-$target) <=> abs($borders{$b}-$target)} grep {$borders{$_} >= 0.5* $tar_chn_len} keys %borders;
				$chosen{$potents[0]} = $borders{$potents[0]};
				$target = $target - ((2*$tar_chn_lap) + length($$RE_DATA{CLEAN}->{$potents[0]})) + $tar_chn_len;
				$tcv++;
				last if ($tar_chn_len < $pa{per_chn_len} && $tcv == 1);
				last if ($wholelen - $target <= ($tar_chn_len-(.5*$tar_chn_len)));
			}
		}
		my ($y, $start) = (0, 0);
	##-Actually make the chunks, including the left over chunk
		foreach my $enz (sort {$chosen{$a} <=> $chosen{$b}}keys %chosen)
		{
			my $chunk = new Chunk;
			$chunk->ChunkSeq(substr($wholeseq, $start, $chosen{$enz} - $start-1));
			$chunk->ChunkLength(length($chunk->ChunkSeq));
			$chunk->ChunkStart($chosen{$enz} - (2 * $tar_chn_lap) - 1 - length($$RE_DATA{CLEAN}->{$enz}));
			$chunk->ThreePrimeEnz($enz);
			$chunk->ChunkNumber($y+1);
			$chunk->Parameters(\%pa);
			$chunk->ChunkStop($chosen{$enz});
			$start = $chosen{$enz} - 2 * $tar_chn_lap - 1 - length($$RE_DATA{CLEAN}->{$enz});
			$chunk->ThreePrimeOlap($chunk->ChunkStop - $start - 1);
			push @BBlocks, $chunk;
			$y++;
		}
		{	
			my $chunk = new Chunk;
			$chunk->ChunkSeq(substr($wholeseq, $start));
			$chunk->ChunkLength(length($chunk->ChunkSeq));
			$chunk->ChunkStart($start);
			$chunk->ChunkNumber($y+1);
			$chunk->Parameters(\%pa);
			$chunk->ChunkStop($wholelen + 1);
			push @BBlocks, $chunk;
			$y++;
		}
		oligocruncher($_, \%pa) foreach (@BBlocks);
	}
	elsif ($config{ALGORITHM} == 1)
	{
		my @Olaps;
		my %bblen = $pa{gapswit}	?	%gapperlen	:	%ungapperlen;
		my $chunkcount = 0;
		my $tar_num = int(($wholelen / ($tar_bbl_len-$bbl_lap_len)) + 0.5);
		my $tar_len = int(($wholelen / $tar_num) + 0.5) - 1;
		
		my ($laststart, $cur) = (0, 0);
		my $tar_cur_dif = length($wholeseq) - ($tar_num * ($tar_bbl_len) - $bbl_lap_len * ($tar_num - 1));
		my $tar_bbl_len = $tar_bbl_len;
		if (abs($tar_cur_dif) >= $tar_num)
		{
			$tar_bbl_len = $tar_bbl_len + int($tar_cur_dif / $tar_num);
			$tar_cur_dif = $tar_cur_dif - ($tar_num * (int($tar_cur_dif / $tar_num)));
		}
		for my $cur (1..$tar_num)
		{
			my $cur_bbl_len = $tar_bbl_len;
			$cur_bbl_len++ if ( $cur <= abs($tar_cur_dif) && $tar_cur_dif > 0);
			$cur_bbl_len-- if ( $cur <= abs($tar_cur_dif) && $tar_cur_dif < 0);
			my $tno = new Chunk;
			my $countstr = $chunkcount + 1;
			while (length(@BBlocks-0) > length($countstr) || length($countstr) > 2)	{	$countstr = "0" . $countstr;}
			$tno->ChunkNumber($countstr);
			$tno->ChunkSeq(substr($wholeseq, $laststart, $cur_bbl_len));
			$tno->ThreePrimeOlap(substr($wholeseq, $laststart + $cur_bbl_len - $bbl_lap_len, $bbl_lap_len));
			$tno->ChunkLength(length($tno->ChunkSeq));
			$tno->ChunkStart($laststart);
			$tno->ChunkStop($tno->ChunkLength + $tno->ChunkStart - 1);
			push @Olaps, $tno->ThreePrimeOlap;
			oligocruncher($tno, \%pa);
			$laststart += $tno->ChunkLength - length($tno->ThreePrimeOlap);
			push @BBlocks, $tno;
			$chunkcount++;
		}
	}
	elsif ($config{ALGORITHM} == 2)
	{
		my $usr_mel			= $config{TARUSRMEL};
		my @usr_uni_len		= @{$config{USRUNILEN}};
		my %FoundSite;
		my %FoundSiteCoor;
		my (@UniUsers, @Collection) = ((), ());
		my ($offset, $count) = (0, 0);
			
	## Load two hashes with the number of times ANxT is seen and where the last one was seen. Parse the number hash for the unique ones, push into Data structure and store in array.
		foreach my $tiv (@usr_uni_len)
		{
			my @sites;
			$sites[0] = "A" . ("N" x $tiv) . "T";
			$sites[1] = complement($sites[0], 1) if (complement($sites[0], 1) ne $sites[0]);
			foreach my $sit (@sites)
			{
				my $exp = regres($sit, 1);
				while ($wholeseq =~ /($exp)/ig)
				{
					my $sitsta = (pos $wholeseq) + 1;
					if ($sitsta ne '') {	$FoundSite{$1}++;	$FoundSiteCoor{$1} = $sitsta + $offset - length($1);	}
				}
			}
		} 
		foreach my $tiv (keys %FoundSite)
		{
			if ($FoundSite{$tiv} == 1 && !exists($FoundSite{complement($tiv)}))
			{
				my $tno = new USERsite;	$tno->Sequence($tiv);	$tno->nNumber(length($tiv)-2);	$tno->Start($FoundSiteCoor{$tiv});
				push @UniUsers, $tno;
			}
		}

	## Adjust the target building block size so as to avoid outliers.
		my $tarnum = int(length($wholeseq) / $tar_bbl_len);
		my $diff = length($wholeseq) - ($tarnum * $tar_bbl_len);
		$tar_bbl_len = (($diff/$tarnum)*12.5 >= $tar_bbl_len)	
			?	int(length($wholeseq)/($tarnum+1) + .5)	
			:	$tar_bbl_len + int($diff/$tarnum);
	## Pick the unique sites as close as possible to the requested intervals.
		my $lasttarget = $offset;
		my $target = 0;
		while ($target < length($wholeseq))
		{
			$target = $tar_bbl_len + $lasttarget;
			my ($seen, $door, $int) = (0, 1, 1);
			while ($seen == 0)
			{
				my @grabbed = grep {$_->Start == $target} @UniUsers;
				if (scalar(@grabbed) > 0)
				{
					my $currchoice = $grabbed[0];
					foreach my $tov (@grabbed)
					{
						$currchoice = $tov	if ($primerrank{length($tov->Sequence)}
							&& $primerrank{length($tov->Sequence)} < $primerrank{length($currchoice->Sequence)});
					}
					$lasttarget = $target;
					$target = $currchoice->Start + $tar_bbl_len;
					push @Collection, $currchoice;
					$seen = 1;
				}
				$target = $target - $int if ($door == 1);
				$target = $target + $int if ($door == 0);
				$door = abs($door-1);
				$int++;
				if ($target <= ($lasttarget + (.4 * $tar_bbl_len)))
				{
					$lasttarget += ($tar_bbl_len * .5);last;
				}
				$seen = 0;	
			}
		}
	## Form chunk objects, fill with user primers and oligos
		my $lastfound = 1;
		my $laststart;
		my $lastlength = 0;
		foreach my $tiv (@Collection)
		{
			my $tno = new Chunk;
			my @Users;
		
			$tno->ChunkSeq(substr($wholeseq, $lastfound - 1, $tiv->Start - $lastfound + $tiv->nNumber + 2));
			if (length($tno->ChunkSeq) < length(substr($wholeseq, $lastfound-1)) && $count == int((length($wholeseq) / $tar_bbl_len)+.5) -1)
			{
				$tno->ChunkSeq(substr($wholeseq, $lastfound-1));
			}
			$tno->ChunkLength(length($tno->ChunkSeq));
			$tno->ChunkStart($lastfound);
			$tno->ChunkStop($tno->ChunkLength + $tno->ChunkStart - 1);
			my $remain = length(substr($wholeseq, $tiv->Start-1));
			if ($remain < $tar_bbl_len / 4)	{	$tno->ChunkSeq(substr($wholeseq, $lastfound - 1));	}
			my $countstr = $count + 1;
			while (length(@Collection-0) > length($countstr))	{	$countstr = "0" . $countstr;}
			$tno->ChunkNumber($countstr);
			my $pri_len = 0;
			if ($count > 0)
			{
				$Users[0] = substr($wholeseq, $laststart, $lastlength + 2);
				until (int(melt($Users[0], 3) + .5) >= $usr_mel)	
				{
					$pri_len++;
					$Users[0] = substr($wholeseq, $laststart, $pri_len)
				}
				$Users[1] = substr($Users[0], 0, $lastlength+1) . 'U' . substr($Users[0], $lastlength + 2);
			}
			else
			{
				$Users[0] = substr($wholeseq, 0, 5);
				until (int(melt($Users[0], 3) + .5) >= $usr_mel)
				{
					$pri_len++;
					$Users[0] = substr($wholeseq, 0, $pri_len)
				}
				$Users[1] = "-";
			}
			$pri_len = 0;
			if ($count != (@Collection-1))
			{
				$Users[2] = substr($wholeseq, $tiv->Start - 1, $tiv->nNumber + 2);
				until (int(melt($Users[2], 3) + .5) >= $usr_mel)	
				{
					$pri_len++;
					$Users[2] = substr($wholeseq, $tiv->Start - 1 - $pri_len, $tiv->nNumber + 2 + $pri_len);
				}
				$Users[2] = complement($Users[2], 1);
				$Users[3] = substr($Users[2], 0, $tiv->nNumber + 1) . 'U' . substr($Users[2], $tiv->nNumber + 2);
				$laststart = $tiv->Start - 1;
				$lastlength = $tiv->nNumber;
			}
			else
			{
				$Users[2] = substr($wholeseq, -10);
				until (int(melt($Users[2], 3) + .5) >= $usr_mel)	
				{
					$pri_len++;$Users[2] = substr($wholeseq, -(10 + $pri_len));
				}
				$Users[2] = complement($Users[2], 1);
				$Users[3] = "-";
			}
			$lastfound = $tiv->Start;#$lastseq = $tiv->Sequence;
			$tno->Users(\@Users);
			$count++;
			oligocruncher($tno, \%pa);
			push @BBlocks, $tno;
		}
	}
	
	##FASTA output
	print (scalar(@BBlocks) . " building blocks were generated for $chunk_name.\n");	
	open (my $bbfh, ">" . $filename . "_gdBB_$config{ALGORITHM}/" . $chunk_name . "_gdBB.FASTA") || die "can't create output file, $!";
	my $lastenz = '';
	foreach my $bb (@BBlocks)
	{
		my $te = $bb->ChunkNumber;
		$te = '0' . $te while (length($te) < length(scalar(@BBlocks)) || length($te) < 2);
		print $bbfh ">$chunk_name.$te (", $bb->ChunkLength, " bp)";
		if ($config{ALGORITHM} == 0)
		{
			print $bbfh " 5' enzyme is ", $lastenz if ($lastenz);
			print $bbfh " 3' enzyme is ", $bb->ThreePrimeEnz if ($bb->ThreePrimeEnz);
			$lastenz = $bb->ThreePrimeEnz;
		}
		print $bbfh "\n", wrap( "", "", $bb->ChunkSeq), "\n";
	}
	close $bbfh;
	print "\t" . $chunk_name . "_gdBB.FASTA has been written.\n";	
	open (my $ofh, ">" . $filename . "_gdBB_$config{ALGORITHM}/" . $chunk_name . "_gdBB_oligos.FASTA") || die "can't create output file, $!";
	foreach my $bb (@BBlocks)
	{
		my $x = 1;
		foreach my $oligo (@{$bb->Oligos})
		{
			my $te = $x;
			$te = '0' . $te while (length($te) < length(scalar(@{$bb->Oligos})) || length($te) < 2);
			print $ofh ">$chunk_name.", $bb->ChunkNumber, ".o$te (", length($oligo), " bp)\n";
			print $ofh "$oligo\n" if ($x % 2);
			print $ofh complement($oligo, 1), "\n" if ($x % 2 == 0);
			$x++;
		}
	}
	close $ofh;
	print "\t" . $chunk_name . "_gdBB_oligos.FASTA has been written.\n";
	if ($config{ALGORITHM} == 2)
	{
		open (my $ufh, ">" . $filename . "_gdBB_$config{ALGORITHM}/" . $chunk_name . "_gdBB_users.FASTA") || die "can't create output file, $!";
		foreach my $bb (@BBlocks)
		{
			my $x = 1;
			foreach my $user (@{$bb->Users})
			{
				print $ufh ">$chunk_name." , $bb->ChunkNumber, ".u", $useroliname{$x%4}, " ", length($user), "bp\n", $user, "\n" if ($user ne "-");
				$x++;
			}
		}
		close $ufh;
		print "\t" . $chunk_name . "_gdBB_users.FASTA has been written.\n";
	}
}

exit;