<?php

exec('python logalyzer/myStats.py', $scanme);
$scanme = implode("\n", $scanme);
print $scanme;
?>
