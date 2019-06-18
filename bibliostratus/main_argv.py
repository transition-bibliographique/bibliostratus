# coding: utf-8

"""
Tests ligne de commande
Lancer 
python main_argv.py convertISBN "2845407769"
python main_argv.py marc2tables main/examples/noticesbib.iso 1 1 test
--> récupérer valeur ISBN13
"""

import sys
from funcs import conversionIsbn
import marc2tables

dic_functions = {
    "convertISBN": conversionIsbn,
    "marc2tables": marc2tables.launch
}
arguments = sys.argv[1:]
function = arguments.pop(0)

if function == "marc2tables":
    args = [None]
    for arg in arguments:
        try:
            args.append(int(arg))
        except TypeError:
            args.append(arg)
        except ValueError:
            args.append(arg)
    args.append(None)
    arguments = args
dic_functions[function](*arguments)
print(converti)