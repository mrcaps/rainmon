/**
 * Results manager
 * @author ishafer
 */
function Res(savename) {
	this.objs = {};
	this.savename = savename;
}
Res.prototype.display = function(next) {
	var self = this;
	self.getMeta(function(meta) {
		
	});
}
/**
 * Get summary metadata
 */
Res.prototype.getMeta = function(next) {
	var self = this;
	if (self.meta) {
		next(self.meta);
	} else {
		$.getJSON("getsummary", {savename:self.savename}, function(dta) {
			self.meta = dta;
			next(self.meta);
		});
	}
}
/**
 * Get final projection matrix
 */
Res.prototype.getProjection = function(next) {
	var self = this;
	if (self.projection) {
		next(self.projection);
	} else {
		$.getJSON("getprojection", {savename:self.savename}, 
		function(dta) {
			self.projection = dta;
			next(self.projection);
		});
	}
}
/**
 * Get heatmap
 */
Res.prototype.getHeatmap = function(next) {
	this.get("heatmap",next);
}
Res.prototype.get = function(name,next) {
	var self = this;
	if (name in self.objs) {
		next(self.objs[name]);
	} else {
		$.getJSON("get" + name, {savename:self.savename}, 
		function(dta) {
			self.objs[name] = dta;
			next(dta);
		});
	}
}

/**
 * List available save files
 */
Res.getSaves = function(next) {
	$.getJSON("getsavenames", {savename:self.savename}, 
	function(dta) {
		next(dta);
	});
}

/**
 * Get status of a save
 */
Res.getStatus = function(savename, next) {
	$.getJSON("getstatus", {savename:savename}, 
	function(dta) {
		next(dta);
	});
}