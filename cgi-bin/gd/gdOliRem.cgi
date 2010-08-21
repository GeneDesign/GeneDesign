#!/usr/bin/perl
use strict;
use warnings;
use GeneDesign;
use GeneDesignML;
use CGI;
use Perl6::Slurp;
use File::Path qw(remove_tree);

my $query = new CGI;
print $query->header;

my $CODON_TABLE	 = define_codon_table(1);
my $RE_DATA = define_sites($enzfile);
$ORGANISMS{7} = "no organism";

my @styles = qw(re);
my @nexts  = qw(SSIns SSRem SeqAna REBB UserBB OlBB);
my $nextsteps = next_stepper(\@nexts, 5);

gdheader("Short Sequence Removal", "gdOliRem.cgi", \@styles);

if (! $query->param('REMSEQ'))
{
	my $orgchoice = organism_selecter_none();
	my $nucseq = $query->param('PASSNUCSEQUENCE')	?	$query->param('PASSNUCSEQUENCE')	:	$query->param('nucseq');
	$nucseq = $nucseq	?	$nucseq	:	"";
	my $readonly = ! $nucseq ?	" "	:	'readonly = "true"';
print <<EOM;
				<div id="notes">
					<strong>To use this module you need two nucleotide sequences, large and small.  An organism name is optional.</strong><br>
					Your nucleotide sequence will be searched for the short sequence you provide and as many iterations as possible will 
					be removed by changing whole codons without changing the amino acid sequence.<br><em>Please Note:</em><br>
					&nbsp;&nbsp;&bull;If you select an organism, targeted codons will be replaced with the codon that has the closest RSCU value in that organism.<br>
					&nbsp;&nbsp;&bull;If you select no organism, targeted codons will be replaced with a random codon.<br>
					See the <a href="$linkpath/Guide/shortr.html" target="blank">manual</a> for more information.
				</div>
				<div id="gridgroup0">
					Your nucleotide sequence:<br>
					<textarea name="nuseq"  rows="6" cols="100" $readonly>$nucseq</textarea><br>
					$orgchoice<br><br>
					Sequence to Remove <input type="text" name="REMSEQ" cols="20"><br><br>
					Number of Iterations to attempt <input type="text" name="ITER" size="5" value="3" maxlength="3"><br><br>
					Enter positions to lock: (Optional) 
					<input type="text" name="LOCK" cols="20"><br>
					<div id="gridgroup1" align ="center" style="position:absolute; top:300; ">
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
	my $lockseq = $query->param('LOCK')	?	$query->param('LOCK')		:	0;
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
	
	my $seq = {">Your sequence" => $nucseq};
	open (my $fh_seq, ">../../documents/gd/tmp/sequence.FASTA") || print "can't create output file, $!";
	print $fh_seq fasta_writer( $seq );
	close $fh_seq;
	
	open (my $fh_rem, ">../../documents/gd/tmp/rem_seq.txt") || print "can't create output file, $!";
	print $fh_rem $remseq;
	close $fh_rem;
	
	my $lock = "";
	$lock .= "-l $lockseq" if ($lockseq);
	print $lock;
	if ($org == 7)
	{
		system("../../bin/Short_Sequence_Subtraction.pl -i ../../documents/gd/tmp/sequence.FASTA -s ../../documents/gd/tmp/rem_seq.txt " . $lock ." -t " . $iter . " 1>../../documents/gd/tmp/output.txt");
	}
	else
	{
		system("../../bin/Short_Sequence_Subtraction.pl -i ../../documents/gd/tmp/sequence.FASTA -s ../../documents/gd/tmp/rem_seq.txt -o " . $org . " " . $lock . " -t " . $iter . " 1>../../documents/gd/tmp/output.txt");
	}
	open (my $newnuc_file, "<../../documents/gd/tmp/sequence_gdSSS/sequence_gdSSS_" . $org . ".FASTA") || print "Can't open FASTA file!";
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
	remove_tree("../../documents/gd/tmp/sequence_gdSSS");
	closer();
}