#!/usr/bin/perl
use strict;
use CGI qw(:standard);
use PML;
use GeneDesign;
use GD::Graph::lines;

my $query = new CGI;
print $query->header;

my $CODON_TABLE = define_codon_table(1);	
my $REV_CODON_TABLE = define_reverse_codon_table($CODON_TABLE);

my @styles = qw(re fn);
my @nexts  = qw(SSIns SSRem OligoDesign SeqAna);
gdheader("Codon Juggling", "gdCodJug.cgi", \@styles);

my $orgchoice = organism_selecter();

if ($query->param('nseq') eq '' && $query->param('PASSNUCSEQUENCE') eq '')
{
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
	my $nucseq = $query->param('PASSNUCSEQUENCE') eq ''	?	cleanup($query->param('nseq'), 0)	:	$query->param('PASSNUCSEQUENCE');
	my $aaseq = translate($nucseq, 1, $CODON_TABLE);
	my $org = $query->param('MODORG') || 0;
	my $ORGANISM = $ORGANISMS{$org};
	my $RSCU_VALUES = define_RSCU_values($org);
	my $bcou = count($nucseq);
	
##	if ($org ne 0)
#	{
		my $opted  = change_codons($nucseq, $CODON_TABLE, $REV_CODON_TABLE, $RSCU_VALUES, 1);	
		my $optal  = compare_sequences($nucseq, $opted);	
		my $bcouo = count($opted);
		my $nextstepopt = next_codjug(\@nexts, 7, 0);

		my $nxmty = change_codons($nucseq, $CODON_TABLE, $REV_CODON_TABLE, $RSCU_VALUES, 2);	
		my $nxtal = compare_sequences($nucseq, $nxmty);	
		my $bcoun = count($nxmty);	
		my $nextstepnxt = next_codjug(\@nexts, 7, 1);

		my $lsted = change_codons($nucseq, $CODON_TABLE, $REV_CODON_TABLE, $RSCU_VALUES, 4);	
		my $lstal = compare_sequences($nucseq, $lsted);	
		my $bcoul = count($lsted);
##		my $nextstepnxt = next_codjug(\@nexts, 7, 1);

#	}	
	my $mstdy = change_codons($nucseq, $CODON_TABLE, $REV_CODON_TABLE, $RSCU_VALUES, 3);		
	my $mstal = compare_sequences($nucseq, $mstdy);	
	my $bcoum = count($mstdy);	
	my $nextstepmst = next_codjug(\@nexts, 7, 2);
		
	my $randy  = change_codons($nucseq, $CODON_TABLE, $REV_CODON_TABLE, $RSCU_VALUES, 0);		
	my $ranal = compare_sequences($nucseq, $randy);	
	my $bcour = count($randy);	
	my $nextstepran = next_codjug(\@nexts, 7, 3);


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
					The optimized and next most optimized algorithms will not be carried out.  The most different algorithm will not be deterministic.
				</div>
EOM
	}
print <<EOM;
				<div id="notes">
					Your nucleotide sequence has been successfully juggled.  Each of the following sequences translate to the same amino acid sequence.
					The reference organism for optimal codons is $ORGANISM<br><br>
					The <strong>Optimized</strong> sequence replaces each codon in the original sequence with the most optimal codon as determined by expressivity in the organism you chose.
					 This algorithm will not be applied if organism is undefined.<br>
					The <strong>Most Different</strong> sequence has as many base changes as possible, with transversions being the most preferred change.  It uses the more optimal codon when possible.<br><br>
					The <strong>Next Most Optimized</strong> sequence uses the most optimal codon that is not the original codon. This algorithm will not be applied if organism is undefined.<br>
					The <strong>Random</strong> sequence uses a random codon that is not the original codon. No optimization is applied.<br><br>
					You can take any one of these sequences to another module by clicking the appropriate button.<br>
					See the <a href="$docpath/Guide/codjug.html" target="blank">manual</a> for more information.
				</div>
				<div id="gridgroup0">
					<textarea name="oldnucseq" rows="6" cols="150" readonly="true">$nucseq</textarea><br>
					<strong>Original Sequence</strong><br>
					&nbsp;_Base Count  : $$bcou{'length'} bp ($$bcou{'A'} A, $$bcou{'T'} T, $$bcou{'C'} C, $$bcou{'G'} G)<br>
					&nbsp;_Composition : $$bcou{'GCp'}% GC, $$bcou{'ATp'}% AT<br><br>
					<div style ="position: relative">
						<div style="position:absolute; top:0; left:550; width:600;">
							<textarea name="mdfnucseq"  rows="6" cols="65" readonly="true">$mstdy</textarea><br>
							<strong>Most Different</strong><br>
							&nbsp;_Base Count  : $$bcoum{'length'} bp ($$bcoum{'A'} A, $$bcoum{'T'} T, $$bcoum{'C'} C, $$bcoum{'G'} G)<br>
							&nbsp;_Composition : $$bcoum{'GCp'}% GC, $$bcoum{'ATp'}% AT<br>
							$$mstal{'I'} Identites, $$mstal{'D'} Changes ($$mstal{'T'} transitions $$mstal{'V'} transversions), $$mstal{'P'}% Identity<br>
							$nextstepmst
						</div>	
						<div style="position:absolute; top:200; left:550; width:600;">
							<textarea name="rdmnucseq" rows="6" cols="65" readonly="true">$randy</textarea><br>
							<strong>Random</strong> (For the experimentalists)<br>
							&nbsp;_Base Count  : $$bcour{'length'} bp ($$bcour{'A'} A, $$bcour{'T'} T, $$bcour{'C'} C, $$bcour{'G'} G)<br>
							&nbsp;_Composition : $$bcour{'GCp'}% GC, $$bcour{'ATp'}% AT<br>
							$$ranal{'I'} Identites, $$ranal{'D'} Changes ($$ranal{'T'} transitions $$ranal{'V'} transversions), $$ranal{'P'}% Identity<br>
							$nextstepran
						</div>
					</div>
EOM
	if ($org ne 0)
	{
print <<EOM;
					<div style ="position: relative">
						<div style="position:absolute; top:0; left:0;">
							<textarea name="optnucseq"  rows="6" cols="65" readonly="true">$opted</textarea><br>
							<strong>Optimized</strong><br>
							&nbsp;_Base Count  : $$bcouo{'length'} bp ($$bcouo{'A'} A, $$bcouo{'T'} T, $$bcouo{'C'} C, $$bcouo{'G'} G)<br>
							&nbsp;_Composition : $$bcouo{'GCp'}% GC, $$bcouo{'ATp'}% AT<br>
							$$optal{'I'} Identites, $$optal{'D'} Changes ($$optal{'T'} transitions $$optal{'V'} transversions), $$optal{'P'}% Identity<br>
							$nextstepopt
						</div>
						<div style="position:absolute; top:200; left:0; width:600;">
							<textarea name="nxtnucseq" rows="6" cols="65" readonly="true">$nxmty</textarea><br>
							<strong>Next Most Different</strong> (For the experimentalists)<br>
							&nbsp;_Base Count  : $$bcoun{'length'} bp ($$bcoun{'A'} A, $$bcoun{'T'} T, $$bcoun{'C'} C, $$bcoun{'G'} G)<br>
							&nbsp;_Composition : $$bcoun{'GCp'}% GC, $$bcoun{'ATp'}% AT<br>
							$$nxtal{'I'} Identites, $$nxtal{'D'} Changes ($$nxtal{'T'} transitions $$nxtal{'V'} transversions), $$nxtal{'P'}% Identity<br>
							$nextstepnxt
						</div>
					</div>
					<div style ="position: relative">
						<div style="position:absolute; top:400; left:0; width:600;">
							<textarea name="lstnucseq" rows="6" cols="65" readonly="true">$lsted</textarea><br>
							<strong>Least Different</strong><br>
							&nbsp;_Base Count  : $$bcoul{'length'} bp ($$bcoul{'A'} A, $$bcoul{'T'} T, $$bcoul{'C'} C, $$bcoul{'G'} G)<br>
							&nbsp;_Composition : $$bcoul{'GCp'}% GC, $$bcoul{'ATp'}% AT<br>
							$$lstal{'I'} Identites, $$lstal{'D'} Changes ($$lstal{'T'} transitions $$lstal{'V'} transversions), $$lstal{'P'}% Identity<br>
						</div>
					</div>
				</div><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>
				<div id="notes">
					The graph below maps the average RSCU over a sliding window for each of the sequences given above.
				</div>
EOM
	my $window = length($nucseq) > 1000	?	20 * (int(length($nucseq)/1000))	:	length($nucseq) > 500	?	20	:	10; #$query->param('WINDOW');
	my $graph = GD::Graph::lines->new(1000, 600);
	$graph->set( 
		  x_label           => 'Residue Postion',
		  y_label           => 'Average Codon Usage Value',
		  title             => "Sliding window of $window codons using $ORGANISM RSCU values",
		  y_max_value       => 1,
		  y_min_value       =>  0,
		  tick_length       => 3,
		  y_tick_number     => 1,
		  y_label_skip      => .1,
		  x_label_skip      => int(length($nucseq)/50),
		  markers           => [1], 
			line_width  => 2,
		  marker_size		=> 2,
		  dclrs => [ qw(black green gray red orange yellow)],
	  ) or die $graph->error;
	  $graph->set_legend(("Original", "Optimized", "Least different", "Most different", "Next Most Different", "Random"));
	  my @data;
	my $CODON_PERCENTAGE_TABLE = define_codon_percentages($CODON_TABLE, $RSCU_VALUES);

my ($nucseqx, $nucseqy) = index_codon_percentages($nucseq, $window, $CODON_PERCENTAGE_TABLE);
my ($optedx, $optedy) = index_codon_percentages($opted, $window, $CODON_PERCENTAGE_TABLE);
my ($lstedx, $lstedy) = index_codon_percentages($lsted, $window, $CODON_PERCENTAGE_TABLE);
my ($mstdyx, $mstdyy) = index_codon_percentages($mstdy, $window, $CODON_PERCENTAGE_TABLE);
my ($nxmtyx, $nxmtyy) = index_codon_percentages($nxmty, $window, $CODON_PERCENTAGE_TABLE);
my ($randyx, $randyy) = index_codon_percentages($randy, $window, $CODON_PERCENTAGE_TABLE);
push @data, $nucseqx, $nucseqy, $optedy, $lstedy, $mstdyy, $nxmtyy, $randyy;

my $format = $graph->export_format;
  open(IMG, ">../../Documents/gd2/tmp/file.$format") or die $!;
  binmode IMG;
  print IMG $graph->plot(\@data)->$format();
  close IMG;
print <<EOM;
	<img height=600 width=1000 src="$docpath/tmp/file.$format">
EOM
#	print header("image/$format");
#	binmode STDOUT;
#	print $graph->plot(\@data)->$format();


print break(5);

print <<EOM;					
				<div id="notes">
					An alignment is presented below. &quot;cons&quot;  is the consensus sequence - these are the bases that are non-negotiable across algorithms.
					There is an asterisk under every tenth nucleotide.
				</div>
				<div class="samewidth">
EOM
		my $rowstart = 0;	my $rowleng = 150;	my $cons = '';	
		for (my $x = 0; $x < length($nucseq); $x++)
		{
			$cons .=  ( (substr($nucseq, $x, 1) eq substr($opted, $x, 1)) && (substr($nucseq, $x, 1) eq substr($mstdy, $x, 1)))	?	substr($nucseq, $x, 1)	:	'_';
		}
		while	($rowstart < length($nucseq))
		{
			my $rt;
			print "\ntran&nbsp;";
			for ($rt = ($rowstart / 3); $rt < ($rowstart / 3) + ($rowleng / 3); $rt++)
			{
				print substr($aaseq, $rt, 1), "&nbsp;&nbsp;";
			}
			print "&nbsp;$rt<br>\n";
			
			print "orig&nbsp;", substr($nucseq, $rowstart, $rowleng), "<br>\n";
			print "opti&nbsp;", substr($opted, $rowstart, $rowleng), "<br>\n";
			print "mtdf&nbsp;", substr($mstdy, $rowstart, $rowleng), "<br>\n";			
			print "cons&nbsp;", substr($cons, $rowstart, $rowleng), "<br>\n";
			print "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;", ("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*" x ($rowleng / 10)), "<br>\n";
			print "<br><br>\n";
			$rowstart+=$rowleng;
		}
		print ("\n\t\t\t\t</div>\n");
	}
	my %hiddenhash = ("PASSNUCSEQUENCE" => "", "PASSAASEQUENCE" => $aaseq, "MODORG" => $org);
	my $hiddenstring = hidden_fielder(\%hiddenhash);
print <<EOM;
				<br><br>&nbsp;
				$hiddenstring
EOM
	closer();
}