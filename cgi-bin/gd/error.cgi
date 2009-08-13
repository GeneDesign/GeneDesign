#!/usr/bin/perl
use strict;

use GeneDesign;
use File::Find;
use CGI;

my $query = new CGI;
print $query->header;

my $comp	 = $query->param('Computer');
my $brow    = $query->param('Browsern');
my $vers    = $query->param('Browserv');
my $when    = $query->param('When');
my $prob    = $query->param('problem');
my $pseq    = $query->param('sequence');
my $vecs    = $query->param('vector');
my $email   = $query->param('email');
my $now = localtime(time);
my $rand = rand (24);
my $file = "$docpath/Errors/" . $email . $when . $rand  . ".log";
open (OUT, ">$file") || die "$! can't open Errors log";
print $file;

print OUT "\n\n---------------------------------\n\n";
print OUT "mail $email comp $comp brow $brow vers $vers prob $prob\n";
print OUT "pseq $pseq\n vecs $vecs\n";
print OUT "problem: $prob\n\n\n";
close OUT;

	print ("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">\n");
	print ("<html>\n<head>\n<meta http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\">\n");
	print ("<link href=\"../../gd2/acss/mn.css\" rel=\"stylesheet\" type=\"text/css\">\n");
	print ("<title>Error Report Submitted</title></head><body>\n");
	print ("Thank you!</body></html>");


