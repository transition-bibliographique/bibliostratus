### version 1.26
Février 2019
- Module blanc (alignements BIB):
	- Correction sur les informations de "méthode d'alignement" :
		- nettoyage des redondances
		- ajout d'informations pour identifier les alignements moins fiables
	- Option "recherche mots-clés dans le Sudoc"

### version 1.25
11 décembre 2018
- Module bleu (conversion de notices en tableaux):
	- Récupération de la zone 702 et 712 pour l'alignement d'autorités à partir de notices bibliographiques
- Module blanc (alignement BIB) :
	- performance : simplification des requêtes sur l'alignement tad2ark (alignement par mots-clés sur le SRU BnF)
	- création d'une classe Alignment_result, 1 fonction spécifique pour l'alignement d'une notice (distincte du code qui envoie l'info dans le fichier de résultats)
	- [gestion du code] ajout d'un test automatique de vérification du résultat d'un alignement
	- alignement Sudoc : directement en parsant le Sudoc et non plus via DoMyBiblio
	- alignement de périodiques : contrôle sur la recherche par ISSN dans le catalogue BnF : on vérifie que l'ISSN cherché est bien en 011$a (sinon, message d'alerte, mais on garde quand même l'identifiant)
	- modification des en-têtes de colonnes : "Identifiants" (incluant PPN et ARK) à la place de "ARK"
- Module rouge (export de notices)
	- Export correct des diacritiques dans le format XML
	- Option de réécriture des notices exportées : injection en 001 du numéro de notice locale (si fichier en entrée a 2 colonnes), et ajout d'une 003 et 033 pour les identifiants des agences

### version 1.24
6 novembre 2018
- Menu principal : remplacement "outil d'alignement BnF" par "outil d'alignement BnF/Abes"
- Module bleu (marc2tables) :
	- Le numéro FBRNF peut être trouvé en 035$a, ou à défaut en 801$h
- Modules blancs :
	- les contrôles sur les notices trouvées se font de la même manière pour idRef, le Sudoc et la BnF
- Module blanc (Alignement BIB) :
	- mise à jour du parsing HTML de DoMyBiblio, pour récupérer correctement le PPN
	- alignement par numéro commercial:
		- alignement sur bib.comref OR bib.ean
		- contrôle simplifié sur les ARK trouvés
	- mise en place d'un timeout de 5 secondes pour interroger DoMyBiblio
- Module blanc (Alignement AUT) :
	- option d'alignement sur les personnes / organisations
	- option d'alignement sur BnF / IdRef
- Module rouge (ark2records) :
	- meilleure préservation des chaînes de caractères (pas d'ajout de caractère d'échappement pour les apostrophes)
	- encodage UTF-8 : restitution correcte dans le XML des caractères diacritiques pour la plupart des entités XML échappées en Unicode (caractères non latins ne sont pas concernés, sauf l'alphabet grec)

### version 1.23
30 septembre 2018
- Modules bleu et blanc : prise en compte du type de document "Carte", encore en cours de développement
- Module bleu (marc2tables) : ajout du type "cartes" (préfixé "CAR"), avec récupération de l'échelle en dernière colonne
- Module blanc (alignement notices bib) :
	- Si alignement par ISBN, contrôle sur le numéro de volume (si renseigné)
	- Modification dans la manière d'ignorer les caractères accentués : 
	seules les lettres de l'alphabet latin avec diacritiques sont nettoyés
	les caractères arabes ou chinois en entrée sont laissés tels quels
	- Ajout de l'alignement sur les cartes : si c'est une carte, on cherche l'échelle dans "tous mots" (bib.anywhere)

### version 1.22
27/08/2018
- Module rouge (ark2records): Correction problèmes à l'export :
	- apostrophes converties en backslash-apostrophe par pymarc
	- apostrophe en fin de record Sudoc dans le format XML
	- possibilité de mettre une liste de PPN (n° notices Sudoc) : fichier dont les PPN sont préfixés "PPN" ou "http://www.sudoc.fr/" ou "http://www.idref.fr" (ou "https" dans les 2 cas)
- Module blanc (Alignements BIB):
	- Alignement par mots-clés (titre-auteur-date) dans le Sudoc :
		- recherche dans DoMyBiblio (par API, ou par HTML si un seul résultat) en mode "anywhere"
		(pas d'autre option de recherche)
		- puis analyse des notices trouvées : comparaison Mots du titre, mots Auteur, date
	- Améliorations sur les notices dont la date à moins de 4 chiffres
	
	
### version 1.21
juillet 2018
- Enrichissement des classes Bib_record et Aut_record
- Fichiers d'exemples consultables en local (et non en ligne)
- Module bleu : possibilité d'importer un fichier Marc21 (en modifiant le fichier main/files/preferences.json)
- favicône "Transition bibliographique" sur les fenêtres du module

### version 1.20
04/07/2018
- Tous modules : 
	- mise en forme PEP8 et flake8
	- initialisation d'un fichier de tests automatiques (à développer)
	- correction lignes lancement
- Module bleu (marc2tables):
	- option : modifier le fichier main\preferences.json pour avoir en entrée un fichier en marc21 plutôt qu'en unimarc
- Module blanc (alignement BIB):
	- Option BnF > Sudoc ou Sudoc > BnF
	- Création d'une classe Bib_record pour gérer les métadonnées en entrée
	Effets de bords possibles sur certaines parties du code (même si tous les impacts sont censés avoir été repris)
- Module rouge (ark2marc) :
	- extraction des notices à partir d'une liste de PPN (et pas seulement d'une liste d'ARK) ou d'une liste mélangée PPN + ARK
	


### version 1.19
08/06/2018
- Module bleu (marc > tables) :
	- option : exporter des métadonnées de notices bibliographiques en vue d'alignements avec des autorités (combinaison Titre-Auteur)
	- nouveau code AUD d'alignement pour les enregistrements sonores, distincts des enregistrements audiovisuels
	- Extraction biblio pour alignement d'autorités : ajout de la date de publication dans les critères d'alignement
- Module blanc (alignements bibliographiques):
	- Alignement sur l'ISSN : par expression exacte (option "adj" du SRU) et non tous mots (option "all")
	- Alignement Titre-Auteur-Date : contrôle sur la date pour vérifier qu'elle est bien présente en date d'édition (zone 100 ou 210$d).
	- fonction spécifique "par item". Facilite la prise en charge du même code par d'autres programmes (via API, interface web, etc.)
	- distinction entre enregistrements sonores (AUD) et vidéos (VID) : alignement sur l'un ou sur l'autre de ces deux types de documents
	- Contrôle sur la date : ajout de la date de copyright (302$a) en plus de la zone 100 et 210$d
- Module blanc (alignements autorités) :
	- Alignement à partir de métadonnées bibliographiques (combinaison Titre-Nom d'auteur) : ajout du critère "Date de publication"
	- Alignement à partir de métadonnées bibliographiques : Alignement sur nom de famille et sur prénom (et pas sur nom de famille seul)

### version 1.17
12/05/2018
Corrections diverses dans les formulaires : homogénéisation, etc.
- Module bleu (marc > tables) :
	- tables de ebooks générés comme les imprimés -> deviennent alignables
- Module blanc (Alignement AUT):
	- Si pas de date de début, alignement sur point d'accès + date de fin
- Module blanc (Alignements BIB et AUT):
	- Amélioration messages d'erreurs (colonnes manquantes en entrée)

### version 1.16
02/05/2018
- Module bleu (marc > tables):
	- Autorités : récupération des dates en 200$f si la zone à positions fixes 103 n'est pas renseignée
- Module blanc (alignement Autorités):
	- si un ISNI a été trouvé, le module vérifie si cet ISNI est dans le catalogue BnF. En effet la base ISNI connaît certaines formes d'auteurs absentes du catalogue BnF
	
### version 1.15
20/04/2018
- Tous modules :
	- Correction lien "Documentation en ligne"
- Module blanc (alignements BIB):
	- Quand la recherche ISBN n'a rien donné : relance d'une recherche ISBN partout dans la notice seulement si sa valeur nettoyée est d'au moins 10 caractères
	- Correction sur l'erreur ConnectionAbortedError
- Module blanc (alignements AUT):
	- nettoyage et formatage des ISNI avant requête dans le SRU
- Module rouge (marc > tableaux) :
	- Erreur d'encodage XML : message d'erreur + fichier en sortie
	- Prise en compte d'un fichier ISO2709 UTF-8 avec BOM : nettoyage du BOM (dans un fichier temporaire) avant d'extraire les notices

### version 1.14
17/04/2018
- Modules blancs (alignements) :
    - ajout d'un marqueur "&origin=bibliostratus" dans les requêtes sur le SRU BnF
	- bug : Exception ConnectionAbortedError mal levée

### version 1.13
16/04/2018
- Module blanc (alignement notices bibliographiques)
	- meilleur nettoyage de l'ISBN
- Module blanc (alignement notices d'autorité)
	- intégration code d'erreur 10053 (problème connexion à l'API)
- Module rouge (extraction de notices à partir d'une liste d'ARK):
	- correction pour extraction correcte d'ARK autorités
	
### version 1.12
14/04/2017
- Module blanc (alignements notices bibliographiques) : 
	- Recherche sur numéro commercial : si 0 résultat quand on cherche sur le critère bib.comref, le programme relançait la recherche partout dans la notice --> ce rebond est désactivé (le "numéro commercial" peut avoir des valeurs trop génériques, comme "208")
	- Correction bug sur les notices sans date pour les recherches Titre-Auteur-Date (la valeur vide de la date était remplacée par "*" qui faisait planter la requête SRU)

### version 1.11
- Module blanc (alignements notices bibliographiques) : 
	- Correction du format des fichiers en sortie quand l'option "Plusieurs fichiers est choisie"
	- Ajout d'un contrôle Titre sur l'alignement par numéro commercial
	- Correction de la fonction Nettoyage ISBN (les ponctuations, etc. n'étaient pas retirées en réalité jusque-là)


### version 1.10
**06/04/2018**

- Tous modules : ajout d'un bouton "Forum utilisateurs" > agoraBib
- Module bleu Marc > tables : 
	- récupération de toutes les autorités (certaines écrasées par d'autres)
	- rapidité : notices écrites directement dans les rapports en sortie au lieu de passer par une liste intermédiaire
	- Stats finales sur le terminal (volumétrie des notices ventilées)

### version 1.09
**04/04/2018**

- Module bleu Marc > tableaux : résolution d'autres problèmes d'encodage des fichiers en entrée

### version 1.08 
**01/04/2018**

- Module bleu Marc > tableaux : résolution des problèmes d'encodage :
désormais, les notices avec caractères non conformes UTF-8 ne font pas planter le programme
Elles constituent une liste à part dans un fichier "ALERT-notices-pb-encodage"
