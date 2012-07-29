## RRD Data Source

Part of this code distribution (in the `rrd` folder) is a server that provides the RRD format as a data source. To create an RRD data source, do the following:

 * In `code/config.json`, set `rrddir` to the location of the directory that RRD data will be served from.
 * Start the RRD server by running `python cmuserver.py` from the `rrd` directory.
 * Create a specification for the server as described [here](datasources.html). The server runs on port 8124 by default.

To help with generating a list of metrics and nodes in RRD files suitable for pasting into `getCompNames` and `getAttrNames`, we provide a tool that gets information about each RRD file in a directory and prints it. Run `python rrd/rrdindex.py` to generate the pasteable list of node and metric names.