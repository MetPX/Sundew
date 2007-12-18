import os,sys

class Language:
    """
        Liste de string constante selon la langue employee a l'execution du script pxRoute.
        Les langues fonctionnelles sont:
            - fr
            - en
            
        Pour changer la langue lors de l'execution, declarez la variable d'environnement PXROUTE_LANGUAGE avec 'fr' ou 'en' :
            export PXROUTE_LANGUAGE='en'    (pour anglais)
            export PXROUTE_LANGUAGE='fr'    (pour francais)
            
    """
    def __init__(self):
        defaultLanguage = "fr"
        if(os.environ.get("PXROUTE_LANGUAGE",defaultLanguage) == "fr"):
            Language.usage = "usage: %prog [options] -m (ajouter|enlever|recreer|chercher) NomClientOuAlias"
            Language.description = "Mise a jour de la table de routage pour un client ou pour un alias." \
                            " Pour plus d'information, voir la documentation (doc_pxRoute.txt)"
            
            Language.groupeFichiersTitre = "Les fichiers d'entrees"
            Language.groupeFichiersDescription = "Specification des fichiers d'entrees pour le fichier de la table de routage et le fichier bulletins"
            Language.groupeModesTitre = "Les modes"
            Language.groupeModesDescription = "Specification du mode d'acces au fichier de la table de routage." \
                                        " Cette option est obligatoire. Les particularites de chacun des modes" \
                                        " peuvent etre consultees dans la documentation (doc_pxRoute.txt)."
                                        
            Language.optVersionHelp = "Affichage de la version."
            Language.optHelpHelp = "Affichage de cette aide en ligne."
            Language.optUndoHelp = "Annule la derniere modification sur le fichier de la table de routage."
            Language.optRoutingHelp = "Nom du fichier de la table de routage. [defaut:pxRouting.conf]"
            Language.optBulletinsHelp = "Nom du fichier contenant une liste de bulletins."
            Language.choixModeAppend = "ajouter"
            Language.choixModeRemove = "enlever"
            Language.choixModeRenew = "recreer"
            Language.choixModeFind = "chercher"
            
            Language.optModeHelp = "Specification du mode d'acces (ajouter | enlever | recreer | chercher)."
            Language.optForceHelp = "Ne demande pas de confirmation a l'ecran."
            Language.optQuietHelp = "Retire l'affichage de l'information d'execution."
            Language.optInvertHelp = "Utilisation conjointe avec l'option '-b'. Inverse la liste de bulletins."
            Language.optTestHelp = "Test l'action en cours est affiche le resultat sur la sortie standard"
            
            Language.argsError = "Nombre d'argument incorrect."
            Language.argsErrorUndo = "Pas d'argument avec l'option '-u'."
            Language.modeError = "Specification du mode obligatoire (-m ajouter | -m enlever | -m recreer | -m chercher)."
            
            Language.optBulletinsMissing = "L'option '-b' doit etre utilise pour specifier une liste de bulletins."
            Language.optBulletinsProhibited = "L'option '-b' est proscrit dans le mode de recherche."
            Language.optInvertError = "L'option '-i' doit etre utilise conjointement avec un liste de bulletins (option '-b')."
            
            #Fichiers
            Language.fileOpenError = "Impossible d'ouvrir"
            Language.openAndRead = "Ouverture et lecture du fichier"
            Language.undoError = "Impossible d'annuler l'action precedente."
            
            #Mots simple
            Language.yes = "o"
            Language.no = "n"
            Language.forbidden = "Interdit"
            Language.backup = "Sauvegarde"
            Language.output = "Sortie"
            Language.double = "Doublons"
            Language.reserved = "Reserve"
            Language.confirm = "Confirmation"
            
            #Entrees valides et non-valides
            Language.noExtension = "Pas d'extension possible"
            Language.notInTable = "Pas dans la table de routage"
            Language.invalidFormat = "Format invalide"
            Language.findInvalidEntries = "Recherche des entrees non-valides ..."
            Language.invertValidEntries = "Inversion de la liste des bulletins valides ..."
            Language.validEntries = "entree(s) valide(s)"
            Language.invalidEntries = "entree(s) non valide(s)"
            Language.validBuletinsList = "#-------- Liste des bulletins valides --------"
            Language.nonvalidBuletinsList = "#-------- Liste des bulletins non-valides --------"
            Language.noValidEntries = "La liste de bulletins entree en parametre ne contient aucune entree valide"
            
            #Mode append
            Language.testAddInscription = "********** TEST - AJOUTER **********"
            Language.addSubscription = "MODE AJOUTER"
            
            #Mode remove
            Language.testCancelInscription = "********** TEST - ENLEVER **********"
            Language.cancelInscription = "MODE ENLEVER"
            Language.totalSupressAlias = "SUPPRESSION TOTALE DE L'ALIAS DU FICHIER DE ROUTAGE"
            Language.totalSupressClient = "SUPPRESSION TOTALE DU CLIENT DU FICHIER DE ROUTAGE"
            Language.totalSupress = "SUPPRESSION TOTALE"
            
            #Mode renew
            Language.testRenewInscription = "********** TEST - RECREER **********"
            Language.subscriptionRenew = "MODE RECREER"
            
            #Mode find
            Language.groupListAlias = "----- Liste des groupes (alias) dont l'alias fait partie -----"
            Language.clientListAlias = "----- Liste des clients faisant partie du groupe (alias) -----"
            Language.noAliasSubscriber = "Cette alias n'a aucun abonne!"
            Language.listBulletinsIntendForGroup = "----- Liste des bulletins destines au groupe (alias) -----"
            Language.groupListClient = "----- Liste des groupes (alias) dont le client fait partie -----"
            Language.listBulletinsIntendForClient = "----- Liste des bulletins destines au client -----"
            Language.noSubscriptionFor = "Aucune inscription pour"
            Language.aliasList = "----- LISTE DES ALIAS -----"
            Language.clientList = "----- LISTE DES CLIENTS -----"
            Language.allBulletinsList = "----- LISTE DE TOUS LES BULLETINS -----"
            
            #Pour tous les modes
            Language.clientNotExistTest = "Le client n'existe pas! Il sera cree pour le test!"
            Language.clientNotExistQuestion = "Le client n'existe pas! Voulez-vous le creer?"
            Language.modificationCalcul = "Calcul des modifications ... (Veuillez patienter)"
            Language.beforeModification = "AVANT MODIFICATION"
            Language.afterModification = "APRES MODIFICATION"
            Language.subscription = "INSCRIPTION"
            Language.cancellationSubscription = "DESINSCRIPTION"
            Language.bulletinsSubscription = "BULLETIN(S) INSCRIT"
            Language.newBulletins = "NOUVEAU(X) BULLETIN(S)"
            Language.noModificationToDo = "Aucune modification a apporter a la table de routage!"
            Language.individuallyRegistered = "TOUS LES CLIENTS ASSOCIES A CETTE ALIAS SERONT INSCRITS INDIVIDUELLEMENT AUX BULLETINS"
            Language.warning = "******************** AVERTISSEMENT ****************************"
            Language.nameNotClientOrAliasError = "Le nom passe en parametre n'est ni un client ni un alias.\nPour avoir la liste des clients et des alias, entrer la commande 'pxRoute -m chercher ?'"
            
            Language.recovery = "Recouvrement de la derniere modification ..."
            Language.lastModification = "Date et heure de la derniere modification: "
            
        elif(os.environ.get("PXROUTE_LANGUAGE",defaultLanguage) == "en"):
            Language.usage = "usage: %prog [options] -m (append|remove|renew|find) ClientOrAliasName"
            Language.description = "Update of the routing table for one client or one alias." \
                                   " For more information, see documentation (doc_pxRoute.txt)"
                    
            Language.groupeFichiersTitre = "Input files"
            Language.groupeFichiersDescription = "Name of the routing table and the bulletins file"
            Language.groupeModesTitre = "Modes"
            Language.groupeModesDescription = "Access modes for the routing table." \
                                        " This option is obligatory. For more informations about modes, see documentation (doc_pxRoute.txt)."

            Language.optVersionHelp = "Print version."
            Language.optHelpHelp = "Print this help."
            Language.optUndoHelp = "Undo the last modification on the routing table file."
            Language.optRoutingHelp = "Path and name of the routing table. [default:pxRouting.conf]"
            Language.optBulletinsHelp = "Path and name of the bulletins file."
            Language.choixModeAppend = "append"
            Language.choixModeRemove = "remove"
            Language.choixModeRenew = "renew"
            Language.choixModeFind = "find"
            
            Language.optModeHelp = "Access modes (append | remove | renew | find)."
            Language.optForceHelp = "No confirmation going to be displayed."
            Language.optQuietHelp = "Execution information is remove."
            Language.optInvertHelp = "Invert the bulletins list. The bulletins file have to be specified."
            Language.optTestHelp = "The action is to be tested. No modification will be made."
            
            Language.argsError = "Incorrect number of arguments."
            Language.argsErrorUndo = "No arguments with '-u' option."
            Language.modeError = "Specification of the mode is obligatory (-m append | -m remove | -m renew | -m find)."
            
            Language.optBulletinsMissing = "Option '-b' is missing."
            Language.optBulletinsProhibited = "Option '-b' is proscribed in finding mode."
            Language.optInvertError = "Option '-i' must be uses jointly with a list of bulletins (option '-b')."
            
            #Fichiers
            Language.fileOpenError = "Unable to open"
            Language.openAndRead = "Opening and reading file"
            Language.undoError = "Can't undo."
            
            #Mots simple
            Language.yes = "y"
            Language.no = "n"
            Language.forbidden = "Forbidden"
            Language.backup = "Backup"
            Language.output = "Output"
            Language.double = "Double"
            Language.reserved = "Reserved"
            Language.confirm = "Confirmation"
            
            #Entrees valides et non-valides
            Language.noExtension = "No extension available"
            Language.notInTable = "Not in routing table"
            Language.invalidFormat = "Invalid format"
            Language.findInvalidEntries = "Finding invalid entries ..."
            Language.invertValidEntries = "Inverting the list of valid entries ..."
            Language.validEntries = "Valid entries"
            Language.invalidEntries = "Invalid entries"
            Language.validBuletinsList = "#-------- List of valid bulletins --------"
            Language.nonvalidBuletinsList = "#-------- List of invalid bulletins --------"
            Language.noValidEntries = "No valid entries find in bulletins file"
            
            #Mode append
            Language.testAddInscription = "********** TEST - APPEND **********"
            Language.addSubscription = "MODE APPEND"
            
            #Mode remove
            Language.testCancelInscription = "********** TEST - REMOVE **********"
            Language.cancelInscription = "MODE REMOVE"
            Language.totalSupressAlias = "TOTAL SUPPRESSION OF THE ALIAS"
            Language.totalSupressClient = "TOTAL SUPPRESSION OF THE CLIENT"
            Language.totalSupress = "TOTAL SUPPRESSION"
            
            #Mode renew
            Language.testRenewInscription = "********** TEST - RENEW **********"
            Language.subscriptionRenew = "MODE RENEW"
            
            #Mode find
            Language.groupListAlias = "----- List groups (alias) of which the alias formed part -----"
            Language.clientListAlias = "----- List clients forming part of the group (alias) -----"
            Language.noAliasSubscriber = "This alias has no subscriber!"
            Language.listBulletinsIntendForGroup = "----- List bulletins intend for the group (alias) -----"
            Language.groupListClient = "----- List groups (alias) of which the client formed part -----"
            Language.listBulletinsIntendForClient = "----- List bulletins intend to the client -----"
            Language.noSubscriptionFor = "No subscriber for"
            Language.aliasList = "----- ALIAS LIST -----"
            Language.clientList = "----- CLIENTS LIST -----"
            Language.allBulletinsList = "----- ALL BULLETINS LIST -----"
            
            #Pour tous les modes
            Language.clientNotExistTest = "The client doesn't exist! It will be created for the test!"
            Language.clientNotExistQuestion = "The client doesn't exist! Do you want to create it?"
            Language.modificationCalcul = "Calculation of the modifications ... (please wait)"
            Language.beforeModification = "BEFORE MODIFICATION"
            Language.afterModification = "AFTER MODIFICATION"
            Language.subscription = "SUBSCRIPTION"
            Language.cancellationSubscription = "CANCELLATION OF SUBSCRIPTION"
            Language.bulletinsSubscription = "REGISTERED BULLETIN(S)"
            Language.newBulletins = "NEW BULLETIN(S)"
            Language.noModificationToDo = "No modification to do in the routing table!"
            Language.individuallyRegistered = "ALL CLIENTS ASSOCIATED WITH THIS ALIAS WILL BE REGISTERED INDIVIDUALLY"
            Language.warning = "*********************** WARNING *******************************"
            Language.nameNotClientOrAliasError = "The Name you give is not a client or an alias.\nIf you want the list of clients and alias, enter the folowing command: 'pxRoute -m find ?'"
            
            Language.recovery = "Recovery of the last modification ..."
            Language.lastModification = "Date et hour of last modification: "
        
        else:
            print os.environ["PXROUTE_LANGUAGE"],"n'est pas une langue reconnue!"
            print os.environ["PXROUTE_LANGUAGE"],"is not a recognized language!"
            sys.exit()