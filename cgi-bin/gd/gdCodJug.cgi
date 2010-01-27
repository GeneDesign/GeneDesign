#!/usr/bin/perl
use strict;
use warnings;

use CGI qw(:standard);
use GeneDesign;
use GeneDesignML;
use GD::Graph::lines;

my $query = new CGI;
print $query->header;

my $CODON_TABLE = define_codon_table(1);

my @styles = qw(re fn);
my @nexts  = qw(SSIns SSRem OligoDesign SeqAna);
gdheader("Codon Juggling", "gdCodJug.cgi", \@styles);

if (! $query->param('nseq') && ! $query->param('PASSNUCSEQUENCE'))
{
	my $orgchoice = organism_selecter();
print <<EOM;
				<div id="notes">
					<strong>To use this module you need a coding nucleotide sequence and an organism name.</strong><br>
					It is recommended that you only use ORFs with this module because codons will be altered without changing the first frame amino acid sequence. If your coding sequence is not in the first frame it will be changed.
					Four different algorithms will be applied to your sequence.  Each will change the nucleotide sequence without changing the translated amino acid sequence. You will be presented with the four new sequences and an alignment at the next screen.<br>
					<em>Please Note:</em><br>
					&nbsp;&nbsp;&bull;The only frame that is considered inviolable is frame 1, which will be determined by the first three nucleotides of your sequence.<br>
					&nbsp;&nbsp;&bull;Ambiguous nucleotides and non-nucleotide characters will be removed.<br>
					See the <a href="$docpath/Guide/codjug.html" target="blank">manual</a> for more information.
				</div>
				<div id="gridgroup0">
					Your nucleotide sequence:<br>
					<textarea name="nseq" rows="6" cols="100"></textarea><br>
					$orgchoice
					<div id="gridgroup1" align ="center" style="position:absolute; top:175;">
						<input type="submit" name=".submit" value=" Next Step: Results " />
					</div>
				</div>
EOM
	closer();
}

else
{	
	my $org			= $query->param('MODORG') || 0;
	my $RSCU_VALUES = define_RSCU_values($org);
	my $nucseq		= ! $query->param('PASSNUCSEQUENCE')	?	cleanup($query->param('nseq'), 0)	:	$query->param('PASSNUCSEQUENCE');
	my $orig_cnt	= count($nucseq);
	my $aaseq	= translate($nucseq, 1, $CODON_TABLE);
	
	my $rand_seq  = change_codons($nucseq, $CODON_TABLE, $RSCU_VALUES, 0);
	my $rand_aln = compare_sequences($nucseq, $rand_seq);
	my $rand_cnt = count($rand_seq);
	my $rand_nxt = next_codjug(\@nexts, 7, 0);

	my $opti_seq = change_codons($nucseq, $CODON_TABLE, $RSCU_VALUES, 1);
	my $opti_aln = compare_sequences($nucseq, $opti_seq);
	my $opti_cnt = count($opti_seq);
	my $opti_nxt = next_codjug(\@nexts, 7, 1);

	my $lsop_seq = change_codons($nucseq, $CODON_TABLE, $RSCU_VALUES, 2);
	my $lsop_aln = compare_sequences($nucseq, $lsop_seq);
	my $lsop_cnt = count($lsop_seq);
	my $lsop_nxt = next_codjug(\@nexts, 7, 2);

	my $msdf_seq = change_codons($nucseq, $CODON_TABLE, $RSCU_VALUES, 3);
	my $msdf_aln = compare_sequences($nucseq, $msdf_seq);
	my $msdf_cnt = count($msdf_seq);
	my $msdf_nxt = next_codjug(\@nexts, 7, 3);

	my $lsdf_seq = change_codons($nucseq, $CODON_TABLE, $RSCU_VALUES, 4);
	my $lsdf_aln = compare_sequences($nucseq, $lsdf_seq);
	my $lsdf_cnt = count($lsdf_seq);
	my $lsdf_nxt = next_codjug(\@nexts, 7, 4);

	my @war2 = pattern_finder($nucseq, "*", 2, 1, $CODON_TABLE);
	my $war3 = 1 if (@war2 && ((@war2-0 > 1 ) || ((($war2[0]+1)*3) != length($nucseq))));
	if (((substr($nucseq, 0, 3) ne 'ATG') || $war3) && $nucseq)
	{
print <<EOM;
				<div id = "warn">
					<strong>Warning:</strong> Your sequence is not a simple coding sequence.<br>
					Either your sequence does not begin with ATG or your sequence has at least one internal stop codon in the first frame.<br>
					It is still possible to manipulate this sequence but you should check to be sure that crucial features are not compromised.
				</div>
EOM
	}
	if ($org eq 0)
	{
print <<EOM;
				<div id = "warn">
					<strong>Warning:</strong> You have not defined an organism recognized by GeneDesign.<br>
					The three RSCU based algorithms will not be carried out.  The most different algorithm will not be deterministic.
				</div>
EOM
	}
print <<EOM;
				<div id="notes">
					Your nucleotide sequence has been successfully juggled.  Each of the following sequences translate to the same amino acid sequence.
					The reference organism for optimal codons is <i>$ORGANISMS{$org}</i>.<br><br>
					The <strong>Optimized</strong> sequence replaces each codon in the original sequence with the optimal codon as determined by expressivity in the organism you chose.
					 This algorithm will not be applied if organism is undefined.<br>
					The <strong>Most Different Sequence</strong> sequence has as many base changes as possible, with transversions being the most preferred change.  It uses the more optimal codon when possible.<br>
					The <strong>Least Different RSCU</strong> sequence has replaced every codon it can with a codon that has an RSCU value as close as possible to that of the original codon, with a difference no greater than 1. This algorithm will not be applied if organism is undefined.<br>
					The <strong>Less Optimized</strong> sequence uses the first optimal codon that is not the original codon. This algorithm will not be applied if organism is undefined.<br>
					The <strong>Random</strong> sequence uses a random codon that is not the original codon. No optimization is applied.<br><br>
					You can take any one of these sequences to another module by clicking the appropriate button.<br>
					See the <a href="$docpath/Guide/codjug.html" target="blank">manual</a> for more information.
				</div>
				<div id="gridgroup0">
					<textarea name="oldnucseq" rows="6" cols="150" readonly="true">$nucseq</textarea><br>
					<strong>Original Sequence</strong><br>
					&nbsp;_Base Count  : $$orig_cnt{'length'} bp ($$orig_cnt{'A'} A, $$orig_cnt{'T'} T, $$orig_cnt{'C'} C, $$orig_cnt{'G'} G)<br>
					&nbsp;_Composition : $$orig_cnt{'GCp'}% GC, $$orig_cnt{'ATp'}% AT<br><br>
					<div style ="position: relative">
						<div style="position:absolute; top:0; left:550; width:600;">
							<textarea name="msdfnucseq"  rows="6" cols="65" readonly="true">$msdf_seq</textarea><br>
							<strong>Most Different Sequence</strong><br>
							&nbsp;_Base Count  : $$msdf_cnt{'length'} bp ($$msdf_cnt{'A'} A, $$msdf_cnt{'T'} T, $$msdf_cnt{'C'} C, $$msdf_cnt{'G'} G)<br>
							&nbsp;_Composition : $$msdf_cnt{'GCp'}% GC, $$msdf_cnt{'ATp'}% AT<br>
							$$msdf_aln{'I'} Identites, $$msdf_aln{'D'} Changes ($$msdf_aln{'T'} transitions $$msdf_aln{'V'} transversions), $$msdf_aln{'P'}% Identity<br>
							$msdf_nxt
						</div>
						<div style="position:absolute; top:400; left:550; width:600;">
							<textarea name="randnucseq" rows="6" cols="65" readonly="true">$rand_seq</textarea><br>
							<strong>Random</strong> (For the experimentalists)<br>
							&nbsp;_Base Count  : $$rand_cnt{'length'} bp ($$rand_cnt{'A'} A, $$rand_cnt{'T'} T, $$rand_cnt{'C'} C, $$rand_cnt{'G'} G)<br>
							&nbsp;_Composition : $$rand_cnt{'GCp'}% GC, $$rand_cnt{'ATp'}% AT<br>
							$$rand_aln{'I'} Identites, $$rand_aln{'D'} Changes ($$rand_aln{'T'} transitions $$rand_aln{'V'} transversions), $$rand_aln{'P'}% Identity<br>
							$rand_nxt
						</div>
					</div>
EOM
	if ($org ne 0)
	{
print <<EOM;
					<div style ="position: relative">
						<div style="position:absolute; top:0; left:0;">
							<textarea name="optinucseq"  rows="6" cols="65" readonly="true">$opti_seq</textarea><br>
							<strong>Optimized</strong><br>
							&nbsp;_Base Count  : $$opti_cnt{'length'} bp ($$opti_cnt{'A'} A, $$opti_cnt{'T'} T, $$opti_cnt{'C'} C, $$opti_cnt{'G'} G)<br>
							&nbsp;_Composition : $$opti_cnt{'GCp'}% GC, $$opti_cnt{'ATp'}% AT<br>
							$$opti_aln{'I'} Identites, $$opti_aln{'D'} Changes ($$opti_aln{'T'} transitions $$opti_aln{'V'} transversions), $$opti_aln{'P'}% Identity<br>
							$opti_nxt
						</div>
						<div style="position:absolute; top:200; left:0; width:600;">
							<textarea name="lsopnucseq" rows="6" cols="65" readonly="true">$lsop_seq</textarea><br>
							<strong>Less Optimized</strong> (For the experimentalists)<br>
							&nbsp;_Base Count  : $$lsop_cnt{'length'} bp ($$lsop_cnt{'A'} A, $$lsop_cnt{'T'} T, $$lsop_cnt{'C'} C, $$lsop_cnt{'G'} G)<br>
							&nbsp;_Composition : $$lsop_cnt{'GCp'}% GC, $$lsop_cnt{'ATp'}% AT<br>
							$$lsop_aln{'I'} Identites, $$lsop_aln{'D'} Changes ($$lsop_aln{'T'} transitions $$lsop_aln{'V'} transversions), $$lsop_aln{'P'}% Identity<br>
							$lsop_nxt
						</div>
						<div style="position:absolute; top:400; left:0; width:600;">
							<textarea name="lsdfnucseq" rows="6" cols="65" readonly="true">$lsdf_seq</textarea><br>
							<strong>Least Different RSCU</strong><br>
							&nbsp;_Base Count  : $$lsdf_cnt{'length'} bp ($$lsdf_cnt{'A'} A, $$lsdf_cnt{'T'} T, $$lsdf_cnt{'C'} C, $$lsdf_cnt{'G'} G)<br>
							&nbsp;_Composition : $$lsdf_cnt{'GCp'}% GC, $$lsdf_cnt{'ATp'}% AT<br>
							$$lsdf_aln{'I'} Identites, $$lsdf_aln{'D'} Changes ($$lsdf_aln{'T'} transitions $$lsdf_aln{'V'} transversions), $$lsdf_aln{'P'}% Identity<br>
							$lsdf_nxt
						</div>
					</div>
					<div style ="position: relative">
					</div>
				</div>
				<div id="notes" style ="position:relative; top:600; text-align:center">
					The graph below maps the average RSCU over a sliding window for each of the sequences given above.<br><br>
EOM
		my $window = length($nucseq) > 1000	?	20 * (int(length($nucseq)/1000))	:	length($nucseq) > 500	?	20	:	10; #$query->param('WINDOW');
		my $graph = GD::Graph::lines->new(800, 600);
		$graph->set( 
			x_label           => 'Window Position (Codon Offset)',
			y_label           => 'Average Relative Synonymous Codon Usage Value',
			title             => "Sliding window of $window using RSCU values from $ORGANISMS{$org}",
			y_max_value       => 1,
			y_min_value       =>  0,
			tick_length       => 3,
			y_tick_number     => 1,
			x_label_position  => 0.5,
			y_label_skip      => .1,
			x_label_skip      => int(length($nucseq)/50),
			markers           => [1], 
			line_width		  => 2,
			marker_size		  => 2,
			dclrs => [ qw(black green gray red orange yellow)],
		) or die $graph->error;
		$graph->set_legend(("Original", "Optimized", "Least different RSCU", "Most different Sequence", "Less optimized", "Random"));
		my $CODON_PERCENTAGE_TABLE = define_codon_percentages($CODON_TABLE, $RSCU_VALUES);

		my ($nucseqx,   $nucseqy)   = index_codon_percentages($nucseq,   $window, $CODON_PERCENTAGE_TABLE);
		my ($opti_seqx, $opti_seqy) = index_codon_percentages($opti_seq, $window, $CODON_PERCENTAGE_TABLE);
		my ($lsdf_seqx, $lsdf_seqy) = index_codon_percentages($lsdf_seq, $window, $CODON_PERCENTAGE_TABLE);
		my ($msdf_seqx, $msdf_seqy) = index_codon_percentages($msdf_seq, $window, $CODON_PERCENTAGE_TABLE);
		my ($lsop_seqx, $lsop_seqy) = index_codon_percentages($lsop_seq, $window, $CODON_PERCENTAGE_TABLE);
		my ($rand_seqx, $rand_seqy) = index_codon_percentages($rand_seq, $window, $CODON_PERCENTAGE_TABLE);
		my $data = [$nucseqx, $nucseqy, $opti_seqy, $lsdf_seqy, $msdf_seqy, $lsop_seqy, $rand_seqy];
		my $format = $graph->export_format;
		open   (IMG, ">$docpath/tmp/file.$format") or die $!;
		binmode IMG;
		print   IMG $graph->plot($data)->$format();
		close   IMG;
		my $cons_seq = cons_seq([$nucseq, $opti_seq, $msdf_seq, $lsdf_seq]);
		my $alignment = print_alignment({"1 orig"=>$nucseq, "2 opti" =>$opti_seq, "3 msdf" => $msdf_seq, "4 lsdf" => $lsdf_seq, "5 cons" => $cons_seq}, 120, 1, $aaseq);
print <<EOM;
					<img height=600 width=800 src="$linkpath/tmp/file.$format">
				</div>
				<br><br><br><br><br>					
				<div id="notes" style ="position:relative;top:550">
					An alignment is presented below. &quot;cons&quot; is the consensus sequence. There is a &times; under every tenth nucleotide.<br>
					<div class="samewidth">
						$alignment
					</div>
				</div>
EOM
	}
	my $hiddenhash = {"PASSNUCSEQUENCE" => "", "PASSAASEQUENCE" => $aaseq, "MODORG" => $org};
	my $hiddenstring = hidden_fielder($hiddenhash);
print <<EOM;
				<br><br>&nbsp;
				$hiddenstring
EOM
	closer();
}