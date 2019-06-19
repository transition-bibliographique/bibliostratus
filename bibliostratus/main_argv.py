# coding: utf-8

"""
Lancer les modules de Bibliostratus en ligne de commande

On lance chaque module par son nom de fichier (bib2id, aut2id, etc.) avec les paramètres de chaque fonction
dans leur ordre d'apparition sur le formulaire
On peut rajouter le repertoire de destination comme dernier argument. Il faut alors le faire preceder de "--"
Les valeurs "None" viennent remplacer les objets "Formulaires" utilisés par les fonctions launch de chaque module

python main_argv.py aut2id None "main/examples/aut_align_aut.tsv" 1 1 1 0 1 argv_test_aut2id 1
python main_argv.py bib2id None None "main/examples/mon_impr.tsv" 1 1 0 1 0 argv_test_bib2id
python main_argv.py marc2tables None "main/examples/noticesbib.iso" 1 1 argv_test_marc2tables None
python main_argv.py marc2tables None "main/examples/noticesbib.iso" 1 1 argv_test_marc2tables None --D:/Mes documents
python main_argv.py ark2records None None "main/examples/listeARKbib.tsv" 1 1 1 0 0 0 argv_test_ark2records 1 1 ""
"""

import sys

import main
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
    # Si le dernier argument commence par un chevron > : c'est le répertoire de destination
    # pour les rapports
    if parametres[-1].startswith("--"):
        main.output_directory = [parametres.pop(-1)[2:].strip()]
    i = 0
    for el in parametres:
        if el == "None":
            parametres[i] = None
        i += 1
    try:
        function(*parametres)
    except ValueError as err:
        print(err)
