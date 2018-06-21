###version 1.20
juin 2018
- Tous modules : 
	- mise en forme PEP8 et flake8
	- initialisation d'un fichier de tests automatiques (à développer)
	- correction lignes lancement
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
