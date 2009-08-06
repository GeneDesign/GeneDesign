package PRISM;
use 5.006;
use POSIX qw(log10);
require Exporter;

@ISA = qw(Exporter);
@EXPORT = qw(hairpins count melt nntherm compareseqs ezalign translate transregex revtrans getcods getaaa codopt stopfinder orffinder 
				complement changeup optimize organism cleanup randDNA siteload sitelength siterunner siteseeker regres mutexclu);
			
###### Functions for Sequence Analysis
##-count		: given a string of nucleotides, returns an array with base count A T C G N, purine, pyrimidine, and nonN non ATCG bases.
##
##-melt			: given a string of nucleotides returns an array with various melting temperatures.  Possible to pass salt and DNA concentrations
##					although this is not used in GeneDesign.
##-nntherm		: given a string of nucleotides, defaults an array with ÆH, ÆS and ÆG from Breslauer 86.
##					nearest neighbor
##-compareseqs	: given two sequences of equal length in string format, reports on whether or not they equal each other, 
##					taking into account ambiguities. Cur is the ambiguous sequence. ***Should probably be replaced with regres
##-ezalign		: given two sequences of presumably the same coordinates, reports on identity, # changes, and type of changes.
##
##-translate	: passed an unambiguous string of nucleotides and a frame returns aa sequence
##
##-transregex	: passed an ambiguous string of nucleotides returns an array of every possible AA combo. HEAVY.  Intended to work only on
##					sequences of restriction site length so don't feed it a gene.  ***Probably needs to be looked at by an expert.
##-revtrans		: passed a string of amino acids and an array of codon values, returns nucleotides.  codon array values should be 
##					$codons[0] = "* TGA"; $codons[1] = "A GCC"; etc
##-getcods		: passed an amino acid character, returns an array of all possible unambiguous codons that could produce it.
##
##-getaaa		: passed a codon string with possibly ambiguous positions, returns possible amino acids as a list  
##					***Maybe this should be a string?
##-codopt		: returns codon optimization information - sets non local array variables to reflect the switch.
##					***Really needs to be looked at by an expert
##-stopfinder	: returns an array of stop positions for the nuc sequence and frame passed
##
##-orffinder	: returns an array of mashed up orflengths and start positions for the nucsequence and frame passed
##

###### Functions for Sequence Manipulation
##-complement	: passed a string of nucleotides, returns the complement (eg, TGC returns ACG)
##					or returns reverse complement (eg, TGC returns GCA) with appropriate switch
##-changeup		: given a nucleotide sequence returns a different nucleotide sequence that codes for the same amino acids 
##					or the same sequence if impossible.  Swit 1 is random.  2 is next most optimal. 3 is most diff.
##-optimize		: picks the most optimal codons from the codopt function for the organism provided.  provide with a nucseq, it returns
##					a nuc seq.
##-organism		: Given an organism number, returns a string containing the name.  ***should really be in PML.pm
##
##-cleanup		: given a sequence (straight from the user) changes case, removes linebreaks, and checks for non
##					nucleotide / non aa characters.  Returns a sequence without any of that stuff or errors (with appropriate switch).

###### Functions for Sequence Generation
##-randDNA		: generates a random sequence of requested length and composition, with or without internal stops in first frame.

###### Functions for Restriction Enzymes
##-siteload		: loads up our enzyme names (default)
##
##-sitelength	: given a resname gets sitelength from enzyme flat file
##
##-siterunner	: given a nucleotide sequence returns information on internal restriction sites
##
##-siteseeker	: given a nucleotide sequence and an enzyme returns an array of positions
##
##-regres		: passed a string that may contain ambiguities, returns a string that can be used for 
##					regular expression searching, for restriction enzyme sites.
##-mutexclu	: checks the passed hash for the existence of mutually exclusive recognition sites.  If found, the
##					conflicting cutter is added to the hash with a value of -2


##-given a string of nucleotides, returns an array with base count in, A T C G N, purine, pyrimidine, and nonN nonATCG bases.
sub count
{
	my ($strand) = @_;
	return if (!$strand);
	$strand = cleanup($strand, 1);
	@stran = split('', $strand);
	undef @sums;
	foreach $n (@stran)
	{
		$sums[0]++ if ($n eq 'A');
		$sums[1]++ if ($n eq 'T');
		$sums[2]++ if ($n eq 'C');
		$sums[3]++ if ($n eq 'G');								
		$sums[4]++ if ($n eq 'N');								#not specified
		$sums[5]++ if ($n eq 'A' || $n eq 'G' || $n eq 'R');	#purine
		$sums[6]++ if ($n eq 'T' || $n eq 'C' || $n eq 'Y');	#pyrimidine
	}
	$sums[7] = length($strand) - ($sums[0]+$sums[1]+$sums[2]+$sums[3]+$sums[4]);
	push @sums, length($strand);
	return @sums;
}

##-given a string of nucleotides, defaults an array with various melting temperatures, returns specific formulas
sub melt
{
	my ($strand, $swit, $salt, $conc) = @_;
	return if (!$strand);
	$strand = cleanup($strand, 1);
	$conc = .0000001 if ($conc == undef);
	$salt = .05 if ($salt == undef);
	$swit = 5   if ($swit == undef);
	@bcomp = count($strand);
	@therg = nntherm($strand);
	$mgc = 1.987;
	my $simple = ((4 * ($bcomp[2] + $bcomp[3])) + (2 * ($bcomp[0] + $bcomp[1])));
	my $baldin = (81.5 + 16.6*log10($salt) + 41*(($bcomp[2]+$bcomp[3])/length($strand)) - (675/length($strand)));
	my $primer = (81.5 + 16.6*log10($salt) + 41*(($bcomp[2]+$bcomp[3])/length($strand)) - (600/length($strand)));
	my $thermo = ((($therg[0]-3.4) / (($therg[1]+($mgc*abs(log($conc/4))))/1000))-273.15) + (16.6*log10($salt));
	my $avrage = int((($baldin+$primer+$thermo)/3)+.5);
	@Tm = (int($baldin+.5), int($primer+.5), int($thermo+.5));
	#@Tm = (int($baldin+.5), int($primer+.5), int($simple+.5));
	return $simple if ($swit == 1);
	return $baldin if ($swit == 2);
	return $primer if ($swit == 3);
	return $thermo if ($swit == 4);
	return @Tm     if ($swit == 5);
	return $avrage if ($swit == 6);
}

##-given a string of nucleotides, defaults an array with ÆH, ÆS and ÆG from Breslauer 86.
sub nntherm
{
	my ($strand) = @_;
	return if (!$strand);
	$strand = cleanup($strand, 1);
	@therm = undef; @count = undef; @thref = undef; $nnref = undef;
	$dH    = undef;    $dS = undef;    $dG = undef;
	##			    ÆHû   ÆSû  ÆGû      sense strand
	$thref[ 0] = ([ 8.8, 23.5, 1.5]); # TC 
	$thref[ 1] = $thref[ 0];          # GA 
	$thref[ 2] = ([ 6.6, 16.4, 1.5]); # CT 
	$thref[ 3] = $thref[ 2];          # AG 
	$thref[ 4] = ([10.9, 28.4, 2.1]); # GG 
	$thref[ 5] = $thref[ 4];          # CC 
	$thref[ 6] = ([ 8.0, 21.9, 1.2]); # AA 
	$thref[ 7] = $thref[ 6];          # TT 
	$thref[ 8] = ([ 5.6, 15.2, 0.9]); # AT 
	$thref[ 9] = ([ 6.6, 18.4, 0.9]); # TA 
	$thref[10] = ([11.8, 29.0, 2.8]); # CG 
	$thref[11] = ([10.5, 26.4, 2.3]); # GC 
	$thref[12] = ([ 8.2, 21.0, 1.7]); # CA
	$thref[13] = $thref[12];          # TG 
	$thref[14] = ([ 9.4, 25.5, 1.5]); # GT 
	$thref[15] = $thref[14];          # AC 
	@nnref = qw(TC GA CT AG GG CC AA TT AT TA CG GC CA TG GT AC);
	for ($r = 0; $r < (@nnref-0); $r++)
	{
		$w = $nnref[$r];
		$count[$r]++ while ($strand =~ /(?=$w)/ig);
	}
	for($r = 0; $r < (@count-0); $r++)
	{
			$dH += ($thref[$r][0]*$count[$r]);
			$dS += ($thref[$r][1]*$count[$r]);
			$dG += ($thref[$r][2]*$count[$r]);
	}
	$dG -= 5.4;
	@therm = ($dH, $dS, $dG);
	return @therm;
}

##-given two sequences in string format, reports on whether or not they equal each other,
##-taking into account ambiguities. Cur is the ambiguous sequence.
sub compareseqs
{
	my ($cur, $tar) = @_;
	@curstr = split ('', $cur);
	@tarstr = split ('', $tar);
	$lenstr = length($tar);
	$total = 0;
	for ($f = 0; $f < $lenstr; $f++)
	{	
		$total++ if ($curstr[$f] eq 'R' && ($tarstr[$f] eq 'A' || $tarstr[$f] eq 'G'));
		$total++ if ($curstr[$f] eq 'Y' && ($tarstr[$f] eq 'T' || $tarstr[$f] eq 'C'));
		$total++ if ($curstr[$f] eq 'M' && ($tarstr[$f] eq 'C' || $tarstr[$f] eq 'A'));
		$total++ if ($curstr[$f] eq 'K' && ($tarstr[$f] eq 'T' || $tarstr[$f] eq 'G'));
		$total++ if ($curstr[$f] eq 'S' && ($tarstr[$f] eq 'C' || $tarstr[$f] eq 'G'));
		$total++ if ($curstr[$f] eq 'W' && ($tarstr[$f] eq 'T' || $tarstr[$f] eq 'A'));
		$total++ if ($curstr[$f] eq 'B' && ($tarstr[$f] eq 'T' || $tarstr[$f] eq 'C' || $tarstr[$f] eq 'G'));
		$total++ if ($curstr[$f] eq 'D' && ($tarstr[$f] eq 'T' || $tarstr[$f] eq 'A' || $tarstr[$f] eq 'G'));
		$total++ if ($curstr[$f] eq 'H' && ($tarstr[$f] eq 'T' || $tarstr[$f] eq 'C' || $tarstr[$f] eq 'A'));
		$total++ if ($curstr[$f] eq 'V' && ($tarstr[$f] eq 'C' || $tarstr[$f] eq 'A' || $tarstr[$f] eq 'G'));
		$total++ if ($curstr[$f] eq 'N');
		$total++ if ($curstr[$f] eq $tarstr[$f]);
	}
	return 1 if ($total == $lenstr);
	return 0 if ($total != $lenstr);
}

##-given two sequences of presumably the same coordinates, reports on identity, #changes, and type
sub ezalign
{
	my ($topseq, $botseq) = @_;
	return if (!$botseq);
	my $len = length($topseq);
	my $count = 0; my $tsit = 0; my $tver = 0;
	my @alresults;
	#return "ERR" if ($len != length($botseq));
	$f = 0;
	while ($f < $len)
	{
		$topbit = (substr $topseq, $f, 1); $botbit = (substr $botseq, $f, 1);
		if ($topbit ne $botbit)
		{
			$count++;
			$tsit++ if (($topbit =~ regres('R') && $botbit =~ regres('R')) || ($topbit =~ regres('Y') && $botbit =~ regres('Y')));
			$tver++ if (($topbit =~ regres('Y') && $botbit =~ regres('R')) || ($topbit =~ regres('R') && $botbit =~ regres('Y')));
		}
		$f++;
	}
	$alresults[0] = $len - $count; #identities
	$alresults[1] = $count;		   #changes
	$alresults[2] = $tsit;		   #transitions
	$alresults[3] = $tver;		   #transversions
	$alresults[4] = (100 - (($count / $len) *100));	#percent identity
	return @alresults;
}
##-passed an unambiguous string of nucleotides, translates into amino acids on passed frame
sub translate
{
	my ($nucseq, $swit) = @_;
	return if (!$nucseq);
	return if $nucseq =~/[RYSWKMBDVHN]/;
	$nucseq = cleanup($nucseq, 1);
	$actnt = undef;
	$swit = 1 if (!$swit);
	$offset = $swit-1;
	for ($j = 0; $j < (int(length($nucseq) / 3)); $j++)
	{
		@temparr = getaaa(substr($nucseq, $offset, 3));
		$actnt .= $temparr[0] if ($offset <= length($nucseq)-3);
		$offset+=3;
	}
	return $actnt;
}

##-passed an ambiguous string of nucleotides returns an array of every possible AA combo
sub transregex
{
	my ($site) = @_;
	return if (!$site);
	$site = cleanup($site, 1);
	my $foff = 0;
	@potarr = undef;
	undef @temcom;
	$site = 'NN' . $site;
	for ($j = 0; $j < 3; $j++)
	{
		my $tcv  = 0;
		my $potstr = '';
		for ($offset = $foff; $offset < (int(length($site))); $offset +=3)
		{
			$tempstr = substr($site, $offset, 3), "\n\n";
			$tempstr .= 'N' while (length($tempstr) < 3);
			$potstr .= join("", getaaa($tempstr)) . " ";
			$tcv++;
		}
		$foff++;
		$tempstr = '';
		push @potarr, $potstr;
		$potstr = '';
	}
	foreach $e (@potarr)
	{
		@temparr = split(" ", $e);
		for ($f = 0; $f <= (@temparr-0); $f++)
		{
			@$f = split("", $temparr[$f]);
		}
		$f-- if ((@$f)-0 == 0);
		foreach $do (@0) #1
		{
			foreach $re (@1) #2
			{
				if ($f >= 3)
				{
					foreach $mi (@2) #3
					{
						if ($f >= 4)
						{
							foreach $fa (@3) #4
							{
								if ($f >= 5)
								{
									foreach $so (@4) #5
									{
										push @temcom, ($do . $re . $mi . $fa . $so);
									}
								}
								else
								{
									push @temcom, ($do . $re . $mi . $fa);
								}
							}
						}
						else
						{
							push @temcom, ($do . $re . $mi);
						}
					}
				}
				else
				{
					push @temcom, ($do . $re);
				}
			}
		}
	}
	return @temcom;
}

##-passed a string of amino acids and an array of codon values, returns nucleotides
## codon array values should be $codons[0] = "* TGA"; $codons[1] = "A GCC"; etc
sub revtrans
{
	my($aaseq, @codons) = @_;
	return if(!$aaseq);
	$aaseq = cleanup($aaseq, 2);
	my $newseq = '';
	@aaseq = split('', $aaseq);
	foreach $h (@aaseq)
	{
		unless ($h eq '*')
		{
			foreach $i (@codons)
			{
				if ($i =~/$h\s+([A-Z]{3})/)
				{
					$newseq .= $1;
					last;
				}
			}
		}
		else
		{
			$i = $codons[0];
			$newseq .= $1 if ($i =~/\*\s+([A-Z]{3})/); 
		}
	}
	return $newseq;	
}

##-passed an amino acid character, returns an array of all possible codons that could produce each
sub getcods
{
	my ($a) = @_;
	@cods = ('GCT', 'GCC', 'GCA', 'GCG')				if ($a eq 'A');
	@cods = ('TGT', 'TGC')								if ($a eq 'C');
	@cods = ('GAT', 'GAC')								if ($a eq 'D');
	@cods = ('GAA', 'GAG')								if ($a eq 'E');
	@cods = ('TTT', 'TTC')								if ($a eq 'F');
	@cods = ('GGT', 'GGC', 'GGA', 'GGG')				if ($a eq 'G');
	@cods = ('CAT', 'CAC')								if ($a eq 'H');
	@cods = ('ATT', 'ATC', 'ATA')						if ($a eq 'I');
	@cods = ('AAA', 'AAG')								if ($a eq 'K');
	@cods = ('TTA', 'TTG', 'CTT', 'CTC', 'CTA', 'CTG')	if ($a eq 'L');
	@cods = ('ATG')										if ($a eq 'M');
	@cods = ('AAT', 'AAC')								if ($a eq 'N');
	@cods = ('CCT', 'CCC', 'CCA', 'CCG')				if ($a eq 'P');
	@cods = ('CAA', 'CAG')								if ($a eq 'Q');
	@cods = ('CGT', 'CGC', 'CGA', 'CGG', 'AGA', 'AGG')	if ($a eq 'R');
	@cods = ('TCT', 'TCC', 'TCA', 'TCG', 'AGT', 'AGC')	if ($a eq 'S');
	@cods = ('ACT', 'ACC', 'ACA', 'ACG')				if ($a eq 'T');
	@cods = ('GTT', 'GTC', 'GTA', 'GTG')				if ($a eq 'V');
	@cods = ('TGG')										if ($a eq 'W');
	@cods = ('TAT', 'TAC')								if ($a eq 'Y');
	@cods = ('TAA', 'TGA', 'TAG')						if ($a eq '*');
	return @cods;
}

##-passed a string with possibly ambiguous codons, returns possible amino acids as an array
sub getaaa 
{
	my ($codonstring) = @_;	
	return if (!$codonstring);
	undef @cre;
	undef %pre;
	$refcodstr    = ".GCT.GCC.GCA.GCG.TGT.TGC.GAT.GAC.GAA.GAG";         # A, C, D, E
	$refcodstr   .= ".TTT.TTC.GGT.GGC.GGA.GGG.CAT.CAC.ATT.ATC.ATA";     # F, G, H, I
	$refcodstr   .= ".AAA.AAG.TTA.TTG.CTT.CTC.CTA.CTG.ATG.AAT.AAC";     # K, L, M, N
	$refcodstr   .= ".CCT.CCC.CCA.CCG.CAA.CAG.CGT.CGC.CGA.CGG.AGA.AGG"; # P, Q, R
	$refcodstr   .= ".TCT.TCC.TCA.TCG.AGT.AGC.ACT.ACC.ACA.ACG";		    # S, T
	$refcodstr   .= ".GTT.GTC.GTA.GTG.TGG.TAT.TAC.TAA.TAG.TGA";		    # V, W, Y, *
	unless ($codonstring eq undef)
	{
		$regcodon = regres($codonstring, 1);
		while ($refcodstr =~ /(?=$regcodon)/ig)
		{
			$red = (pos $refcodstr);
			$pre{$red} = "whack";
		}
		push @cre, ('A') if (exists $pre{1}   || exists $pre{5}   || exists $pre{9}   || exists $pre{13});
		push @cre, ('C') if (exists $pre{17}  || exists $pre{21}  );
		push @cre, ('D') if (exists $pre{25}  || exists $pre{29}  );
		push @cre, ('E') if (exists $pre{33}  || exists $pre{37}  );
		push @cre, ('F') if (exists $pre{41}  || exists $pre{45}  );
		push @cre, ('G') if (exists $pre{49}  || exists $pre{53}  || exists $pre{57}  || exists $pre{61});	
		push @cre, ('H') if (exists $pre{65}  || exists $pre{69}  );
		push @cre, ('I') if (exists $pre{73}  || exists $pre{77}  || exists $pre{81}  );	
		push @cre, ('K') if (exists $pre{85}  || exists $pre{89}  );
		push @cre, ('L') if (exists $pre{93}  || exists $pre{97}  || exists $pre{101} || exists $pre{105} || exists $pre{109} || exists $pre{113});
		push @cre, ('M') if (exists $pre{117} );
		push @cre, ('N') if (exists $pre{121} || exists $pre{125} );
		push @cre, ('P') if (exists $pre{129} || exists $pre{133} || exists $pre{137} || exists $pre{141} );	
		push @cre, ('Q') if (exists $pre{145} || exists $pre{149} );		
		push @cre, ('R') if (exists $pre{153} || exists $pre{157} || exists $pre{161} || exists $pre{165} || exists $pre{169} || exists $pre{173});
		push @cre, ('S') if (exists $pre{177} || exists $pre{181} || exists $pre{185} || exists $pre{189} || exists $pre{193} || exists $pre{197});
		push @cre, ('T') if (exists $pre{201} || exists $pre{205} || exists $pre{209} || exists $pre{213} );
		push @cre, ('V') if (exists $pre{217} || exists $pre{221} || exists $pre{225} || exists $pre{229} );
		push @cre, ('W') if (exists $pre{233} );
		push @cre, ('Y') if (exists $pre{237} || exists $pre{241} );
		push @cre, ('*') if (exists $pre{245} || exists $pre{249} || exists $pre{253} );	
	}
	return @cre;
}

##-returns codon optimization information - sets non local array variables to reflect the switch.
sub codopt
{
	my ($char, $swit) = @_;
	if ($swit == 0)
	{
		$x = "A";
		@A = (1, 3, 0, 2		);	@C = (1, 0,				);	@D = (1, 0,				);	@E = (1, 0				);	
		@F = (1, 0				);	@G = (1, 3, 0, 2		);  @H = (1, 0				);	@I = (1, 0, 2			);	
		@K = (1, 0				);	@L = (5, 1, 3, 2, 0, 4	);	@M = (0					);	@N = (1, 0				);	
		@P = (1, 3, 0, 2		);	@Q = (1, 0				);	@R = (1, 3, 5, 0, 2, 4	);	@S = (5, 1, 3, 0, 4, 2	);	
		@T = (1, 3, 0, 2		);	@V = (3, 1, 2, 0		);	@W = (0					);	@Y = (1, 0				);
		while ($x ne "Y")
		{
			push @$x, splice(@$x, rand(@$x-0), 1);
			$x++; $x++ if ($x eq "B" || $x eq "J" || $x eq "O" || $x eq "U" || $x eq "X");
		}
	}
	if ($swit == 1) #H sapiens
	{
		@A = (1, 3, 0, 2		);	@C = (1, 0,				);	@D = (1, 0,				);	@E = (1, 0				);	
		@F = (1, 0				);	@G = (1, 3, 0, 2		);  @H = (1, 0				);	@I = (1, 0, 2			);	
		@K = (1, 0				);	@L = (5, 1, 3, 2, 0, 4	);	@M = (0					);	@N = (1, 0				);	
		@P = (1, 3, 0, 2		);	@Q = (1, 0				);	@R = (1, 3, 5, 0, 2, 4	);	@S = (5, 1, 3, 0, 4, 2	);	
		@T = (1, 3, 0, 2		);	@V = (3, 1, 2, 0		);	@W = (0					);	@Y = (1, 0				);
	}
	if ($swit == 2) #S cerevisiae
	{
		@A = (0, 1, 2, 3		);	@C = (0, 1,				);	@D = (1, 0,				);	@E = (0, 1				);	
		@F = (1, 0				);	@G = (0, 1, 3, 2		);	@H = (1, 0				);	@I = (1, 0, 2			);	
		@K = (1, 0				);	@L = (1, 0, 4, 2, 5, 3	);	@M = (0					);	@N = (1, 0				);	
		@P = (2, 0, 1, 3		);	@Q = (0, 1				);	@R = (4, 0, 5, 1, 2, 3	);	@S = (0, 1, 5, 2, 4, 3	);	
		@T = (1, 0, 3, 2		);	@V = (0, 1, 3, 2		);	@W = (0					);	@Y = (1, 0				);
	}
	if ($swit == 3) #E coli
	{
		@A = (0, 2, 3, 1		);	@C = (1, 0,				);	@D = (1, 0,				);	@E = (0, 1				);	
		@F = (1, 0				);	@G = (0, 1, 3, 2		);	@H = (1, 0				);	@I = (1, 0, 2			);	
		@K = (0, 1				);	@L = (5, 3, 2, 1, 0, 4	);	@M = (0					);	@N = (1, 0				);	
		@P = (3, 2, 0, 1		);	@Q = (1, 0				);	@R = (0, 1, 2, 3, 4, 5	);	@S = (0, 1, 5, 4, 2, 3	);	
		@T = (1, 0, 3, 2		);	@V = (0, 2, 3, 1		);	@W = (0					);	@Y = (1, 0				);
	}
	if ($swit == 4) #M musculus
	{
		@A = (1, 0, 2, 3		);	@C = (1, 0,				);	@D = (1, 0,				);	@E = (1, 0				);	
		@F = (1, 0				);	@G = (1, 2, 3, 0		);  @H = (1, 0				);	@I = (1, 0, 2			);	
		@K = (1, 0				);	@L = (5, 3, 1, 2, 4, 0	);	@M = (0					);	@N = (1, 0				);	
		@P = (0, 1, 2, 3		);	@Q = (1, 0				);	@R = (5, 4, 3, 1, 2, 0	);	@S = (5, 1, 0, 4, 2, 3	);	
		@T = (1, 2, 0, 3		);	@V = (3, 1, 0, 2		);	@W = (0					);	@Y = (1, 0				);
	}
	if ($swit == 5) #C elegans
	{
		@A = (1, 0, 2, 3 		);	@C = (1, 0				);	@D = (1, 0,				);	@E = (1, 0				);	
		@F = (1, 0				);	@G = (2, 0, 1, 3		);	@H = (1, 0				);	@I = (1, 0, 2			);	
		@K = (1, 0				);	@L = (3, 2, 1, 5, 0, 4	);	@M = (0					);	@N = (1, 0				);	
		@P = (2, 0, 1, 3		);	@Q = (1, 0				);	@R = (0, 1, 4, 5, 2, 3	);	@S = (1, 0, 3, 2, 5, 4	);	
		@T = (1, 0, 2, 3		);	@V = (1, 0, 3, 2		);	@W = (0					);	@Y = (1, 0				);	
	}
	return @$char;
}

##-returns an array of stop positions for the nuc sequence and frame passed
sub stopfinder
{
	my ($strand, $frame) = @_;
	$frame = 1 if (!$frame);
	undef @answer;
	my $strandaa = translate($strand, $frame);
	while ($strandaa =~ /(?=\*)/ig)
	{
		my $sitsta = (pos $strandaa) +1;
		push @answer, $sitsta if ($sitsta != '');
	}
	return @answer;
}

##-returns an array of mashed up orflengths and start positions for the nucsequence and frame passed
sub orffinder
{
	my ($strand, $frame) = @_;
	$frame = 1 if (!$frame);
	undef @answer;
	my $strandaa = translate($strand, $frame);
	my @aa = split('', $strandaa);
	my $leng = length($strandaa);
	my $diff = length($stand) - ($leng/3);
	my $curpos = 0; my $orflength = 0; my $onnaorf = 0; my $orfstart = 0; 
	while ($curpos <= $leng)
	{
		if ($aa[$curpos] eq 'M' && $onnaorf eq '0')
		{
			$onnaorf = 1;
			$orfstart = $curpos;
		}
		if ($aa[$curpos] eq '*')
		{
			$onnaorf= 0;
			push @answer, ($orfstart+1 . 'V' . $orflength) if ($orflength >= .1*($leng));
			$orflength = 0;
		}
		if ($curpos == $leng && $onnaorf == 1)
		{
			$onnaorf = 0;
			push @answer, ($orfstart+1 . 'V' . 500) if ($orflength >= .1*($leng));
			$orflength = 0;
		}
		$curpos++;
		$orflength++ if ($onnaorf == 1);
	}
	return @answer;
}

##-passed a string of nucleotides, returns the complement (eg, TGC returns ACG) or reverse (TGC GCA).
sub complement
{
	my ($strand, $swit) = @_;
	return if (!$strand);
	$strand = cleanup($strand, 1);
	$strand = reverse($strand) if ($swit == 1);
	$strand =~ tr/ACGTRYKMSWBDHV/TGCAYRMKSWVHDB/;
	return $strand;
}

##-given a nucleotide sequence returns a different nucleotide sequence that codes for the
## same amino acids or returns the same sequence if impossible (ATG TGG).  swit 1 is completely random codon exchange.  
## swit 2 is to choose the most optimal codon that is not the current codon (nextopt).  swit 3 is to change the codon
## as much as possible - swap purines and pyrimidines. provide organism for nextopt.  
sub changeup
{
	my ($changer, $swit, $org, $shor) = @_;
	$swit = 1 if (!$swit); $org = 0 if (!$org);
	$sh1 = substr($shor, 0, 1) if  ($shor);
	$changer = cleanup($changer, 0);
	my $offset = 0; my $newcod = ''; my $changed = '';
	for ($b = 0; $b < (length($changer)/3); $b++)
	{
		$curcod = substr $changer, $offset, 3;
		$aachar = translate($curcod);
		@tarn = getcods(getaaa($curcod));
		@tre = codopt($aachar, $org);
		$newcod = $curcod;
		if ($aachar =~ /[MW\*]+/)
		{
			$newcod = $curcod;
		}
		elsif ($aachar =~ /[CDEFHKNQY]+/ || $swit == 1) #-take care of all codons on random, or just CDEFHKNQY if not random 
		{
			$newcod = $tarn[int(rand((@tarn-0)))] until ($curcod ne $newcod);
		}
		elsif ($aachar =~ /[AGPTVLRSI]+/ && $swit == 2) #-take care of everything else on nextopt
		{
			$r = 0;
			if ($shor)
			{
				until ($curcod ne $newcod && $newcod !~ $shor && substr($newcod, 2, 1) ne $sh1)
				{
					$newcod = $tarn[$tre[$r]];
					$r++;
				}
			}
			else
			{
				until ($curcod ne $newcod)
				{
					$newcod = $tarn[$tre[$r]];
					$r++;
				}	
			}
		}
		elsif ($aachar =~ /[AGPTVI]+/ && $swit == 3) #-take care of AGPTV and I
		{
			if ((substr $curcod, 2, 1) =~/[CT]+/)
			{
				$r=0;
				until ($newcod !~ regres('NNY'))
				{
					$newcod = $tarn[$tre[$r]];
					$r++;
				}
			}
			elsif ((substr $curcod, 2, 1)=~/[AG]+/)
			{
				$r=0;
				until ($newcod !~ regres('NNR'))
				{
					$newcod = $tarn[$tre[$r]];
					$r++;
				}			
			}
		}
		elsif ($aachar =~ /[LRS]+/ && $swit == 3) #-take care of LRS
		{
			$firpo = substr $curcod, 0, 1;
			$laspo = substr $curcod, 2, 1;
			$r = 0;
			if    ($aachar eq 'L' && $firpo eq 'T')
			{
				until (($firpo ne substr $newcod, 0, 1) && ($newcod !~ regres('NNR')))
				{
					$newcod = $tarn[$tre[$r]];
					$r++;
				}
			}
			elsif ($aachar eq 'R' && $firpo eq 'A')
			{
				until (($firpo ne substr $newcod, 0, 1) && ($newcod !~ regres('NNR')))
				{
					$newcod = $tarn[$tre[$r]];
					$r++;
				}
			}
			elsif ($aachar eq 'S' && $firpo eq 'A')
			{
				until (($firpo ne substr $newcod, 0, 1) && ($newcod !~ regres('NNY')))
				{
					$newcod = $tarn[$tre[$r]];
					$r++;
				}
			}
			else
			{
				until (($firpo ne substr $newcod, 0, 1) && $laspo ne substr $newcod, 2, 1)
				{
					$newcod = $tarn[$tre[$r]];
					$r++;
				}
			}
		}
		$changed .= $newcod;
		$offset += 3;
	}
	return $changed;
}

##-picks the most optimal codons from the codopt function for the organism provided.
sub optimize
{
	my ($seq, $org) = @_;
	$seq = cleanup($seq, 1);
	my $newseq = ''; my $offset = 0;
	for ($b = 0; $b < (length($seq)/3); $b++)
	{
		$curcod = substr $seq, $offset, 3;
		$aachar = translate($curcod);
		@tarn = getcods(getaaa($curcod));
		@tre = codopt($aachar, $org);
		$newcod = $tarn[$tre[0]];
		$newcod = $curcod if ($aachar eq '*');
		$newseq .= $newcod;
		$offset+=3;
	}
	return $newseq;
}

##-Given an organism number, returns a string containing the name.
sub organism
{
	my($org) = @_;
	return "(no organism defined)"	if ($org == 0);
	return "H. sapiens"		if ($org == 1);
	return "S. cerevisiae"	if ($org == 2);
	return "E. coli"		if ($org == 3);
	return "M. musculus"	if ($org == 4);
	return "C. elegans"		if ($org == 5);
}

##- straight from the user changes case, linebreaks, non nt/aa characters.  Returns a clean sequence
sub cleanup
{
	my ($seq, $swit) = @_;
	return if (!$seq);
	my $tro = $seq;
	#remove deflines
	if ($tro =~ /(>[\S\ ]*[\n\r]{1})/)
	{
			$remove = $1;
			$tro =~ s/$remove//;
	}
	$tro =~ tr/[a-z]/[A-Z]/;	#capitalize everything
	$tro =~ s/\n//g;			#remove unix breaks
	$tro =~ s/\r//g;			#remove mac breaks
	$tro =~ s/\W//g if ($swit == 1 || $swit == 0);			#removes nonlettercharacters
	$tro =~ s/\d//g;			#remove  digits
	$tro =~ s/\s//g;			#remove whitespace;
	if ($swit == 0)				#non-degenerative nucleotide editing
	{
		my @nonnt = qw(B D E F H I J K L M N O P Q R S U V W X Y Z);
		foreach $t (@nonnt)
		{
			$tro =~ s/$t//g;
		}
	}
	elsif ($swit == 1)				#nucleotide editing
	{
		my @nonnt = qw(E F I J L O P Q U X Z);
		foreach $t (@nonnt)
		{
			$tro =~ s/$t//g;
		}
	}
	elsif ($swit == 2)			#amino acid editing
	{
		my @nonaa = qw(B J O U X Z);
		foreach $t (@nonaa)
		{
			$tro =~ s/$t//g;
		}
	}
	return $tro;
}

##-generates a random sequence of requested length and base composition
sub randDNA
{
	my ($length, $ATperc, $stoppa) = @_;
	my @goarray = '';
	my $randbit = 0;
	my $randomDNA = '';
	$stoppa = 1 if (!$stoppa);
	
	$numAT = int(($ATperc/100) * $length)+.5;
	for ($x = 1; $x <= $numAT; $x++)
	{
		$randbit = int(rand(1)+.5);
		$goarray[$x] = 'A' if ($randbit == 1);
		$goarray[$x] = 'T' if ($randbit == 0);
	}
	for ($y = $numAT+1; $x <= $length; $x++)
	{
		$randbit = int(rand(1)+.5);
		$goarray[$x] = 'G' if ($randbit == 1);
		$goarray[$x] = 'C' if ($randbit == 0);
	}
	$x=0;
	while ($x != int(.05*$length) )
	{
		foreach (0..(@goarray-0))
		{
				push @goarray, splice(@goarray, rand(@goarray-0), 1);
		}
		$x++;
	}
	if ($stoppa == 2)
	{
		@ace = stopfinder(join("", @goarray), 1);
		until (@ace-0 == 0)
		{
			foreach (0..(@goarray-0))
			{
				push @goarray, splice(@goarray, rand(@goarray-0), 1);
			}
			@ace = stopfinder(join("", @goarray), 1);
		}
	}
	return join("", @goarray);
}

##-loads up all the cutter names we know from enzyme flat file or just one site, given the name
sub siteload
{
	my ($swit, $name) = @_;
	$swit = 1 if (!$swit);
	open (IN, "<newenz.txt")  || die "can't open enzyme list";
	undef @cutterarray;
	undef $lookslike;
	while (<IN>)
	{
		if ($swit == 2 && $_ =~ /^\Q$name\E\t(\S+)\t/)
		{
			$lookslike = $1; $lookslike =~ s/\W*\d*//g;
			last;
		}
		elsif ($swit == 1 && $_ =~ /^(\w+)\t(\S+)\t/)
		{
			push @cutterarray, $1;
		}
	}
	close IN;
	@cutterarray = sort @cutterarray;
	return @cutterarray if ($swit == 1);
	return $lookslike   if ($swit == 2);
}

##-given a enzyme gets sitelength from enzyme flatfile
sub sitelength
{
	my($name) = @_;
	$lensite = length(siteload(2, $name));
	return $lensite;
}
		
##-given a nucleotide sequence returns information on internal restriction sites
sub siterunner
{
	my($swit, $seq, %banned) = @_;
	my @siteabsents;
	my @siteuniques;
	my @sitepresent;
	my %cutter; my %cutter2;
	##-get cutter information loaded up
	open (IN, "<newenz.txt")  || die "can't open enzyme list";
	while(<IN>)
	{
		if ($_ =~ /^(\w*)\t(\S*)\t/)
		{
			$gotname = $1;  $gotsite = $2;
			$gotsite =~ s/\W*\d*//g;
			$cutter{$gotname} = $gotsite;
			$cutter2{$gotsite} = $gotname;
		}
	}
	close IN;
	##-check the sequence for each site
	foreach $curr (sort values %cutter)
	{
		$snip = length($curr);
		$exp  = regres($curr, 1);
		$name = $cutter2{$curr};
		while ($seq =~ /(?=$exp)/ig)
		{
			$sitsta = (pos $seq) +1;
			push @$name, $sitsta;
		}
		if ($curr ne complement($curr, 1))
		{
			$icurr = complement($curr, 1);
			$exp   = regres($icurr, 1);
			while ($seq =~ /(?=$exp)/ig)
			{
				$sitsta = (pos $seq) +1;
				push @$name, $sitsta;
			}
		}
		unless (exists $banned{$name})
		{
			push @siteabsents, $name if ((@$name-0) == 0);
		}
		push @siteuniques, $name if ((@$name-0) == 1);
		push @sitepresent, $name if ((@$name-0)  > 0);
		undef @$name;
	}
	##-sort out what to return to the user - switch 1 = absents, switch 2 = uniques
	return @siteabsents if ($swit == 1);
	return @siteuniques if ($swit == 2);
	return @sitepresent if ($swit == 3);
}

##-given a nucleotide sequence and a sitename or small sequence returns an array of that site (or sequence)'s  positions
sub siteseeker
{
	my ($pass, $seq, $swit) = @_;
	$swit = 1 if (!$swit);
	return if (!$pass);
	my $site = $pass;
	undef @answer;
	$site = siteload(2, $pass) if ($swit == 1);
	my $snip = length($site);
	my $exp  = regres($site, 1);
	while ($seq =~ /(?=$exp)/ig)
	{
		my $sitsta = (pos $seq) +1;
		push @answer, $sitsta if ($sitsta != '');
	}
	if ($site ne complement($site, 1) && $swit == 1)
	{
		$isite = complement($site, 1);
		$exp   = regres($isite, 1);
		while ($seq =~ /(?=$exp)/ig)
		{
			$sitsta = (pos $seq) +1;
			push @answer, $sitsta if ($sitsta != '');
		}
	}
	return @answer;
}


##-passed a string that may contain ambiguities, returns a string that can be used for 
##-regular expression searching, for restriction enzyme sites etc.
sub regres
{
	my ($strand, $swit) = @_;
	$swit = 1 if (!$swit);
	return if (!$strand);
	$strand = cleanup($strand, $swit);
	@stran = split('', $strand);
	$comp = undef;
	if ($swit == 1 || (!$swit)) #nucleotide regexping
	{
		foreach $n (@stran)
		{
			$comp .= $n       if ($n eq 'T' || $n eq 'A' || $n eq 'G' || $n eq 'C');
			$comp .= "[AGR]"   if ($n eq 'R');
			$comp .= "[CTY]"   if ($n eq 'Y');
			$comp .= "[GTK]"   if ($n eq 'K');
			$comp .= "[ACM]"   if ($n eq 'M');
			$comp .= "[GCS]"   if ($n eq 'S');
			$comp .= "[ATW]"   if ($n eq 'W');
			$comp .= "[CGTBKYS]"  if ($n eq 'B');
			$comp .= "[AGTDRWK]"  if ($n eq 'D');
			$comp .= "[ACTHYMW]"  if ($n eq 'H');
			$comp .= "[ACGVRMS]"  if ($n eq 'V');
			$comp .= "[ATCGNRYBDHVKMSW]" if ($n eq 'N');
		}
	}
	elsif ($swit == 2) #aa regexping
	{
		foreach $n (@stran)
		{
			$comp .= $n if ($n ne '*');
			$comp .= "[\*]" if ($n eq '*');
		}
	}
	return $comp;
}

##-passed a reference to a hash of used sites adds to it all mutually exclusive sites - that is, if you are using .
##-ATTAAT already you don't want to consider TTAA.  This function removes TTAA from consideration.
sub mutexclu
{
	my ($ref, $swit) = @_;
	return if (!$ref);
	my %usedhash = %$ref; my %wholelist;
	open (IN, "<newenz.txt")  || die "can't open enzyme list";
	while(<IN>)
	{
		if ($_ =~ /^(\w*)\t(\S*)\t/)
		{
			$gotname = $1;  $gotsite = $2;
			$gotsite =~ s/\W*\d*//g;
			$wholelist{$gotname} = $gotsite;
		}
	}
	close IN;
	foreach $c (sort keys %usedhash)
	{
		if ($usedhash{$c} != -2) #don't want second degree exclusion - only exclude if it's not a -2 site
		{
			my $te = regres($usedhash{$c});
			foreach $d (sort keys %wholelist)
			{
				if ($c ne $d)
				{
					my $ue = regres($wholelist{$d});
					$usedhash{$d} = -2 if ($usedhash{$c} =~ $ue || $wholelist{$d} =~ $te);
				}
			}
		}
	}
	return %usedhash;
}