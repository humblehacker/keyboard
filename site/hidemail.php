<?PHP  // -*- php -*-
function HideEmail($user, $host, $subject = '') 
{
    $MailLink = '<a href="mailto:' . $user . '@' . $host;
    if ($subject != '')
		$MailLink .= '?subject=' . urlencode($subject);
    $MailLink .= '">' . $user . '@' . $host . '</a>';
    
    $MailLetters = '';
    for ($i = 0; $i < strlen($MailLink); $i ++)
    {
		$l = substr($MailLink, $i, 1);
			if (strpos($MailLetters, $l) === false)
			{
				$p = rand(0, strlen($MailLetters));
				$MailLetters = substr($MailLetters, 0, $p) .
				  $l . substr($MailLetters, $p, strlen($MailLetters));
			}
    }
    
    $MailLettersEnc = str_replace("\\", "\\\\", $MailLetters);
    $MailLettersEnc = str_replace("\"", "\\\"", $MailLettersEnc);

    $MailIndexes = '';
    for ($i = 0; $i < strlen($MailLink); $i ++)
    {
		$index = strpos($MailLetters, substr($MailLink, $i, 1));
		$index += 48;
		$MailIndexes .= chr($index);
    }
    $MailIndexes = str_replace("\\", "\\\\", $MailIndexes);
    $MailIndexes = str_replace("\"", "\\\"", $MailIndexes);
    
?><script type="text/javascript"><!--
	ML="<?= $MailLettersEnc ?>";
	MI="<?= $MailIndexes ?>";
	OT="";
	for(j=0;j<MI.length;j++){
		OT+=ML.charAt(MI.charCodeAt(j)-48);
	}
	document.write(OT);
// --></script><noscript><p>Sorry, you need javascript to view this email address</p></noscript><?PHP
}

function HideEmailWithName($name, $user, $host) {
    print $name . " &lt;";
    HideEmail($user, $host);
    print "&gt;";
}
?>
