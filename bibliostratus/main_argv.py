# coding: utf-8

"""
Tests ligne de commande
Lancer 
python main_argv.py convertISBN "2845407769"

python main_argv.py bib2id None None "main/examples/mon_impr.tsv" 1 1 0 1 0 test_argv
python main_argv.py marc2tables None "main/examples/noticesbib.iso" 1 1 test_argv None


"""

import sys
import marc2tables
import bib2id
import aut2id
import ark2records


dic_functions = {
    "bib2id": bib2id,
    "aut2id": aut2id,
    "marc2tables": marc2tables,
    "ark2records": ark2records
}

if __name__ == "__main__":
    function = dic_functions[sys.argv[1]].launch
    parametres = sys.argv[2:]
    i = 0
    for el in parametres:
        if el == "None":
            parametres[i] = None
    try:
        function(*parametres)
    except ValueError as err:
        print(err)
