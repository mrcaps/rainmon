EXTDATA=../../externaldata
DATATAR=data.tar.gz

#unpack data to an external directory
stage:
	mkdir -p $(EXTDATA)/data
	cp $(DATATAR) $(EXTDATA)
	tar -xvf  $(EXTDATA)/$(DATATAR) -C $(EXTDATA)/data
