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

marc2tables
python bibliostratus-cli-test.py --action marc2tables --file main\examples\3bibrecords.xml --filetype xml-utf8 --recordtype bib --id cli_test

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
    "align_aut": aut2id,
    "marc2tables": marc2tables
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

dic_input_filetype = {"iso2708-utf8": 1,
                      "iso2709": 1,
                      "iso2709-8859-1": 2,
                      "xml-utf8": 3,
                      "xml": 3}

dic_input_recordtype = {"bib": 1,
                        "aut": 2,
                        "bib2aut": 3}

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
    align_bib = initialized_action(align_bib)
    align_bib.add_argument("--doctype", help="Type de documents à aligner", default="tex",
                           choices=dic_doctype.keys())
    align_bib.add_argument("--align_pref", help="Préférences d'alignement (bnf / abes)", default="bnf",
                           choices=["bnf", "abes", "sudoc", "idref"])
    align_bib.add_argument("--sudoc_kw", help="Recherche par mots-clés dans le Sudoc", default="non")
    align_bib.add_argument("--isni", help="Relancer la recherche dans isni.org", default="non")
    align_bib.add_argument("--headers", help="Fichier avec en-têtes", default="oui")
    align_bib.add_argument("--files_nb", help="Nombre de fichiers en sortie", default="1")
    align_bib.add_argument("--metas", help="Récupérer les métadonnées simples", default="0")
    args = align_bib.parse_args()
    args.headers = dic_checkbox[args.headers.lower()]
    args.doctype = dic_doctype[args.doctype.lower()]
    args.align_pref = align_prefs[args.align_pref.lower()]
    args.sudoc_kw = dic_checkbox[args.sudoc_kw.lower()]
    args.isni = dic_checkbox[args.isni.lower()]
    args.files_nb = dic_files_number[args.files_nb.lower()]
    args.metas = dic_checkbox[args.metas.lower()]
    if args.action == "bib2id":
        bib2id.launch(args.file, args.doctype, args.align_pref, args.sudoc_kw,
                      args.files_nb, args.metas, args.id)
    elif args.action == "aut2id":
        aut2id.launch(args.file, args.headers, args.doctype, args.align_pref,
                      args.isni, args.files_nb, args.metas, args.id)


def action_marc2tables():
    convert_marc2tables = argparse.ArgumentParser(description="Conversion de fichiers Marc en tableaux")
    convert_marc2tables = initialized_action(convert_marc2tables)
    convert_marc2tables.add_argument("--filetype", help="Type de fichier en entrée",
                                     default="iso2708-utf8",
                                     choices=["iso2708-utf8", "iso2709-8859-1",
                                              "xml", "xml-utf8"])
    convert_marc2tables.add_argument("--recordtype", help="Type de notices", default="bib",
                                     choices=["bib", "aut", "bib2aut"])
    args = convert_marc2tables.parse_args()
    
    args.filetype = dic_input_filetype[args.filetype.lower()]
    args.recordtype = dic_input_recordtype[args.recordtype.lower()]
    marc2tables.launch(args.file, args.filetype,
                       args.recordtype, args.id)


def action_ark2records():
    convert_ark2records = argparse.ArgumentParser(description="Export de notices en MARC")
    convert_ark2records = initialized_action(convert_ark2records)
    convert_ark2records.add_argument("--recordtype", help="Type de notices", default="bib",
                                     choices=["bib", "aut"])
    convert_ark2records.add_argument("--colnum", help="Nombre de colonnes en entrée [1 / 2]",
                                     default=1,
                                     choices=[1, 2],
                                     type=int)
    convert_ark2records.add_argument("--headers", help="Fichier avec en-têtes", default="oui")
    convert_ark2records.add_argument("--get_authors", 
                                     help="Récupérer les auteurs liés",
                                     default="non")
    convert_ark2records.add_argument("--get_subjets", 
                                     help="Récupérer les notices Sujet liées",
                                     default="non")
    convert_ark2records.add_argument("--get_works", 
                                     help="Récupérer les notices Oeuvres liées",
                                     default="non")
    convert_ark2records.add_argument("--output_format", 
                                     help="Format en sortie des notices",
                                     default="unimarc",
                                     choices=["unimarc", "intermarc", 
                                              "unimarc-anl", "intermarc-anl"])
    convert_ark2records.add_argument("--output_file", 
                                     help="Format en sortie du fichier",
                                     default="iso2709",
                                     choices=["iso2709", "xml", "tab"])
    convert_ark2records.add_argument("--encoding", 
                                     help="Encodage en sortie",
                                     default="utf8",
                                     choices=["utf8", "8859-1"])
    convert_ark2records.add_argument("--fields", 
                                     help="Zones spécifiques à récupérer")

    args = convert_ark2records.parse_args()
    args.headers = dic_checkbox[args.headers.lower()]
    ark2records.launch(args.file, args.recordtype, args.colnum,
                       args.header, args.get_authors, args.get_subjects,
                       args.get_works, args.dir, args.output_format,
                       args.output_file, args.encoding, args.fields,
                       args.id)


def initialized_action(argumentParser):
    argumentParser.add_argument("--action", help="Commande",
                                choices=["bib2id", "aut2id", "marc2tables", "ark2records"])
    argumentParser.add_argument("--file", help="Nom du fichier en entrée")
    argumentParser.add_argument("--dir", help="Dossier de destination", default="")
    argumentParser.add_argument("--id", help="Préfixe pour le(s) fichier(s) en sortie", default="")
    return argumentParser

if __name__ == "__main__":
    if sys.argv[2].endswith("2id"):
        action_align()
    elif sys.argv[2] == "marc2tables":
        action_marc2tables()
    
    