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
# Author      : Nicholas Lemay, but the code is highly inspired by previously created file 
#               named Plotter.py written by Daniel Lemay. This file can be found in the lib
#               folder of this application. 
#
# Date        : 2006-06-06
#
# Description : This class contain the data structure and the methods used to plot a graphic 
#               using previously collected data. The data should have been collected using 
#               the data collecting class' and methods found in the stats library. 
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
import copy 



class StatsPlotter:

    def __init__( self, timespan,  stats = None, clientNames = None, type='impulses', interval=1, imageName="gnuplotOutput", title = "Stats",currentTime = "",now = False):
        """
            StatsPlotter constructor. 
            
        """
        
        self.now         = now                     # False means we round to the top of the hour, True we don't
        self.stats       = stats or []             # DirectoryStatsCollector instance.
        self.clientNames = clientNames or []       # Clients for wich we are producing the graphics. 
        self.timespan    = timespan                # Helpfull to build titles 
        self.currentTime = currentTime             # Time of call
        self.type        = type                    # Must be in: ['linespoint', 'lines', 'boxes', 'impulses'].
        self.imageName   = imageName               # Name of the image file.
        self.nbFiles     = 0                       # Number of files found in the data collected.
        self.xtics       = self.getXTics( )        # Seperarators on the x axis.
        self.graph       = Gnuplot.Gnuplot()       # The gnuplot graphic object itself. 
        self.timeOfMax   = []                      # Time where the maximum value occured.  
        self.machines    = ""                      # List of machine where we collected info.
        self.clientName  = ""                      # Name of the client we are dealing with 
        self.maximums    = []                      # List of all maximum values 1 for each graphic.
        self.minimums    = []                      # Minimum value of all pairs.
        self.means       = []                      # Mean of all the pairs.
        self.maxFileNames= []                      # Name of file where value is the highest . 
        self.timeOfMax   = []                      # List of all the times where said maximums occured. 
        self.nbFilesOverMaxLatency = 0             # Numbers of files for wich the latency was too long.
        self.ratioOverLatency      = 0.0           # % of files for wich the latency was too long. 
        self.filesWhereMaxOccured  = []            # List of files for wich said maximums occured. 
           
       
        
              
    def getXTics(self):
        """
           
           This method builds all the xtics used to seperate data on the x axis.
            
           Xtics values will are used in the plot method so they will be drawn on 
           the graphic. 
           
           Note : All xtics will be devided hourly. This means a new xtic everytime 
                  another hour has passed since the starting point.  
            
            
        """
        
        nbBuckets = ( len( self.stats[0].statsCollection.timeSeperators ) )
        xtics = ''
       
        if nbBuckets != 0 :
            
            startTime = MyDateLib.getOriginalHour( self.stats[0].statsCollection.startTime )
            xtics += '"%s" %i, ' % ( startTime, self.stats[0].statsCollection.startTime  )
            
            for i in range( 1, nbBuckets ):
                
                if ( ( self.stats[0].statsCollection.timeSeperators[i] - self.stats[0].statsCollection.startTime) %(60*60) == 0 ): 
                    
                    hour = MyDateLib.getHoursFromIso( MyDateLib.getIsoFromEpoch( self.stats[0].statsCollection.timeSeperators[i] ) )
                    
                    xtics += '"%s" %i, '%(  hour ,self.stats[0].statsCollection.timeSeperators[i] ) 

        
        return xtics[:-2]
    

    
    def getPairs( self, i ):
        """
           
           This method is used to create the data couples used to draw the graphic.
           Couples are a combination of the data previously gathered and the time
           at wich data was produced.  
           
           Note : One point per pair should generally be drawn on the graphic but
                  certain graph types might combine a few pairs before drawing only 
                  one point for the entire combination.
        
        """
        
        pairs        = []
        nbEntries    = len( self.stats[i].statsCollection.timeSeperators ) 
        self.nbFiles = 0
        self.total   = 0
        
        if nbEntries !=0:
            
            if len( self.stats[i].statsCollection.fileEntries[0].means ) >=1 :
                
                pairs.append( [self.stats[i].statsCollection.startTime, self.stats[i].statsCollection.fileEntries[0].means[0]] )
                self.nbFiles  = self.stats[i].statsCollection.fileEntries[0].values.rows  
            
            else:
                
                pairs.append( [self.stats[i].statsCollection.startTime, 0.0] )
                
            
            self.total = pairs[0][1]
            self.minimums.append( pairs[0][1] )
            self.maximums.append( pairs[0][1] )
            self.filesWhereMaxOccured.append( "" )
            self.timeOfMax.append("")
                       
            
            for j in range( 1, nbEntries ):
                
                self.stats[i].statsCollection.fileEntries[j].means
                
                if len( self.stats[i].statsCollection.fileEntries[j].means ) >=1 :
                    pairs.append( [self.stats[i].statsCollection.timeSeperators[j], self.stats[i].statsCollection.fileEntries[j].means[0]] )
                    
                     
                    if( self.stats[i].statsCollection.fileEntries[j].maximums[0]  > self.maximums[i] ) :
                        
                        self.maximums[i] =  self.stats[i].statsCollection.fileEntries[j].maximums[0]
                        self.timeOfMax[i] = self.stats[i].statsCollection.fileEntries[j].timesWhereMaxOccured[0]
                        self.filesWhereMaxOccured[i] = self.stats[i].statsCollection.fileEntries[j].filesWhereMaxOccured[0]
                    
                    elif self.stats[i].statsCollection.fileEntries[j].minimums[0] < self.minimums[i] :         
                        self.minimums[i] = pairs[j][1]
                    
                    self.nbFiles  = self.nbFiles  + self.stats[i].statsCollection.fileEntries[j].values.rows       
                    
                    self.nbFilesOverMaxLatency = self.nbFilesOverMaxLatency + self.stats[i].statsCollection.fileEntries[j].filesOverMaxLatency
                    
                    
                else:
                    pairs.append( [ self.stats[i].statsCollection.timeSeperators[j], 0.0 ] )
                    
                    
                self.total = self.total + pairs[j][1]
                        
            self.means.append( float( self.total / j ) )
            
            if self.nbFiles != 0 :
                print "allo"
                self.ratioOverLatency  = float( float(self.nbFilesOverMaxLatency) / float(self.nbFiles) ) *100.0
        
        return pairs    
         
    
    
    def buildTitle( self, i ):
        """
            This method is used to build the title we'll print on the graphic.
            Title is built with the current time and the name of the client where
            we collected the data. Also contains the mean and absolute min and max found 
            in the data used to build the graphic. 
            
        """
        
        title = "Latencies for " + str( self.clientNames[i] ) + " queried at " + str ( MyDateLib.getIsoFromEpoch( self.currentTime )) + ' for a span of %s hours \\n\\n'%self.timespan +  "MAX: %3.2f,  MEAN: %3.2f , MIN: %3.2f " %( self.maximums[i], self.means[i], self.minimums[i] )
         
        return title
        
    
    
    def plot( self ):
        """
            Used to plot gnuplot graphics. Settings used are
            slighly modified but mostly based on Plotter.py's
            plot function. 
            
        """
        
        
        color = 1
        
        const = len( self.stats ) -1
        
        self.graph( 'set size 2.0, %2.1f' % (0.55 * len( self.stats )))
        self.graph( 'set linestyle 4 ')
        
        self.graph.xlabel( 'time (hours)' ) #, offset = ( "0.0"," -2.5" )
        self.graph.ylabel( 'latency (seconds)' )
        
        self.graph( 'set grid')
        
        self.graph( 'set xtics (%s)' % self.xtics)
        #self.graph( "set xtics rotate" )
        
        if self.type == 'lines':
            self.graph( 'set data style lines' )  
        elif self.type == 'impulses':
            self.graph( 'set data style impulses' )  
        elif self.type == 'boxes':
            self.graph( 'set data style boxes' )  
        elif self.type == 'linespoints':
            self.graph( 'set data style linespoints' )  
            
        
        self.graph( 'set terminal png size 1024 768' )
        self.imageName = "%s_latencies.%s_%s.png"%("Nicholas", "Lemay", MyDateLib.getIsoFromEpoch( self.currentTime  ))

        self.graph( "set autoscale" )
        self.graph( 'set output "%s%s"' % ( "/apps/", self.imageName ) )
        self.graph( 'set multiplot' ) 
        
        
        
        for i in range( len( self.stats ) ) :
            
            
            pairs = self.getPairs(i)
            
            if self.maximums[i] !=0:
                timeOfMax = MyDateLib.getIsoFromEpoch( self.timeOfMax[i] )
            else:
                timeOfMax = ""
                    
            #self.graph( 'set bmargin 8' )
            #self.graph( ' set rmargin 100 ' )
            
            self.graph( 'set size .65, .55' )
            self.graph( 'set origin 0, %3.2f' %( ((const-i)*.55)  ))

            self.graph( 'set label "Client : %s" at screen .65, screen %3.2f' % ( self.clientNames[i],(.38+(const-i) *.55)  ))
            self.graph( 'set label "Machines :%s" at screen .65, screen %3.2f' % ( self.machines,(.34+(const-i) *.55)  ) )
            
            self.graph( 'set label "Maximum occured at: %s" at screen .65, screen %3.2f' % ( ( timeOfMax, (.30+(const-i) *.55)  )))
            
            self.graph( 'set label "On file :%s" at screen .65, screen %3.2f' % ( self.filesWhereMaxOccured[i], (.26+(const-i) *.55) ))
            
            self.graph( 'set label "Maximum was : %s" at screen .65, screen %3.2f' % ( self.maximums[i], (.22+(const-i) *.55) ) )
            
            self.graph( 'set label "# of files : %s " at screen .65, screen %3.2f' % ( self.nbFiles , (.18+(const-i) *.55) ) )
              
            self.graph( 'set label "# of files over max latency: %s " at screen .65, screen %3.2f' % ( self.nbFilesOverMaxLatency, ( .14+(const-i) *.55 ) ) )
            
            self.graph( 'set label "%% of files over max latency: %3.2f %%" at screen .65, screen %3.2f' % ( self.ratioOverLatency   , ( .10+(const-i) *.55 ) ) )
            
            self.graph.title( "%s" %self.buildTitle(i) )
            self.graph.plot( Gnuplot.Data( pairs , with="%s %s 1" % ( self.type, color) ) )
        
        
        self.graph.reset()
        
        self.graph = None



    
    
    