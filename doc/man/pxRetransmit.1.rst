
==============
 PXRetransmit
==============

-------------------------------------------------
Metpx script to retransmit product(s) to a sender
-------------------------------------------------

:Manual section: 1
:Date: @Date@
:Version: @Version@
:Manual group: MetPx Sundew Suite


SYNOPSIS
========

**pxRetransmit** *sender_name* [ *filepath1 filepath2 filepath3...* ]

DESCRIPTION
===========

pxRetransmit can be used to resend products to a client.  first determine
the products within METPX's database $PXROOT/db/yyyymmdd... to be retransmitted,
Then invoke the program followed by the sender's name and the product  
filepath.

**pxRetransmit** does the following ::

   check the number of arguments
   make sure that the sender queue exists $PXROOT/txq/"sender_name"
   verify/create a priority directory named 0
   verify/create a datetime subdirectory under directory 0
   cp the product file in that sender's subdirectory

The sender, scans endlessly all directories under $PXROOT/txq/"sender_name" in 
search of products.  For products present under the 0 priority directory,
the sender process them without duplicate checking if enabled.

The user must be careful when using **pxRetransmit**.
Any product given to the script will be put in the client's queue regardless 
of the whole routing process and the sender's configuration.
