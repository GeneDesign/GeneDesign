package RESite;
require Exporter;
use PRISM;

@ISA = qw(Exporter);
@EXPORT = qw(ValueUp LabelUp);
			
#constructor
sub new 
{
	my ($class) = @_;
	my $self = 
	{
		_SiteNumber => undef,
		_CutterName => undef,
		_AARecogniz => undef,
		_NtRecogniz => undef,
		_NtPosition => undef,
		_MustChange => undef,
		_NewSequenc => undef,
		_Sticky		=> undef,
		_RxnTemp	=> undef,
		_StarAct	=> undef,
		_UPrice		=> undef,
		_Methyb		=> undef,
		_Methyi		=> undef,
		_CutsAt		=> undef,
		_Dirty		=> undef,
		_Vendor		=> undef
	};
	bless $self, $class;
	return $self;
}

#accessors
sub SiteNumber
{
	my ( $self, $SiteNumber ) = @_;
	$self->{_SiteNumber} = $SiteNumber if defined($SiteNumber);
	return $self->{_SiteNumber};
}
sub CutterName
{
	my ( $self, $CutterName ) = @_;
	$self->{_CutterName} = $CutterName if defined($CutterName);
	return $self->{_CutterName};
}
sub AARecogniz
{
	my ( $self, $AARecogniz ) = @_;
	$self->{_AARecogniz} = $AARecogniz if defined($AARecogniz);
	return $self->{_AARecogniz};
}
sub NtRecogniz
{
	my ( $self, $NtRecogniz ) = @_;
	$self->{_NtRecogniz} = $NtRecogniz if defined($NtRecogniz);
	return $self->{_NtRecogniz};
}
sub NtPosition
{
	my ( $self, $NtPosition ) = @_;
	$self->{_NtPosition} = $NtPosition if defined($NtPosition);
	return $self->{_NtPosition};
}
sub MustChange
{
	my ( $self, $MustChange ) = @_;
	$self->{_MustChange} = $MustChange if defined($MustChange);
	return $self->{_MustChange};
}
sub NewSequenc
{
	my ( $self, $NewSequenc ) = @_;
	$self->{_NewSequenc} = $NewSequenc if defined($NewSequenc);
	return $self->{_NewSequenc};
}
sub Sticky
{
	my ( $self, $Sticky ) = @_;
	$self->{_Sticky} = $Sticky if defined($Sticky);
	return $self->{_Sticky};
}
sub RxnTemp
{
	my ( $self, $RxnTemp ) = @_;
	$self->{_RxnTemp} = $RxnTemp if defined($RxnTemp);
	return $self->{_RxnTemp};
}
sub StarAct
{
	my ( $self, $StarAct ) = @_;
	$self->{_StarAct} = $StarAct if defined($StarAct);
	return $self->{_StarAct};
}
sub UPrice
{
	my ( $self, $UPrice ) = @_;
	$self->{_UPrice} = $UPrice if defined($UPrice);
	return $self->{_UPrice};
}
sub Methyb
{
	my ( $self, $Methyb ) = @_;
	$self->{_Methyb} = $Methyb if defined($Methyb);
	return $self->{_Methyb};
}
sub Methyi
{
	my ( $self, $Methyi ) = @_;
	$self->{_Methyi} = $Methyi if defined($Methyi);
	return $self->{_Methyi};
}
sub CutsAt
{
	my ( $self, $CutsAt ) = @_;
	$self->{_CutsAt} = $CutsAt if defined($CutsAt);
	return $self->{_CutsAt};
}
sub Dirty
{
	my ( $self, $Dirty ) = @_;
	$self->{_Dirty} = $Dirty if defined($Dirty);
	return $self->{_Dirty};
}
sub Vendor
{
	my ( $self, $Vendor ) = @_;
	$self->{_Vendor} = $Vendor if defined($Vendor);
	return $self->{_Vendor};
}

###FUNCTIONS

##Filter Out by Ends
sub CompareEnds
{
	my ($self, $refends) = @_;
	@ends = @$refends;
	@ends = qw(5 3 r) if (!$refends);
	$endstr  = join '', @ends;
	return 1 if ($endstr =~/a/);
	my $flage = 0;
	foreach $e (@ends)
	{
		$flage = 1 if ($self->Sticky =~ $e);
	}
	if ($endstr !~ /1/)
	{
		$flage = 0 if ($self->Sticky =~ /1/);
	}
	return $flage;
}
##Filter Out by Cut
sub CompareCut
{
	my ($self, $refcut) = @_;
	@cut = @$refcut;
	@cut = qw(1 r) if (!$refcut);
	$cutstr  = join '', @cut;
	return 1 if ($cutstr =~/a/);
	my $flagc = 0;
	$flagc = 1 if ($self->CutsAt =~ /\((\d+)\/(\d+)\)/ && $cutstr =~ 2);
	$flagc = 1 if ($self->CutsAt !~ /\((\d+)\/(\d+)\)/ && $cutstr =~ 1);
	return $flagc;
}

##Filter Out by Lengths
sub CompareLength
{
	my ($self, $refleng) = @_;
	@leng = @$refleng;
	@leng = qw(a) if (!@leng);
	my $flagl = 0;
	return 1 if ((join '', @leng) =~ /a/);
	foreach $l (@leng)
	{
		my $len = length($self->NtRecogniz);
		$flagl = 1 if ($len == $l || $len > 8 && $l == 9 || $len <= 8 && $l == 7);
	}
	return $flagl;
}

##Filter Out by Price
sub ComparePrice
{
	my ($self, $refpric) = @_;
	@pric = @$refpric;
	@pric = qw(.00424 .504) if (!@pric);
	return 1 if ((join '', @pric) =~ /a/);
	my $flagp = 0;
	$flagp = 1 if ($self->UPrice >= $pric[0] && $self->UPrice <= $pric[1]);
	return $flagp;
}

##Filter Out by Ambiguity
sub CompareAmbig
{
	my ($self, $refambi) =@_;
	my @ambi = @$refambi;
	return 1 if ((join '', @ambi) =~ /a/);
	my $flagg = 0;
	$flagg = 1 if ($self->NtRecogniz !~ /N/ && ((join '', @ambi) =~ 1));
	$flagg = 1 if ($self->NtRecogniz !~ /[RYKMSWBDHVN]+/ && ((join '', @ambi) =~ 2));
	return $flagg;
}

##Filter Out by Methylation
sub CompareMeth
{
	my ($self, $refmeth) = @_;
	my @meth = @$refmeth;
	return 1 if ((join '', @meth) =~ /a/);
	return 1 if ((join '', @meth) =~ /r/ && ($self->Methyb !~ /\w/ && $self->Methyi !~ /\w/));
	my $flagm = 0;
	if ((join '', @meth) =~ /o/)
	{
		$flagm = 1 if ($self->Methyb =~ /p/ && ((join '', @meth) =~ 1));
		$flagm = 1 if ($self->Methyi =~ /p/ && ((join '', @meth) =~ 2));
		$flagm = 1 if ($self->Methyb =~ /a/ && ((join '', @meth) =~ 3));
		$flagm = 1 if ($self->Methyi =~ /a/ && ((join '', @meth) =~ 4));
		$flagm = 1 if ($self->Methyb =~ /c/ && ((join '', @meth) =~ 5));
		$flagm = 1 if ($self->Methyi =~ /c/ && ((join '', @meth) =~ 6));
	}
	return $flagm;
}
##Filter Out by Unacceptable Internal Sequence
sub SeqFilter
{
	my ($self, $reflow, $swit) = @_; #swit - is this disallow (1) or allow (2)
	my @lows = @$reflow;
	return 1 if (@lows-0 == 0);
	my $flags = 0;
	for ($t=0; $t< @lows-0; $t++)
	{
		$flags = 1 if ($self->NtRecogniz !~ regres($lows[$t]) && $swit == 1);
		$flags = 1 if ($self->NtRecogniz =~ regres($lows[$t]) && $swit == 2);
	#	print $self->NtRecogniz, ", $flags, $swit, $lows[$t]<br>";
		last if ($flags == 0 && $swit == 1); $flags = 0 if ($t < @lows-1 && $swit == 1);
		last if ($flags == 1 && $swit == 2); $flags = 1 if ($t < @lows-1 && $swit == 0);
	}
	return $flags;
}

#Make a table header - an object filled with the column titles
sub TableHeader
{
	my ($self) = @_;
	$self->CutterName("Name");
	$self->CutsAt("Cuts");
	$self->NtPosition("At<br>(bp)");
	$self->RxnTemp("Incub.<br>Temp.");
	$self->Sticky("Ends");	
	$self->Methyb("Blocked<br>by");
	$self->Methyi("Impaired<br>by");
	$self->Vendor("Available From");
	$self->UPrice("NEB Price<br>Per Unit(\44)");
	return $self;
}

#Get info from flatfile - Clean (1)
sub LoadInfo
{
	my ($self) = @_;
	$name = $self->CutterName;
	my $lef = ''; my $rig = '';
	$set = ''; $done = 0;
	open (IN, "<newenz.txt")  || die "can't open enzyme list";
	while (<IN>)
	{
		if ($_ =~ /^\Q$name\E\t(\S+)\t(\d+)\t(\W?)\t([acp]*)\t([acp]*)\t(\w*)\t(\d*\.\d+)/ )
		{
			$cuts = $1; $temp = $2; $star = $3; $block = $4; $imp = $5; $vend = $6; $pric = $7;
			$self->CutsAt($cuts);	$cuts =~ s/\W*\d*//g;	$self->NtRecogniz($cuts);	$self->RxnTemp($temp);
			$self->StarAct($star);	$self->Methyb($block);	$self->Methyi($imp);		$self->Vendor($vend);	$self->UPrice($pric);	
		#figure Stickiness
			if ($self->CutsAt =~ /(\w*)\^(\w*)/)
			{	
				$lef = length($1); $rig = length($2);
			}
			elsif ($self->CutsAt =~ /\Q$cuts\E\((\-*\d+)\/(\-*\d+)\)/)
			{
				$lef = $1; $rig = $2;
				if($self->CutsAt =~/\-\S+\-/)
				{
					$lef = abs($lef); $rig = abs($rig);
				}
			}			
			$set .= "1" if (abs($lef-$rig) == 1);
			$set .= "b" if ($lef - $rig    == 0);
			$set .= "5" if ($lef < $rig);
			$set .= "3" if ($lef > $rig);
			$self->Sticky($set);
			last;
		}
	}
	close IN;
	return $self;
}

##-passed a complete enzyme object, makes it user friendly
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

sub ValueUp
{
	my ($swit) = @_;
	return if (!$swit);
	my @curv;
	@curv = qw(5 3 b 1)	if ($swit == 1);			#Ends
	@curv = qw(4 5 6 8 9)	if ($swit == 2);		#Lengths
	@curv = qw(1 2)			if ($swit == 3);		#CutLoc
	@curv = qw(1 2)			if ($swit == 6);		#Ambig
	@curv = qw(1 3 5 2 4 6)	if ($swit == 7);		#Meth
	return @curv;
}
sub LabelUp
{
	my ($swit) = @_;	
	return if(!$swit);
	my %curl;
	@keyz = ValueUp($swit);
	@curl{@keyz} = ("5' overhangs ", "3' overhangs ", "blunt ends ", "1bp overhangs")		if ($swit == 1); #Ends
	@curl{@keyz} = ('4bp ','5bp ','6bp ','8bp ','>8bp')										if ($swit == 2); #Lengths
	@curl{@keyz} = ("Inside Cutters", "Outside Cutters")									if ($swit == 3); #CutLoc
	@curl{@keyz} = ("Non-N bases", "ATCG bases")										if ($swit == 6); #Ambig
	@curl{@keyz} = ("B CpG", "B Dam", "B Dcm", "I CpG", "I Dam", "I Dcm")	if ($swit == 7); #Methylation
	return %curl;
}
1;