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
 * Plot management for Project Rain
 * @author ishafer
 */

/**
 * @param summcont container for summary plots
 * @param maincont container for main plots
 */
function PlotManager(summcont, maincont) {
    this.plots = [];
    this.summcont = summcont;
    this.maincont = maincont;
    var self = this;
    this.selcb = function(ranges, obj) {
        self.plots = $.grep(self.plots, function(el, i) {
            return el.isActive();
        });
        $.each(self.plots, function(i, el) {
            if (!el.isSumm()) {
                el.setRange(ranges);
            } else {
                el.setSelection(ranges);
            }
        });
    }
    this.hovercb = function(pos, obj) {
        
    };
}
PlotManager.prototype.setHoverFn = function(hovercb) {
    for (var i = 0; i < this.plots.length; ++i) {
        this.plots[i].hovercb = hovercb;
    }
    this.hovercb = hovercb;
}
PlotManager.prototype.add = function(p) {
    this.plots.push(p);
    if (p.isSumm()) {
        this.summcont.append(p.el());
    } else {
        this.maincont.append(p.el());
    }
    p.selcb = this.selcb;
    p.hovercb = this.hovercb;
    p.remake();
}
PlotManager.prototype.remake = function() {
    for (var i = 0; i < this.plots.length; ++i) {
        this.plots[i].remake();
    }
}

/**
 * @param hmap Heatmap object
 * @param times list of timestamps
 * @param sizer has width(), height()
 */

function HeatmapPlot(hmap,sizer) {
    this.hmap = hmap;
    this.sizer = sizer;
    this.wasRemoved = false;
    this.selcb = function(ranges, obj) {};
    this.hovercb = function(ranges, obj) {};
    this.plotopts = {
        yaxis: { labelWidth: Plot.LABEL_WIDTH },
        xaxis: { mode: "time", tickLength: 6 },
          
    };

    this.plotel = $("<div>").css({
        width: sizer.width(),
        height: sizer.height()
    }).data("pobj", this);
    this.theel = $("<div>").append(this.plotel);
}
HeatmapPlot.prototype.getWidth = function() {
    return this.sizer.width();
}
HeatmapPlot.prototype.addArea = function(el) {
    this.theel.append(el);
}
HeatmapPlot.prototype.isActive = function() {
    return !this.wasRemoved;
}
HeatmapPlot.prototype.remove = function() {
    this.wasRemoved = true;
}
HeatmapPlot.prototype.isSumm = function() {
    return false;
}
HeatmapPlot.prototype.el = function() {
    return this.theel;
}
HeatmapPlot.prototype.appendTo = function(parent) {
    this.el().appendTo(parent);
}
HeatmapPlot.prototype.opts = function() {
    return this.plotopts;
}
HeatmapPlot.prototype.setRange = function(ranges) {
    $.extend(this.plotopts.xaxis, {
        min: ranges.xaxis.from, 
        max: ranges.xaxis.to
    });
    this.remake();
}
HeatmapPlot.prototype.setSelection = function(ranges) {
    this.suspend = true;
    this.pobj.setSelection(ranges);
    this.suspend = false;
}
HeatmapPlot.prototype.getIndices = function(tmin, tmax, next) {
    var self = this;
    self.hmap.getIndex(tmin, function(i1) {
        self.hmap.getIndex(tmax, function(i2) {
            var htmin = self.hmap.times[i1]*1000;
            var htmax = self.hmap.times[i2]*1000;
            next(i1, i2, htmin, htmax);            
        });
    });  
}
HeatmapPlot.prototype.remake = function() {
    var self = this;
    $(self.plotel).css({
        width: self.sizer.width(),
        height: self.sizer.height()
    });
    var xmin = self.plotopts.xaxis.min, xmax = self.plotopts.xaxis.max;
    if (!xmin) { xmin = 0; }
    if (!xmax) { xmax = 1e20; }

    //async plot from tmin to tmax
    var doplot = function(tmin, tmax) {
        //get index of tmin, tmax
        self.getIndices(tmin, tmax, function(i1, i2, htmin, htmax) {
            var nstreams = self.hmap.heatmap.length;
            self.pobj = $.plot(self.plotel, 
                [{data: [[htmin,0],[htmax,nstreams]]}],
                self.opts());
            self.pobj.hooks.drawOverlay.push(function(plot, ctx) {
                var width = plot.width();
                var height = plot.height();
                var offset = plot.getPlotOffset();
                ctx.save();
                ctx.translate(offset.left, offset.top);
                
                var dx = width/(i2-i1); //delta x
                var startx = 0;
                var dy = height/nstreams;
                for (var i = i1; i < i2; ++i) {
                    var starty = height-dy;
                    for (var s = 0; s < nstreams; ++s) {
                        ctx.fillStyle = self.hmap.colormap(
                            self.hmap.scale(self.hmap.heatmap[s][i])
                        );
                        ctx.fillRect(startx,starty,dx,dy);
                        starty -= dy;
                    }
                    startx += dx;
                }

                
                ctx.restore();
            });
            self.pobj.triggerRedrawOverlay();             
        });
    }

    doplot(xmin, xmax);

    this.el()
        .unbind("plotselected")
        .unbind("plothover")
        .bind("plotselected", function(event, ranges) {
            if (self.suspend) {
                return;
            }
            doplot(ranges.xaxis.from, ranges.xaxis.to);
            self.selcb(ranges, self);

            if (self.summ) {
                self.pobj.setSelection(ranges, true);
            }
        })
        .bind("plothover", function(event, pos, item) {
            self.hovercb(pos, self);
        });
}

/**
 * @param datasrc data source with get()
 * @param isSumm is this a summary plot?
 * @param sizer has: width(), height()
 * @param selcb what if any callback we should invoke on range selection
 * @param hovercb what if any callback we should invoke on hover
 */
function Plot(datasrc,isSumm,sizer,selcb,hovercb) {
    this.sizer = sizer;
    this.datasrc = datasrc;
    this.summ = isSumm;
    this.wasRemoved = false;
    this.plotopts = {
        yaxis: { labelWidth: Plot.LABEL_WIDTH },
        xaxis: { mode: "time", tickLength: 6 },
        selection: { mode: "x" },
        crosshair: { mode: "x" },
        legend: {
            show: true,
            position: "ne",
            labelFormatter: function(label, series) {
                return label + " ";
            }
        },
        grid: {
            backgroundColor: { colors: ["#fff", "#eee"]},
            hoverable: true
        },
        series: {
            shadowSize: 0
        }
    };
    if (isSumm) {
        $.extend(this.plotopts, {
            series: {
                lines: { show: true, lineWidth: 2 },
                shadowSize: 0            
            },
            yaxis: {ticks: 1, labelWidth: Plot.LABEL_WIDTH},
            legend: {
                show: true
            }
        });
    }
    if (!selcb) {
        selcb = function(ranges, obj) {};
    }
    if (!hovercb) {
        hovercb = function(pos, obj) {};
    }
    this.selcb = selcb;
    this.hovercb = hovercb;

    this.plotel = $("<div>").css({
        width: sizer.width(),
        height: sizer.height()
    }).data("pobj", this);
    this.theel = $("<div>").append(this.plotel);
}
Plot.prototype.getWidth = function() {
    return this.sizer.width();
}
Plot.prototype.addArea = function(el) {
    this.theel.append(el);
}
Plot.prototype.isActive = function() {
    return !this.wasRemoved;
}
Plot.prototype.remove = function() {
    this.wasRemoved = true;
}
Plot.LABEL_WIDTH = 50;
Plot.prototype.isSumm = function() {
    return this.summ;
}
Plot.prototype.el = function() {
    return this.theel;
}
Plot.prototype.appendTo = function(parent) {
    this.el().appendTo(parent);
}
Plot.prototype.opts = function() {
    return this.plotopts;
}
Plot.prototype.setRange = function(ranges) {
    $.extend(this.plotopts.xaxis, {
        min: ranges.xaxis.from, 
        max: ranges.xaxis.to
    });
    this.remake();
}
Plot.prototype.setSelection = function(ranges) {
    this.suspend = true;
    this.pobj.setSelection(ranges);
    this.suspend = false;
}
Plot.prototype.remake = function() {
    var self = this;
    $(self.plotel).css({
        width: self.sizer.width(),
        height: self.sizer.height()
    });
    var xmin = self.plotopts.xaxis.min, xmax = self.plotopts.xaxis.max;
    if (!xmin) {
        xmin = 0;
    }
    if (!xmax) {
        xmax = 1e20;
    }
    //those would be the old ranges, matey.
    if (false) {
        var ax = self.pobj.getXAxes();
        if (ax.length) {
            ax = ax[0];
        }
        xmin = ax.min ? ax.min : ax.datamin; //or datamin
        xmax = ax.max ? ax.max : ax.datamax; //or datamax
    }

    //async plot from tmin to tmax
    var doplot = function(tmin, tmax) {
        self.datasrc.get(tmin, tmax, function(dta) {
            self.pobj = $.plot(self.plotel, 
                dta,
                self.opts());
        });
    }

    doplot(xmin, xmax);

    this.el()
        .unbind("plotselected")
        .unbind("plothover")
        .bind("plotselected", function(event, ranges) {
            if (self.suspend) {
                return;
            }
            doplot(ranges.xaxis.from, ranges.xaxis.to);
            self.selcb(ranges, self);

            if (self.summ) {
                self.pobj.setSelection(ranges, true);
            }
        })
        .bind("plothover", function(event, pos, item) {
            self.hovercb(pos, self);

            self.pobj.setCrosshair(pos);
        });
}