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