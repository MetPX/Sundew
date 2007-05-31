#!/usr/bin/env python2
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.

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

import os, sys
"""
    Small function that adds pxlib to the environment path.  
"""
sys.path.insert(1, sys.path[0] + '/../../')
try:
    pxlib = os.path.normpath( os.environ['PXROOT'] ) + '/lib/'
except KeyError:
    pxlib = '/apps/px/lib/'
sys.path.append(pxlib)


"""
    Imports
    Logger requires pxlib 
""" 
import sys, commands, copy, logging, shutil 
import Gnuplot, Gnuplot.funcutils

from   Logger  import *

from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.ClientStatsPickler import ClientStatsPickler
from pxStats.lib.StatsPaths import StatsPaths


LOCAL_MACHINE = os.uname()[1]


class StatsPlotter:

    def __init__( self, timespan,  stats = None, clientNames = None, groupName = "", type='lines', interval=1, imageName="gnuplotOutput", title = "Stats",currentTime = "",now = False, statsTypes = None, productTypes = ["All"], logger = None, fileType = "tx", machines = "", entryType = "minute", maxLatency = 15 ):
        """
            StatsPlotter constructor. 
            
        """                                                                    
   
        
        #TODO Verify if all theses fileds are really necessary.    
        machines = "%s" %machines
        machines = machines.replace( "[","").replace( "]","" ).replace( "'", "" )
        
        self.now         = now                     # False means we round to the top of the hour, True we don't
        self.stats       = stats or []             # ClientStatsPickler instance.
        self.clientNames = clientNames or []       # Clients for wich we are producing the graphics. 
        self.groupName   = groupName               # Group name used when combining data of numerous client/sources.
        self.timespan    = timespan                # Helpfull to build titles 
        self.currentTime = currentTime             # Time of call
        self.type        = 'impulses'              # Must be in: ['linespoint', 'lines', 'boxes', 'impulses'].
        self.fileType    = fileType                # Type of file for wich the data was collected
        self.imageName   = imageName               # Name of the image file.
        self.nbFiles     = []                      # Number of files found in the data collected per server.
        self.nbErrors    = []                      # Number of errors found per server
        self.graph       = Gnuplot.Gnuplot()       # The gnuplot graphic object itself. 
        self.timeOfMax   = [[]]                    # Time where the maximum value occured.  
        self.machines    = machines                # List of machine where we collected info.
        self.entryType   = entryType               # Entry type :  minute, hour, week, month
        self.clientName  = ""                      # Name of the client we are dealing with 
        self.maxLatency  = maxLatency              # Maximum latency 
        self.maximums    = [[]]                    # List of all maximum values 1 for each graphic.
        self.minimums    = [[]]                    # Minimum value of all pairs.
        self.means       = [[]]                    # Mean of all the pairs.
        self.maxFileNames= [[]]                    # Name of file where value is the highest .
        self.filesWhereMaxOccured = [[]]           # List of files for wich said maximums occured.  
        self.statsTypes  = statsTypes or []        # List of data types to plot per client.
        self.totalNumberOfBytes    = []            # Total of bytes for each client 
        self.nbFilesOverMaxLatency = []            # Numbers of files for wich the latency was too long.
        self.ratioOverLatency      = []            # % of files for wich the latency was too long. 
        self.const = len( self.stats ) -1          # Usefull constant
        self.productTypes = productTypes           # Type of product for wich the graph is being generated.  
        self.initialiseArrays()
        self.loggerName       = 'statsPlotter'
        self.logger           = logger
        
        if self.fileType == 'tx':
            self.sourlient = "Client"
        else:
            self.sourlient = "Source"  
        
        if self.logger == None: # Enable logging
            self.logger = Logger( StatsPaths.STATSLOGGING +  'stats_' + self.loggerName + '.log', 'INFO', 'TX' + self.loggerName, bytes = True  ) 
            self.logger = self.logger.getLogger()
            
        self.xtics       = self.getXTics( )        # Seperators on the x axis.
    
    
    def initialiseArrays( self ):
        """
            Used to set the size of the numerous arrays needed in StatsPlotter
        """
        
        #TODO Verify if really necessary
        nbClients = len( self.clientNames )
        nbTypes   = len( self.statsTypes )
        
        self.nbFiles = [0] * nbClients
        self.nbErrors = [0] * nbClients
        self.nbFilesOverMaxLatency = [0] * nbClients
        self.totalNumberOfBytes    = [0] * nbClients
        self.ratioOverLatency      = [0.0] * nbClients
        self.timeOfMax   = [ [0]*nbTypes  for x in range( nbClients ) ]
        self.maximums    = [ [0.0]*nbTypes  for x in range( nbClients ) ] 
        self.minimums    = [ [0.0]*nbTypes  for x in range( nbClients ) ]
        self.means       = [ [0.0]*nbTypes  for x in range( nbClients ) ]
        self.maxFileNames= [ [0.0]*nbTypes  for x in range( nbClients ) ]
        self.filesWhereMaxOccured =  [ [0.0]*nbTypes  for x in range( nbClients ) ] 
            
        
    def buildImageName( self ):
        """
            Builds and returns the absolute fileName so that it can be saved 
            
            If folder to file does not exists creates it.
        
        """ 
        
        entityName = ""
        
        if len( self.clientNames ) == 0:
            entityName = self.clientNames[0]
        else:
            if self.groupName == "" :
                for name in self.clientNames :
                    entityName = entityName + name  
                    if name != self.clientNames[ len(self.clientNames) -1 ] :
                        entityName = entityName + "-"  
            else:
                entityName = self.groupName 
                
        date = self.currentTime.replace( "-","" ).replace( " ", "_")
        
        if self.productTypes[0] == "All":
            formattedProductName = "All"
        else:
            formattedProductName = "Specific"    
                
        fileName = StatsPaths.STATSGRAPHS + "others/gnuplot/%.50s/%s_%.50s_%s_%s_%shours_on_%s_for %s products.png" %( entityName, self.fileType, entityName, date, self.statsTypes, self.timespan, self.machines, formattedProductName )
        
        
        fileName = fileName.replace( '[', '').replace(']', '').replace(" ", "").replace( "'","" )               
        #TODO make other method out of this
        splitName = fileName.split( "/" ) 
        
        if fileName[0] == "/":
            directory = "/"
        else:
            directory = ""
        
        for i in range( 1, len(splitName)-1 ):
            directory = directory + splitName[i] + "/"
        
          
        if not os.path.isdir( directory ):
            os.makedirs( directory, mode=0777 )  
        
          
        
        return fileName 
    
    
        
    def getXTics( self ):
        """
           
           This method builds all the xtics used to seperate data on the x axis.
            
           Xtics values will are used in the plot method so they will be drawn on 
           the graphic. 
           
           Note : All xtics will be devided hourly. This means a new xtic everytime 
                  another hour has passed since the starting point.  
            
            
        """
        #print "get x tics"
        if self.logger != None :
            self.logger.debug( "Call to getXtics received" )
        
        nbBuckets = ( len( self.stats[0].statsCollection.timeSeperators ) )
        xtics = ''
        startTime = StatsDateLib.getSecondsSinceEpoch( self.stats[0].statsCollection.timeSeperators[0] )
        
        if nbBuckets != 0 :
            
            for i in range(0, nbBuckets ):
                 
                   
                if ( (  StatsDateLib.getSecondsSinceEpoch(self.stats[0].statsCollection.timeSeperators[i]) - ( startTime  ) ) %(60*60)  == 0.0 ): 
                    
                    hour = StatsDateLib.getHoursFromIso( self.stats[0].statsCollection.timeSeperators[i] )
                    
                    xtics += '"%s" %i, '%(  hour , StatsDateLib.getSecondsSinceEpoch(self.stats[0].statsCollection.timeSeperators[i] ) )

        
        #print nbBuckets
        #print "len xtics %s" %len(xtics) 
        return xtics[:-2]
         
        
        
    def getPairs( self, clientCount , statType, typeCount  ):
        """
           
           This method is used to create the data couples used to draw the graphic.
           Couples are a combination of the data previously gathered and the time
           at wich data was produced.  
           
           Note : One point per pair will generally be drawn on the graphic but
                  certain graph types might combine a few pairs before drawing only 
                  one point for the entire combination.
                  
           Warning : If illegal statype is found program will be terminated here.       
           
           #TODO Using dictionaries instead of arrays might speed thinga up a bit.
            
        """
        
        if self.logger != None: 
            self.logger.debug( "Call to getPairs received." )
        
        k = 0 
        pairs = []
        total = 0
        self.nbFiles[clientCount]  = 0
        self.nbErrors[clientCount] = 0
        self.nbFilesOverMaxLatency[clientCount] = 0
        nbEntries = len( self.stats[clientCount].statsCollection.timeSeperators )-1 
               
        
        if nbEntries !=0:
            
            total = 0
                            
            self.minimums[clientCount][typeCount] = 100000000000000000000 #huge integer
            self.maximums[clientCount][typeCount] = None
            self.filesWhereMaxOccured[clientCount][typeCount] =  "" 
            self.timeOfMax[clientCount][typeCount] = ""
            
            for k in range( 0, nbEntries ):
                
                try :
                    
                    if len( self.stats[clientCount].statsCollection.fileEntries[k].means ) >=1 :
                            
                        #special manipulation for each type                    
                        if statType == "latency":
                            self.nbFilesOverMaxLatency[clientCount] = self.nbFilesOverMaxLatency[ clientCount ] + self.stats[clientCount].statsCollection.fileEntries[k].filesOverMaxLatency    
                    
                        elif statType == "bytecount":
                            self.totalNumberOfBytes[clientCount] =  self.totalNumberOfBytes[clientCount] +    self.stats[clientCount].statsCollection.fileEntries[k].totals[statType]
                        
                        
                        elif statType == "errors":
                                                    #calculate total number of errors
                            self.nbErrors[clientCount] = self.nbErrors[clientCount] + self.stats[clientCount].statsCollection.fileEntries[k].totals[statType] 
                            
                            
                        #add to pairs    
                        if statType == "errors" or statType == "bytecount": #both use totals     
                            pairs.append( [StatsDateLib.getSecondsSinceEpoch(self.stats[clientCount].statsCollection.timeSeperators[k]), self.stats[clientCount].statsCollection.fileEntries[k].totals[statType]] )
                                               
                            #print    StatsDateLib.getSecondsSinceEpoch(self.stats[clientCount].statsCollection.timeSeperators[k]), self.stats[clientCount].statsCollection.fileEntries[k].totals[statType]                        
                            
                        else:#latency uses means
                            
                            pairs.append( [ StatsDateLib.getSecondsSinceEpoch(self.stats[clientCount].statsCollection.timeSeperators[k]), self.stats[clientCount].statsCollection.fileEntries[k].means[statType]] )
                            
                            #print self.stats[clientCount].statsCollection.timeSeperators[k], self.stats[clientCount].statsCollection.fileEntries[k].means[statType]
                        
                            
                        if( self.stats[clientCount].statsCollection.fileEntries[k].maximums[statType]  > self.maximums[clientCount][typeCount] ) :
                            
                            self.maximums[clientCount][typeCount] =  self.stats[clientCount].statsCollection.fileEntries[k].maximums[statType]
                            
                            self.timeOfMax[clientCount][typeCount] = self.stats[clientCount].statsCollection.fileEntries[k].timesWhereMaxOccured[statType]
                            
                            self.filesWhereMaxOccured[clientCount][typeCount] = self.stats[clientCount].statsCollection.fileEntries[k].filesWhereMaxOccured[statType]
                        
                            
                        elif self.stats[clientCount].statsCollection.fileEntries[k].minimums[statType] < self.minimums[clientCount][typeCount] :      
                            
                            if not ( statType == "bytecount" and  self.stats[clientCount].statsCollection.fileEntries[k].minimums[statType] == 0 ):
                                self.minimums[clientCount][typeCount] = self.stats[clientCount].statsCollection.fileEntries[k].minimums[statType]
                                                    
                        self.nbFiles[clientCount]  = self.nbFiles[clientCount]  + self.stats[clientCount].statsCollection.fileEntries[k].nbFiles   
                   
                              
                    else:
                   
                        pairs.append( [ StatsDateLib.getSecondsSinceEpoch(self.stats[clientCount].statsCollection.timeSeperators[k]), 0.0 ] )
                
                
                except KeyError:
                    
                    self.logger.error( "Error in getPairs." )
                    self.logger.error( "The %s stat type was not found in previously collected data." %statType )    
                    pairs.append( [ StatsDateLib.getSecondsSinceEpoch(self.stats[clientCount].statsCollection.timeSeperators[k]), 0.0 ] )
                    pass    
                
                
                total = total + pairs[k][1]            
            
            self.means[clientCount][typeCount] = (total / (k+1) ) 
            
            
            if self.nbFiles[clientCount] != 0 :
                self.ratioOverLatency[clientCount]  = float( float(self.nbFilesOverMaxLatency[clientCount]) / float(self.nbFiles[clientCount]) ) *100.0
            
            if self.minimums[clientCount][typeCount] == 100000000000000000000 :
                self.minimums[clientCount][typeCount] = None
            
            #print pairs 
                       
            return pairs    



    def getMaxPairValue( self, pairs ):
        """
            Returns the maximum value of a list of pairs. 
        
        """
        
        maximum = None
        
        if len( pairs) != 0 :
            
            for pair in pairs:
                if pair[1] > maximum:    
                    maximum = pair[1] 
                    
                    
        return  maximum 
        
        
        
    def getMinPairValue( self, pairs ):
        """
            Returns the maximum value of a list of pairs. 
        """     
            
        minimum = None 
        
        if len( pairs ) != 0 :
            minimum = pairs[0][1]
            for pair in pairs:
                if pair[1] < minimum:    
                    minimum = pair[1] 
                    
                    
        return  minimum         
    
            
    def buildTitle( self, clientIndex, statType, typeCount, pairs ):
        """
            This method is used to build the title we'll print on the graphic.
            Title is built with the current time and the name of the client where
            we collected the data. Also contains the mean and absolute min and max found 
            in the data used to build the graphic.          
               
        """  
        
        maximum = self.getMaxPairValue( pairs )
               
        minimum = self.getMinPairValue( pairs )
        
        if maximum != None :
            if statType == "latency":
                maximum = "%.2f" %maximum
            else:
                maximum = int(maximum)
            
        if minimum != None :
            if statType == "latency":
                minimum = "%.2f" %minimum
            else:
                minimum = int(minimum)
                
        if statType == "latency":
            explanation = "With values rounded for every minutes."
        else:
            explanation = "With the total value of every minutes."
                        
        statType = statType[0].upper() + statType[1:]             
              
        if self.groupName == "":
            entityName = self.clientNames[clientIndex]
        else:          
            entityName = self.groupName
            
        title =  "%s for %s for a span of %s hours ending at %s\\n%s\\n\\nMAX: %s  MEAN: %3.2f MIN: %s " %( statType, entityName, self.timespan, self.currentTime, explanation, maximum, self.means[clientIndex][typeCount], minimum )     
        
        return title
        
    
    
    def createCopy( self ):
        """
            Creates a copy of the created image file so that it
            easily be used in columbo. 
            
        """
        
        src = self.imageName
        
        if self.groupName != "":            
            
            destination = StatsPaths.STATSGRAPHS + "webGraphics/groups/%s.png"  %self.groupName 
                
        else:   
        
            clientName = ""
                   
            if len( self.clientNames ) == 0:
                clientName = self.clientNames[0]
            else:
                for name in self.clientNames :
                    clientName = clientName + name  
                    if name != self.clientNames[ len(self.clientNames) -1 ] :
                        clientName = clientName + "-" 
        
            destination = StatsPaths.STATSGRAPHS + "webGraphics/columbo/%s.png" %clientName

        
        if not os.path.isdir( os.path.dirname( destination ) ):
            os.makedirs(  os.path.dirname( destination ), mode=0777 )                                                      
        
        shutil.copy( src, destination ) 
        
        print "cp %s %s  "  %( src, destination )
       

       
    def plot( self, createCopy = False  ):
        """
            Used to plot gnuplot graphics. Settings used are
            slighly modified but mostly based on Plotter.py's
            plot function. 
            
        """
        
        if self.logger != None:
            self.logger.debug( "Call to plot received" )
        
        #Set general settings for graphs 
        color = 1
        nbGraphs = 0
         
        totalSize  = ( 0.40 * len( self.stats )  * len( self.statsTypes ) )
        totalHeight = ( 342 * len( self.stats )  * len( self.statsTypes ) )
        
        self.graph( 'set terminal png size 1280,768' ) 
        self.graph( 'set size 1.0, %2.1f' % ( totalSize ) )
        
        self.graph( 'set linestyle 4 ')
        
        self.graph.xlabel( 'time (hours)' ) #, offset = ( "0.0"," -2.5" )
        
        self.graph( 'set grid')
        self.graph( 'set format y "%10.0f"' )
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
            
        
        #self.graph( 'set terminal png size 800,600' )
       
        self.imageName = self.buildImageName()

        #self.graph( "set autoscale" )
        self.graph( 'set output "%s"' % (  self.imageName ) )
        self.graph( 'set multiplot' ) 
        
        
        for clientIndex in range( len( self.stats ) ) :            
                       
            for statsTypeIndex in range ( len ( self.statsTypes ) ):
                
                pairs        = self.getPairs( clientCount = clientIndex , statType= self.statsTypes[statsTypeIndex], typeCount = statsTypeIndex )
                maxPairValue = self.getMaxPairValue( pairs )
                self.maxLatency = self.stats[clientIndex].statsCollection.maxLatency
                
                if self.statsTypes[statsTypeIndex] == "errors" :
                    color =2 #green                    
                    self.addErrorsLabelsToGraph(  clientIndex , statsTypeIndex, nbGraphs, maxPairValue )
                
                elif self.statsTypes[statsTypeIndex] == "latency" :
                    color =1 #red                    
                    self.addLatencyLabelsToGraph(  clientIndex , statsTypeIndex, nbGraphs,  maxPairValue )
                
                elif self.statsTypes[statsTypeIndex] == "bytecount" :
                    color =3 #blue 
                    self.addBytesLabelsToGraph(  clientIndex , statsTypeIndex, nbGraphs,  maxPairValue )
                    
                self.graph.title( "%s" %self.buildTitle( clientIndex, self.statsTypes[statsTypeIndex] , statsTypeIndex, pairs) )
                
                self.graph.plot( Gnuplot.Data( pairs , with="%s %s 1" % ( self.type, color) ) )
                
                nbGraphs = nbGraphs + 1 
                
                    
        if createCopy :
            del self.graph
            self.createCopy( )     
         
            
            
    def addLatencyLabelsToGraph( self, clientIndex, statsTypeIndex, nbGraphs, maxPairValue ):
        """
            Used to set proper labels for a graph relating to latencies. 
             
        """            
        
        if self.maximums[clientIndex][statsTypeIndex] != None and self.maximums[clientIndex][statsTypeIndex] !=0 :
            
            timeOfMax = self.timeOfMax[clientIndex][statsTypeIndex] 
            
            if maxPairValue < 5 :
                self.graph( 'set format y "%7.2f"' )
            else:
                self.graph( 'set format y "%7.0f"' )
            
            maximum = self.maximums[clientIndex][statsTypeIndex]
        
        else:
            timeOfMax = ""
            maximum = ""       
            
            
        if self.groupName == "" :
            entityType = self.sourlient
            entityName = self.clientNames[clientIndex]
        else:
            entityType = "Group"
            entityName = self.groupName
                  
        
        formatedProductTypes = "%-25s" %( (str)( self.productTypes ) ).replace('[','' ).replace( ']', '' ).replace("'","")
                
        self.graph( 'set size .545, .37' )
        
        self.graph( 'set origin 0, %3.2f' %( ((nbGraphs)*.40)  ) )

        self.graph.ylabel( 'latency (seconds)' )
        
        self.graph( 'set label "%s : %s" at screen .545, screen %3.2f' % ( entityType, entityName,(.26+(nbGraphs) *.40)  ))
        
        self.graph( 'set label "Machines : %s" at screen .545, screen %3.2f' % ( self.machines,(.24+(nbGraphs) *.40)  ) )
        
        self.graph( 'set label "Product type(s) : %s" at screen .545, screen %3.2f' % ( formatedProductTypes,(.22+(nbGraphs) *.40)  ) )
        
        self.graph( 'set label "Absolute max. lat. : %s seconds" at screen .545, screen %3.2f' % ( maximum, (.20+(nbGraphs) *.40) ) )
        
        self.graph( 'set label "Time of max. lat. : %s" at screen .545, screen %3.2f' % ( ( timeOfMax, (.18+(nbGraphs) *.40)  )))
        
        if len ( self.filesWhereMaxOccured[clientIndex][statsTypeIndex] ) <= 50 :
            self.graph( 'set label "File with max. lat. :%s" at screen .545, screen %3.2f' % ( self.filesWhereMaxOccured[clientIndex][statsTypeIndex], (.16+(nbGraphs) *.40) ))     
        
        else:
            self.graph( 'set label "File with max. lat. :" at screen .545, screen %3.2f' % ( (.16+(nbGraphs) *.40) ))  
            
            self.graph( 'set label "%s" at screen .545, screen %3.2f' % ( self.filesWhereMaxOccured[clientIndex][statsTypeIndex], (.14+(nbGraphs) *.40 ) ))          
        
        self.graph( 'set label "# of files : %s " at screen .545, screen %3.2f' % ( self.nbFiles[clientIndex] , (.12+(nbGraphs) *.40) ) )
        
        self.graph( 'set label "# of files over %s seconds: %s " at screen .545, screen %3.2f' % ( self.maxLatency, self.nbFilesOverMaxLatency[clientIndex], ( .10+(nbGraphs) *.40 ) ) )
        
        self.graph( 'set label "%% of files over %s seconds: %3.2f %%" at screen .545, screen %3.2f' % (  self.maxLatency, self.ratioOverLatency[clientIndex] , ( .08 + (nbGraphs) *.40 ) ) )
        
                
    
            
    def addBytesLabelsToGraph( self, clientIndex, statsTypeIndex, nbGraphs, maxPairValue ):
        """
            Used to set proper labels for a graph relating to bytes. 
             
        """            
        
        if self.maximums[clientIndex][statsTypeIndex] != None and self.maximums[clientIndex][statsTypeIndex] != 0 :
            
            timeOfMax = self.timeOfMax[clientIndex][statsTypeIndex] 
            
            if maxPairValue < 5 :
                self.graph( 'set format y "%7.2f"' )
            else:
                self.graph( 'set format y "%7.0f"' )    
                
            maximum = self.maximums[clientIndex][statsTypeIndex]
        
        else:
            timeOfMax = ""
            maximum = ""
       
        
        if self.groupName == "" :
            entityType = self.sourlient
            entityName = self.clientNames[clientIndex]
        else:
            entityType = "Group"
            entityName = self.groupName
        
       
        if self.totalNumberOfBytes[clientIndex] < 1000:#less than a k
            totalNumberOfBytes = "%s Bytes" %int( self.totalNumberOfBytes[clientIndex] )
            
        elif self.totalNumberOfBytes[clientIndex] < 1000000:#less than a meg 
            totalNumberOfBytes = "%.2f kiloBytes"  %( self.totalNumberOfBytes[clientIndex]/1000.0 )
        
        elif self.totalNumberOfBytes[clientIndex] < 1000000000:#less than a gig      
            totalNumberOfBytes = "%.2f MegaBytes"  %( self.totalNumberOfBytes[clientIndex]/1000000.0 )
        else:#larger than a gig
            totalNumberOfBytes = "%.2f GigaBytes"  %( self.totalNumberOfBytes[clientIndex]/1000000000.0 )
         
        formatedProductTypes = "%-25s" %( (str)( self.productTypes ) ).replace('[','' ).replace( ']', '' ).replace("'","") 
            
        self.graph( 'set size .545, .37' )
        
        self.graph( 'set origin 0, %3.2f' %( ((nbGraphs)*.40)  ))
        
        self.graph.ylabel( 'Bytes/Minute' )
        
        self.graph( 'set label "%s : %s" at screen .545, screen %3.2f' % ( entityType, entityName,(.26+(nbGraphs) *.40)  ))
        
        self.graph( 'set label "Machines : %s" at screen .545, screen %3.2f' % ( self.machines,(.24+(nbGraphs) *.40)  ) )
        
        self.graph( 'set label "Product type(s) : %s" at screen .545, screen %3.2f' % ( formatedProductTypes,(.22+(nbGraphs) *.40)  ) )
        
        
        if len ( self.filesWhereMaxOccured[clientIndex][statsTypeIndex] ) <= 65 :            
            self.graph( 'set label "Largest file : %s" at screen .545, screen %3.2f' % ( self.filesWhereMaxOccured[clientIndex][statsTypeIndex], (.20+(nbGraphs) *.40) ))
            x = .20
        else:
            self.graph( 'set label "Largest file : " at screen .545, screen %3.2f' % ( ( .20 + ( nbGraphs ) *.40) ) )
            
            self.graph( 'set label "%s" at screen .545, screen %3.2f' % ( self.filesWhereMaxOccured[clientIndex][statsTypeIndex], (.18+(nbGraphs) *.40) ))
            x = .18
                    
        self.graph( 'set label "Size of largest file : %s Bytes" at screen .545, screen %3.2f' % ( maximum, (x -.02+(nbGraphs) *.40) ) )       
                
        self.graph( 'set label "Time of largest file : %s" at screen .545, screen %3.2f' % ( ( timeOfMax, (x -.04+(nbGraphs) *.40)  )))     
        
        self.graph( 'set label "# of files : %s " at screen .545, screen %3.2f' % ( self.nbFiles[clientIndex] , ( x-.06+(nbGraphs) *.40) ) )
    
        self.graph( 'set label "# of Bytes: %s " at screen .545, screen %s' % (  totalNumberOfBytes,( x -.08 +(nbGraphs) *.40 ) ) )
                

    
    
    def addErrorsLabelsToGraph( self, clientIndex, statsTypeIndex, nbGraphs, maxPairValue ):
        """
            Used to set proper labels for a graph relating to bytes. 
             
        """   
                 
        if self.maximums[clientIndex][statsTypeIndex] !=None and self.maximums[clientIndex][statsTypeIndex] != 0 :
            
            timeOfMax =  self.timeOfMax[clientIndex][statsTypeIndex]
            timeOfMax =  StatsDateLib.getIsoWithRoundedSeconds( timeOfMax )
            
            if maxPairValue < 5 :
                self.graph( 'set format y "%7.2f"' )
            else:
                self.graph( 'set format y "%7.0f"' )
        
            maximum = self.maximums[clientIndex][statsTypeIndex]
        
        else:
            timeOfMax = ""
            maximum = ""
               
        if self.groupName == "" :
            entityType = self.sourlient
            entityName = self.clientNames[clientIndex]
        else:
            entityType = "Group"
            entityName = self.groupName    
        
        formatedProductTypes = "%-25s" %( (str)( self.productTypes ) ).replace('[','' ).replace( ']', '' ).replace("'","")
        
        self.graph( 'set size .545, .37' )
        
        self.graph( 'set origin 0, %3.2f' %( ((nbGraphs)*.40)  ))
        
        self.graph.ylabel( 'Errors/Minute' )
        
        self.graph( 'set label "%s : %s" at screen .545, screen %3.2f' % ( entityType, entityName,(.26+(nbGraphs) *.40)  ))
        
        self.graph( 'set label "Machines : %s" at screen .545, screen %3.2f' % ( self.machines,(.24+(nbGraphs) *.40)  ) )
        
        self.graph( 'set label "Product type(s) : %s" at screen .545, screen %3.2f' % ( formatedProductTypes,(.22+(nbGraphs) *.40)  ) )
        
        self.graph( 'set label "Max error/%s : %s" at screen .545, screen %3.2f' % ( self.entryType, maximum, (.20+(nbGraphs) *.40) ))        
        
        self.graph( 'set label "Time of max. : %s" at screen .545, screen %3.2f' % ( ( timeOfMax, (.18+(nbGraphs) *.40)  )))
        
        self.graph( 'set label "# of errors : %.f" at screen .545, screen %3.2f' % ( self.nbErrors[clientIndex], (.16+(nbGraphs) *.40) ) )
      
                
                
            




    
    
    
