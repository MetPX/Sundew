"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: TextSplitter.py
#
# Author: Daniel Lemay
#
# Date: 2005-05-24
#
# Description: 
#
# Modification: Michel Grenier (splitting with a report maker like "=\n")
#
#############################################################################################

"""
import sys, os, commands, signal, string

class TextSplitter:
    """
    If you have some protocol that define the way each line of data must terminate
    and also determine the maximum length the encapsulated message can have, you can
    use this class to split the data (text) in blocks that will respect the maximum
    predetermined size. 
    
    For that you have to know:

    text: This is the data (if end of lines are included, they will be replaced by the
    one contained in alignment) you want to split (no splitting will be done if it is
    not necessary).

    maxSize: This is the maximum size of the encapsulated message.

    alignment: This is the "end of line" marker you want.

    overhead: This is the number of fixed character added by the protocol to 
              encapsulate the message.
    """
    def __init__(self, text, maxSize, alignment="\n", overhead=5, marker="=\n" ):
        self.__text = text                       # Original text (a string)
        self.__maxSize = maxSize                 # Maximum size for each string
        self.__alignment = alignment             # Alignment function (ex: '\r\n')
        self.__overhead = overhead               # Number of overhead character in a text block
        self.__marker = marker                   # Marker for different splitting
        self.__alignmentLength = len(alignment)  # Length of the alignment function
        self.__lines = text.splitlines()         # Original text, splitted in lines (alignment removed)
        self.__blocks = []                       # Final blocks of text that respect the maximum size 
        #self.breakLongText()                     

    def setText(self, text):
        self.__text = text
        self.__lines = text.splitlines()

    def getText(self):
        return self.__text

    def setMaxSize(self, maxSize):
        self.__maxSize = maxSize

    def getMaxSize(self):
        return self.__maxSize

    def setAlignment(self, alignment):
        self.__alignment = alignment

    def getAlignment(self):
        return self.__alignment

    def setOverhead(self, value):
        self.__overhead = value

    def getOverhead(self):
        return self.__overhead

    def setAlignmentLength(self, length):
        self.__alignmentLength = length
        
    def getAlignmentLength(self):
        return self.__alignmentLength
    
    def setLines(self):
        self.__lines = self.__text.splitlines()

    def getLines(self):
        return self.__lines

    def getBlocks(self):
        return self.__blocks

    def breakLongLine(self, line):
        """
        Breaks long line in block of text that respect the maximum size for this 
        type of message. An alignment function is added at the end of the
        individual blocks.
        """
        maxLength = self.__maxSize - self.__alignmentLength - self.__overhead
        count = 0
        blocks = []
        newLine = ""

        for char in line:
            if count < maxLength: 
                newLine += char
                count += 1
            else:
                blocks.append(newLine + self.__alignment)
                count = 1
                newLine = char 
        blocks.append(newLine + self.__alignment)

        return blocks

    def breakLongText(self):
        """
        Will break text in group of maxsize. Contrary to breakLongText1, this 
        method will procede correctly in case of line longer than maxSize.
        """

        global block, count
        block = ""
        blocks = []
        count = self.__overhead

        def processLine(line):
            global block, count

            #print "processLine() has been called with: %s" % line

            # The line is too long, we have to split it.
            if len(line) >= self.__maxSize - self.__alignmentLength - self.__overhead:
                # If a block is in use, add it to blocks, before splitting the long line
                if not block == "":
                    blocks.append(block)
                    block = ""
                    count = self.__overhead
                # Add all the blocks that come from splitting the long line
                blocks.extend(self.breakLongLine(line))
            else:
                lineLength = len(line) + self.__alignmentLength
                if (count + lineLength) < self.__maxSize:
                    block += line + self.__alignment
                    count += lineLength
                else: # If we append the line, the block will be too long. We start a new block
                      # and we process the line that we cannot apppend.
                    blocks.append(block)
                    block = ""
                    count = self.__overhead
                    # We process the line with a recursive call
                    processLine(line)

        for line in self.__lines:
            processLine(line)
        
        # If not empty, we append the last unfilled block
        if not block == "":
            blocks.append(block)

        self.__blocks = blocks 
        return blocks

    def breakLongText1(self):
        """
        Will break text in group of maxsize. If a given line is longer than
        maxSize, a problem will result. If this is a situation with which we 
        have to deal, this method will have to be rewritten

        Check breakLongText if you need to treat long line

        FIXME: Deal with empty text
        """

        blocks = []
        index = 0
        blocks.insert(index, "")
        count = self.__overhead
        
        for line in self.__lines:
            lineLength = len(line) + self.__alignmentLength
            #print (count + lineLength)
            if (count + lineLength) < self.__maxSize:
                blocks[index] += line + self.__alignment
                count += lineLength
            else: # The block is full. We start with a new block
                index += 1
                blocks.insert(index, "") 
                count = self.__overhead
                #print (count + lineLength)
                if (count + lineLength) < self.__maxSize:
                    blocks[index] += line + self.__alignment
                    count += lineLength
                else: 
                    print "You should never get here. If you are, it's probably because we need to rewrite this method"
                    print "A given line is longer than the maxSize. We don't want to break line, don't we?"
                    self.__blocks = [] 
                    return blocks 

        self.__blocks = blocks 
        return blocks

    def breakMarker(self):
        """
        Will break text in group of maxsize. The algorithm is carefull to cut
        text on a marker... making sure that information is cut where it should
        FIXME: Current behavior -> when a marker is not found... cut to maximum
               would be better to raise an exception but it should never happen
        """

        blocks = []
        first  = 0
        text   = self.__text
        eot    = len(text)
        marker = self.__marker
        lmark  = len(marker)

        while first < eot :
              last = first + self.__maxSize

              if last < eot :
                 marker_pos = string.rfind(text[first:last],marker)
                 if marker_pos != -1 :
                    last = first + marker_pos + lmark
              else :
                 last = eot

              blocks.append(text[first:last])
              first = last
                 
        self.__blocks = blocks 

        return blocks

if __name__ == "__main__":

    # The case tested here is an extreme case where all lines composing
    # the message are longer than maxSize. This is not representing a realistic
    # case where in practice a line will never be longer than the maxSize.

    maxSize = 25
    alignment = '/r/n'
    overhead = 5

    text = """
    Ceci est un essai afin de voir le fonctionnement
    de ce test splitter. J'espere obtenir des
    resultats concluants. Je commence a etre tanne
    de taper des niaiseries, je vais donc proceder a
    l'essai immediatement.


    DL
    """

    splitter = TextSplitter(text, maxSize, alignment, overhead)
    print splitter.getLines()
    splitter.breakLongText()

    for line in splitter.getBlocks():
        print line, len(line)

#
#
#if __name__ == "__main__":
#
#    # The case tested here is an extreme case where all lines composing
#    # the message are longer than maxSize. This is not representing a realistic
#    # case where in practice a line will never be longer than the maxSize.
#
#    maxSize = 20
#    alignment = '\r\n'
#    overhead = 5 
#
#    text = """
#Ceci est un essai afin de voir le fonctionnement
#de ce test splitter. J'espere obtenir des 
#resultats concluants. Je commence a etre tanne
#de taper des niaiseries, je vais donc proceder a
#l'essai immediatement.
#
#
#DL
#"""
#   
##   file = open('/apps/px/toSendAFTN/canada_warnings.xml:wxo-b1.cmc.ec.gc.ca:WEATHEROFFICE:WXO_WARNING:1:XML:20060106233004', 'r')
##   text = file.read()
#    splitter = TextSplitter(text, maxSize, alignment, overhead)
#    #print splitter.getLines()
#    blocks = splitter.breakLongText()
##   i = 1 
##   for block in blocks:
##       print("*********** Begining of block #%s**********" % i)
##       print block[:20]
##       print("*********** End of block #%s**********" % i)
##       i +=1
#
#    for line in splitter.getBlocks():
#        print line, len(line)
#        
