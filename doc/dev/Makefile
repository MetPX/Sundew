
.SUFFIXES: .dia .png .pdf .txt .html

default: 

 
.txt.html:
	rst2html $*.txt >$*.html

.dia.png:
	dia -t png $*.dia

clean: 
	rm -f *.html



all: Guide.pdf Guide.rtf

