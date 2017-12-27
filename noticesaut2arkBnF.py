# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 18:30:30 2017

@author: Etienne Cavalié

Programme de manipulations de données liées à la Transition bibliographique 
Alignement des données d'autorité

"""

from lxml import etree
from urllib import request
import urllib.parse
from unidecode import unidecode
import urllib.error as error
import csv
import tkinter as tk
from tkinter import filedialog
from collections import defaultdict
import webbrowser
import codecs
import json
import noticesbib2arkBnF as bib2ark
import marc2tables as marc2tables
import ark2records as ark2records
import main as main

#import matplotlib.pyplot as plt

version = 0.03
lastupdate = "26/12/2017"
programID = "noticesaut2arkBnF"

#Pour chaque notice, on recense la méthode qui a permis de récupérer le ou les ARK
NumNotices2methode = defaultdict(list)

def create_reports(id_traitement_code, nb_fichiers_a_produire):
    reports = []
    stats_report_file_name=id_traitement_code + "-" + "rapport_stats_noticesbib2ark.txt"
    stats_report_file = open(stats_report_file_name,"w")
    stats_report_file.write("Nb ARK trouvés\tNb notices concernées\n")
    
    report_type_convert_file_name = id_traitement_code + "-" + "NumNotices-TypeConversion.txt"
    report_type_convert_file = open(report_type_convert_file_name,"w")
    report_type_convert_file.write("NumNotice\tMéthode pour trouver l'ARK\n")
    if (nb_fichiers_a_produire == 1):
        reports = create_reports_1file(id_traitement_code)
    else:
        reports = create_reports_files(id_traitement_code)
    reports.append(stats_report_file)
    reports.append(report_type_convert_file)
    return reports

def create_reports_1file(id_traitement_code):
    unique_file_results_frbnf_isbn2ark_name = id_traitement_code + "-" + "resultats_noticesbib2arkBnF.txt"
    unique_file_results_frbnf_isbn2ark = open(unique_file_results_frbnf_isbn2ark_name, "w", encoding="utf-8")
    return [unique_file_results_frbnf_isbn2ark]
    
def create_reports_files(id_traitement_code):    
    multiple_files_pbFRBNF_ISBN_name = id_traitement_code + "-resultats_Probleme_FRBNF_ISBN.txt"
    multiple_files_0_ark_name =  id_traitement_code + "-resultats_0_ark_trouve.txt"
    multiple_files_1_ark_name =  id_traitement_code + "-resultats_1_ark_trouve.txt"
    multiple_files_plusieurs_ark_name =  id_traitement_code + "-resultats_plusieurs_ark_trouves.txt"
    
    multiple_files_pbFRBNF_ISBN = open(multiple_files_pbFRBNF_ISBN_name, "w", encoding="utf-8")
    multiple_files_0_ark = open(multiple_files_0_ark_name, "w", encoding="utf-8")
    multiple_files_1_ark = open(multiple_files_1_ark_name, "w", encoding="utf-8")
    multiple_files_plusieurs_ark_name = open(multiple_files_plusieurs_ark_name, "w", encoding="utf-8")
    
    return [multiple_files_pbFRBNF_ISBN,multiple_files_0_ark,multiple_files_1_ark,multiple_files_plusieurs_ark_name]


# Rapport statistique final
nb_notices_nb_ARK = defaultdict(int)

def row2file(liste_metadonnees,liste_reports):
    liste_metadonnees_to_report = [str(el) for el in liste_metadonnees]
    liste_reports[0].write("\t".join(liste_metadonnees_to_report ) + "\n")

def row2files(liste_metadonnees,liste_reports):
    liste_metadonnees_to_report = [str(el) for el in liste_metadonnees]
    nbARK = liste_metadonnees[0]
    ark = liste_metadonnees[2]
    if (ark == "Pb FRBNF"):
        liste_reports[0].write("\t".join(liste_metadonnees_to_report) + "\n")
    elif (nbARK == 0):
        liste_reports[1].write("\t".join(liste_metadonnees_to_report) + "\n")
    elif (nbARK == 1):
        liste_reports[2].write("\t".join(liste_metadonnees_to_report) + "\n")
    else:
        liste_reports[3].write("\t".join(liste_metadonnees_to_report) + "\n")


#Si on a coché "Récupérer les données bibliographiques" : ouverture de la notice BIB de l'ARK et renvoie d'une liste de métadonnées
def ark2metadc(ark):
#Attention : la variable 'ark' peut contenir plusieurs ark séparés par des virgules
    listeARK = ark.split(",")

    #On récupére tous les titres de chaque ARK, puis tous les auteurs
    accesspointList = []
    accesspoint_complList = []
    datesList = []
    for ark in listeARK:
        metas_ark = ark2metas(ark,False)
        accesspointList.append(metas_ark[0])
        accesspoint_complList.append(metas_ark[1])
        datesList.append(metas_ark[2])
    accesspointList = "|".join(accesspointList)
    accesspoint_complList = "|".join(accesspoint_complList)
    datesList = "|".join(datesList)
    metas = [accesspointList,accesspoint_complList,datesList]
    return metas

def ark2metas(ark, unidec=True):
    recordBNF_url = bib2ark.url_requete_sru('bib.persistentid any "' + ark + '"')
    (test,record) = bib2ark.testURLetreeParse(recordBNF_url)
    accesspoint = ""
    accesspoint_compl = ""
    dates = ""
    if (test == True):
        if (record.find("//mxc:datafield[@tag='200']/mxc:subfield[@code='a']", namespaces=main.ns) is not None):
            accesspoint = record.find("//mxc:datafield[@tag='200']/mxc:subfield[@code='a']", namespaces=main.ns).text
        if (record.find("//mxc:datafield[@tag='210']/mxc:subfield[@code='a']", namespaces=main.ns) is not None):
            accesspoint = record.find("//mxc:datafield[@tag='210']/mxc:subfield[@code='a']", namespaces=main.ns).text
        if (record.find("//mxc:datafield[@tag='200']/mxc:subfield[@code='b']", namespaces=main.ns) is not None):
            accesspoint_compl = record.find("//mxc:datafield[@tag='200']/mxc:subfield[@code='b']", namespaces=main.ns).text
        if (record.find("//mxc:datafield[@tag='210']/mxc:subfield[@code='b']", namespaces=main.ns) is not None):
            accesspoint_compl = record.find("//mxc:datafield[@tag='210']/mxc:subfield[@code='b']", namespaces=main.ns).text

        if (record.find("//mxc:datafield[@tag='200']/mxc:subfield[@code='f']", namespaces=main.ns) is not None):
            dates = record.find("//mxc:datafield[@tag='200']/mxc:subfield[@code='f']", namespaces=main.ns).text
        if (record.find("//mxc:datafield[@tag='210']/mxc:subfield[@code='f']", namespaces=main.ns) is not None):
            dates = record.find("//mxc:datafield[@tag='210']/mxc:subfield[@code='f']", namespaces=main.ns).text

    metas = [accesspoint,accesspoint_compl,dates]
    if (unidec == True):
        metas = [unidecode(meta) for meta in metas]
    return metas




def align_from_aut(master, entry_filename, headers, input_data_type, file_nb, id_traitement, liste_reports, meta_bnf):
    header_columns = ["nbARK","NumNot","ark initial","frbnf initial","ISNI", "ark trouvé","Nom","Complément nom","Date début","Date fin"]
    if (meta_bnf == 1):
        header_columns.extend(["[BnF] Nom","[BnF] Complément Nom","[BnF] Dates"])
    if (file_nb ==  1):
        row2file(header_columns,liste_reports)
    elif(file_nb ==  2):
        row2files(header_columns,liste_reports)
    n = 0
    with open(entry_filename, newline='\n',encoding="utf-8") as csvfile:
        entry_file = csv.reader(csvfile, delimiter='\t')
        if (headers):
            next(entry_file)
        for row in entry_file:
            n += 1
            NumNot = row[0]
            ark_init = row[1]
            frbnf_init = row[2]
            isni = row[3]
            nom = row[4]
            nom_nett = main.clean_string(nom, False, True)
            prenom = row[5]
            prenom_nett = main.clean_string(prenom, False, True)
            date_debut = row[6]
            date_fin = row[7]
            ark_trouve = ""
            if (ark_init != ""):
                ark_trouve = ark2ark(NumNot, ark_init)
            if (ark_trouve == "" and isni != ""):
                ark_trouve = isni2ark(NumNot, isni)
            if (ark_trouve == "" and frbnf_init != ""):
                ark_trouve = frbnf2ark(NumNot, ark_init, nom_nett)
            if (ark_trouve == "" and nom != ""):
                ark_trouve = accesspoint2ark(NumNot, nom_nett, prenom_nett, date_debut, date_fin)
            print(str(n) + ". " + NumNot + " : " + ark_trouve)
            nbARK = len(ark_trouve.split(","))
            if (ark_trouve == ""):
                nbARK = 0   
            if (ark_trouve == "Pb FRBNF"):
                nb_notices_nb_ARK["Pb FRBNF"] += 1
            else:
                nb_notices_nb_ARK[nbARK] += 1
            liste_metadonnees = [nbARK,NumNot,ark_init,frbnf_init,isni,ark_trouve,nom,prenom,date_debut,date_fin]
            if (meta_bnf == 1):
                liste_metadonnees.extend(ark2metadc(ark_trouve))
            if (file_nb.get() ==  1):
                row2file(liste_metadonnees,liste_reports)
            elif(file_nb.get() ==  2):
                row2files(liste_metadonnees,liste_reports)


def align_from_bib(master, entry_filename, headers, input_data_type, file_nb, id_traitement, liste_reports, meta_bnf):
    header_columns = ["nbARK","NumNot","ark initial","frbnf initial","ISNI","ark trouvé", "Titre","Nom","Complément nom","date début"]
    if (meta_bnf == 1):
        header_columns.extend(["[BnF] Nom","[BnF] Complément Nom","[BnF] Dates"])
    if (file_nb ==  1):
        row2file(header_columns,liste_reports)
    elif(file_nb ==  2):
        row2files(header_columns,liste_reports)
    n = 0
    with open(entry_filename, newline='\n',encoding="utf-8") as csvfile:
        entry_file = csv.reader(csvfile, delimiter='\t')
        if (headers):
            next(entry_file)
        for row in entry_file:
            n += 1
            NumNot = row[0]
            ark_init = row[1]
            frbnf_init = row[2]
            isni = row[3]
            titre = row[4]
            titre_nett = main.clean_string(titre, False, True)
            nom = row[5]
            nom_nett = main.clean_string(nom, False, True)
            prenom = row[6]
            prenom_nett = main.clean_string(prenom, False, True)
            date_debut = row[7]
            ark_trouve = ""
            if (ark_trouve == ""):
                ark_trouve = bib2arkAUT(NumNot, titre_nett, nom_nett, prenom_nett, date_debut)
            print(str(n) + ". " + NumNot + " : " + ark_trouve)
            nbARK = len(ark_trouve.split(","))
            if (ark_trouve == ""):
                nbARK = 0   
            if (ark_trouve == "Pb FRBNF"):
                nb_notices_nb_ARK["Pb FRBNF"] += 1
            else:
                nb_notices_nb_ARK[nbARK] += 1
            liste_metadonnees = [nbARK,NumNot,ark_init,frbnf_init,isni,ark_trouve,nom,prenom,date_debut,titre]
            if (meta_bnf == 1):
                liste_metadonnees.extend(ark2metadc(ark_trouve))
            if (file_nb.get() ==  1):
                row2file(liste_metadonnees,liste_reports)
            elif(file_nb.get() ==  2):
                row2files(liste_metadonnees,liste_reports)

#==============================================================================
# Fonctions d'alignement
#==============================================================================
def ark2ark(NumNot,ark):
    url = bib2ark.url_requete_sru('aut.persistentid all "' + ark + '"')
    (test,page) = bib2ark.testURLetreeParse(url)
    nv_ark = ""
    if (test == True):
        if (page.find("//srw:recordIdentifier", namespaces=main.ns) is not None):
            nv_ark = page.find("//srw:recordIdentifier", namespaces=main.ns).text
            NumNotices2methode[NumNot].append("Actualisation ARK")
    return nv_ark

def isni2ark(NumNot, isni):
    url = bib2ark.url_requete_sru('aut.isni all "' + isni + '"')
    (test,page) = bib2ark.testURLetreeParse(url)
    nv_ark = ""
    if (test == True):
        if (page.find("//srw:recordIdentifier", namespaces=main.ns) is not None):
            nv_ark = page.find("//srw:recordIdentifier", namespaces=main.ns).text
            NumNotices2methode[NumNot].append("ISNI")
    return nv_ark

def frbnf2ark(NumNot,frbnf,nom):
    ark = ""
    url = bib2ark.url_requete_sru('aut.otherid all "' + frbnf + '"')
    (test,page) = bib2ark.testURLetreeParse(url)
    if (test == True):
        nb_resultats = int(page.find("//srw:numberOfRecords", namespaces=main.ns).text)
        if (nb_resultats == 0):
            ark = oldfrbnf2ark(NumNot,frbnf,nom)
        elif (nb_resultats == 1):
            ark = page.find("//srw:recordIdentifier", namespaces=main.ns).text
            NumNotices2methode[NumNot].append("FRBNF")
        else:
            ark = ",".join([ark.text for ark in page.xpath("//srw:recordIdentifier", namespaces=main.ns)])
    return ark

#Si le FRBNF n'a pas été trouvé, on le recherche comme numéro système -> pour ça on extrait le n° système
def oldfrbnf2ark(NumNot, frbnf, nom):
    systemid = ""
    if (frbnf[0:5].upper() == "FRBNF"):
        systemid = frbnf[5:14]
    else:
        systemid = frbnf[4:13]
    ark = rechercheNNA(NumNot,systemid[0:8],nom)
    if (ark==""):
        ark = systemid2ark(NumNot,systemid,False,nom)
    return ark

def rechercheNNA(NumNot,nna,nom):
    ark = ""
    if (nna.isdigit() is False):
        #pb_frbnf_source.write("\t".join[NumNot,nnb] + "\n")
        ark = "Pb FRBNF"
    elif (10000000 < int(nna) < 25000000):
        url = bib2ark.url_requete_sru('aut.recordid any "' + nna + '"')
        (test,page) = bib2ark.testURLetreeParse(url)
        if (test == True):
            for record in page.xpath("//srw:records/srw:record", namespaces=main.ns):
                ark_current = record.find("srw:recordIdentifier",namespaces=main.ns).text
                ark = comparerAutBnf(NumNot,ark_current,nna,nom,"Numéro de notice")
    return ark

def systemid2ark(NumNot,systemid,tronque,nom):
    url = bib2ark.url_requete_sru('aut.otherid all "' + systemid + '"')
    #url = "http://catalogueservice.bnf.fr/SRU?version=1.2&operation=searchRetrieve&query=NumNotice%20any%20%22" + systemid + "%22&recordSchema=InterXMarc_Complet&maximumRecords=1000&startRecord=1"
    listeARK = []
    (test,page) = bib2ark.testURLetreeParse(url)
    if (test):
        for record in page.xpath("//srw:records/srw:record", namespaces=main.ns):
            ark_current = record.find("srw:recordIdentifier",namespaces=main.ns).text
            for zone9XX in record.xpath("srw:recordData/mxc:record/mxc:datafield", namespaces=main.ns):
                #print(ark_current)
                tag = zone9XX.get("tag")
                if (tag[0:1] =="9"):
                    if (zone9XX.find("mxc:subfield[@code='a']", namespaces=main.ns) is not None):
                        if (zone9XX.find("mxc:subfield[@code='a']", namespaces=main.ns).text is not None):
                            if (zone9XX.find("mxc:subfield[@code='a']", namespaces=main.ns).text == systemid):
                                #print(zone9XX.get("tag"))
                                listeARK.append(comparerAutBnf(NumNot,ark_current,systemid,nom, "Ancien n° notice"))
    listeARK = ",".join([ark1 for ark1 in listeARK if ark1 != ''])    

#Si pas de réponse, on fait la recherche SystemID + Nom auteur
    if (listeARK == ""):
        listeARK = relancerNNA_nomAuteur(NumNot,systemid,nom)
    listeARK = ",".join([ark1 for ark1 in listeARK.split(",") if ark1 != ''])
    
#Si à l'issue d'une première requête sur le numéro système dont on a conservé la clé ne donne rien -> on recherche sur le numéro tronqué comme numéro système
    if (listeARK == "" and tronque == False):
        systemid_tronque = systemid[0:len(systemid)-1]
        systemid2ark(NumNot, systemid_tronque, True, nom)   
    listeARK = ",".join([ark1 for ark1 in listeARK.split(",") if ark1 != ''])   
    return listeARK

def relancerNNA_nomAuteur(NumNot,systemid,nom):
    listeArk = []
    if (nom != "" and nom is not None):
        urlSRU = bib2ark.url_requete_sru('aut.accesspoint all "' + nom + '" and aut.otherid all "' + systemid + '"')
        (test,pageSRU) = bib2ark.testURLetreeParse(urlSRU)
        if (test == True):
            for record in pageSRU.xpath("//srw:records/srw:record", namespaces=main.ns):
                ark = record.find("srw:recordIdentifier", namespaces=main.ns).text
                NumNotices2methode[NumNot].append("N° sys FRBNF + Nom")
                listeArk.append(ark)
    listeArk = ",".join(listeArk)
    return listeArk

def accesspoint2ark(NumNot, nom_nett, prenom_nett, date_debut, date_fin):
    listeArk = []
    url = bib2ark.url_requete_sru(" ".join(["aut.accesspoint adj", nom_nett, prenom_nett, date_debut]))
    (test,results) = bib2ark.testURLetreeParse(url)
    if (test):
        for record in results.xpath("//srw:recordIdentifier", namespaces=main.ns):
            listeArk.append(record.text)
            NumNotices2methode[NumNot].append("Access point")
    listeArk = ",".join(listeArk)
    return listeArk

def bib2arkAUT(NumNot, titre, nom, prenom, date_debut):
    listeArk = []
    url = bib2ark.url_requete_sru("".join('bib.title all "',titre,
                                          '" and bib.author all "',nom," ",prenom))
    (test,results) = bib2ark.testURLetreeParse(url)
    if (test):
        for record in results.xpath("//srw:recordData:mxc:record",namespaces=main.ns):
            listeArk.extend(extractNNAfromBIB(record,nom,prenom,date_debut))
    listeArk = ",".join(set(listeArk))
    return listeArk

def nna2ark(nna):
    url = bib2ark.url_requete_sru("aut.record any " + nna)
    ark = ""
    (test,record)=bib2ark.testURLetreeParse(url)
    if (test):
        if (record.find("//srw:recordIdentifier",namespaces=main.ns) is not None):
            ark = record.find("//srw:recordIdentifier",namespaces=main.ns).text
    return ark

#==============================================================================
# Fonctions de comparaison pour contrôle
#==============================================================================

def comparerAutBnf(NumNot,ark_current,nna,nom,origineComparaison):
    ark = ""
    url = bib2ark.url_requete_sru('aut.persistentid all "' + ark_current + '"')
    (test,recordBNF) = bib2ark.testURLetreeParse(url)
    if (test == True):
        ark =  compareAccessPoint(NumNot,ark_current,nna,nom,recordBNF)
    return ark

def compareAccessPoint(NumNot,ark_current,nna,nom,recordBNF):
    ark = ""
    accessPointBNF = ""
    #Si le FRBNF de la notice source est présent comme ancien numéro de notice 
    #dans la notice BnF, on compare les noms (100$a ou 110$a)
    if (recordBNF.find("//mxc:datafield[@tag='100']/mxc:subfield[@code='a']", namespaces=main.ns) is not None):
        accessPointBNF = main.clean_string(recordBNF.find("//mxc:datafield[@tag='100']/mxc:subfield[@code='a']", namespaces=main.ns).text)
    elif (recordBNF.find("//mxc:datafield[@tag='110']/mxc:subfield[@code='a']", namespaces=main.ns) is not None):
        accessPointBNF = main.clean_string(recordBNF.find("//mxc:datafield[@tag='110']/mxc:subfield[@code='a']", namespaces=main.ns).text)
    if (nom != "" and accessPointBNF != ""):
        if (nom in accessPointBNF):
            ark = ark_current
            NumNotices2methode[NumNot].append("N° sys FRBNF + contrôle Nom")
        if (accessPointBNF in nom):
            ark = ark_current
            NumNotices2methode[NumNot].append("N° sys FRBNF + contrôle Nom")
    return ark

def extractNNAfromBIB(record,nom,prenom,date_debut):
    listeNNA = []
    listeArk = []
    listeFieldsAuteur = defaultdict(dict)
    i = 0
    for field in extractNNAfromBIB.xpath("mxc:datafield",namespaces=main.ns):
        i += 1
        if (field.get("tag")[0] == "7"):
            listeFieldsAuteur[i]["tag"] = field.get("tag") 
            for subfield in field.xpath("mxc:subfield",namespaces=main.ns):
                if (subfield.get("code")=="3"):
                    listeFieldsAuteur[i]["nna"] = subfield.text
                if (subfield.get("code")=="a"):
                    listeFieldsAuteur[i]["nom"] = main.clean_string(subfield.text,False,True)
                if (subfield.get("code")=="b"):
                    listeFieldsAuteur[i]["prenom"] = main.clean_string(subfield.text,False,True)
                if (subfield.get("code")=="f"):
                    listeFieldsAuteur[i]["dates"] = main.clean_string(subfield.text,False,True)
    for auteur in listeFieldsAuteur:
        if (nom in listeFieldsAuteur[auteur]["nom"] or listeFieldsAuteur[auteur]["nom"] in nom):
            if (prenom != "" and "prenom" in listeFieldsAuteur[auteur]):
                if (prenom in listeFieldsAuteur[auteur][prenom] or listeFieldsAuteur[auteur][prenom in nom]):
                    if (date_debut != "" and "dates" in listeFieldsAuteur[auteur]):
                        if (date_debut in listeFieldsAuteur[auteur]["dates"] or listeFieldsAuteur[auteur]["dates"] in date_debut):
                            listeNNA.append(listeFieldsAuteur[auteur]["nna"])
                    else:
                        listeNNA.append(listeFieldsAuteur[auteur]["nna"])
                elif (date_debut != "" and "dates" in listeFieldsAuteur[auteur]):
                    if (date_debut in listeFieldsAuteur[auteur]["dates"] or listeFieldsAuteur[auteur]["dates"] in date_debut):
                        listeNNA.append(listeFieldsAuteur[auteur]["nna"])
                else:
                    listeNNA.append(listeFieldsAuteur[auteur]["nna"])
    for nna in listeNNA:
        listeArk.append(nna2ark(nna))
    return listeArk



#==============================================================================
# Gestion du formulaire
#==============================================================================

def launch(master, entry_filename, headers, input_data_type, file_nb, id_traitement, meta_bnf):
    #results2file(nb_fichiers_a_produire)
    liste_reports = create_reports(id_traitement, file_nb)    
    
    if (input_data_type == 1):
        align_from_aut(master, entry_filename, headers, input_data_type, file_nb, id_traitement, liste_reports, meta_bnf)
    elif (input_data_type == 2):
        align_from_bib(master, entry_filename, headers, input_data_type, file_nb, id_traitement, liste_reports, meta_bnf)
    else:
        main.popup_errors("Format en entrée non défini")


def formulaire_noticesaut2arkBnF(access_to_network=True, last_version=[0,False]):
    couleur_fond = "white"
    couleur_bouton = "#515151"
    
    [master,
     zone_alert_explications,
     zone_access2programs,
     zone_actions,
     zone_ok_help_cancel,
     zone_notes] = main.form_generic_frames("Aligner ses données d'autorité avec les notices BnF",
                                      couleur_fond,couleur_bouton,
                                      access_to_network)
    
    zone_ok_help_cancel.config(padx=10)
    
    frame_input = tk.Frame(zone_actions, 
                           bg=couleur_fond, padx=10, pady=10,
                           highlightthickness=2, highlightbackground=couleur_bouton)
    frame_input.pack(side="left", anchor="w", padx=10,pady=10)
    frame_input_header = tk.Frame(frame_input,bg=couleur_fond)
    frame_input_header.pack(anchor="w")
    frame_input_file = tk.Frame(frame_input, bg=couleur_fond)
    frame_input_file.pack()
    frame_input_aut = tk.Frame(frame_input, bg=couleur_fond,)
    frame_input_aut.pack(anchor="w")
    
    frame_output = tk.Frame(zone_actions, 
                           bg=couleur_fond, padx=10, pady=10,
                           highlightthickness=2, highlightbackground=couleur_bouton)
    frame_output.pack(side="left", anchor="w")
    frame_output_header = tk.Frame(frame_output,bg=couleur_fond)
    frame_output_header.pack(anchor="w")
    frame_output_file = tk.Frame(frame_output, bg=couleur_fond, padx=10, pady=10)
    frame_output_file.pack(anchor="w")
    frame_output_options = tk.Frame(frame_output, bg=couleur_fond, padx=10, pady=10)
    frame_output_options.pack(anchor="w")
    frame_output_options_marc = tk.Frame(frame_output_options, bg=couleur_fond)
    frame_output_options_marc.pack(side="left", anchor="nw")
    frame_output_options_inter = tk.Frame(frame_output_options, bg=couleur_fond)
    frame_output_options_inter.pack(side="left")
    frame_output_options_format = tk.Frame(frame_output_options, bg=couleur_fond)
    frame_output_options_format.pack(side="left", anchor="nw")
    
    tk.Label(frame_input_header, text="En entrée", font="bold", fg=couleur_bouton, bg=couleur_fond).pack()

    tk.Label(frame_input_file, text="Fichier contenant les données d'autorité à aligner", 
             bg=couleur_fond, justify="left").pack(side="left", anchor="w")
    entry_filename = tk.Entry(frame_input_file, width=20, bd=2, bg=couleur_fond)
    entry_filename.pack(side="left")
    entry_filename.focus_set()

    #Fichier avec en-têtes ?
    headers = tk.IntVar()
    tk.Checkbutton(frame_input_aut, text="Mon fichier a des en-têtes de colonne", 
                       variable=headers,
                       bg=couleur_fond, justify="left").pack(anchor="w")
    headers.set(1)

    tk.Label(frame_input_aut,bg=couleur_fond, text="\nType de données en entrée", font="Arial 10 bold", anchor="w").pack(anchor="w")
    input_data_type = tk.IntVar()
    tk.Radiobutton(frame_input_aut,bg=couleur_fond, text="N° Notice AUT, ARK, FRBNF, ISNI, Nom, Prénom, Date de naissance, Date de mort\n(extraction base d'autorités)", variable=input_data_type, value=1, justify="left").pack(anchor="w")
    tk.Radiobutton(frame_input_aut,bg=couleur_fond, text="N° Notice AUT, ARK, FRBNF, ISNI, Nom, Prénom, Titre\n(extraction base notices bib)", variable=input_data_type, value=2, justify="left").pack(anchor="w")

    tk.Label(frame_input_aut,bg=couleur_fond, text="\n").pack()

    tk.Label(frame_output_header, text="En sortie", font="bold", fg=couleur_bouton, bg=couleur_fond).pack()    
    

    file_nb = tk.IntVar()
    tk.Radiobutton(frame_output_file,bg=couleur_fond, text="1 fichier", variable=file_nb , value=1, justify="left").pack(anchor="w")
    tk.Radiobutton(frame_output_file,bg=couleur_fond, text="Plusieurs fichiers \n(Pb / 0 / 1 / plusieurs ARK trouvés)", justify="left", variable=file_nb , value=2).pack(anchor="w")
    file_nb.set(2)


    tk.Label(frame_output_file, text="ID de traitement (facultatif)",
             bg=couleur_fond).pack(anchor="w")
    outputID = tk.Entry(frame_output_file, bg=couleur_fond)
    outputID.pack(anchor="w")

    tk.Label(frame_output_file, text="\n",
             bg=couleur_fond).pack(anchor="w")

    
    #Récupérer les métadonnées BnF au passage ?
    meta_bnf = tk.IntVar()
    tk.Checkbutton(frame_output_file, text="Récupérer les métadonnées BnF ?", 
                       variable=meta_bnf,
                       bg=couleur_fond, justify="left").pack(anchor="w")


    
    #file_format.focus_set()
    b = tk.Button(zone_ok_help_cancel, text = "Aligner\nles autorités", 
                  command = lambda: launch(master, entry_filename.get(), headers.get(), input_data_type.get(), file_nb.get(), outputID.get(), meta_bnf.get()), 
                  width = 15, borderwidth=1, pady=40, fg="white",
                  bg=couleur_bouton, font="Arial 10 bold"
                  )
    b.pack()
    
    main.form_saut_de_ligne(zone_ok_help_cancel, couleur_fond)
    call4help = tk.Button(zone_ok_help_cancel, text="Besoin d'aide ?", command=lambda: main.click2help("https://github.com/Lully/transbiblio"), padx=10, pady=1, width=15)
    call4help.pack()    
    cancel = tk.Button(zone_ok_help_cancel, bg=couleur_fond, text="Annuler", command=lambda: main.annuler(master), padx=10, pady=1, width=15)
    cancel.pack()

    tk.Label(zone_notes, text = "Version " + str(version) + " - " + lastupdate, bg=couleur_fond).pack()

    
    if (last_version[1] == True):
        download_update = tk.Button(zone_notes, text = "Télécharger la version " + str(last_version[0]), command=main.download_last_update)
        download_update.pack()
    
    tk.mainloop()

if __name__ == '__main__':
    access_to_network = main.check_access_to_network()
    last_version = [0,False]
    if(access_to_network is True):
        last_version = main.check_last_compilation(programID)
    formulaire_noticesaut2arkBnF(access_to_network,last_version)
    
    