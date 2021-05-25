Bibliostratus : STRatégie d'Alignement d'URIs pour la Transition bibliographique
==

[![alt Télécharger Bibliostratus : Windows 64 bit - Dernière version](https://raw.githubusercontent.com/Transition-bibliographique/bibliostratus/master/img/bouton_telecharger_bibliostratus.png)](https://github.com/Transition-bibliographique/bibliostratus/raw/master/bin/bibliostratus_latest_win64_py3.6.zip)

[Autres configurations](https://github.com/Transition-bibliographique/bibliostratus/tree/master/bin)

* Le répertoire *bibliostratus* contient le code développé en Python
* Le répertoire *bin* contient la dernière version compilée de l'exécutable, à télécharger et lancer directement pour utiliser le programme (le code source n'est pas forcément compilé à chaque modification)

Bibliostratus a pour objectif de proposer un ensemble de fonctions permettant de s'aligner avec les données bibliographiques de la [Bibliothèque nationale de France](http://www.bnf.fr), afin de pouvoir bénéficier de leurs travaux de FRBRisation de masse.

Actuellement quatre modules sont en cours de développement, non encore finalisés :

* **Bleu (conversion de notices MARC en tableurs)** : permet de charger en entrée l'extraction d'un catalogue de bibliothèque en Unimarc (formats iso2709 ou MarcXML). Le programme produit autant de fichiers tabulés (tableaux) qu'il y a de combinaisons Type de document / type de notice. Ces tableaux sont au format attendu pour le 2e programme
* **Blanc (alignement de notices bibliographiques)** : exploitation des métadonnées de chaque notice bibliographique pour identifier la notice correspondante dans le catalogue BnF ou le Sudoc. On charge les ressources par type de document/notice (monographies imprimées, CD/DVD, périodiques, etc.). 
* **Blanc (alignement de notices d'autorité)** : son équivalent pour s'aligner avec les autorités (Personnes physiques et organisations), avec la BnF ou IdRef
* **Rouge (extraction de notices Marc BnF ou Abes)** : en entrée un fichier listant des ARK BnF, ou des PPN Sudoc/IdRef, afin de récupérer les notices bibliographiques (+option avec notices d'autorité) correspondantes. Le format en sortie est pour l'instant du XML. Il devrait y avoir de l'iso2709 à terme.


Objectifs du programme
--

Le présupposé de ce projet est que les bibliothèques doivent, à terme, bénéficier de catalogues contenant des notices conformes au modèle FRBR-LRM. 
Afin d'éviter qu'elles ne transforment leurs notices de manière indépendantes, ou qu'elles achètent les notices transformées à des fournisseurs (ou pire, qu'elles acquièrent des logiciels qui calculent le regroupement de notices en arbres FRBR à la volée), les agences nationales proposent de faciliter la redistribution de leurs notices.
Mais pour cela, il faut que chaque bibliothèque ait fait un travail préalable d'*alignement* de son catalogue avec la BnF ou l'Abes, pour que chaque notice d'un catalogue local soit "lié" à la notice du réservoir national (catalogue général BnF ou Sudoc)

Mode d'emploi et tutoriels
--
* [Voir le wiki](https://github.com/Transition-bibliographique/bibliostratus/wiki "Consulter les pages du wiki sur Github")
* [Tutoriels vidéo](https://www.transition-bibliographique.fr/systemes-et-donnees/tutoriels-video/)
* [Support de formation : Prezi](https://prezi.com/view/OHjLk8kA9skbEP3bJirl/)
* [Erreurs fréquentes](https://www.transition-bibliographique.fr/systemes-et-donnees/erreurs-frequentes/)
* [Consulter le forum utilisateurs](http://www.agorabib.fr/topic/3317-bibliostratus-mettre-en-correspondance-ses-notices-avec-celles-de-la-bnf/ "topic Agorabib")
* [Consulter la documentation technique](https://github.com/Transition-bibliographique/bibliostratus/tree/master/doc)
* [Installer Bibliostratus sur Linux](INSTALL.md)

* [Notes de version](bibliostratus/release_notes.md)
