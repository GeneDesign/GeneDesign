#!/usr/bin/perl
use strict;
use CGI qw(:standard);
use PML;
use GeneDesign;

my $query = new CGI;
print $query->header;

my $RE_DATA = define_sites("<newenz.txt");

my @styles = qw(re mg fn);

gdheader("Enzyme Chooser", "gdEnzChooser.cgi", \@styles);

if ($query->param('first') == 0)
{
print <<EOM;
				<div id="notes">
					This module is for the selection of restriction enzymes. The next screen will present a sorted 
					and annotated list of enzymes that match the criteria you specify.<br>
					&nbsp;&nbsp;&bull;GeneDesign uses a non-redundant list of restriction enzymes (one isoschizomer per site).<br>
					&nbsp;&nbsp;&bull;Price is measured in 2004 US dollars from the NEB catalog.<br>
					See the <a href="$docpath/Guide/enzcho.html">manual</a> for more information.
				</div>
				<div id="gridgroup0"> 
					What sort of thing do you like to see in an enzyme?
EOM
	enzyme_chooser(5);
print <<EOM;
				</div><br><br>
				<input type="submit" name=".defaults"  value="Defaults" />
				<input type="submit" name=".submit" value="Show me the Enzymes" /><br><br><br><br><br>
				<input type="hidden" name="first" value="1"  />
EOM
	closer();
}

else
{
	my %pa;
	$pa{check_price}			=	$query->param('crPrir');
	$pa{low_price}				=	$query->param('crPrlo');
	$pa{high_price}				=	$query->param('crPrhi');
	$pa{check_stickiness}		=	$query->param('crEndss');
	$pa{stickiness}				=	join " ", $query->param('crEnds');
	$pa{check_cleavage_site}	=	$query->param('crCutss');
	$pa{cleavage_site}			=	join " ", $query->param('crCuts');
	$pa{check_ambiguity}		=	$query->param('crAmbis');
	$pa{ambiguity}				=	join " ", $query->param('crAmbi');
	$pa{check_meth_status}		=	$query->param('crMeths');
	$pa{meth_status}			=	join " ", $query->param('crMeth');
	$pa{check_site_length}		=	$query->param('crLengs');
	$pa{site_length}			=	join " ", $query->param('crLeng');
	$pa{disallowed_seq}			=	$query->param('crDisa');
	$pa{required_seq}			=	$query->param('crAllo');
	
#	print "ends: $ends<br>price: @pric<br>Disallow: $diss<br>Force: $alls<br>cuts: $cuts<br>ambiguity: $ambi<br>Meth: @meth<br>lengths: @leng<br><br>";
		
	my @finarr = sort {$$RE_DATA{SCORE}->{$a} <=> $$RE_DATA{SCORE}->{$b}} filter_sites(\%pa, $RE_DATA);
	my $num = scalar(@finarr);
	
print <<EOM;
				<div id="notes">
					There are $num enzymes that fit your criteria.<br>
					See the <a href="$docpath/Guide/enzcho.html">manual</a> for more information.\n
				</div>
				<div id="gridgroup0">
					Ranked Summary: <br>
					<textarea name="list" rows="5" cols="116" readonly>@finarr</textarea><br><br>
EOM
	print_enzyme_table(\@finarr, $RE_DATA, 5);
	print tab(4), "</div>\n";
	closer();
}