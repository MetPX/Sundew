
.SUFFIXES: .dia .png .pdf .txt .html

default: DevGuide.html
 
.txt.html:
	rst2html --link-stylesheet --stylesheet=css/bootstrap.min.css,css/metpx-sidebar.css $(TEMPLATE) $*.txt $*.html
	sed -i 's/<a class="toc-backref" .*">\(.*\)<\/a>/\1/' $@
	python ../../../template.py $@
	sed -i 's/<img \(.*\)\/>/<div class="panel"><div class="panel-body"><img \1 class="img-responsive"\/><\/div><\/div>/' $@

.dia.png:
	dia -t png $*.dia

clean: 
	rm -f *.html

all: Guide.pdf Guide.rtf

