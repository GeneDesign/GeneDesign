#!/usr/bin/perl
use warnings;
use strict;
use GeneDesign;
use GeneDesignML;
use GeneDesignSufTree;
use CGI;

my $query = new CGI;
print $query->header;

my $CODON_TABLE	 = define_codon_table(1);

my @styles = qw(re mg pd fn);
my @nexts  = qw(SSIns SSRem SeqAna REBB UserBB OlBB);
my $nextsteps = next_stepper(\@nexts, 5);

gdheader("Silent Short Sequence Insertion", "gdOliIns.cgi", \@styles);

if (! $query->param('swit') && ! $query->param('insseq'))
{
	my $nucseq = $query->param('PASSNUCSEQUENCE')	?	$query->param('PASSNUCSEQUENCE')	:	$query->param('nucseq');
	my $readonly = $nucseq	?	'readonly = "true"'	:	'';
print <<EOM;
				<div id="notes">
					<strong>To use this module you need two nucleotide sequences, large and small.  An organism name is optional.</strong><br>
					Your nucleotide sequence will be searched for the short sequence you provide and as many iterations as possible will be inserted by changing whole codons 
					without changing the amino acid sequence.<br><br>
					See the <a href="$docpath/Guide/shortr.html">manual</a> for more information.
				</div>
				<div id="gridgroup0">
					Your nucleotide sequence:<br>
					<textarea name="nuseq"  rows="6" cols="100" $readonly>$nucseq</textarea><br>
					Sequence(s) to be Inserted: <input type="text" name="insseq"  columns="20" /><br><br>
					Also consider reverse complemented sequences <input type="checkbox" name="revcomp" value="1"><br><br>
					<div id="gridgroup1" align ="center" style="position:absolute; top:170; ">
						<input type="submit" name=".submit" value=" Insert short sequences " />
					</div>
				</div>
EOM
	closer();
}

elsif ($query->param('firstaround') ne 'no')
{
	if ($query->param('nuseq') eq '')
	{
		take_exception("You need a nucleotide sequence.<br>");
		exit;
	}
	if ($query->param('insseq') eq '')
	{
		take_exception("You need a short sequence to be inserted (at least two bp) <br> ");
		exit;
	}
	if (length($query->param('insseq')) >= length($query->param('nuseq')))
	{
		take_exception("Your short sequence should be shorter than your nucleotide sequence.<br>\n");
		exit;
	}
	my $nucseq = $query->param('PASSNUCSEQUENCE')	?	$query->param('PASSNUCSEQUENCE')	:	cleanup($query->param('nuseq'));
	my $aaseq = translate($nucseq, 1, $CODON_TABLE);
	my @war2 = pattern_finder($nucseq, "*", 2, 1, $CODON_TABLE);
	my $war3 = 1 if (@war2 && ((scalar(@war2) > 1 ) || (($war2[0] + 1) != length($aaseq))));
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
	my @insseqs = split(/[\s\,]/, $query->param('insseq'));
	print "insseqs @insseqs<br><br>";
	my @finarr;
	my $OL_DATA = define_oligos(\@insseqs, $query->param('revcomp'));


	my ($t_arr, $t_hsh) = ([], {});
	foreach my $oligo (@insseqs)	
	{
		my $site = $$OL_DATA{CLEAN}->{$oligo};
		my $etis = complement($site, 1);
		push @{$t_arr}, map {"$_ . $oligo"} amb_translation($site, $CODON_TABLE);
		if ($etis ne $site && $query->param('revcomp'))
		{
			push @{$t_arr}, map {"$_ . $oligo"} amb_translation($etis, $CODON_TABLE);
		}
	}
	my $tree = new_aa GeneDesignSufTree();
	$tree->add_aa_paths($_, $t_hsh) foreach (@{$t_arr});
	my @array = $tree->find_aa_paths($aaseq); #looks like ("1: MlyI MSH", "1: PleI MSH"...)
	my @hits = map {$_ . " . "} @array;
	
	my $len = length($nucseq);
	my $results;
	foreach my $insseq (@insseqs)
	{
		my $temphash = siteseeker($nucseq, $$OL_DATA{CLEAN}->{$insseq}, $$OL_DATA{REGEX}->{$insseq});
		$results .= "I was asked to insert the sequence $insseq. " . scalar(keys %$temphash) ." instances are already present and will not be annotated here.<br>\n\t\t\t\t\t";
	}
	
print <<EOM;
				<div id="notes">
					$results
					<input type="submit" value=" Insert the instances you have selected " onClick="OliISum(0);">
				</div>
				<div id = "gridgroup0"><br>
EOM
#					<input type="submit" value=" Insert all possible instances " onClick="OliISum(1);"><br>
	annpsite($aaseq, \@array);
	my $hiddenhash = {'swit' => "some", 'insseq' => join(" ", @insseqs), 'nucseq' => $nucseq, 'firstaround' => "no", 'revcomp' => $query->param('revcomp'),};
	$$hiddenhash{org} = $query->param('MODORG') if ($query->param('MODORG'));
	my $hiddenstring = hidden_fielder($hiddenhash);
print <<EOM;
				</div>
				$hiddenstring
EOM
	closer();
}

elsif ($query->param('swit') eq 'all' || $query->param('swit') eq 'some')
{
	my $org = $query->param('org');
	my $nucseq = $query->param('nucseq');
	my $aaseq = translate($nucseq, 1, $CODON_TABLE);
	my @insseqs = split(/[\s]/, $query->param('insseq'));
	my $newnuc = $nucseq;
	my $OL_DATA = define_oligos(\@insseqs, $query->param('revcomp'));
	my $result = qr/[\W ]*([A-Za-z0-9]+) ([A-Z]+)/;
	my $inscount = 0;
	my $results = " ";
	if ($query->param('swit') eq 'some')
	{
		for my $m (1.. length($aaseq))
		{
			my ($box, $seq) = ($1, $2) if ($query->param('site' . $m) && $query->param('site' . $m) =~ $result);
			if($box && $box ne '-')
			{
				$inscount++;
#	print "GOT $box ($$OL_DATA{CLEAN}->{$box}) at $m with $seq<br>";
				my $critseg = substr($nucseq, ($m*3) - 3, length($seq)*3);
				my $peptide = translate($critseg, 1, $CODON_TABLE);
				my $newpatt = pattern_aligner($critseg, $$OL_DATA{CLEAN}->{$box}, $peptide, $CODON_TABLE);
				my $newcritseg = pattern_adder($critseg, $newpatt, $CODON_TABLE);
#	print "pattern ", $$OL_DATA{CLEAN}->{$box}, ", pattern $newpatt,  peptide $peptide, critseg $critseg, newcritseg $newcritseg<br>";
				substr($newnuc, $m*3 - 3, length($newcritseg)) = $newcritseg;
			#	push @Error1, $box;
			}
		}
	}
	$results .= "Translation error! the translation of your sequence has been altered.<br>" if (translate($nucseq, 1, $CODON_TABLE) ne translate($newnuc, 1, $CODON_TABLE));
	my $newal = compare_sequences($nucseq, $newnuc);
	my $bcou = count($newnuc); 
	my $hiddenstring = hidden_fielder({"MODORG" => $org});
	
print <<EOM;
				<div id="notes">
					I was asked to insert $inscount instance(s) of @insseqs.<br>
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