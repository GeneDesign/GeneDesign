package PML;
use GeneDesign;
use 5.006;
require Exporter;
@ISA = qw(Exporter);
@EXPORT = qw(break space tab 
			cssbrowser platform 
			gdheader closer take_exception take_note
			hidden_fielder next_stepper next_codjug organism_selecter
			annpsite friendly print_enzyme_table enzyme_chooser print_oligos_aligned
			print_vector_table);
			
###### Functions for Making Life Easier
##-break			: makes the passed number of html line breaks.
##
##-space			: makes the passed number of non-braking spaces.
##
##-cssbrowser		: detects browser from $ENV and translates for the benefit of CSS stylesheet selection.
##						returns the appropriate stylesheet link
##-platform			: detects OS from $ENV and translates for the benefit of CSS stylesheet selection.
##						returns the appropriate stylesheet link
##-header			: prints the top of each GeneDesign page
##
##-hidden_fielder	: takes a hash of hidden variables and returns them as hidden fields in HTML.
##
##-annpsite			: prints an amino acid sequence in rows and inserts popup menus at provided landmarks.
##
##-next_stepper		: takes an array of possible next steps and prints them as submit buttons
##
##-organism_selecter		: prints the organism radio buttons

my %dests = ('SSIns' => "Silent Site Insertion", 'SSRem' => "Silent Site Removal", 'SeqAna' => "Sequence Analysis", 
			'OligoDesign' => "Oligo Design", 'toCodJug' => "Codon Juggling");

sub break
{
	my ($num) = @_;
	return "<br>" x $num;
}
sub space
{
	my($num) = @_;
	return "&nbsp;" x $num;
}
sub tab
{
	my($num) = @_;
	return "\t" x $num;
}

sub cssbrowser
{
	my $browstring = $ENV{'HTTP_USER_AGENT'};
	$brow = ''		if ($browstring =~ /Safari/);
	$brow = 'ff'	if ($browstring =~ /Firefox/);
	$brow = 'wie'	if ($browstring =~ /MSIE/ && $browstring =~ /Windows/);
	return $brow;
}

sub platform
{
	my $browstring = $ENV{'HTTP_USER_AGENT'};
	$plat = 'win'	if ($browstring =~ /Windows/);
	$plat = 'mac'	if ($browstring =~ /Macintosh/);
	return $plat;
}

sub gdheader
{
	my ($name, $cginame, $arrref) = @_;
	my $sheets = (cssbrowser() ne '')	?	"<link href=\"$linkpath/acss/" . cssbrowser() . ".css\" rel=\"stylesheet\" type=\"text/css\">\n"	:	"";
	foreach my $tiv (@$arrref)	{ $sheets .= "\n" . tab(2) . "<link href=\"$linkpath/acss/$tiv.css\" rel=\"stylesheet\" type=\"text/css\">";	}
print <<EOM;
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
		$sheets
		<script src="$linkpath/scripts.js" type="text/javascript" language="Javascript"></script>
		<META NAME="robots" CONTENT="noindex, nofollow, noarchive">
		<title>GeneDesign: $name</title>
	</head>
	<body>
		<div id="bigbox">
			<div id="toppa">
				<a href="$linkpath/index.html"><img src="$linkpath/img/gdlogobanner.gif" align = "absmiddle"></a>
				<a class="headli">$name</a>
			</div>
			<form method="post" action="./$cginame" enctype="application/x-www-form-urlencoded" name="form1">
EOM
}

sub closer
{
print <<EOM;
			</form>
		</div>
	</body>
</html>
EOM
}

sub hidden_fielder
{
	my($hashref) = @_;
	my $hiddenstring = "<div id = \"gridgoup1\">\n";
	foreach my $tiv (sort keys %{$hashref})
	{
		$hiddenstring .= tab(5) . "<input type=\"hidden\" name=\"$tiv\" value=\"$$hashref{$tiv}\" />\n";
	}
	$hiddenstring .= tab(4) . "</div>";
	return $hiddenstring;
}

sub next_stepper
{
	my ($arrref, $indent) = @_;
	my $taketo = "<div id=\"notes\" style=\"text-align:center\">\n";
	$taketo .= tab($indent + 1) . "You can take this sequence to another module now.<br>\n";
	$taketo .= tab($indent + 1) . "<strong>Take this sequence to:</strong>\n";
	foreach my $tiv (@$arrref)
	{
		$taketo .= tab($indent + 1) . "<input type=\"submit\" name=\".submit\" value=\"$dests{$tiv}\" onclick=\"$tiv();\" />\n";
	}
	$taketo .= tab($indent) . "</div><br>";
	return $taketo;
}

sub next_codjug
{
	my ($arrref, $indent, $swit) = @_;
	my $count = 0;
	my $taketo = "Go to:";
	foreach my $tiv (@$arrref)
	{
		$taketo .= "\n" . tab($indent) . "<input type=\"submit\" name=\".submit\" value=\"$dests{$tiv}\" onclick=\"CodJug($swit, $count);\" />&nbsp;";
		$count++;
	}
	return $taketo;
}

sub organism_selecter
{
	my $string = "Select Your Organism: <br>\n";
	  $string .= "\t\t\t\t\t\t\t\t<input type=\"radio\" name=\"MODORG\" value=\"1\" onClick=\"organism=1;SWMarkOptimal(form1);\">S. cerevisiae\n";
	  $string .= "\t\t\t\t\t\t\t\t<input type=\"radio\" name=\"MODORG\" value=\"2\" onClick=\"organism=2;SWMarkOptimal(form1);\">E. coli\n";
	  $string .= "\t\t\t\t\t\t\t\t<input type=\"radio\" name=\"MODORG\" value=\"3\" onClick=\"organism=3;SWMarkOptimal(form1);\">H. sapiens<br>\n";
	  $string .= "\t\t\t\t\t\t\t\t<input type=\"radio\" name=\"MODORG\" value=\"4\" onClick=\"organism=4;SWMarkOptimal(form1);\">C. elegans\n";
	  $string .= "\t\t\t\t\t\t\t\t<input type=\"radio\" name=\"MODORG\" value=\"5\" onClick=\"organism=4;SWMarkOptimal(form1);\">D. melanogaster";
	return $string;
}

sub take_exception
{
	my ($msg) = @_;
print <<EOM;
				<div id="notes">
					$msg
					<br><br><input type="button" value="Back" onClick="history.go(-1)">
				</div>
EOM
	closer();
	return;
}

sub take_note
{
	my ($msg) = @_;
print <<EOM;
				<div id="notes">
					$msg
				</div>
EOM
	return;
}

sub annpsite
{
	my ($aaseq, $absref, $selref) = @_;
	@resabs = @$absref;	@ressel = @$selref;
	my $silentsite = qr/([0-9]+): ([A-Za-z0-9]+ [A-Z]+)/;
	my %abssite;	my %selsite;	my $rowleng = 40;	my $curpos = -1;	my $starta = 0;
	foreach $tiv (@resabs)	{	if ($tiv =~ $silentsite)	{$abssite{$1 + 1} .= "$2\t";	}	}
	foreach $tiv (@ressel)	{	if ($tiv =~ $silentsite)	{$selsite{$1 + 1} .= "$2";	}	}
	$lininc = (platform() eq 'mac' && cssbrowser() eq 'ff')	?	30	:	28;
	$dotinc = (platform() eq 'mac' && cssbrowser() eq 'ff')	?	27	:	25;
	for ($j = 0; $j <= length($aaseq)/$rowleng; $j++)
	{
		$top = $j*230;
		$bgcolor = ($j % 2)	?	"CDE"	:	"ABC";
		print tab(5), "<div id = \"gridgoup1\" style = \"background-color:\43$bgcolor; position:absolute; top:$top;\">\n";
		print tab(6), "<p id = \"aaline\">", substr($aaseq, $starta, $rowleng);	
		$starta = $starta + $rowleng < length($aaseq)	?	$starta + $rowleng	:	length($aaseq);
		print "<$starta<br>\n", ((space(9) . "*") x ($rowleng / 10)), "<br>\n", tab(6), "</p>\n";
		for ($x = 1; $x <= $rowleng; $x++)
		{
			$curpos++;
			$color = exists($abssite{$curpos})	?	(exists($selsite{$curpos})	?	"blue"	:	"red")	:	"black";
			$dotpos = $x*17 + $dotinc;	$linpos = $x * 17 + $lininc;
			if (exists($abssite{$curpos}))
			{
				print tab(6), "<select id =\"box$x\" name=\"site$curpos\">\n";
				print tab(7), "<option>-</option>\n";
				foreach $tiv (split("\t", $abssite{$curpos}))	
				{
					($selsite{$curpos} eq $tiv)	?	print tab(7), "<option selected>&bull; $selsite{$curpos}</option>\n"	:	print tab(7), "<option>* $tiv</option>\n";
				}
				print tab(6), "</select>\n";
				print tab(6), "<img id=\"dot$x\" style=\"left:$dotpos; z-index:325\" src=\"$docpath/img/d$color.gif\">\n";
				print tab(6), "<img id=\"line$x\" style=\"left:$linpos; z-index:175\" src=\"$docpath/img/l$color.gif\">\n";
			}
		}
 		print tab(6), break(14), space(1);
		print "\n",  space(200), "." unless ($j % 2);
		print tab(5), "</div><br>\n";
	}
}

sub enzyme_chooser
{
	my($indent) = @_;
	$tab = tab($indent);
print <<EOM;
$tab<div id="critbox">
$tab	<div id="critsep">
$tab		<span id="critlabel">Ends</span>
$tab		<span id="criteria">
$tab			<input type="radio" name="crEndss" value="0"> All Ends<br>
$tab			<input type="radio" name="crEndss" value="1" checked> Only 
$tab			<label><input type="checkbox" name="crEnds" value="5'" checked="checked" />5&rsquo; overhangs</label>
$tab			<label><input type="checkbox" name="crEnds" value="3'" checked="checked" />3&rsquo; overhangs</label>
$tab			<label><input type="checkbox" name="crEnds" value="b" />blunt ends</label>
$tab			<label><input type="checkbox" name="crEnds" value="1bp" />1bp overhangs
$tab		</span>
$tab	</div><br><br><br>
$tab	<div id="critsep">
$tab		<span id="critlabel">Cut</span>
$tab		<span id="criteria">
$tab			<input type="radio" name="crCutss" value="0"> All Cuts<br>
$tab			<input type="radio" name="crCutss" value="1" checked> Only 
$tab			<label><input type="checkbox" name="crCuts" value="P" checked="checked" />Inside Cutters</label>
$tab			<label><input type="checkbox" name="crCuts" value="A" />Outside Cutters</label>
$tab		</span>
$tab	</div><br><br><br>
$tab	<div id="critsep">
$tab		<span id="critlabel">Site Length</span>
$tab		<span id="criteria">
$tab			<input type="radio" name="crLengs" value="0" checked> All Lengths<br>
$tab			<input type="radio" name="crLengs" value="1"> Only Lengths of 
$tab			<label><input type="checkbox" name="crLeng" value="4" />4bp </label>
$tab			<label><input type="checkbox" name="crLeng" value="5" />5bp </label>
$tab			<label><input type="checkbox" name="crLeng" value="6" />6bp </label>
$tab			<label><input type="checkbox" name="crLeng" value="7" />7bp </label>
$tab			<label><input type="checkbox" name="crLeng" value="8" />8bp </label>
$tab			<label><input type="checkbox" name="crLeng" value="b" />&gt;8bp</label>
$tab		</span>
$tab	</div><br><br><br>
$tab	<div id="critsep">
$tab		<span id="critlabel">Allow Ambiguous Bases?</span>
$tab		<span id="criteria">
$tab			<input type="radio" name="crAmbis" value="0" checked> Allow Any Base<br>
$tab			<input type="radio" name="crAmbis" value="1"> Allow Only 
$tab			<label><input type="checkbox" name="crAmbi" value="1" checked="checked" />Non-N bases</label>
$tab			<label><input type="checkbox" name="crAmbi" value="2" checked="checked" />ATCG bases</label>
$tab		</span>
$tab	</div><br><br><br>
$tab	<div id="critsep">
$tab		<span id="critlabel">Methylation Sensitivity</span>
$tab		<span id="criteria">
$tab			<input type="radio" name="crMeths" value="0" checked> Allow Any Sensitivity<br>
$tab			<input type="radio" name="crMeths" value="1"> Allow No Sensitivity<br>
$tab			<input type="radio" name="crMeths" value="2">Allow Only Cutters that are<br>
$tab			&nbsp;&nbsp;<label><input type="checkbox" name="crMeth" value="bp" />Blocked by CpG</label>
$tab			<label><input type="checkbox" name="crMeth" value="ba" />Blocked by Dam</label>
$tab			<label><input type="checkbox" name="crMeth" value="bc" />Blocked by Dcm</label><br>
$tab			&nbsp;&nbsp;<label><input type="checkbox" name="crMeth" value="ip" />Inhibited by CpG</label>
$tab			<label><input type="checkbox" name="crMeth" value="ia" />Inhibited by Dam</label>
$tab			<label><input type="checkbox" name="crMeth" value="ic" />Inhibited by Dcm</label>
$tab		</span>
$tab	</div><br><br><br><br><br><br><br>
$tab	<div id="critsep">
$tab		<span id="critlabel">Price Range</span>
$tab		<span id="criteria">
$tab			<input type="radio" name="crPrir" value="0" checked> Any (\$.00424 to \$2.304 per unit)<br>
$tab			<input type="radio" name="crPrir" value="1"> Must be between &#36;
$tab			<input type="text" name="crPrlo" value=".00424" size="7" maxlength="6" />and &#36;
$tab			<input type="text" name="crPrhi" value=".504" size="7" maxlength="6" /> per unit
$tab		</span>
$tab	</div><br><br><br>
$tab	<div id="critsep">
$tab		<span id="critlabel" style="width:200;">Disallow sites with: (boolean OR, separate by space)</span>
$tab		<span id="criteria" style="left:200;">
$tab			<input type="text" name="crDisa"  size="20" />
$tab		</span>
$tab	</div><br><br><br>
$tab	<div id="critsep">
$tab		<span id="critlabel" style="width:200;">Allow only sites with: (boolean OR, separate by space)</span>
$tab		<span id="criteria" style="left:200;">
$tab			<input type="text" name="crAllo"  size="20" />
$tab		</span>
$tab	</div><br><br><br>
$tab	<input type="button"  name="ShowAll" value="Most Permissive Settings" onclick="EnzMostPerm();" />
$tab</div>	
EOM
}

sub friendly
{
	my $tempend = ''; my $temptemp = ''; my $tempmethi = ''; my $tempmethb = ''; 
	my ($self) = @_;
	#ends
		if ($self->Sticky =~ /([35b]+)/)
		{
			$tempend = $1;
			$tempend .= "'" if ($1 =~ /\d/);
			$tempend = "blunt" if ($1 eq 'b');
			$tempend .= "&laquo;" if ($self->Sticky =~ /1/);
		}
	#temp
		$temptemp = $self->RxnTemp . "&deg;";
	#methylation
		$tempmethb .= "CpG " if ($self->Methyb =~ /p/);
		$tempmethb .= "dcm " if ($self->Methyb =~ /c/);
		$tempmethb .= "dam " if ($self->Methyb =~ /a/);
		$tempmethi .= "CpG " if ($self->Methyi =~ /p/);
		$tempmethi .= "dcm " if ($self->Methyi =~ /c/);
		$tempmethi .= "dam " if ($self->Methyi =~ /a/);
	$self->Sticky($tempend); $self->RxnTemp($temptemp); $self->Methyb($tempmethb); $self->Methyi($tempmethi);
	return $self;
}

sub print_enzyme_table
{
	my ($list_ref, $site_data_ref, $indent) = @_;
	my $tab = tab($indent);
	my %RE_DATA = %$site_data_ref;
	my $j = 1;
	my $color = "9AB";
print <<EOM;
$tab<div id = "gridgroup1">
$tab	<div id = "gridgroup1" style = "background-color: \43$color;">
$tab		<span id = "cuNum"></span>
$tab		<span id = "cuName">Name</span>
$tab		<span id = "cuRecog">Cuts (StarAct)</span>
$tab		<span id = "cuSite" >At</span>
$tab		<span id = "cuStick">Sticky?</span>
$tab		<span id = "cuRxnTe">Incub.<br>Temp</span>
$tab		<span id = "cuMethb">Blocked<br>by</span>
$tab		<span id = "cuMethi">Impaired<br>by</span>
$tab		<span id = "cuVendr">Available From</span>
$tab		<span id = "cuUpric">NEB Price<br>Per Unit(\44)</span>
$tab		&nbsp;<br>&nbsp;
$tab	</div>
EOM
	foreach $m (@{$list_ref})
	{
		$color = ($j % 2)	?	"CDE"	:	"ABC"	;
		$j++;
print <<EOM;
$tab	<div id = "gridgroup1" style = "background-color: \43$color;">
$tab		<span id = "cuNum"><input type="checkbox" name="nextrem" value="$m" /></span>
$tab		<span id = "cuName"><a href="http://rebase.neb.com/rebase/enz/$m.html" target="blank">$m</a></span>
$tab		<span id = "cuRecog">$RE_DATA{TABLE}->{$m} $RE_DATA{STAR}->{$m}</span>
$tab		<span id = "cuSite" >$RE_DATA{POST}->{$m}</span>
$tab		<span id = "cuStick">$RE_DATA{TYPE}->{$m}</span>
$tab		<span id = "cuRxnTe">$RE_DATA{TEMP}->{$m}&deg;</span>
$tab		<span id = "cuMethb">$RE_DATA{METHB}->{$m}</span>
$tab		<span id = "cuMethi">$RE_DATA{METHI}->{$m}</span>
$tab		<span id = "cuVendr">$RE_DATA{VEND}->{$m}</span>
$tab		<span id = "cuUpric">$RE_DATA{SCORE}->{$m}</span>
$tab		&nbsp;<br>&nbsp;
$tab	</div>
EOM
	}
print <<EOM;
$tab	<div id = "gridgroup1" style = "background-color: \439AB;">
$tab		<br> * This enzyme may exhibit star activity under certain conditions.
$tab		<br>\'1 This enzyme has a 1bp overhang and may be very difficult to ligate.&nbsp;<br>&nbsp;
$tab	</div>
$tab</div>
EOM
	return;
}

sub print_vector_table
{
	my ($list_ref, $indent) = @_;
	my $tab = tab($indent);
	my $j = 0;
	my $color = "9AB";
print <<EOM;
$tab<div id = "gridgroup1">
$tab	<div id = "gridgroup1" style = "background-color: \43$color;">
$tab		<span id = "vNum">s</span>
$tab		<span id = "vName">vector name</span>
$tab		<span id = "vLength">size (bp)</span>
$tab		<span id = "vAbs" style="font-size: 12px;">absent sites</span>
$tab		<span id = "vUni" style="font-size: 12px;">unique sites</span>
$tab		&nbsp;<br>&nbsp;
$tab	</div>
EOM
	foreach $m (@{$list_ref})
	{
		$color = ($j % 2)	?	"ABC"	:	"CDE"	;
		$j++;
print <<EOM;
$tab	<div id = "gridgroup1" style = "background-color: \43$color;">
$tab		<span id = "vNum">$j</span>
$tab		<span id = "vName">$m->[0]</span>
$tab		<span id = "vLength">$m->[1]</span>
$tab		<span id = "vAbs" >@{$m->[2]}</span>
$tab		<span id = "vUni">@{$m->[3]}</span>
$tab		&nbsp;<br><br><br><br><br><br><br><br>&nbsp;
$tab	</div>
EOM
	}
print <<EOM;
$tab	<div id = "gridgroup1" style = "background-color: \439AB;">
$tab		&nbsp;<br>
$tab	</div>
$tab</div>
EOM
	return;
}

sub print_oligos_aligned
{
	my ($self, $gapswit, $indent, $maskswit) = @_;		
	$maskswit = 0 unless($maskswit);
	my $oliarrref = $self->Oligos;	my @oligoarr = @$oliarrref;
	my $olapref   = $self->Olaps;    my @olaparr = @$olapref;
	my $colhasref = $self->Collisions; my %colhas = %$colhasref; my @colkeys = keys %colhas;
	my $tab = tab($indent);
	my $toprow; my $botrow;
	my $master = $self->ChunkSeq; my $retsam = complement($master, 0);
	if ($maskswit == 1)
	{
		my $mask = $self->Mask; 
		my $tagstart = "<font color = \"\43FF0000\">"; 
		my $tagstop = "</font>";
		@masterarr = split("", $master);
		@retsamarr = split("", $retsam);
		my (@remaster, @reretsam);
		$count = 0;
		for ($x = 0; $x < @masterarr; $x++)
		{
			push @remaster, $masterarr[$x];
			push @reretsam, $retsamarr[$x];
			if (substr($mask, $x, 1) == 0 && substr($mask, $x+1, 1) == 1)
			{
				push @remaster, $tagstart;
				push @reretsam, $tagstart; $count++;
			}
			elsif (substr($mask, $x, 1) == 1 && substr($mask, $x+1, 1) == 0)
			{
				push @remaster, $tagstop;
				push @reretsam, $tagstop; $count--;
			}
		}
		push @remaster, $tagstop if ($count == 1);
		push @reretsam, $tagstop if ($count == 1);
		$master = join("", @remaster);
		$retsam = join("", @reretsam);
	}
	$k = 0;
	for ($w = 0; $w < @oligoarr-0; $w+=2)
	{
		if (!exists($colhas{$w}) && !exists($colhas{$w-2}) && $gapswit == 1)
		{
			my $nextlap = $w+1 < @olaparr-0	?	length($olaparr[$w+1])	:	0;
			my $nextoli = $w+1 < @oligoarr-0	?	length($oligoarr[$w+1])	:	0;
			$toprow .= $oligoarr[$w] . space($nextoli-(length($olaparr[$w])+$nextlap));
		}
		elsif ($gapswit == 1)
		{
			$prev = 0;
			if (exists($colhas{$w-2}) && $w != 0) #previous one collided - draw first bases in red
			{
				$toprow .= "<font color =\"\43FF0000\">" . substr($oligoarr[$w-2], length($oligoarr[$w-2])-$colhas{$w-2}) . "</font>";
				$prev = $colhas{$w-2};
			}
			$toprow .= substr($oligoarr[$w], $prev, (length($oligoarr[$w]) - $colhas{$w} - $prev));
			$toprow .= space(length($oligoarr[$w+1]) - (length($olaparr[$w]) + length($olaparr[$w+1]))) if (!exists($colhas{$w}) && $w != @oligoarr-0);
		}
		elsif ($gapswit == 0)
		{
			$toprow .= "<font color = \"437777DD\">" . $oligoarr[$w] . "</font>" . space(length($oligoarr[$w+1])-(length($olaparr[$w])+length($olaparr[$w+1]))) if ($k % 2 == 0);
			$toprow .= $oligoarr[$w] . space(length($oligoarr[$w+1])-(length($olaparr[$w])+length($olaparr[$w+1]))) if ($k % 2 == 1);
			$k++;
		}
	}
	$botrow = space(length($oligoarr[0])-length($olaparr[0])); 
	$k = 0;
	for ($w = 1; $w < @oligoarr-0; $w+=2)
	{
		if (!exists($colhas{$w}) && !exists($colhas{$w-2}) && $gapswit == 1)
		{
			my $nextlap = $w+1 < @olaparr-0	?	length($olaparr[$w+1])	:	0;
			my $nextoli = $w+1 < @oligoarr-0	?	length($oligoarr[$w+1])	:	0;
			$botrow .= complement($oligoarr[$w], 0) . space($nextoli-(length($olaparr[$w])+$nextlap));
		}
		elsif ($gapswit == 1)
		{
			$prev = 0;
			if (exists($colhas{$w-2}) && $w != 1) #previous one collided - draw first bases in red
			{
				$botrow .= "<font color =\"\43FF0000\">" . complement(substr($oligoarr[$w-2], length($oligoarr[$w-2]) - $colhas{$w-2}), 0) . "</font>";
				$prev = $colhas{$w-2};
			}
			$botrow .= complement(substr($oligoarr[$w], $prev, (length($oligoarr[$w]) - $colhas{$w} - $prev)), 0);
			$botrow .= space(length($oligoarr[$w+1])-(length($olaparr[$w])+length($olaparr[$w+1]))) if (!exists($colhas{$w}));
		}
		elsif ($gapswit == 0)
		{
			$botrow .= "<font color = \"437777DD\">" . complement($oligoarr[$w], 0) . "</font>" . space(length($oligoarr[$w+1])-(length($olaparr[$w])+length($olaparr[$w+1]))) if ($k % 2 == 0);
			$botrow .= complement($oligoarr[$w], 0) . space(length($oligoarr[$w+1])-(length($olaparr[$w])+length($olaparr[$w+1]))) if ($k % 2 == 1);
			$k++;
		}					
	}
	
print <<EOM;
$tab<div id = "oligo">
$tab	$master<br>
$tab	$toprow<br>
$tab	$botrow<br>
$tab	$retsam&nbsp;&nbsp;&nbsp;&nbsp;.
$tab</div>
EOM
}
1;