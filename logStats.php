<?php
require_once('config.php');

$output = '';

if (!$cacheFileEnabled || !file_exists($cacheFile) || filemtime($cacheFile) + $cacheFileMaxAge < time()) {
	$scanme = array();
	exec('python logalyzer/myStats.py -html ' . implode(' ', $logFiles), $scanme);
	$output = implode("\n", $scanme);
	file_put_contents($cacheFile, $output);
} else {
	$output = file_get_contents($cacheFile);
}


print $output;

?>