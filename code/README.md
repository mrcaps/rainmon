## Overview

This code package contains the source for RainMon. In brief, it is a system for decomposing, summarizing, and predicting timeseries systems timeseries monitoring data. For more detail on the technique, please see the KDD 2012 paper. The description below is a quick guide to some of the key parts of the code.

## Installation

For a guide on how to install these requirements, please see the [Setup Guide](setup.html) 

Base requirements (all Python-based):

 * Python (tested on 2.7)
  * http://www.python.org/getit/releases/2.7.2/
 * scipy/numpy
  * see http://www.scipy.org/Installing_SciPy
  * If you don't already have these, consider using the Enthought Python distribution: http://www.enthought.com/products/epd.php
 * matplotlib (for producing figures)
  * see http://matplotlib.sourceforge.net/users/installing.html

Required for interface:

 * Django 
  * The database portion is not required (using SQLite is fine)
  * https://docs.djangoproject.com/en/dev/topics/install/?from=olddocs
 * RabbitMQ (though other AMQP brokers compatible with Celery should work)
  * http://www.rabbitmq.com/download.html
  * Note: requires Erlang (the installation will prompt for it)
  * Leave the server running as a daemon
 * Celery and django-celery for distributed task scheduling:
  * `easy_install celery`
  * `easy_install django-celery`

## Configuration

### config.json

First, copy `config.template.json` to `config.json` file in this directory, and edit the following keys:

 * "rrddir": "...path to directory with .rrd files"
 * "tsdbhost": "... host/IP that default timeseries database is located on ..."
 * "tsdbport": "... port of default timeseries database (4242 for OpenTSDB, 8000 for RRD)"

RainMon currently supports two timeseries databases: OpenTSDB, a scalable distributed database, and an RRD server.

### OpenTSDB

For detail on how to set up OpenTSDB, please see the OpenTSDB "getting started" guide at http://opentsdb.net/getting-started.html. The Haodop dataset is available only from within the CMU campus network (or on VPN).

### RRDtool

The `rrd` folder contains a server for RRDtool-format data.

## Running

First, `cd` to the `code` folder. 

### From the command line

A simple example of how to only run the analysis pipeline without the UI is located in `boot.py`. Look inside `generate()`: it shows what needs to be specified (name to save, nodes, attributes, and time range).

### Running the UI

To run the UI:

 * `make celerystart`
  * starts up a task node on the current machine. For the single-node configuration, just run this on the same node as the Django server.
 * `make serverstart`
  * starts the Django server

Then, navigate with a web browser to `http://localhost:8000/`, where `localhost` is the IP of the machine you ran the make commands from.

## Disclaimer

This is "research" code - we fully expect that there are bugs.

For licensing information that applies to the project, see LICENSE.