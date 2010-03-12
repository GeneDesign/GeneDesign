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
my @nexts  = qw(SSIns SSRem SeqAna REBB UserBB OlBB);
my $nextsteps = next_stepper(\@nexts, 5);
my $iter = 3;

gdheader("Restriction Site Subtraction", "gdSSRem.cgi", \@styles);

if (! $query->param('MODORG'))
{
	my $orgchoice = organism_selecter();
	my $nucseq = $query->param('PASSNUCSEQUENCE')	?	$query->param('PASSNUCSEQUENCE')	:	$query->param('nucseq');
	$nucseq = $nucseq	?	$nucseq	:	"";
	my $readonly = ! $nucseq ?	" "	:	'readonly = "true"';
print <<EOM;
				<div id="notes">
					<strong>To use this module you need a nucleotide sequence.  An organism name is optional.</strong><br>
					Your nucleotide sequence will be searched for restriction sites and you will be prompted to choose as many as you want for removal.<br>
					Sites will be removed without changing the amino acid sequence by changing whole codons.<br><em>Please Note:</em><br>
					&nbsp;&nbsp;&bull;If you select an organism, targeted codons will be replaced with the codon that has the closest RSCU value in that organism.<br>
					&nbsp;&nbsp;&bull;If you select no optimization, targeted codons will be replaced with a random codon.<br>
					See the <a href="$linkpath/Guide/ssr.html" target="blank">manual</a> for more information.
				</div>
				<div id="gridgroup0">
					Your nucleotide sequence:<br>
					<textarea name="nuseq"  rows="6" cols="100" $readonly>$nucseq</textarea><br>
					$orgchoice
					<div id="gridgroup1" align ="center" style="position:absolute; top:150; ">
						<input type="submit" name=".submit" value=" Next Step: which sites are present? " />
					</div>
				</div>
EOM
	closer();
}

elsif ($query->param('MODORG') && ! $query->param('removeme'))
{
	my $nucseq = $query->param('PASSNUCSEQUENCE')	?	$query->param('PASSNUCSEQUENCE')	:	cleanup($query->param('nuseq'));
	my $organism = $query->param('MODORG');
	my $SITE_STATUS = define_site_status($nucseq, $$RE_DATA{REGEX});
	my @presents = grep {$$SITE_STATUS{$_} > 0}	sort keys %{$$RE_DATA{CLEAN}};
	my ($curpos, $i, $xpos, $ypos) = (0, 0, 0, 0);
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
print <<EOM;
				<div id="notes">
					Below are your nucleotide sequence and all of the restriction sites that I recognized. Your current organism is $ORGANISMS{$organism}.<br>
					Check as many as you like for removal.<br>
					See the <a href="$linkpath/Guide/ssr.html" target="blank">manual</a> for more information.
				</div>
				<div id="gridgroup0">
					This is your nucleotide sequence:<br>
					<textarea name="nucseq"  rows="6" cols="120" readonly="true">$nucseq</textarea><br><br>
					Present Restriction Sites:<br>
					<div id="gridgroup2" style = "position:relative">
EOM
	for (0..int(scalar(@presents)/10))
	{
		while ($curpos != 10 && $i < scalar(@presents))
		{
			my $count = scalar(keys %{siteseeker($nucseq, $presents[$i], $$RE_DATA{REGEX}->{$presents[$i]})});
print <<EOM;
						<span id = "brubox" style = "top:$ypos; left:$xpos;">
							<input type="checkbox" name="removeme" value="$presents[$i]">
							<a href="http://rebase.neb.com/rebase/enz/$presents[$i].html" target="blank">$presents[$i]</a>($count)
						</span>
EOM
			($curpos, $i, $xpos) = ($curpos+1, $i+1, $xpos+95);
		}
		($curpos, $ypos, $xpos) = (0, $ypos+20, 0);
	}
print <<EOM;
					</div>
					<div style = "position:relative;top:400">
						<input type="hidden" name="MODORG" value="1"/>
						<input type="submit" name=".submit" value=" Next Step: Remove these sites "/>
					</div>
				</div>
EOM
	closer();
}

else
{
	my ($Error4, $Error0) = (" ", "" );
	my $org = $query->param('MODORG');
	my $oldnuc = cleanup($query->param('nucseq'), 0);
	my $newnuc = $oldnuc;
	my @removes = $query->param('removeme');
	for (1..$iter)
	{
		foreach my $enz (@removes)
		{	
			my $temphash = siteseeker($newnuc, $enz, $$RE_DATA{REGEX}->{$enz});
			foreach my $grabbedpos (keys %$temphash)
			{
				my $grabbedseq = $$temphash{$grabbedpos};
				my $framestart = ($grabbedpos) % 3;
				my $critseg = substr($newnuc, $grabbedpos - $framestart, ((int(length($grabbedseq)/3 + 2))*3));
				my $newcritseg = pattern_remover($critseg, $$RE_DATA{CLEAN}->{$enz}, $CODON_TABLE, define_RSCU_values($org));
#				print "$grabbedpos $$temphash{$grabbedpos} $critseg, $newcritseg<br>";
				substr($newnuc, $grabbedpos - $framestart, length($newcritseg)) = $newcritseg if (scalar( keys %{siteseeker($newcritseg, $enz, $$RE_DATA{REGEX}->{$enz})}) == 0);
			}
		}
	}
	foreach my $enz (@removes)
	{
		my $checkpres = siteseeker($newnuc, $enz, $$RE_DATA{REGEX}->{$enz});
		$Error4 .= "&nbsp;I was unable to remove $enz after $iter iterations.<br>\n" . tab(5) if (scalar(keys %$checkpres) != 0);
		$Error0 .= "&nbsp;&nbsp;I successfully removed $enz from your sequence.<br>\n" . tab(5) if (scalar (keys %$checkpres) == 0);
	}
	my $newal = compare_sequences($oldnuc, $newnuc);
	my $bcou = count($newnuc); 
	my $newhsh = {">Your edited sequence" => $newnuc};
	my $FASTAoff = offer_fasta(fasta_writer($newhsh));
	my $hiddenstring = hidden_fielder({"MODORG" => $org});
print <<EOM;
				<div id="notes">
					I was asked to remove: @removes.<br>
					$Error0
					$Error4
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
			</form>
			<br><br><br>
			$FASTAoff
EOM
	closer();
}