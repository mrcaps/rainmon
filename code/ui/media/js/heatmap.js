/**
 * Heatmap
 * @param res the results holder
 * @param el the element to display the heatmap inside
 */
function Heatmap(res,el,width,height) {
	this.res = res;
	this.el = el;
	this.width = width;
	this.height = height;
	this.enabled = false;
	this.cols = 8;
	this.rows = 2;
}
Heatmap.prototype.load = function(next) {
	var self = this;
	if (!self.heatmap) {
		self.res.getMeta(function(meta) {
			self.times = meta.tsample;
			self.res.getHeatmap(function(map) {
				if (null == map) {
					return;
				}
				self.heatmap = map;

				self.allmin = 1e10;
				self.allmax = -1e10;
				for (var i = 0; i < map.length; ++i) {
					for (var j = 0; j < map[i].length; ++j) {
						self.allmin = Math.min(self.allmin, map[i][j]);
						self.allmax = Math.max(self.allmax, map[i][j]);
					}
				}

				next();
			});
		});
	} else {
		next();
	}
}
Heatmap.prototype.toggle = function() {
	var self = this;
	self.enabled = !self.enabled;
	$(self.el).animate({
		height: this.enabled ? self.height : 0
	});
	if (!self.items) {
		this.load(function() {
			self.items = [];

			var XPAD = 16, YPAD = 16;
			var xp = XPAD;
			var yp = YPAD;
			var hstep = (self.width - xp*2) / self.cols;
			var vstep = (self.height - yp*2) / self.rows;
			for (var i = 0; i < self.heatmap.length; ++i) {
				if (i % self.cols == 0) {
					xp = XPAD;
					yp += vstep;
				}
				var it = $("<div>").css({
					"position": "absolute",
					"left": xp,
					"top": yp,
					"width": hstep,
					"height": vstep,
					"border": "1px solid #ccc",
					"text-align": "center",
					"line-height": vstep + "px",
					"background-color": "#000",
					"color": "#fff"
				}).text((i+1)+"");
				xp += hstep;

				self.items.push(it);
				$(self.el).append(it);
			}
			//hardcoded for now
		});
	}
}
/**
 * @param val strength value between 0 and 1
 */
Heatmap.prototype.colormapRed = function(val) {
	return [val, 0, 0];
};
Heatmap.prototype.colormapJet = function(val) {
	return [
		val,
		(0.5-Math.abs(0.5-val))*2,
		1-val
	];
};
Heatmap.prototype.colormap = function(val) {
	var col = this.colormapJet(val);
	for (var j = 0; j < col.length; ++j) {
		col[j] = Math.max(0, Math.min(254, Math.round(col[j]*255)));
	}
	return "rgb(" + col[0] + "," + col[1] + "," + col[2] + ")";
};
Heatmap.prototype.scale = function(val) {
	return (val - this.allmin) / (this.allmax - this.allmin)
}
Heatmap.prototype.showIndex = function(dx) {
	if (this.enabled && this.items && this.heatmap) {
		if (dx >= 0 && dx < this.heatmap[0].length) {
			for (var i = 0; i < this.heatmap.length; ++i) {
				var frac = this.scale(this.heatmap[i][dx]);
				$(this.items[i]).css("background-color", this.colormap(frac));
			}
		}
	}
}
/**
 * Lookup the heatmap index for the given time value
 * @param tval timestamp in milliseconds
 */
Heatmap.prototype.getIndex = function(tval, next) {
	var self = this;
	self.load(function() {
		var pos = binSearch(self.times, tval / 1000);
		if (pos < 0) {
			pos = -pos;
		}
		next(pos);		
	});
}