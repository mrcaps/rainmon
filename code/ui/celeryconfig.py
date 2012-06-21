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

import os, sys

try:
	import pipeline
except:
	sys.path.append(os.path.abspath("."))
	os.chdir("../")

CELERY_IMPORTS = ("rain.tasks", )

CELERY_RESULT_BACKEND = "amqp"

CELERY_QUEUES = {"default": {"exchange": "default",
                             "exchange_type": "direct",
                             "binding_key": "default"}}
CELERY_DEFAULT_QUEUE = "default"
CELERY_DEFAULT_EXCHANGE = "default"
