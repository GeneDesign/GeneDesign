// JavaScript Document<!-- used in makegene iteration oneorganism = 1;function SWMarkOptimal(f) {	if (organism == 1)	//Saccharomyces Cerevsiae	{		f.A.selectedIndex = 3;		f.C.selectedIndex = 1;		f.D.selectedIndex = 0;		f.E.selectedIndex = 0;		f.F.selectedIndex = 0;		f.G.selectedIndex = 3;		f.H.selectedIndex = 0;		f.I.selectedIndex = 1;		f.K.selectedIndex = 1;		f.L.selectedIndex = 5;		f.M.selectedIndex = 0;		f.N.selectedIndex = 0;		f.P.selectedIndex = 0;		f.Q.selectedIndex = 0;		f.R.selectedIndex = 0;		f.S.selectedIndex = 5;		f.T.selectedIndex = 1;		f.V.selectedIndex = 3;		f.W.selectedIndex = 0;		f.Y.selectedIndex = 0;   	}    else if (organism == 2) //Escherichia Coli 	{		f.A.selectedIndex = 3;		f.C.selectedIndex = 0;		f.D.selectedIndex = 0;		f.E.selectedIndex = 0;		f.F.selectedIndex = 0;		f.G.selectedIndex = 3;		f.H.selectedIndex = 0;		f.I.selectedIndex = 1;		f.K.selectedIndex = 0;		f.L.selectedIndex = 2;		f.M.selectedIndex = 0;		f.N.selectedIndex = 0;		f.P.selectedIndex = 2;		f.Q.selectedIndex = 1;		f.R.selectedIndex = 5;		f.S.selectedIndex = 5;		f.T.selectedIndex = 1;		f.V.selectedIndex = 3;		f.W.selectedIndex = 0;		f.Y.selectedIndex = 0;	} 	else if (organism == 3) // Homo Sapiens	{		f.A.selectedIndex = 1;		f.C.selectedIndex = 0;		f.D.selectedIndex = 0;		f.E.selectedIndex = 1;		f.F.selectedIndex = 0;		f.G.selectedIndex = 1;		f.H.selectedIndex = 0;		f.I.selectedIndex = 1;		f.K.selectedIndex = 1;		f.L.selectedIndex = 2;		f.M.selectedIndex = 0;		f.N.selectedIndex = 0;		f.P.selectedIndex = 1;		f.Q.selectedIndex = 1;		f.R.selectedIndex = 3;		f.S.selectedIndex = 0;		f.T.selectedIndex = 1;		f.V.selectedIndex = 2;		f.W.selectedIndex = 0;		f.Y.selectedIndex = 0;	}	else if (organism == 4) //Caenorhabditis elegans	{		f.A.selectedIndex = 3;		f.C.selectedIndex = 1;		f.D.selectedIndex = 1;		f.E.selectedIndex = 0;		f.F.selectedIndex = 0;		f.G.selectedIndex = 0;		f.H.selectedIndex = 1;		f.I.selectedIndex = 2;		f.K.selectedIndex = 1;		f.L.selectedIndex = 3;		f.M.selectedIndex = 0;		f.N.selectedIndex = 1;		f.P.selectedIndex = 0;		f.Q.selectedIndex = 0;		f.R.selectedIndex = 5;		f.S.selectedIndex = 5;		f.T.selectedIndex = 3;		f.V.selectedIndex = 3;		f.W.selectedIndex = 0;		f.Y.selectedIndex = 0;	}
	else if (organism == 5) //Drosophila melanogaster
	{
		f.A.selectedIndex = 1;
		f.C.selectedIndex = 0;
		f.D.selectedIndex = 0;
		f.E.selectedIndex = 1;
		f.F.selectedIndex = 0;
		f.G.selectedIndex = 1;
		f.H.selectedIndex = 0;
		f.I.selectedIndex = 1;
		f.K.selectedIndex = 1;
		f.L.selectedIndex = 2;
		f.M.selectedIndex = 0;
		f.N.selectedIndex = 0;
		f.P.selectedIndex = 1;
		f.Q.selectedIndex = 1;
		f.R.selectedIndex = 3;
		f.S.selectedIndex = 3;
		f.T.selectedIndex = 1;
		f.V.selectedIndex = 2;
		f.W.selectedIndex = 0;
		f.Y.selectedIndex = 0;
	}
	else if (organism == 6) //Bacillus subtilis
	{
		f.A.selectedIndex = 3;
		f.C.selectedIndex = 0;
		f.D.selectedIndex = 0;
		f.E.selectedIndex = 0;
		f.F.selectedIndex = 0;
		f.G.selectedIndex = 0;
		f.H.selectedIndex = 1;
		f.I.selectedIndex = 1;
		f.K.selectedIndex = 0;
		f.L.selectedIndex = 4;
		f.M.selectedIndex = 0;
		f.N.selectedIndex = 0;
		f.P.selectedIndex = 3;
		f.Q.selectedIndex = 0;
		f.R.selectedIndex = 5;
		f.S.selectedIndex = 5;
		f.T.selectedIndex = 3;
		f.V.selectedIndex = 3;
		f.W.selectedIndex = 0;
		f.Y.selectedIndex = 0;
    }}//--><!-- Used in makegene iteration twofunction pick() {	len1 = menu1.length ;    for ( i=0; i<len1 ; i++)	{        if (menu1.options[i].selected == true ) 		{            len2 = menu2.length;            menu2.options[len2]= new Option(menu1.options[i].text);        }    }    for ( i = (len1 -1); i>=0; i--)	{        if (menu1.options[i].selected == true ) 		{            menu1.options[i] = null;        }    }	flag2.checked = false;	flag3.checked = false;	flag1.checked = true;}function vpicka(){	len1 = v1.length;	for ( i=0; i<len1; i++)	{		if (v1.options[i].selected == true )		{			len2 = v2.length;			v2.options[len2] = new Option(v1.options[i].text);		}	}	for ( i = (len1 - 1); i >=0; i--)	{		if (v1.options[i].selected == true )		{			v1.options[i] = null;		}	}}function vpickp(){	len1 = v1.length;	for ( i=0; i<len1; i++)	{		if (v1.options[i].selected == true )		{			len3 = v3.length;			v3.options[len3] = new Option(v1.options[i].text);		}	}	for ( i = (len1 - 1); i >=0; i--)	{		if (v1.options[i].selected == true )		{			v1.options[i] = null;		}	}}function vabandona(){	len2 = v2.length;	for (i=0; i<len2; i++)	{		if (v2.options[i].selected == true)		{			len1 = v1.length;			v1.options[len1]=new Option(v2.options[i].text);		}	}	for (i=(len2-1); i>=0; i--)	{		if (v2.options[i].selected == true)		{			v2.options[i] = null;		}	}}function vabandonp(){	len3 = v3.length;	for (i=0; i<len3; i++)	{		if (v3.options[i].selected == true)		{			len1 = v1.length;			v1.options[len1]=new Option(v3.options[i].text);		}	}	for (i=(len3-1); i>=0; i--)	{		if (v3.options[i].selected == true)		{			v3.options[i] = null;		}	}}function pickn() {	len1 = menn1.length ;    for ( i=0; i<len1 ; i++)	{        if (menn1.options[i].selected == true ) 		{            len2 = menn2.length;            menn2.options[len2]= new Option(menn1.options[i].text);        }    }    for ( i = (len1 -1); i>=0; i--)	{        if (menn1.options[i].selected == true ) 		{            menn1.options[i] = null;        }    }}function abandon() {    len2 = menu2.length ;    for ( i=0; i<len2 ; i++)		{    	if (menu2.options[i].selected == true ) 		{        	len1 = menu1.length;        	menu1.options[len1]= new Option(menu2.options[i].text);        }	}    for ( i=(len2-1); i>=0; i--) 	{   		if (menu2.options[i].selected == true ) 		{        	menu2.options[i] = null;        }    }}function abandonn() {    len2 = menn2.length ;    for ( i=0; i<len2 ; i++)		{    	if (menn2.options[i].selected == true ) 		{        	len1 = menu1.length;        	menn1.options[len1]= new Option(menn2.options[i].text);        }	}    for ( i=(len2-1); i>=0; i--) 	{   		if (menn2.options[i].selected == true ) 		{        	menn2.options[i] = null;        }    }}function vselect(){	len3 = v3.length;	for (i=0; i< len3; i++)	{		v3.options[i].selected = true;	}	len2 = v2.length;	for (i=0; i<len2; i++)	{		v2.options[i].selected = true;	}}function selectem() {	len3 = menn2.length ;	for (i=0; i< len3; i++) 	{		menn2.options[i].selected = true;	}	if (flag1.checked == true)	{			len2 = menu2.length ;		for (i=0; i< len2; i++) 		{			menu2.options[i].selected = true;		}	}	else if (flag2.checked == true || flag3.checked == true)	{		len2 = menu2.length ;		for (i=0; i< len2; i++) 		{			menu2.options[i].selected = false;		}	}	if (text == 1)	{		len2 = menu2.length ;		for (i=0; i< len2; i++) 		{			menu2.options[i].selected = true;		}	}}function OrderForm(){	document.form1.target = "_blank";	document.form1.action = "./order.cgi";}function ReportForm(){	document.form1.target = " ";	document.form1.action = "./report.cgi";}function FASTArizer(inp){	document.form2.target = "_blank";	document.form2.swit.value = inp;}function EnzMostPerm(){	document.form1.crEndss[0].checked = true;	document.form1.crEndss[1].checked = false;
	document.form1.crCutss[0].checked = true;
	document.form1.crCutss[1].checked = false;
	document.form1.crOhangss[0].checked = true;
	document.form1.crOhangss[1].checked = false;	document.form1.crLengs[0].checked = true;	document.form1.crLengs[1].checked = false;	document.form1.crAmbis[0].checked = true;	document.form1.crAmbis[1].checked = false;
	document.form1.crBuffs[0].checked = true;
	document.form1.crBuffs[1].checked = false;
	document.form1.crHeats[0].checked = true;
	document.form1.crHeats[1].checked = false;
	document.form1.crTemps[0].checked = true;
	document.form1.crTemps[1].checked = false;
	document.form1.crStars[0].checked = true;
	document.form1.crStars[1].checked = false;
	document.form1.crStars[2].checked = false;
	document.form1.crMeths[0].checked = true;
	document.form1.crMeths[1].checked = false;
	document.form1.crMeths[2].checked = false;	document.form1.crPrir[0].checked = true;	document.form1.crPrir[1].checked = false;}function VecMostPerm(){	document.form1.crSize[0].checked = true;	document.form1.crSize[1].checked = false;	document.form1.crNabs[0].checked = true;	document.form1.crNabs[1].checked = false;	document.form1.crResp[0].checked = true;	document.form1.crResp[1].checked = false;}<!-- used in renzymeinterface, all iterationsfunction SSISum(pre){	if (pre != 1)	{		document.form1.swit.value = 'wu';	}	else	{		document.form1.swit.value = 'ih';	}}function OliISum(pre){	if (pre == 1)	{		document.form1.swit.value = 'all';	}	else	{		document.form1.swit.value = 'some';	}}function REBB(){	document.form1.action = './gdOliDes.cgi';}
function UserBB()
{
	document.form1.action = './gdUserDes.cgi';
}
function OlBB()
{
	document.form1.action = './gdOlapDes.cgi';
}function SSRem(){	document.form1.action = './gdSSRem.cgi';}function SSIns(){	document.form1.action = './gdSSIns.cgi';}function toCodJug(){	document.form1.action = './gdCodJug.cgi';}function SeqAna(){	document.form1.action = './gdSeqAna.cgi';}function CodJug(hal, loi){		if (hal == 1)	{		document.form1.PASSNUCSEQUENCE.value = document.form1.optinucseq.value;	}	if (hal == 2)	{		document.form1.PASSNUCSEQUENCE.value = document.form1.lsopnucseq.value;	}	if (hal == 3)	{		document.form1.PASSNUCSEQUENCE.value = document.form1.msdfnucseq.value;	}	if (hal == 0)	{		document.form1.PASSNUCSEQUENCE.value = document.form1.randnucseq.value;	}
	if (hal == 4)
	{
		document.form1.PASSNUCSEQUENCE.value = document.form1.lsdfnucseq.value;
	}	if (loi == 0)	{		document.form1.action = './gdSSIns.cgi';	}	if (loi == 1)	{			document.form1.action = './gdSSRem.cgi';	}	if (loi == 2)	{		document.form1.action = './gdSeqAna.cgi';	}	if (loi == 3)	{		document.form1.action = './gdOliDes.cgi';	}
	if (loi == 4)
	{
		document.form1.action = './gdUserDes.cgi';
	}
	if (loi == 5)
	{
		document.form1.action = './gdOlapDes.cgi';
	}	}//-->