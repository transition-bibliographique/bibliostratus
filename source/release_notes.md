### version 1.14
- Modules blancs (alignements) :
    - ajout d'un marqueur "&origin=bibliostratus" dans les requêtes sur le SRU BnF
	- bug : Exception ConnectionAbortedError mal levée

### version 1.13
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
