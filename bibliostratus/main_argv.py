# coding: utf-8

"""
Lancer les modules de Bibliostratus en ligne de commande

On lance chaque module par son nom de fichier (bib2id, aut2id, etc.) avec les paramètres de chaque fonction
dans leur ordre d'apparition sur le formulaire
On peut rajouter le repertoire de destination comme dernier argument. Il faut alors le faire preceder de "--"

python main_argv.py aut2id "main/examples/aut_align_aut.tsv" 1 1 1 0 1 1 argv_test_aut2id
python main_argv.py bib2id "main/examples/mon_impr.tsv" 1 1 0 1 0 argv_test_bib2id
python main_argv.py marc2tables "main/examples/noticesbib.iso" 1 1 argv_test_marc2tables
python main_argv.py marc2tables "main/examples/noticesbib.iso" 1 1 argv_test_marc2tables --D:/Mes documents
python main_argv.py ark2records "main/examples/listeARKbib.tsv" 1 1 1 0 0 0 argv_test_ark2records 1 1 ""
"""

import sys

import main
import marc2tables
import bib2id
import aut2id
import ark2records

dic_functions = {
    "bib2id": {"action": bib2id,
               "description": "Alignement de notices bibliographiques",
               "parametres":
                [["Nom du fichier", "Chemin (relatif ou absolu) du fichier en entrée à utiliser"],
                 ["Type de documents", "Valeurs autorisées :\n\
     1 (TEX)\n\
     2 (VID)\n\
     3 (AUD)\n\
     4 (PER)\n\
     5 (CAR)\n\
     6 (PAR) "],
                 ["Préférences d'alignement", "Valeurs autorisées :\n\
     1 : BnF,\n\
     2 : Sudoc,\n"],
                 ["Recherche mot-clé dans le Sudoc", "Valeurs autorisées :\n\
     0 : Non,\n\
     1 : Oui,\n"],
                 ["Nombre de fichiers", "Valeurs autorisées :\n\
     1 : 1 fichier,\n\
     2 : 3 fichiers,\n"],
                 ["Récupérer les métadonnées bibliographiques", "Valeurs autorisées :\n\
     0 : Non,\n\
     1 : Oui,\n"],
                 ["Identifiant du traitement", ""],
                ]
              },
    "aut2id": {"action": aut2id,
               "description": "Alignement de notices d'autorité",
               "parametres": 
                [["Nom du fichier", "Chemin (relatif ou absolu) du fichier en entrée à utiliser"],
                 ["Type de notices", "Valeurs autorisées :\n\
     1 (PERS),\n\
     2 (ORG),\n\
     3 (notices BIB pour alignement d'autorités),\n\
     4 (Rameau) "],
                 ["Préférences d'alignement", "Valeurs autorisées :\n\
     1 : BnF\n\
     2 : Sudoc\n"],
                 ["Rebond sur l'ISNI", "Valeurs autorisées : \n\
     0 : non \n\
     1 : oui\n"],
                 ["Nombre de fichiers", "Valeurs autorisées :\n\
     1 : 1 fichier\n\
     2 : 3 fichiers\n"],
                 ["Récupérer les métadonnées", "Valeurs autorisées : \n\
     0 : non \n\
     1 : oui\n"],
                 ["Identifiant du traitement", ""],
                ]
              },
    "marc2tables": {"action": marc2tables,
                    "description": "Conversion d'un fichier MARC en plusieurs fichiers tabulés",
                    "parametres":
                        [["Nom du fichier", "Chemin (relatif ou absolu) du fichier en entrée à utiliser"],
                         ["Format du fichier", "Valeurs autorisées :\n\
     1 (iso2709 en UTF-8)\n\
     2 (iso2709 en 8859-1)\n\
     3 (XML en UTF-8)"],
                         ["Type de notices dans le fichier", "Valeurs autorisées:\n\
     1 (BIB)\n\
     2 (AUT)\n\
     3 (BIB pour alignement AUT)"]
                        ]
                    },                     
    "ark2records": {"action": ark2records,
                    "description": "Conversion d'une liste d'identifiants BnF (ARK) ou Abes (PPN) en fichier de notices MARC",
                    "parametres":
                        [["Nom du fichier", "Chemin (relatif ou absolu) du fichier en entrée à utiliser"],
                         ["Format du fichier", "Valeurs autorisées :\n     1 (iso2709 en UTF-8)\n\
     2 (iso2709 en 8859-1)\n     3 (XML en UTF-8)"],
                         ["Type de notices dans le fichier", "Valeurs autorisées:\n     1 (BIB)\n     2 (AUT)"]
                        ]
                    }
    }

functions_description = [" : ".join([key,  dic_functions[key]['description']]) 
                         for key in dic_functions]
error_function_name = "Les fonctions prévues par le programme sont : \n  " + '\n  '.join(functions_description)

if __name__ == "__main__":
    try:
        function_name = sys.argv[1]
    except IndexError:
        print(f"\nListe des fonctions disponibles : {', '.join(dic_functions.keys())}")
        sys.exit(1)
    try:
        function = dic_functions[function_name]["action"].launch
    except KeyError:
        print("\nErreur : nom de fonction appelée = ", function_name, "\n")
        print(error_function_name)
        sys.exit()
    parametres = sys.argv[2:]
    # Si le dernier argument commence par un chevron > : c'est le répertoire de destination
    # pour les rapports
    if len(parametres) and parametres[-1].startswith("--"):
        main.output_directory = [parametres.pop(-1)[2:].strip()]
    i = 0
    for el in parametres:
        if el == "None":
            parametres[i] = None
        i += 1
    try:
        function(*parametres)
    except TypeError as err:
        print("\n")
        print("Fonction appelée : ", function_name)
        print(dic_functions[function_name]["description"])
        print("Liste des paramètres : ")
        i = 1
        j = 0
        for el in dic_functions[function_name]["parametres"]:
            print("  ", i, ".", el[0], ":", el[1])
            try:
                print("    Valeur indiquée : ", parametres[j], "\n"*3)
            except IndexError:
                print("    Valeur indiquée : non renseigné")
            print("\n")
            i += 1
            j += 1
        print("\n\nOn peut rajouter le repertoire de destination comme dernier argument. Il faut alors le faire preceder de \"--\"")
        sys.exit()