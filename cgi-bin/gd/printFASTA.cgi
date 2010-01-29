#!/usr/bin/perl
use strict;
use CGI;

my $query = new CGI;
print $query->header(-type=>'text/plain');
print $query->param('inseq');