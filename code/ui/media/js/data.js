//Copyright (c) 2012, Carnegie Mellon University.
//All rights reserved.
//
//Redistribution and use in source and binary forms, with or without
//modification, are permitted provided that the following conditions
//are met:
//1. Redistributions of source code must retain the above copyright
//   notice, this list of conditions and the following disclaimer.
//2. Redistributions in binary form must reproduce the above copyright
//   notice, this list of conditions and the following disclaimer in the
//   documentation and/or other materials provided with the distribution.
//3. Neither the name of the University nor the names of its contributors
//   may be used to endorse or promote products derived from this software
//   without specific prior written permission.

/**
 * Data sources
 * @author ishafer
 */

function FakeData(freq,lbl) {
    this.freq = freq;
    this.dta = [];
    var TSTART = 1319000400699;
    var TEND = 1321708772699;
    var NPOINTS = 500;
    for (var i = 0; i < NPOINTS; ++i) {
        var t = (i+0.0)/NPOINTS*(TEND-TSTART)+TSTART;
        this.dta.push([t, Math.sin(t*freq)+1]);
    }
    this.lbl = lbl;
}
FakeData.prototype.get = function(tmin, tmax, next) {
    next([{
        color: "rgb(255,0,0)",
        data: this.dta,
        label: this.lbl
    }]);
}

/**
 * @param ids a list of timeseries identifiers
 * each id looks like: {node:"cirrus1", metric:"cpu.usage.average"} 
 */
function BoundData(savename, ids) {
    this.ids = ids;
    this.series = [];
    this.savename = savename;
}
BoundData.prototype.pull = function(tmin, tmax, next) {
    this.series = [];
    var self = this;
    $.each(self.ids, function(i, id) {
        var rparams;
        $.getJSON("data", rparams = {
            savename: self.savename,
            tmin: tmin,
            tmax: tmax,
            node: id.node,
            metric: id.metric
        }, function(res) {
            var dta = res.dta;
            for (var i = 0; i < dta.length; ++i) {
                //multiply by 1000 for milliseconds for server data
                dta[i][0] *= 1000;
                //nuke the NaNs
                if (dta[i][1] != dta[i][1]) {
                    dta[i][1] = "NaN";
                }
            }
            self.series.push({
                data: dta,
                label: id.node + " " + id.metric
            });
            if (self.series.length == self.ids.length) {
                next();
            }
        });
        //console.log("Request params were ", rparams);
    });
}
BoundData.cmpfn = function(a,b) {
    return a[0] - b[0];
};
BoundData.prototype.get = function(tmin, tmax, next) {
    var self = this;
    //check to see if we need to reload
    var dxmin = 0, hbnd = 0;
    if (self.series[0]) {
        var dxmin = binSearch(self.series[0].data, [tmin, 0], BoundData.cmpfn);
        var dxmax = binSearch(self.series[0].data, [tmax, 0], BoundData.cmpfn);
        var hbnd = -self.series[0].data.length + 2;
    }
    if (dxmin == 0 || dxmax < hbnd) {
        //query is out of range
        this.pull(tmin, tmax, function() {
            next(self.series);
        });
    } else {
        //use cache
        next(self.series);
    }
}

/**
 * Binary search. Return -(pos_to_insert) if value is not found.
 * @param buf buffer to search
 * @param val x (time) value to search for
 */
var binSearch = function(arr, val, comparator) {
    if (!comparator) {
        comparator = function(a,b) {
            return a - b;
        };
    }
    var lo = 0;
    var hi = arr.length-1;
    var cmp = 0;
    var mid = 0;
    while (lo <= hi) {
        mid = Math.floor(lo/2 + hi/2);
        cmp = comparator(val, arr[mid]);
        if (cmp < 0) {
            hi = mid - 1;
        } else if (cmp > 0) {
            lo = mid + 1;
        } else {
            return mid;
        }
    }
    
    return -mid;
}