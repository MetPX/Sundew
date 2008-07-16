"""
#############################################################################################
# Name: pxRetransLanguage.py
#
# Author: Daniel Lemay
#
# Date: 2007-10-10
#
# Description: French and English dictionaries for pxRetrans application
#
#############################################################################################
"""

english = {
'lang':'eng',

# Menu
'80-':100*'-',
'HELP':'HELP',
'printMenu':'print this menu',
'listMenu':'list matching bulletins',
'listOptionsMenu':'list search options',
'retransmitMenu':'retransmit selected bulletins (ex: rtx 1-18,21,23,35-37 )',
'resetMenu':'reset search options',
'getFlowNames':"get all flow's name",
'getClientNames': "get all client's name",
'getSourceNames': "get all source's name",
'getClusterFlowNames':"get all flow's name on a given cluster",
'getClusterClientNames': "get all client's name on a given cluster",
'getClusterSourceNames': "get all source's name on a given cluster",
'getProdSources': "get product's sources",
'getProdClients': "get product's clients",
'getProdFreqs': "get product's frequencies",
'getPotentialClients': "get all potential clients (search with IP or hostname)",
'quitMenu':'quit',

# Usage
'progDesc':'This program is used to retransmit files on px clusters',
'isInMinutes':'is in minutes',
'example':'example',
'groupNote':'Note: If you are on a frontend, you must set a group (ex: --group px | --group pds | --group pxatx)',
'mustSetAGroup': 'You must set a group (ex: --group px | --group pds | --group pxatx)',

# Options
'verboseHelp':'verbose mode',
'quietHelp':'quiet mode',
'spanHelp': 'span in minutes (default: 240) ex: --span 30, -s 30',
'offsetHelp': 'offset in minutes (default: 0) ex: --offset "7*24*60", -o "7*24*60"',
'startDateHelp': 'start date (format: YYYY-MM-DD HH:mm:ss, default: "") ex: --startDate "2007-10-09 21:35:59"',
'endDateHelp': 'end date (format: YYYY-MM-DD HH:mm:ss, default: "") ex: --endDate "2007-10-09 23:35:59"',
'sourcesHelp': 'defined sources used to find files (ex: --sources "ncp1,ncp2")',
#'clientsHelp': 'clients to which files will be retransmitted (ex: --clients "awws1,awws2")',
'clientsHelp': 'client to which files will be retransmitted (ex: --clients awws)',
'regexHelp': 'general regex to match files',
'timestampHelp': 'timestamp to add to files (ex: --timestamp 20070928201758)', 
'groupHelp':'same groups as those declared in /etc/dsh/group (ex: --group pds | -g px)',
'scpHelp': "scp the 'retransmit' file (ex: --scp lvs1-op)",
'basenameHelp': "print only the basename of the files",
'prioHelp': "define retransmission priority (default is 0, -1 is original priority)",
'interHelp':'interactive mode',

# Listing
'listAll':'List all bulletins matching search criterias (including first and last bulletins):',
'searchInterval': 'Search interval: [%s, %s]',
'numBullToRetrans':'Number of bulletins matching search criterias: %s bulletin%s',
'firstBullToRetrans': 'First bulletin matching search criterias: %s %s %s',
'lastBullToRetrans': 'Last bulletin matching search criterias: %s %s %s',

# Execution
'problem':'problem',
'startDateOlder':'Your startDate is older than you endDate!',
'badOptions': 'Bad combination of options, read help (h)',
'wrong-': '%s is wrong because %s > %s',
'createAListFirst': 'You must first create a list (l)',
'createANewList': 'You must create a new list (l) because some options has been changed',
'noClients': 'Only for viewing, no clients',
'retransmittedWithPrio': 'Note: files will be retransmitted with priority %s', 
'forClient':'for client',
'onlyForViewing': '(only for viewing, no clients)',
'optionMustBePresent':'Option --%s must be set',
'optionsMustBePresent': 'Option --%s or --%s must be set',
'youAreOnAFrontend':'(you are on a "frontend")',
'noSourceMeanOneClient': 'Since no sources are set, you must have only 1 client => retransmission by client',
'youAreOn': 'you are on %s (no master repository)',
'searchOnClusters':'Search for clients on the following clusters: %s',
'searchLocally':'Search for clients locally only (%s)',
'potentialClients':'Potential clients:',
'noResults':'No results',
'searchOnXMachines':'Search on cluster %s (%i machine(s)): %s',
'onlyAvailableOnFrontend':"This function is only available on frontends",

# Errors
'flowTypeNone': 'Flow type is None: probably means that no configuration\n\
file exists for %s on %s',
'notRetransmitted': "will not be retransmitted",
'cannotCopyDBNameInQueueName':"PROBLEM: Copy from DB to client's queue doesn't work.",
'copyDBNameInQueueName': "%s:%s has been copied in %s",
'fileStillInClientQueue':"File is still in client's queue after %i seconds.\n\
You will have to check in the client's log (%s)",
'badClientName': "Bad client name or more than 1 client",
'noMachineInThisGroup': "There is no machine in this group (%s)",
'commandNotAvailable': "This command is not available on a backend (use %s instead)",
'possibleProblemWithFilename': "Unable to construct DB path from: %s\n\
Probably a problem with filename's syntax.",
}


french = {
'lang':'fra',

# Menu
'80-': 100*'-',
'HELP':'AIDE',
'printMenu':'imprimer ce menu',
'listMenu':'lister les bulletins selectionnes',
'listOptionsMenu':'lister les options de recherche',
'retransmitMenu':'retransmettre les bulletins selectionnes (ex: rtx 1-18,21,23,35-37 )',
'resetMenu':'reinitialiser les options de recherche',
'getFlowNames':'obtenir le nom de tous les flots',
'getClientNames': 'obtenir le nom de tous les clients',
'getSourceNames': 'obtenir le nom de toutes les sources',
'getClusterFlowNames':'obtenir le nom de tous les flots sur une grappe donnee',
'getClusterClientNames': 'obtenir le nom de tous les clients sur une grappe donnee',
'getClusterSourceNames': 'obtenir le nom de toutes les sources sur une grappe donnee',
'getProdSources': "obtenir le nom de toutes les sources du produit",
'getProdClients': "obtenir le nom de tous les clients du produit",
'getProdFreqs': "obtenir toutes les frequences du produit",
'getPotentialClients': "obtenir tous les clients potentiels grace a l'adresse IP ou au nom de machine",
'quitMenu':'quitter',

# Usage
'progDesc':'Ce programme sert a retransmettre des fichiers sur les grappes px',
'isInMinutes':'est en minutes',
'example':'exemple',
'groupNote':'Note: Si vous etes sur un frontend, vous devez fixer un groupe (ex: --group px | --group pds | --group pxatx)',
'mustSetAGroup': 'Vous devez fixer un groupe (ex: --group px | --group pds | --group pxatx)',

# Options
'verboseHelp':'mode verbeux',
'quietHelp':'mode silencieux',
'spanHelp': 'etendue en minutes (defaut: 240) ex: --span 30, -s 30',
'offsetHelp': 'decalage en minutes (defaut: 0) ex: --offset "7*24*60", -o "7*24*60"',
'startDateHelp': 'date de depart (format: AAAA-MM-JJ HH:mm:ss, defaut: "") ex: --startDate "2007-10-09 21:35:59"',
'endDateHelp': 'date de fin (format: AAAA-MM-JJ HH:mm:ss, defaut: "") ex: --endDate "2007-10-09 23:35:59"',
'sourcesHelp': 'sources utilisees afin de trouver les fichiers a retransmettre (ex: --sources "ncp1,ncp2")',
#'clientsHelp': 'clients auxquels les fichiers seront retransmis (ex: --clients "awws1,awws2")',
'clientsHelp': 'client auquel les fichiers seront retransmis (ex: --clients awws)',
'regexHelp': 'regex generale afin de selectionner les correspondances',
'timestampHelp': 'estampille de temps ajoutee au nom des fichiers (ex: --timestamp 20070928201758)',
'groupHelp':'memes groupes que ceux declares dans /etc/dsh/group (ex: --group pds | -g px)',
'scpHelp': 'scp le fichier contenant la liste des fichiers a retransmettre (ex: --scp lvs1-op)',
'basenameHelp': 'imprime seulement le nom de base des fichiers',
'prioHelp': 'fixe la priorite de retransmission (le defaut est 0, -1 est la priorite originale)',
'interHelp':'mode interactif',

# Listing 
'listAll':'Liste de tous les bulletins correspondant aux criteres de recherche (incluant le premier et le dernier):',
'searchInterval': 'Intervalle de recherche: [%s, %s]',
'numBullToRetrans':'Nombre de bulletins correspondant aux criteres de recherche: %s bulletin%s',
'firstBullToRetrans': 'Premier bulletin correspondant aux criteres de recherche: %s %s %s',
'lastBullToRetrans': 'Dernier bulletin correspondant aux criteres de recherche: %s %s %s',

# Execution
'problem':'problem',
'startDateOlder':'Votre startDate est plus vieille que votre endDate!',
'badOptions': "Mauvaise combinaison d'options, lisez l'aide (h)",
'wrong-': "%s n'est pas bon car %s > %s",
'createAListFirst': 'Vous devez creer une liste (l) en premier ',
'createANewList': 'Vous devez creer une nouvelle liste (l) car certaines options ont changees de valeur',
'noClients': 'Seulement pour visualisation, pas de clients',
'retransmittedWithPrio': 'Note: les fichiers seront retransmis avec la priorite %s', 
'forClient':'pour le client',
'onlyForViewing': '(seulement pour visualisation, pas de clients)',
'optionMustBePresent':"L'option --%s doit etre fixee",
'optionsMustBePresent': "L'option --%s ou --%s doit etre fixee",
'youAreOnAFrontend':'(vous etes sur un "frontend")',
'noSourceMeanOneClient': "Etant donne que vous n'avez pas defini de sources, vous devez avoir 1 seul client => retransmission par client",
'youAreOn': 'Vous etes sur %s (pas de depot maitre)',
'searchOnClusters':'Recherche de clients sur les grappes suivantes: %s',
'searchLocally':'Recherche de clients localement seulement (%s)',
'potentialClients':'Clients potentiels:',
'noResults':'Aucun resultat',
'searchOnXMachines':'Recherche sur la grappe %s (%i machine(s)): %s',
'onlyAvailableOnFrontend':"Cette fonction n'est disponible que sur les 'frontends'",

# Errors
'flowTypeNone': "Le type du flot est None: signifie probablement qu'il n'existe pas\n\
de fichier de configuration pour %s sur %s",
'notRetransmitted': "ne sera pas retransmis",
'cannotCopyDBNameInQueueName':'PROBLEME: Copie de la DB a la queue du client ne fonctionne pas',
'copyDBNameInQueueName': "%s:%s a ete copie dans %s",
'fileStillInClientQueue':"Le fichier est encore dans la queue du client apres %i secondes.\n\
Vous allez devoir verifier dans le log du client (%s)",
'badClientName': "Mauvais nom de client ou plus d'un client",
'noMachineInThisGroup': "Il n'y a pas de machines dans ce groupe (%s)",
'commandNotAvailable': "Cette commande n'est pas disponible sur un backend (utilisez %s a la place)",
'possibleProblemWithFilename': 'Incapable de construire le chemin a la base de donnees a partir de: %s\n\
Probablement un probleme avec la syntaxe du nom de fichier.',
}
