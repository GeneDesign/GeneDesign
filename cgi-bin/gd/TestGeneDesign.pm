package TestGeneDesign;
use 5.006;
require Exporter;
use GeneDesign;
use ResSufTree;

@ISA = qw(Exporter);
@EXPORT = qw(test_amb_transcription test_amb_translation test_change_codons test_cleanup test_compareseqs test_complement test_count test_define_site_status 
			test_define_aa_defaults test_define_codon_percentages test_define_reverse_codon_table test_degcodon_to_aas test_melt test_orf_finder
			test_pattern_adder test_pattern_aligner test_pattern_finder test_pattern_remover test_randDNA test_regres test_reverse_translate test_siteseeker test_translate
			test_codon_count test_generate_RSCU_values);

my $CODON_TABLE = define_codon_table(1);	
my $RSCU_VALUES = define_RSCU_values(1);

#print "$_:\t$$RSCU_VALUES{$_}\n" foreach (keys %$RSCU_VALUES);

my $RE_DATA = define_sites("</Library/WebServer/CGI-Executables/gd2/newenz.txt");	

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

my %CODON_PERCENTAGES = ("AAA" => 0.08, "AAC" => 0.97, "AAG" => 0.92, "AAT" => 0.03, "ACA" => 0, "ACC" => 0.5375, "ACG" => 0.0025, "ACT" => 0.4575, "AGA" => 0.895, "AGC" => 0.0266666666666667, "AGG" => 0, "AGT" => 0.01, "ATA" => 0, "ATC" => 0.58, "ATG" => 1, "ATT" => 0.42, "CAA" => 0.99, "CAC" => 0.84, "CAG" => 0.01, "CAT" => 0.16, "CCA" => 0.9425, "CCC" => 0.005, "CCG" => 0, "CCT" => 0.0525, "CGA" => 0, "CGC" => 0, "CGG" => 0, "CGT" => 0.105, "CTA" => 0.025, "CTC" => 0, "CTG" => 0.00333333333333333, "CTT" => 0.00333333333333333, "GAA" => 0.99, "GAC" => 0.65, "GAG" => 0.01, "GAT" => 0.35, "GCA" => 0.0075, "GCC" => 0.2225, "GCG" => 0, "GCT" => 0.7725, "GGA" => 0, "GGC" => 0.015, "GGG" => 0.005, "GGT" => 0.98, "GTA" => 0, "GTC" => 0.4775, "GTG" => 0.005, "GTT" => 0.5175, "TAA" => 0.333333333333333, "TAC" => 0.97, "TAG" => 0, "TAT" => 0.03, "TCA" => 0.0133333333333333, "TCC" => 0.403333333333333, "TCG" => 0.00333333333333333, "TCT" => 0.543333333333333, "TGA" => 0, "TGC" => 0.1, "TGG" => 1, "TGT" => 0.9, "TTA" => 0.0816666666666667, "TTC" => 0.905, "TTG" => 0.89, "TTT" => 0.095);

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
my %pospeps = map {$_ => 1} qw(ML MH MR TL TH TR RL RH RR YAF YAL YAC YAS YAY YA* YAW *AF *AL *AC *AS *AY *A* *AW HAF HAL HAC HAS HAY HA* HAW QAF QAL QAC QAS QAY QA* QAW NAF NAL NAC NAS NAY NA* NAW KAF KAL KAC KAS KAY KA* KAW DAF DAL DAC DAS DAY DA* DAW EAF EAL EAC EAS EAY EA* EAW LCF LCL LCI LCM LCV LRF LRL LRI LRM LRV LGF LGL LGI LGM LGV SCF SCL SCI SCM SCV SRF SRL SRI SRM SRV SGF SGL SGI SGM SGV *CF *CL *CI *CM *CV *RF *RL *RI *RM *RV *GF *GL *GI *GM *GV PCF PCL PCI PCM PCV PRF PRL PRI PRM PRV PGF PGL PGI PGM PGV QCF QCL QCI QCM QCV QRF QRL QRI QRM QRV QGF QGL QGI QGM QGV RCF RCL RCI RCM RCV RRF RRL RRI RRM RRV RGF RGL RGI RGM RGV ICF ICL ICI ICM ICV IRF IRL IRI IRM IRV IGF IGL IGI IGM IGV TCF TCL TCI TCM TCV TRF TRL TRI TRM TRV TGF TGL TGI TGM TGV KCF KCL KCI KCM KCV KRF KRL KRI KRM KRV KGF KGL KGI KGM KGV VCF VCL VCI VCM VCV VRF VRL VRI VRM VRV VGF VGL VGI VGM VGV ACF ACL ACI ACM ACV ARF ARL ARI ARM ARV AGF AGL AGI AGM AGV ECF ECL ECI ECM ECV ERF ERL ERI ERM ERV EGF EGL EGI EGM EGV GCF GCL GCI GCM GCV GRF GRL GRI GRM GRV GGF GGL GGI GGM GGV);

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


my %RE_status = ("AarI" => 1, "AatII" => 0, "AccI" => 0, "AciI" => 8, "AclI" => 0, "AcyI" => 0, "AflII" => 0, "AflIII" => 0, "AgeI" => 0, "AluI" => 4, "AlwI" => 1, "AlwNI" => 1, "ApaI" => 0, "ApaLI" => 0, "ApoI" => 0, "AscI" => 0, "Asp718I" => 0, "AsuII" => 0, "AvaI" => 0, "AvaII" => 2, "AvrII" => 0, "BalI" => 1, "BamHI" => 0, "BanI" => 1, "BanII" => 0, "BbeI" => 0, "BbsI" => 2, "BbvCI" => 0, "BbvI" => 2, "BccI" => 4, "BceAI" => 2, "BciVI" => 0, "BclI" => 4, "BfrBI" => 0, "BglI" => 0, "BglII" => 1, "BisI" => 5, "BlpI" => 1, "Bpu10I" => 2, "BpuEI" => 0, "BsaAI" => 0, "BsaBI" => 0, "BsaJI" => 2, "BsaWI" => 0, "BseMII" => 3, "BseRI" => 1, "BseSI" => 0, "BseYI" => 0, "BsgI" => 1, "BsiEI" => 0, "BsiHKAI" => 0, "BsiYI" => 5, "BsmAI" => 1, "BsmI" => 1, "Bsp120I" => 0, "Bsp1407I" => 0, "BspEI" => 0, "BspHI" => 0, "BspLU11I" => 0, "BspMI" => 2, "BsrBI" => 0, "BsrDI" => 0, "BsrI" => 1, "BssHII" => 0, "BssSI" => 1, "Bst1107I" => 0, "BstAPI" => 1, "BstEII" => 0, "BstF5I" => 2, "BstNI" => 2, "BstUI" => 3, "BstXI" => 0, "Bsu36I" => 0, "BtgI" => 0, "BtgZI" => 1, 
				 "BtrI" => 0, "BtsI" => 1, "Cac8I" => 3, "Cfr10I" => 2, "CfrI" => 1, "ClaI" => 0, "CviAII" => 1, "CviJI" => 17, "DdeI" => 3, "DpnI" => 8, "DraI" => 0, "DraII" => 1, "DraIII" => 0, "DrdI" => 0, "EagI" => 0, "Eam1105I" => 0, "EciI" => 0, "Eco31I" => 1, "Eco47III" => 0, "Eco57I" => 2, "Eco57MI" => 4, "EcoICRI" => 0, "EcoNI" => 2, "EcoRI" => 0, "EcoRII" => 2, "EcoRV" => 0, "EcoT22I" => 0, "Esp3I" => 0, "FatI" => 1, "FauI" => 3, "Fnu4HI" => 5, "FokI" => 2, "FseI" => 0, "FspAI" => 0, "FspI" => 0, "GsuI" => 2, "HaeII" => 0, "HaeIII" => 6, "HgaI" => 0, "HhaI" => 2, "HinP1I" => 2, "HindII" => 0, "HindIII" => 0, "HinfI" => 0, "HpaI" => 0, "HpaII" => 2, "HphI" => 4, "Hpy188I" => 1, "Hpy188III" => 4, "Hpy8I" => 0, "Hpy99I" => 1, "HpyCH4III" => 1, "KasI" => 0, "KpnI" => 0, "Ksp632I" => 0, "MaeI" => 0, "MaeII" => 0, "MaeIII" => 0, "MboI" => 8, "MboII" => 3, "MfeI" => 0, "MluI" => 0, "MlyI" => 0, "MmeI" => 0, "MnlI" => 5, "MseI" => 2, "MslI" => 1, "MspA1I" => 0, "MwoI" => 9, "NaeI" => 0, "NarI" => 0, "NciI" => 0, "NcoI" => 0, "NdeI" => 0, "NheI" => 0, 
				 "NlaIII" => 1, "NlaIV" => 2, "NotI" => 0, "NruI" => 0, "NspI" => 0, "OliI" => 1, "PacI" => 1, "PasI" => 0, "PflMI" => 0, "PfoI" => 1, "PleI" => 0, "PmaCI" => 0, "PmeI" => 0, "PpuMI" => 1, "PshAI" => 0, "PsiI" => 0, "PspXI" => 0, "PstI" => 1, "PvuI" => 0, "PvuII" => 0, "RsaI" => 0, "RsrII" => 0, "SacI" => 0, "SacII" => 0, "SalI" => 0, "SanDI" => 0, "SapI" => 0, "Sau96I" => 4, "ScaI" => 0, "ScrFI" => 2, "SduI" => 0, "SexAI" => 0, "SfaNI" => 0, "SfcI" => 1, "SfiI" => 0, "SgfI" => 0, "SgrAI" => 0, "SmaI" => 0, "SmlI" => 0, "SnaBI" => 0, "SpeI" => 0, "SphI" => 0, "SrfI" => 0, "Sse8387I" => 1, "SspI" => 0, "StuI" => 0, "StyI" => 1, "SwaI" => 0, "TaiI" => 0, "TaqI" => 1, "TatI" => 0, "TauI" => 3, "TfiI" => 0, "TseI" => 2, "Tsp45I" => 0, "TspDTI" => 2, "TspEI" => 2, "TspGWI" => 0, "TspRI" => 1, "Tth111I" => 0, "VspI" => 1, "XbaI" => 0, "XcmI" => 0, "XhoI" => 0, "XhoII" => 2, "XmaI" => 0, "XmnI" => 0, "ZraI" => 0);

my %RE_positions = ("AarI" => [275], "AatII" => [], "AccI" => [], "AciI" => [30, 74, 77, 211, 217, 304, 499, 504], "AclI" => [], "AcyI" => [], "AflII" => [], "AflIII" => [], "AgeI" => [], "AluI" => [23, 44, 465, 534], "AlwI" => [451], "AlwNI" => [19], "ApaI" => [], "ApaLI" => [], "ApoI" => [], "AscI" => [], "Asp718I" => [], "AsuII" => [], "AvaI" => [], "AvaII" => [244, 289], "AvrII" => [], "BalI" => [363], "BamHI" => [], "BanI" => [213], "BanII" => [], "BbeI" => [], "BbsI" => [68, 319], "BbvCI" => [], "BbvI" => [150, 232], "BccI" => [204, 324, 366, 561], "BceAI" => [189, 339], "BciVI" => [], "BclI" => [171, 372, 405, 438], "BfrBI" => [], "BglI" => [], "BglII" => [7], "BisI" => [76, 150, 211, 232, 503], "BlpI" => [466], "Bpu10I" => [163, 589], "BpuEI" => [], "BsaAI" => [], "BsaBI" => [], "BsaJI" => [50, 399], "BsaWI" => [], "BseMII" => [164, 467, 590], "BseRI" => [461], "BseSI" => [], "BseYI" => [], "BsgI" => [233], "BsiEI" => [], "BsiHKAI" => [], "BsiYI" => [77, 204, 394, 436, 454], "BsmAI" => [269], "BsmI" => [471], "Bsp120I" => [], "Bsp1407I" => [],  
					"BspEI" => [], "BspHI" => [], "BspLU11I" => [], "BspMI" => [276, 300], "BsrBI" => [], "BsrDI" => [], "BsrI" => [228], "BssHII" => [], "BssSI" => [527], "Bst1107I" => [], "BstAPI" => [295], "BstEII" => [], "BstF5I" => [367, 433], "BstNI" => [62, 265], "BstUI" => [31, 281, 500], "BstXI" => [], "Bsu36I" => [], "BtgI" => [], "BtgZI" => [547], "BtrI" => [], "BtsI" => [594], "Cac8I" => [352, 356, 497], "Cfr10I" => [146, 291], "CfrI" => [363], "ClaI" => [], "CviAII" => [122], "CviJI" => [23, 44, 167, 176, 191, 200, 231, 314, 334, 341, 355, 364, 396, 425, 465, 534, 541], "DdeI" => [164, 467, 590], "DpnI" => [8, 142, 172, 373, 385, 406, 439, 451], "DraI" => [], "DraII" => [243], "DraIII" => [], "DrdI" => [], "EagI" => [], "Eam1105I" => [], "EciI" => [], "Eco31I" => [269], "Eco47III" => [], "Eco57I" => [344, 536], "Eco57MI" => [63, 263, 344, 536], "EcoICRI" => [], "EcoNI" => [436, 454], "EcoRI" => [], "EcoRII" => [62, 265], "EcoRV" => [], "EcoT22I" => [], "Esp3I" => [], "FatI" => [122], "FauI" => [73, 304, 498], "Fnu4HI" => [76, 150, 211, 232, 503], 
					"FokI" => [367, 433], "FseI" => [], "FspAI" => [], "FspI" => [], "GsuI" => [63, 263], "HaeII" => [], "HaeIII" => [191, 334, 341, 364, 425, 541], "HgaI" => [], "HhaI" => [280, 501], "HinP1I" => [280, 501], "HindII" => [], "HindIII" => [], "HinfI" => [], "HpaI" => [], "HpaII" => [147, 292], "HphI" => [54, 144, 307, 403], "Hpy188I" => [475], "Hpy188III" => [369, 408, 435, 528], "Hpy8I" => [], "Hpy99I" => [568], "HpyCH4III" => [37], "KasI" => [], "KpnI" => [], "Ksp632I" => [], "MaeI" => [], "MaeII" => [], "MaeIII" => [], "MboI" => [8, 142, 172, 373, 385, 406, 439, 451], "MboII" => [68, 319, 346], "MfeI" => [], "MluI" => [], "MlyI" => [], "MmeI" => [], "MnlI" => [52, 262, 422, 461, 526], "MseI" => [97, 101], "MslI" => [523], "MspA1I" => [], "MwoI" => [168, 192, 232, 295, 356, 457, 488, 497, 542], "NaeI" => [], "NarI" => [], "NciI" => [], "NcoI" => [], "NdeI" => [], "NheI" => [], "NlaIII" => [122], "NlaIV" => [213, 244], "NotI" => [], "NruI" => [], "NspI" => [], "OliI" => [523], "PacI" => [97], "PasI" => [], "PflMI" => [], "PfoI" => [264], 
					"PleI" => [], "PmaCI" => [], "PmeI" => [], "PpuMI" => [243], "PshAI" => [], "PsiI" => [], "PspXI" => [], "PstI" => [455], "PvuI" => [], "PvuII" => [], "RsaI" => [], "RsrII" => [], "SacI" => [], "SacII" => [], "SalI" => [], "SanDI" => [], "SapI" => [], "Sau96I" => [244, 289, 424, 541], "ScaI" => [], "ScrFI" => [62, 265], "SduI" => [], "SexAI" => [], "SfaNI" => [], "SfcI" => [455], "SfiI" => [], "SgfI" => [], "SgrAI" => [], "SmaI" => [], "SmlI" => [], "SnaBI" => [], "SpeI" => [], "SphI" => [], "SrfI" => [], "Sse8387I" => [454], "SspI" => [], "StuI" => [], "StyI" => [399], "SwaI" => [], "TaiI" => [], "TaqI" => [387], "TatI" => [], "TauI" => [76, 211, 503], "TfiI" => [], "TseI" => [150, 232], "Tsp45I" => [], "TspDTI" => [431, 512], "TspEI" => [99, 109], "TspGWI" => [], "TspRI" => [593], "Tth111I" => [], "VspI" => [100], "XbaI" => [], "XcmI" => [], "XhoI" => [], "XhoII" => [7, 450], "XmaI" => [], "XmnI" => [], "ZraI" => []);

my %codshuffle = (1 => "ATGGACAGATCTTGGAAGCAAAAGTTGAACAGA", 2 => "ATGGATCGTTCCTGGAAACAAAAATTGAATAGA", 3 => "ATGGATCGTAGCTGGAAACAAAAATTAAATAGA", 4 => "ATGGATAGATCCTGGAAGCAGAAGCTTAACCGA");

my %orf_codoncount_true = ("TTT" => 1, "TTA" => 1, "TTG" => 2, "CTT" => 5, "CTA" => 3, "CTG" => 5, "ATT" => 1, "ATG" => 2, "GTG" => 2, "TCT" => 2, "TCC" => 1, "TCA" => 1, "CCT" => 15, "CCC" => 6, "CCA" => 9, "CCG" => 3, "ACT" => 1, "ACC" => 3, "GCT" => 5, "GCC" => 2, "GCA" => 6, "GCG" => 3, "TAT" => 2, "CAT" => 11, "CAC" => 7, "CAA" => 15, "CAG" => 6, "AAT" => 2, "AAC" => 1, "AAA" => 1, "AAG" => 3, "GAT" => 7, "GAC" => 6, "GAA" => 12, "GAG" => 4, "TGC" => 1, "TGA" => 1, "TGG" => 4, "CGT" => 3, "CGC" => 6, "CGA" => 5, "CGG" => 4, "AGA" => 3, "GGT" => 2, "GGC" => 4, "GGA" => 8, "GGG" => 3, "XXX" => 0, ); 

my %orf_rscu_true = ("TTT" => 2.0000, "TTA" => 0.3750, "TTG" => 0.7500, "CTT" => 1.8750, "CTA" => 1.1250, "CTG" => 1.8750, "ATT" => 3.0000, "ATG" => 1.0000, "GTG" => 4.0000, "TCT" => 3.0000, "TCC" => 1.5000, "TCA" => 1.5000, "CCT" => 1.8182, "CCC" => 0.7273, "CCA" => 1.0909, "CCG" => 0.3636, "ACT" => 1.0000, "ACC" => 3.0000, "GCT" => 1.2500, "GCC" => 0.5000, "GCA" => 1.5000, "GCG" => 0.7500, "TAT" => 2.0000, "CAT" => 1.2222, "CAC" => 0.7778, "CAA" => 1.4286, "CAG" => 0.5714, "AAT" => 1.3333, "AAC" => 0.6667, "AAA" => 0.5000, "AAG" => 1.5000, "GAT" => 1.0769, "GAC" => 0.9231, "GAA" => 1.5000, "GAG" => 0.5000, "TGC" => 2.0000, "TGA" => 3.0000, "TGG" => 1.0000, "CGT" => 0.8571, "CGC" => 1.7143, "CGA" => 1.4286, "CGG" => 1.1429, "AGA" => 0.8571, "GGT" => 0.4706, "GGC" => 0.9412, "GGA" => 1.8824, "GGG" => 0.7059, );

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
	foreach (keys %{$tSITE_STATUS})
	{
		$flags++ if (! exists $RE_status{$_});
	}
	foreach (keys %RE_status)
	{
		$flags++ if (! exists $$tSITE_STATUS{$_});
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
		for ($x = 0; $x < @sing-0; $x++)
		{
			$flags++ if ($sing[$x] != $tsing[$x]+1);
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