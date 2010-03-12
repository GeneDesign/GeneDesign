#!/usr/bin/perl

use strict;
use GeneDesign;
use GeneDesignML;
use CGI;
use Perl6::Slurp;

my $query = new CGI;
print $query->header;

my $CODON_TABLE	 = define_codon_table(1);
my $RE_DATA = define_sites($enzfile);	
my $REoptions = "";
$REoptions .= "<option value=\"$_\">$_</option>\n" . tab(10)	foreach (sort keys %{$$RE_DATA{CLEAN}});

opendir(VECTORFOLDER, "vectors");		
my @vec = map {$_ =~/(p[A-Za-z0-9]+\s*[A-Za-z0-9]*)\.txt/} readdir(VECTORFOLDER);		
closedir(VECTORFOLDER);
my $vecnum = scalar(@vec);

my @styles = qw(re mg fn);
my @nexts  = qw(SSIns SSRem SeqAna REBB UserBB OlBB);
my $nextsteps = next_stepper(\@nexts, 5);

gdheader("Vector Chooser", "gdVecChooser.cgi", \@styles);

if ($query->param('first') == 0)
{
print <<EOM;
				<div id="notes">
					This module allows you to select a vector by restriction characteristics or size.  This search is limited to the $vecnum vectors that GeneDesign knows.<br>
					&nbsp;&nbsp;&bull;GeneDesign uses a non-redundant list of restriction enzymes (one isoschizomer per site).<br>
					See the <a href="$linkpath/Guide/veccho.html">manual</a> for more information.
				</div>
				<div id="gridgroup0"> What sort of thing do you want to see in a vector?
					<div id="critbox">
						<div id="critsep">
							<span id="critlabel">Size</span>
							<span id="criteria">
								<input type="radio" name="crSize" value="a" checked> Any Size\n<br>
								<input type="radio" name="crSize" value="g"> Greater Than
								<input type="text" name="crsg"  size="3" maxlength="2" default="6" /> kb<br>
								<input type="radio" name="crSize" value="l"> Less Than
								<input type="text" name="crsl"  size="3" maxlength="2"  default="4" /> kb
							</span>
						</div>
						<br><br><br><br><br>
						<div id="critsep">
							<span id="critlabel">Number of Absent Sites</span>
							<span id="criteria">
								<input type="radio" name="crNabs" value="a" checked> Any<br>
								<input type="radio" name="crNabs" value="r"> At Least
								<input type="text" name="crna"  size="3" maxlength="2" default="10" />
							</span>
						</div>
						<br><br><br><br>
						<div id="critsep">
							<span id="critlabel">Restriction Sites</span>
							<span id="criteria">
								<input type="radio" name="crResp" value="a" checked> Any<br>
								<div id="column1" style="top:20;">
									<input type="radio" name="crResp" value="r"> Specify
									<select name="list" multiple="multiple" size="8">
										$REoptions
									</select>
									<div id="but">
										<input type="button"  name="button" value=">absent" onclick="vpicka()" />
										<input type="button"  name="button" value=">unique" onclick="vpickp()" />
									</div>
								</div>
								<div id="column2" style="top:20;">
									Must be Absent<br>
									<select name="absents" size="8" multiple="multiple">
									</select>
									<div id="but">
										<input type="button"  name="button" value=" <-- " onclick="vabandona()" />
									</div>
								</div>
								<div id="column3" style="top:20; left:220;">
									Must be Unique<br>
									<select name="uniques" size="8" multiple="multiple">
									</select>
									<div id="but">
										<input type="button"  name="button" value=" <-- " onclick="vabandonp()" />
									</div>
								</div>
							</span>
						</div>
						<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>
						<input type="submit" name=".defaults"  value="Defaults" /> &nbsp;&nbsp;
						<input type="button"  name="ShowAll" value="Most Permissive Settings" onclick="VecMostPerm();" /><br><br>
						<input type="submit" name=".submit" value="Show me the Vectors" onclick="vselect()" /><br><br><br><br><br>
						<input type="hidden" name="first" value="1"/>
						<script language="JavaScript">
							var v1 = document.form1.list;
							var v2 = document.form1.absents;
							var v3 = document.form1.uniques;
						</script>
					</div>
				</div>
EOM
	closer();
}


else
{
##-Get Selection Variables
	my %absents = map {$_ => 1} $query->param('absents');
	my %uniques	= map {$_ => 1} $query->param('uniques');
	my $wsize	= $query->param('crSize');
	my $wsizemin = $query->param('crsg') if ($wsize eq 'g');
	my $wsizemax = $query->param('crsl') if ($wsize eq 'l');
	my $wnabs = $query->param('crNabs');
	my $wnabsmin = $query->param('crna') if($wnabs eq 'r' );
	my $wresc = $query->param('crResp');
#	print "absents: ", keys %absents, "<br>uniques: ", keys %uniques, "<br>wsize: $wsize<br>wsizemin: ";
#	print "$wsizemin<br>wsizemax: $wsizemax<br>wnabs: $wnabs<br>wnabsmin: $wnabsmin<br>\n\n";
	my %details;
	foreach my $vector (@vec)
	{
		my $allow = 1;
		my $vecseq = slurp('vectors/' . $vector . '.txt');
		my $lenvec = length($vecseq);
	#exclude by size of vector
		$allow = 0 unless ($wsize eq 'a' || ($wsize eq 'g' && $lenvec >= ($wsizemin*1000)) || ($wsize eq 'l' && $lenvec <= ($wsizemax*1000)));
	#exclude by number of absent sites
		my $SITE_STATUS = define_site_status($vecseq, $$RE_DATA{REGEX});
		my @vabs = map {exists($absents{$_})	?	"<strong>$_</strong>"	:	$_} sort grep {$$SITE_STATUS{$_} == 0} keys %$SITE_STATUS;
		my @vuns = map {exists($uniques{$_})	?	"<strong>$_</strong>"	:	$_} sort grep {$$SITE_STATUS{$_} == 1} keys %$SITE_STATUS;
		$allow = 0 unless ($wnabs eq 'a' || ($wnabs eq 'r' && scalar(@vabs) >= $wnabsmin));
	#exclude by site names
		$allow = 0 foreach ( grep {$$SITE_STATUS{$_} != 0} keys %absents);
		$allow = 0 foreach ( grep {$$SITE_STATUS{$_} != 1} keys %uniques);
	#put suitable vectors in hash
		$details{$vector} = [$vector, $lenvec, \@vabs, \@vuns] if ($allow == 1);
	}
	my @vectors = sort keys %details;
	my $count = scalar(@vectors);
	my @toprint = sort {$details{$a->[0]} <=> $details{$b->[0]}} values %details;
print <<EOM;
				<div id="notes">
					There are $count vectors that fit your criteria.<br>
				</div>
				<div id="gridgroup0">
EOM
	print ("Summary: <br><textarea name=\"list\" rows=\"5\" cols=\"116\" readonly>@vectors</textarea>\n<br><br>");
	print_vector_table(\@toprint, 4);
	closer();
}