#!/usr/bin/perl

use CGI;
use PRISM;
$query = new CGI;
print $query->header(-type=>'text/plain');
@olarray = split(" ", $query->param('olarray'));
$ch = "\11" if ($query->param('sepchar') eq 'tab');
$ch = ','	if ($query->param('sepchar') eq 'comma');
$ch = ' '	if ($query->param('sepchar') eq 'space');
$ch = '_'	if ($query->param('sepchar') eq 'underscore');
$nucseq = $query->param('nucseq');
	@bcou = count($nucseq); 
	$GC = int(((($bcou[3]+$bcou[2])/$bcou[8])*100)+.5);
	$AT = int(((($bcou[0]+$bcou[1])/$bcou[8])*100)+.5);
$aaseq  = $query->param('aaseq' );
$aasiz  = length($aaseq) if ($aaseq !~ /was defined/);
$codons = $query->param('codons');
$vecname= $query->param('vecname');
$absents= $query->param('absents');
$enzcrit= $query->param('enzcrit');
$inte = $query->param('inte');
$actu = $query->param('actu');
$insert = $query->param('insert');
@inse = split(" ", $insert);
$numin = (@inse-0);
$remove = $query->param('remove');
@nowabs = sort(siterunner(1, $nucseq));
@nowuni = sort(siterunner(2, $nucseq));
$cuslen  = $query->param('ollen');
$cusmel  = $query->param('ovmel');
$whtemp   = $query->param('whtemp');
$flank   = $query->param('whflank');
@joenz = split(" ", $query->param('joenz'));
$joenznum = (@joenz+1);

# Nucleotide Sequence and Analysis
	print "\n__Nucleotide Sequence__\n$nucseq\n";
	print "_Base Count  : $bcou[8] bp ($bcou[0] A, $bcou[1] T, $bcou[2] C, $bcou[3] G)\n";
	print "_Composition : $GC% GC, $AT% AT\n\n";
# Amino Acid Sequence and Analysis
	print "__Amino Acid Sequence__\n$aaseq\n";
	print "_AA Count : $aasiz aa\n\n";
# Codon Table
	print "__Codon Table__\n$codons\n\n";
# Vector Information
	print "__Vector Information__\n";
	print "_Vector name: $vecname\n";
	print "_Sites for consideration: $absents\n\n";
# Enzyme Ranking Criteria
	print "__Enzyme Ranking Criteria__\n$enzcrit\n\n";
# GeneDesign Bit
	print "__Silent Mutations__\n";
	print "_Specified AA interval for silent site mutation: $inte\n";
	print "_Average AA interval: $actu\n";
	print "_# of silent sites mutated: $numin\n";
	print "_Sites inserted: $insert\n";
	print "_Sites removed: $remove\n";
# General ReSite Info
	print "_Absent Sites: @nowabs\n";
	print "_Unique Sites: @nowuni\n";
# Oligo Information
	print "\n__Oligo Information__\n";
	print "_Oligo Length: $cuslen\n";
	print "_Overlap Melting Temperature (deg C): $cusmel\n";
	print "_Melting Temperature Formula : $whtemp\n";
	print "_Flank Chunk Enzymes with : $flank bp\n";
	print "_Chunk Enzymes: @joenz\n";
	print "_Number of Chunks: $joenznum\n";
	print "_Oligos (5' to 3') \n";

	
for ($y = 0; $y < @olarray-0; $y++)
{
	$x = $y+1;
	$x = '0' . $x while (length($x) < length(@olarray-0));
	print $query->param('oldesig'), $x, $ch, $olarray[$y], "\n";
}