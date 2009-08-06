#!/usr/bin/perl

use File::Find;
use CGI;
$query = new CGI;
print $query->header;

$comp	 = $query->param('Computer');
$brow    = $query->param('Browsern');
$vers    = $query->param('Browserv');
$when    = $query->param('When');
$prob    = $query->param('problem');
$pseq    = $query->param('sequence');
$vecs    = $query->param('vector');
$email   = $query->param('email');
$now = localtime(time);
$rand = rand (24);
$file = "Errors/" . $email . $when . $rand  . ".log";
open (OUT, ">$file") || die "can't open Errors log";
print $file;
print OUT "\n\n---------------------------------\n\n";
print OUT "mail $email comp $comp brow $brow vers $vers prob $prob\n";
print OUT "pseq $pseq\n vecs $vecs\n";
print OUT "problem: $prob\n\n\n";
close OUT;

	print ("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">\n");
	print ("<html>\n<head>\n<meta http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\">\n");
	print ("<link href=\"../../gd/acss/mn.css\" rel=\"stylesheet\" type=\"text/css\">\n");
	print ("<title>Error Report Submitted</title></head><body>\n");
	print ("Thank you!</body></html>");


