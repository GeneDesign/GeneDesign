#!/usr/bin/perl
use strict;
use warnings;

use Getopt::Long;
use CPAN '!get';
use Config;
use Cwd;
use LWP::Simple;
use File::Temp qw(tempdir);
use File::Copy 'cp';

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
	GeneDesign and its prerequisites.  Owes a lot to gbrowse's netinstall.pl

  Optional arguments:
    -h,   --help : display this message

";
	exit;
}


print STDERR "This whole process will take several minutes and will generate lots of messages.\n";
print STDERR "\nPress return when you are ready to start!\n";

my $h = <>;
print STDERR "\nInstalling the perl modules GeneDesign needs...\n";


my $perl_path = $Config{perlpath}; 
my $windows = $Config{osname} =~ /mswin/i;
my $perl_version = $Config{PERL_VERSION};

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
	system("ppm rep add trouchelle.com-$perl_version http://trouchelle.com/ppm$perl_version/");
	system("ppm rep add trouchelle.com-$perl_version-UNSTABLE http://trouchelle.com/ppm$perl_version/unstable/");
	system("ppm install Scalar-List-Utils");
	system("ppm install List-MoreUtils");
	system("ppm install Text-Tabs+Wrap");
	system("ppm install Getopt-Long");
	system("ppm install CGI.pm");
	system("ppm install Archive-Zip");
	system("ppm install libwww-perl");
	system("ppm install Perl6-Slurp");
}
else 
{
	CPAN::Shell->install('List::Util');
	CPAN::Shell->install('List::MoreUtils');
	CPAN::Shell->install('Text::Wrap');
	CPAN::Shell->install('Getopt::Long');
	CPAN::Shell->install('CGI');
	CPAN::Shell->install('Archive::Zip');
	CPAN::Shell->install('LWP::Simple');
	CPAN::Shell->install('Perl6::Slurp');
}
use constant NMAKE => 'http://download.microsoft.com/download/vc15/patch/1.52/w95/en-us/nmake15.exe';

eval "use Archive::Zip ':ERROR_CODES',':CONSTANTS'";
if ($windows && !-e "$binaries/${make}.exe")
{
	print STDERR "Installing make utility...\n";
	-w $binaries or die "$binaries directory is not writeable. Please re-login as Admin.\n";
	chdir $tmpdir;

	my $rc = mirror(NMAKE,"nmake.zip");
	die "Could not download nmake executable from Microsoft web site." unless $rc == RC_OK() or $rc == RC_NOT_MODIFIED();

	my $zip = Archive::Zip->new('nmake.zip') or die "Couldn't open nmake zip file for decompression: $!";
	$zip->extractTree == AZ_OK() or die "Couldn't unzip file: $!";
	-e 'NMAKE.EXE' or die "Couldn't extract nmake.exe";

	cp('NMAKE.EXE',"$binaries/${make}.EXE") or die "Couldn't install nmake.exe: $!";
	cp('NMAKE.ERR',"$binaries/${make}.ERR"); # or die "Couldn't install nmake.err: $!"; # not fatal
}

CPAN::Shell->install('Class::Struct');
CPAN::Shell->install('HTML::Tagset');


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
