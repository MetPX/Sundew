=================
Bienvenue � MetPX
=================

MetPX - L��changeur de produits m�t�orologiques
===============================================

.. |Date| date::

Date: |Date|

[ English_ ]

.. _English: indexe.html


MetPX est une collection d�outils cr��e afin de faciliter l�acquisition, l�aiguillage, et la diss�mination 
de donn�es dans un contexte m�t�orologique. Il y a deux applications principales: Sundew et Sarracenia. 
MetPX-Sundew_ est ax� sur le support et la compatibilit� des syst�mes matures de Syst�me de t�l�communication
mondiale (STM) de l�Organisation mondiale de la m�t�o (OMM). Il acquiert, transforme, et livre des produits 
individuels, tandis que MetPX-Sarracenia_ adopte une nouvelle approche, et offre la copie 
compl�te (filtr�e) de l'arborescence source. Sarracenia abandonne la compatibilit� afin de r�pondre aux 
besoins actuels. Par contre, sundew demeure tout de m�me un lien essentiel aux 
anciens syst�mes.

[ liste de couriel (Anglais-Fran�ais): `metpx-devel <http://lists.sourceforge.net/lists/listinfo/metpx-devel>`_ , `metpx-commit <http://lists.sourceforge.net/lists/listinfo/metpx-commit>`_ ] 
[ projet: `Sourceforge <http://www.sourceforge.net/projects/metpx>`_ ]
[ Documentation_ ]
[ `T�l�chargement <http://sourceforge.net/project/showfiles.php?group_id=165061>`_ ]
[ `Acc�s au code source`_ ]
[ `Liens et R�f�rences`_ ]

[ liste de couriel (Anglais-Fran�ais): `metpx-devel <http://lists.sourceforge.net/lists/listinfo/metpx-devel>`_ , `metpx-commit <http://lists.sourceforge.net/lists/listinfo/metpx-commit>`_ ] 
[ Page principale de d�v�loppement: `Sourceforge <http://www.sourceforge.net/projects/metpx>`_ ]


MetPX-Sarracenia
================

MetPX-Sarracenia est un engin de copie et de distribution de donn�es qui utilise des technologies 
standards (tel que les services web et le courtier de messages AMQP) afin d'effectuer des transferts de 
donn�es en temps r�el tout en permettant une transparence de bout en bout. Alors que chaque commutateur 
Sundew est unique en soit, offrant des configurations sur mesure et permutations de donn�es multiples, 
Sarracenia cherche � maintenir l'int�grit� de la structure des donn�es, tel que propos�e et organis�e 
par la source, � travers tous les noeuds de la cha�ne, jusqu'� destination. Le client peut 
fournir des accus�s de r�ception qui se propagent en sens inverse jusqu'� la source. Tandis qu'un 
commutateur traditionnel �change les donn�es de point � point, Sarracenia permet le passage des 
donn�es d'un bout � l'autre du r�seau, tant dans une direction que dans l'autre.

Sarracenia, � sa plus simple expression, expose une arborescence de dossiers disponibles sur la toile 
("Web Accessible Folders"). Le temps de latence est une composante n�vralgique des applications m�t�o: les minutes, et parfois les secondes, sont compt�es. Les technologies standards, telles que ATOM et
RSS, sont des technologies qui consomment beaucoup de bande passante et de ressouces lorsqu'elles doivent r�pondre � ces contraintes. Les standards limitent la fr�quence maximale de v�rification de serveur � cinq minutes. 
Le protocol de s�quencement de messages avanc�s (Advanced Message Queuing Protocol, AMQP) est une 
approche beaucoup plus efficace pour la livraison d'annonces de nouveaux produits.

.. image:: f-ddsr-components.gif

Les sources annoncent la disponibilit� des donn�es, les commutateurs en font une copie 
et la diffusent � leurs clients. Quand les clients t�l�chargent des donn�es, ils ont l'option 
d'enregistrer cette transaction. Les enregistrements de transaction sont r�achemin�s aux sources, 
en passant par chaque syst�me du chemin inverse. Ceci permet aux sources de voir exactement le 
chemin qu'ont pris les donn�es pour se rendre aux clients.  Avec les syst�mes traditionnels 
d'�change de donn�es, chaque source peut seulement confirmer que le transfert vers le prochain 
noeud de la cha�ne a �t� compl�t�. Tout transfert subs�quent est � opaque � et tracer le 
cheminement d'un produit exige l'aide des administrateurs des syst�mes interm�diaires. Gr�ce au 
concept de Sarracenia, pr�voyant l'acheminement des enregistrements de transactions � travers 
le r�seau, la diffusion des donn�es devient transparente aux sources. Les diagnostiques en 
sont aussi grandement simplifi�s.

Tandis que Sundew supporte plusieurs protocoles et formats de la m�t�orologie,
Sarracenia se retire de cette sp�cificit� et g�n�ralise son approche, ce qui lui permet d'�tre utile pour d�autres domaines scientifiques. Le client prototype, dd_subscribe, est en service depuis
2013 et implante une grande partie des fonctions de consommateurs de donn�es. Elle est la seule composante
dans les paquets Debian actuels. Le reste des composantes devraient �tre disponibles � l'automne 2015.

Sarracenia est plus simple que Sundew, peu importe l'utilisateur: op�rateur, d�v�loppeur, analyste, 
source et consommateurs de donn�es. Bien qu�il impose une interface pour l�acc�s au 
donn�es, Sarracenia est compl�tement g�n�rique et portable.  Il sera disponible sur n�importe 
quelle plateforme moderne (GNU/Linux, Windows, Apple)

Pourquoi ne pas utiliser RSync?
===============================

Il existe multiples solutions pour la copie de donn�es, pourquoi en inventer une autre? Rsync et la
plupart des autres outils sont 1:1, ils comparent source et destination.  Sarracenia, bien qu�il ne sert
pas de multi-cast, est orient� vers la livraison � de multiples clients en temps r��l. La synchronization 
RSync se fait via la communication de l�arborescences, en calculant des signatures pour chaque fichier, pour
chaque client. Pour les arborescences importantes, comprennant plusieurs clients, ces calculs et transactions deviennent on�reuses, limitant la fr�quence de mise � jour et le nombre de clients peuvant �tre support�s. Sarracenia �vite le parcours des arborescences, et les processus qui �crivent les fichiers calculent les checksum une fois seulement, afin d'�tre utilis� directement par tous les intervenants. Ces deux am�liorations rendent Sarracenia beaucoup plus efficace que RSync dans le cas d'arborescences imposantes comprenant l'ajout fr�quent de fichiers. LSync est un outil qui utilise INOTIFY sur GNU/Linux pour avoir une notification en temps r�el, mais la gestion 
des checksum et la communication des enregistrements � travers le r�seau n'existent pas. De plus,
LSync n�est pas interop�rable avec d'autres syst�mes d'exploitation.

 
RSync est �galement une solution point � point. Sarracenia mise sur la "transitivit�", c'est-�-dire sur la capacit� d'encha�ner plusieurs commutateurs de produits et de s�assurer que les accus�es de r�ception se propagent jusqu��
la source. Par contre, l�implantation initiale de sarracenia ne traite pas des deltas (changement de 
contenu de fichiers existants) et va t�l�charger le contenu complet a chaque annonce. On �tudie pr�sentement
le cas des deltas, et l�utilisation de l�algorithm RSync via l�outil zsync est en consid�ration.


MetPX-Sundew
============


MetPX-Sundew est un syst�me de commutation de messages sur les circuits TCP/IP du 
Syst�me de t�l�communications mondiales (STM) de l'Organisation mondial de 
la m�t�orologie (l'`OMM <http://www.wmo.int>`_ ) Pour certaines fonctionnalit�s, le syst�me est d�j� d'une qualit� op�rationelle et est utilis� au Centre m�t�orologique canadien en tant que noyau national de commutation de bulletins
et fichiers (satelites, radars, produits num�riques). le logiciel permet
la participation canadienne � des projets internationaux tel que 

`Unidata <http://www.unidata.ucar.edu/>`_ et `TIGGE <http://tigge.ecmwf.int/>`_ via une passerelle 
� LDM, ainsi que `NAEFS <http://www.emc.ncep.noaa.gov/gmb/ens/NAEFS.html>`_ via le transfert de fichiers.
MetPX se d�marque par sa capacit� de routage d�taill� a tr�s faible latence et � haute vitesse.
Le projet se veut une sorte de plateforme partag� et universelle pour les t�l�communications via STM, sur 
le mod�le d�Apache pour les serveurs web.

Types de connections TCP/IP:

 - AM (socket prori�taire aux syst�mes canadiens)
 - sockets OMM (voir le manuel 386) 
 - FTP pour le transport, pas de nomenclature de l'OMM pour l�instant (facile � ajouter)
 - SFTP (but similaire au FTP, mais avec plus de s�curit�)
 - AFTN/IP passerelle (Version NavCanada du "Aviation Fixed Telecommunications Network", normalement bas�e sur du X.25)
 - AMQP (protocol ouvert de messagerie provenant du monde des affaires)

Fonctionnalit�s:

 - Routage d�taill� (.... avec 30&nbsp;000 entr�es distinctes dans la table de routage)
 - modalit�s de commutation commun entre les fichiers et les bulletins.
 - Temps de commutation inf�rieur � une seconde (avec 28&nbsp;000 entr�es)
 - Commutation et livraison � haute vitesse (�tait plus de 300 messages par seconde l'an dernier) 
   mais il est � noter que plusieurs fonctionnalit�s ont �t� ajout�s qui pourraient 
   affecter la vitesse. Il serait n�cessaire de re-v�rifier cet aspect.
 - Aucune limite de taille des messages.
 - Segmentation de messages (pour protocols tels que AM &amp; OMM qui ont de telles limites)
 - Supression des duplicata (� l'envoi)
 - AFTN/IP canadien.
 - collecte de bulletins
 - m�canisme de filtrage g�n�ral (les collections seront adapt�es � ce m�canisme) 

Il y a actuellement trois modules dans ce projet et un quatri�me est � l'�tude. 
Les modules de MetPX sont nomm�s selon des noms d'esp�ces de plantes 
en voie de disparition au Canada. (voir `Esp�ces en p�ril <http://www.especesenperil.gc.ca>`_ )

 - sundew: module de commutation de l'OMM
 - columbo: module de surveillance, pour sundew et PDS
 - stats: module de collecte et affichages de statistiques.
 

Plateforme: GNU/Linux d�riv� de Debian (Sarge, Etch, Lenny, Ubuntu...) N�importe quel syst�me GNU/Linux moderne (2.6 vanille ou bien 2.4 avec plusieurs rustines). Python version 2.3 o� plus r�cent)

license: GPLv2

le code source en d�v�loppement est disponible en utilisant subversion via: git clone git://git.code.sf.net/p/metpx/git metpx
( acc�s anonyme pour fins de lecture. )

Documentation
=============

La documentation en fran�ais n�est pas disponible pour le moment.
Ca va �tre traduite une fois qu�on aura stabilis� une premi�re �dition en anglais.

Veuillez consulter la `Documentation anglaise <indexe.html#Documentation>`_ pour l�instant

T�l�chargement
==============

`T�l�chargement <http://sourceforge.net/project/showfiles.php?group_id=165061>`_

Le module Sundew est relativement stable et peut �tre t�l�charg� du site 
de Sourceforge.  Les autres modules ne sont pas assez matures pour �tre distribu�s.

Acc�s au code source
====================

Pr�sentement, les installations sont faites une � la fois, � partir du code source.
Le d�veloppement se fait dans le branche �trunk� (terminologie de subversion.) Quand
on installe, on cr�e une branche de maintenance pour l�installation. Il y a des 
fichiers README et INSTALL qui peuvent donner des indices pour arriver a une 
installation initiale.

Il est � noter qu'il est assez critique d�installer des �jobs cron� (mr-clean 
en particulier) parce que le cas �cheant, le serveur va tranquillement rouler 
de plus en plus lentement jusqu�au moment o� il arr�te carr�ment. �a serait 
optimal de vous inscrire � la liste de couriel (fran�ais, bienvenu, peut-�tre 
m�me pr�f�r�...) ce qui nous donnera des indices pour des t�ches futures et de
potentielles collaborations.

Sentez-vous libre de prendre une copie de la version � jour du code source via::

 svn co https://svn.sourceforge.net/svnroot/metpx/trunk

(disponible anonymement en lecture seulement.) D�autre versions sont disponibles 
en t�l�chargeant une branche sp�cifique.

AMQP
====

 - AMQP est un protocol standard pour l'�change de messages qui origine du domaine de la finance.  
   AMQP est apparu en 2007 et a graduellement gagn� en maturit�. Il y a aujourd'hui plusieurs 
   impl�mentations de ce protocole en logiciel libre.  AMQP offre une m�thode pour le transport des 
   messages JAVA, mais il n'est pas d�di� uniquement � ce langage. Sa neutralit� envers les diff�rents 
   langages de programmation facilite l'interop�rabilit� avec les fournisseurs JMS, sans se limiter 
   � JAVA. Le langage AMQP et ses messages sont neutres. Certaines impl�mentations utilisent 
   python, C++ et ruby, tandis que les fournisseurs de JMS sont fortement orient�s JAVA.
 - `www.amqp.org <http://www.amqp.org>`_ D�finition d�AMQP.
 - `www.openamq.org <http://www.openamq.org>`_ pr�mi�re Implantation de JPMorganChase
 - `www.rabbitmq.com <http://www.rabbitmq.com>`_ Une autre implantatation. Celle utilis� par le pr�sent projet.
 - `Apache Qpid <http://cwiki.apache.org/qpid>`_ Encore une autre implantation.
 - `Apache ActiveMQ <http://activemq.apache.org>`_ Un "fournisseur JMS" avec la capacit� d�utiliser AMQP comme transport. 

Sarracenia utilise les concepts de � courtier de messages � et � �changes bas�s sur le sujet � qui, 
ant�rieurement � la version 1.0, �taient standards dans AMQP. A partir de la version 1.0, le comit� 
des standards AMQP a d�cid� de retirer ces aspects avec l'id�e de les r�introduire dans le futur. 
D� � cette d�cision, Sarracenia d�pend des versions pr� 1.0 de AMQP, tel que � rabbitmq �.

Liens et R�f�rences
===================

D�autres projets et produits qui sont vaguement dans une domaine similaire. Les mentions ici ne doivent pas �tre interpret�es comme des recommandations.

 - le manuel WMO 386, r�f�rence pour le domaine.(version sans doute p�rim�e est `WMO-386 <WMO-386.pdf>`_ ici. Voir http://www.wmo.int pour une version plus r�cente.
 - `http://www.unidata.ucar.edu/software/ldm <http://www.unidata.ucar.edu/software/ldm>`_ - Local Data 
   Manager. LDM inclut un protocol r�sautique, et veut fondamentalement �changer des donn�es avec d�autres serveurs LDM. 
   Ce logiciel a servi comme inspiration de plusieurs fa�ons. Au d�but des ann�es 2000, nous avions �tudi� le protocol 
   pour les besoins du CMC et identifi� des charact�ristiques qui le rendaient inapte � notre application.  Par 
   contre, il y avait un effort �NLDM� qui avait remplac� le protocol r�sautique de 
   LDM par un protocol standard (NNTP.) L��ffort a sombr�, par contre, �a a servi comme inspiration pour la s�paration de le domaine m�t�orologique de protocol de t�l�communication, ce qui a �t� reprit philosophiquement par MetPX. 
 - `http://www.dwd.de/AFD <http://www.dwd.de/AFD>`_ - Automatic File Distributor - du Service m�t�orologique allemand. Aiguilleur de fichiers dans le protocol au choix de l�usager. Similaire � MetPX en philosophie
 - `Corrobor <http://www.corobor.com>`_ - commutateur OMM commerciale.
 - `Netsys <http://www.netsys.co.za>`_ - commutateur OMM commerciale.
 - `IBLSoft <http://www.iblsoft.com>`_ - commutateur OMM commerciale.
 - Quelques autres logiciels de transfert de fichiers: Standard Networks Move IT DMZ, Softlink B-HUB & 
   FEST, Globalscape EFT Server, Axway XFB, Primeur Spazio, Tumbleweed Secure File Transfer, Messageway
 - `Rsync <https://rsync.samba.org/>`_ engin de transfert incrementale rapide.
 - `Lsync <https://code.google.com/p/lsyncd>`_ engin de synchronization en temps reel.
 - `Zsync <http://zsync.moria.org.uk>`_ RSync sur HTTP.


