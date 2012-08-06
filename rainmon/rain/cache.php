<?php

$req = $_GET["req"] or die("Must specify req= parameter");

$CACHEDIR = "cache";

function sanitized($getkey) {
	return str_replace("/", "_", $_GET[$getkey]);
}

switch ($req) {
	case "getsavenames":
		$names = array();
		if ($dh = opendir($CACHEDIR)) {
			while (false !== ($en = readdir($dh))) {
				if ($en != "." && $en != "..") {
					array_push($names, $en);
				}
			}
		}
		echo json_encode($names);
		break;
	case "getprojection":
		$path = $CACHEDIR . "/" . sanitized("savename");
		echo file_get_contents($path . "/projection.json");
		break;
	case "getheatmap":
		$path = $CACHEDIR . "/" . sanitized("savename");
		echo file_get_contents($path . "/projection.json");
		break;
	case "getsummary":
		$path = $CACHEDIR . "/" . sanitized("savename");
		$index = (array) json_decode(file_get_contents($path . "/index.json"));
		$contents = array();
		if ($dh = opendir($path)) {
			while (false !== ($en = readdir($dh))) {
				if ($en != "." && $en != "..") {
					array_push($contents, substr($en, 0, -5));
				}
			}
		}
		$index["contents"] = $contents;
		$index["tsample"] = json_decode(file_get_contents($path . "/tsample.json"));
		echo json_encode($index);
		break;
	case "data": //?req=data&tmin=0&tmax=10000000000&node=&metric=hv.0
		$path = $CACHEDIR . "/" . sanitized("savename");
		//downsampling length
		$DSLEN = 1000;

		$tmin = $_GET["tmin"]+1 or die("Must specify tmin= parameter");
		$tmax = $_GET["tmax"]+1 or die("Must specify tmax= parameter");
		$metric = $_GET["metric"] or die("Must specify metric= parameter");

		$times = json_decode(file_get_contents($path . "/tsample.json"));
		$data = json_decode(file_get_contents($path . "/" . $metric . ".json"));
		$ret = array();
		$dx = 0;
		while ($times[$dx] < $tmin && $dx < count($times) - 1) {
			++$dx;
		}
		while ($times[$dx] < $tmax && $dx < count($times) - 1) {
			array_push($ret, array($times[$dx],$data[$dx]));
			++$dx;
		}
		$skip = intval(floor(count($ret)/$DSLEN));

		$result = $ret;
		if ($skip > 1) {
			$retds = array();
			for ($i = 0; $i < count($ret); $i += $skip) {
				array_push($retds, $ret[$i]);
			}
			$result = $retds;
		}
		echo json_encode(array("dta" => $result));
		break;
	case "default":
		die("Invalid request");
}

//don't print anything more.

?>