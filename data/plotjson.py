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

#generate matplotlib plots directly from JSON store that backs the UI

from pylab import *
import json
import os
import sys
import matplotlib
matplotlib.rcParams.update({
    "font.size": 15,
    "lines.linewidth": 1,
    "ps.useafm": True,
    "pdf.use14corefonts": True,
    "text.usetex": True
})

DAY = 60*60*24

class Cache:
    def __init__(self,rootdir):
        self.rootdir = rootdir
        fp = open(os.path.join(rootdir,"index.json"),"r")
        self.index = json.load(fp)
        fp.close()
        fp = open(os.path.join(rootdir,"tsample.json"),"r")
        self.tsample = [num2date(float(t)/DAY) for t in json.load(fp)]
        fp.close()

    def data(self,tsname,tsrange=(0,-1)):
        fp = open(os.path.join(self.rootdir,tsname + ".json"),"r")
        ys = json.load(fp)
        fp.close()
        return (self.tsample[tsrange[0]:tsrange[-1]],
                ys[tsrange[0]:tsrange[-1]])

    def dateify(self,locator):
        ax = gca()
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(DateFormatter("%b %d"))

#Scatterplot of first two columns of W
def plot_cloud_disk():
    ca = Cache("cache-cloud-disk-oct12-oct16")

    fig = figure(figsize=(4.5,2.5))
    fig.subplots_adjust(left=0.2,bottom=0.22,top=0.92,right=0.95)
    (ts,proj) = ca.data("projection")

    hv1 = []
    hv2 = []
    for i in xrange(len(proj)):
        hv1.append(proj[i][0])
        hv2.append(proj[i][1])
    MSIZE = 15

    plot(hv1[::2],hv2[::2],'.',color=(1.0, 0.3, 0.9), markersize=MSIZE, label='Read Requests')
    plot(hv1[1::2],hv2[1::2],'b.',markersize=MSIZE, label='Write Requests')
    matplotlib.rcParams.update({"legend.fontsize":"small"})
    leg = legend(numpoints=1)

    node = 10
    gca().annotate("cloud" + str(node+1), 
        xy=(hv1[node*2],hv2[node*2]), xytext=(-.28,-.20),
        arrowprops=dict(facecolor='black', shrink=0.05))
    gca().annotate("cloud" + str(node+1)[:-1], 
        xy=(hv1[node*2+1],hv2[node*2+1]), xytext=(-.28,-.20),
        arrowprops=dict(facecolor='black', shrink=0.05))

    xticks([-0.3,-0.2,-0.1])

    xlabel("$W_{:, 1}$")
    ylabel("$W_{:,2}$")

    show()

#Show a sample of dimensionality reduction
def plot_dim_reduction():
    ca = Cache("cache-cloud-disk-oct12-oct16")

    fig = figure(figsize=(6.3,3.75))

    nplots = 6
    subplot(nplots,1,1)
    (xs,ys) = ca.data("hv.0")
    xticks([])
    yticks([])
    plot(xs,ys,linewidth=2)
    xlmin, xlmax = xlim()
    sample = ((xlmin+xlmax)*0.5, xlmax)
    xlim(sample)
    common_ylim = 350
    for i in xrange(2,nplots+1):
        subplot(nplots,1,i)
        (xs,ys) = ca.data("cloud%d.iostat.disk.read_requests.smooth" % (i-1))
        plot(xs,ys,linewidth=2)
        xlim(sample)
        ylim(0,common_ylim)
        yticks([])
        if i == nplots:
            ca.dateify(DayLocator(interval=1))
        else:
            xticks([])

    show()


#Scatterplot of disk data for multiple groups of nodes
# unpack cache-machine-groups.tar.gz to plot
def plot_cloud_disk2():
    ca = Cache("cache")

    fig = figure(figsize=(6.3,3.75))
    fig.subplots_adjust(left=0.17,bottom=0.18,top=0.85)
    (ts,proj) = ca.data("projection")
    hv1 = []
    hv2 = []
    for i in xrange(len(proj)):
        hv1.append(proj[i][0])
        hv2.append(proj[i][1])
    MSIZE = 24
    h1, = plot(hv1[::2],hv2[::2],'.',color=(1.0, 0.3, 0.9),markersize=MSIZE)
    h2, = plot(hv1[1::2],hv2[1::2],'b.',markersize=MSIZE)
    leg=legend([h1,h2],["Read Requests","Write Requests"], \
       numpoints=1,bbox_to_anchor=(0., 1.02, 1., .102), loc=3, \
       ncol=2, mode="expand", borderaxespad=0.0)
    #leg.draggable(True)    
    setp(leg.get_texts(), fontsize='small')
    xticks([0,0.1,0.2,0.3,0.4])
    #leg.get_frame().set_alpha(0.9)

    r = Rectangle((0.01,-0.3),0.07,0.45,fill=False,color=(0.5,0.5,0.5),linewidth=3)
    gca().add_patch(r)
    r = Rectangle((0.12,-0.5),0.07,0.43,fill=False,color=(0.5,0.5,0.5),linewidth=3)
    gca().add_patch(r)

    xlabel("$W_{:, 1}$")
    ylabel("$W_{:,2}$")
    ylim((-0.55,0.45))
    
    show()

#Timeseries comparison of disk read data from cloud11 and four other machines
def plot_cloud_disk_nodes():
    ca = Cache("cache-cloud-disk-oct12-oct16")

    fig = figure(figsize=(4.5,2.5))
    fig.subplots_adjust(left=0.18,bottom=0.22,top=0.9,right=0.95)

    #show four other nodes
    onodes = [3,6,9,12]
    ho = []
    for dx in xrange(len(onodes)):
        onode = onodes[dx]
        frac = float(dx)/len(onodes)
        (xs,ys) = ca.data("cloud%d.iostat.disk.read_requests.smooth" % (onode))
        ho.append(plot(xs,ys,'k-',linewidth=1,color=(frac,frac,frac)))

    (xs,ys) = ca.data("cloud11.iostat.disk.read_requests.smooth")
    h1=plot(xs,ys,'r',linewidth=3)
    #(xs,ys) = ca.data("cloud1.iostat.disk.read_requests.smooth")
    #h2=plot(xs,ys,'b',linewidth=3)

    matplotlib.rcParams.update({"legend.fontsize":"small"})
    legend([ho[0],h1],["Other Nodes","cloud11"])

    ca.dateify(DayLocator(interval=1))
    ylabel("Disk Read Requests")
    xlabel("Time")

    show()

def plot_cloud_disk_nodes_overlap():
    ca = Cache("cache-cloud-disk-oct9-oct13")
    fig = figure(figsize=(8,6))
    subplots_adjust(hspace=0.3);
    #fig.subplots_adjust(left=0.15,bottom=0.17)
    subplot(2, 1, 1)

    #show four other nodes
    onodes = [1,2,3,4,5,6,7,8,9,10,12,13,14,15]
    ho = []
    for dx in xrange(len(onodes)):
        onode = onodes[dx]
        frac = float(dx)/len(onodes)
        (xs,ys) = ca.data("cloud%d.iostat.disk.read_requests.smooth" % (onode),
                         (40, -1))
        ho.append(plot(xs,ys,"--",color='0.75',linewidth=1.5))
        (xs,ys) = ca.data("cloud%d.iostat.disk.write_requests.smooth" % (onode),
                         (40, -1))
        ho.append(plot(xs,ys,"--",color='0.75',linewidth=1.5))

    (xs,ys) = ca.data("cloud11.iostat.disk.write_requests.smooth", (50, -1))
    h2=plot(xs,ys,'b',linewidth=2)
    (xs,ys) = ca.data("cloud11.iostat.disk.read_requests.smooth", (50, -1))
    h1=plot(xs,ys,color=(1.0, 0.3, 0.9),linewidth=2)

    #(xl1,xl2) = xlim()
    #xlim((xl1, (xl1+xl2)/2))
    legend([ho[0]],["Other\nMachines"], loc=(.2,.7), prop={'size':15})

    pfromdx = 240
    ptodx = 250
    gca().annotate("Imbalanced\nMachines",color='black',
        xy=(xs[ptodx],ys[ptodx]), xytext=(xs[pfromdx],450),
        arrowprops=dict(facecolor='black', shrink=0.05))

    ca.dateify(DayLocator(interval=1))
    ylabel("(Read/Write) Disk Requests")
    xlabel("Time")


    ca = Cache("cache-cloud-disk-oct9-oct13")

    ax = subplot(2, 1, 2)
    (ts,proj) = ca.data("projection")

    hv1 = []
    hv2 = []
    for i in xrange(len(proj)):
        hv1.append(proj[i][0])
        hv2.append(proj[i][1])
    MSIZE = 14

    plot(hv1[::2][:-2],hv2[::2][:-2],'.',color=(1.0, 0.3, 0.9),markersize=MSIZE, label='Read Requests')
    plot(hv1[1::2][:-2],hv2[1::2][:-2],'b.', markersize=MSIZE, label='Write Requests')
    plot(1, 1, 'g-', label='Imbalanced Machines', lw=1.5)
    plot(1, 1, '--', label='Other Machines', lw=1.5, color='0.75')
    xlim((-0.23, 0))
    ylim((-0.35, 0.28))
    circ = matplotlib.patches.Ellipse((-0.138, 0.03), 0.03, 0.2, ls='solid', color="w", ec="g", lw=1.5)
    ax.add_patch(circ)
    circ = matplotlib.patches.Ellipse((-0.098, -0.23), 0.03, 0.2, ls='solid', color="w", ec="g", lw=1.5)
    ax.add_patch(circ)
    circ = matplotlib.patches.Ellipse((-0.21, 0.16), 0.03, 0.2, ls='dashed', color="0.9", ec="0.75", lw=1.5)
    ax.add_patch(circ)
    circ = matplotlib.patches.Ellipse((-0.17, -0.21), 0.03, 0.2, ls='dashed', color="0.9", ec="0.75", lw=1.5)
    ax.add_patch(circ)

    leg = legend(numpoints=1, prop={'size':15})
    xlabel("$W_{ :,1}$")
    ylabel("$W_{:,2}$")

    savefig("intro-example.pdf")
    show()

def plot_spike_data():
    ca = Cache("cache-mahout")

    fig = figure()
    # fig.subplots_adjust(left=0.12,right=0.88)
    subplots_adjust(hspace=0.5);
    matplotlib.rcParams.update({'font.size': 12})

    nodes = [17,19,30,49,52,9,28,62]

    subplot(3,1,1);

    for dx in xrange(len(nodes)):
        node = nodes[dx]
        (xs,ys) = ca.data("cloud%d.proc.stat.cpu,type.user.original" % (node))
        if node == 9:
        	plot(xs, ys, 'k--', linewidth=2, color='blue', label='cloud9');
        elif node == 28:
        	plot(xs, ys, 'k--', linewidth=2, color='red', label='cloud28');
        elif node == 62:
        	plot(xs, ys, color='0.4', linewidth=2, label='other nodes');
        else:
        	plot(xs, ys, color='0.4', linewidth=2);

    title("Original Data");
    xlabel("Time")
    ylabel("CPU Usage (User)")
    legend();

    subplot(3,1,2);

    for dx in xrange(len(nodes)):
        node = nodes[dx]
        (xs,ys) = ca.data("cloud%d.proc.stat.cpu,type.user.spikes" % (node))
        if node == 9:
        	plot(xs, ys, 'k--', linewidth=2, color='blue', label='cloud9');
        elif node == 28:
        	plot(xs, ys, 'k--', linewidth=2, color='red', label='cloud28');
        elif node == 62:
        	plot(xs, ys, color='0.4', linewidth=2, label='other nodes');
        else:
        	plot(xs, ys, color='0.4', linewidth=2);

    title("Extracted Spikes");
    xlabel("Time")
    ylabel("CPU Usage (User)")
    legend();

    subplot(3,1,3);
        
    (xs, ys) = ca.data("hv.0");
    plot(xs, ys, color='blue', linewidth=2, label='hv0');
    (xs, ys) = ca.data("hv.1")
    plot(xs, ys, color='red', linewidth=2, label='hv1');

    title("Hidden Variables");
    xlabel("Time")
    ylabel("Value")

    legend();

    savefig('mahout-summary.pdf')
    # show()

#Change in behavior (Qatar) and spike (PSU) found from first hidden variable
def plot_psu_qatar():
    ca = Cache("cache-psu-spike")

    #matplotlib axes: 
    #    https://github.com/matplotlib/matplotlib/blob/master/lib/matplotlib/axes.py
    fig = figure(figsize=(6.16,4))
    fig.subplots_adjust(left=0.15,right=0.88)
    subplot(2,1,1)
    (xs,ys) = ca.data("hv.0")
    plot_date(xs,ys,"b",linewidth=2)
    ca.dateify(DayLocator(interval=5))
    legend(["Hidden Variable 1"],loc=(0.5,0.1))
    (xmin,xmax) = xlim()
    ylabel("Value")

    subplot(2,1,2)
    (xs,ys) = ca.data("PSU.median.smooth")
    h1, = plot_date(xs,ys,"g",linewidth=2)
    ylabel("PSU Ping (s)")
    yticks([0.12,0.16,0.20,0.24])
    ca.dateify(DayLocator(interval=5))

    a1 = gca()
    a2 = axes(a1.get_position(),frameon=False)
    a2.yaxis.tick_right()
    a2.yaxis.set_label_position('right')
    a2.set_xticks([])
    (xs,ys) = ca.data("Qatar.median.smooth")
    h2, = plot_date(xs,ys,"r",linewidth=2)
    ylim((0.21,0.25))
    yticks([0.21,0.22,0.23,0.24,0.25])
    legend([h1,h2],["PSU","Qatar"],loc="upper left")
    ylabel("Qatar Ping (s)")
    xlabel("Time")

    show()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Please specify a plot to create; see README.md for options"
        sys.exit(1)

    pname = sys.argv[1]
    if pname == "fig1":
        plot_cloud_disk_nodes_overlap()
    elif pname == "fig8":
        plot_cloud_disk()
    elif pname == "fig9":
        plot_cloud_disk_nodes()
    elif pname == "fig10":
        plot_spike_data()
    elif pname == "fig11":
        plot_cloud_disk2()
    elif pname == "fig13":
        plot_psu_qatar()
    elif pname == "dim-red-example":
        plot_dim_reduction()