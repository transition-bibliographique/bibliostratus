transbiblio : Programmes pour accompagner la Transition bibliographique dans les bibliothèques françaises
==

transbiblio est une **expérimentation** pour concevoir un ensemble de programmes permettant de s'aligner avec les données bibliographiques de la Bibliothèque nationale de France, afin de pouvoir bénéficier de leurs travaux de FRBRisation de masse.

Actuellement quatre programmes sont en cours de développement **et très loin d'être finalisés** :

* marc2tables : permet de charger en entrée l'extraction d'un catalogue de bibliothèque en Unimarc (formats iso2709 ou MarcXML). Le programme produit autant de fichiers tabulés (tableaux) qu'il y a de combinaisons Type de document / type de notice. Ces tableaux sont au format attendu pour le 2e programme
* noticesbib2arkBnF : exploitation des métadonnées de chaque notice bibliographique pour identifier la notice correspondante dans le catalogue BnF. Pour l'instant, on charge les ressources par type de document/notice (monographies imprimées, CD/DVD, périodiques, etc.)
* ark2record : en entrée un fichier listant des ARK BnF, afin de récupérer les notices bibliographiques (+option avec notices d'autorité) correspondantes. Le format en sortie est pour l'instant du XML. Il devrait y avoir de l'iso2709 à terme.
* transbiblio : le programme qui encapsule les 3 précédents pour les concevoir comme autant d'étapes dans la transition bibliographique des établissements

Objectifs du programme
--

Le présupposé de ce projet est que les bibliothèques doivent, à terme, bénéficier de catalogues contenant des notices conformes au modèle FRBR-LRM. 
Afin d'éviter qu'elles ne transforment leurs notices de manière indépendantes, ou qu'elles achètent les notices transformées à des fournisseurs (ou pire, qu'elles acquièrent des logiciels qui calculent le regroupement de notices en arbres FRBR à la volée), les agences nationales proposent de faciliter la redistribution de leurs notices.
Mais pour cela, il faut que chaque bibliothèque ait fait un travail préalable d'*alignement* de son catalogue avec la BnF ou l'Abes, pour que chaque notice d'un catalogue local soit "lié" à la notice du réservoir national (catalogue général BnF ou Sudoc)