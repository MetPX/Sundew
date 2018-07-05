
===========
 PXRouting
===========

--------------------------
defining the file's syntax
--------------------------

DESCRIPTION
===========

The product routing table is a simple ascii file. It must be placed in 
directory $PXROOT/etc (PXROOT is usually /apps/px). The default file's name
is ** pxRouting.conf**. You can overwrite the default with the option 
**routingTable <filename>**. 

Basically, the routing table is a table indexed by "product keys". To each product key
is associated two informations : the product's priority and the product's list of interested
processes (clients).

The product priority is a number from 1 to 5 where 1 gets the highest attention...etc.
The syntax to define such a table entry is :

**key <productKey> <client1,client2,...,clientN> <productPriority>**

A client list can become very long. Fortunately, some clients can be grouped, 
or associated in some intelligable fashion. To make our table entries more readable
(and shorter) the user can define aliases for lists of clients. Each clientAlias 
defines a unique name that refers to a particular list of clients. To define a clientAlias :

**clientAlias <aliasName> <client1,client2,...,clientN>**

and a product table entry can become :

**key <productKey> <client1,alias1,...,aliasX,clientN> <productPriority>**

When parsing the routing table file, duplicated clients in resulting client list are removed.

Defining exhaustive key entries  becomes fastidious. It is possible to associate a priority and a client list
to all the product keys that match a regexp pattern. The routing table instruction to use is key_accept and
its syntax is :

**key_accept <regexpKeyPattern> <client1,alias1,...,aliasX,clientN> <productPriority>**


**subclient <client>  <subclient1, subclient2,...,subclientN>**

This directive is used to define the subclients to which a given client can refers.
The following clients can be used in "key" and "clientAlias" directives::

  <client.subclient1>
  <client.subclient2>
  <...>
  <client.subclientN>

On reception, the bulletin will be linked in the tx queue of <client>. 
On transmission, the <client> must know how to use the <subclient?> part
to do appropriate delivery.

At this moment, the subclient directive is only used for a transceiver of type aftn.

ex: We will use a "client" with the name "toto" that is a transceiver of type aftn

::

  subclient toto AAAAAAAA,BBBBBBBB,CCCCCCCC
  clientAlias ab toto.AAAAAAAA toto.BBBBBBBB
  clientAlias abc AB,toto.CCCCCCCC
  key AACN01_ANIK ab,client1,client2
  key AACN02_ANIK client3,abc

When a px receiver receive an AACN01_ANIK bulletin, it will be linked in the tx queue of the 
transceiver named toto.

The transceiver named toto will delivers the AACN01_ANIK bulletin to the following address:
AAAAAAAA and BBBBBBBB (because the transceiver toto know how to use these subclient (in our 
example, these are AFTN addresses))


**Special directive for transceiver of type aftn** :

**aftnMap     <address|DEFAULT>     <prefix_header>**
This directive is only used on reception of message by a transceiver of type aftn.
If the text part of the message has no WMO Header, one will be created (thanks to the
aftnMap entries) for each destination address in the message.

If a destination address present in the message has no associated aftnMap directive, the prefix_header defined
by aftnMap DEFAULT will be used.

ex::
  aftnMap DEFAULT AACN30
  aftnMap AAAAAAAA AACN30
  aftnMap BBBBBBBB UANT30

A transceiver (type aftn) receive a message with no WMO header and the destinaton addresses are: AAAAAAAA, BBBBBBBBB, CCCCCCCC
Bulletins with following header will be created, ingested in the DB and linked to appropriate (following key directives) clients::

 AACN30 AAAA  (AAAA is the last 4 characters of AAAAAAAA)
 UANT30 BBBB  (BBBB is the last 4 characters of BBBBBBBB)
 AACN30 CCCC  (CCCC is the last 4 characters of CCCCCCCC) 

