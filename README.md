Bibliostratus : STRatégie d'Alignement d'URIs pour la Transition bibliographique
==

* Le répertoire *source* contient le code développé en Python
* Le répertoire *bin* contient la dernière version compilée de l'exécutable, à télécharger et lancer directement pour utiliser le programme (le code source n'est pas forcément compilé à chaque modification)

**Alignement-donnees-bnf est une expérimentation** pour concevoir un ensemble de programmes permettant de s'aligner avec les données bibliographiques de la Bibliothèque nationale de France, afin de pouvoir bénéficier de leurs travaux de FRBRisation de masse.

Actuellement quatre modules sont en cours de développement, non encore finalisés :

* **marc2tables** : permet de charger en entrée l'extraction d'un catalogue de bibliothèque en Unimarc (formats iso2709 ou MarcXML). Le programme produit autant de fichiers tabulés (tableaux) qu'il y a de combinaisons Type de document / type de notice. Ces tableaux sont au format attendu pour le 2e programme
* **noticesbib2arkBnF** : exploitation des métadonnées de chaque notice bibliographique pour identifier la notice correspondante dans le catalogue BnF. Pour l'instant, on charge les ressources par type de document/notice (monographies imprimées, CD/DVD, périodiques, etc.). 
* **noticesaut2arkBnF** : son équivalent pour s'aligner avec les autorités (Personnes physiques et organisations), peu testé pour le moment
* **ark2records** : en entrée un fichier listant des ARK BnF, afin de récupérer les notices bibliographiques (+option avec notices d'autorité) correspondantes. Le format en sortie est pour l'instant du XML. Il devrait y avoir de l'iso2709 à terme.

Le fichier **main** encapsule les 4 précédents pour les concevoir comme autant d'étapes dans la transition bibliographique des établissements

Objectifs du programme
--

Le présupposé de ce projet est que les bibliothèques doivent, à terme, bénéficier de catalogues contenant des notices conformes au modèle FRBR-LRM. 
Afin d'éviter qu'elles ne transforment leurs notices de manière indépendantes, ou qu'elles achètent les notices transformées à des fournisseurs (ou pire, qu'elles acquièrent des logiciels qui calculent le regroupement de notices en arbres FRBR à la volée), les agences nationales proposent de faciliter la redistribution de leurs notices.
Mais pour cela, il faut que chaque bibliothèque ait fait un travail préalable d'*alignement* de son catalogue avec la BnF ou l'Abes, pour que chaque notice d'un catalogue local soit "lié" à la notice du réservoir national (catalogue général BnF ou Sudoc)

Mode d'emploi et tutoriels
--
[Voir le wiki](https://github.com/Lully/transbiblio/wiki "Consulter les pages du wiki sur Github")
