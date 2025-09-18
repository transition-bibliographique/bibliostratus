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


Compilation
__
Environnement virtuel (18/09/2025) :

Python 3.10.10 + fichier requirements.txt

Avant lancement de l'environnement virtuel, ajout dans le fichier Scripts\activate.bat des lignes :
set PATH=%VIRTUAL_ENV%\Scripts
set PYTHONPATH=%VIRTUAL_ENV%\Lib\site-packages;%VIRTUAL_ENV%\bibliostratus

Puis
pyinstaller main.spec

Contenu du fichier main.spec :
___

```

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[("dll/api-ms-win-core-console-l1-1-0.dll", "."), ("dll/api-ms-win-core-datetime-l1-1-0.dll", "."), ("dll/api-ms-win-core-debug-l1-1-0.dll", "."), ("dll/api-ms-win-core-errorhandling-l1-1-0.dll", "."), ("dll/api-ms-win-core-file-l1-1-0.dll", "."), ("dll/api-ms-win-core-file-l1-2-0.dll", "."), ("dll/api-ms-win-core-file-l2-1-0.dll", "."), ("dll/api-ms-win-core-handle-l1-1-0.dll", "."), ("dll/api-ms-win-core-heap-l1-1-0.dll", "."), ("dll/api-ms-win-core-interlocked-l1-1-0.dll", "."), ("dll/api-ms-win-core-libraryloader-l1-1-0.dll", "."), ("dll/api-ms-win-core-localization-l1-2-0.dll", "."), ("dll/api-ms-win-core-memory-l1-1-0.dll", "."), ("dll/api-ms-win-core-namedpipe-l1-1-0.dll", "."), ("dll/api-ms-win-core-processenvironment-l1-1-0.dll", "."), ("dll/api-ms-win-core-processthreads-l1-1-0.dll", "."), ("dll/api-ms-win-core-processthreads-l1-1-1.dll", "."), ("dll/api-ms-win-core-profile-l1-1-0.dll", "."), ("dll/api-ms-win-core-rtlsupport-l1-1-0.dll", "."), ("dll/api-ms-win-core-string-l1-1-0.dll", "."), ("dll/api-ms-win-core-synch-l1-1-0.dll", "."), ("dll/api-ms-win-core-synch-l1-2-0.dll", "."), ("dll/api-ms-win-core-sysinfo-l1-1-0.dll", "."), ("dll/api-ms-win-core-timezone-l1-1-0.dll", "."), ("dll/api-ms-win-core-util-l1-1-0.dll", "."), ("dll/api-ms-win-crt-conio-l1-1-0.dll", "."), ("dll/api-ms-win-crt-convert-l1-1-0.dll", "."), ("dll/api-ms-win-crt-environment-l1-1-0.dll", "."), ("dll/api-ms-win-crt-filesystem-l1-1-0.dll", "."), ("dll/api-ms-win-crt-heap-l1-1-0.dll", "."), ("dll/api-ms-win-crt-locale-l1-1-0.dll", "."), ("dll/api-ms-win-crt-math-l1-1-0.dll", "."), ("dll/api-ms-win-crt-multibyte-l1-1-0.dll", "."), ("dll/api-ms-win-crt-private-l1-1-0.dll", "."), ("dll/api-ms-win-crt-process-l1-1-0.dll", "."), ("dll/api-ms-win-crt-runtime-l1-1-0.dll", "."), ("dll/api-ms-win-crt-stdio-l1-1-0.dll", "."), ("dll/api-ms-win-crt-string-l1-1-0.dll", "."), ("dll/api-ms-win-crt-time-l1-1-0.dll", "."), ("dll/api-ms-win-crt-utility-l1-1-0.dll", "."), ("dll/bzip2.dll", "."), ("dll/concrt140.dll", "."), ("dll/ffi-7.dll", "."), ("dll/ffi-8.dll", "."), ("dll/ffi.dll", "."), ("dll/libbz2.dll", "."), ("dll/libcrypto-1_1-x64.dll", "."), ("dll/libffi-7.dll", "."), ("dll/liblzma.dll", "."), ("dll/libopenblas64__v0.3.23-293-gc2f4bdbb-gcc_10_3_0-2bde3a66a51006b2b53eb373ff767a3f.dll", "."), ("dll/libscipy_openblas64_-43e11ff0749b8cbe0a615c9cf6737e0e.dll", "."), ("dll/libssl-1_1-x64.dll", "."), ("dll/msvcp140-263139962577ecda4cd9469ca360a746.dll", "."), ("dll/msvcp140.dll", "."), ("dll/msvcp140_1.dll", "."), ("dll/msvcp140_2.dll", "."), ("dll/msvcp140_codecvt_ids.dll", "."), ("dll/python3.dll", "."), ("dll/python310.dll", "."), ("dll/sqlite3.dll", "."), ("dll/tcl86t.dll", "."), ("dll/tk86t.dll", "."), ("dll/ucrtbase.dll", "."), ("dll/vccorlib140.dll", "."), ("dll/vcomp140.dll", "."), ("dll/vcruntime140.dll", "."), ("dll/vcruntime140_1.dll", "."), ("dll/zlib.dll", ".")],
    datas=[],
    hiddenimports=["tkinter", "_tkinter"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['numpy', 'pandas', 'scipy', 'notebook', 'matplotlib'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
```