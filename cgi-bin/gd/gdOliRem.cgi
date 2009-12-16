#!/usr/bin/perl
use strict;
use warnings;
use GeneDesign;
use GeneDesignML;
use CGI;

my $query = new CGI;
print $query->header;

my $CODON_TABLE	 = define_codon_table(1);
my $RE_DATA = define_sites($enzfile);

my @styles = qw(re);
my @nexts  = qw(SSIns SSRem SeqAna OligoDesign);
my $nextsteps = next_stepper(\@nexts, 5);

gdheader("Short Sequence Removal", "gdOliRem.cgi", \@styles);

if (! $query->param('REMSEQ'))
{
	my $orgchoice = organism_selecter();
	my $nucseq = $query->param('PASSNUCSEQUENCE')	?	$query->param('PASSNUCSEQUENCE')	:	$query->param('nucseq');
	$nucseq = $nucseq	?	$nucseq	:	"";
	my $readonly = ! $nucseq ?	" "	:	'readonly = "true"';
print <<EOM;
				<div id="notes">
					<strong>To use this module you need two nucleotide sequences, large and small.  An organism name is optional.</strong><br>
					Your nucleotide sequence will be searched for the short sequence you provide and as many iterations as possible will 
					be removed by changing whole codons without changing the amino acid sequence.<br><em>Please Note:</em><br>
					&nbsp;&nbsp;&bull;If you select an organism, targeted codons will be replaced with the codon that has the closest RSCU value in that organism.<br>
					&nbsp;&nbsp;&bull;If you select no optimization, targeted codons will be replaced with a random codon.<br>
					See the <a href="$docpath/Guide/shortr.html" target="blank">manual</a> for more information.
				</div>
				<div id="gridgroup0">
					Your nucleotide sequence:<br>
					<textarea name="nuseq"  rows="6" cols="100" $readonly>$nucseq</textarea><br>
					$orgchoice<br><br>
					Sequence to Remove <input type="text" name="REMSEQ" cols="20"><br><br>
					Number of Iterations to attempt <input type="text" name="ITER" size="5" value="3" maxlength="3"><br><br>
					<div id="gridgroup1" align ="center" style="position:absolute; top:240; ">
						<input type="submit" name=".submit" value=" Remove short sequences " />
					</div>
				</div>
EOM
	closer();
}

else
{
	if (! $query->param('nuseq'))
	{
		take_exception("You need a nucleotide sequence.<br>");
		exit;
	}
	if (length($query->param('REMSEQ')) < 2)
	{
		take_exception("You need a short sequence to be removed (at least two bp) <br> ");
		exit;
	}
	if (length($query->param('REMSEQ')) >= length($query->param('nuseq')))
	{
		take_exception("Your short sequence should be shorter than your nucleotide sequence.<br>\n");
		exit;
	}
	
	my $iter = $query->param('ITER');
	my $nucseq = $query->param('PASSNUCSEQUENCE')	?	$query->param('PASSNUCSEQUENCE')	:	cleanup($query->param('nuseq'));
	my $org = $query->param('MODORG');
	my @war2 = pattern_finder($nucseq, "*", 2, 1, $CODON_TABLE);
	my $war3 = 1 if (@war2 && ((scalar(@war2) > 1 ) || (($war2[0] + 1) != length(translate($nucseq, 1, $CODON_TABLE)))));
	if ((substr($nucseq, 0, 3) ne 'ATG' || $war3) && $nucseq)
	{
print <<EOM;
				<div id = "warn">
					<strong>Warning:</strong> Your sequence is not a simple coding sequence.<br>
					Either your sequence does not begin with ATG or your sequence has at least one internal stop codon in the first frame.<br>
					It is still possible to manipulate this sequence but you should check to be sure that crucial features are not compromised.
				</div>
EOM
	}
	my $remseq = cleanup($query->param('REMSEQ'), 0);
	my $arr = [ regres($remseq, 1) ];
	my $oldnuc = $nucseq;
	my $newnuc = $oldnuc;
	my $temphash = siteseeker($newnuc, $remseq, $arr);
	my $starnum = scalar(keys %$temphash);
	for my $one (1..$iter)
	{
		$temphash = siteseeker($newnuc, $remseq, $arr);
		foreach my $grabbedpos (keys %$temphash)
		{
			my $grabbedseq = $$temphash{$grabbedpos};
			my $framestart = ($grabbedpos) % 3;
			my $critseg = substr($newnuc, $grabbedpos - $framestart, ((int(length($grabbedseq)/3 + 2))*3));
			my $newcritseg = pattern_remover($critseg, $remseq, $CODON_TABLE, define_RSCU_values($org)) || $critseg;
#			print "$one $grabbedpos $$temphash{$grabbedpos} $critseg, $newcritseg<br>";
			substr($newnuc, $grabbedpos - $framestart, length($newcritseg)) = $newcritseg;# if (scalar( keys %{siteseeker($newcritseg, $remseq, $arr)}) == 0);
		}	
	}
	$temphash = siteseeker($newnuc, $remseq, $arr);
	my $results;
	if (scalar(keys %$temphash))
	{
		$results .= "But after $iter iterations, I couldn't remove " . scalar(keys %$temphash) . " instances of it.\n";
		$results .= "You might try again from the top with this sequence and random codon replacement.<br>";
	}
	else
	{
		$results .= "All instances of $remseq were removed.<br>\n";
	}
	if (translate($oldnuc, 1, $CODON_TABLE) ne translate($newnuc, 1, $CODON_TABLE))
	{
		$results .= "The translation has been changed!<br>\n";
	}
	my $newal = compare_sequences($oldnuc, $newnuc);
	my $bcou = count($nucseq); 
	my $hiddenstring = hidden_fielder({"MODORG" => $org});
print <<EOM;
				<div id="notes">
					I was asked to remove $starnum occurences of the sequence $remseq.<br>
					$results
				</div>
				<div id="gridgroup0">
					Your altered nucleotide sequence:
					<textarea name="PASSNUCSEQUENCE"  rows="6" cols="120">$newnuc</textarea><br>
					&nbsp;_Base Count  : $$bcou{length} bp ($$bcou{A} A, $$bcou{T} T, $$bcou{C} C, $$bcou{G} G)<br>
					&nbsp;_Composition : $$bcou{GCp}% GC, $$bcou{ATp}% AT<br>
					$$newal{'I'} Identites, $$newal{'D'} Changes ($$newal{'T'} transitions $$newal{'V'} transversions), $$newal{'P'}% Identity<br><br><br>
					$nextsteps
				</div>
				$hiddenstring
EOM
	closer();
}