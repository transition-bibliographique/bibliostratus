# coding: utf-8

explain = """
Module d'alignement de fichier Excel dans le cadre des chargements BnF pour les Gallica Marque Blanche
Les bibliothèques partenaires constituent un fichier Excel dans un certain formatage.

Le présent script utilise les colonnes (avec un fichier de paramètres éditable par l'utilisateur)
d'un fichier Excel décrivant des monographies imprimées

"""

import os
from collections import defaultdict
#import pandas as pd
#from pandas import read_excel, DataFrame
from pprint import pprint
import csv
from string import ascii_uppercase

import funcs
import forms
import main
import bib2id
import aut2id
import funcs

COLS_NAME = ",".join([l for l in ascii_uppercase]) + ","
COLS_NAME += ",".join([f"A{l}" for l in ascii_uppercase])
COLS_NAME = COLS_NAME.split(",")


def align_gmb(input_filename, prefix, dir, params_gmb):
    # Création du fichier intermédiaire au format BBS
    # puis lancement de l'alignement ligne à ligne
    bbs_filename = xlsxfile2bbsfile(input_filename, params_gmb)
    print("Lancement de l'alignement")
    bib2id.launch([bbs_filename], 1, 1, 0, 1, 1, prefix)
    print("-"*20)
    print("Fin du programme")
    print("-"*20)



def gmb_entities2results(form_bib2ark, gmb_records, liste_reports, parametres, params_gmb):
    # Au lieu de file2row (fonctionnement normal)
    # on récupère les entités produites par la fonction csv2entities
    # (qui pour chaque ligne du fichier en entrée produit
    # une Bib_record et une Bib_Aut_record)
    # Si 0 résultat trouvé pour la BIB
    # on cherche à identifier l'auteur sur un alignement Titre-Nom-Prénom
    parametres["type_doc_bib"] = 1
    parametres["preferences_alignement"] = 1
    parametres["kwsudoc_option"] = 0
    n = 1
    for record in gmb_records:
        #bib2id.row2file(gmb_records[record]["bbs_row"], liste_reports)
        bib_record = gmb_records[record]["bib"]
        bib_aut_records = gmb_records[record]["bib_aut"]
        bib_alignment_result = bib2id.item_alignement(bib_record, parametres)
        aut_alignment_results = ["", "", ""]
        if bib_alignment_result.nb_ids == 0:
            i = 0
            for bib_aut_record in bib_aut_records:
                bib_aut_parametres = {"headers": True,
                                      "input_data_type": 3,
                                      "isni_option": 0,
                                      "file_nb": parametres["file_nb"],
                                      "meta_bnf": parametres["meta_bib"],
                                      "id_traitement": parametres["id_traitement"],
                                      "type_aut": "a b",
                                      "preferences_alignement": 1,
                                      "stats":  defaultdict(int)
                                     }
                aut_alignment_result = aut2id.align_from_bib_alignment(bib_aut_records[bib_aut_record], bib_aut_parametres)
                aut_alignment_results[i] = aut_alignment_result.ids_str
                i += 1
        output_row = [gmb_records[record]["bbs_row"][0],
                      bib_alignment_result.ids_str,
                      bib_alignment_result.nb_ids,
                      bib_alignment_result.alignment_method_str
                      ] + gmb_records[record]["bbs_row"][1:]
        i = 0
        for bib_aut_record in bib_aut_records:
            extension = [aut_alignment_results[i],
                         bib_aut_records[bib_aut_record].lastname.init,
                         bib_aut_records[bib_aut_record].firstname.init]
            output_row.extend(extension)
            i += 1
        for i in range(len(bib_aut_records), 3):
            output_row.extend(["", "", ""])
        output_row.extend(gmb_records[record]["full_row"])
        if bib_alignment_result.nb_ids:
            print(f"{n}. {bib_record.NumNot} : {bib_alignment_result.ids_str}")
        elif "".join(aut_alignment_results):
            print(f"{n}. {bib_record.NumNot} : Auteurs identifiés : {aut_alignment_results}")
        else:
            print(f"{n}. {bib_record.NumNot}")
        n += 1
        
        if parametres["file_nb"] == 1:
            bib2id.row2file(output_row, liste_reports)
        elif parametres["file_nb"] == 2:
            bib2id.row2files(output_row, liste_reports, headers=True)
        
                      


def file2row(form_bib2ark, entry_filename, liste_reports, parametres):
    """Récupération du contenu du fichier et application des règles d'alignement
    ligne à ligne"""
    header_columns = ["NumNot", "Nb identifiants trouvés",
                      "Liste identifiants trouvés",
                      "Méthode d'alignement"]
    header_columns.extend(el for el in parametres["header_columns_init"][1:])
    header_columns.append("Type doc / Type notice")
    if parametres["meta_bib"] == 1:
        headers_add_metas = [f"[BnF/Abes] {el}" for el in headers_dict["all"][3:]]
        headers_add_metas.extend(["[BnF/Abes] Ids pérennes BnF/Abes", "[BnF/Abes] Type notice-doct"])
        header_columns.extend(headers_add_metas)
    # Ajout des en-têtes de colonne dans les fichiers
    if parametres["file_nb"] == 1:
        row2file(header_columns, liste_reports)
    elif parametres["file_nb"] == 2:
        row2files(header_columns, liste_reports, headers=True)
    n = 1
    with open(entry_filename, newline="\n", encoding="utf-8") as csvfile:
        entry_file = csv.reader(csvfile, delimiter="\t")
        try:
            next(entry_file)
        except UnicodeDecodeError:
            main.popup_errors(
                form_bib2ark,
                main.errors["pb_input_utf8"],
                "Comment modifier l'encodage du fichier",
                "https://github.com/Transition-bibliographique/bibliostratus/wiki/2-%5BBlanc%5D-:-alignement-des-donn%C3%A9es-bibliographiques-avec-la-BnF#erreur-dencodage-dans-le-fichier-en-entr%C3%A9e",  # noqa
            )
        for rows in funcs.chunks_iter(entry_file, NUM_PARALLEL):
            if (n-1) == 0:
                assert main.control_columns_number(
                        form_bib2ark, rows[0], parametres["header_columns_init"]
                        )
            if (n-1) % 100 == 0:
                main.check_access2apis(n, dict_check_apis)
            alignment_results = Parallel(n_jobs=NUM_PARALLEL)(delayed(item2id)(row, n, parametres) for row in rows)
            for alignment_result in alignment_results:
                alignment_result2output(alignment_result, alignment_result.input_record,
                                        parametres, liste_reports, n)
                parametres["stats"][alignment_result.nb_ids] += 1
                if "Pb FRBNF" in alignment_result.ids_str:
                    parametres["stats"]["Pb FRBNF"] += 1
                n += 1




def csv2entities(input_filename, params_gmb):
    """
    A partir d'un nom de fichier CSV en entrée, 
    on sélectionne les colonnes pour construire
        1. les BIB à aligner
        2. pour chaque BIB > pour chaque auteur, les entités auteur-bib à aligner
    On renvoie donc, pour chaque ligne (numéro de notice) :
        - un objet Bib_record
        - pour chaque auteur renseigné : un objet Bib_Aut_record
    """
    # df = pd.read_excel(input_filename, index_col=None, na_values=['NA'], usecols = "A,C:AA")
    init_table = funcs.file2list(input_filename, all_cols=True)
    headers = init_table.pop(0)
    records = defaultdict(dict)
    
    i = 0
    for row in init_table:
        bib_record = []
        bib_aut_records = defaultdict(list)
        numnot = get_value_of_table(row, params_gmb["NumNot"])
        frbnf = get_value_of_table(row, params_gmb["FRBNF"])
        ark = get_value_of_table(row, params_gmb["ARK"])
        isbn = get_value_of_table(row, params_gmb["ISBN"])
        ean = get_value_of_table(row, params_gmb["EAN"])
        title = get_value_of_table(row, params_gmb["Titre"])
        authors = get_value_of_table(row, params_gmb["Auteurs"])
        date = get_value_of_table(row, params_gmb["Date"])
        volume = get_value_of_table(row, params_gmb["Tome-Volume"])
        publisher = get_value_of_table(row, params_gmb["Editeur"])
        liste_auteurs = []
        for auteur in params_gmb["Auteurs (nom-prénom)"]:
            col_nom, col_prenom = auteur
            liste_auteurs.append([row[col_nom], row[col_prenom]])
        bbs_row = [numnot, frbnf, ark, isbn, ean, title, authors, date, volume, publisher, "am"]
        if numnot.strip() == "" or numnot in records:  # Si le numéro de notice est vide ou n'est pas unique
            numnot = "-".join(bbs_row)                     # on génère un nouvel identifiant constitué du contenu de la ligne
        bib_record = funcs.Bib_record(bbs_row, 1)
        for auteur in liste_auteurs:
            cle = " ".join(auteur) + " " + numnot
            bib_international_id = ean
            if ean == "":
                bib_international_id = isbn
            if "".join([el.strip() for el in auteur]):
                bib_aut_records[cle] = funcs.Bib_Aut_record([cle, numnot, ark, frbnf, bib_international_id,
                                                             title, "", "", auteur[0], auteur[1], ""])                       
        records[numnot] = {"full_row": row,
                           "bbs_row": bbs_row,
                           "bib": bib_record,
                           "bib_aut": bib_aut_records}
    return headers, records


def get_value_of_table(row, nr_of_column):
    # Extraire l'information de la bonne colonne du tableau
    value = []
    if type(nr_of_column) == int:
        nr_of_column = [nr_of_column]
    for nr in nr_of_column:
        value.append(row[int(nr)])
    value = " ".join(value)
    return value

def load_preferences():
    params_gmb_file_name = 'main/files/params_gmb.tsv'
    params_gmb = {"NumNot": -1,
                  "FRBNF": "",
                  "ARK": "",
                  "ISBN": "",
                  "EAN": "",
                  "Titre": [0,1,2,3],
                  "Auteurs": [4,5,6,12,13,17,18,22,23],
                  "Date": 30,
                  "Tome-Volume": "",
                  "Editeur": 28,
                  "Auteurs (nom-prénom)": [(12,13), (17,18), (22,23)]
                 }
    try:
        with open(params_gmb_file_name, encoding="utf-8") as params_gmb_file:
            params_gmb = csv2dict(csv.reader(params_gmb_file, delimiter="\t"), params_gmb)
            #print(params_gmb)
    except FileNotFoundError:
        print("Tentative pour ouvrir le fichier de préférences", params_gmb_file_name)
        print("Fichier non trouvé, les valeurs par défaut seront appliquées")
        print("Attribut : numéro de colonne")
        #pprint(params_gmb)
    except ValueError as err:
        print("*"*20)
        print(err)
        print("")
        print("Fichier mal formé : main/files/params_gmb.tsv")
        print("Corrigez le fichier suivant la documentation et relancez Bibliostratus")
        raise
    return params_gmb


def csv2dict(table, params_gmb):
    # Convertit un tableau à 2 colonnes (nom de l'attribut, nombre)
    # en dictionnaire
    
    for row in table:
        key = row[0]
        value = row[1]
        if key in params_gmb:
            if "," in value:
                if ("(") in value:  # Alors c'est une liste de paires nom-prénom
                    value = convertstring2tuples(value)
                    params_gmb[key] = value
                else:               # alors c'est juste une liste de valeurs
                    value = [int(val.strip()) for val in value.split(",") if funcs.RepresentsInt(val.strip())]
                    params_gmb[key] = value
            elif value == "":
                params_gmb[key] = ""
            elif funcs.RepresentsInt(value):
                params_gmb[key] = int(value)
    #print("-"*10, "\n" , params_gmb)
    return params_gmb

def convertstring2tuples(value):
    # Pour importer la ligne de paires "Nom-prénom" des auteurs, on récupère une chaine de caractères
    value = value.replace(" ", "").replace("),(", "\t").replace("(", "").replace(")", "")
    value = [tuple(map(int, el.split(','))) for el in value.split("\t")]
    return value


def launch_gmb_program():
    # Initialisation des paramètres GMB (numéro de colonne Excel > Colonne Bibliostratus)
    print(explain)
    print(r"Le fichier de paramètres \main\files\params_gmb.txt va être importé")
    print("\nAttribut de la colonne : Numéro de colonne (la numérotation commence à 0)\n")
    params_gmb = load_preferences()
    pprint(params_gmb)
    print("\nSi vous ne l'avez pas édité, veuillez  fermer ce programme et le modifier maintenant\npuis relancez Bibliostratus")
    return params_gmb

