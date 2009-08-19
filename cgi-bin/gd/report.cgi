#!/usr/bin/perl
use strict;
use CGI;
use GeneDesign;


my $CODON_TABLE	 = define_codon_table(1);
my $RE_DATA = define_sites("<newenz.txt");

my $query = new CGI;
print $query->header(-type=>'text/plain');
my %SEPCHAR = {tab => "\11", comma => ",", space => " ", underscore => "_"};

my @olarray = split(" ", $query->param('olarray'));
my $ch = $SEPCHAR{ $query->param('sepchar')};
my $nucseq = $query->param('nucseq');
my $SITE_STATUS = define_site_status($nucseq, $$RE_DATA{REGEX});
my $bcou = count($nucseq); 
my $aaseq  = $query->param('aaseq' );
my $aasiz  = length($aaseq);
my $codons = $query->param('codons');
my $vecname= $query->param('vecname');
my $absents= $query->param('absents');
my $enzcrit= $query->param('enzcrit');
my $inte = $query->param('inte');
my $actu = $query->param('actu');
my $insert = $query->param('insert');
my $numin = scalar(split(" ", $insert));
my $remove = $query->param('remove');
my @nowabs = sort grep {$$SITE_STATUS{$_} == 0} keys %$SITE_STATUS;
my @nowuni = sort grep {$$SITE_STATUS{$_} == 1} keys %$SITE_STATUS;
my $cuslen  = $query->param('ollen');
my $cusmel  = $query->param('ovmel');
my $whtemp   = $query->param('whtemp');
my $flank   = $query->param('whflank');
my @joenz = split(" ", $query->param('joenz'));
my $joenznum = scalar(@joenz)+1;

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

	
for my $y (0..scalar(@olarray)-1)
{
	my $x = $y+1;
	$x = '0' . $x while (length($x) < length(scalar(@olarray)));
	print $query->param('oldesig'), $x, $ch, $olarray[$y], "\n";
}