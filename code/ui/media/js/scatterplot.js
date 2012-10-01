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

function Scatterplot(res,el,width,height) {
    this.res = res;
    this.el = el;
    this.width = width;
    this.height = height;
    this.enabled = false;
    this.loaded = false;
}
Scatterplot.prototype.load = function(next) {
    var self = this;
    if (!this.proj) {
        this.res.getProjection(function(proj) {
            self.res.getMeta(function(meta) {
                self.proj = proj;
                self.meta = meta;
            });
        });
        next();
    } else {
        next();
    }
}
Scatterplot.prototype.toggle = function() {
    var self = this;
    this.enabled = !this.enabled;
    $(this.el).animate({
        height: this.enabled ? this.height : 0
    });
    if (!this.loaded) {
        this.loaded = true;
        var PAD = 10;
        this.plotel = $("<div>").css({
            left: PAD,
            top: PAD,
            width: this.width-PAD*2,
            height: this.height-PAD*2
        }).appendTo(this.el);

        this.load(function() {
            self.doPlot(0,1);
        });
    }
}
Scatterplot.prototype.getSymbol = function(dx) {
    var syms = ["circle", "square", "diamond", "triangle", "cross"];
    return syms[dx%syms.length];
}
Scatterplot.prototype.doPlot = function(hv1dx,hv2dx) {
    var self = this;
    var dta = [];
    /*
    //plot all
    for (var i = 0; i < this.proj.length; ++i) {
        dta.push([this.proj[i][hv1dx], this.proj[i][hv2dx]]);
    }
    var toplot = [{label: "all", data: dta, points: {symbol: "circle"}}];
    */

    var mbins = this.getMetricBins(this.meta.ts_names);
    var toplot = [];
    var dx = 0;
    $.each(mbins, function(k,v) {
        var set = {label: k, data: [], points: {symbol: self.getSymbol(dx)}};
        for (var i = 0; i < v.length; ++i) {
            set.data.push([self.proj[v[i].index][hv1dx], self.proj[v[i].index][hv2dx]]);
        }
        ++dx;
        toplot.push(set);
    });

    var plot = $.plot(this.plotel, toplot, {
        series: {points: { show: true, radius: 3 }},
        grid: { hoverable: true, clickable: true },
        xaxis: { show: false },
        yaxis: { show: false }
    });
    var tip = $("<div>").css({
        "position":"absolute",
        "font-weight":"bold"
    }).appendTo(this.plotel);

    $(this.plotel).unbind("plothover");
    $(this.plotel).bind("plothover", function(evt,pos,item) {
        if (item) {
            var bin = mbins[item.series.label];
            var pt = bin[item.dataIndex];
            var o = plot.pointOffset({x: item.datapoint[0], y: item.datapoint[1]});
            $(tip).css({
                "left": o.left+5,
                "top": o.top-22
            }).text(pt.node);

        }
    });
}
/**
 * Assume the metric name is the second dot separated part of the full name
 */
Scatterplot.prototype.getMetricName = function(fullname) {
    var splt = fullname.indexOf(".");
    if (splt > -1) {
        return {
            node: fullname.substring(0,splt),
            metric: fullname.substring(splt+1)
        };
    } else {
        return {
            node: fullname,
            metric: "other"
        };
    }
}
Scatterplot.prototype.getMetricBins = function(tsnames) {
    var mbins = {};
    for (var i = 0; i < tsnames.length; ++i) {
        var n = this.getMetricName(tsnames[i]);
        if (!(n.metric in mbins)) {
            mbins[n.metric] = [];
        };
        if (n.metric in mbins) {
            mbins[n.metric].push({
                node: n.node,
                index: i
            });
        }
    }
    return mbins;
}