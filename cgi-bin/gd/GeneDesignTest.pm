package GeneDesignTest;
use 5.006;
require Exporter;
use GeneDesign;
use GeneDesignSufTree;

@ISA = qw(Exporter);
@EXPORT = qw(test_amb_transcription test_amb_translation test_change_codons test_cleanup test_compareseqs test_complement test_count test_define_site_status 
			test_define_aa_defaults test_define_codon_percentages test_define_reverse_codon_table test_degcodon_to_aas test_melt test_orf_finder
			test_pattern_adder test_pattern_aligner test_pattern_finder test_pattern_remover test_randDNA test_regres test_reverse_translate test_siteseeker test_translate
			test_codon_count test_generate_RSCU_values test_random_pattern_remover test_replace_lock test_check_lock);

my $CODON_TABLE = define_codon_table(1);	
my $RSCU_VALUES = define_RSCU_values(1);

#print "$_:\t$$RSCU_VALUES{$_}\n" foreach (keys %$RSCU_VALUES);

#my $RE_DATA = define_sites("newenz.txt");	
my $RE_DATA = define_sites("bs_enzymes.txt");

$REV_CODON_TABLE{"C"} = ['TGT', 'TGC'];		$REV_CODON_TABLE{"D"} = ['GAT', 'GAC'];		$REV_CODON_TABLE{"E"} = ['GAA', 'GAG'];									
$REV_CODON_TABLE{"F"} = ['TTT', 'TTC'];		$REV_CODON_TABLE{"H"} = ['CAT', 'CAC'];		$REV_CODON_TABLE{"K"} = ['AAA', 'AAG'];	
$REV_CODON_TABLE{"N"} = ['AAT', 'AAC'];		$REV_CODON_TABLE{"Q"} = ['CAA', 'CAG'];		$REV_CODON_TABLE{"Y"} = ['TAT', 'TAC'];
$REV_CODON_TABLE{"I"} = ['ATT', 'ATC', 'ATA'];			$REV_CODON_TABLE{"L"} = ['TTA', 'TTG', 'CTT', 'CTC', 'CTA', 'CTG'];	
$REV_CODON_TABLE{"*"} = ['TAA', 'TAG', 'TGA'];			$REV_CODON_TABLE{"R"} = ['CGT', 'CGC', 'CGA', 'CGG', 'AGA', 'AGG'];
$REV_CODON_TABLE{"A"} = ['GCT', 'GCC', 'GCA', 'GCG'];	$REV_CODON_TABLE{"G"} = ['GGT', 'GGC', 'GGA', 'GGG'];									
$REV_CODON_TABLE{"P"} = ['CCT', 'CCC', 'CCA', 'CCG'];	$REV_CODON_TABLE{"T"} = ['ACT', 'ACC', 'ACA', 'ACG'];					
$REV_CODON_TABLE{"S"} = ['TCT', 'TCC', 'TCA', 'TCG', 'AGT', 'AGC'];		$REV_CODON_TABLE{"V"} = ['GTT', 'GTC', 'GTA', 'GTG'];
$REV_CODON_TABLE{"W"} = ['TGG'];										

$DEG_REV_CODON_TABLE{"A"} = ['GCN'];		$DEG_REV_CODON_TABLE{"C"} = ['TGY'];		$DEG_REV_CODON_TABLE{"D"} = ['GAY'];		
$DEG_REV_CODON_TABLE{"E"} = ['GAR'];		$DEG_REV_CODON_TABLE{"F"} = ['TTY'];		$DEG_REV_CODON_TABLE{"G"} = ['GGN'];					
$DEG_REV_CODON_TABLE{"H"} = ['CAY'];		$DEG_REV_CODON_TABLE{"I"} = ['ATH'];		$DEG_REV_CODON_TABLE{"K"} = ['AAR'];		
$DEG_REV_CODON_TABLE{"L"} = ['YTR', 'CTY'];	$DEG_REV_CODON_TABLE{"M"} = ['ATG'];		$DEG_REV_CODON_TABLE{"N"} = ['AAY'];
$DEG_REV_CODON_TABLE{"P"} = ['CCN'];		$DEG_REV_CODON_TABLE{"Q"} = ['CAR'];		$DEG_REV_CODON_TABLE{"R"} = ['MGR', 'CGY'];	
$DEG_REV_CODON_TABLE{"S"} = ['WCY', 'TCR'];	$DEG_REV_CODON_TABLE{"T"} = ['ACN'];		$DEG_REV_CODON_TABLE{"V"} = ['GTN'];
$DEG_REV_CODON_TABLE{"W"} = ['TGG'];		$DEG_REV_CODON_TABLE{"Y"} = ['TAY'];		$DEG_REV_CODON_TABLE{"*"} = ['TAR', 'TGA'];

my %SCER_CODONS = (A => "GCT", C => "TGT", D => "GAC", E => "GAA", F => "TTC", G => "GGT", H => "CAC", I => "ATC", K => "AAG", L => "TTG", M => "ATG",
				N => "AAC", P => "CCA", Q => "CAA", R => "AGA", S => "TCT", T => "ACC", V => "GTT", W => "TGG", Y => "TAC", "*" => "TAA");

my %CODON_PERCENTAGES = ("AAA" => 0.08, "AAC" => 0.97, "AAG" => 0.92, "AAT" => 0.03, "ACA" => 0, "ACC" => 0.5375, "ACG" => 0.0025, "ACT" => 0.4575, "AGA" => 0.895, "AGC" => 0.0266666666666667, "AGG" => 0, "AGT" => 0.01, "ATA" => 0, "ATC" => 0.58, "ATG" => 1, "ATT" => 0.42, "CAA" => 0.99, "CAC" => 0.84, "CAG" => 0.01, "CAT" => 0.16, "CCA" => 0.9425, "CCC" => 0.005, "CCG" => 0, "CCT" => 0.0525, "CGA" => 0, "CGC" => 0, "CGG" => 0, 
						"CGT" => 0.105, "CTA" => 0.025, "CTC" => 0, "CTG" => 0.00333333333333333, "CTT" => 0.00333333333333333, "GAA" => 0.99, "GAC" => 0.65, "GAG" => 0.01, "GAT" => 0.35, "GCA" => 0.0075, "GCC" => 0.2225, "GCG" => 0, "GCT" => 0.7725, "GGA" => 0, "GGC" => 0.015, "GGG" => 0.005, "GGT" => 0.98, "GTA" => 0, "GTC" => 0.4775, "GTG" => 0.005, "GTT" => 0.5175, "TAA" => 0.333333333333333, "TAC" => 0.97, "TAG" => 0, "TAT" => 0.03, "TCA" => 0.0133333333333333, "TCC" => 0.403333333333333, "TCG" => 0.00333333333333333, "TCT" => 0.543333333333333, "TGA" => 0, "TGC" => 0.1, "TGG" => 1, "TGT" => 0.9, "TTA" => 0.0816666666666667, "TTC" => 0.905, "TTG" => 0.89, "TTT" => 0.095);

my $orf = "ATGGACAGATCTTGGAAGCAGAAGCTGAACCGCGACACCGTGAAGCTGACCGAGGTGATGACCTGGAGAAGACCCGCCGCTAAATGGTTTTATACTTTAATTAATGCTAATTATTTGCCACCATGCCCACCCGACCACCAAGATCACCGGCAGCAACAACTACCTGAGCCTGATCAGCCTGAACATCAACGGCCTGAACAGCCCCATCAAGCGGCACCGCCTGACCGACTGGCTGCACAAGCAGGACCCCACCTTCTGTTGCCTCCAGGAGACCCACCTGCGCGAGAAGGACCGGCACTACCTGCGGGTGAAGGGCTGGAAGACCATCTTTCAGGCCAACGGCCTGAAGAAGCAGGCTGGCGTGGCCATCCTGATCAGCGACAAGATCGACTTCCAGCCCAAGGTGATCAAGAAGGACAAGGAGGGCCACTTCATCCTGATCAAGGGCAAGATCCTGCAGGAGGAGCTGAGCATTCTGAACATCTACGCCCCCAACGCCCGCGCCGCCACCTTCATCAAGGACACCCTCGTGAAGCTGAAGGCCCACATCGCTCCCCACACCATCATCGTCGGCGACCTGAACACCCCCCTGAGCAGTGA";
my $orf_comp = "TACCTGTCTAGAACCTTCGTCTTCGACTTGGCGCTGTGGCACTTCGACTGGCTCCACTACTGGACCTCTTCTGGGCGGCGATTTACCAAAATATGAAATTAATTACGATTAATAAACGGTGGTACGGGTGGGCTGGTGGTTCTAGTGGCCGTCGTTGTTGATGGACTCGGACTAGTCGGACTTGTAGTTGCCGGACTTGTCGGGGTAGTTCGCCGTGGCGGACTGGCTGACCGACGTGTTCGTCCTGGGGTGGAAGACAACGGAGGTCCTCTGGGTGGACGCGCTCTTCCTGGCCGTGATGGACGCCCACTTCCCGACCTTCTGGTAGAAAGTCCGGTTGCCGGACTTCTTCGTCCGACCGCACCGGTAGGACTAGTCGCTGTTCTAGCTGAAGGTCGGGTTCCACTAGTTCTTCCTGTTCCTCCCGGTGAAGTAGGACTAGTTCCCGTTCTAGGACGTCCTCCTCGACTCGTAAGACTTGTAGATGCGGGGGTTGCGGGCGCGGCGGTGGAAGTAGTTCCTGTGGGAGCACTTCGACTTCCGGGTGTAGCGAGGGGTGTGGTAGTAGCAGCCGCTGGACTTGTGGGGGGACTCGTCACT";
my $fro = "TCACTGCTCAGGGGGGTGTTCAGGTCGCCGACGATGATGGTGTGGGGAGCGATGTGGGCCTTCAGCTTCACGAGGGTGTCCTTGATGAAGGTGGCGGCGCGGGCGTTGGGGGCGTAGATGTTCAGAATGCTCAGCTCCTCCTGCAGGATCTTGCCCTTGATCAGGATGAAGTGGCCCTCCTTGTCCTTCTTGATCACCTTGGGCTGGAAGTCGATCTTGTCGCTGATCAGGATGGCCACGCCAGCCTGCTTCTTCAGGCCGTTGGCCTGAAAGATGGTCTTCCAGCCCTTCACCCGCAGGTAGTGCCGGTCCTTCTCGCGCAGGTGGGTCTCCTGGAGGCAACAGAAGGTGGGGTCCTGCTTGTGCAGCCAGTCGGTCAGGCGGTGCCGCTTGATGGGGCTGTTCAGGCCGTTGATGTTCAGGCTGATCAGGCTCAGGTAGTTGTTGCTGCCGGTGATCTTGGTGGTCGGGTGGGCATGGTGGCAAATAATTAGCATTAATTAAAGTATAAAACCATTTAGCGGCGGGTCTTCTCCAGGTCATCACCTCGGTCAGCTTCACGGTGTCGCGGTTCAGCTTCTGCTTCCAAGATCTGTCCAT";
my $revorf = "ATGGACAGATCTTGGAAGCAAAAGTTGAACAGAGACACCGTTAAGTTGACCGAAGTTATGACCTGGAGAAGACCAGCTGCTAAGTGGTTCTACACCTTGATCAACGCTAACTACTTGCCACCATGTCCACCAGACCACCAAGACCACAGACAACAACAATTGCCAGAACCAGACCAACCAGAACACCAAAGACCAGAACAACCACACCAAGCTGCTCCACCAGACAGATTGGCTGCTCAAGCTGGTCCACACTTGTTGTTGCCACCAGGTGACCCACCAGCTAGAGAAGGTCCAGCTTTGCCAGCTGGTGAAGGTTTGGAAGACCACTTGTCTGGTCAAAGACCAGAAGAAGCTGGTTGGAGAGGTCACCCAGACCAAAGACAAGACAGATTGCCAGCTCAAGGTGACCAAGAAGGTCAAGGTGGTCCATTGCACCCAGACCAAGGTCAAGACCCAGCTGGTGGTGCTGAACACTCTGAACACTTGAGACCACAAAGACCAAGAAGACACTTGCACCAAGGTCACCCAAGAGAAGCTGAAGGTCCACACAGATCTCCACACCACCACAGAAGAAGACCAGAACACCCACCAGAACAATAA";
my $busted = "ATGGAYMGNWSNTGGAARCARAARYTNAAYMGNGAYACNGTNAARYTNACNGARGTNATGACNTGGMGNMGNCCNGCNGCNAARTGGTTYTAYACNYTNATHAAYGCNAAYTAYYTNCCNCCNTGYCCNCCNGAYCAYCARGAYCAYMGNCARCARCARYTNCCNGARCCNGAYCARCCNGARCAYCARMGNCCNGARCARCCNCAYCARGCNGCNCCNCCNGAYMGNYTNGCNGCNCARGCNGGNCCNCAYYTNYTNYTNCCNCCNGGNGAYCCNCCNGCNMGNGARGGNCCNGCNYTNCCNGCNGGNGARGGNYTNGARGAYCAYYTNWSNGGNCARMGNCCNGARGARGCNGGNTGGMGNGGNCAYCCNGAYCARMGNCARGAYMGNYTNCCNGCNCARGGNGAYCARGARGGNCARGGNGGNCCNYTNCAYCCNGAYCARGGNCARGAYCCNGCNGGNGGNGCNGARCAYWSNGARCAYYTNMGNCCNCARMGNCCNMGNMGNCAYYTNCAYCARGGNCAYCCNMGNGARGCNGARGGNCCNCAYMGNWSNCCNCAYCAYCAYMGNMGNMGNCCNGARCAYCCNCCNGARCARTRR";
my $detsub = "YYAYTGYTCNGGNGGRTGYTCNGGNCKNCKNCKRTGRTGRTGNGGNSWNCKRTGNGGNCCYTCNGCYTCNCKNGGRTGNCCYTGRTGNARRTGNCKNCKNGGNCKYTGNGGNCKNARRTGYTCNSWRTGYTCNGCNCCNCCNGCNGGRTCYTGNCCYTGRTCNGGRTGNARNGGNCCNCCYTGNCCYTCYTGRTCNCCYTGNGCNGGNARNCKRTCYTGNCKYTGRTCNGGRTGNCCNCKCCANCCNGCYTCYTCNGGNCKYTGNCCNSWNARRTGRTCYTCNARNCCYTCNCCNGCNGGNARNGCNGGNCCYTCNCKNGCNGGNGGRTCNCCNGGNGGNARNARNARRTGNGGNCCNGCYTGNGCNGCNARNCKRTCNGGNGGNGCNGCYTGRTGNGGYTGYTCNGGNCKYTGRTGYTCNGGYTGRTCNGGYTCNGGNARYTGYTGYTGNCKRTGRTCYTGRTGRTCNGGNGGRCANGGNGGNARRTARTTNGCRTTDATNARNGTRTARAACCAYTTNGCNGCNGGNCKNCKCCANGTCATNACYTCNGTNARYTTNACNGTRTCNCKRTTNARYTTYTGYTTCCANSWNCKRTCCAT";
my $shortorf = "ATGGACAGATCTTGGAAGCAGAAGCTGAACCGC";
my $shortaddorf = "ATGGACCGGAGCTGGAAGCAGAAGCTGAACCGC";
my $shortmessy = "\"ATGGAC>fastaTCttg ecZAGGWXYNNRB";
my $shortclean = "ATGGACASTATCTTGCAGGWYNNRB";
my $shortcleanstrict = "ATGGACATATCTTGCAGG";
my $fasta = ">holy crap, this sequence is awesome and starts with ATGG\nATGGACAGATCTTGGAAGCAGAAGCTGAACCGC\n";
my @shortmelt = [0, 28, 60.5695687386446, 62.8422960113718, 66.6428506098526];
my $rlshortorf =  "ATGGACAGAT";
my $rlshortbust = "RYSKAMDVWB";
my $rlshortwrng = "RRSKAMDVWB";
my $shortamb = "ABGCDT";
my %transcamb = map {$_ => 1} qw(ACGCAT AGGCAT ATGCAT ACGCGT AGGCGT ATGCGT ACGCTT AGGCTT ATGCTT);
my $rlessshortbust = "ARYSKAMDVWBG";
my $shortbusted = "ABCDGHKMNRSTVWXY";
my $shortbustedreg = "A[BCGKSTY]C[ADGKRTW]G[ACHMTWY][GKT][ACM][ABCDGHKMNRSTVWY][AGR][CGS]T[ACGMRSV][ATW][X][CTY]";
my $orfmap = [[1, 0, 199], [2, 34, 165], [-1, 11, 27], [-1, 39, 50]];
my %pospeps = map {$_ => 1} qw(ML MH MR TL TH TR RL RH RR YAF YAL YAC YAS YAY YA* YAW *AF *AL *AC *AS *AY *A* *AW HAF HAL HAC HAS HAY HA* HAW QAF QAL QAC QAS QAY QA* QAW NAF NAL NAC NAS NAY NA* NAW KAF KAL KAC KAS KAY KA* KAW DAF DAL DAC DAS DAY DA* DAW EAF EAL EAC EAS EAY EA* EAW LCF LCL LCI LCM LCV LRF LRL LRI LRM LRV LGF LGL LGI LGM LGV SCF SCL SCI SCM SCV SRF SRL SRI SRM SRV SGF SGL SGI SGM SGV *CF *CL *CI *CM *CV *RF *RL *RI *RM *RV *GF *GL *GI *GM *GV PCF PCL PCI PCM PCV PRF PRL PRI PRM PRV PGF PGL PGI PGM PGV QCF QCL QCI QCM QCV QRF QRL QRI QRM QRV QGF QGL QGI QGM QGV RCF RCL RCI RCM RCV RRF RRL RRI RRM RRV RGF RGL RGI RGM RGV ICF ICL ICI ICM ICV IRF IRL IRI IRM IRV IGF IGL IGI IGM IGV TCF TCL TCI TCM TCV TRF TRL TRI TRM TRV TGF TGL TGI TGM TGV KCF KCL KCI KCM KCV KRF KRL KRI KRM KRV KGF KGL KGI KGM KGV VCF VCL VCI VCM VCV 
								VRF VRL VRI VRM VRV VGF VGL VGI VGM VGV ACF ACL ACI ACM ACV ARF ARL ARI ARM ARV AGF AGL AGI AGM AGV ECF ECL ECI ECM ECV ERF ERL ERI ERM ERV EGF EGL EGI EGM EGV GCF GCL GCI GCM GCV GRF GRL GRI GRM GRV GGF GGL GGI GGM GGV);

my $peptide = "MDRSWKQKLNRDTVKLTEVMTWRRPAAKWFYTLINANYLPPCPPDHQDHRQQQLPEPDQPEHQRPEQPHQAAPPDRLAAQAGPHLLLPPGDPPAREGPALPAGEGLEDHLSGQRPEEAGWRGHPDQRQDRLPAQGDQEGQGGPLHPDQGQDPAGGAEHSEHLRPQRPRRHLHQGHPREAEGPHRSPHHHRRRPEHPPEQ*";
my $eptide = "WTDLGSRS*TATP*S*PR**PGEDPPLNGFIL*LMLIICHHAHPTTKITGSNNYLSLISLNINGLNSPIKRHRLTDWLHKQDPTFCCLQETHLREKDRHYLRVKGWKTIFQANGLKKQAGVAILISDKIDFQPKVIKKDKEGHFILIKGKILQEELSILNIYAPNARAATFIKDTLVKLKAHIAPHTIIVGDLNTPLSS";
my $ptide = "GQILEAEAEPRHREADRGDDLEKTRR*MVLYFN*C*LFATMPTRPPRSPAATTT*A*SA*TSTA*TAPSSGTA*PTGCTSRTPPSVASRRPTCARRTGTTCG*RAGRPSFRPTA*RSRLAWPS*SATRSTSSPR*SRRTRRATSS*SRARSCRRS*AF*TSTPPTPAPPPSSRTPS*S*RPTSLPTPSSSAT*TPP*AV";
my $editpep = "SLLRGVFRSPTMMVWGAMWAFSFTRVSLMKVAARALGA*MFRMLSSSCRILPLIRMKWPSLSFLITLGWKSILSLIRMATPACFFRPLA*KMVFQPFTRR*CRSFSRRWVSWRQQKVGSCLCSQSVRRCRLMGLFRPLMFRLIRLR*LLLPVILVVGWAWWQIISIN*SIKPFSGGSSPGHHLGQLHGVAVQLLLPRSVH";
my $ditpep = "HCSGGCSGRRR*WCGERCGPSASRGCP**RWRRGRWGRRCSECSAPPAGSCP*SG*SGPPCPS*SPWAGSRSCR*SGWPRQPASSGRWPERWSSSPSPAGSAGPSRAGGSPGGNRRWGPACAASRSGGAA*WGCSGR*CSG*SGSGSCCCR*SWWSGGHGGK*LALIKV*NHLAAGLLQVITSVSFTVSRFSFCFQDLS";
my $itpep = "TAQGGVQVADDDGVGSDVGLQLHEGVLDEGGGAGVGGVDVQNAQLLLQDLALDQDEVALLVLLDHLGLEVDLVADQDGHASLLLQAVGLKDGLPALHPQVVPVLLAQVGLLEATEGGVLLVQPVGQAVPLDGAVQAVDVQADQAQVVVAAGDLGGRVGMVANN*H*LKYKTI*RRVFSRSSPRSASRCRGSASASKICP";
my $shortpep = "MDRSWKQKLNRDTVKLTEVMTWR*";
my $shortpepreg = "MDRSWKQKLNRDTVKLTEVMTWR[\*]";
my $shortmessypep = "MDRSWKxbjQKLNRDTVBZKLTEVMTW!& R*";
my @stops = (9, 14, 16, 19, 20, 33);
my %orf_true = ("A" => 159, "T" => 95, "C" => 197, "G" => 149, "R" => 0, "Y" => 0, "W" => 0, "S" => 0, "M" => 0, "K" => 0, "B" => 0, "D" => 0, "H" => 0, "V" => 0, "U" => 0, "N" => 0, "length" => 600, "?" => 0, "d" => 600, "n" => 0, "GCp" => 58, "ATp" => 42);
my %busted_true = ("A" => 91, "T" => 31, "C" => 125, "G" => 113, "R" => 43, "Y" => 54, "W" => 4, "S" => 4, "M" => 21, "K" => 0, "B" => 0, "D" => 0, "H" => 1, "V" => 0, "U" => 0, "N" => 113, "length" => 600, "?" => 0, "d" => 360, "n" => 240, "GCp" => 60, "ATp" => 40);


my %RE_positions = ("AarI" => [275], "AciI" => [30, 74, 77, 211, 217, 304, 499, 504], "AcuI" => [344, 536], "AleI" => [523], "AluI" => [23, 44, 465, 534], "AlwI" => [451], "AlwNI" => [19], "AseI" => [100], "AvaII" => [244, 289], "BanI" => [213], "BbsI" => [68, 319], "BbvI" => [150, 232], "BccI" => [204, 324, 366, 561], "BceAI" => [189, 339], "BclI" => [171, 372, 405, 438], "BfuAI" => [276, 300], "BglII" => [7], "BlpI" => [466], "BpmI" => [63, 263], "Bpu10I" => [163, 589], "BsaI" => [269], "BsaJI" => [50, 399], "BseMII" => [164, 467, 590], "BseRI" => [461], "BsgI" => [233], "BslI" => [77, 204, 394, 436, 454], "BsmAI" => [269], "BsmI" => [471], "BspCNI" => [164, 467, 590], "BspMI" => [276, 300], "BsrFI" => [146, 291], "BsrI" => [228], "BssKI" => [62, 265], "BssSI" => [527], "BstAPI" => [295], "BstNI" => [62, 265], "BstUI" => [31, 281, 500], "BstYI" => [7, 450], "BtgZI" => [547], "BtsCI" => [367, 433], "BtsI" => [594], 
					"Cac8I" => [352, 356, 497], "CviAII" => [122], "CviKI" => [23, 44, 167, 176, 191, 200, 231, 314, 334, 341, 355, 364, 396, 425, 465, 534, 541], "DdeI" => [164, 467, 590], "DpnI" => [8, 142, 172, 373, 385, 406, 439, 451], "DpnII" => [8, 142, 172, 373, 385, 406, 439, 451], "EaeI" => [363], "Eco31I" => [269], "Eco57MI" => [63, 263, 344, 536], "EcoNI" => [436, 454], "EcoO109I" => [243], "EcoRII" => [62, 265], "FatI" => [122], "FauI" => [73, 304, 498], "Fnu4HI" => [76, 150, 211, 232, 503], "FokI" => [367, 433], "HaeIII" => [191, 334, 341, 364, 425, 541], "HhaI" => [280, 501], "HinP1I" => [280, 501], "HpaII" => [147, 292], "HphI" => [54, 144, 307, 403], "Hpy188I" => [475], "Hpy188III" => [369, 408, 435, 528], "Hpy99I" => [568], "HpyAV" => [252, 286, 310, 412, 510, 538], "HpyCH4III" => [37], "HpyCH4V" => [234, 456], "MboII" => [68, 319, 346], 
					"MnlI" => [52, 262, 422, 461, 526], "MscI" => [363], "MseI" => [97, 101], "MslI" => [523], "MwoI" => [168, 192, 232, 295, 356, 457, 488, 497, 542], "NlaIII" => [122], "NlaIV" => [213, 244], "PacI" => [97], "PfoI" => [264], "PpuMI" => [243], "PspGI" => [62, 265], "PstI" => [455], "Sau96I" => [244, 289, 424, 541], "SbfI" => [454], "ScrFI" => [62, 265], "SfcI" => [455], "StyI" => [399], "TaqI" => [387], "TauI" => [76, 211, 503], "TseI" => [150, 232], "Tsp509I" => [99, 109], "TspDTI" => [431, 512], "TspRI" => [593], "XhoII" => [7, 450]);
$RE_positions{$_} = [] foreach qw(AatII Acc65I AccI AclI AfeI AflII AflIII AgeI AhdI ApaI ApaLI ApoI AscI AsiSI AsuII AvaI AvrII BaeGI BamHI BanII BbvCI BciVI BfaI BglI BmgBI BmrI BmtI BpuEI BsaAI BsaBI BsaHI BsaWI BseYI BsiEI BsiHKAI BsiWI BsmBI BsmFI BsoBI Bsp1286I BspEI BspHI BspQI BsrBI BsrDI BsrGI BssHII BstBI BstEII BstXI BstZ17I Bsu36I BtgI BtrI ClaI CviQI DraI DraIII DrdI EagI EarI EciI Eco53KI EcoP15I EcoRI EcoRV Esp3I FseI FspAI FspI HaeII HgaI HincII HindIII HinfI HpaI Hpy166II HpyCH4IV KasI KpnI MaeI MaeII MaeIII MfeI MluI MlyI MmeI MspA1I NaeI NarI NciI NcoI NdeI NgoMIV NheI NmeAIII NsiI NotI NruI NspI PasI PciI PflFI PflMI PleI PmeI PshAI PsiI PspOMI PspXI PvuI PvuII RsaI RsrII SacI SacII SalI SanDI ScaI SexAI SfaNI SfiI SfoI SgrAI SmaI SmlI SnaBI SpeI SphI SrfI SspI StuI SwaI TaiI TatI TfiI Tsp45I TspGWI TspMI Tth111I XbaI XcmI XhoI XmaI XmnI ZraI);
my %RE_status = map {$_ => scalar(@{$RE_positions{$_}})} keys %RE_positions;

my %codshuffle = (1 => "ATGGACAGATCTTGGAAGCAAAAGTTGAACAGA", 2 => "ATGGATCGTTCCTGGAAACAAAAATTGAATAGA", 3 => "ATGGATCGTAGCTGGAAACAAAAATTAAATAGA", 4 => "ATGGATAGATCCTGGAAGCAGAAGCTTAACCGA");

my %orf_codoncount_true = ("TTT" => 1, "TTA" => 1, "TTG" => 2, "CTT" => 5, "CTA" => 3, "CTG" => 5, "ATT" => 1, "ATG" => 2, "GTG" => 2, "TCT" => 2, "TCC" => 1, "TCA" => 1, "CCT" => 15, "CCC" => 6, "CCA" => 9, "CCG" => 3, "ACT" => 1, "ACC" => 3, "GCT" => 5, "GCC" => 2, "GCA" => 6, "GCG" => 3, "TAT" => 2, "CAT" => 11, "CAC" => 7, "CAA" => 15, "CAG" => 6, "AAT" => 2, "AAC" => 1, "AAA" => 1, "AAG" => 3, "GAT" => 7, "GAC" => 6, "GAA" => 12, "GAG" => 4, "TGC" => 1, "TGA" => 1, "TGG" => 4, "CGT" => 3, "CGC" => 6, "CGA" => 5, "CGG" => 4, "AGA" => 3, "GGT" => 2, "GGC" => 4, "GGA" => 8, "GGG" => 3, "XXX" => 0, ); 

my %orf_rscu_true = ("TTT" => "2.000", "TTA" => 0.375, "TTG" => "0.750", "CTT" => 1.875, "CTA" => 1.125, "CTG" => 1.875, "ATT" => "3.000", "ATG" => "1.000", "GTG" => "4.000", "TCT" => "3.000", "TCC" => "1.500", "TCA" => "1.500", "CCT" => 1.818, "CCC" => 0.727, "CCA" => 1.091, "CCG" => 0.364, "ACT" => "1.000", "ACC" => "3.000", "GCT" => "1.250", "GCC" => "0.500", "GCA" => "1.500", "GCG" => "0.750", "TAT" => "2.000", "CAT" => 1.222, "CAC" => 0.778, "CAA" => 1.429, "CAG" => 0.571, "AAT" => 1.333, "AAC" => 0.667, "AAA" => "0.500", "AAG" => "1.500", "GAT" => 1.077, "GAC" => 0.923, "GAA" => "1.500", "GAG" => "0.500", "TGC" => "2.000", "TGA" => "3.000", "TGG" => "1.000", "CGT" => 0.857, "CGC" => 1.714, "CGA" => 1.429, "CGG" => 1.143, "AGA" => 0.857, "GGT" => 0.471, "GGC" => 0.941, "GGA" => 1.882, "GGG" => 0.706, );

sub test_amb_transcription
{
	my $flags = 0;
	my %ttransamb = map {$_ =>1} amb_transcription($shortamb, $CODON_TABLE, undef);
	my %ttransambp = map {$_ =>1} amb_transcription($shortamb, $CODON_TABLE, "GTL");
	foreach (keys %transcamb)
	{
		if (! exists $ttransamb{$_})
		{
			$flags++;
#			print "\t$_ ($transcamb{$_}) not found in test data\n";
			
		}
	}
	foreach (keys %ttransamb)
	{
		if (! exists $transcamb{$_})
		{
			$flags++;
#			print "\t$_ ($ttransamb{$_}) not found in ref data\n";
		}
	}
#	print "\t$_, $ttransambp{$_}\n" foreach (keys %ttransambp);
	print "amb_transcription()\t\t failed $flags subtests\n";
	return $flags == 0	?	1	:	0;	
}

sub test_amb_translation
{
	my $flags = 0;
	my %tpospeps = map {$_ => 1} amb_translation($shortamb, $CODON_TABLE);
	foreach (keys %pospeps)
	{
		if (! exists $tpospeps{$_})
		{
			$flags++;
			print "\t$_ ($pospeps{$_}) not found in test data\n";
		}
	}
	foreach (keys %tpospeps)
	{
		if (! exists $pospeps{$_})
		{
			$flags++;
			print "\t$_ ($tpospeps{$_}) not found in ref data\n";
		}
	}
	print "amb_translation()\t\t failed $flags subtests\n";
	return $flags == 0	?	1	:	0;	
}

sub test_change_codons()
{
	my $flags = 0;
	$flags++ if ($shortorf eq change_codons($shortorf, $CODON_TABLE, $RSCU_VALUES, 0));
#	print "\t0:\t$shortorf\t", change_codons($shortorf, $CODON_TABLE, $RSCU_VALUES, 0), "\t$flags\n";
	foreach my $x (1..4)
	{	
		$flags++ if ($codshuffle{$x} ne change_codons($shortorf, $CODON_TABLE, $RSCU_VALUES, $x));
#		print "\t$x:\t$codshuffle{$x}\t", change_codons($shortorf, $CODON_TABLE, $RSCU_VALUES, $x), "\t$flags\n";
	}
	print "change_codons()\t\t\t failed $flags subtests\n";
	return $flags == 0	?	1	:	0;	
}

sub test_cleanup()
{
	my $flags = 0;
	$tcleanst = cleanup($shortmessy, 0);
	$tclean = cleanup($shortmessy, 1);
	$tcleanpep = cleanup($shortmessypep, 2);
	$tcleanfasta = cleanup($fasta, 1);
	$flags++ if ($tcleanst ne $shortcleanstrict);
	$flags++ if ($tclean ne $shortclean);
	$flags++ if ($tcleanpep ne $shortpep);
	$flags++ if ($tcleanfasta ne $shortorf);
	print "cleanup()\t\t\t failed $flags subtests\n";
	return $flags == 0	?	1	:	0;	
}

sub test_compareseqs()
{
	my $flags = 0;
	my $tcomp1 = compareseqs($rlshortorf, $rlshortbust);
	my $tcomp2 = compareseqs($rlshortbust, $rlshortorf);
	my $tcomp3 = compareseqs($rlshortwrng, $rlshortorf);
	my $tcomp4 = compareseqs($rlessshortbust, $rlshortorf);
	$flags++ if $tcomp1 != 1;
	$flags++ if $tcomp2 != 1;
	$flags++ if $tcomp3 == 1;
	$flags++ if $tcomp4 == 1;
	print "compareseqs()\t\t\t failed $flags subtests\n";
	return $flags == 0	?	1	:	0;
}

sub test_complement()
{
	my $flags = 0;
	my $tfro = complement($orf, 1);
	my $tfro2 = complement($orf);
	my $tdets = complement($busted, 1);
	my $utest = complement();
	$flags++ if ($utest ne undef);
	$flags++ if ($tfro ne $fro);
	$flags++ if ($tfro2 ne $orf_comp);
	$flags++ if ($tdets ne $detsub);
	print "complement()\t\t\t failed $flags subtests\n";
	return $flags == 0	?	1	:	0;
}

sub test_count()
{
	my $torf_count = count($orf);
	my $bust_count = count($busted);
	my $flags = 0;
	foreach (keys %$torf_count)
	{
		if ($$torf_count{$_} ne $orf_true{$_})
		{
			$flags++;
			print "\tTrue: $_ ", "$$torf_count{$_} ne $orf_true{$_}\n";
			
		}
	}
	foreach (keys %$bust_count)
	{
		if ($$bust_count{$_} ne $busted_true{$_})
		{
			$flags++;
			print "\tBust: $_ ", "$$bust_count{$_} ne $busted_true{$_}\n";
		}
	}
	print "count()\t\t\t\t failed $flags subtests\n";
	return $flags == 0	?	1	:	0;
}

sub test_define_aa_defaults()
{
	my $flags = 0;
	my %tAA_DEFAULTS = define_aa_defaults($CODON_TABLE, $RSCU_VALUES);
	foreach (keys %tAA_DEFAULTS)
	{
		$flags++ if ($tAA_DEFAULTS{$_} ne $SCER_CODONS{$_});
	}
	print "define_aa_defaults()\t\t failed $flags subtests\n";
	return $flags == 0	?	1	:	0;
}

sub test_define_codon_percentages
{
	my $flags = 0;
	my %tPercentages = define_codon_percentages($CODON_TABLE, $RSCU_VALUES);
	foreach (keys %tPercentages)
	{
		if ($tPercentages{$_} ne $CODON_PERCENTAGES{$_})
		{
			$flags++ ;
			print "$_, $tPercentages{$_}, $CODON_PERCENTAGES{$_}\n";
		}
	}
	print "define_codon_percentages()\t failed $flags subtests\n";
	return $flags == 0	?	1	:	0;
}

sub test_define_site_status()
{
	my $flags = 0 ;
	my $tSITE_STATUS = define_site_status($orf, $$RE_DATA{REGEX});
	foreach (keys %RE_status)
	{
		if ($$tSITE_STATUS{$_} != $RE_status{$_})
		{
			$flags++;
			print "$_, $$tSITE_STATUS{$_} != $RE_status{$_}\n" 
		}
	}
	foreach (keys %$tSITE_STATUS)
	{
		if (! exists $RE_status{$_})
		{
			$flags++ ;
			print "$_ not found in canon\n";
		}
	}
	foreach (keys %RE_status)
	{
		if (! exists $$tSITE_STATUS{$_})
		{
			$flags++;
			print "$_ not found in test\n";
		}
	}
	print "define_site_status()\t\t failed $flags subtests\n";
	return $flags == 0	?	1	:	0;
}

sub test_define_reverse_codon_table()
{
	my $flags = 0;
	my $tREV_CODON_TABLE = define_reverse_codon_table($CODON_TABLE);
	foreach (keys %{$REV_CODON_TABLE})
	{
		my %isect = {}; 
		my %union = {};
		foreach (@{$$REV_CODON_TABLE{$_}}, @{$$REV_CODON_TABLE{$_}}) { $union{$_}++ && $isect{$_}++ }
		$flags++ if ((keys %isect)-0 != (keys %union)-0);
	}
	print "define_reverse_codon_table()\t failed $flags subtests\n";
	return $flags == 0	?	1	:	0;
}

sub test_degcodon_to_aas()
{
	my $flags = 0;
	foreach (keys %DEG_REV_CODON_TABLE)
	{
		$flags++ if $_ != degcodon_to_aas($DEG_REV_CODON_TABLE{$_}, $CODON_TABLE);
	}
	print "degcodon_to_aas()\t\t failed $flags subtests\n";
	return $flags == 0	?	1	:	0;	
}

sub test_melt()
{
	my $tmelt1 = melt($rlshortorf, 1);
	my $tmelt2 = melt($shortorf, 2);
	my $tmelt3 = melt($shortorf, 3);
	my $tmelt4 = melt($shortorf, 4);
	my $utest = melt();
	$flags++ if ($utest ne undef);
	$flags++ if ($tmelt1 != $shortmelt[1]);
	$flags++ if ($tmelt2 != $shortmelt[2]);
	$flags++ if ($tmelt3 != $shortmelt[3]);
	$flags++ if ($tmelt4 != $shortmelt[4]);
	my $flags = 0;
	print "melt()\t\t\t\t failed $flags subtests\n";
	return $flags == 0	?	1	:	0;
}

sub test_randDNA
{
	my $flags = 0;
	my $tnostops = randDNA(600, 60, 2, $CODON_TABLE);
	my $tstops = randDNA(600, 60, 1, $CODON_TABLE);
	my @stopcheck = pattern_finder($tnostops, "*", 2, 1, $CODON_TABLE);
	$flags++ if (@stopcheck-0 > 0);
	my $tbcnostops = count($tnostops);
	my $tbcstops = count($tstops);
	$flags++ if ($$tbcnostops{A} + $$tbcnostops{T} > 365 || $$tbcnostops{A} + $$tbcnostops{T} < 355);
	$flags++ if ($$tbcstops{A} + $$tbcstops{T} > 365 || $$tbcstops{A} + $$tbcstops{T} < 355);
	print "randDNA()\t\t\t failed $flags subtests\n";
	return $flags == 0	?	1	:	0;
}

sub test_reverse_translate
{
	my $flags = 0;
	my $trevorf = reverse_translate($peptide, \%SCER_CODONS);
	$flags++ if ($trevorf ne $revorf);
	print "reverse_translate()\t\t failed $flags subtests\n";
	return $flags == 0	?	1	:	0;
}

sub test_pattern_adder
{
	my $flags = 0;
	my $tnewshort = pattern_adder("GACAGATCT", "NNCCGGAGC", $CODON_TABLE);
	$flags++ if ($tnewshort ne "GACCGGAGC");
	print "pattern_adder()\t\t\t failed $flags subtests\n";
	return $flags == 0	?	1	:	0;
}

sub test_pattern_aligner
{
	my $flags = 0;
	my $tnewaligned = pattern_aligner("GACAGATCT", "CCGGAGC", "DRS", $CODON_TABLE);
	my $tnewaligned2 = pattern_aligner("GACAGATCT", "GACCGGA", "DRS", $CODON_TABLE);
	my $tnewaligned3 = pattern_aligner("GACAGATCT", "ACAGATC", "DRS", $CODON_TABLE);
	$flags++ if ($tnewaligned ne "NNCCGGAGC");
	$flags++ if ($tnewaligned2 ne "GACCGGANN");
	$flags++ if ($tnewaligned3 ne "NACAGATCN");
#	print "\n\t$tnewaligned\n\t$tnewaligned2\n\t$tnewaligned3\n";
	print "pattern_aligner()\t\t failed $flags subtests\n";
	return $flags == 0	?	1	:	0;
}

sub test_pattern_finder
{
	my $flags = 0;
	my @tstops = pattern_finder($orf, "*", 2, 2, $CODON_TABLE);
	$flags++ if ((@tstops - 0) != (@stops - 0));
	for (my $x = 0; $x < @tstops; $x++)
	{
		$flags++ if ($tstops[$x]+1 != $stops[$x]);
	}
	print "pattern_finder()\t\t failed $flags subtests\n";
	return $flags == 0	?	1	:	0;
}

sub test_pattern_remover()
{
	my $flags = 0;
	my $tnewshort = pattern_remover("GACAGATCT", "CAGATCT", $CODON_TABLE, $RSCU_VALUES);
	$flags++ if ($tnewshort ne "GATAGATCT");
	print "pattern_remover()\t\t failed $flags subtests\n";
	return $flags == 0	?	1	:	0;	
}

sub test_regres()
{
	my $tbreg = regres($shortbusted, 1);
	my $tpreg = regres($shortpep, 2);
	my $flags = 0;
	$flags++ if ($tbreg ne $shortbustedreg);
	$flags++ if ($tpreg ne $shortpepreg);
	print "regres()\t\t\t failed $flags subtests\n";
	return $flags == 0	?	1	:	0;
}

sub test_siteseeker()
{
	my $flags = 0;
	foreach (keys %RE_status)
	{
		$tpositions = siteseeker($orf, $$RE_DATA{CLEAN}->{$_}, $$RE_DATA{REGEX}->{$_});
		my @sing = sort {$a <=> $b} @{$RE_positions{$_}};
		my @tsing = sort {$a <=> $b} keys %{$tpositions};
		for ($x = 0; $x < scalar(@sing); $x++)
		{
			if ($sing[$x] != $tsing[$x]+1)
			{
				$flags++;
				print "\t$sing[$x] != $tsing[$x]\n";
			}
		}
		for ($x = 0; $x < scalar(@tsing); $x++)
		{
			if ($sing[$x] != $tsing[$x]+1)
			{
				$flags++;
				print "\t$sing[$x] != $tsing[$x]\n";
			}
		}
	}
	print "siteseeker()\t\t\t failed $flags subtests\n";
	return $flags == 0	?	1	:	0;	
}

sub test_translate()
{
	my $tpeptide = translate($orf, 1, $CODON_TABLE);
	my $teptide = translate($orf, 2, $CODON_TABLE);
	my $tptide = translate($orf, 3, $CODON_TABLE);
	my $teditpep = translate($orf, -1, $CODON_TABLE);
	my $tditpep = translate($orf, -2, $CODON_TABLE);
	my $titpep = translate($orf, -3, $CODON_TABLE);
	my $flags = 0;
	$flags++ if ($tpeptide ne $peptide);
	$flags++ if ($teptide ne $eptide);
	$flags++ if ($tptide ne $ptide);
	$flags++ if ($teditpep ne $editpep);
	$flags++ if ($tditpep ne $ditpep);
	$flags++ if ($titpep ne $itpep);
	print "translate()\t\t\t failed $flags subtests\n";
	return $flags == 0	?	1	:	0;
}

sub test_orf_finder()
{
	my $flags = 0;
	my $torfmap = orf_finder($orf, $CODON_TABLE);
	for my $x (0..scalar(@$torfmap))
	{
		for my $y ( 0..scalar(@{$$torfmap[$x]}) )
		{
			$flags++ if ($$torfmap[$x]->[$y] != $$orfmap[$x]->[$y]);
		}
	}
	print "test_orf_finder()\t\t failed $flags subtests\n";
	return $flags == 0	?	1	:	0;
}

#Paul Nunley
sub test_codon_count()
{
	my $flags = 0;
	my $test_count = codon_count([$orf], $CODON_TABLE);
	foreach (keys %$test_count)
	{
		if ($$test_count{$_} != $orf_codoncount_true{$_})
		{
			$flags++;
			print "$_ ";
			print "$$test_count{$_}\t\t$orf_codoncount_true{$_}\n";
		}
	}
	print "codon_count()\t\t\t failed $flags subtests\n";
	return $flags == 0	?	1	:	0;
}

#Paul Nunley
sub test_generate_RSCU_values()
{
	my $flags = 0;
	my $orfcodoncountref = codon_count([$orf]);
	my $tRSCU = generate_RSCU_values($orfcodoncountref, $CODON_TABLE);
	foreach (sort keys %$tRSCU)
	{
		if ($$tRSCU{$_} ne $orf_rscu_true{$_})
		{
			$flags++;
			print "$_\t";
			print "$$tRSCU{$_}\t\t$orf_rscu_true{$_}\n";
		}
	}
	print "generate_RSCU_values()\t\t failed $flags subtests\n";
	return $flags == 0	?	1	:	0;
}

sub test_random_pattern_remover()
{
	my $flags = 0;
	my $nucseq = $shortorf;
	my @remove_RE = ("AciI", "AluI", "AlwNI", "BglII");
	my $newcritseg;

        for (1..5) {
		foreach my $enz (@remove_RE) {
			my $temphash = siteseeker($nucseq, $enz, $$RE_DATA{REGEX}->{$enz});
			foreach my $grabbedpos (keys %$temphash) {
				my $grabbedseq = $$temphash{$grabbedpos};
				my $framestart = ($grabbedpos) % 3;
				my $critseg = substr($nucseq, $grabbedpos - $framestart, ((int(length($grabbedseq)/3 + 2))*3));
				$newcritseg = random_pattern_remover($critseg, $$RE_DATA{CLEAN}->{$enz}, $CODON_TABLE);
				substr($nucseq, $grabbedpos - $framestart, length($newcritseg)) = $newcritseg if (scalar( keys %{siteseeker($newcritseg, $enz, $$RE_DATA{REGEX}->{$enz})}) == 0);
			}
		}
	}
	
	foreach my $enz (@remove_RE){
		if (scalar( keys %{siteseeker($newcritseg, $enz, $$RE_DATA{REGEX}->{$enz})} ) != 0) {
			$flags++;
		}
	}
	
	print "random_pattern_remover()\t failed $flags subtests\n";
	return $flags == 0	?	1	:	0;
}

sub test_replace_lock()
{
	my $flags = 0;
	my $oldnuc = $shortorf;
	my $newnuc = "ATGGACCGATCTTGGAAGCAAAAACTGAATCGC";
	my @lockseq = ("15-24", "27-29");
	
	($newnuc, @lockseq) = replace_lock($oldnuc, $newnuc, $CODON_TABLE, @lockseq);
	
	$flags++ if ($newnuc ne "ATGGACCGATCTTGGAAGCAGAAGCTGAATCGC");
	
	print "test_replace_lock()\t\t failed $flags subtests\n";
	return $flags ==0	?	1	:	0;
}

sub test_check_lock()
{
	my $flags = 0;
	my $newnuc = "ATGGACCGATCTTGGAAGCAGAAGCTGAATCGC";
	my @remove_RE = ("AciI", "AluI", "AlwNI", "BglII");
	my @lockseq = ("15-24", "27-29");
	my %lock_enz = ();
	foreach my $enz (@remove_RE)
	{
		my $newcheckpres = siteseeker($newnuc, $enz, $$RE_DATA{REGEX}->{$enz});
		if ( scalar ( keys %$newcheckpres ) != 0 )
		{
			$lock_enz{$enz} = 0;
			%lock_enz = check_lock($newcheckpres, $enz, \@lockseq, %lock_enz);
		}
	}
	$flags++ if ($lock_enz{"AluI"} != 2);
	
	$flags++ if ($lock_enz{"AlwNI"} != 1);
	
	$flags++ if ($lock_enz{"AciI"} != 0);
	
	$flags++ if ($lock_enz{"BglII"} != 0);
	
	print "test_check_lock()\t\t failed $flags subtests\n";
	return $flags ==0	?	1	:	0;
}