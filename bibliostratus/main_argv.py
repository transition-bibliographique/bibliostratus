# coding: utf-8

"""
Tests ligne de commande
Lancer 
python main_argv.py "2845407769"
--> récupérer valeur ISBN13
"""

import sys
from funcs import conversionIsbn

arguments = sys.argv[1:]
converti = conversionIsbn(arguments[0])
print(converti)