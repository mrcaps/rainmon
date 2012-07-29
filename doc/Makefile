MDTOHTML = pandoc --from markdown --to html5 --template=src/pandoc-template.html 

OTHERSRC = ../code/README.html
all: $(patsubst %.md,%.html,$(wildcard *.md)) $(OTHERSRC)
	mv $(OTHERSRC) .

clean:
	rm *.html

%.html: %.md
	$(MDTOHTML) $< --css src/styles.css --output $@