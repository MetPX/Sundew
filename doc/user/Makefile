.SUFFIXES: .dia .png .pdf .html

PNG_SRCS = $(wildcard *.dia)
PNG_TRGT = $(patsubst %.dia,%.png,$(PNG_SRCS))

TARGETS = $(PNG_TRGT) Guide.html

default: $(TARGETS)

%.png: %.dia
	dia -t png $<

Guide.rtf: Guide.latex
	latex2rtf </dev/null Guide.latex >Guide.rtf

Guide.latex:  Guide.txt
	rst2latex <Guide.txt >Guide.latex
 
Guide.html: Guide.txt
	rst2html --link-stylesheet --stylesheet=css/bootstrap.min.css,css/metpx-sidebar.css $(TEMPLATE) $< $@
	sed -i 's/<a class="toc-backref" .*">\(.*\)<\/a>/\1/' $@
	python ../../../site/template.py $@
	sed -i 's/<img \(.*\)\/>/<div class="panel"><div class="panel-body"><img \1 class="img-responsive"\/><\/div><\/div>/' $@

Guide.pdf: Guide.latex
	pdflatex </dev/null Guide.latex 

clean: 
	rm -f Guide.rtf Guide.latex Guide.pdf texput.log Guide.log Guide.aux $(TARGETS)

all: Guide.pdf Guide.rtf

