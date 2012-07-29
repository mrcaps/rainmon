## Data Sources

RainMon works with timeseries databases that use the OpenTSDB wire format for sending data. The code includes a server that delivers popular RRDtool files in this format. Each data source runs as a server, and the analysis pipeline connects to one of those servers to get data.

To get a data source working with RainMon, it must be added to the `code/ui/media/js/selector.js` file, which contains definitions for each source. Each definition consists of the following:

 * `host`: the IP address or hostname of the server (OpenTSDB or RRD/Ganglia server)
 * `port`: the port of the server
 * `name`: the name to display in the UI
 * `getCompNames`: a function that returns which machines/nodes the data source provides
 * `getAttrNames`: a function that returns which metrics the data source provides
 * `getCompSel`: a function that determines which machines/nodes should be selected by default in the UI. It can decide based on the index of the machine/node (`i`) or its name (`el`). 
 * `getAttrSel`: a function that determines which metrics should be selected by default.
 * `compcols`: the number of columns to display the machines/nodes in (1 for a list, more for a grid)
 * `cloudifyNames`: specify `true` to append `cloud` to the beginning of each machine/node name.

Details for configuring an RRD server and generating a list suitable for `getCompNames` and `getAttrNames` are available [on the RRD page of the guide](RRD)