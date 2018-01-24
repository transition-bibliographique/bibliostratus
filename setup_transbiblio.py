# -*- coding: utf-8 -*-
"""Fichier d'installation du script ExtractionCatalogueBnF_code.py."""
#Commande Windows à utiliser : D:\BNF0017855\Programmes\Anaconda2\python setup_transbiblio.py build

from cx_Freeze import setup, Executable
import os


path_anaconda = r"D:\BNF0017855\Programmes\Anaconda2"
if (path_anaconda[-1] != "\\"):
    path_anaconda = path_anaconda + "\\"

os.environ['TCL_LIBRARY'] = path_anaconda + r"tcl\tcl8.6"
os.environ['TK_LIBRARY'] = path_anaconda + r"tcl\tk8.6"
# On appelle la fonction setup

includes  = ["lxml._elementpath"]
include_files = [path_anaconda + r"DLLs\tcl86t.dll",
                 path_anaconda + r"DLLs\tk86t.dll"]
base = None

build_exe_options = {"packages": ["files", "tools"], "include_files": ["tcl86t.dll", "tk86t.dll"]}  
setup(

    name = "TransBiblio",

    version = "1",

    description = "Programme d'alignement avec les données de la BnF",
    options = {"build_exe": {"includes": includes,"include_files":include_files}},
    executables = [Executable("main.py", base=base)],

)

#Ajout d'un raccourci pointant vers le fichier *.exe
raccourci = open("build/transbiblio.bat","w")
raccourci.write("start exe.win-amd64-3.5/main.exe")
