# CMU.net Dataset

RainMon

## About

This "smokeping" dataset consists of recordings of the time taken for a packet to traverse the Internet from CMU to another location and return. It has been collected and stored by CMU Network Operations, and dataset comprises approximately a year of ping times between Carnegie Mellon - Pittsburgh and six destinations:

 * Local (cmu.net)
 * Penn State
 * CMU West
 * A CMU server in New York
 * CMU Qatar

## Format

The `.xml` files contained in this directory are XML dumps of RRD (round robin database) databases. We provide them in this format since the native RRD format is not platform-agnostic. To use these files with RRDtool, use `rrdtool restore`, which is documented here: [rrdrestore](http://oss.oetiker.ch/rrdtool/doc/rrdrestore.en.html).

## Usage with the tool

After converting the data to native `.rrd` format, RainMon consumes the data through an OpenTSDB-style API. The server is provided in the `code/rrd` directory. To reproduce the results in the RainMon paper, the analysis should be performed with `get_default_pipeline` (see `code/pipeline.py`).

## Acknowledgment

This dataset is provided courtesy of the network operations team at CMU.