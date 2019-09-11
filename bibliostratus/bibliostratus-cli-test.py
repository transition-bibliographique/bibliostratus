# coding: utf-8

"""
Lancer les modules de Bibliostratus en ligne de commande

On lance chaque module par son nom de fichier (bib2id, aut2id, etc.) avec les paramètres de chaque fonction
dans leur ordre d'apparition sur le formulaire
On peut rajouter le repertoire de destination comme dernier argument. Il faut alors le faire preceder de "--"

bib2id (utilisant les valeurs par défaut pour plusieurs arguments)
python bibliostratus-cli-test.py --action bib2id --file main\examples\mon_impr.tsv --id cli_test

aut2id
python bibliostratus-cli-test.py --action aut2id --file main\examples\aut_align_aut.tsv
"""

import sys
import argparse

import main
import marc2tables
import bib2id
import aut2id
import ark2records





dic_functions = {
    "align_bib": bib2id,
    "align_aut": aut2id
}

dic_doctype = {"tex": 1,
               "vid": 2,
               "aud": 3,
               "per": 4,
               "car": 5,
               "par": 6,
               "pers": 1,
               "org": 2,
               "bib2aut": 3,
               "ram": 4,
               "rameau": 4}
align_prefs = {"bnf": 1,
                "sudoc": 2,
                "idref": 2,
                "abes": 2}
dic_files_number = {"1": 1,
                    "mul": 2,
                    "plusieurs": 2,
                    "plus": 2}
dic_checkbox = {"1": 1,
                "o": 1,
                "oui": 1,
                "y": 1,
                "yes": 1,
                "True": 1,
                "0": 0,
                "n": 0,
                "non": 0,
                "no": 0,
                "False": 0}


def action_align():
    align_bib = argparse.ArgumentParser(description="Alignement de notices")
    align_bib.add_argument("--action", help="Commande")
    align_bib.add_argument("--file", help="Nom du fichier en entrée")
    align_bib.add_argument("--doctype", help="Type de documents à aligner", default="tex")
    align_bib.add_argument("--align_pref", help="Préférences d'alignement (bnf / abes)", default="bnf")
    align_bib.add_argument("--sudoc_kw", help="Recherche par mots-clés dans le Sudoc", default="non")
    align_bib.add_argument("--isni", help="Relancer la recherche dans isni.org", default="non")
    align_bib.add_argument("--headers", help="Fichier avec en-têtes", default="oui")
    align_bib.add_argument("--dir", help="Dossier de destination", default="")
    align_bib.add_argument("--files_nb", help="Nombre de fichiers en sortie", default="1")
    align_bib.add_argument("--metas", help="Récupérer les métadonnées simples", default="0")
    align_bib.add_argument("--id", help="Préfixe pour les fichiers en sortie", default="")
    args = align_bib.parse_args()
    args.headers = dic_checkbox[args.headers]
    args.doctype = dic_doctype[args.doctype]
    args.align_pref = align_prefs[args.align_pref]
    args.sudoc_kw = dic_checkbox[args.sudoc_kw]
    args.isni = dic_checkbox[args.isni]
    args.files_nb = dic_files_number[args.files_nb]
    args.metas = dic_checkbox[args.metas]
    if args.action == "bib2id":
        bib2id.launch(args.file, args.doctype, args.align_pref, args.sudoc_kw,
                      args.files_nb, args.metas, args.id)
    elif args.action == "aut2id":
        aut2id.launch(args.file, args.headers, args.doctype, args.align_pref,
                      args.isni, args.files_nb, args.metas, args.id)


if __name__ == "__main__":
    if sys.argv[2].endswith("2id"):
        action_align()
    
    