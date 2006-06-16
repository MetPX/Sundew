#!/usr/bin/env python2
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: Plotter.py
#
# Author: Nicholas Lemay, but the code is highly inspired by previously created file named 
#         Plotter.py made written by Daniel Lemay
#
# Date: 2006-06-06
#
# Description: 
# 
#############################################################################################
"""


#important files 
import sys 
import MyDateLib
from MyDateLib import *
import DirectoryStatsCollector
from Numeric import *
import Gnuplot, Gnuplot.funcutils


class StatsPlotter:

    def __init__( self, timespan, stats = None, clientNames = None, type='impulses', interval=1, imageName="gnuplotOutput", title = "Stats",currentTime = "" ):
        """
            StatsPlotter constructor. 
            
        """
        
        self.stats       = stats or []             # DirectoryStatsCollector instance.
        self.clientNames = clientNames or []       # 
        self.timespan    = timespan                # Helpfull to build titles 
        self.currentTime = currentTime             # Time of call
        self.type        = type                    # Must be in: ['linespoint', 'lines', 'boxes', 'impulses'].
        self.imageName   = imageName               # Name of the image file.
        self.xtics       = self.getXTics( )        # Seperarators on the x axis.
        self.graph       = Gnuplot.Gnuplot()       # The gnuplot graphic object itself. 
        self.minimum     = 0.0                     # Minimum value of all pairs.
        self.max         = 0.0                     # Maximum value of all pairs.
        self.mean        = 0.0                     # Mean of all the pairs.
        self.maxFile     = ""                      # Name of file where value is the highest .    
        self.timeOfMax   = ""                      # Time where the maximum value occured.  
        self.machines    = ""                      # List of machine where we collected info.
        self.clientName  =""                       # Name of the client we are dealing with 
        
            
    def getXTics(self):
        """
            Bug : timeseperators are modified between creation and their arrival here.cant quite
            figure out why.....
            
        """
        
        nbBuckets = ( len( self.stats[0].statsCollection.timeSeperators ) )
        xtics = ''
       
        if nbBuckets != 0 :
            #print MyDateLib.getOriginalHour( self.stats[0].statsCollection.startTime )
            startTime = MyDateLib.getOriginalHour( self.stats[0].statsCollection.startTime )
            xtics += '"%s" %i, ' % ( startTime, self.stats[0].statsCollection.startTime  )
            
            for i in range( 1, nbBuckets ):
                #print MyDateLib.getOriginalDate(self.stats.statsCollection.timeSeperators[i] )
                
                if ( (  self.stats[0].statsCollection.timeSeperators[0] - self.stats[0].statsCollection.startTime) %(60*60) == 0): 
                      
                    originalDate = MyDateLib.getOriginalHour(self.stats[0].statsCollection.timeSeperators[i] )
                    xtics += '"%s" %i, '%( originalDate ,self.stats[0].statsCollection.timeSeperators[i] ) 
                        
                    
        return xtics[:-2]
    

    
    def getPairs( self, i ):
        """
            Faire boucle qui construit les pairs a partir des seperator et du data qu'on a deja  
        """
        
        total = 0
        
        pairs = []
        nbEntries = len( self.stats[i].statsCollection.timeSeperators ) 
    
        if nbEntries !=0:
            
            if len( self.stats[i].statsCollection.fileEntries[0].means ) >=1 :
                pairs.append( [self.stats[i].statsCollection.startTime, self.stats[i].statsCollection.fileEntries[0].means[0]] )
            else:
                pairs.append( [self.stats[i].statsCollection.startTime, 0.0] )
                
            self.minimum = pairs[0][1]
            self.max = pairs[0][1]
            self.total = pairs[0][1]
            print  "min:%s" %pairs[0][1]        
        
        for j in range( 1, nbEntries ):
            
            self.stats[i].statsCollection.fileEntries[j].means
            if len( self.stats[i].statsCollection.fileEntries[j].means ) >=1 :
                pairs.append( [self.stats[i].statsCollection.timeSeperators[j], self.stats[i].statsCollection.fileEntries[j].means[0]] )
            else:
                
                pairs.append( [self.stats[i].statsCollection.timeSeperators[j], 0.0] )
                
            #print " %s-paire :%s "  %(i, pairs[i]    )
            if pairs[j][1] > self.max :
                
                self.max = pairs[j][1]
            
            elif pairs[j][1] < self.minimum:         
                print "min:%s" %pairs[j][1]
                self.minimum = pairs[j][1]
                
            total = total + pairs[j][1]
                        
        
        self.mean = float( total / j )        
        
        return pairs    
         
    
    
    def buildTitle( self,i ):
        """
            This method is used to build the title we'll print on the graphic.
            Title is built with the current time adn the name of the client where
            we collected the data. 
            
        """
        
        title = "Latencies for " + str( self.clientNames[i] ) + " queried at " + str (MyDateLib.getOriginalDate( self.currentTime)) + " for a span of %s hours" %self.timespan
        
        return title
        
    
    
    def plot( self ):
        """
            Used to plot graphic.
        
        """
        
        
        color = 1
        
        const = len( self.stats ) -1
        
         
        self.graph('set size 1.5, %2.1f' % (0.65 * len( self.stats )))
        self.graph('set linestyle 1 ')
        
        self.graph.xlabel( 'time (hours)', offset = ("0.0"," -2.5") )
        self.graph.ylabel( 'latency (seconds)' )
        
        #self.graph( 'set grid')
        self.graph( 'set grid linestyle 1')
        
    
        self.graph( 'set xtics (%s)' % self.xtics)
        self.graph( "set xtics rotate" )

        
        if self.type == 'lines':
            self.graph( 'set data style lines' )  
        elif self.type == 'impulses':
            self.graph( 'set data style impulses' )  
        elif self.type == 'boxes':
            self.graph( 'set data style boxes' )  
        elif self.type == 'linespoints':
            self.graph( 'set data style linespoints' )  
            
        
        self.graph( 'set terminal png size 1024 768' )
        self.imageName = "%s_latencies.%s_%s.png" % ( "Nicholas", "Lemay", "STATS"  )

        self.graph( "set autoscale" )
        self.graph( 'set output "%s%s"' % ( "/apps/", self.imageName ) )
        self.graph('set multiplot') 
        
        
        for i in range( len( self.stats ) ) :
            
            pairs = self.getPairs(i)
            
            
            #print "i :%s" %i
            self.graph( 'set bmargin 8' )
            self.graph(' set rmargin 100 ')
            self.graph('set size 1.50, .65')
            self.graph('set origin 0, %3.2f' %(((const-i)*.65)  ))

            #print "origine : %s " %((const-i)*.65) 
            
            self.graph( 'set label "MAX: %3.2f,  MEAN: %4.2f ,  MIN: %3.2f" at screen %i, screen %3.2f' %( self.max, self.mean, self.minimum,1.0,( 0.55 +(const-i) *.65) ) )
            self.graph( 'set label "Client : %s" at screen .85, screen %3.2f' % ("Le px",(.40+(const-i) *.65)  ))
            self.graph( 'set label "Machines :%s" at screen .85, screen %3.2f' % ("Le px",(.38+(const-i) *.65)  ) )
            self.graph( 'set label "Maximum occured at: %s" at screen .85, screen %3.2f' % ("Le px", (.36+(const-i) *.65)  ))
            self.graph( 'set label "On file :%s" at screen .85, screen %3.2f' % ("Le px", (.34+(const-i) *.65) ))
            
            # self.graph('set multiplot') 
            self.graph.title( "%s" %self.buildTitle(i) )
    
            
            #print "pairs : %s "  %( pairs )
           
            
            
            self.graph.plot( Gnuplot.Data( pairs , with="%s %s 1" % ( self.type, color) ) )
        
        
        
        #raw_input('Please press return to continue...\n')
        
        self.graph.reset()
        
        self.graph = None

        
        
    #if __name__ == '__main__':
    
    #     ds = DirectoryStatsCollector.main()
    #     plotter = StatsPlotter(ds)
    #     plotter.plot()

    
    
    