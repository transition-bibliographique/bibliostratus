# coding: utf-8

explain = """
Module d'alignement de fichier Excel dans le cadre des chargements BnF pour les Gallica Marque Blanche
Les bibliothèques partenaires constituent un fichier Excel dans un certain formatage.

Le présent script utilise les colonnes (avec un fichier de paramètres éditable par l'utilisateur)
d'un fichier Excel décrivant des monographies imprimées

"""

import os
#import pandas as pd
#from pandas import read_excel, DataFrame
from pprint import pprint
import csv
from string import ascii_uppercase

import funcs
import main
import bib2id
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


def csvfile2bbsfile(input_filename, params_gmb):
    # A partir d'un nom de fichier Excel
    # on renvoie un nom de fichier au format Bibliostratus
    # où les colonnes ont été sélectionnées
    # en fonction des paramètres du fichier gmb_preferences
    bbs_table = csv2bbs(input_filename, params_gmb)
    #pprint(bbs_table)
    bbs_file = create_file(input_filename, main.output_directory[0], "bibliostratus")
    for row in bbs_table:
        funcs.line2report(row, bbs_file, display=False)
    #bbs_dataframe.to_csv(bbs_filename, index=False, sep="\t")
    return bbs_file.name

def create_file(input_filename, dir, prefix):
    outputfilename = f"{'.'.join(input_filename.split('.')[:-1])}-{prefix}.tsv"
    outputfilename = os.path.join(dir, outputfilename)
    outputfile = bib2id.create_reports_1file(outputfilename)[0]
    return outputfile


def csv2bbs(input_filename, params_gmb):
    """
    A partir d'un nom de fichier CSV en entrée, 
    on sélectionne les colonnes
    """
    
    # df = pd.read_excel(input_filename, index_col=None, na_values=['NA'], usecols = "A,C:AA")
    init_table = funcs.file2list(input_filename, all_cols=True)
    bbs_table = []
    for row in init_table:
        new_row = []
        for attribute in params_gmb:
            value = ""
            if params_gmb[attribute] == "":
                value = ""
            elif type(params_gmb[attribute]) == int:
                colnr = params_gmb[attribute]
                value = row[colnr]
            elif type(params_gmb[attribute]) == list:
                value = []
                for colnr in params_gmb[attribute]:
                    value.append(row[colnr])
                value = " ".join(value)
            new_row.append(value)
        new_row.append("am")
        bbs_table.append(new_row)
    """
    for colname in params_gmb:
        if params_gmb[colname] == -1:
            bbs_df[colname] = " "
        elif type(params_gmb[colname]) == int:
            colnr = params_gmb[colname]
            colnm = df.keys()[colnr]
            bbs_df[colname] = df[colnm]
        elif type(params_gmb[colname]) == list:
            bbs_df[colname] = ""
            for colnr in params_gmb[colname]:
                colnm = df.keys()[colnr]
                bbs_df[colname] += " " + df[colnm]
    bbs_df["Type"] = "am"
    """
    return bbs_table


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
                 }
    try:
        with open(params_gmb_file_name, encoding="utf-8") as params_gmb_file:
            params_gmb = csv2dict(csv.reader(params_gmb_file, delimiter="\t"), params_gmb)
            
    except FileNotFoundError:
        print("Tentative pour ouvrir le fichier de préférences", params_gmb_file_name)
        print("Fichier non trouvé, les valeurs par défaut seront appliquées")
        print("Attribut : numéro de colonne")
        pprint(params_gmb)
    return params_gmb


def csv2dict(table, params_gmb):
    # Convertit un tableau à 2 colonnes (nom de l'attribut, nombre)
    # en dictionnaire
    
    for row in table:
        key = row[0]
        value = row[1]
        if key in params_gmb:
            if "," in value:
                value = [int(val) for val in value.split(",") if funcs.RepresentsInt(val)]
                params_gmb[key] = value
            elif value == "":
                params_gmb[key] = ""
            elif funcs.RepresentsInt(value):
                params_gmb[key] = int(value)
    return params_gmb


def launch_gmb_program():
    # Initialisation des paramètres GMB (numéro de colonne Excel > Colonne Bibliostratus)
    print(explain)
    print(r"Le fichier de paramètres \main\files\params_gmb.txt va être importé")
    print("\nAttribut de la colonne : Numéro de colonne (la numérotation commence à 0)\n")
    params_gmb = load_preferences()
    pprint(params_gmb)
    print("\nSi vous ne l'avez pas édité, veuillez  fermer ce programme et le modifier maintenant\npuis relancez Bibliostratus")
    return params_gmb

