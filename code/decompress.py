#Copyright (c) 2012, Carnegie Mellon University.
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions
#are met:
#1. Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#2. Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#3. Neither the name of the University nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.

import sys
import os
import numpy as np
from optparse import OptionParser

class Decompressor():
	def __init__(self, target):
		self.target = target

	def decompress(self):
		cont = np.load(self.target)

		def hasit(name):
			try:
				return name in cont
			except KeyError:
				return name in cont.files

		#reconstruction
		assert hasit("hvs"), "Decompression error: no hidden variables"
		assert hasit("proj"), "Decompression error: no weight matrix"
		recon = np.dot(cont["hvs"].T, cont["proj"])

		if hasit("center"):
			recon *= cont["center"][0] 
			recon += cont["center"][1]

		recon = recon.T

		if hasit("xforms"):
			assert recon.shape[0] == len(cont["xforms"])
			for rdx in xrange(recon.shape[0]):
				recon[rdx,:] = cont["xforms"][rdx].unapply(recon[rdx,:])

		if hasit("spikes"):
			recon += cont["spikes"]

		return recon

if __name__ == '__main__':
	parser = OptionParser()
	(options, args) = parser.parse_args()

	if len(args) < 1:
		print "No argument specified for filename to decompress"
		sys.exit(1)

	target = sys.argv[1]
	if not os.path.exists(target):
		print "Target file %s does not exist" % (target)
		sys.exit(1)

	decomp = Decompressor(target)
	decomp.decompress()