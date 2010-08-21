#!/usr/bin/perl
use strict;
use warnings;

use Getopt::Long;
use CPAN '!get';
use Config;
use Cwd;
use File::Temp qw(tempdir);

##Get Arguments
my %config = ();
GetOptions (

			'help'			=> \$config{HELP}
		   );


##Respond to cries of help, if applicable
if ($config{HELP})
{
	print "
GeneDesign_Install.pl
	
    This script will connect to the internet and coordinate the installation of
	GeneDesign and its prerequisites.

  Optional arguments:
    -h,   --help : display this message

";
	exit;
}

print STDERR "You will be asked various questions during this process. ";
print STDERR "You can always accept the default answer.\n";
print STDERR "The whole process will take several minutes and will generate lots of messages.\n";
print STDERR "\nPress return when you are ready to start!\n";

my $h = <>;
print STDERR "\nInstalling the Perl files GeneDesign needs...\n";


my $perl_path = $Config{perlpath}; 
my $windows = $Config{osname} =~ /mswin/i;

if ($windows)
{
	print STDERR "\n\nInstalling Win32 perl module\n\n";
	system("ppm install Win32");
}

eval "CPAN::HandleConfig->load";
eval "CPAN::HandleConfig->commit";

my $working_dir = getcwd;

my $tmpdir = tempdir(CLEANUP=>1) or die "Could not create temporary directory: $!";

my $binaries = $Config{'binexp'};
my $make     = $Config{'make'};

if ($windows) 
{
	system("ppm install Scalar-List-Utils");
	system("ppm install List-MoreUtils");
	system("ppm install Text-Tabs+Wrap");
	system("ppm install Getopt-Long");
	system("ppm install CGI.pm");
}
else 
{
	CPAN::Shell->install('List::Util');
	CPAN::Shell->install('List::MoreUtils');
	CPAN::Shell->install('Text::Wrap');
	CPAN::Shell->install('Getopt::Long');
	CPAN::Shell->install('CGI');
}
CPAN::Shell->install('Perl6::Slurp');
CPAN::Shell->install('Class::Struct');
unless ( eval "use File::Path; 1" )
{
	if ($windows)
	{
		system("ppm install File-Path");
	}
	else
	{
		CPAN::Shell->install('File::Path');
	}
}

unless ( eval "use File::Basename; 1" )
{
	CPAN::Shell->install('File::Basename');
}

unless ( eval "use GD 2.31; 1" ) 
{
	if ($windows)
	{
		print STDERR "Installing GD via ppm.\n";
		print STDERR "(This may take a while...\n";
		system("ppm install GD");
		system("ppm install GDGraph");
		
	}
	else
	{
		print STDERR "Installing GD via CPAN...\n";
		CPAN::Shell->install('GD') unless eval "use GD 2.31; 1";
		CPAN::Shell->install('GD::Graph');
	}
}
