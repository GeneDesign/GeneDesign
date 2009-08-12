#!/usr/bin/env perl

use TestGeneDesign;

print "\n";
$flag = 0;

$flag += test_amb_transcription();
$flag += test_amb_translation();
$flag += test_cleanup();
$flag += test_change_codons();
$flag += test_compareseqs();
$flag += test_complement();
$flag += test_count();
$flag += test_define_aa_defaults();
$flag += test_define_codon_percentages();
$flag += test_define_site_status();
$flag += test_define_reverse_codon_table();
$flag += test_degcodon_to_aas();
$flag += test_melt();
$flag += test_pattern_adder();
$flag += test_pattern_aligner();
$flag += test_pattern_finder();
$flag += test_pattern_remover();
$flag += test_randDNA();
$flag += test_regres();
$flag += test_reverse_translate();
$flag += test_siteseeker();
$flag += test_translate();
$flag += test_orf_finder();
$flag += test_codon_count();
$flag += test_generate_RSCU_values();

print "\npassed $flag out of 25 tests\n\n";