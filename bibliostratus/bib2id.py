# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 18:30:30 2017

@author: Etienne Cavalié

Programme d'identification des ARK BnF à partir de numéros FRBNF

Reprendre à la fonction issn2ark
Puis modifier le formulaire pour proposer l'option "Périodiques"
 + définir les colonnes (date ?)

"""

import csv
import os
import ssl
import socket
import tkinter as tk
import http.client
import urllib.parse
import re
from collections import defaultdict
from lxml import etree
from lxml.html import parse
from urllib import request
import json

import funcs
import main
import aut2id_idref
import sru

# Ajout exception SSL pour éviter
# plantages en interrogeant les API IdRef
# (HTTPS sans certificat)
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
   getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


url_access_pbs = []





# Permet d'écrire dans une liste accessible au niveau général depuis le
# formulaire, et d'y accéder ensuite
entry_file_list = []

# Pour chaque notice, on recense la méthode
# qui a permis de récupérer le ou les ARK
NumNotices2methode = defaultdict(list)
# Si on trouve la notice grâce à un autre ISBN :
# on l'indique dans un dictionnaire qui
# est ajouté dans le rapport stat
NumNotices_conversionISBN = defaultdict(dict)

# Toutes les 100 notices, on vérifie que les API BnF et Abes
# répondent correctement.
# Résultats (True/False) enregistrés dans ce dictionnaire
dict_check_apis = defaultdict(dict)

# Quelques listes de signes à nettoyer
listeChiffres = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
lettres = [
    "a",
    "b",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
]
lettres_sauf_x = [
    "a",
    "b",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "y",
    "z",
]
ponctuation = [
    ".",
    ",",
    ";",
    ":",
    "?",
    "!",
    "%",
    "$",
    "£",
    "€",
    "#",
    '"',
    "&",
    "~",
    "{",
    "(",
    "[",
    "`",
    "\\",
    "_",
    "@",
    ")",
    "]",
    "}",
    "=",
    "+",
    "*",
    "/",
    "<",
    ">",
    ")",
    "}",
]
header_columns_init_monimpr = [
    "Num Not",
    "FRBNF",
    "ARK",
    "ISBN",
    "EAN",
    "Titre",
    "Auteur",
    "Date",
    "Volume-Tome",
    "Editeur",
]
header_columns_init_cddvd = [
    "Num Not",
    "FRBNF",
    "ARK",
    "EAN",
    "N° commercial",
    "Titre",
    "Auteur",
    "Date",
    "Editeur",
]
header_columns_init_perimpr = [
    "Num Not",
    "FRBNF",
    "ARK",
    "ISSN",
    "Titre",
    "Auteur",
    "Date",
    "Lieu de publication",
]

header_columns_init_cartes = [
    "Num Not",
    "FRBNF",
    "ARK",
    "ISBN",
    "EAN",
    "Titre",
    "Auteur",
    "Date",
    "Editeur",
    "Echelle"
]

header_columns_init_partitions = [
    "Num Not",
    "FRBNF",
    "ARK",
    "EAN",
    "Référence commerciale",  #023$a en Intermarc, 071$a en Unimarc
    "Titre",
    "Titre de partie",
    "Auteur",
    "Date",
    "Editeur",
]

# Noms des fichiers en sortie


def create_reports(id_traitement_code, nb_fichiers_a_produire):
    reports = []
    stats_report_file_name = (
        id_traitement_code + "-" + "rapport_stats_bib2id.txt"
    )
    stats_report_file = open(stats_report_file_name, "w")
    stats_report_file.write("Nb ID trouvés\tNb notices concernées\n")

    if nb_fichiers_a_produire == 1:
        reports = create_reports_1file(id_traitement_code)
    else:
        reports = create_reports_files(id_traitement_code)
    reports.append(stats_report_file)
    # reports.append(report_type_convert_file)
    return reports


def create_reports_1file(id_traitement_code):
    unique_file_results_frbnf_isbn2ark_name = (
        id_traitement_code + "-" + "resultats_bib2id.txt"
    )
    unique_file_results_frbnf_isbn2ark = open(
        unique_file_results_frbnf_isbn2ark_name, "w", encoding="utf-8"
    )
    return [unique_file_results_frbnf_isbn2ark]


def create_reports_files(id_traitement_code):
    multiple_files_pbFRBNF_ISBN_name = (
        id_traitement_code + "-Problemes_donnees_initiales.txt"
    )
    multiple_files_0_ark_name = "".join([id_traitement_code,
                                        "-resultats_0_ID_trouve.txt"])
    multiple_files_1_ark_name = "".join([id_traitement_code,
                                        "-resultats_1_ID_trouve.txt"])
    multiple_files_plusieurs_ark_name = (
        id_traitement_code + "-resultats_plusieurs_ID_trouves.txt"
    )

    multiple_files_pbFRBNF_ISBN = open(
        multiple_files_pbFRBNF_ISBN_name, "w", encoding="utf-8"
    )
    multiple_files_0_ark = open(multiple_files_0_ark_name,
                                "w", encoding="utf-8")
    multiple_files_1_ark = open(multiple_files_1_ark_name,
                                "w", encoding="utf-8")
    multiple_files_plusieurs_ark_name = open(
        multiple_files_plusieurs_ark_name, "w", encoding="utf-8"
    )

    return [
        multiple_files_pbFRBNF_ISBN,
        multiple_files_0_ark,
        multiple_files_1_ark,
        multiple_files_plusieurs_ark_name,
    ]

ns = {
    "srw": "http://www.loc.gov/zing/srw/",
    "mxc": "info:lc/xmlns/marcxchange-v2",
    "m": "http://catalogue.bnf.fr/namespaces/InterXMarc",
    "mn": "http://catalogue.bnf.fr/namespaces/motsnotices",
}
nsOCLC = {"xisbn": "http://worldcat.org/xid/isbn/"}
nsSudoc = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "bibo": "http://purl.org/ontology/bibo/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "rdafrbr1": "http://rdvocab.info/RDARelationshipsWEMI/",
    "marcrel": "http://id.loc.gov/vocabulary/relators/",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "gr": "http://purl.org/goodrelations/v1#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "isbd": "http://iflastandards.info/ns/isbd/elements/",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "rdafrbr2": "http://RDVocab.info/uri/schema/FRBRentitiesRDA/",
    "rdaelements": "http://rdvocab.info/Elements/",
    "rdac": "http://rdaregistry.info/Elements/c/",
    "rdau": "http://rdaregistry.info/Elements/u/",
    "rdaw": "http://rdaregistry.info/Elements/w/",
    "rdae": "http://rdaregistry.info/Elements/e/",
    "rdam": "http://rdaregistry.info/Elements/m/",
    "rdai": "http://rdaregistry.info/Elements/i/",
    "sudoc": "http://www.sudoc.fr/ns/",
    "bnf-onto": "http://data.bnf.fr/ontology/bnf-onto/",
}


# fonction de mise à jour de l'ARK s'il existe un ARK
def ark2ark(input_record):
    result = sru.SRU_result(f'bib.persistentid all "{input_record.ark_init}"')
    nv_ark = ",".join(result.list_identifiers)
    if nv_ark != input_record.ark_init:
        input_record.alignment_method.append("Actualisation ARK")
    elif nv_ark == input_record.ark_init:
        input_record.alignment_method.append("ARK identique")
    elif nv_ark == "":
        input_record.alignment_method.append("ARK initial supprimé")
    return nv_ark


def relancerNNBAuteur(input_record, NumNot, systemid, isbn, titre, auteur, date):
    """Si la recherche NNB avec comporaison Mots du titre n'a rien donné, on
    recherche sur N° interne BnF + Auteur (en ne gardant que le mot le plus
    long du champ Auteur)"""
    listeArk = []
    if (auteur and auteur is not None):
        results = sru.SRU_result(f'bib.author all "{auteur}" and bib.otherid all "{systemid}"')
        for ark_current in results.list_identifiers:
            listeArk.append(ark)
    if listeArk:
        input_record.alignment_method.append("N° sys FRBNF + Auteur")
    listeArk = ",".join([ark for ark in listeArk if ark])
    return listeArk



def comparerBibBnf(input_record,
                   NumNot, ark_current, 
                   xml_record_current,
                   systemid, 
                   identifier, 
                   titre, auteur,
                   date, origineComparaison
                  ):
    """
    Quand on a trouvé l'ancien numéro système dans une notice BnF :
    on compare l'ISBN de la notice de la Bibliothèque
    avec celui de la BnF pour voir si ça colle
    à défaut, on compare les titres (puis demi-titres)
    """
    
    ark = comparaisonIsbn(input_record,
                          NumNot, ark_current, xml_record_current,
                          systemid,
                          identifier, titre, auteur, date, 
                         )
    if ark == "":
        ark = comparaisonTitres(
            input_record,
            NumNot,
            ark_current,
            systemid,
            identifier,
            titre,
            auteur,
            date,
            "",
            xml_record_current,
            origineComparaison,
        )
    return ark


def comparaisonIsbn(input_record, NumNot, 
                    ark_current, xml_record_current,
                    systemid, isbn, titre, auteur, date):
    ark = ""
    isbnBNF = ""
    sourceID = "ISBN"
    # Si le FRBNF de la notice source est présent comme ancien numéro de notice
    # dans la notice BnF, on compare les ISBN en 010, ou à défaut les EAN
    # ou à défaut les ISSN (il peut s'agir d'un périodique)
    isbnBNF = funcs.nettoyage(sru.record2fieldvalue(xml_record_current, "010$a").split("~")[0])
    if isbnBNF == "":
        isbnBNF = funcs.nettoyage(sru.record2fieldvalue(xml_record_current, "038$a").split("~")[0])
        sourceID = "EAN"
    if isbnBNF == "":
        isbnBNF = funcs.nettoyage(sru.record2fieldvalue(xml_record_current, "011$a").split("~")[0])
        sourceID = "ISSN"
    if isbn != "" and isbnBNF != "":
        if isbn in isbnBNF:
            ark = ark_current
            input_record.alignment_method.append("N° sys FRBNF \
+ contrôle " + sourceID)
    return ark


def comparaisonTitres(
    input_record,
    NumNot,
    ark_current,
    systemid,
    isbn,
    titre,
    auteur,
    date,
    numeroTome,
    recordBNF,
    origineComparaison,
    ):
    ark = ""
    subfields_list = ["200$a", "200$e", "200$i",
                    "750$a", "753$a", "500$a",
                    "500$e", "503$e", "540$a",
                    "540$e", "410$a", "225$a",
                    "461$t", "464$t"]
    text_method_alignment = ""
    for subfield in subfields_list:
        if (ark == ""):
            ark, text_method_alignment = comparaisonTitres_sous_zone(
                                            input_record,
                                            NumNot,
                                            ark_current,
                                            systemid,
                                            isbn,
                                            titre,
                                            auteur,
                                            date,
                                            recordBNF,
                                            origineComparaison,
                                            subfield
                                            )
    if (ark != ""
       and input_record.type == "PAR"
       and input_record.soustitre.controles != ""):
        ark_confirmed = ""
        subfields_list_2 = ["464$t", "200$a+200$e", "225$e"]
        for subfield in subfields_list_2:
            if ark_confirmed == "":
                ark_confirmed, compl_text_method_alignment = comparaisonTitres_sous_zone(
                                                        input_record,
                                                        NumNot,
                                                        ark_current,
                                                        systemid,
                                                        isbn,
                                                        input_record.soustitre.controles,
                                                        auteur,
                                                        date,
                                                        recordBNF,
                                                        origineComparaison,
                                                        subfield
                                                        )
        if ark_confirmed == ark:
            text_method_alignment += compl_text_method_alignment
        else:
            ark = ""
    if ark != "" and numeroTome != "":
        ark = verificationTomaison(ark, numeroTome, recordBNF)
    if ark != "" and date != "":
        if (
            "ISBN" in origineComparaison
            or "EAN" in origineComparaison
            or "commercial" in origineComparaison
        ):
            ark = checkDate(ark, date, recordBNF)
    if ark:
        input_record.alignment_method.append(text_method_alignment)
    return ark


def verificationTomaison(ark, numeroTome, recordBNF):
    """Une fois qu'on a trouvé un ARK (via une recherche Titre-Auteur-Date,
    s'il y a un numéro de volume dans les données en entrée on va vérifier
    si on le retrouve bien dans une des zones où il pourrait se trouver :
    D'abord 200$h, 461$v
    Si ces deux zones sont vides, on va regarder les nombres dans la zone 200$a
    La comparaison se fait en normalisant les données de part en d'autres,
    pour n'avoir que des chiffres arabes sans 0 initial
    Conséquence : s'il y a un numéro de volume en entrée, le programme peut
    aller jusqu'à convertir tout ce qui ressemble à un chiffre romain dans
    la zone de titre"""
    liste_subfields_volume = ["200$h", "200$u", "461$v"]
    volumesBNF = ""
    for subf in liste_subfields_volume:
        volumesBNF += "~" + sru.record2fieldvalue(recordBNF,
                                                  subf)
    volumesBNF = funcs.convert_volumes_to_int(volumesBNF)
    if volumesBNF == "":
        volumesBNF = sru.record2fieldvalue(recordBNF, "200$a")
        volumesBNF = funcs.convert_volumes_to_int(volumesBNF)
        for lettre in lettres:
            volumesBNF = volumesBNF.replace(lettre, "~")
        volumesBNF = volumesBNF.split("~")
        volumesBNF = set(str(funcs.ltrim(nb)) for nb in volumesBNF if nb != "")
    if volumesBNF != "" and numeroTome in volumesBNF:
        return ark
    else:
        return ""


def verificationTomaison_sous_zone(ark, numeroTome, numeroTomeBnF):
    """Vérifie si le numéro du tome en entrée est présent dans
    l'extraction des nombres de la sous-zone
    """
    return ark, False


# =============================================================================
# def ltrim(nombre_texte):
#     "Supprime les 0 initiaux d'un nombre géré sous forme de
#      chaîne de caractères"
#     while(len(nombre_texte) > 1 and nombre_texte[0] == "0"):
#         nombre_texte = nombre_texte[1:]
#     return nombre_texte
# =============================================================================


def checkDate(ark, date_init, recordBNF):
    ark_checked = ""
    dateBNF = []
    dateBNF_100 = funcs.unidecode_local(sru.record2fieldvalue(recordBNF, "100$a").split("~")[0].lower())[9:13]
    if len(dateBNF_100) > 4:
        dateBNF_100 = dateBNF_100[0:4]
    if main.RepresentsInt(dateBNF_100) is True:
        dateBNF_100 = int(dateBNF_100)
        dateBNF.extend([dateBNF_100 + 1, dateBNF_100 - 1])
    dateBNF.append(dateBNF_100)
    dateBNF_210d = funcs.unidecode_local(
        sru.record2fieldvalue(recordBNF, "210$d").split("~")[0].lower()
    )
    dateBNF_306a = funcs.unidecode_local(
        sru.record2fieldvalue(recordBNF, "306$a").split("~")[0].lower()
    )
    for lettre in lettres:
        dateBNF_210d = dateBNF_210d.replace(lettre, "~")
        dateBNF_306a = dateBNF_306a.replace(lettre, "~")
    for signe in ponctuation:
        dateBNF_210d = dateBNF_210d.replace(signe, "~")
        dateBNF_306a = dateBNF_306a.replace(signe, "~")
    dateBNF_210d = [el for el in dateBNF_210d.split("~") if el != ""]
    dateBNF_306a = [el for el in dateBNF_306a.split("~") if el != ""]
    for date in dateBNF_210d:
        if main.RepresentsInt(date) is True:
            date = int(date)
            dateBNF.extend([date + 1, date - 1])
    for date in dateBNF_306a:
        if main.RepresentsInt(date) is True:
            date = int(date)
            dateBNF.extend([date + 1, date - 1])
    dateBNF.extend(dateBNF_210d)
    dateBNF.extend(dateBNF_306a)
    dateBNF = " ".join([str(date) for date in dateBNF])
    if len(str(date_init)) > 3 and str(date_init)[0:4] in dateBNF:
        ark_checked = ark
    elif (date_init in dateBNF):
        ark_checked = ark
    return ark_checked


def comparaisonTitres_sous_zone(
    input_record,
    NumNot,
    ark_current,
    systemid,
    isbn,
    titre,
    auteur,
    date,
    recordBNF,
    origineComparaison,
    sous_zone,
):
    ark = ""
    if ("+" in sous_zone):
        titreBNF = ""
        for f in sous_zone.split("+"):
            titreBNF += funcs.nettoyageTitrePourControle(
                                                         sru.record2fieldvalue(recordBNF, f.split("~")[0])
                                                        )

    else:
        titreBNF = funcs.nettoyageTitrePourControle(sru.record2fieldvalue(recordBNF, 
                                                                          sous_zone.split("~")[0])
                                                   )
    text_method_alignment = ""
    # print(titre, titreBNF, sous_zone)
    if titre != "" and titreBNF != "":
        if titre == titreBNF:
            ark = ark_current
            text_method_alignment = origineComparaison + " + contrôle Titre " + sous_zone
            if len(titre) < 5:
                # NumNotices2methode[NumNot].append("[titre court]")
                input_record.alignment_method.append("[titre court]")
        elif titre[0: round(len(titre) / 2)] == titreBNF[
                                                0: round(len(titre) / 2)]:
            ark = ark_current
            text_method_alignment = origineComparaison + " + contrôle Titre " + sous_zone
            if round(len(titre) / 2) < 10:
                text_method_alignment += "".join(["[demi-titre",
                                                  "-",
                                                  str(round(len(titre) / 2)),
                                                  " caractères]"])
        elif titreBNF in titre:
            text_method_alignment = origineComparaison + " + contrôle : Titre BnF/Sudoc \
contenu dans titre initial"
            ark = ark_current
        elif titre in titreBNF:
            text_method_alignment = origineComparaison + " + contrôle Titre initial \
contenu dans titre BnF/Sudoc"
            ark = ark_current
    elif (titre == "" and input_record.titre.controles == ""):
        ark = ark_current
        text_method_alignment = origineComparaison + " + pas de titre initial pour comparer"
    elif (titre == "" and input_record.titre.controles != ""):
        ark = ark_current
        text_method_alignment = origineComparaison + " | Problèmes dans métadonnées Titre-Auteur-Date-Volume"
    return ark, text_method_alignment


# Recherche par n° système. Si le 3e paramètre est "False", c'est qu'on a pris
# uniquement le FRBNF initial, sans le tronquer.
# Dans ce cas, et si 0 résultat pertinent, on relance la recherche avec
# info tronqué


def systemid2ark(input_record, NumNot, systemid, tronque, isbn, titre, auteur, date):
    listeARK = []
    results = sru.SRU_result(f'bib.otherid all "{systemid}"')
    for ark_current in results.dict_records:
        zones9XX = [str(i) for i in range(900, 1000)]
        for zone in zones9XX:
            for zone9XX in record.xpath(f"*[@tag='{zone}']"):
                local_val = sru.field2subfield(zone9XX, "a")
                if local_val == systemid:
                    listeARK.append(comparerBibBnf(input_record,
                                                    NumNot,
                                                    ark_current,
                                                    systemid,
                                                    isbn,
                                                    titre,
                                                    auteur,
                                                    date,
                                                    "Ancien n° notice"
                                                    )
                                    )
    

    # Si pas de réponse, on fait la recherche SystemID + Auteur
    if listeARK == []:
        listeARK = relancerNNBAuteur(input_record, NumNot, systemid, isbn,
                                     titre, auteur, date)

    # Si à l'issue d'une première requête sur le numéro système dont on a
    # conservé la clé ne donne rien -> on recherche sur le numéro tronqué
    # comme numéro système
    if (listeARK == []
       and not tronque):
        listeARK = systemid2ark(input_record, NumNot, systemid[:-1],
                                True, isbn, titre, auteur, date)
    listeARK = ",".join([ark for ark in listeARK if ark])
    return listeARK


def rechercheNNB(input_record, nnb):
    ark = []
    if nnb.isdigit() is False:
        # pb_frbnf_source.write("\t".join[NumNot,nnb] + "\n")
        ark = "Pb FRBNF"
    elif 30000000 < int(nnb) < 50000000:
        sru_result = sru.SRU_result(f"bib.recordid any \"{nnb}\"")
        identifier = ""
        if input_record.type == "TEX":
            identifiant = input_record.isbn.propre
        elif (input_record.type == "VID" 
              or input_record.type == "AUD"
              or input_record.type == "CAR"
              or input_record.type == "PAR"):
            identifiant = input_record.ean.propre
        elif input_record.type == "PER":
            identifiant = input_record.issn.propre
        for ark_current in sru_result.dict_records:
            ark.append(comparerBibBnf(
                                    input_record,
                                    input_record.NumNot,
                                    ark_current,
                                    sru_result.dict_records[ark_current],
                                    nnb,
                                    identifiant,
                                    input_record.titre_nett,
                                    input_record.auteur_nett,
                                    input_record.date_nett,
                                    "Numéro de notice",
                                    )
                          )
    ark = ",".join([el for el in ark if el])
    return ark


# Si le FRBNF n'a pas été trouvé, on le recherche comme numéro système ->
# pour ça on extrait le n° système


def oldfrbnf2ark(input_record):
    """Extrait du FRBNF le numéro système, d'abord sur 9 chiffres,
    puis sur 8 si besoin, avec un contrôle des résultats sur le
    contenu du titre ou sur l'auteur"""
    systemid = input_record.frbnf.propre.upper().replace("FRBNF","").replace("FRBNF", "")[0:8]
    ark = rechercheNNB(input_record, systemid[0:8])
    if ark == "":
        ark = systemid2ark(
            input_record,
            input_record.NumNot,
            systemid,
            False,
            input_record.isbn.nett,
            input_record.titre_nett,
            input_record.auteur_nett,
            input_record.date_nett,
        )
    return ark


def frbnf2ark(input_record):
    """Rechercher le FRBNF avec le préfixe "FRBN" ou "FRBNF".

    A défaut, lance d'autres fonctions pour lancer la recherche en utilisant
    uniquement le numéro, soit comme NNB/NNA, soit comme ancien
    numéro système (en zone 9XX)"""
    ark = ""
    if input_record.frbnf.propre[0:4].lower() == "frbn":
        sru_result = sru.SRU_result(f'bib.otherid all "{input_record.frbnf.propre}"')
        if sru_result.nb_results == 0:
            ark = oldfrbnf2ark(input_record)
        else:
            ark = ",".join(sru_result.list_identifiers)
            input_record.alignment_method.append("FRBNF > ARK")
    return ark


def row2file(liste_metadonnees, liste_reports):
    metas2report = [str(el) for el in liste_metadonnees]
    if ("timestamp" in main.prefs
       and main.prefs["timestamp"]["value"] == "True"):
        timest = funcs.timestamp()
        metas2report.append(timest)
    liste_reports[0].write("\t".join(metas2report) + "\n")
    return metas2report


def row2files(liste_metadonnees, liste_reports):
    # [
    #     "NumNot", "nbARK", "ark trouvé", "Méthode", "ark initial", "FRBNF",
    #     "ISBN", "EAN", "Titre", "auteur", "date", "Tome/Volume", "editeur"
    # ]
    # Le paramètre header sert à préciser s'il s'agit d'ajouter dans le fichier
    # les entêtes de colonnes (et non les résultats de l'alignement)
    liste_metadonnees_to_report = [str(el) for el in liste_metadonnees]
    nbARK = liste_metadonnees[1]
    ark = liste_metadonnees[2]
    if ark == "Pb FRBNF":
        liste_reports[0].write("\t".join(liste_metadonnees_to_report) + "\n")
    elif nbARK == 0:
        liste_reports[1].write("\t".join(liste_metadonnees_to_report) + "\n")
    elif nbARK == 1:
        liste_reports[2].write("\t".join(liste_metadonnees_to_report) + "\n")
    elif nbARK == "Nb identifiants trouvés":
        liste_reports[0].write("\t".join(liste_metadonnees_to_report) + "\n")
        liste_reports[1].write("\t".join(liste_metadonnees_to_report) + "\n")
        liste_reports[2].write("\t".join(liste_metadonnees_to_report) + "\n")
        liste_reports[3].write("\t".join(liste_metadonnees_to_report) + "\n")
    else:
        liste_reports[3].write("\t".join(liste_metadonnees_to_report) + "\n")


def isbn2sru(input_record, NumNot, isbn, titre, auteur, date):
    listeARK = []
    results = sru.SRU_result(f'bib.isbn all "{isbn}"')
    
    for ark_current in results.dict_records:
        ark = comparaisonTitres(
            input_record,
            NumNot,
            ark_current,
            "",
            isbn,
            titre,
            auteur,
            date,
            "",
            results.dict_records[ark_current],
            "ISBN",
        )
        # NumNotices2methode[NumNot].append("ISBN > ARK")
        listeARK.append(ark)
    if (listeARK == [""] and auteur != ""):
        listeARK = isbnauteur2sru(input_record, NumNot, isbn, titre, auteur, date)
    listeARK = ",".join([ark for ark in listeARK if ark])
    return listeARK


def isbnauteur2sru(input_record, NumNot, isbn, titre, auteur, date):
    """Si la recherche ISBN avec contrôle titre n'a rien donné,
    on recherche ISBN + le mot le plus long dans la zone "auteur",
    et pas de contrôle sur Titre ensuite
    """
    motlongauteur = funcs.nettoyageAuteur(auteur, True)
    urlSRU = funcs.url_requete_sru(
        'bib.isbn all "' + isbn + '" and bib.author all "'
        + motlongauteur + '"'
    )
    results = sru.SRU_result(f'bib.isbn all "{isbn}" and bib.author all "{motlongauteur}"')
    for ark_current in results.dict_records:
        ark = checkDate(ark_current, date, results.dict_records[ark_current])
        if ark:
            listeARK.append(ark)
    if (listeARK):
        input_record.alignment_method.append("ISBN + Auteur > ARK")
    return listeARK


def eanauteur2sru(input_record, NumNot, ean, titre, auteur, date):
    """Si la recherche EAN avec contrôle titre n'a rien donné,
    on recherche EAN + le mot le plus long dans la zone "auteur",
    et pas de contrôle sur Titre ensuite
    """
    motlongauteur = funcs.nettoyageAuteur(auteur, True)
    results = sru.SRU_result(f'bib.ean all "{ean}" and bib.author all "{motlongauteur}"')
    if results.list_identifiers:
        input_record.alignment_method.append("EAN + Auteur > ARK")
    return ",".join(results.list_identifiers)


def isbn_anywhere2sru(input_record, NumNot, isbn, titre, auteur, date):
    """
    Si l'ISBN n'a été trouvé ni dans l'index ISBN, ni dans l'index EAN
    on le recherche dans tous les champs (not. les données d'exemplaires,
    pour des réimpressions achetées par un département de la Direction des
    collections de la BnF)
    """
    results = sru.SRU_result(f'bib.anywhere all "{isbn}"')
    for ark_current in results.dict_records:
        ark = comparaisonTitres(
            input_record,
            NumNot,
            ark_current,
            "",
            isbn,
            titre,
            auteur,
            date,
            "",
            results.dict_records[ark_current],
            "ISBN dans toute la notice",
        )
        if ark:
            listeARK.append(ark)
    listeARK = ",".join([ark for ark in listeARK if ark])
    return listeARK


def isbn2sudoc(input_record, parametres):
    """A partir d'un ISBN, recherche dans le Sudoc.

    Pour chaque notice trouvée, on regarde sur la notice Sudoc a un ARK BnF ou
    un FRBNF, auquel cas on convertit le PPN en ARK. Sinon, on garde le(s) PPN
    """
    url = "https://www.sudoc.fr/services/isbn2ppn/" + input_record.isbn.propre
    Listeppn = []
    isbnTrouve = funcs.testURLretrieve(url)
    ark = []
    if isbnTrouve:
        (test, resultats) = funcs.testURLetreeParse(url)
        if test and resultats.find(".//ppn") is not None:
            for ppn in resultats.xpath("//ppn"):
                ppn_val = check_ppn_by_kw(ppn.text, input_record, "isbn2ppn")
                if (ppn_val):
                    Listeppn.append("PPN" + ppn_val)
                    # Si BnF > Sudoc : on cherche l'ARK dans
                    # la notice Sudoc trouvée
                    if parametres["preferences_alignement"] == 1:
                        ark.append(
                            ppn2ark(
                                input_record,
                                ppn_val,
                                parametres
                            )
                        )
            if Listeppn == "" and ark == []:
                url = (
                    "https://www.sudoc.fr/services/isbn2ppn/"
                    + input_record.isbn.converti
                )
                isbnTrouve = funcs.testURLretrieve(url)
                if isbnTrouve:
                    (test, resultats) = funcs.testURLetreeParse(url)
                    if test:
                        for ppn in resultats.xpath("//ppn"):
                            ppn_val = ppn.text
                            Listeppn.append("PPN" + ppn_val)
                            # Si BnF > Sudoc : on cherche l'ARK
                            # dans la notice Sudoc trouvée
                            if parametres["preferences_alignement"] == 1:
                                ark = ppn2ark(
                                    input_record,
                                    ppn_val,
                                    parametres
                                )
                            if Listeppn != []:
                                add_to_conversionIsbn(
                                    input_record.NumNot,
                                    input_record.isbn.propre,
                                    input_record.isbn.converti,
                                    True,
                                )
    # Si on trouve un PPN, on ouvre la notice pour voir s'il n'y a pas un ARK
    # déclaré comme équivalent --> dans ce cas on récupère l'ARK
    Listeppn = ",".join([ppn for ppn in Listeppn if ppn])
    ark = ",".join([ark1 for ark1 in ark if ark1])
    if ark != "":
        return ark
    else:
        return Listeppn


def ean2sudoc(input_record, parametres, controle_titre=True):
    """A partir d'un EAN, recherche dans le Sudoc.

    Pour chaque notice trouvée, on regarde sur la notice Sudoc a un ARK BnF ou
    un FRBNF, auquel cas on convertit le PPN en ARK. Sinon, on garde le(s)
    PPN
    """
    url = "https://www.sudoc.fr/services/ean2ppn/" + input_record.ean.propre
    Listeppn = []
    eanTrouve = funcs.testURLretrieve(url)
    ark = []
    if eanTrouve:
        (test, resultats) = funcs.testURLetreeParse(url)
        if test:
            for ppn in resultats.xpath("//ppn"):
                ppn_val = check_ppn_by_kw(ppn.text, input_record, "ean2ppn")
                if (ppn_val):
                    Listeppn.append("PPN" + ppn_val)
                    # NumNotices2methode[NumNot].append("EAN > PPN")
                    # input_record.alignment_method.append("EAN > PPN")
                    # Si BnF > Sudoc : on cherche l'ARK
                    # dans la notice Sudoc trouvée
                    if parametres["preferences_alignement"] == 1:
                        temp_record = funcs.Bib_record(
                            [
                            input_record.NumNot, "", "", "", input_record.ean.propre,
                            input_record.titre_nett, input_record.auteur_nett,
                            input_record.date_nett, "", ""
                            ],
                            parametres["type_doc_bib"]
                            )
                        ark.append(
                                ppn2ark(temp_record, ppn_val, parametres)
                                )
    # Si on trouve un PPN, on ouvre la notice pour voir s'il n'y a pas un ARK
    # déclaré comme équivalent --> dans ce cas on récupère l'ARK
    Listeppn = ",".join([ppn for ppn in Listeppn if ppn != ""])
    ark = ",".join([ark1 for ark1 in ark if ark1 != ""])
    if ark != "":
        return ark
    else:
        return Listeppn


def ppn2ark(input_record, ppn, parametres):
    ark = ""
    ppn = ppn.replace("PPN", "")
    url = "https://www.sudoc.fr/" + ppn + ".rdf"
    (test, record) = funcs.testURLetreeParse(url)
    if test:
        for sameAs in record.xpath("//owl:sameAs", namespaces=main.nsSudoc):
            resource = sameAs.get(
                "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"
            )
            if resource.find("ark:/12148/") > 0:
                ark = resource[24:46]
                # NumNotices2methode[input_record.NumNot].append("PPN > ARK")
                input_record.alignment_method.append("PPN > ARK")
        if ark == "":
            for frbnf in record.xpath("//bnf-onto:FRBNF",
                                      namespaces=main.nsSudoc):
                frbnf_val = frbnf.text
                # NumNotices2methode[input_record.NumNot].append("PPN > FRBNF")
                input_record.alignment_method.append("PPN > FRBNF")
                temp_record = funcs.Bib_record(
                    [
                     input_record.NumNot, frbnf_val,
                     "", input_record.isbn.init, "",
                     input_record.titre.init,
                     input_record.auteur,
                     input_record.date, "", ""
                    ],
                    parametres["type_doc_bib"]
                )
                ark = frbnf2ark(temp_record)
    return ark


def add_to_conversionIsbn(NumNot, isbn_init, isbn_trouve, via_Sudoc=False):
    NumNotices_conversionISBN[NumNot]["isbn initial"] = isbn_init
    NumNotices_conversionISBN[NumNot]["isbn trouvé"] = isbn_trouve
    NumNotices_conversionISBN[NumNot]["via Sudoc"] = str(via_Sudoc)


def isbn2ark(input_record,
             NumNot, isbn_init, isbn_propre, isbn_converti,
             titre_nett, auteur_nett, date_nett):
    # Recherche sur l'ISBN tel que saisi dans la source
    resultatsIsbn2ARK = isbn2sru(input_record, NumNot, 
                                 isbn_init, titre_nett,
                                 auteur_nett, date_nett)
    # Requête sur l'ISBN dans le SRU, avec contrôle sur Titre ou auteur
    if resultatsIsbn2ARK == "" and isbn_init != isbn_propre:
        resultatsIsbn2ARK = isbn2sru(input_record,
                                     NumNot, isbn_propre, 
                                     titre_nett, auteur_nett,
                                     date_nett)

    # isbnConverti = conversionIsbn(input_record.isbn.propre)
    # Si pas de résultats : on convertit l'ISBN en 10 ou 13 et on relance une
    # recherche dans le catalogue BnF
    if resultatsIsbn2ARK == "":
        resultatsIsbn2ARK = isbn2sru(input_record, NumNot, 
                                     isbn_converti, titre_nett,
                                     auteur_nett, date_nett)
        if resultatsIsbn2ARK != "":
            add_to_conversionIsbn(NumNot, isbn_init, isbn_converti, False)
    # Si pas de résultats et ISBN 13 : on recherche sur EAN
    if resultatsIsbn2ARK == "" and len(isbn_propre) == 13:
        resultatsIsbn2ARK = ean2ark(input_record,
            NumNot, isbn_propre, titre_nett, auteur_nett, date_nett
        )
    if resultatsIsbn2ARK == "" and len(isbn_converti) == 13:
        resultatsIsbn2ARK = ean2ark(input_record,
            NumNot, isbn_converti, titre_nett, auteur_nett, date_nett
        )
        if resultatsIsbn2ARK != "":
            add_to_conversionIsbn(NumNot, isbn_init, isbn_converti, False)

    # Si pas de résultats et ISBN 13 : on recherche l'ISBN dans tous les
    # champs (dont les données d'exemplaire)
    if resultatsIsbn2ARK == "":
        resultatsIsbn2ARK = isbn_anywhere2sru(input_record, NumNot, isbn_propre,
                                              titre_nett, auteur_nett, date_nett)
    if resultatsIsbn2ARK == "" and len(isbn_converti) == 13:
        resultatsIsbn2ARK = isbn_anywhere2sru(input_record, NumNot, isbn_converti,
                                              titre_nett, auteur_nett, date_nett)
        if resultatsIsbn2ARK != "":
            add_to_conversionIsbn(NumNot, isbn_init, isbn_converti, False)

    return resultatsIsbn2ARK


def issn2ark(input_record, NumNot, issn_init, issn, titre, auteur, date):
    listeArk = issn2sru(input_record, NumNot, issn_init)
    if listeArk == "":
        listeArk = issn2sru(input_record, NumNot, issn)
    return listeArk


def issn2sru(input_record, NumNot, issn):
    listeArk = []
    results = sru.SRU_result(f'bib.issn adj "{issn}"')
    for ark_current in results.dict_records:
        record = results.dict_records[ark_current]
        typeNotice = main.extract_leader(record, 7)
        if typeNotice == "s":
            test_issn = check_issn_in_011a(record, issn)
            if test_issn:
                input_record.alignment_method.append("ISSN")
                listeArk.append(ark_current)
            else:
                input_record.alignment_method.append("ISSN de lien ou erroné")
                listeArk.append(ark_current)
    listeArk = ",".join([ark for ark in listeArk if ark])
    return listeArk


def check_issn_in_011a(record, issn):
    f011a = sru.record2fieldvalue(record, "011$a")
    print(f011a)
    if (issn[0:4] in f011a):
        return True
    else:
        return False

def issn2sudoc(input_record, NumNot, issn_init, issn_nett, 
               titre, auteur, date, parametres):
    """A partir d'un ISSN, recherche dans le Sudoc.

    Pour chaque notice trouvée, on regarde sur la notice Sudoc a un ARK BnF ou
    un FRBNF, auquel cas on convertit le PPN en ARK. Sinon, on garde le(s) PPN
    """
    url = "https://www.sudoc.fr/services/issn2ppn/" + issn_nett
    Listeppn = []
    issnTrouve = funcs.testURLretrieve(url)
    ark = []
    if issnTrouve:
        (test, resultats) = funcs.testURLetreeParse(url)
        if test:
            # if resultats.find("//ppn") is not None:
                # NumNotices2methode[NumNot].append("ISSN > PPN")
                # input_record.alignment_method.append("ISSN > PPN")
            for ppn in resultats.xpath("//ppn"):
                ppn_val = check_ppn_by_kw(ppn.text, input_record, "issn2ppn")
                if (ppn_val):
                    Listeppn.append("PPN" + ppn_val)
                    if (parametres["preferences_alignement"] == 1):
                        temp_record = funcs.Bib_record(
                                                        [
                                                            NumNot,
                                                            "",
                                                            "",
                                                            issn_nett,
                                                            titre,
                                                            auteur,
                                                            date
                                                        ],
                                                        parametres["type_doc_bib"]
                                                        )
                        ark.append(ppn2ark(temp_record, ppn_val, parametres))
    # Si on trouve un PPN, on ouvre la notice pour voir s'il n'y a pas un ARK
    # déclaré comme équivalent --> dans ce cas on récupère l'ARK
    Listeppn = ",".join([ppn for ppn in Listeppn if ppn != ""])
    ark = ",".join([ark1 for ark1 in ark if ark1 != ""])
    if ark != "":
        return ark
    else:
        return Listeppn


def ark2metas(ark, unidec=True):
    url = funcs.url_requete_sru('bib.persistentid any "' + ark + '"')
    if (ark.lower().startswith("ppn")):
        url = "https://www.sudoc.fr/" + ark[3:] + ".xml"
    (test, record) = funcs.testURLetreeParse(url)
    titre = ""
    premierauteurPrenom = ""
    premierauteurNom = ""
    tousauteurs = ""
    date = ""
    typeSupport = ""
    dic_182c = {"s": "audio",
                "c": "informatique",
                "h": "microforme",
                "p": "microscopique",
                "g": "projeté",
                "e": "stéréoscopique",
                "v": "vidéo",
                "x": "autre",
                "n": "sans médiation"}
    dic_183a = {"caa": "Bobine de bande informatique",
            "cab": "Cartouche informatique",
            "cac": "Cassette de bande informatique",
            "cad": "Dispositif électronique autonome",
            "cae": "Mémoire USB",
            "caf": "Puce RFID",
            "caz": "Support numérique manipulable (générique)",
            "cba": "Carte mémoire",
            "cbb": "Carte mémoire propriétaire",
            "cca": "Cartouche de jeu",
            "cda": "Blu-ray disc",
            "cdb": "Blu-ray disc propriétaire",
            "cdc": "CD-I",
            "cdd": "CD-Photo",
            "cde": "CD-ROM",
            "cdf": "CD-ROM propriétaire",
            "cdg": "CDTV",
            "cdh": "Disque optique hybride",
            "cdi": "Disquette",
            "cdj": "Disquette propriétaire",
            "cdk": "DVD-ROM",
            "cdl": "DVD-ROM propriétaire",
            "cea": "Clé de licence de produit numérique",
            "ceb": "Ressource dématérialisée",
            "czz": "Autre support électronique",
            "eaa": "Carte stéréoscopique",
            "eab": "Disque stéréoscopique",
            "eac": "Plaque stéréoscopique",
            "ezz": "Autre support stéréoscopique",
            "gab": "Bobine de film",
            "gac": "Cartouche de film fixe",
            "gad": "Diapositive",
            "gae": "Film fixe",
            "gaf": "Film fixe court",
            "gag": "Rouleau de film",
            "gah": "Transparent pour rétroprojecteur",
            "gaz": "Film ou transparent (générique)",
            "gba": "Plaque de lanterne magique",
            "gzz": "Autre support pour les images projetées",
            "haa": "Carte à fenêtre",
            "hab": "Cassette de microfiches",
            "hac": "Micro-opaque",
            "had": "Microfiche",
            "haz": "Microforme (générique)",
            "hba": "Bande de microfilm",
            "hbb": "Bobine de microfilm",
            "hbc": "Cartouche de microfilm",
            "hbd": "Cassette de microfilm",
            "hbe": "Rouleau de microfilm",
            "hbz": "Microfilm",
            "hzz": "Autre support pour les microformes",
            "naa": "Carte",
            "nba": "Bande de film photographique",
            "nbb": "Bobine de film photographique",
            "nbc": "Rouleau de film photographique",
            "nbz": "Film photographique (terme générique)",
            "nca": "Tableau à feuilles mobiles",
            "nda": "Feuille",
            "ndb": "Autocollant",
            "ndc": "Dépliant",
            "ndd": "Transparent",
            "nea": "Appareil (terme générique)",
            "neb": "Globe",
            "nec": "Kit",
            "ned": "Maquette",
            "nef": "Matrice",
            "neg": "Objet numismatique",
            "neh": "Panneau",
            "nei": "Panneau dépliant",
            "nej": "Plaque",
            "nek": "Plaque photographique",
            "nel": "Plateau de jeu",
            "nez": "Objet",
            "nfa": "Rouleau",
            "nga": "Volume",
            "ngb": "Brochure",
            "ngc": "Fascicule",
            "nzz": "Autre support sans médiation",
            "paa": "Lame pour microscope",
            "pzz": "Autre support microscopique",
            "saa": "Bande magnétique audio",
            "sab": "Bobine de piste sonore",
            "sac": "Bande perforée pour instrument mécanique",
            "saz": "Support audio (générique)",
            "sba": "Cartouche audio",
            "sbb": "Bande TEFI",
            "sca": "Cassette audio analogique",
            "scb": "Cassette audio numérique",
            "sda": "Cylindre phonographique",
            "sdb": "Fil magnétique",
            "sdc": "Ruban métallique magnétique",
            "sea": "CD audio",
            "seb": "CD-Extra",
            "sec": "Disque audio",
            "sed": "DVD audio",
            "see": "Feuille acoustique",
            "sef": "MiniDisc",
            "seg": "Blu-ray audio",
            "szz": "Autre support vidéo",
            "vaa": "Bande vidéo",
            "vaz": "Vidéo (Terme générique)",
            "vba": "Cassette vidéo",
            "vbb": "Cassette vidéo numérique",
            "vca": "Blu-ray vidéo",
            "vcb": "Disque vidéo",
            "vcc": "DVD vidéo",
            "vcd": "HD DVD",
            "vce": "Vidéo CD",
            "vzz": "Autre support vidéo"}
    if test:
        titre = sru.record2fieldvalue(record, "200$a")
        titre_compl = sru.record2fieldvalue(record, "200$e")
        if (titre_compl):
            titre += titre_compl
        premierauteurNom = sru.record2fieldvalue(record, "700$a")
        premierauteurPrenom = sru.record2fieldvalue(record, "700$b")
        if not premierauteurNom:
            premierauteurNom = sru.record2fieldvalue(record, "710$a")
            premierauteurPrenom = sru.record2fieldvalue(record, "710$b")
        tousauteurs = sru.record2fieldvalue(record, "200$f")
        date = sru.record2fieldvalue(record, "210$d")
        typemedia182 = sru.record2fieldvalue(record, "182$c")
        typesupport183 = sru.record2fieldvalue(record, "183$a")
        if typemedia182 in dic_182c:
            typemedia182 = dic_182c[typemedia182]
        if typesupport183 in dic_183a:
            typesupport183 = dic_183a[typesupport183]
        typeSupport = ",".join([typemedia182, typesupport183]).strip(",")
    metas = [titre, premierauteurPrenom, premierauteurNom,
             tousauteurs, date, typeSupport]
    if unidec:
        metas = [funcs.unidecode_local(meta) for meta in metas]
    return metas


def ppn2metas(ppn):
    ppn = ppn.replace("PPN", "")
    url = "https://www.sudoc.fr/" + ppn + ".rdf"
    (test, record) = funcs.testURLetreeParse(url)
    titre = ""
    premierauteurPrenom = ""
    premierauteurNom = ""
    tousauteurs = ""
    if test:
        if record.find("//dc:title", namespaces=main.nsSudoc) is not None:
            titre = (
                funcs.unidecode_local(record.find("//dc:title",
                                      namespaces=main.nsSudoc).text)
                .split("[")[0]
                .split("/")[0]
            )
            tousauteurs = funcs.unidecode_local(
                record.find("//dc:title", namespaces=main.nsSudoc).text
            ).split("/")[1]
            if titre[0:5] == tousauteurs[0:5]:
                tousauteurs = ""
        if (
            record.find("//marcrel:aut/foaf:Person/foaf:name", namespaces=main.nsSudoc)
            is not None
        ):
            premierauteurNom = funcs.unidecode_local(
                record.find(
                    "//marcrel:aut/foaf:Person/foaf:name", namespaces=main.nsSudoc
                ).text
            ).split(",")[0]
            if (
                record.find(
                    "//marcrel:aut/foaf:Person/foaf:name", namespaces=main.nsSudoc
                ).text.find(",")
                > 0
            ):
                premierauteurPrenom = funcs.unidecode_local(
                    record.find(
                        "//marcrel:aut/foaf:Person/foaf:name", namespaces=main.nsSudoc
                    ).text
                ).split(",")[1]
            if premierauteurPrenom.find("(") > 0:
                premierauteurPrenom = premierauteurPrenom.split("(")[0]
    return [titre, premierauteurPrenom, premierauteurNom, tousauteurs]


def tad2ark(input_record, parametres, 
            anywhere=False, annee_plus_trois=False):
    """Fonction d'alignement par Titre-Auteur-Date
    (et contrôles sur type Notice, sur n° de volume si nécessaire)
    
    En entrée : le numéro de notice, le titre (qu'il faut nettoyer pour la recherche)
    L'auteur = zone auteur initiale, ou à défaut auteur_nett
    date_nett
    
    Cas des périodiques = on récupère uniquement la première date
    Si elle est sur moins de 4 caractères (19.. devenu 19, 196u devenu 196)
       -> on tronque
    """

    listeArk = []

    index = ""
    param_date, date_nett = tad2ark_date(input_record, annee_plus_trois)
    if input_record.titre.recherche != "":
        auteur = input_record.auteur
        auteur_nett = input_record.auteur_nett
        pubPlace_nett = input_record.pubPlace_nett
        if input_record.auteur == "":
            auteur = "-"
        if auteur_nett == "":
            auteur_nett = "-"
        if pubPlace_nett == "":
            pubPlace_nett = "-"
        search_query = [f'bib.title all "{input_record.titre.recherche}"',
                        f'bib.author all "{auteur}"',
                        f'bib.date {param_date} "{date_nett}"',
                        f'bib.publisher all "{pubPlace_nett}"',
                        f'bib.doctype any "{input_record.intermarc_type_doc}"'
                       ]
        if anywhere:
            search_query = [f'bib.anywhere all "{input_record.titre.recherche} {auteur} {pubPlace_nett}"',
                            f'bib.anywhere {param_date} "{date_nett}"',
                            f'bib.doctype any "{input_record.intermarc_type_doc}"'
                           ]
            index = " dans toute la notice"

        # Ajout du critère Echelle pour les cartes
        if (input_record.type == "CP"
           and input_record.scale):
            search_query.append(f'bib.anywhere all "{input_record.scale}"')
        search_query = " and ".join(search_query)
        results = sru.SRU_result(search_query)
        if (results.nb_results == 0):
            search_query = [f'bib.title all "{input_record.titre.recherche}"',
                            f'bib.author all "{auteur_nett}"',
                            f'bib.date {param_date} "{date_nett}"',
                            f'bib.publisher all "{pubPlace_nett}"',
                            f'bib.doctype any "{input_record.intermarc_type_doc}"'
                           ]
            if anywhere:
                search_query = [f'bib.anywhere all "{input_record.titre.recherche} {auteur_nett} {pubPlace_nett}"',
                                f'bib.anywhere {param_date} "{date_nett}"',
                                f'bib.doctype any "{input_record.intermarc_type_doc}"'
                               ]
                index = " dans toute la notice"
            search_query = " ".join(search_query)
            results = sru.SRU_result(search_query)
        if results.list_identifiers:
            i = 1
            for ark_current in results.dict_records:
                if (results.nb_results > 100):
                    print(" "*4, input_record.NumNot, "-",
                          ark_current, f"{str(i)}/{str(results.nb_results)}",
                          "(limite max 1000)"),
                    i += 1
                ark_validated = tad2ark_controle_record(input_record, ark_current, 
                                                auteur, date_nett,
                                                annee_plus_trois, index,
                                                results.dict_records[ark_current])
                listeArk.append(ark_validated)

    listeArk = ",".join(ark for ark in listeArk if ark)
    # Si la liste retournée est vide, et qu'on est sur des périodiques
    # et que la date
    if (listeArk == ""
        and input_record.intermarc_type_record == "s"
        and not annee_plus_trois
    ):
        listeArk = tad2ark(input_record, parametres, 
                           anywhere=False, annee_plus_trois=True)
    return listeArk


def tad2ark_date(input_record, annee_plus_trois):
    """
    Définition du paramètre date (et option de recherche all/any)
    """
    date = input_record.date_nett
    if (input_record.intermarc_type_record == "s"
       and not annee_plus_trois):
        date = input_record.date_debut
    if (len(str(date)) < 4 and date != ""):
        date += "*"
    # Si on cherche l'année de début de périodique
    # en élargissant à une fourchette de dates
    # 3 ans avant et 3 ans après
    if annee_plus_trois:
        param_date = "any"
        date = input_record.dates_elargies_perios
    else:
        param_date = "all"
    if (date == ""):
        date = "-"
    return param_date, date


def tad2ark_controle_record(input_record, ark_current, 
                            auteur, date_nett, annee_plus_trois, index, 
                            xml_record):
    """
    Ensemble de contrôles sur une notice BnF trouvée par une recherche 
    Titre-Auteur-Date
    """
    ark = ""
    typeRecord_current = main.extract_leader(xml_record, 7)
    if (type(input_record) == funcs.Bib_record
        and typeRecord_current == input_record.intermarc_type_record):
            ark = comparaisonTitres(input_record,
                                    input_record.NumNot,
                                    ark_current,
                                    "",
                                    "",
                                    input_record.titre.controles,
                                    auteur,
                                    date_nett,
                                    input_record.tome_nett,
                                    xml_record,
                                    "Titre-Auteur-Date" + index)
            if (ark != "" and date_nett != "-"):
                ark = checkDate(ark, input_record.date_nett,
                                xml_record)
            if ark != "":
                if "*" in date_nett:
                    input_record.alignment_method.append("Date début tronquée")
                if annee_plus_trois:
                    input_record.alignment_method.append("Date début +/- 3 ans")
    elif (type(input_record) == funcs.Bib_Aut_record):
        ark = comparaisonTitres(input_record,
                                input_record.NumNot,
                                ark_current,
                                "",
                                "",
                                input_record.titre.controles,
                                auteur,
                                date_nett,
                                "",
                                xml_record,
                                "Titre-Auteur-Date" + index)
    if (ark and input_record.isbn.propre):
        input_record.alignment_method.append("Problème ISBN non reconnu")
    if (ark and input_record.ean.propre):
        input_record.alignment_method.append("Problème EAN non reconnu")
    if (ark and input_record.issn.propre):
        input_record.alignment_method.append("Problème ISSN non reconnu")
    return ark


def tad2ppn_from_domybiblio(input_record, parametres):
    # Recherche dans DoMyBiblio : Titre & Auteur dans tous champs, Date dans
    # un champ spécifique
    Listeppn = []
    ark = []

    typeRecord4DoMyBiblio = "all"
    """all (pour tous les types de document),
           B (pour les livres),
           T (pour les périodiques),
           Y (pour les thèses version de soutenance),
           V (pour le matériel audio-visuel)"""
    typeRecordDic = {"TEX": "B", "VID": "V", "AUD": "V",
                     "PER": "T", "CP": "K", "PAR": "M"}
    if input_record.type in typeRecordDic:
        typeRecord4DoMyBiblio = typeRecordDic[input_record.type]
    kw = " ".join([input_record.titre.recherche, input_record.auteur_nett])

    # On prévoit 2 URL : par défaut, requête sur l'API DoMyBiblio (XML)
    # Si plante > screenscraping de DoMyBiblio version HTML
    url1 = "".join(
        [
            "http://domybiblio.net/search/search_api.php?type_search=all&q=",
            urllib.parse.quote(kw),
            "&type_doc=",
            typeRecord4DoMyBiblio,
            "&period=",
            input_record.date_debut,
            "&pageID=1&wp=false&idref=false&loc=false",
        ]
    )

    url2 = "".join(
        [
            "http://domybiblio.net/search/search.php?type_search=all&q=",
            urllib.parse.quote(kw),
            "&type_doc=",
            typeRecord4DoMyBiblio,
            "&period=",
            input_record.date_debut,
            "&pageID=1&wp=false&idref=false&loc=false",
        ]
    )
    try:
        type_page = "xml"
        page = etree.parse(request.urlopen(url1, timeout=5))
    except ConnectionResetError:
        type_page = "html"
        test, result = funcs.testURLurlopen(url2, display=False)
        if (test):
            page = parse(result)
        else:
        #    print("erreur XML timeout, puis erreur HTML")
            type_page = ""
    except socket.timeout:
        type_page = "html"
        test, result = funcs.testURLurlopen(url2, display=False)
        if (test):
            page = parse(result)
        else:
        #    print("erreur XML timeout, puis erreur HTML")
            type_page = ""
    except urllib.error.HTTPError:
        type_page = "html"
        test, result = funcs.testURLurlopen(url2, display=False)
        if (test):
            page = parse(result)
        else:
            type_page = ""
        #    print("erreur XML HTTPerror, puis erreur HTML")
    except urllib.error.URLError:
        type_page = "html"
        test, result = funcs.testURLurlopen(url2, display=False)
        if (test):
            page = parse(result)
        else:
            type_page = ""
        #    print("erreur XML HTTPerror, puis erreur HTML")
    except etree.XMLSyntaxError:
        # problème de conformité XML du résultat
        # type_page = "html"
        # page = parse(request.urlopen(url2))
        test, result = funcs.testURLurlopen(url2, display=False)
        if (test):
            page = parse(result)
        else:
            type_page = ""
        #    print("erreur XML SyntaxError, puis erreur HTML")
        # print("erreur XML", url1)
    except http.client.RemoteDisconnected:
        type_page = ""
        # print("erreur connexion DoMyBiblio", url1)
    if (type_page == "html"):
        liste_resultats = page.xpath("//li[@class='list-group-item']/a")
        for lien in liste_resultats:
            href = lien.get("href")
            ppn = "PPN" + href.split("/")[-1].split("&")[0].strip()
            if ("id=" in ppn):
                ppn = ppn[ppn.find("id="):].replace("id=", "").split("&")[0].strip()
            ppn = controle_keywords2ppn(input_record, ppn)
            Listeppn.append(ppn)
    elif (type_page == "xml"):
        liste_resultats = page.xpath("//records/record")
        nb_results = int(page.find(".//results").text)
        for record in liste_resultats:
            ppn = record.find("identifier").text
            ppn = controle_keywords2ppn(input_record, ppn)
            Listeppn.append(ppn)
        if nb_results > 10:
            tad2ppn_pages_suivantes(
                input_record,
                url1,
                nb_results,
                2,
                Listeppn,
            )
    # Si on trouve un PPN, on ouvre la notice pour voir s'il n'y a pas un ARK
    # déclaré comme équivalent --> dans ce cas on récupère l'ARK
    Listeppn = ",".join([ppn for ppn in Listeppn if ppn != ""])
    if (Listeppn):
        """NumNotices2methode[input_record.NumNot].append(
            "Titre-Auteur-Date DoMyBiblio")"""
        input_record.alignment_method.append("Titre-Auteur-Date DoMyBiblio")
    if (Listeppn and parametres["preferences_alignement"] == 1):
        for ppn in Listeppn.split(","):
            ark.append(ppn2ark(input_record, ppn, parametres))
    ark = ",".join([ark1 for ark1 in ark if ark1 != ""])
    if ark != "":
        # NumNotices2methode[input_record.NumNot].append("PPN > ARK")
        input_record.alignment_method.append("PPN > ARK")
        return ark
    else:
        return Listeppn



def tad2ppn_pages_suivantes(
    input_record,
    url,
    nb_results,
    pageID,
    Listeppn,
):
    url = url + "pageID=" + str(pageID)
    (test, results) = funcs.testURLetreeParse(url)
    if test:
        for record in results.xpath("//records/record"):
            ppn = "PPN" + record.find("identifier").text
            ppn = controle_keywords2ppn(input_record, ppn)
            Listeppn.append(ppn)
        if nb_results >= pageID * 10:
            tad2ppn_pages_suivantes(
                input_record,
                url,
                nb_results,
                pageID + 1,
                Listeppn,
            )
    return Listeppn


def tad2ppn(input_record, parametres):
    """
    Recherche par mots clés dans le Sudoc en parsant les pages HTML
    """    
    typeRecord4Sudoc = ""
    """vide (pour tous les types de document),
           B (pour les livres),
           T (pour les périodiques),
           Y (pour les thèses version de soutenance),
           V (pour le matériel audio-visuel)
           K (pour les cartes)
           M (partitions)"""
    typeRecordDic = {"TEX": "B", "VID": "V", 
                     "AUD": "V", "PER": "T",
                     "CP": "K", "PAR": "M"}
    url = "http://www.sudoc.abes.fr//DB=2.1/SET=18/TTL=1/CMD?ACT=SRCHM\
&MATCFILTER=Y&MATCSET=Y&NOSCAN=Y&PARSE_MNEMONICS=N&PARSE_OPWORDS=N&PARSE_OLDSETS=N\
&IMPLAND=Y&ACT0=SRCHA&screen_mode=Recherche\
&IKT0=1004&TRM0=" + urllib.parse.quote(input_record.auteur_nett) + "\
&ACT1=*&IKT1=4&TRM1=" + urllib.parse.quote(input_record.titre.recherche) + "\
&ACT2=*&IKT2=1016&TRM2=&ACT3=*&IKT3=1016&TRM3=&SRT=YOP" + "\
&ADI_TAA=&ADI_LND=&ADI_JVU=" + urllib.parse.quote(input_record.date_nett) + "\
& ADI_MAT = " + typeRecordDic[input_record.type]
    url = url.replace("ADI_MAT=B", "ADI_MAT=B&ADI_MAT=Y")
    url = url.replace("ADI_MAT=N", "ADI_MAT=N&ADI_MAT=G")
    listePPN = urlsudoc2ppn(url)
    listePPN = check_sudoc_results(input_record, listePPN)
    return listePPN


def check_sudoc_results(input_record, listePPN):
    """
    Pour une liste de PPN trouvée, vérifier ceux qui correspondent bien à la notice initiale
    """
    listePPN_checked = []
    for ppn in listePPN:
        ppn_checked = check_sudoc_result(input_record, ppn)
        if (ppn_checked):
            listePPN_checked.append(ppn_checked)
    listePPN_checked = ",".join(["PPN"+el for el in listePPN_checked if el])
    return listePPN_checked

def check_sudoc_result(input_record, ppn):
    """
    Vérification de l'adéquation entre un PPN et une notice en entrée
    """
    ppn_checked = ""
    test, xml_record = ppn2recordSudoc(ppn)
    if test:
        if (type(input_record) == funcs.Bib_record):
            ppn_checked = tad2ark_controle_record(input_record, ppn, 
                                    input_record.auteur_nett,
                                    input_record.date_nett, False, "",
                                    xml_record)
        elif (type(input_record) == funcs.Bib_Aut_record):
            ppn_checked = tad2ark_controle_record(input_record, ppn, 
                                    input_record.lastname.propre,
                                    input_record.pubdate_nett, False, "",
                                    xml_record)
    ppn_checked = ",".join([ppn for ppn in ppn_checked if ppn])            
    return ppn_checked


def urlsudoc2ppn(url):
    """
    Extrait l'ensemble des PPN (avec pagination des résultats)
    à partir d'une URL de requête dans le Sudoc
    """
    listePPN = []
    (test, page) = funcs.testURLurlopen(url, display=False, timeout_def=10)
    if test:
        page = parse(page)
        nb_results = extract_nb_results_from_sudoc_page(page)
        if nb_results > 100:
            nb_results = 100
        if nb_results == 1:
            listePPN = [extractPPNfromrecord(page)]
        else:
            listePPN = extractPPNfromsudocpage(page)
        i = 11
        while nb_results > i:
            url_f = url + "&FRST=" + str(i)
            test, following_page = funcs.testURLurlopen(url_f)
            if test:
                following_page = parse(following_page)
                listePPN.extend(extractPPNfromsudocpage(following_page, nb_results, i))
            i += 10
    return listePPN


def extractPPNfromrecord(page):
    """
    Si un seul résultat : l'URL Sudoc ouvre la notice détaillée
    --> on récupère le PPN dans le permalien
    """
    link = page.find("//link[@rel='canonical']").get("href")
    ppn = link.split("/")[-1]
    return ppn



def extract_nb_results_from_sudoc_page(html_page):
    """
    Renvoie le nombre de résultats affiché sur une page de résultats Sudoc
    html_page est le contenu parsé (avec lxml.html.parse()) d'une page HTML
    """
    nb_results = 0
    ligne_info = ""
    try:
        ligne_info = etree.tostring(html_page.find("//table[@summary='query info']/tr")).decode(encoding="utf-8")
    except ValueError:
        pass
    except TypeError:
        pass
    if ("<span>" in ligne_info):
        nb_results = ligne_info.split("<span>")[-1].split("&")[0]
        nb_results = int(nb_results)
    return nb_results


def extractPPNfromsudocpage(html_page, nb_results=0, i=0):
    """
    Renvoie une liste de PPN 
    à partir du code HTML d'une liste de résultats Sudoc
    html_page est le contenu parsé (avec lxml.html.parse()) d'une page HTML
    """
    listePPN = []
    for inp in html_page.xpath("//input[@name]"):
        if inp.get("name").startswith("ppn"):
            ppn = inp.get("value")
            listePPN.append(ppn)
    return listePPN




def controle_keywords2ppn(input_record, ppn):
    """Pour les notices obtenues en recherche par mot-clé
    via DoMyBiblio, il faut vérifier que les mots cherchés comme
    titre, auteur et date sont bien présents dans ces zones
    respectives, car la recherche est effectuée
    dans toute la notice """
    ppn_final = ""
    url_sudoc_record = "https://www.sudoc.fr/" + ppn.replace("PPN", "") + ".xml"
    (test, record_sudoc) = funcs.testURLetreeParse(url_sudoc_record)
    if (test):
        ppn_final = comparaisonTitres(input_record,
                                      input_record.NumNot,
                                      ppn,
                                      "",
                                      "",
                                      input_record.titre.controles,
                                      input_record.auteur,
                                      input_record.date_nett,
                                      input_record.tome_nett,
                                      record_sudoc,
                                      "Titre-Auteur-Date DoMyBiblio",
                                      )
        if (ppn_final and input_record.date_nett):
            ppn_final = checkDate(ppn, input_record.date_nett, record_sudoc)
    #    if (ppn_final and input_record.auteur_nett):
    #        ppn_final = controle_auteurs(ppn, input_record, record_sudoc)
    if ppn_final:
        ppn_final = "PPN" + ppn_final
    return ppn_final


def checkTypeRecord(ark, typeRecord_attendu):
    url = funcs.url_requete_sru('bib.ark any "' + ark + '"')
    # print(url)
    ark_checked = ""
    (test, record) = funcs.testURLetreeParse(url)
    if test:
        typeRecord = main.extract_leader(record, 7)
        if typeRecord == typeRecord_attendu:
            ark_checked = ark
    return ark_checked


# =============================================================================
# def datePerios(date):
#     """Requête sur la date en élargissant sa valeur aux dates approximatives"""
#     date = date.split(" ")
#     date = date[0]
#     return date
#
# def elargirDatesPerios(n):
#     j = n-4
#     liste = []
#     i = 1
#     while (i < 8):
#         liste.append(j+i)
#         i += 1
#     return " ".join([str(el) for el in liste])
# =============================================================================


def extract_meta(recordBNF, field_subfield, occ="all", anl=False):
    assert field_subfield.find("$") == 3
    assert len(field_subfield) == 5
    field = field_subfield.split("$")[0]
    subfield = field_subfield.split("$")[1]
    value = []
    path = (".//*[@tag='" + field + "']/*[@code='" + subfield + "']")
    for elem in recordBNF.xpath(path, namespaces=main.ns):
        if elem.text is not None:
            value.append(elem.text)
    if occ == "first":
        value = value[0]
    elif occ == "all":
        value = " ".join(value)
    return value


def ark2recordBNF(ark, typeRecord="bib"):
    record = id2record(ark, typeRecord)
    if record is not None:
        return True, record
    else:
        return False, record


def id2record(identifier, typeRecord="bib"):
    """
    A partir d'un identifiant ARK BNF ou PPN Sudoc/IdRef, renvoie une notice Marc XML
    Si pas de résultat, renvoie None
    """
    test = False
    record = None
    if ("ark" in identifier):
        result = sru.SRU_result(f'{typeRecord}.persistentid any "{identifier}"')
        if result.list_identifiers:
            test = True
            record = result.dict_records[result.list_identifiers[0]]
    elif (identifier.lower().startswith("ppn")):
        if (typeRecord == "bib"):
            url = "https://www.sudoc.fr/" + identifier[3:] + ".xml"
        elif (typeRecord == "aut"):
            url = "https://www.idref.fr/" + identifier[3:] + ".xml"
        (test, record) = funcs.testURLetreeParse(url)
    if test:
        return record
    else:
        return None


def ppn2recordSudoc(ppn):
    record = id2record(ppn, "bib")
    if record is not None:
        return True, record
    else:
        return False, record


def ean2ark(input_record, NumNot, ean, titre, auteur, date):
    listeARK = []
    results = sru.SRU_result(f'bib.ean all "{ean}"')
    for ark_current in results.dict_records:    
        ark = comparaisonTitres(input_record, NumNot,
                                ark_current, "", ean,
                                titre, auteur, date, "",
                                results.dict_records[ark_current],
                                "EAN")
        if ark != "":
            input_record.alignment_method.append("EAN > ARK")
            listeARK.append(ark)
    listeARK = ",".join([ark for ark in listeARK if ark])
    if listeARK == "" and auteur != "":
        listeARK = eanauteur2sru(input_record, NumNot, ean, titre, auteur, date)
    return listeARK


def nettoyage_no_commercial(no_commercial_propre):
    no_commercial_propre = funcs.unidecode_local(no_commercial_propre.lower())
    return no_commercial_propre


def no_commercial2ark(input_record, NumNot,
                      no_commercial, titre, auteur,
                      date, anywhere=False, publisher=""):
    """
    Alignement par numéro commercial (partitions, audiovisuel)
    """
    listeArk = []
    no_commercial = no_commercial.strip()
    if (" " in no_commercial):
        no_commercial_source = " ".join([mot for mot in no_commercial.split(" ")[0:-1]])
        no_commercial_id = no_commercial.split(" ")[-1]
        query = f'bib.anywhere all "{no_commercial_source}" and bib.comref all "{no_commercial_id}"'
    elif anywhere:
        query = f'bib.anywhere  all "{no_commercial}"'
    else:
        query = f'bib.comref all "{no_commercial}"'
        if (re.fullmatch("\d{13}", no_commercial) is not None):
            query += f' or bib.ean all "{no_commercial}"'
    results = sru.SRU_result(query)
    
    for ark_current in results.dict_records:
        ark = controleNoCommercial(input_record, NumNot, ark_current, no_commercial,
                                   titre, auteur, date, results.dict_records[ark_current])
        if ark:
            listeArk.append(ark)
    listeArk = ",".join([ark for ark in listeArk if ark])
    return listeArk


def controleNoCommercial(input_record, NumNot, ark_current, no_commercial,
                         titre, auteur, date, recordBNF):
    """
    Après avoir recherché le numéro commercial dans la notice, on vérifie que les mots recherchés
    sont présents dans les bonnes zones (et pas n'importe où, signifiant tout à fait autre chose)
    """
    ark = ""
    no_commercialBNF = " ".join(
        [
            nettoyage_no_commercial(extract_meta(recordBNF, "071$b")),
            nettoyage_no_commercial(extract_meta(recordBNF, "071$a")),
            nettoyage_no_commercial(extract_meta(recordBNF, "073$a")),
        ]
    )
    if no_commercial != "" and no_commercialBNF != "":
        if no_commercial == no_commercialBNF or no_commercial in no_commercialBNF:
            ark = comparaisonTitres(
                input_record,
                NumNot,
                ark_current,
                "",
                no_commercial,
                titre,
                auteur,
                date,
                "",
                recordBNF,
                "No commercial",
            )
        elif no_commercialBNF in no_commercial:
            ark = comparaisonTitres(
                input_record,
                NumNot,
                ark_current,
                "",
                no_commercial,
                titre,
                auteur,
                date,
                "",
                recordBNF,
                "No commercial",
            )
    return ark


# Si on a coché "Récupérer les données bibliographiques" : ouverture de la
# notice BIB de l'ARK et renvoie d'une liste de métadonnées


def ark2meta_simples(ark):
    """" Le parametre 'ark' peut contenir plusieurs identifiants 
    séparés par des virgules.
    Pour chaque ARK, il récupère les métadonnées spécifiques au type de document
    Et les renvoie dans une liste
    Renvoie toutes les infos, car il peut y avoir plusieurs types de notices
    dans une liste d'ARK
    """
    metas = []
    for ark in ark.split(","):
        record = id2record(ark)        
        if record is not None:
            record = funcs.XML2record(record, 1, True)
            if metas == []:
                for el in record.metadata:
                    metas.append([])
            i = 0
            for el in record.metadata:
                metas[i].append(el)
                i += 1 
    i = 0
    for liste_el in metas:
        metas[i] = "|".join(liste_el)
        i += 1
    return metas


def extract_cols_from_row(row, liste):
    nb_cols = len(row)
    i = 0
    liste_values = []
    for el in liste:
        if i < nb_cols:
            liste_values.append(row[i])
        else:
            liste_values.append("")
        i += 1
    return tuple(liste_values)


# ==============================================================================
# def record2dic(row, option):
#     """A partir d'une, et de l'indication de l'option "type de notice" (TEX, VID, AUD, PER)
#     renvoi d'un dictionnaire fournissant les valeurs des différents champs"""
#     input_record = funcs.Bib_record(row, option)
#     return input_record
#
# ==============================================================================


def item2ark_by_id(input_record, parametres):
    """Tronc commun de fonctions d'alignement, applicables pour tous les types de notices
    Par identifiant international : EAN, ISBN, N° commercial, ISSN"""
    ark = ""

    if input_record.ark_init != "":
        ark = ark2ark(input_record)

    # A défaut, recherche de l'ARK à partir du FRBNF (+ contrôles sur ISBN, ou
    # Titre, ou Auteur)
    if ark == "" and input_record.frbnf.propre != "":
        ark = frbnf2ark(input_record)
        ark = ",".join([ark1 for ark1 in ark.split(",") if ark1 != ""])
    if (ark == "" and input_record.ppn.propre != ""):
        ark = aut2id_idref.idrefAut2arkAut(input_record, "sudoc")

    # A défaut, recherche sur EAN
    if ark == "" and input_record.ean.nett != "":
        ark = ean2ark(input_record,
                      input_record.NumNot,
                      input_record.ean.propre,
                      input_record.titre_nett,
                      input_record.auteur_nett,
                      input_record.date_nett,
                     )

    # Si la recherche EAN + contrôles Titre/Date n'a rien donné -> on cherche
    # EAN seul
    if ark == "" and input_record.ean.nett != "":
        ark = ean2ark(input_record, input_record.NumNot,
                      input_record.ean.propre, "", "", "")

    # A défaut, recherche sur ISBN
    # Si plusieurs résultats, contrôle sur l'auteur
    if ark == "" and input_record.isbn.nett != "":
        ark = isbn2ark(input_record,
                       input_record.NumNot,
                       input_record.isbn.init,
                       input_record.isbn.propre,
                       input_record.isbn.converti,
                       input_record.titre_nett,
                       input_record.auteur_nett,
                       input_record.date_nett,
                      )

    # Si la recherche ISBN + contrôle Titre/Date n'a rien donné -> on cherche
    # ISBN seul
    if ark == "" and input_record.isbn.nett != "":
        ark = isbn2ark(
            input_record,
            input_record.NumNot,
            input_record.isbn.init,
            input_record.isbn.propre,
            "",
            "",
            "",
            "",
        )

    # Après alignement sur ISBN/EAN, on
    # ajoute un contrôle sur le numéro
    # de tome/volume, s'il est renseigné
    # dans les données en entrée
    if ark != "" and input_record.tome != "":
        numeroTome = funcs.nettoyageTome(input_record.tome)
        if (numeroTome != ""):
                recordBNF = id2record(ark)
                if recordBNF is not None:
                    ark = verificationTomaison(ark, numeroTome, recordBNF)

    # A défaut, recherche sur no_commercial
    if ark == "" and input_record.no_commercial != "" and input_record.no_commercial_propre != "":
        ark = no_commercial2ark(
            input_record,
            input_record.NumNot,
            input_record.no_commercial_propre,
            input_record.titre_nett,
            input_record.auteur_nett,
            input_record.date_nett,
            False,
            input_record.publisher_nett,
        )

    # A défaut, recherche sur ISSN
    if ark == "" and input_record.issn.propre != "":
        ark = issn2ark(
            input_record,
            input_record.NumNot,
            input_record.issn.init,
            input_record.issn.propre,
            input_record.titre_nett,
            input_record.auteur_nett,
            input_record.date_nett,
        )
    return ark


def item2ppn_by_id(input_record, parametres):
    """Tronc commun de fonctions d'alignement, applicables pour tous les types de notices
    Quand l'option "BnF" d'abord a été choisie"""
    ppn = ""

    # Si pas de résultats : on relance une recherche dans le Sudoc
    if (ppn == "" and input_record.ean.propre):
        ppn = ean2sudoc(input_record, parametres, True)

    # Si pas de résultats : on relance une recherche dans le Sudoc avec l'EAN
    # seul
    if (ppn == "" and input_record.ean.propre):
        ppn = ean2sudoc(input_record, parametres, False)
    if (ppn == "" and input_record.isbn.propre):
        ppn = isbn2sudoc(input_record, parametres)

    # Après alignement sur ISBN/EAN, on
    # ajoute un contrôle sur le numéro
    # de tome/volume, s'il est renseigné
    # dans les données en entrée
    """if ppn != "" and input_record.tome != "":
        numeroTome = funcs.nettoyageTome(input_record.tome)
        if (numeroTome != ""):
                url = ppn2recordSudoc(ppn)
                (test, recordSudoc) = funcs.testURLetreeParse(url)
                if test:
                    ppn = verificationTomaison(ppn, numeroTome, recordSudoc)"""
    if (ppn == "" and input_record.issn.propre):
        ppn = issn2sudoc(
            input_record,
            input_record.NumNot,
            input_record.issn.init,
            input_record.issn.propre,
            input_record.titre.controles,
            input_record.auteur_nett,
            input_record.date_nett,
            parametres,
        )
    return ppn

def check_ppn_by_kw(ppn, input_record, source_alignement):
    url_sudoc_record = "https://www.sudoc.fr/" + ppn.replace("PPN", "") + ".xml"
    (test, record_sudoc) = funcs.testURLetreeParse(url_sudoc_record, display=False)
    if test:
        ppn_checked = comparaisonTitres(input_record,
                                        input_record.NumNot,
                                        ppn,
                                        "",
                                        "",
                                        input_record.titre.controles,
                                        input_record.auteur,
                                        input_record.date_nett,
                                        input_record.tome_nett,
                                        record_sudoc,
                                        source_alignement,
                                        )
    else:
        ppn_checked = ppn
        input_record.alignment_method.append(f"Problème {ppn} : métadonnées Sudoc non vérifiées")
    return ppn_checked


def item2ark_by_keywords(input_record, parametres):
    """Alignement par mots clés sur le catalogue BnF"""
    ark = ""
    # A défaut, recherche sur Titre-Auteur-Date
    if input_record.titre.init != "":
        ark = tad2ark(input_record, parametres,
                      False, False)

    # Si rien trouvé et si nombres dans le titre :
    # on recherche avec la version chiffres->lettres
    # ou lettres->chiffres
    if (ark == "" and input_record.titre.recherche_nombres_convertis):
        temp_input_record = input_record
        temp_input_record.titre.recherche = temp_input_record.titre.recherche_nombres_convertis
        temp_input_record.titre.controles = funcs.nettoyageTitrePourControle(temp_input_record.titre.recherche)
        ark = tad2ark(temp_input_record, parametres,
                      False, False)
        if ark:
            input_record.alignment_method.append("conversion Nombres/Texte")


    # Si rien trouvé et si c'est une partition
    # et si mention d'opus -> on cherche sans la mention d'opus
    if (ark == "" 
       and "type_doc_bib" in parametres
       and parametres["type_doc_bib"] == 6
       and input_record.titre.recherche_sans_num_opus):
        temp_input_record = input_record
        temp_input_record.titre = funcs.Titre(temp_input_record.titre.recherche_sans_num_opus)
        temp_input_record.titre = temp_input_record.titre
        ark = tad2ark(temp_input_record, 
                      parametres, 
                      False, False)
        if ark:
            input_record.alignment_method.append(" recherche sans mention d'opus")

    # Si pas trouvé, on cherche l'ensemble des
    # mots dans toutes les zones indifféremment
    if ark == "" and input_record.titre.init != "":
        ark = tad2ark(input_record, parametres,
                      True, False)
    return ark


def item2ppn_by_keywords(input_record, parametres):
    """Alignement par mots clés sur le catalogue Sudoc"""
    ppn = ""
    if input_record.titre.init != "":
        ppn = tad2ppn(input_record, parametres)

    # Si rien trouvé et si nombres dans le titre :
    # on recherche avec la version chiffres->lettres
    # ou lettres->chiffres
    if (ppn == "" and input_record.titre.recherche_nombres_convertis):
        temp_input_record = input_record
        temp_input_record.titre.recherche = temp_input_record.titre.recherche_nombres_convertis
        temp_input_record.titre.controles = funcs.nettoyageTitrePourControle(temp_input_record.titre.recherche)
        ppn = tad2ppn(temp_input_record, parametres)
        if ppn:
            input_record.alignment_method.append("conversion Nombres/Texte")


    # Si rien trouvé et si c'est une partition
    # et si mention d'opus -> on cherche sans la mention d'opus
    if (ppn == "" 
       and "type_doc_bib" in parametres
       and parametres["type_doc_bib"] == 6
       and input_record.titre.recherche_sans_num_opus):
        temp_input_record = input_record
        temp_input_record.titre.recherche = temp_input_record.titre.recherche_sans_num_opus
        ppn = tad2ppn(temp_input_record, parametres)
        if ppn:
            input_record.alignment_method.append(" recherche sans mention d'opus")

    return ppn


def item_alignement(input_record, parametres):
    """
    Successions d'alignements pour une notices
    En entrée, une Bib_record (générée à partir d'une ligne du fichier
    en sortie, la liste des métadonnées attendues par le rapport)
    """
    ark = ""
    # Si option 1 : on aligne sur les ID en commençant par la BnF, puis par le Sudoc
    # Si aucun résultat -> recherche Titre-Auteur-Date à la BnF
    # Si option 2 : on commence par le Sudoc, puis par la BnF
    if parametres["preferences_alignement"] == 1:
        ark = item2ark_by_id(input_record, parametres)
        if ark == "":
            ark = item2ark_by_keywords(input_record, parametres)
        if ark == "":
            ark = item2ppn_by_id(input_record, parametres)
        if (ark == "" 
            and "kwsudoc_option" in parametres
            and parametres["kwsudoc_option"]==1):
            ark = item2ppn_by_keywords(input_record, parametres)
    else:
        ark = item2ppn_by_id(input_record, parametres)
        if (ark == "" 
            and "kwsudoc_option" in parametres
            and parametres["kwsudoc_option"]==1):
            ark = item2ppn_by_keywords(input_record, parametres)
        if ark == "":
            ark = item2ark_by_id(input_record, parametres)
        if ark == "":
            ark = item2ark_by_keywords(input_record, parametres)
    alignment_result = funcs.Alignment_result(input_record, ark, parametres)
    if ark == "Pb FRBNF":
        parametres["stats"]["Pb FRBNF"] += 1
    else:
        parametres["stats"][alignment_result.nb_ids] += 1
    return alignment_result


def item2id(row, n, form_bib2ark, parametres, liste_reports):
    """Pour chaque ligne : constitution d'une notice et règles d'alignement
    propres à ce type de notice"""
    if n == 0:
        assert main.control_columns_number(
            form_bib2ark, row, parametres["header_columns_init"]
        )
    if n % 100 == 0:
        main.check_access2apis(n, dict_check_apis)
    # print(row)
    input_record = funcs.Bib_record(row, parametres["type_doc_bib"])
    alignment_result = item_alignement(input_record, parametres)
    
    # Si échec et que c'est une partition, relancer avec titre de partie
    if ("type_doc_bib" in parametres
       and parametres["type_doc_bib"] == 6
       and alignment_result.nb_ids == 0
       and row[5]
       and row[6]):
        input_record.titre = input_record.soustitre
        input_record.soustitre = funcs.Titre("")
        alignment_result = item_alignement(input_record, parametres)
        if alignment_result.nb_ids:
            alignment_result.liste_metadonnees[3] += " - Sans alignement titre principal"

    # Si échec et que c'est une partition, relancer avec titre d'ensemble
    if ("type_doc_bib" in parametres
       and parametres["type_doc_bib"] == 6
       and alignment_result.nb_ids == 0
       and row[5]
       and row[6]):
        input_record.titre = funcs.Titre(row[5])
        alignment_result = item_alignement(input_record, parametres)
        if alignment_result.nb_ids:
            alignment_result.liste_metadonnees[3] += " - Sans alignement titre de partie"
    alignment_result2output(alignment_result, input_record,
                            parametres, liste_reports, n)
    return alignment_result


def alignment_result2output(alignment_result, input_record, parametres, liste_reports, n):
    """
    Format de sortie de l'alignement
    """
    print(str(n) + ". " + input_record.NumNot + " : " + alignment_result.ids_str)
    if parametres["meta_bib"] == 1:
        alignment_result.liste_metadonnees.extend(ark2meta_simples(alignment_result.ids_str))
    if parametres["file_nb"] == 1:
        row2file(alignment_result.liste_metadonnees, liste_reports)
    elif parametres["file_nb"] == 2:
        row2files(alignment_result.liste_metadonnees, liste_reports)


def file2row(form_bib2ark, entry_filename, liste_reports, parametres):
    """Récupération du contenu du fichier et application des règles d'alignement
    ligne à ligne"""
    header_columns = ["NumNot", "Nb identifiants trouvés",
                      "Liste identifiants trouvés",
                      "Méthode d'alignement"]
    header_columns.extend(el for el in parametres["header_columns_init"][1:])
    if parametres["meta_bib"] == 1:
        header_columns.extend(
            [
                "[BnF/Abes] Titre",
                "[BnF/Abes] 1er auteur Prénom",
                "[BnF/Abes] 1er auteur Nom",
                "[BnF/Abes] Tous auteurs",
                "[BnF/Abes] Date",
                "[BnF/Abes] Type"
            ]
        )
    # Ajout des en-têtes de colonne dans les fichiers
    if parametres["file_nb"] == 1:
        row2file(header_columns, liste_reports)
    elif parametres["file_nb"] == 2:
        row2files(header_columns, liste_reports)
    n = 0
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
        for row in entry_file:
            item2id(row, n, form_bib2ark, parametres, liste_reports)
            n += 1


def launch(entry_filename,
           type_doc_bib,
           preferences_alignement,
           kwsudoc_option,
           file_nb,
           meta_bib,
           id_traitement,
           form_bib2ark=None
           ):
    # Préférences alignement : 1 = BnF d'abord, puis Sudoc. 2 : Sudoc d'abord,
    # puis BnF
    try:
        [entry_filename, type_doc_bib,
        preferences_alignement,
        kwsudoc_option,
        file_nb, meta_bib,
        id_traitement] = [str(entry_filename), int(type_doc_bib),
                          int(preferences_alignement),
                          int(kwsudoc_option),
                          int(file_nb), int(meta_bib),
                          str(id_traitement)]
    except ValueError as err:
        print("\n\nDonnées en entrée erronées\n")
        print(err)
    header_columns_init_dic = {
        1: header_columns_init_monimpr,
        2: header_columns_init_cddvd,
        3: header_columns_init_cddvd,
        4: header_columns_init_perimpr,
        5: header_columns_init_cartes,
        6: header_columns_init_partitions
    }
    parametres = {
        "meta_bib": meta_bib,
        "type_doc_bib": type_doc_bib,
        "file_nb": file_nb,
        "id_traitement": id_traitement,
        "header_columns_init": header_columns_init_dic[type_doc_bib],
        "preferences_alignement": preferences_alignement,
        "kwsudoc_option": kwsudoc_option,
        "stats": defaultdict(int)
    }
    main.check_file_name(form_bib2ark, entry_filename)
    liste_reports = create_reports(funcs.id_traitement2path(id_traitement), file_nb)
    file2row(form_bib2ark, entry_filename, liste_reports, parametres)

    fin_traitements(form_bib2ark, liste_reports, parametres["stats"])

#
# ==============================================================================


def fin_traitements(form_bib2ark, liste_reports, nb_notices_nb_ARK):
    stats_extraction(liste_reports, nb_notices_nb_ARK)
    url_access_pbs_report(liste_reports)
    check_access_to_apis(liste_reports)
    typesConversionARK(liste_reports)
    print("Programme terminé")
    if form_bib2ark is not None:
        form_bib2ark.destroy()
    for file in liste_reports:
        file.close()
    main.output_directory = [""]

def stats_extraction(liste_reports, nb_notices_nb_ARK):
    """Ecriture des rapports de statistiques générales d'alignements"""
    for key in nb_notices_nb_ARK:
        liste_reports[-1].write(str(key) + "\t" + str(nb_notices_nb_ARK[key]) + "\n")


def url_access_pbs_report(liste_reports):
    """A la suite des stats générales, liste des erreurs rencontrées

    (plantage URL) + ISBN différents en entrée et en sortie
    """
    if len(url_access_pbs) > 0:
        liste_reports[-1].write(
            "\n\nProblème d'accès à certaines URL :\nURL\tType de problème\n"
        )
        for pb in url_access_pbs:
            liste_reports[-1].write("\t".join(pb) + "\n")
    if len(NumNotices_conversionISBN) > 0:
        liste_reports[-1].write("".join(["\n\n", 10 * "-", "\n"]))
        liste_reports[-1].write(
            "Liste des notices dont l'ISBN en entrée est différent de celui dans la notice trouvée\n"  # noqa
        )
        liste_reports[-1].write(
            "\t".join(
                [
                    "NumNotice",
                    "ISBN initial",
                    "ISBN converti",
                    "Notice trouvée dans le Sudoc ?",
                ]
            )
            + "\n"
        )
        for record in NumNotices_conversionISBN:
            liste_reports[-1].write(
                "\t".join(
                    [
                        record,
                        NumNotices_conversionISBN[record]["isbn initial"],
                        NumNotices_conversionISBN[record]["isbn trouvé"],
                        NumNotices_conversionISBN[record]["via Sudoc"],
                    ]
                )
                + "\n"
            )


def check_access_to_apis(liste_reports):
    """Contrôles réguliers de l'accès aux API Abes et BnF -> enregistrés dans
    le dictionnaire dict_check_apis.
    Si celui-ci contient au moins un "False", on génère une rubrique
    dans le rapport Stats"""
    for api in dict_check_apis:
        if not dict_check_apis[api]["global"]:
            liste_reports[-1].write(
                "\n\nProblème d'accès aux" + dict_check_apis[api]["name"] + " :\n"
            )
        for key in dict_check_apis[api]:
            if dict_check_apis["testAbes"][key] is False:
                liste_reports[-1].write(
                    "".join(
                        [str(key), " : " + dict_check_apis[api]["name"] + " down\n"]
                    )
                )


def typesConversionARK(liste_reports):
    """Dans un rapport spécifique, pour chaque notice en entrée,
    mention de la méthode d'alignement (ISBN, ISNI, etc.)
    """
    # for key in NumNotices2methode:
    #     value = " / ".join(NumNotices2methode[key])
    #     liste_reports[-1].write(key + "\t" + value + "\n")


def annuler(form_bib2ark):
    """Fermeture du formulaire (bouton "Annuler")"""
    form_bib2ark.destroy()



def radioButton_lienExample(
    frame, variable_button, val, couleur_fond, text1, text2, link
):
    packButton = tk.Frame(frame, bg=couleur_fond)
    packButton.pack(anchor="w")
    line1 = tk.Frame(packButton, bg=couleur_fond)
    line1.pack(anchor="w")
    tk.Radiobutton(
        line1,
        bg=couleur_fond,
        text=text1,
        variable=variable_button,
        value=val,
        justify="left",
    ).pack(anchor="w", side="left")
    if link != "":
        tk.Label(line1, text="  ", bg=couleur_fond).pack(anchor="w", side="left")
        if "http" in link:
            example_ico = tk.Button(
                line1,
                bd=0,
                justify="left",
                font="Arial 7 underline",
                text="exemple",
                fg="#0000ff",
                bg=couleur_fond,
                command=lambda: main.click2url(link),
            )
        else:
            link = os.path.join(os.path.dirname(__file__), link)
            example_ico = tk.Button(
                line1,
                bd=0,
                justify="left",
                font="Arial 7 underline",
                text="exemple",
                fg="#0000ff",
                bg=couleur_fond,
                command=lambda: funcs.open_local_file(link),
            )
        example_ico.pack(anchor="w", side="left")
    if text2 != "":
        line2 = tk.Frame(packButton, bg=couleur_fond)
        line2.pack(anchor="w")
        tk.Label(line2, bg=couleur_fond, text="      " + text2, justify="left").pack(
            anchor="w"
        )


def form_bib2id(
    master, access_to_network=True, last_version=[0, False]
):
    """Affichage du formulaire : disposition des zones, options, etc."""
    couleur_fond = "white"
    couleur_bouton = "#acacac"

    [
        form_bib2ark,
        zone_alert_explications,
        zone_access2programs,
        zone_actions,
        zone_ok_help_cancel,
        zone_notes,
    ] = main.form_generic_frames(
        master,
        "Programme d'alignement de données bibliographiques avec la BnF et le Sudoc",
        couleur_fond,
        couleur_bouton,
        access_to_network,
    )

    cadre_input = tk.Frame(
        zone_actions,
        highlightthickness=2,
        highlightbackground=couleur_bouton,
        relief="groove",
        height=150,
        padx=10,
        bg=couleur_fond,
    )
    cadre_input.pack(side="left")
    cadre_input_header = tk.Frame(cadre_input, bg=couleur_fond)
    cadre_input_header.pack(anchor="w")
    cadre_input_file = tk.Frame(cadre_input, bg=couleur_fond)
    cadre_input_file.pack(anchor="w")
    cadre_input_infos_format = tk.Frame(cadre_input, bg=couleur_fond)
    cadre_input_infos_format.pack(anchor="w")
    cadre_input_type_docs = tk.Frame(cadre_input, bg=couleur_fond)
    cadre_input_type_docs.pack(anchor="w")

    cadre_input_type_docs_zone = tk.Frame(cadre_input_type_docs, bg=couleur_fond)
    cadre_input_type_docs_zone.pack(anchor="w")
    cadre_input_type_docs_explications = tk.Frame(
        cadre_input_type_docs, bg=couleur_fond
    )
    cadre_input_type_docs_explications.pack(anchor="w")

    cadre_inter = tk.Frame(zone_actions, borderwidth=0, padx=10, bg=couleur_fond)
    cadre_inter.pack(side="left")
    tk.Label(cadre_inter, text=" ", bg=couleur_fond).pack()

    cadre_output = tk.Frame(
        zone_actions,
        highlightthickness=2,
        highlightbackground=couleur_bouton,
        relief="groove",
        height=150,
        padx=10,
        bg=couleur_fond,
    )
    cadre_output.pack(side="left", anchor="w")
    cadre_output_header = tk.Frame(cadre_output, bg=couleur_fond)
    cadre_output_header.pack(anchor="w")
    cadre_output_nb_fichier = tk.Frame(cadre_output, bg=couleur_fond)
    cadre_output_nb_fichier.pack(anchor="w")

    cadre_output_nb_fichiers_zone = tk.Frame(cadre_output_nb_fichier, 
                                             bg=couleur_fond)
    cadre_output_nb_fichiers_zone.pack(anchor="w")
    cadre_output_nb_fichiers_explications = tk.Frame(
        cadre_output_nb_fichier, bg=couleur_fond
    )
    cadre_output_nb_fichiers_explications.pack(anchor="w")

    cadre_output_files = tk.Frame(cadre_output, padx=2, 
                                  bg=couleur_fond)
    cadre_output_files.pack(anchor="w")
    
    cadre_output_directory = tk.Frame(cadre_output_files, 
                                      padx=1, bg=couleur_fond)
    cadre_output_directory.pack(side="left", anchor="w")

    cadre_output_id_traitement = tk.Frame(cadre_output_files, padx=1, bg=couleur_fond)
    cadre_output_id_traitement.pack(side="left", anchor="w")

    zone_notes_message_en_cours = tk.Frame(zone_notes, padx=20, bg=couleur_fond)
    zone_notes_message_en_cours.pack()

    # ==============================================================================
    # Message d'alerte dans le formulaire si besoin
    # ==============================================================================
    # tk.Label(
    #     zone_alert_explications,
    #     text="Attention : format MON IMPR avec une colonne supplémentaire en entrée (EAN)",
    #     bg=couleur_fond,
    #     fg="red",
    # ).pack()
    # définition input URL (u)

    main.download_zone(
                        cadre_output_directory,
                        "Sélectionner un dossier\nde destination",
                        main.output_directory,
                        couleur_fond,
                        type_action="askdirectory",
                        widthb = [40,1]
                        )
    tk.Label(
        cadre_input_header,
        bg=couleur_fond,
        fg=couleur_bouton,
        text="En entrée :",
        justify="left",
        font="bold",
    ).pack()

    tk.Label(
        cadre_input_file, bg=couleur_fond, 
        text="Fichier contenant les notices :\n\n"
    ).pack(side="left")
    main.download_zone(
        cadre_input_file,
        "Sélectionner un fichier\nSéparateur TAB, Encodage UTF-8",
        entry_file_list,
        couleur_fond,
        zone_notes,
        #widthb=[40,1]
        )

    tk.Label(
        cadre_input_type_docs_zone,
        bg=couleur_fond,
        text="Type de documents  ",
        font="Arial 10 bold",
        justify="left",
    ).pack(anchor="w", side="left")

    type_doc_bib = tk.IntVar()
    radioButton_lienExample(
        cadre_input_type_docs,
        type_doc_bib,
        1,
        couleur_fond,
        "[TEX] Monographies texte",
        main.display_headers_in_form(header_columns_init_monimpr),
        "main/examples/mon_impr.tsv",  # noqa
    )
    radioButton_lienExample(
        cadre_input_type_docs,
        type_doc_bib,
        2,
        couleur_fond,
        "[VID] Audiovisuel (DVD)",
        main.display_headers_in_form(header_columns_init_cddvd),
        "",
    )
    radioButton_lienExample(
        cadre_input_type_docs,
        type_doc_bib,
        3,
        couleur_fond,
        "[AUD] Enregistrements sonores",
        main.display_headers_in_form(header_columns_init_cddvd),
        "main/examples/audio.tsv",  # noqa
    )
    radioButton_lienExample(
        cadre_input_type_docs,
        type_doc_bib,
        4,
        couleur_fond,
        "[PER] Périodiques",
        main.display_headers_in_form(header_columns_init_perimpr),
        "main/examples/per.tsv",  # noqa
    )
    radioButton_lienExample(
        cadre_input_type_docs,
        type_doc_bib,
        5,
        couleur_fond,
        "[CAR] Cartes",
        main.display_headers_in_form(header_columns_init_cartes),
        "",  # noqa
    )
    radioButton_lienExample(
        cadre_input_type_docs,
        type_doc_bib,
        6,
        couleur_fond,
        "[PAR] Partitions",
        main.display_headers_in_form(header_columns_init_partitions),
        "",  # noqa
    )
    type_doc_bib.set(1)

    tk.Label(
        cadre_input_type_docs,
        bg=couleur_fond,
        text="\nAligner de préférence :",
        font="Arial 10 bold",
        justify="left",
    ).pack(anchor="w")
    preferences_alignement = tk.IntVar()
    radioButton_lienExample(
        cadre_input_type_docs,
        preferences_alignement,
        1,
        couleur_fond,
        "Avec la BnF (et à défaut avec le Sudoc)",
        "",
        "",
    )

    radioButton_lienExample(
        cadre_input_type_docs,
        preferences_alignement,
        2,
        couleur_fond,
        "Avec le Sudoc (et à défaut avec la BnF)",
        "",
        "",
    )
    preferences_alignement.set(1)

    kwsudoc_option = tk.IntVar()
    kwsudoc_option_check = tk.Checkbutton(
        cadre_input_type_docs,
        bg=couleur_fond,
        text="+ Utiliser aussi la recherche par mots-clés dans le Sudoc \
(peut ralentir le programme)",
        variable=kwsudoc_option,
        justify="left",
    )
    kwsudoc_option.set(1)
    kwsudoc_option_check.pack(anchor="w")



    # Choix du format
    tk.Label(
        cadre_output_header,
        bg=couleur_fond,
        fg=couleur_bouton,
        text="En sortie :",
        font="bold",
    ).pack(anchor="w")
    tk.Label(
        cadre_output_nb_fichiers_zone,
        bg=couleur_fond,
        font="Arial 10 bold",
        text="Nombre de fichiers  ",
    ).pack(anchor="w", side="left")
    file_nb = tk.IntVar()
    # file_nb = tk.Entry(cadre_output_nb_fichiers_zone, width=3, bd=2)
    # file_nb.pack(anchor="w", side="left")
    # tk.Label(
    #     cadre_output_nb_fichiers_explications,
    #     bg=couleur_fond,
    #     text=
    #     "1 = 1 fichier d'alignements\n2 = Plusieurs fichiers (0 ARK trouvé / 1 ARK / Plusieurs ARK)",  # noqa
    #     justify="left"
    # ).pack(anchor="w")

    tk.Radiobutton(
        cadre_output_nb_fichier,
        bg=couleur_fond,
        text="1 fichier",
        variable=file_nb,
        value=1,
        justify="left",
    ).pack(anchor="w")
    tk.Radiobutton(
        cadre_output_nb_fichier,
        bg=couleur_fond,
        text="Plusieurs fichiers\n(Pb / 0 / 1 / plusieurs ARK trouvés)",
        justify="left",
        variable=file_nb,
        value=2,
    ).pack(anchor="w")
    file_nb.set(1)
    # Récupérer les métadonnées BIB (dublin core)
    tk.Label(
        cadre_output_nb_fichier, bg=couleur_fond, fg=couleur_bouton, text="\n"
    ).pack()
    meta_bib = tk.IntVar()
    meta_bib_check = tk.Checkbutton(
        cadre_output_nb_fichier,
        bg=couleur_fond,
        text="Récupérer les métadonnées simples",
        variable=meta_bib,
        justify="left",
    )
    meta_bib_check.pack(anchor="w")
    tk.Label(cadre_output_directory, text="\n", bg=couleur_fond).pack()

    
    # tk.Label(frame_header, text="\n", bg=couleur_fond).pack()



    # Ajout (optionnel) d'un identifiant de traitement
    #tk.Label(cadre_output_id_traitement,
    #         bg=couleur_fond, text="\n"*1).pack()
    tk.Label(
        cadre_output_id_traitement, bg=couleur_fond, 
        text="Préfixe fichiers en sortie").pack()
    id_traitement = tk.Entry(cadre_output_id_traitement, width=20, bd=2)
    id_traitement.pack()
    tk.Label(cadre_output_files, bg=couleur_fond, text="\n"*22).pack()

    # Bouton de validation

    b = tk.Button(
        zone_ok_help_cancel,
        bg=couleur_bouton,
        fg="white",
        font="Arial 10 bold",
        text="Aligner les\nnotices BIB",
        command=lambda: launch(entry_file_list[0],
                               type_doc_bib.get(),
                               preferences_alignement.get(),
                               kwsudoc_option.get(),
                               file_nb.get(),
                               meta_bib.get(),
                               id_traitement.get(),
                               form_bib2ark,
                              ),
        borderwidth=5,
        padx=10,
        pady=10,
        width=10,
        height=4,
    )
    b.pack()

    tk.Label(zone_ok_help_cancel, font="bold", text="", bg=couleur_fond).pack()

    call4help = tk.Button(
        zone_ok_help_cancel,
        text=main.texte_bouton_help,
        command=lambda: main.click2url(main.url_online_help),
        pady=5,
        padx=5,
        width=12,
    )
    call4help.pack()
    tk.Label(
        zone_ok_help_cancel, text="\n", bg=couleur_fond, font="Arial 1 normal"
    ).pack()

    forum_button = tk.Button(
        zone_ok_help_cancel,
        text=main.texte_bouton_forum,
        command=lambda: main.click2url(main.url_forum_aide),
        pady=5,
        padx=5,
        width=12,
    )
    forum_button.pack()

    tk.Label(
        zone_ok_help_cancel, text="\n", bg=couleur_fond, font="Arial 4 normal"
    ).pack()
    cancel = tk.Button(
        zone_ok_help_cancel,
        text="Annuler",
        bg=couleur_fond,
        command=lambda: main.annuler(form_bib2ark),
        pady=10,
        padx=5,
        width=12,
    )
    cancel.pack()

    zone_version = tk.Frame(zone_notes, bg=couleur_fond)
    zone_version.pack()
    tk.Label(
        zone_version,
        text="Bibliostratus - Version " + str(main.version) + " - " + main.lastupdate,
        bg=couleur_fond,
    ).pack()

    zone_controles = tk.Frame(zone_notes, bg=couleur_fond)
    zone_controles.pack()
    tk.mainloop()


if __name__ == "__main__":
    access_to_network = main.check_access_to_network()
    last_version = [0, False]
    if access_to_network is True:
        last_version = main.check_last_compilation(main.programID)
    main.formulaire_main(access_to_network, last_version)
