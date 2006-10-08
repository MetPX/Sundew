
.SUFFIXES: .dia .png .pdf .html

default: Guide.html

Guide.rtf:   Guide.latex
	latex2rtf </dev/null Guide.latex >Guide.rtf

Guide.latex:  Guide.txt
	rst2latex <- Guide.txt >Guide.latex
 
.dia.png:
	dia -t png $*.dia

Guide.html: Guide.txt BigPicture.png
	rst2html Guide.txt Guide.html

Guide.pdf:   Guide.latex
	pdflatex </dev/null Guide.latex 

clean: 
	rm -f Guide.rtf Guide.latex Guide.pdf texput.log Guide.log  Guide.aux Guide.html BigPicture.png



all: Guide.pdf Guide.rtf

