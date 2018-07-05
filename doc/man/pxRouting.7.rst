
===========
 PXRouting
===========

----------------------------------------
how data travels between Metpx processes
----------------------------------------

:Manual section: 7
:Date: @Date@
:Version: @Version@
:Manual group: MetPx Sundew Suite



DESCRIPTION
===========

METPX defines **routing** as the means to define how data must travel through its processes.
A more practical way of looking at it is how a received product will be sent to the proper clients.

The programs that initiate routing are the one receiving data namely: receivers, filters and
transceivers. The routing algorithm is the same for all of them.  For simplicity,
throughout this document we will use a receiver as the routing initiator.

The data is routed to processes such as filters, transceivers and senders.
Again for simplicity, we will use senders as the routing's end target.

When a receiver starts (or reloads), it reads his configuration file and it loads its routing table.
The receiver creates a list of active senders, by parsing the configuration of all senders available in the
METPX's current implementation.

The routing table is a table indexed by "product keys". To each product key is associated two 
informations : the product's priority and the product's list of interested senders. 

To perform the routing of a product, the receiver will ::

     1- accept or reject the product
     2- genarate a product key
     3- establish a list of routable senders
     4- deliver to senders accepting the product

ACCEPT OR REJECT THE PRODUCT
============================

When a receiver has received a product, it determines the filename that the product will be given.
By convention that filename is called the ingestName. 

The ingestName is matched against the **accept** and **reject** regexp patterns of the receiver's
configuration file.  The default (no match) is for the file to be accepted.

**reject** can be used to suppress reception of files with a certain pattern. Files suppressed are
not ingested into the DB and they are not routed any further.

If the product is accepted, its routing continues.

GENERATE A PRODUCT KEY
======================

The receiver derives from the product received a product key.
For bulletins, the key generated is T1T2A1A1ii_CCCC (see wmo bulletin definition). 
For example SACN31_CWAO.

For anything else, the key is the ingestName (filename given to the incoming product)
without its datetime reception suffix.

There are cases where the ingestName has unstable parts. The ingestName as is, cannot be a
constant product key hence routing becomes impossible. In this case, the **accept** option
is instrumented to pick parts of the ingestName and create a stable product key.
You just have to put into parenthesis the parts that you want to keep in the product key.
Enclosed regular expressions are kept too. If more than one part are selected, the key 
will be the concatenation of the parts separeted by underscore.
For example ::

          accept .*(txt:AQ).*(:AIRNOW:.*:ASCII)
          ingestName = 20070515.txt:AQ1245Z:AIRNOW:CMQ:ASCII
          the product key generated will be txt:AQ_:AIRNOW:CMQ:ASCII

ESTABLISH THE LIST OF ROUTABLE SENDERS
======================================

Once the product key generated, the routing table is adressed with it.
If the product key is not found, the product is databased and its routing stops.
The receiver logs a warning saying that key "X" generated from "ingestName"
is not defined.

When the product key is found, the routing table provides the receiver 
with the product's associated list of senders and its priority. A sender is
considered routable if and only if this sender is present in the 
routing table list and the active sender list created at startup (reload).

DELIVER TO SENDERS ACCEPTING THE PRODUCT
========================================

For each routable sender, the ingestName is matched against the **accept** and **reject** 
regexp patterns from its configuration file.

The product isrouted to a sender only if it matches one of its **accept** options without
having matched a **reject** previously.

Once the receiver has determined that the sender should have the product, it writes
the products in its transmission directory tree...  namely under 
$PXROOT/txq/"sender_name"/priority/YYYYMMDDHH where YYYYMMDDHH is the current
date time. The priority is the one found in the routing table.

The routing ends when the sender processes the product.
