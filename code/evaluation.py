#!/usr/bin/python
#Experiments and plots for evaluation
#@author ishafer

from pipeline import *
from pylab import *

import os

import matplotlib
matplotlib.rcParams.update({
    "font.size": 20,
    "lines.linewidth": 1,
    "ps.useafm": True,
    "pdf.use14corefonts": True,
    "text.usetex": True})

def testnormalization():
    cfg = getconfig()
    crawler = OpenTSDBCrawlStage('kmonitor.cloud.pdl.cmu.local','4242')
    resample = ResampleStage()
    pipeline = Pipeline()
    pipeline.append_stage(crawler)
    pipeline.append_stage(resample)

    input = {}
    input['hosts'] = ['cloud1']
    mlist = getmetrics()
    input['metrics'] = mlist
    input['start'] = '2011/11/22-15:00:00'
    input['end'] = '2011/11/24-23:45:00'
    output = pipeline.run(input)

    tsnames = output["ts_names"]
    nstage = NormalizeStage(True)
    for i in xrange(len(tsnames)):
        dtai = output["data"][i]
        absg1 = ""
        xformed = nstage.get_transform(tsnames[i]).apply(dtai)
        print "%2d %35s min=%.4f max=%.4f %4s" % \
            (i, tsnames[i], min(dtai), max(dtai), absg1)
        print "      min=%.4f max=%.4f" % (min(xformed), max(xformed))

def get_spirit_eval_pipe():
    cfg = getconfig()
    tmpdir = cfg["tmpdir"][3:]
    crawler = CachingCrawlStage(os.path.join(tmpdir,"tsdb"),TSDBHOST,TSDBPORT)
    trimmer = TrimStage()
    resample = ResampleStage(300)
    cypress = CypressStage()
    spirit = SpiritStage(ispca=False,startm=5,thresh=0.03,ebounds=(0,1.1))
    kalman = KalmanStage()
    normalize = NormalizeStage(True)
    denormalize = NormalizeStage(False)
    draw = DrawStage(tmpdir, False)
    errorcalc = ErrorStage()
    pipeline = Pipeline()
    pipeline.append_stage(crawler)
    pipeline.append_stage(trimmer)
    pipeline.append_stage(resample)
    pipeline.append_stage(cypress)
    pipeline.append_stage(normalize)
    pipeline.append_stage(spirit)
    #pipeline.append_stage(kalman)
    pipeline.append_stage(denormalize)
    pipeline.append_stage(errorcalc)
    #pipeline.append_stage(draw)

    return (pipeline, cfg, trimmer, cypress, spirit)

def evalvaryk():
    (pipeline, cfg, trimmer, cypress, spirit) = get_spirit_eval_pipe()

    input = {}
    input['hosts'] = ['cloud%d' % (i) for i in xrange(1,65)]
    #this host has issues...
    del input['hosts'][29]
    #print input['hosts']

    mlist = ['iostat.disk.read_requests','iostat.disk.write_requests']
    input['metrics'] = mlist
    input['start'] = '2011/11/22-15:00:00'
    input['end'] = '2011/11/24-23:45:00'

    nhostvals = [2,4,8,16,32,63]
    startms = range(1,11)
    res = np.zeros((len(nhostvals),len(startms))) - 1

    #Compute an attempt to model nh hosts with nm hidden vars
    i = 0
    for nh in nhostvals:
        j = 0
        for nm in startms:
            if nm <= nh * len(mlist):
                print "hosts=", nh, "k=", nm
                trimmer.sethosts(nh)
                spirit.startm = nm
                output = pipeline.run(input)
                geoerr = output["error"][0]
                res[i][j] = geoerr
                j += 1
        i += 1

    resultsdir = cfg["resultsdir"][3:]
    np.savez(os.path.join(resultsdir, "evalvaryk.npz"),\
        res=res,\
        nhostvals=nhostvals,\
        startms=startms)


def plotvaryk():
    cfg = getconfig()
    resultsdir = cfg["resultsdir"][3:]
    data = np.load(os.path.join(resultsdir, "evalvaryk.npz"))
    nhostvals = data["nhostvals"]
    startms = data["startms"]
    res = data["res"]

    #entries where k > numstreams
    res[res<0] = 1

    fig = pylab.figure()
    fig.subplots_adjust(bottom=0.15)

    plots = []
    for i in xrange(1,len(res)):
        col = float(i)/len(res)
        p = plot(startms, res[i,:],'b.-',markersize=18,linewidth=3,color=(col,0,0,1))
        plots.append(p)

    legend(plots, ["%d Streams" % (x*2) for x in nhostvals[1:]], \
        loc='lower right')
    xlabel('Number of Hidden Variables')
    ylabel('Error E')

    ylim(ymin=0.90)

    show()

    #print nhostvals, startms
    #print res

def evalcompression():
    (pipeline, cfg, trimmer, cypress, spirit) = get_spirit_eval_pipe()
    spirit.ispca = True

    input = {}
    input['hosts'] = ['cloud%d' % (i) for i in xrange(1,65)]
    #this host has issues...
    del input['hosts'][29]

    mlist = ['iostat.disk.read_requests','iostat.disk.write_requests']
    input['metrics'] = mlist
    #small time range sample
    input['start'] = '2011/11/22-15:00:00'
    input['end'] = '2011/11/24-23:45:00'

    #large time range sample
    #input['start'] = '2012/01/05-12:00:00'
    #input['end'] = '2012/02/09-12:00:00'

    trimmer.sethosts(60)
    hvnums = [8,12,16,24,32,64]

    i = 0
    hvsizes = []
    lpsizes = []
    origsizes = []
    spikesizes = []
    errors = []
    skipcypress = []
    for skipcyp in [False,True]:
        for hvnum in hvnums:
            spirit.startm = hvnum
            spirit.pcafixk = hvnum
            cypress.skipstage = skipcyp

            output = pipeline.run(input)

            resultsdir = cfg["resultsdir"][3:]

            maxhvs = output["maxhvs"]
            print "max hvs:", maxhvs
            hvchunk = output["hvlog"][:maxhvs,:]
            print "hvchunk shape:", hvchunk.shape
            #save npz output

            print "Error was ", output["error"][0]
            errors.append(output["error"][0])

            def saveandsize(name, **keywords):
                pth = os.path.join(resultsdir, name)
                np.savez_compressed(pth,**keywords)
                s = os.stat(pth)
                print "Size of %s was %d" % (name, s.st_size)
                return s.st_size

            hvsize = saveandsize("hv.npz", hvs=hvchunk, proj=output["projection"])
            hvsizes.append(hvsize)

            results = output["data"]
            recon = output["reconlog"]
            lowpass = zeros(recon.shape)
            original = zeros(recon.shape)
            spiky = zeros(recon.shape)
            #original = zeros(recon.shape)
            for m in xrange(recon.shape[1]):
                #low pass
                lowpass[:,m] = results[m][0]
                #spiky
                spiky[:,m] = results[m][1]
                #original
                original[:,m] = results[m][3]

            #save original output
            lowpasssize = saveandsize("lowpass.npz", dta=lowpass)
            lpsizes.append(lowpasssize)
            originalsize = saveandsize("original.npz", dta=original)
            origsizes.append(originalsize)
            spikessize = saveandsize("spiky.npz", dta=spiky)
            spikesizes.append(spikessize)
            skipcypress.append(skipcyp)

        np.savez(os.path.join(resultsdir, "evalcompression.npz"),\
            hvnums=hvnums,\
            hvsizes=hvsizes,\
            lpsizes=lpsizes,\
            origsizes=origsizes,\
            spikesizes=spikesizes,\
            skipcypress=skipcypress,\
            errors=errors)

#Turn handles into legend-able handles for compatibility with pre-matplotlib 1.1
def compat_legendify_hs(hs):
    for dx in xrange(len(hs)):
        try:
            len(hs[dx])
            hs[dx] = hs[dx][0]
        except:
            pass
    return hs 

def plotcompression():
    cfg = getconfig()
    resultsdir = cfg["resultsdir"][3:]
    data = np.load(os.path.join(resultsdir, "evalcompression.npz"))
    hvnums = data["hvnums"]
    hvsizes = data["hvsizes"]/1000
    lpsizes = data["lpsizes"]
    origsizes = data["origsizes"]/1000
    spikesizes = data["spikesizes"]/1000
    skipcypress = data["skipcypress"]
    errors = data["errors"]

    N = len(hvnums)

    ind = np.arange(N)
    bw = 0.4

    def mkfig():
        fig = pylab.figure(figsize=(8,3.5))
        fig.subplots_adjust(bottom=0.18,left=0.18)
        return fig

    fig = mkfig()
    phv = bar(ind-bw, hvsizes[:N], bw, color=(1.0, 0.5, 0.5))
    phv2 = bar(ind, hvsizes[N:], bw, color='b')
    pspike = bar(ind-bw, spikesizes[:N], bw, color='k', bottom=hvsizes[:N])
    ls = np.copy(ind)
    ls[0] = -1
    ls[len(ls)-1] = max(ls)+1
    porig = plot(ls, origsizes[:N], 'g-', linewidth=8)
    xlim(xmin=-0.5,xmax=N-0.5)
    (ymin, ymax) = ylim()
    ylim(ymax=ymax+10)

    xticks(ind, hvnums)
    xlabel('Number of Hidden Variables')
    ylabel('Size (kilobytes)')

    leg = legend(compat_legendify_hs([phv, phv2, pspike, porig[0]]), \
        ["HVs + W (With Decomposition)","HVs + W (No Decomposition)","Spike","Original (gzip)"],
        frameon=False,loc=(0,0.15))
    ltext  = leg.get_texts()
    setp(ltext, fontsize=17.0)
    #    bbox_to_anchor=(0., 1.02, 1., .102), loc=3, \
    #    ncol=1, mode="expand", borderaxespad=0.0)

    fig = mkfig()
    err1 = bar(ind-bw, errors[:N], bw, color=(1.0, 0.5, 0.5))
    err2 = bar(ind, errors[N:], bw, color='b')
    fig.subplots_adjust(right=0.7)

    ylim((0.6,1))
    xticks(ind,hvnums)
    xlabel('Number of Hidden Variables')
    leg = legend(compat_legendify_hs([err1, err2]), \
        ["With\nDecomp.","No\nDecomp."], \
        bbox_to_anchor=(1.02, 0.3, 0.5, 0.5), loc=3, \
        ncol=1, mode="expand", borderaxespad=0.0)
    ltext  = leg.get_texts()
    setp(ltext, fontsize=15.0) 
    yticks([0.60,0.7,0.8,0.9,1])
    ylabel("Reconstruction\nAccuracy",multialignment="center")

    show()

    #print nhostvals, startms
    #print res

def plotcompression_multi():
    cfg = getconfig()
    rootdir = os.path.join(cfg["resultsdir"][3:],"compression")
    hvnums = []
    hvsizes = []
    lpsizes = []
    origsizes = []
    spikesizes = []
    skipcypress = []
    errors = []
    for f in os.listdir(rootdir):
        data = np.load(os.path.join(rootdir, f))
        hvnums.append(data["hvnums"])
        hvsizes.append(data["hvsizes"]/1000)
        lpsizes.append(data["lpsizes"])
        origsizes.append(data["origsizes"]/1000)
        spikesizes.append(data["spikesizes"]/1000)
        skipcypress.append(data["skipcypress"])
        errors.append(data["errors"])
    print "nfiles:", len(os.listdir(rootdir))

    #assume all hvnum lengths are equal
    N = len(hvnums[0])
    ind = np.arange(N)
    bw = 0.4

    def mkfig():
        fig = pylab.figure(figsize=(8,3.5))
        fig.subplots_adjust(bottom=0.18,left=0.18)
        return fig

    fig = mkfig()

    totalsizes = np.array(hvsizes) + np.array(spikesizes)

    phv = bar(ind-bw, np.mean(hvsizes,0)[:N], bw, color=(1.0, 0.5, 0.5))
    phv2 = bar(ind, np.mean(hvsizes,0)[N:], bw, color='b', \
        yerr=np.std(totalsizes[:,N:],0))
    pspike = bar(ind-bw, np.mean(spikesizes,0)[:N], bw, \
        color='k', bottom=np.mean(hvsizes,0)[:N], \
        yerr=np.std(totalsizes[:,:N],0))

    print "Totalsize", np.mean(totalsizes[:,:N],0)
    print "Totalvar", np.std(totalsizes[:,:N],0)

    print "Spikesize", np.mean(spikesizes,0)[:N]
    ls = np.copy(ind)
    ls[0] = -1
    ls[len(ls)-1] = max(ls)+1

    originalsize = np.mean(origsizes,0)[:N]
    porig = plot(ls, originalsize, 'g-', linewidth=8)
    print "Originalsize", originalsize
    print "Originalvar", np.var(origsizes,0)[:N]

    xlim(xmin=-0.5,xmax=N-0.5)
    (ymin, ymax) = ylim()
    ylim(ymax=ymax+10)

    xticks(ind, hvnums[0])
    xlabel('Number of Hidden Variables')
    ylabel('Size (kilobytes)')

    leg = legend(compat_legendify_hs([phv, phv2, pspike, porig[0]]), \
        ["HVs + W (With Decomposition)","HVs + W (No Decomposition)","Spike","Original (gzip)"],
        frameon=False,loc=(0,0.2))
    ltext  = leg.get_texts()
    setp(ltext, fontsize=17.0)

    errors = np.array(errors)
    
    fig = mkfig()
    err1 = bar(ind-bw, np.mean(errors,0)[:N], bw, color=(1.0, 0.5, 0.5),
        yerr=np.std(errors,0)[:N],ecolor='k')
    err2 = bar(ind, np.mean(errors,0)[N:], bw, color='b',
        yerr=np.std(errors,0)[N:],ecolor='k')
    fig.subplots_adjust(right=0.7)

    print "Errormean1", np.mean(errors,0)[:N]
    print "Errorvar1", np.std(errors,0)[N:]

    print "Errormean2", np.mean(errors,0)[N:]
    print "Errorvar2", np.std(errors,0)[N:]

    ylim((0.6,1))
    xticks(ind,hvnums[0])
    xlabel('Number of Hidden Variables')
    leg = legend(compat_legendify_hs([err1, err2]), \
        ["With\nDecomp.","No\nDecomp."], \
        bbox_to_anchor=(1.02, 0.3, 0.5, 0.5), loc=3, \
        ncol=1, mode="expand", borderaxespad=0.0)
    ltext  = leg.get_texts()
    setp(ltext, fontsize=15.0) 
    yticks([0.6,0.7,0.8,0.9,1])
    ylabel("Reconstruction\nAccuracy",multialignment="center")

    show()

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "testnormalization":
        testnormalization()
    elif cmd == "varyk":
        #evalvaryk()
        plotvaryk()
    elif cmd == "compression":
        evalcompression()
        plotcompression()
    elif cmd == "compressionmulti":
        plotcompression_multi()
