package ResSufTree;
use 5.006;
use strict;

## From John Kloss

sub new_aa
{
	my ($class) = @_;
	my $self = 
	{
		root => [ ( undef ) x 23 ]
	};
	bless $self, $class;
	return $self;
}

sub root 
{ 
	my ($self, $root) = @_;	
	$self->{ root} = $root if defined($root);	
	return $self->{root};
}

my %AA_KEYS =	('A'=> 0, 'C'=> 1, 'D'=> 2, 'E'=> 3, 'F'=> 4, 'G'=> 5, 'H'=> 6, 'I'=> 7, 'K'=> 8, 'L'=> 9, 
				 'M'=>10, 'N'=>11, 'P'=>12, 'Q'=>13, 'R'=>14, 'S'=>15, 'T'=>16, 'V'=>17, 'W'=>18, 'Y'=>19, '*'=>20	);

sub add_aa_paths
{
	my ($self, $ivno, $hashref) = @_;
	my $next = $self->{ root };
	my $peptide; my $enzyme;
	if ($ivno =~ /([A-Z\*]+) . ([A-Z0-9a-z]+)/) 
	{
		$peptide = $1; 
		$enzyme  = $2;
	}
	foreach (split '', $peptide)
	{
		my $charnum = $AA_KEYS{$_};
		$next->[$charnum] ||= [ (undef) x 23 ];
		$next = $next->[$charnum];
	}
	$$hashref{$peptide} .= "$enzyme ";
	$next->[21] = $$hashref{$peptide};
	$next->[22] = $peptide;
}


sub find_aa_paths
{
	my ($self, $protein) = @_;
	my @locations;
	my @seq = split '', $protein;
	for (my $seq_idx = 0; $seq_idx < @seq; $seq_idx++)
	{
		my $cur_idx = $seq_idx;
		my $ref_idx = $AA_KEYS{$seq[$seq_idx]};
		my $ref     = $self->{root};
		while (++$cur_idx < @seq and $ref)
		{
			if ($ref->[21]) 
			{	
				foreach (split " ", $ref->[21])	
				{	
					push @locations, $seq_idx+1 . ": $_ " . $ref->[22];	
				}	
			}
			$ref_idx = $AA_KEYS{$seq[$cur_idx]};
			$ref = $ref->[$ref_idx];
		}
	}
	return @locations;
}
1;

__END__