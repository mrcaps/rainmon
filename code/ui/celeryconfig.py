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
