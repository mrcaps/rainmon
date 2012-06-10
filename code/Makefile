#start celeryd
celerystart:
	python boot.py celeryd start --settings=settings

#run pipeline without webserver
piperun:
	python boot.py generate | tee ../etc/tmp/runoutput.txt

#celery won't die on Windows unless we apply some force
celerykill:
	tasklist /fi "IMAGENAME eq python.exe" /fo csv /nh | tail -n 3 | head -n 1 | cut -d, -f 2 | xargs taskkill /f /pid
#	taskkill /f /im python.exe

#start django
serverstart:
	python boot.py runserver

#start public server
serverstartpublic:
	python boot.py runserver 0.0.0.0:8000

#clear all analysis results
clearcache:
	rm -r ../etc/tmp/cache/*

#count raw lines of code (SLOC) in project
countsloc:
	rm -f lines.txt
	@echo "Python:"
	@wc -l `find . -path "./lib" -prune -o -print | grep '\.py'` | tail -n 1 | tee -a lines.txt
	@echo "Javascript:"
	@wc -l `find ui/templates -name '*.html'` | tail -n 1 | tee -a lines.txt
	@wc -l `find ui/media/js -name '*.js'` | tail -n 1 | tee -a lines.txt
	@echo "Total SLOC:"
	@cat lines.txt | awk '{ sum += $$1} END { print sum }'
	@rm lines.txt
