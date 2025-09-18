## Télécharger la version compilée

Les noms des fichiers contiennent :
- le nom du logiciel
- le numéro de version
- (avec éventuellement la mention *RC* pour *release candidate*, qui sont des versions qui ajoutent de nouvelles fonctions mais qui n'ont pas été complètement débugguées)
- le système d'exploitation (windows 64 bits, windows 32 bits)
- la version Python utilisée

Depuis la migration vers Python 3.10, les nouveaux paquets suivent la convention
`bibliostratus_<version>_win64_py3.10.zip`. Les scripts batch
`launch_pyinstaller_winXX.bat` se chargent automatiquement de cette nouvelle
nomination après la compilation avec PyInstaller.

Cliquez sur le nom du fichier qui vous convient, puis sur le bouton Download

![Télécharger le logiciel](https://raw.githubusercontent.com/Transition-bibliographique/bibliostratus/master/img/telecharger_logiciel.png)



Le fichier zip contient un dossier toujours intitulé de la même manière (quelle que soit la version) : "bibliostratus"
A chaque mise à jour, vous pouvez ainsi facilement écraser le contenu du dossier précédemment récupéré

![Décompresser et installer le logiciel](https://raw.githubusercontent.com/Transition-bibliographique/bibliostratus/master/img/decompression_logiciel.png)


**Ce dossier bibliostratus sert de répertoire de travail** : c'est directement dans ce dossier que le logiciel dépose les fichiers qu'il produit

Ce dossier contient
- un fichier **bibliostratus.bat** sur lequel il faut double-cliquer pour lancer le programme.
- un répertoire *main* avec tous les programmes (inutile d'ouvrir ce répertoire)

## Pour lancer le programme

1. Décompresser le fichier téléchargé. Cela crée un dossier bibliostratus
2. Déposer ce dossier où vous voulez sur votre ordinateur
3. Y mettre aussi vos fichiers de travail (extraction du catalogue, tableaux de jeux de données)
4. Double-cliquer sur le fichier alignements-donnees-bnf.bat
