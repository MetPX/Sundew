"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

##############################################################################
##
##
## Name   : generateGraphics.py 
##
##
## Author : Nicholas Lemay
##
## Date   : 06-07-2006 
##
##
## Description : Very small application usefull for testing graphic production.
##
##
##############################################################################



import os, time, sys
from optparse import OptionParser
from ConfigParser import ConfigParser
from ClientGraphicProducer import *
import PXPaths

PXPaths.normalPaths()



class _GraphicsInfos:

    def __init__( self, directory, fileType, types, collectUpToNow,  clientNames = None ,  timespan = 12, currentTime = None, productType = "All", machines = ["pdsGG"]  ):

            
        self.directory    = directory         # Directory where log files are located. 
        self.fileType     = fileType          # Type of log files to be used.    
        self.types        = types             # Type of graphics to produce. 
        self.collectUpToNow = collectUpToNow  # Whether we create graphic up to collectUpToNow or not.
        self.clientNames  = clientNames or [] # Client name we need to get the data from.
        self.timespan     = timespan          # Number of hours we want to gather the data from. 
        self.currentTime  = currentTime       # Time when stats were queried.
        self.productType  = productType       # Specific data type on wich we'll collect the data.
        self.machines     = machines          # Machine fro wich we want the data to be calculated.
        
        
#################################################################
#                                                               #
#############################PARSER##############################
#                                                               #
#################################################################   
def getOptionsFromParser( parser ):
    """
        
        This method parses the argv received when the program was called
        It takes the params wich have been passed by the user and sets them 
        in the corresponding fields of the infos variable.   
    
        If errors are encountered in parameters used, it will immediatly terminate 
        the application. 
    
    """ 
    
    currentTime   = []
    
    ( options, args )= parser.parse_args()        
    collectUpToNow   = options.collectUpToNow
    timespan         = options.timespan
    machines         = options.machines.replace( ' ','').split(',')
    clientNames      = options.clients.replace( ' ','' ).split(',')
    types            = options.types.replace( ' ', '').split(',')
    currentTime      = options.currentTime.replace('"','').replace("'",'')
    fileType         = options.fileType.replace("'",'')
    collectUpToNow   = options.collectUpToNow
    productType      = options.productType.replace( ' ', '' )     
     
    try:    
        if int( timespan ) < 1 :
            raise 
            print "trouve lerreur"
    
    except:
        
        print "Error. The timespan value needs to be an integer one above 0." 
        print "Use -h for help."
        print "Program terminated."
        sys.exit()
        
    
    if fileType != "tx" and fileType != "rx":
        print "Error. File type must be either tx or rx."
        print 'Multiple types are not accepted.' 
        print "Use -h for additional help."
        print "Program terminated."
        sys.exit()    
        
    
    if fileType == "tx":       
        validTypes = ["errors","latency","bytecount"]

    else:
        validTypes = ["errors","bytecount"]
           
    try :
        for t in types :
            if t not in validTypes:
                raise 
                print "trouve lerreur"
    except:    
        
        print "Error. With %s fileType, possible data types values are : %s." %(fileType,validTypes )
        print 'For multiple types use this syntax : -t "type1,type2"' 
        print "Use -h for additional help."
        print "Program terminated."
        sys.exit()
    
    directory = PXPaths.LOG
    

   
    infos = _GraphicsInfos( collectUpToNow = collectUpToNow, currentTime = currentTime, clientNames = clientNames,  directory = directory , types = types, fileType = fileType, timespan = timespan, productType = productType, machines = machines )
    
    if collectUpToNow == False:
        infos.endTime = MyDateLib.getIsoWithRoundedHours( infos.currentTime ) 
    
    
    return infos 
                   

        
        
def createParser( ):
    """ 
        Builds and returns the parser 
    
    """
    
    usage = """

%prog [options]
********************************************
* See doc.txt for more details.            *
********************************************
Notes :
- Now option not yet implemented.    

Defaults :

- Default Client name does not exist.
- Default Date is current system time.  
- Default Types value is latency.
- Default span is 12 hours.
- Accepted values for types are : errors,latency,bytecount
  -To use mutiple types, use -t|--types "type1,type2"


Options:
 
    - With -c|--clients you can specify the clients names on wich you want to collect data. 
    - With -d|--date you can specify the time of the request.( Usefull for past days and testing. )
    - With -f|--fileType you can specify the file type of the log fiels that will be used.  
    - With -n|--collectUpToNow you can specify that data must be collected right up to the minute of the call. 
    - With -s|--span you can specify the time span to be used to create the graphic 
    - With -t|--types you can specify what data types need to be collected
    
      
WARNING: - Client name MUST be specified,no default client exists. 
          
            
Ex1: %prog                                   --> All default values will be used. Not recommended.  
Ex2: %prog -c satnet                         --> All default values, for client satnet. 
Ex3: %prog -c satnet -d '2006-06-30 05:15:00'--> Client satnet, Date of call 2006-06-30 05:15:00.
Ex4: %prog -c satnet -t "errors,latency"     --> Uses current time, client satnet and collect those 2 types.
********************************************
* See /doc.txt for more details.           *
********************************************"""   
    
    parser = OptionParser( usage )
    addOptions( parser )
    
    return parser     
        
        

def addOptions( parser ):
    """
        This method is used to add all available options to the option parser.
        
    """
    
    localMachine = os.uname()[1]
    
    parser.add_option("-c", "--clients", action="store", type="string", dest="clients", default="satnet",
                        help="Clients' names")

    parser.add_option("-d", "--date", action="store", type="string", dest="currentTime", default=MyDateLib.getIsoFromEpoch( time.time() ), help="Decide current time. Usefull for testing.")
    
    parser.add_option("-f", "--fileType", action="store", type="string", dest="fileType", default='tx', help="Type of log files wanted.")                     
   
    parser.add_option( "-m", "--machines", action="store", type="string", dest="machines", default=localMachine, help = "Machines for wich you want to collect data." ) 
    
    parser.add_option("-n", "--collectUpToNow", action="store_true", dest = "collectUpToNow", default=False, help="Collect data up to current second.")
    
    parser.add_option("-p", "--product", action="store", type = "string", dest = "productType", default="All", help="Product type to look for in the data collected.")
    
    parser.add_option("-s", "--span", action="store",type ="int", dest = "timespan", default=12, help="timespan( in hours) of the graphic.")
       
    parser.add_option("-t", "--types", type="string", dest="types", default="latency,errors,bytecount",
                        help="Types of data to look for.")   





def main():
    
    parser = createParser( )  #will be used to parse options 
    
    infos = getOptionsFromParser( parser )      
        
    gp = ClientGraphicProducer( clientNames = infos.clientNames, timespan = infos.timespan, currentTime = infos.currentTime, productType = infos.productType, directory = infos.directory , fileType = infos.fileType, machines = infos.machines )  
    
    gp.produceGraphicWithHourlyPickles( types = infos.types, now = infos.collectUpToNow   )
    
    #add logging here 
    print "Done."


if __name__ == "__main__" :
    main()