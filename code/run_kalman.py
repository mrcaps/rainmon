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

# run_kalman.py

import pipeline
import numpy
import pylab
import os

if __name__ == "__main__":
    pipe = pipeline.get_default_pipeline()

    outdir = '../etc/tmp'

    input = {} 
    input['hosts'] = []
    for i in range(1, 65):
        input['hosts'].append('cloud%d'%(i))

    input['start'] = '2011/11/22-15:00:00'
    input['end'] = '2011/11/24-23:45:00'

    metrics = ['iostat.disk.read_requests',
               'iostat.disk.write_requests',
                ]

    input['metrics'] = metrics
    output = pipe.run(input)

    if "predict" in output:
        hvs_predict = output["predict"]
        hvs = output["hvlog"]
        max_ind = numpy.max(output["mlog"])
        mse = numpy.mean((hvs[0:max_ind,:]-hvs_predict)**2,0)
        pylab.clf()
        pylab.title("Kalman Filter Mean Squared Prediction Error ")
        pylab.subplot(111)
        pylab.plot(mse,'r')
        pylab.xlim(0,mse.size)
        pylab.savefig(os.path.join(outdir, "kalman_mse.png"))
        pylab.clf()
        pylab.title("# of Prediction Samples")
        pylab.subplot(111)
        pylab.plot(output["ind"],'r')
        pylab.xlim(0,output["ind"].size)
        pylab.savefig(os.path.join(outdir, "kalman_predict_samples.png"))
        print numpy.mean(output["ind"]), numpy.std(output["ind"])

        for i in xrange(len(hvs_predict)):
            hv = hvs[i]
            hv_predict = hvs_predict[i]
            pylab.clf()
            pylab.title("Predicted hidden variable " + str(i))
            pylab.subplot(111)
            p1 = pylab.plot(hv,'r-')
            p2 = pylab.plot(hv_predict,'b--')
            pylab.xlim(0,hv.size)
            pylab.legend(('Spirit Coefficients','Predicted Coefficients'))
            pylab.savefig(os.path.join(outdir, "kalman_predict_hv_%d.png" % i))