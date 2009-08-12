#!/usr/bin/perl
use strict;
use GeneDesign;
use ResSufTree;
use CGI;
use PML;

my $query = new CGI;
print $query->header;

my $CODON_TABLE	 = define_codon_table(1);

my @styles = qw(re mg pd fn);
my @nexts  = qw(SSIns SSRem SeqAna OligoDesign);
my $nextsteps = next_stepper(\@nexts, 5);

gdheader("Silent Short Sequence Insertion", "gdOliIns.cgi", \@styles);

if ($query->param('swit') eq '' && $query->param('remseq') eq '')
{
	my $nucseq = $query->param('PASSNUCSEQUENCE')	?	$query->param('PASSNUCSEQUENCE')	:	$query->param('nucseq');
	my $readonly = $nucseq	?	'readonly = "true"'	:	'';
print <<EOM;
				<div id="notes">
					<strong>To use this module you need two nucleotide sequences, large and small.  An organism name is optional.</strong><br>
					Your nucleotide sequence will be searched for the short sequence you provide and as many iterations as possible will be inserted by changing whole codons 
					without changing the amino acid sequence.<br><br>
					See the <a href="$docpath/Guide/shortr.html">manual</a> for more information.
				</div>
				<div id="gridgroup0">
					Your nucleotide sequence:<br>
					<textarea name="nuseq"  rows="6" cols="100" $readonly>$nucseq</textarea><br>
					Sequence to be Inserted: 
					<input type="text" name="remseq"  columns="20" /><br><br>
					<div id="gridgroup1" align ="center" style="position:absolute; top:170; ">
						<input type="submit" name=".submit" value=" Insert short sequences " />
					</div>
				</div>
EOM
	closer();
}

elsif ($query->param('swit') eq '' && ($query->param('nuseq') eq '' || length($query->param('remseq')) >= length($query->param('nuseq')) || length($query->param('remseq')) < 2 ))
{
	print ("<div id=\"notes\">");
	print ("You need a nucleotide sequence.<br>") if ($query->param('nuseq') eq '');
	print ("You need a short sequence to be inserted (at least two bp) <br> ") if ($query->param('remseq') eq '');
	print ("Your short sequence should be shorter than your nucleotide sequence.<br>\n") if ($query->param('remseq') >= length($query->param('nuseq')));
	print break(2), ("<input type=\"button\" value=\"Back\" onClick=\"history.go(-1)\">");
	print ("</div>");
}

elsif ($query->param('firstaround') ne 'no')
{
	@remseqs = split(/[ \,]/, $query->param('remseq'));
	print "REMSEQS @remseqs<br><br>";
	$nucseq = cleanup($query->param('nuseq'), 0);
	$aaseq  = translate($nucseq, 1, $CODON_TABLE);

	push @finarr, "$_ . $remseq" foreach (amb_translation($remseq, $CODON_TABLE));
	my %hashofpeps;
	my $trnrentree = new_aa ResSufTree();	
	$trnrentree->add_aa_paths($_, \%hashofpeps) foreach (@finarr);
	@array = $trnrentree->find_aa_paths($aaseq);
	push @hits, $_ . " . " foreach (@array);
	
	$len = length($nucseq);
	@aa = split('', translate($nucseq));
	@nuc = split('', $nucseq);
	$organism = $query->param('MODORG');

	print ("<div id=\"notes\">");
	print "\nI was asked to insert the sequence $remseq. ", (@answer2-0), " instances are already present and will not be annotated here. ";
	print @answer-0, " possible insertion sites have been found.";
	print ("  <input type=\"submit\" value=\" Just insert the instances I have selected \" onClick=\"OliISum(0);\">\n");
	print ("  <input type=\"submit\" value=\" Insert all possible instances \" onClick=\"OliISum(1);\">\n");
	print break(1);
	print "</div>"; 

	print ("<div id=\"gridgroup0\">\n");
	annpsite($aaseq, \@array); 
	$top += 500;
	foreach $trep (@answer)
	{
		$tempstr = $trep . "\n";
		push @answer3, $tempstr;
	}
	print ("   <input type=\"hidden\" name=\"org\" value=\"", $query->param('org'), "\">\n");
	print ("   <input type=\"hidden\" name=\"swit\" value=\"some\">\n");
	print ("   <input type=\"hidden\" name=\"remseq\" value=\"$remseq\">\n");
	print ("   <input type=\"hidden\" name=\"nucseq\" value=\"$nucseq\">\n");
	print ("   <input type=\"hidden\" name=\"allsites\" value=\"@answer3\">\n");
	print ("   <input type=\"hidden\" name=\"firstaround\" value=\"no\">\n");
	print (" </div>");
}

if ($query->param('swit') eq 'all' || $query->param('swit') eq 'some')
{
	$org = $query->param('org');
	$nucseq = $query->param('nucseq');
	$aaseq = translate($nucseq);
	$remseq = $query->param('remseq');
	undef @newarr;
	$rh = regres($remseq);
	@aa = split('', translate($nucseq));
	@nt = split('', $nucseq);	$nstring = 'NNNNNNNN';
	if ($query->param('swit') eq 'all')
	{
		@newarr = split('\n', $query->param('allsites')); 
	}
	elsif ($query->param('swit') eq 'some')
	{
		@array = split('\n', $query->param('allsites'));
		for ($m = 1; $m <(@aa+1); $m++)
		{
			$curstr = 'site' . $m;
			$box = $query->param($curstr);
			$box = $1 if ($box =~ /\W([A-Za-z0-9]*)/);
			if($box ne '' && $box ne '-')
			{
				$aapos = $m;
				foreach $l (@array)
				{
					$t = ' ' . $l;
					$o = $aapos;
					$aarecogniz = $1 if ($t =~ / $o: $box ([A-Z*]+)/);
				}
				$currstring = "$aapos: $box $aarecogniz";
				push @newarr, $currstring;
			}
		}
	}
	foreach $instance (@newarr)
	{
		if ($instance =~ /([0-9]+)\: [A-Z]+ ([A-Z]+)/)
		{	
			$curraapos = $1 - 1; $curraaseq = $2;  $currnucpos = ($curraapos *3); 
			$matchers = ''; $diff = (length($curraaseq)*3) - length($remseq);
			@reccedstr = split('', substr($aaseq, $curraapos, length($curraaseq)));
			for ($i = 0; $i <= $diff; $i++)
			{
				$matchers = ((substr $nstring, 0, $i) . $remseq);
				$matchers = $matchers . 'N' while (length($matchers) != length($curraaseq)*3);
				$check ='';
				$offset = 0;
				for ($j = 0; $j < (int(length($matchers) / 3)); $j++)
				{
					@checker = getaaa(substr($matchers, $offset, 3));
					for ($g = 0; $g < (@checker-0); $g++)	{	$check .= $checker[$g] if ($reccedstr[$j] eq $checker[$g]);	}
					$offset += 3;
				}
				last if ($check eq substr($aaseq, $curraapos, length($curraaseq)));
			}
			$offset = 0; $newseq = '';
			for ($i = 0; $i < (length( substr($nucseq, $currnucpos, length($curraaseq)*3)) / 3); $i++)
			{
				$curcod = substr  substr($nucseq, $currnucpos, length($curraaseq)*3), $offset, 3;
				$curtar = substr $matchers, $offset, 3;
				@workaal = getaaa($curcod);
				foreach $g (@workaal)
				{
					@workcod = getcods($g);
					if ($curcod ne $curtar && $curtar ne 'NNN')
					{
						foreach $l (@workcod)
						{
							$tot = compareseqs($curtar, $l);
							$newseq .= $l if ($tot == 1);
							last if ($tot == 1);
						}
					}
					else
					{
						$newseq .= $curcod;
					}					
				}
				$offset += 3;
			}		
		}
	#	print "$currnucpos, $curraapos, aaseq ", substr($aaseq, $curraapos, length($curraaseq)), " nucseq ", substr($nucseq, $currnucpos, length($curraaseq)*3), " $matchers, $newseq, ", translate ($newseq), "<br>";
		$newcurrstr = "$currnucpos..$newseq";
		push @tobeinsarr, $newcurrstr;
	}
	$newnuc = ''; $curpos = 0; print "<br>"; $cannotdo = 0; $cananddid= 0;
	foreach $treeeg (@tobeinsarr)
	{
		if ($treeeg =~ /([0-9]+)\.\.([A-Z]+)/) { $thispos = $1; $thisnew = $2; }
		unless ($thispos <= $curpos)
		{
			$newnuc .= substr ( $nucseq, $curpos, (($thispos)-$curpos));
			$newnuc .= $thisnew;
			$curpos = length ($newnuc);
#			print "..$thispos, $curpos<br>";
			$cananddid++;
		}
		else
		{
			$cannotdo++;
		}
	}
	$newnuc .= substr ($nucseq, $curpos, (length($nucseq)-$curpos));
print "Translation error! please notify admin<br>" if (translate($nucseq) ne translate($newnuc));
	if ($cannotdo > 0)
	{
		print "$cannotdo possible instance(s) of $remseq could not be inserted because they overlapped with other insertions that were made.\n";
		print break(1);
	}
	print "$cananddid instance(s) of $remseq were inserted.\n";
	print "</div>"; 
	print break(1);
	print ("<div id=\"gridgroup0\">Your altered nucleotide sequence:\n");
	print $query->textarea(-name=>'nusseq', -rows=>6, -columns=>120, -default=>$newnuc), break(1);
	@newal = ezalign($nucseq, $newnuc);
		@bcou = count($newnuc); 
	$GC = int(((($bcou[3]+$bcou[2])/$bcou[8])*100)+.5);
	$AT = int(((($bcou[0]+$bcou[1])/$bcou[8])*100)+.5);

	print "Your new sequence has $newal[0] identites, $newal[1] changes, and is $newal[4]% identical to the original sequence.<br>Composition : $GC% GC, $AT% AT</div>", break(3);
		print ("<div id=\"gridgroup1\" align =\"center\" style=\"position:relative \">\n");
	print $query->hidden(-name=>'passnucseq', value=>$nucseq);
	
	print ("<div id=\"notes\" style=\"text-align:center;\">");
	print ("You can take this nucleotide sequence to another module now.");
	print ("</div>");	
	print break(1), "<strong>Take this sequence to</strong>";
	print break(1), $query->submit(-value=>'Silent Site Insertion', -onclick=>'SSIns();'), "<-- to insert restriction sites";
	print break(1), $query->submit(-value=>'Silent Site Removal', -onclick=>'SSRem();'), "<-- to remove restriction sites";
	print break(1), $query->submit(-value=>'Oligo Design', -onclick=>'OligoDesign();'), "<-- to get a list of oligos for assembly";
	print break(1). $query->submit(-value=>'Sequence Analysis', -onclick=>'SeqAna();'), "<-- for information about this sequence";
	print $query->endform, $query->end_html;

}