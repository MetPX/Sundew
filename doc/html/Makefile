.SUFFIXES: .1 .5 .7 .dia .png .pdf .html


#Guide.rtf:   Guide.latex
#	latex2rtf </dev/null Guide.latex >Guide.rtf

MANPAGES= pxTransceiver.1.html pxSender.1.html pxReceiver.1.html pxFilter.1.html px.1.html pxRetransmit.1.html pxRouting.conf.5.html pxRouting.7.html
TARGETS= Guide.html DevGuide.html $(MANPAGES)

default: $(TARGETS) 

.dia.png:
	dia -t png $*.dia

Guide.html:  ../user/Guide.txt
	cd ../user; make Guide.html; cp *.png Guide.html ../html

DevGuide.html:  ../dev/DevGuide.txt
	cd ../dev; make DevGuide.html; cp DevGuide.html ../html

# there should be a way to make an implicit rule for the man pages,
# some sort of thing that would scan all of man tree, and do the right
# thing...
# but copy paste was faster...
# when you add a man page, need to:
#         -- add an explicit target here.
#         -- add a link from index.html.
#
pxSender.1.html: ../../../sundew/man/man1/pxSender.1
	groff -Thtml -man ../../../sundew/man/man1/pxSender.1 >pxSender.1.html

pxTransceiver.1.html: ../../../sundew/man/man1/pxTransceiver.1
	groff -Thtml -man ../../../sundew/man/man1/pxTransceiver.1 >pxTransceiver.1.html

pxReceiver.1.html: ../../../sundew/man/man1/pxReceiver.1
	groff -Thtml -man ../../../sundew/man/man1/pxReceiver.1 >pxReceiver.1.html

pxRetransmit.1.html: ../../../sundew/man/man1/pxRetransmit.1
	groff -Thtml -man ../../../sundew/man/man1/pxRetransmit.1 >pxRetransmit.1.html

px.1.html: ../../../sundew/man/man1/px.1
	groff -Thtml -man ../../../sundew/man/man1/px.1 >px.1.html

pxFilter.1.html: ../../../sundew/man/man1/pxFilter.1
	groff -Thtml -man ../../../sundew/man/man1/pxFilter.1 >pxFilter.1.html

pxRouting.conf.5.html: ../../../sundew/man/man5/pxRouting.conf.5
	groff -Thtml -man ../../../sundew/man/man5/pxRouting.conf.5 >pxRouting.conf.5.html

pxRouting.7.html: ../../../sundew/man/man7/pxRouting.7
	groff -Thtml -man ../../../sundew/man/man7/pxRouting.7 >pxRouting.7.html

Guide.pdf:   Guide.latex
	pdflatex </dev/null Guide.latex 

clean: 
	rm -f $(TARGETS) *.png 



