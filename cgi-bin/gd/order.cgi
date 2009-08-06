#!/usr/bin/perl

use CGI;
use PRISM;
$query = new CGI;
print $query->header(-type=>'text/plain');
@olarray = split(" ", $query->param('olarray'));

$ch = "\11" if ($query->param('sepchar') eq 'tab');
$ch = ','	if ($query->param('sepchar') eq 'comma');
$ch = ' '	if ($query->param('sepchar') eq 'space');
$ch = '_'	if ($query->param('sepchar') eq 'underscore');

for ($y = 0; $y < @olarray-0; $y++)
{
	$x = $y+1;
	$x = '0' . $x while (length($x) < length(@olarray-0));
	print $query->param('oldesig'), $x, $ch, $olarray[$y], "\n";
}