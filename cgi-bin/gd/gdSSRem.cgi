#!/usr/bin/perl
use strict;
use warnings;
use GeneDesign;
use GeneDesignML;
use Perl6::Slurp;
use CGI;
use File::Path qw(remove_tree);

my $query = new CGI;
print $query->header;

my $CODON_TABLE	 = define_codon_table(1);
my $RE_DATA = define_sites($enzfile);

my @styles = qw(re);
my @nexts  = qw(SSIns SSRem SeqAna REBB UserBB OlBB);
my $nextsteps = next_stepper(\@nexts, 5);
my $iter = 3;

gdheader("Restriction Site Subtraction", "gdSSRem.cgi", \@styles);
$ORGANISMS{7} = "no organism";

if (! $query->param('MODORG'))
{
	my $orgchoice = organism_selecter_none();
	my $nucseq = $query->param('PASSNUCSEQUENCE')	?	$query->param('PASSNUCSEQUENCE')	:	$query->param('nuseq');
	$nucseq = $nucseq	?	$nucseq	:	"";
	my $readonly = ! $nucseq ?	" "	:	'readonly = "true"';
print <<EOM;
				<div id="notes">
					<strong>To use this module you need a nucleotide sequence.  An organism name is optional.</strong><br>
					Your nucleotide sequence will be searched for restriction sites and you will be prompted to choose as many as you want for removal.<br>
					Sites will be removed without changing the amino acid sequence by changing whole codons.<br><em>Please Note:</em><br>
					&nbsp;&nbsp;&bull;If you select an organism, targeted codons will be replaced with the codon that has the closest RSCU value in that organism.<br>
					&nbsp;&nbsp;&bull;If you select no organism, targeted codons will be replaced with a random codon.<br>
					See the <a href="$linkpath/Guide/ssr.html" target="blank">manual</a> for more information.
				</div>
				<div id="gridgroup0">
					Your nucleotide sequence:<br>
					<textarea name="nuseq"  rows="6" cols="100" $readonly>$nucseq</textarea><br><br>
					$orgchoice<br><br>
					Enter positions to lock: (Optional)<br>
					<input type="text" name="LOCK" cols="20"><br>
					<div id="gridgroup1" align ="center" style="position:absolute; top:250; ">
						<input type="submit" name=".submit" value=" Next Step: which sites are present? " />
					</div>
				</div>
EOM
	closer();
}

elsif ($query->param('MODORG') && ! $query->param('removeme'))
{
	my $nucseq = $query->param('PASSNUCSEQUENCE')	?	$query->param('PASSNUCSEQUENCE')	:	cleanup($query->param('nuseq'));
	my $organism = $query->param('MODORG')		?	$query->param('MODORG')			:	0;
	my $lockseq = $query->param('LOCK')	? 	$query->param('LOCK')	: 0;
	my $hiddenlock = hidden_fielder({"LOCK" => $lockseq});
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
					<div style = "position:relative;top:220">
						<input type="hidden" name="MODORG" value="1"/>
						<input type="submit" name=".submit" value=" Next Step: Remove these sites "/>
					</div>
					$hiddenlock
				</div>
EOM
	closer();
}

else
{
	my ($Error4, $Error0) = (" ", "" );
	my $org = $query->param('MODORG')	?	$query->param('MODORG')		:	0;
	my $oldnuc = cleanup($query->param('nucseq'), 0);
	my $lockseq = $query->param('LOCK')	?	$query->param('LOCK')		:	0;
	my $nucseq = {">Your sequence" => $oldnuc};
	open (my $fh_seq, ">../../documents/gd/tmp/sequence.FASTA") || print "can't create output file, $!";
	print $fh_seq fasta_writer( $nucseq );
	close $fh_seq;
	
	my @removes = $query->param('removeme');
	open (my $fh_rem, ">../../documents/gd/tmp/rem_seq.txt") || print "can't create output file, $!";
	print $fh_rem array_writer(@removes);
	close $fh_rem;
	my $lock = "";
	$lock .= "-l $lockseq" if ($lockseq);
	if ($org == 7)
	{
		system("../../bin/Restriction_Site_Subtraction.pl -i ../../documents/gd/tmp/sequence.FASTA -s ../../documents/gd/tmp/rem_seq.txt " . $lock ." 1>../../documents/gd/tmp/output.txt -t 3");
	}
	else
	{
		system("../../bin/Restriction_Site_Subtraction.pl -i ../../documents/gd/tmp/sequence.FASTA -s ../../documents/gd/tmp/rem_seq.txt -o " . $org . " " . $lock ." 1>../../documents/gd/tmp/output.txt -t 3");
	}
	open (my $newnuc_file, "<../../documents/gd/tmp/sequence_gdRSS/sequence_gdRSS_" . $org . ".FASTA") || print "Can't open FASTA file!";
	my $slurp_nuc = slurp ( $newnuc_file );
	my $newhsh = fasta_parser ( $slurp_nuc );
	my $newnuc;
	foreach my $id (keys %$newhsh) ##Only one key
	{
		$newnuc = $$newhsh{$id};
	}
	close $newnuc_file;
	
	open (my $output_file, "<../../documents/gd/tmp/output.txt");
	my ($header, $body) = ("", "<br>");
	my $split_text = 0;
	my @output = <$output_file>;
	for (my $index = 0; $index < scalar(@output); $index++)
	{
		next if ($output[$index] =~ m/^\n/);
		if ($split_text == 0)
		{
			if ($output[$index] =~ m/Base/)
			{
				$body .= $output[$index] . "<br>";
				$split_text = $index;
			}
			else
			{
				next if ($output[$index] =~ m/For the sequence/);
				$header .= $output[$index] . "<br>";
			}
		}
		else
		{
			last if ($output[$index] =~ m/sequence*/);
			$body .= $output[$index] . "<br>";
		}
	}
	close $output_file;
	

	my $FASTAoff = offer_fasta(fasta_writer($newhsh));
	my $hiddenstring = hidden_fielder({"MODORG" => $org});
print <<EOM;
				<div id="notes">
					$header
				</div>
				<div id="gridgroup0">
					Your altered nucleotide sequence:
					<textarea name="PASSNUCSEQUENCE"  rows="6" cols="120">$newnuc</textarea><br>
					$body
					$nextsteps
				</div>
				$hiddenstring
			</form>
			<br><br><br>
			$FASTAoff
EOM
	my @removefile = ("../../documents/gd/tmp/output.txt", "../../documents/gd/tmp/sequence.FASTA", "../../documents/gd/tmp/rem_seq.txt");
	unlink @removefile;
	remove_tree("../../documents/gd/tmp/sequence_gdRSS");
	closer();
}