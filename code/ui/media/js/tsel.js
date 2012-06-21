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
 * Timeseries selector
 * @param res a result object
 */
function TSel(res) {
	this.res = res;
	this.lst = [];
}
TSel.prototype.init = function() {
	var self = this;
	self.lst = [];
	self.res.getMeta(function(meta) {
		$.each(meta.contents, function(i, el) {
			if (el == "index" || el == "tsample") {
				return;
			}
			self.lst.push({
				value: el,
				label: el
			});
		});
		self.makeUI();
	});
}
TSel.prototype.fmtMetric = function(text) {
	var elts = text.split(".");
	if (elts.length > 2) {
		return "" +
			elts[0] + 
			"<br/>" + 
			elts.slice(1,-1).join(".") + 
			"<br/>" + 
			"<b>" + elts[elts.length-1] + "</b>"; 
	} else {
		return text;
	}
}
TSel.prototype.makeUI = function() {
	var self = this;
	$("#tsinput").autocomplete({
		minLength: 0,
		source: self.lst,
		focus: function(evt, ui) {
			$("#tsinput").val(ui.item.label);
			return false;
		},
		select: function(evt, ui) {
			$("<li>")
				.append(self.fmtMetric(ui.item.label))
				.data("metric", ui.item.value)
				.appendTo($("#lst-newplot"));
			$("#tsinput").val("");
			return false;
		}
	}).data("autocomplete")._renderItem = function(ul, item) {
		return $("<li>")
			.data("item.autocomplete", item)
			.append("<a>" + item.label + "</a>")
			.appendTo(ul);	
	};

	$("#btn-addplot").button().click(function() {
		var bndlst = [];
		var hvs = [];
		$("#lst-newplot").children().each(function(i, el) {
			var mname = $(el).data("metric");
			var msplit = mname.split(".");
			if (msplit[0].substring(0,2) == "hv") {
				hvs.push(parseInt(msplit[1]));
			}
			bndlst.push({node:"", metric:mname});
		});
		var dsrc = new BoundData(self.res.savename, bndlst);
		var theplot = new Plot(dsrc, false, new Sizer(200), null, null)
		mgr.add(theplot);
		for (var i = 0; i < hvs.length; ++i) {
			TSel.addHvDots(theplot, hvs[i]);
		}
		$("#lst-newplot").empty();
	});
}
TSel.addHvDots = function(theplot, hvdx) {
	Exec.res.getProjection(function(proj) {
		Exec.res.getMeta(function(meta) {
			var tsnames = meta["ts_names"];
			var tosort = [];
			for (var i = 0; i < proj.length; ++i) {
				tosort.push({
					name: tsnames[i], 
					val: proj[i][hvdx]
				});
			}
			//sort by descending absolute value
			tosort.sort(function(a,b) {
				return Math.abs(b.val) - Math.abs(a.val);
			});
			var maxv = Math.abs(tosort[0].val),
				minv = Math.abs(tosort[tosort.length-1].val);
			
			var nfo = $("<div>").css({
				"font-size":"80%",
				"overflow":"hidden",
				"padding-left":Plot.LABEL_WIDTH,
				"position":"relative"
			});
			for (var i = 0; i < tosort.length; ++i) {
				var it = tosort[i];
				/* //for basic text
				nfo.append(
					$("<span>")
						.css({"margin-right":"8px"})
						.text(it.name)
				);*/
				var plotw = theplot.getWidth() - Plot.LABEL_WIDTH;
				var offset = (Math.abs(it.val) - minv) / (maxv - minv) * plotw;
				nfo.append(
					$("<div>")
						.attr("title",it.name + "|val=" + (Math.round(it.val*1e3)/1e3))
						.css({
							"position":"absolute",
							"top":"-15px",
							"opacity":0.5,
							"left":Plot.LABEL_WIDTH + plotw - offset,
							"font-size":"35px"
						})
						.html("&bull;")
						.cluetip({
							cluetipClass: "jtip", arrows: true,
							splitTitle: "|",
							showTitle: true,
							positionBy: "bottomTop"
						})
				);
			}
			nfo.append($("<div>").html("&nbsp;&nbsp;"));
			theplot.addArea(nfo);
		});
	});
};