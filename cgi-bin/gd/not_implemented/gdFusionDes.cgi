#!/usr/bin/perl
#use warnings;
#use strict;
use CGI;
use PML;
use GeneDesign;

$query = new CGI;
print $query->header;
%CODON_TABLE = define_codon_table(1);
%REV_CODON_TABLE = define_reverse_codon_table(\%CODON_TABLE);
$allaa = "ACDEFGHIKLMNPQRSTVWY";

my @styles = qw(re);
gdheader("Site Directed Mutagenesis by PCR", "gdFusiondes.cgi", \@styles);
	
if ($query->param('TARMUT') eq '' && $query->param('MUTMETHOD') eq '')
{
	$nucseq = $query->param('passnucseq') if ($query->param('passnucseq') ne '');
	$nucseq = $query->param('nucseq') if ($query->param('passnucseq') eq '');
	
print <<EOM;
				<div id="notes">
					<strong>To use this module you need a nucleotide sequence at least 200bp long, nucleotide bases or a residue for mutation, a model organism, and a melting temperature.</strong><br>
					For this step you will define the sequences to be mutated; on the following screens you will decide the method of mutation and the primer design.<br>
					If you wish to change a residue (a codon in a coding sequence), select the residue option.<br>
					If you wish to change a sequence of bases regardless of coding status, select the nucleotides option.<br>
					<em>Please Note:</em><br>
					&nbsp;&nbsp;&bull;Format for residue mutation is amino acid one letter code followed by the residue coordinate: K35 means the thirty-fifth amino acid, which is a lysine.<br>
					&nbsp;&nbsp;&bull;Format for nucleotide mutation is the nucleotide sequence followed by the coordinate of the first base: ATTG27, for example.<br>
					See the <a href="../../gd2/Guide/Fusiondes.html" target="blank">manual</a> for more information.
				</div>
				<div id="gridgroup0">
					Your nucleotide sequence:<br>
					<textarea name="WHOLESEQ"  rows="6" cols="100" default="$nucseq"></textarea><br>
					Kind of mutation: 
					<input type="radio" name="MUTKIND" value="1">Single Residue
					<input type="radio" name="MUTKIND" value="2">Nucleotides<br>
					Residue or Nucleotides to mutate: <input type="text" name="TARMUT" size="11" maxlength="10" /><br><br>
					<div id="gridgroup1" align ="center" style="position:absolute; top:250; ">
						<input type="submit" name=".submit" value=" Next Step " />
					</div>
				</div>
EOM
	closer();
}

elsif($query->param('WHOLESEQ') ne '' && $query->param('TAROLIMEL') eq '')
{
	$mut_kind  = $query->param('MUTKIND');
	$wholeseq  = $query->param('WHOLESEQ');	
	$wholeseq =~ tr/atcg/ATCG/;		
	$wholeseq =~ s/\n//g;			#remove unix breaks
	$wholeseq =~ s/\r//g;			#remove mac breaks		
	$wholeseq =~ s/\s//g;
	$trans_seq = translate($wholeseq, 1, \%CODON_TABLE);
	$tar_mut  = $query->param('TARMUT');
	$tar_mut_cor = $1 if ($tar_mut =~ /([0-9]+)/);
	$tar_mut_res = substr($tar_mut, 0, 1) if ($mut_kind == 1);
	$tar_mut_res = $1 if ($tar_mut =~ /([A-Za-z]+)/ && $mut_kind == 2);
	my @error;
## PRE ERROR CHECKING
	if (length($wholeseq) < 200)
	{
		push @error, "\t\t\t\t\tYour sequence mutation input is too small for this program, which does not include the error checking necessary to ensure that your amplification primers are not disrupted by the mutations you introduce.<br>\nIf desire is expressed for this kind of error checking, this feature will be added.<br>\n";
	}
	if ($mut_kind == 1 && $tar_mut !~ /[ACDEFGHIKLMNPQRSTVWY][0-9]+/)
	{
		push @error, "\t\t\t\t\tYour residue mutation input $tar_mut_res contains a character not recognized as a residue, or is more than one residue long.<br>";
	}
	if ($mut_kind == 1 && $tar_mut_cor - 1 > length($trans_seq))
	{
		push @error, "\t\t\t\t\tYour residue mutation position $tar_mut_cor is beyond the length of the translated sequence.<br>";
	}
	if ($mut_kind == 1 && substr($trans_seq, $tar_mut_cor - 1, 1) ne $tar_mut_res)
	{
		push @error, "\t\t\t\t\tYour residue mutation input $tar_mut_res cannot be found in the translated sequence at coordinate $tar_mut_cor.<br>\n";
	}
	if ($mut_kind == 2 && $tar_mut !~ /[ATCG]+[0-9]+/)
	{
		push @error, "\t\t\t\t\tYour nucleotide mutation input $tar_mut_res contains a character not recognized as a nucleotide.<br>\n";
	}
	if ($mut_kind == 2 && $tar_mut_cor - 1 > length($wholeseq))
	{
		push @error, "\t\t\t\t\tYour nucleotide mutation position $tar_mut_cor is beyond the length of the nucleotide sequence.<br>";
	}
	if ($mut_kind == 2 && substr($wholeseq, $tar_mut_cor - 1, length($tar_mut_res)) ne $tar_mut_res)
	{
		push @error, "\t\t\t\t\tYour nucleotide mutation input $tar_mut_res cannot be found in the sequence at coordinate $tar_mut_cor.<br>\n";
	}
	if (@error-0 != 0)
	{
print <<EOM;
				<div id="notes">
					@error
					<br><br><input type="button" value="Back" onClick="history.go(-1)">
				</div>
EOM
		closer();
	}
	else
	{
print <<EOM;
				<div id="notes">
					<strong>Now you will decide how the residue will be mutated.</strong><br>
					Two kinds of primers will be created, using the target Tm you define.<br>
					Flanking Primers will be created from the 5&rsquo; and 3&rsquo; ends of the original sequence.<br>
					Mutation Primers will have the mutation in the center and will be directed to the 5&rsquo; and 3&rsquo; flanking primers.<br>
					<em>Please Note:</em><br>
					&nbsp;&nbsp;&bull;The model organism will be used to determine which synonymous codon bias to use for mutation.  Select &quot;None&quot; for random codon replacement; 
					otherwise the most optimal codon for expression in that organism will be used.<br>
					&nbsp;&nbsp;&bull;If you wish to direct mutagenesis to a number of residues, simply enter them all as single letter codes without spaces; a set of primers will be generated for each. 
					To include a deletion, use the single letter code &quot;X&quot;<br>
					&nbsp;&nbsp;&bull;The designation tag will be prepended to each oligo name to help you identify oligos when you place your order.<br>
					See the <a href="../../gd2/Guide/Fusiondes.html" target="blank">manual</a> for more information.
				</div>
				<div id="gridgroup0">
					Your nucleotide sequence:<br>
					<textarea name="WHOLESEQ"  rows="5" cols="100" readonly="yes">$wholeseq</textarea><br><br>
					Translated:<br>
					<textarea name="TRANSSEQ"  rows="5" cols="100" readonly="yes">$trans_seq</textarea><br><br>
					Model organism:
					 <select name="TARMODORG" >
						<option value="0">No model organism</option>
						<option value="3">H. sapiens</option>
						<option value="2">E. coli</option>
						<option value="1"selected="selected" >S. cerevisiae</option>
						<option value="4">C. elegans</option>
					</select><br><br>
					Mutation:<br>
					<input type="radio" name="MUTMETHOD" value="1" checked>Specific residues&nbsp;&nbsp;&nbsp;&nbsp;
					(Change $tar_mut_res at position $tar_mut_cor to <input type="text" name="NEWRES" size="20" maxlength="20">)<br>
					<input type="radio" name="MUTMETHOD" value="2" checked>Whole shebang&nbsp;&nbsp;&nbsp;&nbsp;
					(Change $tar_mut_res to each other amino acid at position $tar_mut_cor)<br>
					<input type="radio" name="MUTMETHOD" value="3">Deletion&nbsp;&nbsp;&nbsp;&nbsp;
					(Delete $tar_mut_res from position $tar_mut_cor)<br><br>
					Designation tag for these primers: <input type="text" name="OLIDES" size="50" maxlength="50" /><br>
					Return  primers of Tm: <input type="text" name="TAROLIMEL" value="56" size="2" maxlength="2" />&deg;&nbsp;&nbsp;
					within ± <input type="text" name="OLIMELTOL" value="1.0" size="3" maxlength="3" />&deg;<br>
					Melting Temperature Determination by :
					<select name="MELTFORM">
						<option value="1">Simple</option>
						<option value="2">DNA Strider, after Baldwin et al (PMID 2725322)</option>
						<option value="3"selected="selected" >Primer3, after Sambrook et al (www.MolecularCloning.com)</option>
						<option value="4">Nearest Neighbor Thermodynamics (PMIDs 4427357 and 2243783)</option>
						<option value="6">Average of DNA Strider, Primer3, and Nearest Neighbor</option>
					</select><br><br><br>
					<div id="gridgroup1" align ="center" style="position:absolute; top:410; ">
						<input type="submit" name=".submit" value=" Make Primers " />
						<input type="hidden" name="TARMUTRES" value="$tar_mut_res">
						<input type="hidden" name="TARMUTCOR" value="$tar_mut_cor">
					</div>
				</div>
EOM
		closer();
	}
}

else
{
print <<EOM;
				<div id="notes">
					<strong>Here are your primers.</strong><br>
					<em>Please Note:</em><br>
					&nbsp;&nbsp;&bull;Melting Temperatures may appear to be out of your specified range; this is because they are being rounded to the nearest integer.<br>
					&nbsp;&nbsp;&bull;s primers are sense; a primers are antisense.<br>  				
					See the <a href="../../gd2/Guide/Fusiondes.html" target="blank">manual</a> for more information.
				</div>
				<div id="gridgroup0">
EOM
	$wholeseq    = $query->param('WHOLESEQ');	
	$transseq    = $query->param('TRANSSEQ');
	$tar_mut_res = $query->param('TARMUTRES');
	$tar_mut_cor = $query->param('TARMUTCOR');
	$tar_mod_org = $query->param('TARMODORG');
	$mut_meth    = $query->param('MUTMETHOD');
	$new_res     = $query->param('NEWRES');
	$oli_des     = $query->param('OLIDES');
	$mform       = $query->param('MELTFORM');								#default is 3, or primer3
	$tar_oli_mel = $query->param(-name=>'TAROLIMEL');						#default is 56˚
	$oli_mel_tol = $query->param(-name=>'OLIMELTOL');						#default is 1.0˚
	
	my %AMPprimers;	my %AMPprimersmelt; my %AMPprimersleng;
	my %MUTprimers;	my %MUTprimersmelt; my %MUTprimersleng;
	$oli_des .= "." if ($oli_des ne '');
	%RSCU_VALUES = define_RSCU_values($tar_mod_org);
	my $rampprimer;	my $lampprimer;
	my $start = 1;		my $end = length($wholeseq) - 1;
	while (melt($lampprimer, $mform) < ($tar_oli_mel - $oli_mel_tol))	{	$start++;	$lampprimer = substr($wholeseq, 0, $start);	}
	while (melt($rampprimer, $mform) < ($tar_oli_mel - $oli_mel_tol))	{	$end--;		$rampprimer = substr($wholeseq, $end);		}
	$AMPprimers{"sense"} = $lampprimer;					$AMPprimersmelt{"sense"} = int(melt($lampprimer, $mform) + .5);					$AMPprimersleng{"sense"} = length($lampprimer);
	$AMPprimers{"antisense"} = complement($rampprimer, 1);	$AMPprimersmelt{"antisense"} = int(melt(complement($rampprimer, 1), $mform) + .5);	$AMPprimersleng{"antisense"} = length($rampprimer);

	my @newresidues;
	if		($mut_meth == 1)	{	@newresidues = split('', $new_res);	}
	elsif	($mut_meth == 2)	{	$mostaa = $allaa; $mostaa =~ s/$tar_mut_res//;	@newresidues = split('', $mostaa);	}
	elsif	($mut_meth == 3)	{	@newresidues = ('X');	}
	foreach my $tiv (@newresidues)
	{
		my $primer = '';
		my $primerfodder = $wholeseq;
		my $workcods = $REV_CODON_TABLE{$tiv};	
		my $new_codon = '';	my $myrscu = 0;
		if ($mut_meth != 3)	{	foreach my $l (@$workcods)	{	if ($RSCU_VALUES{$l} > $myrscu)	{	$new_codon = $l;	$myrscu = $RSCU_VALUES{$l};	}	}	}
		substr($primerfodder, $tar_mut_cor * 3 - 3, 3) = $new_codon;
		my $start = $tar_mut_cor*3 - 4;		my $length = 5;
		while(melt($primer, $mform) < ($tar_oli_mel - $tar_mel_tol))	{	$start--;	$length+=2;		$primer = substr($primerfodder, $start, $length);	}
		if (melt($primer, $mform) > ($tar_oli_mel - $tar_mel_tol))	{	$length--;	$primer = substr($primerfodder, $start, $length);	}
		my $key = $tar_mut_res . $tar_mut_cor . $tiv;
		$MUTprimers{$key . '.s'} = $primer;					$MUTprimersmelt{$key . '.s'} = int(melt($primer, $mform) + .5);					$MUTprimersleng{$key . '.s'} = length($primer);
		$MUTprimers{$key . '.a'} = complement($primer, 1);	$MUTprimersmelt{$key . '.a'} = int(melt(complement($primer, 1), $mform) + .5);	$MUTprimersleng{$key . '.a'} = length($primer);
	}
print <<EOM;
					Amplification (flanking) primers<br>
					<table style="font-family: Courier, monospace; font-size: 14;">
						<tr>
							<td>&nbsp;&nbsp;Designation&nbsp;&nbsp;&nbsp;&nbsp;</td>
							<td>&nbsp;&nbsp;Sequence 5&rsquo;-3&rsquo;</td>
							<td>Tm</td>
							<td>bp</td>
						</tr>
EOM
	foreach $tiv (sort keys %AMPprimers)
	{
print <<EOM
						<tr>
							<td>$oli_des$tiv</td>
							<td>$AMPprimers{$tiv}</td>
							<td>$AMPprimersmelt{$tiv}</td>
							<td>$AMPprimersleng{$tiv}</td>
						</tr>
EOM
	}
print <<EOM;
					</table><br><br>
					Mutation primers<br>
					<table style="font-family: Courier, monospace; font-size: 14;">
						<tr>
							<td>&nbsp;&nbsp;Designation&nbsp;&nbsp;&nbsp;&nbsp;</td>
							<td>&nbsp;&nbsp;Sequence 5&rsquo;-3&rsquo;</td>
							<td>Tm</td>
						</tr>
EOM
	foreach $tiv (sort keys %MUTprimers)
	{
print <<EOM;
						<tr>
							<td>$oli_des$tiv</td>
							<td>$MUTprimers{$tiv}</td>
							<td>$MUTprimersmelt{$tiv}</td>
							<td>$MUTprimersleng{$tiv}</td>
						</tr>
EOM
	}
print <<EOM;
					</table><br><br>
				</div>
EOM
	closer();
}