# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 18:30:30 2017

@author: Etienne Cavalié

Programme de manipulations de données liées à la Transition bibliographique
Alignement des données d'autorité

"""

import csv
import tkinter as tk
import urllib.parse
from collections import defaultdict
import os, ssl

from joblib import Parallel, delayed
import multiprocessing

from unidecode import unidecode

import funcs
import main
import bib2id
import aut2id_idref
import aut2id_concepts
import forms


NUM_PARALLEL = 100    # Nombre de notices à aligner simultanément

# Ajout exception SSL pour éviter
# plantages en interrogeant les API IdRef
# (HTTPS sans certificat)
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
   getattr(ssl, '_create_unverified_context', None)): 
    ssl._create_default_https_context = ssl._create_unverified_context

# Permet d'écrire dans une liste accessible au niveau général depuis le
# formulaire, et d'y accéder ensuite
entry_file_list = []

header_columns_init_aut2aut = [
    'N° Notice AUT', 'FRBNF', 'ARK', 'ISNI', 'Nom', 'Prénom',
    'Date de début', 'Date de fin'
]


header_columns_init_aut2aut_org = [
    'N° Notice AUT', 'FRBNF', 'ARK', 'ISNI', 'Nom', 'Complément nom',
    'Date de début', 'Date de fin'
]

header_columns_init_bib2aut = [
    "N° Notice AUT", "N° notice BIB", "ARK Bib", "FRBNF Bib", "ISBN/EAN", "Titre",
    "Date de publication", "ISNI", "Nom", "Prénom", "Dates auteur"
]

header_columns_init_rameau = [
    'N° Notice AUT', 'FRBNF', 'ARK', 'Point d\'accès Rameau'
]

aligntype2headers = {1: header_columns_init_aut2aut,
                     2: header_columns_init_aut2aut_org,
                     3: header_columns_init_bib2aut,
                     4: header_columns_init_rameau}

# Pour chaque notice, on recense la méthode qui a permis de récupérer le
# ou les ARK

# Toutes les 100 notices, on vérifie que les API BnF et Abes répondent correctement.
# Résultats (True/False) enregistrés dans ce dictionnaire
dict_check_apis = defaultdict(dict)


def create_reports(id_traitement_code, nb_fichiers_a_produire):
    reports = []
    stats_report_file_name = id_traitement_code + \
        "-" + "rapport_stats_aut2id.txt"
    stats_report_file = open(stats_report_file_name, "w")
    stats_report_file.write("Nb identifiants (ARK ou PPN) trouvés\tNb notices concernées\n")

    # $1eport_type_convert_file_name = id_traitement_code + "-" + "NumNotices-TypeConversion.txt"
    # $1eport_type_convert_file = open(report_type_convert_file_name,"w")
    # $1eport_type_convert_file.write("NumNotice\tMéthode pour trouver l'ARK\n")
    if (nb_fichiers_a_produire == 1):
        reports = create_reports_1file(id_traitement_code)
    else:
        reports = create_reports_files(id_traitement_code)
    reports.append(stats_report_file)
    # reports.append(report_type_convert_file)
    return reports


def create_reports_1file(id_traitement_code):
    unique_file_results_frbnf_isbn2ark_name = id_traitement_code + \
        "-" + "resultats_aut2id.txt"
    unique_file_results_frbnf_isbn2ark = open(
        unique_file_results_frbnf_isbn2ark_name, "w", encoding="utf-8")
    return [unique_file_results_frbnf_isbn2ark]


def create_reports_files(id_traitement_code):
    multiple_files_pbFRBNF_ISBN_name = id_traitement_code + \
        "-Problemes_donnees_initiales.txt"
    multiple_files_0_ark_name = id_traitement_code + "-resultats_0_ID_trouve.txt"
    multiple_files_1_ark_name = id_traitement_code + "-resultats_1_ID_trouve.txt"
    multiple_files_plusieurs_ark_name = id_traitement_code + \
        "-resultats_plusieurs_ID_trouves.txt"

    multiple_files_pbFRBNF_ISBN = open(
        multiple_files_pbFRBNF_ISBN_name, "w", encoding="utf-8")
    multiple_files_0_ark = open(
        multiple_files_0_ark_name, "w", encoding="utf-8")
    multiple_files_1_ark = open(
        multiple_files_1_ark_name, "w", encoding="utf-8")
    multiple_files_plusieurs_ark_name = open(
        multiple_files_plusieurs_ark_name, "w", encoding="utf-8")

    return [multiple_files_pbFRBNF_ISBN, multiple_files_0_ark,
            multiple_files_1_ark, multiple_files_plusieurs_ark_name]


# Rapport statistique final



def row2file(liste_metadonnees, liste_reports):
    liste_metadonnees_to_report = [str(el) for el in liste_metadonnees]
    if ("timestamp" in main.prefs
       and main.prefs["timestamp"]["value"] == "True"):
        timest = funcs.timestamp()
        liste_metadonnees_to_report.append(timest)
    liste_reports[0].write("\t".join(liste_metadonnees_to_report) + "\n")


def row2files(liste_metadonnees, liste_reports, headers=False):
    liste_metadonnees_to_report = [str(el) for el in liste_metadonnees]
    nbARK = liste_metadonnees[1]
    ark = liste_metadonnees[2]
    if headers:
        liste_reports[1].write("\t".join(liste_metadonnees_to_report) + "\n")
        liste_reports[2].write("\t".join(liste_metadonnees_to_report) + "\n")
        liste_reports[3].write("\t".join(liste_metadonnees_to_report) + "\n")
    elif (ark == "Pb FRBNF"):
        liste_reports[0].write("\t".join(liste_metadonnees_to_report) + "\n")
    elif (nbARK == 0):
        liste_reports[1].write("\t".join(liste_metadonnees_to_report) + "\n")
    elif (nbARK == 1):
        liste_reports[2].write("\t".join(liste_metadonnees_to_report) + "\n")
    else:
        liste_reports[3].write("\t".join(liste_metadonnees_to_report) + "\n")


# Si on a coché "Récupérer les données bibliographiques" : ouverture de la
# notice BIB de l'ARK et renvoie d'une liste de métadonnées
def ark2meta_aut(ark):
    # Attention : la variable 'ark' peut contenir plusieurs ark séparés par
    # des virgules
    listeARK = ark.split(",")

    # On récupére tous les titres de chaque ARK, puis tous les auteurs
    accesspointList = []
    accesspoint_complList = []
    datesList = []
    isnis = []
    other_ids = []
    for ark in listeARK:
        metas_ark = ark2metas_aut(ark, False)
        accesspointList.append(metas_ark[0])
        accesspoint_complList.append(metas_ark[1])
        datesList.append(metas_ark[2])
        isnis.append(metas_ark[3])
        other_ids.append(metas_ark[4])
    accesspointList = "|".join(accesspointList)
    accesspoint_complList = "|".join(accesspoint_complList)
    datesList = "|".join(datesList)
    isnis = "|".join(isnis)
    other_ids = "|".join(other_ids)
    metas = [accesspointList, accesspoint_complList, datesList, isnis, other_ids]
    return metas


def ark2metas_aut(ark, unidec=True):
    url = funcs.url_requete_sru(f'aut.persistentid any "{ark}" and aut.status any "sparse validated"')
    if ("ppn" in ark.lower()):
        url = "https://www.idref.fr/" + ark[3:] + ".xml"
    (test, record) = funcs.testURLetreeParse(url)
    accesspoint, accesspoint_compl, dates, isni, other_ids = ["", "", "", "", ""]
    if test:
        accesspoint = main.extract_subfield(record, "200", "a")
        if not accesspoint:
            accesspoint = main.extract_subfield(record, "210", "a")
        accesspoint_compl = main.extract_subfield(record, "200", "b")
        if not accesspoint_compl:
            accesspoint_compl = main.extract_subfield(record, "210", "b")
        dates = main.extract_subfield(record, "200", "f")
        if not dates:
            dates = main.extract_subfield(record, "210", "f")
        isni = main.extract_subfield(record, "010", "a")
        other_ids = main.extract_subfield(record, "033", "a")
    metas = [accesspoint, accesspoint_compl, dates, isni, other_ids]
    if unidec:
        metas = [unidecode(meta) for meta in metas]
    return metas


def isni2id(input_record, parametres, origine="isni"):
    """
    Recherche d'un identifiant ARK ou PPN à partir d'un ISNI
    """
    Liste_ids = []
    if (parametres["preferences_alignement"] == 2):
        Liste_ids = aut2id_idref.isni2ppn(input_record, input_record.isni.propre,
                                             parametres,
                                             origine="accesspoint")
        if Liste_ids == []:
            liste_ark = isni2ark(input_record, parametres)
            for ark in liste_ark:
                ppn = aut2id_idref.autArk2ppn(input_record, ark)
                if (ppn):
                    Liste_ids.append(ppn)
                    input_record.alignment_method.append("ISNI > ARK > PPN")
                else:
                    Liste_ids.append(ark)
    else:
        Liste_ids = isni2ark(input_record, parametres)
    if (Liste_ids):
        if (origine == "isni"):
            input_record.alignment_method.append("ISNI")
    if type(Liste_ids) == list:
        Liste_ids = ",".join([el for el in Liste_ids if el])
    return Liste_ids


def isni2ark(input_record, parametres):
    liste_ark = []
    url = funcs.url_requete_sru(
            'aut.isni all "' + input_record.isni.propre + '" and aut.status any "sparse validated"')
    (test, page) = funcs.testURLetreeParse(url)
    if test:
        for ark in page.xpath("//srw:recordIdentifier", namespaces=main.ns):
            liste_ark.append(ark.text)
    return liste_ark




#==============================================================================
#             input_record.NumNot, input_record.lastname.propre, 
#             input_record.firstname.propre, input_record.firstdate.propre, 
#             input_record.lastdate.propre
#==============================================================================
def accesspoint2isniorg(input_record, parametres):
    url = "http://isni.oclc.nl/sru/?query=pica.nw%3D%22" + urllib.parse.quote(
        " ".join([
                input_record.lastname.propre, 
                input_record.firstname.propre, 
                input_record.firstdate.propre])
    ) + "%22&operation=searchRetrieve&recordSchema=isni-b"
    isnis = []
    (test, records) = funcs.testURLetreeParse(url)
    if test:
        for rec in records.xpath("//srw:records/srw:record", namespaces=main.nsisni):
            isni = ""
            if (rec.find("srw:recordData//isniURI",
                            namespaces=main.nsisni) is not None):
                isni = rec.find("srw:recordData//isniURI",
                                namespaces=main.nsisni).text
            forenames = []
            for forename in rec.xpath("srw:recordData//forename", namespaces=main.nsisni):
                if (unidecode(forename.text).lower() not in forenames):
                    forenames.append(unidecode(forename.text).lower())
            surnames = []
            for surname in rec.xpath("srw:recordData//surname", namespaces=main.nsisni):
                if (unidecode(surname.text).lower() not in surnames):
                    surnames.append(unidecode(surname.text).lower())
            dates = []
            for date in rec.xpath("srw:recordData//marcDate",
                                  namespaces=main.nsisni):
                if (unidecode(date.text).lower() not in dates):
                    dates.append(unidecode(date.text).lower())
            forenames = " ".join(forenames)
            surnames = " ".join(surnames)
            dates = " ".join(dates)
            if (input_record.lastname.propre in surnames 
                or surnames in input_record.lastname.propre):
                if (input_record.firstname.propre in forenames 
                    or forenames in input_record.firstname.propre):
                    if (input_record.firstdate.propre in dates 
                        or dates in input_record.firstdate.propre):
                        isnis.append(isni)
    if (isnis != []):
        input_record.alignment_method.append("Point d'accès > ISNI")
    i = 0
    if (parametres["preferences_alignement"] == 1):
        for isni in isnis:
            # isni_id = isni.split("/")[-1]
            ark = isni2id(input_record, parametres, origine="accesspoint")
            if (ark != ""):
                isnis[i] = ark
                input_record.alignment_method.append("ISNI > ARK")
            i += 1
    elif (parametres["preferences_alignement"] == 2):
        for isni in isnis:
            isni_id = isni.split("/")[-1]
            ppn = aut2id_idref.isni2ppn(input_record, isni_id,
                                           parametres,
                                           origine="accesspoint")
            if (ppn != ""):
                isnis[i] = ppn
                input_record.alignment_method.append("ISNI > PPN")
            i += 1
    if type(isnis == list):
        isnis = ",".join(isnis)
    return isnis


def aut2ark_by_id(input_record, parametres):
    """Alignement sur un identifiant ARK (actualisation)"""
    ark = ""
    if (ark == "" and input_record.ark_init != ""):
        ark = arkAut2arkAut(input_record, input_record.NumNot,
                            nettoyageArk(input_record.ark_init))
    if (ark == "" and input_record.isni.propre != ""):
        ark = isni2id(input_record, parametres)
    if (ark == "" and input_record.frbnf.propre != ""):
        ark = frbnfAut2arkAut(input_record)
    if (ark == "" and input_record.ppn.propre != ""):
        ark = aut2id_idref.idrefAut2arkAut(input_record)
    return ark


def align_from_aut_alignment(input_record, parametres):
    if (parametres["preferences_alignement"] == 1):
        ark = aut2ark_by_id(input_record, parametres)
        if (ark == ""):
            ark = aut2ark_by_accesspoint(
                    input_record,
                    input_record.NumNot, 
                    input_record.lastname.propre,
                    input_record.firstname.propre,
                    input_record.firstdate.propre,
                    input_record.lastdate.propre,
                    parametres
                    )
        if (ark == ""):
            ark = aut2id_idref.aut2ppn_by_id(input_record, parametres)
        if (ark == "" and input_record.lastname.propre):
            ark = aut2id_idref.aut2ppn_by_accesspoint(input_record, parametres)
        if (ark == ""):
            ark = aut2ark_by_id(input_record, parametres)
        if (ark == ""):
            ark = aut2ark_by_accesspoint(
                    input_record,
                    input_record.NumNot, 
                    input_record.lastname.propre,
                    input_record.firstname.propre,
                    input_record.firstdate.propre,
                    input_record.lastdate.propre,
                    parametres
                    )
    else:
        ark = aut2id_idref.aut2ppn_by_id(input_record, parametres)
        if (ark == "" and input_record.lastname.propre):
            ark = aut2id_idref.aut2ppn_by_accesspoint(input_record, parametres)
        if (ark == ""):
            ark = aut2ark_by_id(input_record, parametres)
        if (ark == ""):
            ark = aut2ark_by_accesspoint(
                    input_record,
                    input_record.NumNot, 
                    input_record.lastname.propre,
                    input_record.firstname.propre,
                    input_record.firstdate.propre,
                    input_record.lastdate.propre,
                    parametres
                    )

    if (ark == "" and parametres["isni_option"] == 1):
        ark = accesspoint2isniorg(input_record, parametres)
    alignment_result = funcs.Alignment_result(input_record, ark, parametres)
    return alignment_result



def alignment_result2output(alignment_result, input_record, parametres, liste_reports, n):
    """
    Format de sortie de l'alignement
    """
    print(str(n) + ". " + input_record.NumNot + " : " + alignment_result.ids_str)
    if parametres["meta_bnf"] == 1:
        alignment_result.liste_metadonnees.extend(ark2meta_aut(alignment_result.ids_str))
    if parametres["file_nb"] == 1:
        row2file(alignment_result.liste_metadonnees, liste_reports)
    elif parametres["file_nb"] == 2:
        row2files(alignment_result.liste_metadonnees, liste_reports)



def aut2id_item(row, n, parametres):
    if parametres["input_data_type"] in [1, 2]:
        input_record = funcs.Aut_record(row, parametres)
        alignment_result = align_from_aut_alignment(input_record, parametres)
    elif parametres["input_data_type"] == 3:
        input_record = funcs.Bib_Aut_record(row, parametres)
        alignment_result = align_from_bib_alignment(input_record, parametres)
    elif parametres["input_data_type"] == 4:
        input_record = funcs.Aut_record(row, parametres)
        alignment_result = align_from_rameau_alignment(input_record, parametres)
    return alignment_result


def align_aut_file(form, entry_filename, liste_reports, parametres):
    """Aligner ses données d'autorité avec les autorités BnF à partir
    d'une extraction tabulée de la base d'autorités"""
    header_columns = ["NumNot", "Nb identifiants trouvés", 
                      "Liste identifiants AUT trouvés", "Méthode"] + aligntype2headers[parametres["input_data_type"]][1:]
    if (parametres['meta_bnf'] == 1):
        header_columns.extend(
            ["[BnF/IdRef] Nom", "[BnF/IdRef] Complément Nom", "[BnF/IdRef] Dates", "[BnF/IdRef] ISNI", "[BnF/IdRef] Autres ID"])
    if (parametres['file_nb'] == 1):
        row2file(header_columns, liste_reports)
    elif(parametres['file_nb'] == 2):
        row2files(header_columns, liste_reports, headers=True)
    n = 1
    with open(entry_filename, newline='\n', encoding="utf-8") as csvfile:
        entry_file = csv.reader(csvfile, delimiter='\t')
        if (parametres['headers']):
            try:
                next(entry_file)
            except UnicodeDecodeError:
                main.popup_errors(
                    form, main.errors["pb_input_utf8"],
                    "Comment modifier l'encodage du fichier",
                    "https://github.com/Transition-bibliographique/bibliostratus/wiki/2-%5BBlanc%5D-:-alignement-des-donn%C3%A9es-bibliographiques-avec-la-BnF#erreur-dencodage-dans-le-fichier-en-entr%C3%A9e"  # noqa
                )
        for rows in funcs.chunks_iter(entry_file, NUM_PARALLEL):
            if ((n-1) == 0):
                assert main.control_columns_number(form,
                                                   rows[0],
                                                   aligntype2headers[parametres["input_data_type"]])
            if ((n-1) % 100 == 0):
                main.check_access2apis(n, dict_check_apis)
            alignment_results = Parallel(n_jobs=NUM_PARALLEL)(delayed(aut2id_item)(row, n, parametres) for row in rows)
            for alignment_result in alignment_results:
                alignment_result2output(alignment_result, alignment_result.input_record,
                                        parametres, liste_reports, n)
                if alignment_result.ids_str == "Pb FRBNF":
                    parametres["stats"]["Pb FRBNF"] += 1
                else:
                    parametres["stats"][alignment_result.nb_ids] += 1
                n += 1
        # for row in entry_file:
        #     align_from_aut_item(row, n, form, parametres, liste_reports)
        #     n += 1


def align_from_rameau_alignment(input_record, parametres):
    """
    Alignement sur une notice Rameau
    input_record est de type Aut_record
    Renvoie le résultat de l'alignement sous
    la forme d'un objet de class Alignment_result
    """
    arks = aut2ark_by_id(input_record, parametres)
    if (arks == ""):
        arks = aut2id_concepts.ram2ark_by_accesspoint(
                                                     input_record,
                                                     parametres
                                                    )
    # Si l'utilisateur préfère récupérer des PPN
    # on convertit les ARK en PPN
    if (arks 
       and parametres["preferences_alignement"] == 2):
        liste_ppn = []
        for ark in arks.split(","):
            ppn = aut2id_idref.autArk2ppn(input_record, ark)
            if ppn:
                liste_ppn.append(ppn)
                if ("type_notices_rameau" in parametres
                    and ark in parametres["type_notices_rameau"]):
                    parametres["type_notices_rameau"][ppn] = parametres["type_notices_rameau"][ark]
        liste_ppn = ",".join(liste_ppn)
        alignment_result = funcs.Alignment_result(input_record, liste_ppn,
                                                  parametres)
    else:
        alignment_result = funcs.Alignment_result(input_record, arks,
                                                  parametres)
    return alignment_result

def align_from_bib_alignment(input_record, parametres):
    """
    Alignement sur 1 notice de type Bib_Aut_record
    Renvoie le résultat de l'alignement sous
    la forme d'un objet de class Alignment_result
    """
    parametres["type_doc_bib"] = ""
    ark_trouve = ""
    if (ark_trouve == "" and input_record.isni.propre != ""):
        ark_trouve = isni2id(input_record, parametres)
    if (parametres["preferences_alignement"] == 1):
        if (ark_trouve == "" and input_record.ark_bib_init != ""):
            ark_trouve = arkBib2arkAut(input_record, parametres)
        if (ark_trouve == "" and input_record.frbnf_bib.init != ""):
            ark_trouve = frbnfBib2arkAut(input_record, parametres)
        if (ark_trouve == "" and input_record.isbn_bib.propre != ""):
            ark_trouve = isbnBib2arkAut(input_record, parametres)
        if (ark_trouve == "" and input_record.lastname != ""):
            ark_trouve = bib2arkAUT(input_record, parametres)
        if (ark_trouve == "" and input_record.lastname != ""):
            ark_trouve = bib2ppnAUT(input_record, parametres)
    else:
        if (ark_trouve == "" and input_record.isbn_bib.propre != ""):
            ark_trouve = isbnBib2ppnAut(input_record, parametres)
        if (ark_trouve == "" and input_record.lastname != ""):
            ark_trouve = bib2ppnAUT(input_record, parametres)
        if (ark_trouve == "" and input_record.ark_bib_init != ""):
            ark_trouve = arkBib2arkAut(input_record, parametres)
        if (ark_trouve == "" and input_record.frbnf_bib.init != ""):
            ark_trouve = frbnfBib2arkAut(input_record, parametres)
        if (ark_trouve == "" and input_record.lastname != ""):
            ark_trouve = bib2arkAUT(input_record, parametres)

    alignment_result = funcs.Alignment_result(input_record, ark_trouve,
                                              parametres)

    return alignment_result


def nettoyageArk(ark):
    ark_nett = ""
    if ("ark:/12148/cb" in ark):
        pos = ark.find("ark:/12148/cb")
        ark_nett = ark[pos:pos + 22]
    return ark_nett


# ==============================================================================
# Fonctions d'alignement : recherche sur identifiants, points d'accès ou titre-auteur
# ==============================================================================
def arkAut2arkAut(input_record, NumNot, ark):
    """Actualisation d'un ARK de notice d'autorité"""

    url = funcs.url_requete_sru('aut.persistentid all "' + ark + '"')
    (test, page) = funcs.testURLetreeParse(url)
    nv_ark = ""
    if test:
        if (page.find("//srw:recordIdentifier", namespaces=main.ns) is not None):
            nv_ark = page.find("//srw:recordIdentifier",
                               namespaces=main.ns).text
            input_record.alignment_method.append("Actualisation ARK")
    return nv_ark


def arkBib2arkAut(input_record, parametres):
    """Identifier un ARK de notice d'autorité
    à partir d'un ARK de notice BIB + contrôle sur le nom
    """
    url = funcs.url_requete_sru('bib.persistentid all "' + input_record.ark_bib_init + '"')
    (test, page) = funcs.testURLetreeParse(url)
    listeArk = []
    if test:
        for xml_record in page.xpath("//srw:recordData/*", namespaces=main.ns):
            arks = extractARKautfromBIB(input_record, xml_record)
            input_record.alignment_method.append("ARK notice BIB + contrôle accesspoint")
            if (parametres["preferences_alignement"] == 2):
                for ark in arks:
                    ppn = aut2id_idref.autArk2ppn(input_record, ark)
                    if (ppn):
                        listeArk.append(ppn)
                    else:
                        listeArk.append(ark)
            else:
                listeArk.extend(arks)
    if type(listeArk) == list:
        listeArk = ",".join([el for el in listeArk if el])
    return listeArk


def nettoyage_isni(isni):
    if (isni[0:20] == "http://www.isni.org"):
        isni = isni[20:36]
    else:
        isni = funcs.nettoyage(isni)
    for lettre in funcs.lettres:
        isni = isni.replace(lettre, "")
    return isni


def nettoyageFRBNF(frbnf):
    frbnf_nett = ""
    if (frbnf[0:4].lower() == "frbn"):
        frbnf_nett = unidecode(frbnf.lower())
    for signe in funcs.ponctuation:
        frbnf_nett = frbnf_nett.split(signe)[0]
    return frbnf_nett


def frbnfAut2arkAut(input_record):
    ark = ""
    url = funcs.url_requete_sru('aut.otherid all "' + input_record.frbnf.propre + '"')
    (test, page) = funcs.testURLetreeParse(url)
    if test:
        nb_resultats = int(
            page.find("//srw:numberOfRecords", namespaces=main.ns).text)
        if (nb_resultats == 0):
            ark = oldfrbnf2ark(input_record)
        elif (nb_resultats == 1):
            ark = page.find("//srw:recordIdentifier", namespaces=main.ns).text
        else:
            ark = ",".join([ark.text for ark in page.xpath(
                "//srw:recordIdentifier", namespaces=main.ns)])
    if (ark):
        input_record.alignment_method.append("FRBNF")
    return ark


def frbnfBib2arkAut(input_record, parametres):
    """Recherche de l'identifiant d'auteur à partir d'une recherche N° BIB + nom d'auteur :
        on cherche le n° BIB comme NNB, comme FRBNF ou comme ancien numéro"""
    listeArk = []
    bib_record = funcs.Bib_record([input_record.NumNot, input_record.frbnf_bib.init,
                                   "", "", "", input_record.titre.init,
                                   input_record.lastname.propre + " ", "", "", ""], 
                                   1)
    listeArk_bib = bib2id.frbnf2ark(bib_record)
    for ark in listeArk_bib:
        test, records = bib2id.ark2recordBNF(ark)
        if test:
            for record in records.xpath("//srw:recordData", namespaces=main.ns):
                listeArk.extend(extractARKautfromBIB(input_record, record))
    listeArk = ",".join(set(listeArk))
    if (listeArk != ""):
        input_record.alignment_method.append("FRBNF bib > ARK")
    return listeArk


def isbnBib2arkAut(input_record, parametres):
    """Recherche de l'identifiant d'auteur à partir d'une recherche ISBN + nom d'auteur :
        """
    listeArk = []
    bib_record = funcs.Bib_record([input_record.NumNot, input_record.frbnf_bib.init,
                                   "", input_record.isbn_bib.init, "", input_record.titre.init,
                                   input_record.lastname.propre + " ", "", "", ""], 
                                   1)
    listeArk_bib = bib2id.isbn2ark(bib_record,
                                   input_record.NumNot_bib, input_record.isbn_bib.init,
                                   input_record.isbn_bib.propre, "",
                                   input_record.titre.controles,
                                   input_record.lastname.propre,
                                   "")
    for ark in listeArk_bib.split(","):
        test, records = bib2id.ark2recordBNF(ark)
        if test:
            for record in records.xpath("//srw:recordData", namespaces=main.ns):
                listeArk.extend(extractARKautfromBIB(input_record, record))
    listeArk = ",".join(set(listeArk))
    if (listeArk != ""):
        input_record.alignment_method.append("ISBN bib > ARK")
    return listeArk


def isbnBib2ppnAut(input_record, parametres):
    """Recherche de l'identifiant d'auteur à partir d'une recherche ISBN + nom d'auteur :
        """
    listePPN = []
    bib_record = funcs.Bib_record([input_record.NumNot, input_record.frbnf_bib.init,
                                   "", input_record.isbn_bib.init, "", input_record.titre.init,
                                   input_record.lastname.propre + " ", "", "", ""], 
                                   1)
    listePPN_bib = bib2id.isbn2sudoc(bib_record, parametres)
    for ppn in listePPN_bib.split(","):
        if ppn:
            test, record = bib2id.ppn2recordSudoc(ppn)
            listePPN.extend(extractARKautfromBIB(input_record, record, "sudoc"))
    listePPN = ",".join(set(listePPN))
    if (listePPN != ""):
        input_record.alignment_method.append("ISBN bib > PPN")
    return listePPN

# Si le FRBNF n'a pas été trouvé, on le recherche comme numéro système ->
# pour ça on extrait le n° système

def oldfrbnf2ark(input_record):
    systemid = ""
    if (input_record.frbnf.propre[0:5] == "frbnf"):
        systemid = input_record.frbnf.propre[5:14]
    else:
        systemid = input_record.frbnf.propre[4:13]
    ark = rechercheNNA(input_record,
                    input_record.NumNot, 
                    systemid[0:8], 
                    input_record.lastname.propre)
    if (ark == ""):
        ark = systemid2ark(input_record, input_record.NumNot,
                           systemid, False, 
                           input_record.lastname.propre)
    return ark


def rechercheNNA(input_record, NumNot, nna, nom):
    ark = ""
    if (nna.isdigit() is False):
        # $1b_frbnf_source.write("\t".join[NumNot,nnb] + "\n")
        ark = "Pb FRBNF"
    elif (10000000 < int(nna) < 25000000):
        url = funcs.url_requete_sru('aut.recordid any "' + nna + '"')
        (test, page) = funcs.testURLetreeParse(url)
        if test:
            for record in page.xpath(
                    "//srw:records/srw:record", namespaces=main.ns):
                ark_current = record.find(
                    "srw:recordIdentifier", namespaces=main.ns).text
                ark = comparerAutBnf(input_record, NumNot, ark_current,
                                     nna, nom, "Numéro de notice")
    return ark


def systemid2ark(input_record, NumNot, systemid, tronque, nom):
    """
    Recherche par ancien numéro de notice
    Si présence d'un nom d'auteur, on contrôle sur le nom
    """
    url = funcs.url_requete_sru('aut.otherid all "' + systemid + '"')
    # $1rl = (
    #     "http://catalogueservice.bnf.fr/SRU?version=1.2&operation=searchRetrieve&query=NumNotice%20any%20%22"
    #     + systemid +
    #     "%22&recordSchema=InterXMarc_Complet&maximumRecords=1000&startRecord=1"
    # )
    listeARK = []
    (test, page) = funcs.testURLetreeParse(url)
    if (test):
        for record in page.xpath(
                "//srw:records/srw:record", namespaces=main.ns):
            ark_current = record.find(
                "srw:recordIdentifier", namespaces=main.ns).text
            if (nom != ""):
                for zone9XX in record.xpath(".//*[@tag]"):
                    # print(ark_current)
                    tag = zone9XX.get("tag")
                    if (tag[0] == "9"):
                        local_value = main.field2subfield(zone9XX, "a")
                        if local_value == systemid:
                            listeARK.append(comparerAutBnf(input_record,
                                                           NumNot, ark_current,
                                                           systemid, nom,
                                                           "Ancien n° notice")
                                           )
            else:
                listeARK.append(ark_current)
    listeARK = ",".join([ark for ark in listeARK if ark != ''])

    # Si pas de réponse, on fait la recherche SystemID + Nom auteur
    if (listeARK == ""):
        listeARK = relancerNNA_nomAuteur(input_record, NumNot, systemid, nom)
    listeARK = ",".join([ark1 for ark1 in listeARK.split(",") if ark1 != ''])

    # Si à l'issue d'une première requête sur le numéro système dont on a
    # conservé la clé ne donne rien -> on recherche sur le numéro tronqué
    # comme numéro système
    if (listeARK == "" and not tronque):
        systemid_tronque = systemid[0:len(systemid) - 1]
        systemid2ark(input_record, NumNot, systemid_tronque, True, nom)
    listeARK = ",".join([ark1 for ark1 in listeARK.split(",") if ark1 != ''])
    return listeARK


def relancerNNA_nomAuteur(input_record, NumNot, systemid, nom):
    listeArk = []
    if (nom != "" and nom is not None):
        urlSRU = funcs.url_requete_sru(
            'aut.accesspoint all "' + nom + '" and aut.otherid all "' + systemid + '"')
        (test, pageSRU) = funcs.testURLetreeParse(urlSRU)
        if test:
            for record in pageSRU.xpath(
                    "//srw:records/srw:record", namespaces=main.ns):
                ark = record.find("srw:recordIdentifier",
                                  namespaces=main.ns).text
                input_record.alignment_method.append("N° sys FRBNF + Nom")
                listeArk.append(ark)
    listeArk = ",".join(listeArk)
    return listeArk


def aut2ark_by_accesspoint(input_record, NumNot, nom_nett, prenom_nett, 
                           date_debut, date_fin, parametres):
    # Conversion du type d'autorité des codes Unimarc
    # en codes Intermarc pour le SRU BnF
    type_aut_dict = {"a" : "PEP",
                     "b": "ORG",
                     "a b": "PEP ORG"}

    listeArk = []
    url = funcs.url_requete_sru(
        'aut.accesspoint adj "' + " ".join([nom_nett, prenom_nett, date_debut]) 
        + '" and aut.status any "sparse validated"'
        + ' and aut.type any "' + type_aut_dict[parametres["type_aut"]] + '"')
    testdatefin = False
    if (date_debut == "" and date_fin != ""):
        url = funcs.url_requete_sru('aut.accesspoint adj "' + " ".join(
            [nom_nett, prenom_nett]) + '" and aut.accesspoint all "' + date_fin 
        + '" and aut.status any "sparse validated"'
        + ' and aut.type any "' + type_aut_dict[parametres["type_aut"]] + '"')
        testdatefin = True
    (test, results) = funcs.testURLetreeParse(url)
    if (test):
        for record in results.xpath("//srw:records/srw:record", namespaces=main.ns):
            ark = record.find("srw:recordIdentifier", namespaces=main.ns).text
            if testdatefin:
                f103a_datefin = main.extract_subfield(record, "103", "a")
                if (len(f103a_datefin) > 15):
                    f103a_datefin = f103a_datefin[11:15]
                    if (date_fin == f103a_datefin):
                        listeArk.append(ark)
                        input_record.alignment_method.append("Point d'accès avec date de fin")
            elif (date_debut != ""):
                listeArk.append(ark)
                input_record.alignment_method.append("Point d'accès avec date de début")
            else:
                listeArk.append(ark)
                input_record.alignment_method.append("Point d'accès")
    listeArk = ",".join(listeArk)
    return listeArk


def bib2arkAUT(input_record, parametres):
    listeArk = []
    pubDate = input_record.pubdate_nett
    if (input_record.pubdate_nett == ""):
        pubDate = "-"
    url = funcs.url_requete_sru("".join(['bib.title all "', input_record.titre.recherche,
                                         '" and bib.author all "', input_record.lastname.propre,
                                         " ", input_record.firstname.propre,
                                         '" and bib.publicationdate all "', pubDate, '"'
                                         ])).replace(
                                             "%20and%20bib.publicationdate%20all%20%22-%22",
                                             ""
                                         )
    (test, results) = funcs.testURLetreeParse(url)
    if (test):
        for record in results.xpath(
                "//srw:recordData", namespaces=main.ns):
            arks = extractARKautfromBIB(input_record, record)
            if arks:
                input_record.alignment_method.append("Titre-Auteur-Date > ARK Auteur")
            if (parametres["preferences_alignement"] == 2):
                for ark in arks:
                    ppn = aut2id_idref.autArk2ppn(input_record, ark)
                    if (ppn):
                        listeArk.append(ppn)
                        input_record.alignment_method.append("ARK > PPN")
                    else:
                        listeArk.append(ark)
            else:
                listeArk.extend(arks)

    listeArk = ",".join(set([el for el in listeArk if el]))
    if (listeArk != ""):
        input_record.alignment_method.append("Titre-Auteur-Date")
    return listeArk


def bib2ppnAUT(input_record, parametres):
    """
    Récupération du PPN à partir d'une recherche Titre-Auteur dans DoMyBiblio
    input_record en entrée est une instance de la classe Bib_Aut_record
    Pour chaque PPN trouvé dans DoMyBiblio, on ouvre la notice Unimarc
    --> contrôles sur le nom, prénom, date de naissance de l'auteur
    """
    listePPNaut = []
    listePPNbib = bib2ppnAUT_from_sudoc(input_record, parametres).split(",")
    listePPNbib = [el.replace("PPN", "") for el in listePPNbib if el]                        
    for ppn in listePPNbib:
        url = "https://www.sudoc.fr/" + ppn.replace("PPN", "") + ".xml"
        (test, results) = funcs.testURLetreeParse(url)
        if (test):
            for record in results.xpath(
                    "//record", namespaces=main.ns):
                listePPNaut.extend(extractARKautfromBIB(input_record, record, source="sudoc"))
    
    if parametres["preferences_alignement"] == 1:
        listeARKaut = []
        for el in listePPNaut:
            ark = idrefppn2arkAut(el)
            if ark:
                listeARKaut.append(ark)
            # Reprendre ici la conversion des PPN en ARK autorités
        if listeARKaut:
            listePPNaut = listeARKaut
    listePPNaut = ",".join(set([el for el in listePPNaut if el]))
    return listePPNaut


def idrefppn2arkAut(idrefppn):
    """ Conversion d'un PPN IdRef de personne en ARK BnF"""
    temp_aut_record = funcs.Aut_record(f",{idrefppn},,,,,,".split(","), {"input_data_type": 1})
    ark = aut2id_idref.idrefAut2arkAut(temp_aut_record, "idref")
    return ark


def bib2ppnAUT_from_sudoc(input_record, parametres):
    """
    Recherche dans le sudoc (interface web parsée)
    à partir d'un input_record d'instance Bib_Aut_record
    """
    listePPN = []
    listePPN = ",".join(bib2ppnAUT_from_isbnean(input_record, parametres))
    if len(listePPN) == 0:
        url = "http://www.sudoc.abes.fr//DB=2.1/SET=18/TTL=1/CMD?ACT=SRCHM\
&MATCFILTER=Y&MATCSET=Y&NOSCAN=Y&PARSE_MNEMONICS=N&PARSE_OPWORDS=N&PARSE_OLDSETS=N\
&IMPLAND=Y&ACT0=SRCHA&screen_mode=Recherche\
&IKT0=1004&TRM0=" + urllib.parse.quote(input_record.lastname.propre + " " + input_record.firstname.propre) + "\
&ACT1=*&IKT1=4&TRM1=" + urllib.parse.quote(input_record.titre.recherche) + "\
&ACT2=*&IKT2=1016&TRM2=&ACT3=*&IKT3=1016&TRM3=&SRT=YOP" + "\
&ADI_TAA=&ADI_LND=&ADI_JVU=" + urllib.parse.quote(input_record.pubdate_nett) + "\
&ADI_MAT="
        listePPN = bib2id.urlsudoc2ppn(url)
        listePPN = bib2id.check_sudoc_results(input_record, listePPN, "Titre-Auteur-Date")
    return listePPN


def bib2ppnAUT_from_isbnean(input_record, parametres):
    # Recherche de la notice BIB à partir de l'EAN
    listePPN = []

        # Si pas de résultats : on relance une recherche dans le Sudoc
    if (len(listePPN) == 0 and input_record.ean.propre):
        listePPN = bib2id.ean2sudoc(input_record, parametres, True).split(",")
        listePPN = [el for el in listePPN if el]
    # Si pas de résultats : on relance une recherche dans le Sudoc avec l'EAN
    # seul
    if (len(listePPN) == 0 and input_record.ean.propre):
        listePPN = bib2id.ean2sudoc(input_record, parametres, False).split(",")
        listePPN = [el for el in listePPN if el]
    if (len(listePPN) == 0 and input_record.isbn.propre):
        listePPN = bib2id.isbn2sudoc(input_record, parametres).split(",")
        listePPN = [el for el in listePPN if el]
    return listePPN

def nna2ark(nna):
    url = funcs.url_requete_sru(
        'aut.recordid any ' + nna + 'and aut.status any "sparse validated"')
    ark = ""
    (test, record) = funcs.testURLetreeParse(url)
    if (test):
        if (record.find("//srw:recordIdentifier", namespaces=main.ns) is not None):
            ark = record.find("//srw:recordIdentifier",
                              namespaces=main.ns).text
    return ark

# ==============================================================================
# Fonctions de comparaison pour contrôle
# ==============================================================================


def comparerAutBnf(input_record, NumNot, ark_current, nna, nom, origineComparaison):
    ark = ""
    url = funcs.url_requete_sru('aut.persistentid all "' + ark_current + '"')
    (test, recordBNF) = funcs.testURLetreeParse(url)
    if test:
        ark = compareAccessPoint(input_record, NumNot, ark_current, nna, nom, recordBNF)
    return ark


def compareAccessPoint(input_record, NumNot, ark_current, nna, nom, recordBNF):
    """Vérifier si deux noms de famille sont identiques.
    Contrôle pertinent si on part d'un identifiant (ancien FRBNF par exemple.
    Sinon, il vaut mieux utiliser compareFullAccessPoint"""
    ark = ""
    accessPointBNF = ""
    # Si le FRBNF de la notice source est présent comme ancien numéro de notice
    # dans la notice BnF, on compare les noms (100$a ou 110$a)
    accessPointBNF = main.clean_string(
        main.extract_subfield(recordBNF, "200", "a", "all", " "))
    if (accessPointBNF == ""):
        accessPointBNF = main.clean_string(
            main.extract_subfield(recordBNF, "210", "a", "all", " "))
    if (nom != "" and accessPointBNF != ""):
        if (nom in accessPointBNF):
            ark = ark_current
            input_record.alignment_method.append("N° sys FRBNF + contrôle Nom")
        if (accessPointBNF in nom):
            ark = ark_current
            input_record.alignment_method.append("N° sys FRBNF + contrôle Nom")
    return ark


def compareFullAccessPoint(NumNot, ark_current, recordBNF, nom, prenom, date_debut):
    """Comparaison des noms, puis des prénoms, puis des dates.
    Si les dates sont vides, on ne compare que noms et prénoms
    Si les prénoms sont vides, on ne compare que les noms"""
    nomBNF = main.clean_string(main.extract_subfield(
        recordBNF, "200", "a", "all", " "))
    prenomBNF = main.clean_string(
        main.extract_subfield(recordBNF, "200", "b", "all", " "))
    datesBNF = main.clean_string(
        main.extract_subfield(recordBNF, "200", "f", "all", " "))
    ark = ""
    if (nomBNF == ""):
        nomBNF = main.extract_subfield(recordBNF, "210", "a", "all", " ")
        prenomBNF = main.extract_subfield(recordBNF, "210", "b", "all", " ")
        datesBNF = main.extract_subfield(recordBNF, "210", "f", "all", " ")
    if (nom in nomBNF or nomBNF in nom):
        if (prenom != ""):
            if (prenom in prenomBNF or prenomBNF in prenom):
                if (date_debut != ""):
                    if (date_debut in datesBNF or datesBNF in date_debut):
                        ark = ark_current
                else:
                    ark = ark_current
        else:
            ark = ark_current
    return ark


def extractARKautfromBIB(input_record, xml_record, source="bnf"):
    """Récupère tous les auteurs d'une notice bibliographique
    et compare chacun avec un nom-prénom d'auteur en entrée"""
    listeNNA = []
    listeArk = []
    listeFieldsAuteur = defaultdict(dict)
    i = 0
    if xml_record is not None:
        for field in xml_record.xpath(".//*[@tag]"):
            i += 1
            if (field.get("tag")[0] == "7"):
                listeFieldsAuteur[i]["tag"] = field.get("tag")
                for subfield in field.xpath("*"):
                    if (subfield.get("code") == "3"):
                        listeFieldsAuteur[i]["nna"] = subfield.text
                    if (subfield.get("code") == "a"):
                        listeFieldsAuteur[i]["nom"] = main.clean_string(
                            subfield.text, True, True)
                    if (subfield.get("code") == "b"):
                        listeFieldsAuteur[i]["prenom"] = main.clean_string(
                            subfield.text, True, True)
                    if (subfield.get("code") == "f"):
                        listeFieldsAuteur[i]["dates"] = main.clean_string(
                            subfield.text, True, True)
    for auteur in listeFieldsAuteur:
        if (("nom" in listeFieldsAuteur[auteur])
            and (input_record.lastname.nett in listeFieldsAuteur[auteur]["nom"] or
            listeFieldsAuteur[auteur]["nom"] in input_record.lastname.nett)):
            if (input_record.firstname.nett != "" and "prenom" in listeFieldsAuteur[auteur]):
                if (input_record.firstname.nett in listeFieldsAuteur[auteur]["prenom"] 
                    or listeFieldsAuteur[auteur]["prenom"] in input_record.firstname.nett):
                    if (input_record.date_debut != "" and
                            "dates" in listeFieldsAuteur[auteur]):
                        if (input_record.date_debut in listeFieldsAuteur[auteur]["dates"] 
                            or listeFieldsAuteur[auteur]["dates"] in input_record.date_debut):
                            try:
                                listeNNA.append(listeFieldsAuteur[auteur]["nna"])
                            except KeyError:
                                pass
                    else:
                        try:
                            listeNNA.append(listeFieldsAuteur[auteur]["nna"])
                        except KeyError:
                            pass
            elif (input_record.date_debut != "" and "dates" in listeFieldsAuteur[auteur] and "nna" in listeFieldsAuteur[auteur]):
                if (input_record.date_debut in listeFieldsAuteur[auteur]["dates"] or
                        listeFieldsAuteur[auteur]["dates"] in input_record.date_debut):
                    listeNNA.append(listeFieldsAuteur[auteur]["nna"])
            elif ("nna" in listeFieldsAuteur[auteur]):
                listeNNA.append(listeFieldsAuteur[auteur]["nna"])
    if source == "bnf":
        for nna in listeNNA:
            listeArk.append(nna2ark(nna))
        return listeArk
    else:
        listeNNA = ["PPN"+el for el in listeNNA]
        return listeNNA


# ==============================================================================
# Gestion du formulaire
# ==============================================================================

def launch(entry_filename, headers, input_data_type, preferences_alignement, 
           isni_option, file_nb, meta_bnf, id_traitement, form=None):
    """
    Exécution du programme avec tous les paramètres, quand on clique
    sur le bouton OK
    """
    if entry_filename == []:
        main.popup_errors(form, "Merci d'indiquer un nom de fichier en entrée")
        raise
    else:
        entry_filename = entry_filename[0]
    try:
        [entry_filename, headers,
         input_data_type, preferences_alignement,
         isni_option, file_nb, meta_bnf, id_traitement] = [str(entry_filename), 
                                                           int(headers), int(input_data_type), 
                                                           int(preferences_alignement),
                                                           int(isni_option), int(file_nb), 
                                                           int(meta_bnf),
                                                           str(id_traitement)
                                                           ]
    except ValueError as err:
        print("\n\nDonnées en entrée erronées\n")
        print(err)
    # main.check_file_name(entry_filename)
    # results2file(nb_fichiers_a_produire)
    # Si la valeur input_data_type en entrée est 1 => PEP (code Unimarc IdRef "a")
    # Si cette valeur est 2 => ORG (code Unimarc IdRef "b")
    type_aut_dict = {
        1 : "a",
        2 : "b",
        3 : "a b",
        4 : "j"   # type de notice = Rameau
    }
    parametres = {"headers": headers,
                  "input_data_type": input_data_type,
                  "isni_option": isni_option,
                  "file_nb": file_nb,
                  "meta_bnf": meta_bnf,
                  "id_traitement": id_traitement,
                  "type_aut": type_aut_dict[input_data_type],
                  "preferences_alignement": preferences_alignement,
                  "stats":  defaultdict(int)}
    if (input_data_type == 4):
        parametres["type_notices_rameau"] = defaultdict(str)
    liste_reports = create_reports(funcs.id_traitement2path(id_traitement), file_nb)

    if (input_data_type in [1, 2, 3, 4]):
        align_aut_file(form, entry_filename, liste_reports, parametres)
    elif form is not None:
        main.popup_errors("Format en entrée non défini")
    bib2id.fin_traitements(form, liste_reports, parametres["stats"])


def form_aut2id(master, access_to_network=True, last_version=[0, False]):
    """
    Génération de la fenêtre de formulaire 
    d'alignement des notices d'autorité
    """
    couleur_fond = "white"
    couleur_bouton = "#515151"

    form, zone_alert_explications, zone_access2programs, zone_actions, \
        zone_ok_help_cancel, zone_notes = main.form_generic_frames(
            master, "Aligner ses données d'autorité avec la BnF ou IdRef",
            couleur_fond, couleur_bouton, access_to_network
        )

    zone_ok_help_cancel.config(padx=10)

    frame_input = tk.Frame(zone_actions,
                           bg=couleur_fond, padx=10, pady=10,
                           highlightthickness=2, highlightbackground=couleur_bouton)
    frame_input.pack(side="left", anchor="w", padx=10, pady=10)
    frame_input_header = tk.Frame(frame_input, bg=couleur_fond)
    frame_input_header.pack(anchor="w")
    frame_input_file = tk.Frame(frame_input, bg=couleur_fond)
    frame_input_file.pack()
    frame_input_aut = tk.Frame(frame_input, bg=couleur_fond,)
    frame_input_aut.pack(anchor="w")
    frame_input_aut_headers = tk.Frame(frame_input_aut, bg=couleur_fond,)
    frame_input_aut_headers.pack(anchor="w")
    frame_input_aut_input_data_type = tk.Frame(frame_input_aut, bg=couleur_fond,)
    frame_input_aut_input_data_type.pack()
    frame_input_aut_preferences = tk.Frame(frame_input_aut, bg=couleur_fond,)
    frame_input_aut_preferences.pack(anchor="w")

    frame_output = tk.Frame(zone_actions,
                            bg=couleur_fond, padx=10, pady=10,
                            highlightthickness=2, highlightbackground=couleur_bouton)
    frame_output.pack(side="left", anchor="w")
    frame_output_header = tk.Frame(frame_output, bg=couleur_fond)
    frame_output_header.pack(anchor="w")
    frame_output_file = tk.Frame(
        frame_output, bg=couleur_fond, padx=10, pady=10)
    frame_output_file.pack(anchor="w")

    zone_notes_message_en_cours = tk.Frame(
        zone_notes, padx=20, bg=couleur_fond)
    zone_notes_message_en_cours.pack()

    tk.Label(frame_input_header, text="En entrée", font="bold",
             fg=couleur_bouton, bg=couleur_fond).pack()

    tk.Label(frame_input_file, text="Fichier contenant \nles notices d'autorité à aligner\n\n",
             bg=couleur_fond, justify="left").pack(side="left", anchor="w")

    
    main.download_zone(frame_input_file,
                       "Sélectionner un fichier\nSéparateur TAB, Encodage UTF-8",
                       entry_file_list, couleur_fond, zone_notes_message_en_cours)

    # Fichier avec en-têtes ?
    
    headers = tk.IntVar()
    """tk.Checkbutton(frame_input_aut, text="Mon fichier a des en-têtes de colonne",
                   variable=headers,
                   bg=couleur_fond, justify="left").pack(anchor="w")"""
    headers.set(1)

    input_data_type = tk.IntVar()
    input_data_type.set(1)

    # Préférences : BnF > Idref ou IdRef > BnF
    preferences_alignement = tk.IntVar()
    preferences_alignement.set(1)

    # Option Relance sur isni ?
    isni_option = tk.IntVar()
    isni_option.set(1)


    tk.Label(frame_output_header, text="En sortie", font="bold",
             fg=couleur_bouton, bg=couleur_fond).pack()

    main.download_zone(
        frame_output_file,
        "Sélectionner un dossier\nde destination",
        main.output_directory,
        couleur_fond,
        type_action="askdirectory",
        widthb = [40,1]
    )

    file_nb = tk.IntVar()
    file_nb.set(1)

    meta_bnf = tk.IntVar()
    meta_bnf.set(0)

    frame2var = [{"frame": frame_input_aut_headers,
                  "name": "frame_input_aut_headers",
                  "variables": [["headers", headers]]},
                  {"frame": frame_input_aut_input_data_type,
                  "name": "frame_input_aut_input_data_type",
                  "variables": [["input_data_type", input_data_type]]},
                  {"frame": frame_input_aut_preferences,
                   "name": "frame_input_aut_preferences",
                   "variables": [["preferences_alignement", preferences_alignement],
                                 ["isni_option", isni_option]]},
                  {"frame": frame_output_file,
                  "name": "frame_output_file",
                  "variables": [["file_nb", file_nb],
                                ["meta_bnf", meta_bnf]]}
                ]

    forms.display_options(frame2var, forms.form_aut2id)
    outputID = forms.Entry(frame_output_file,
                           forms.form_aut2id["frame_output_file"]["outputID"]["title"],
                           forms.form_aut2id["frame_output_file"]["outputID"]["params"])
    forms.add_saut_de_ligne(frame_output_file, nb_sauts=7)

    b = tk.Button(zone_ok_help_cancel, text="Aligner\nles autorités",
                  command=lambda: launch(entry_file_list, headers.get(),
                                         input_data_type.get(),
                                         preferences_alignement.get(), 
                                         isni_option.get(),
                                         file_nb.get(), meta_bnf.get(),
                                         outputID.value.get(), form),
                  width=15, borderwidth=1, pady=40, fg="white",
                  bg=couleur_bouton, font="Arial 10 bold"
                  )
    b.pack()

    main.form_saut_de_ligne(zone_ok_help_cancel, couleur_fond)
    call4help = tk.Button(zone_ok_help_cancel,
                          text=main.texte_bouton_help,
                          command=lambda: main.click2url(main.url_online_help),
                          pady=5, padx=5, width=12)
    call4help.pack()
    tk.Label(zone_ok_help_cancel, text="\n",
             bg=couleur_fond, font="Arial 1 normal").pack()

    forum_button = forms.forum_button(zone_ok_help_cancel)
    forum_button.pack()

    tk.Label(zone_ok_help_cancel, text="\n",
             bg=couleur_fond, font="Arial 4 normal").pack()
    cancel = tk.Button(zone_ok_help_cancel, text="Annuler", bg=couleur_fond,
                       command=lambda: main.annuler(form), pady=10, padx=5, width=12)
    cancel.pack()

    forms.footer(zone_notes, couleur_fond)

    tk.mainloop()


if __name__ == '__main__':
    multiprocessing.freeze_support()
    forms.default_launch()
