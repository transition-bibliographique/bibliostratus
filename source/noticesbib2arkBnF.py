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
import tkinter as tk
import urllib.parse
from collections import defaultdict

from unidecode import unidecode

import funcs
import main
from funcs import Bib_record


#import matplotlib.pyplot as plt


url_access_pbs = []

#Permet d'écrire dans une liste accessible au niveau général depuis le formulaire, et d'y accéder ensuite
entry_file_list = []

#Pour chaque notice, on recense la méthode qui a permis de récupérer le ou les ARK
NumNotices2methode = defaultdict(list)
#Si on trouve la notice grâce à un autre ISBN : on l'indique dans un dictionnaire qui
#est ajouté dans le rapport stat
NumNotices_conversionISBN = defaultdict(dict)

#Toutes les 100 notices, on vérifie que les API BnF et Abes répondent correctement.
#Résultats (True/False) enregistrés dans ce dictionnaire
dict_check_apis = defaultdict(dict)

#Quelques listes de signes à nettoyer
listeChiffres = ["0","1","2","3","4","5","6","7","8","9"]
lettres = ["a","b","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
lettres_sauf_x = ["a","b","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","y","z"]
ponctuation = [".",",",";",":","?","!","%","$","£","€","#","\\","\"","&","~","{","(","[","`","\\","_","@",")","]","}","=","+","*","\/","<",">",")","}"]
header_columns_init_monimpr = ["Num Not", "FRBNF", "ARK", "ISBN", "EAN", "Titre", "Auteur", "Date", "Volume-Tome", "Editeur"]
header_columns_init_cddvd = ["Num Not", "FRBNF", "ARK", "EAN", "N° commercial", "Titre", "Auteur", "Date", "Editeur"]
header_columns_init_perimpr = ["Num Not", "FRBNF", "ARK", "ISSN", "Titre", "Auteur", "Date", "Lieu de publication"]


#Noms des fichiers en sortie


def create_reports(id_traitement_code, nb_fichiers_a_produire):
    reports = []
    stats_report_file_name=id_traitement_code + "-" + "rapport_stats_noticesbib2ark.txt"
    stats_report_file = open(stats_report_file_name,"w")
    stats_report_file.write("Nb ARK trouvés\tNb notices concernées\n")

    #report_type_convert_file_name = id_traitement_code + "-" + "NumNotices-TypeConversion.txt"
    #report_type_convert_file = open(report_type_convert_file_name,"w")
    #report_type_convert_file.write("NumNotice\tMéthode pour trouver l'ARK\n")
    if (nb_fichiers_a_produire == 1):
        reports = create_reports_1file(id_traitement_code)
    else:
        reports = create_reports_files(id_traitement_code)
    reports.append(stats_report_file)
    #reports.append(report_type_convert_file)
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


ns = {"srw":"http://www.loc.gov/zing/srw/", "mxc":"info:lc/xmlns/marcxchange-v2", "m":"http://catalogue.bnf.fr/namespaces/InterXMarc","mn":"http://catalogue.bnf.fr/namespaces/motsnotices"}
nsOCLC = {"xisbn": "http://worldcat.org/xid/isbn/"}
nsSudoc = {"rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bibo":"http://purl.org/ontology/bibo/", "dc":"http://purl.org/dc/elements/1.1/", "dcterms":"http://purl.org/dc/terms/", "rdafrbr1":"http://rdvocab.info/RDARelationshipsWEMI/", "marcrel":"http://id.loc.gov/vocabulary/relators/", "foaf":"http://xmlns.com/foaf/0.1/", "gr":"http://purl.org/goodrelations/v1#", "owl":"http://www.w3.org/2002/07/owl#", "isbd":"http://iflastandards.info/ns/isbd/elements/", "skos":"http://www.w3.org/2004/02/skos/core#", "rdafrbr2":"http://RDVocab.info/uri/schema/FRBRentitiesRDA/", "rdaelements":"http://rdvocab.info/Elements/", "rdac":"http://rdaregistry.info/Elements/c/", "rdau":"http://rdaregistry.info/Elements/u/", "rdaw":"http://rdaregistry.info/Elements/w/", "rdae":"http://rdaregistry.info/Elements/e/", "rdam":"http://rdaregistry.info/Elements/m/", "rdai":"http://rdaregistry.info/Elements/i/", "sudoc":"http://www.sudoc.fr/ns/", "bnf-onto":"http://data.bnf.fr/ontology/bnf-onto/"}


#fonction de mise à jour de l'ARK s'il existe un ARK
def ark2ark(input_record):
    url = funcs.url_requete_sru('bib.persistentid all "' + input_record.ark_init + '"')
    (test,page) = funcs.testURLetreeParse(url)
    nv_ark = ""
    if (test == True):
        if (page.find("//srw:recordIdentifier", namespaces=main.ns) is not None):
            nv_ark = page.find("//srw:recordIdentifier", namespaces=main.ns).text
            NumNotices2methode[input_record.NumNot].append("Actualisation ARK")
    return nv_ark

#nettoyage des chaines de caractères (titres, auteurs, isbn) : suppression ponctuation, espaces (pour les titres et ISBN) et diacritiques
# =============================================================================
# def nettoyage(string,remplacerEspaces=True,remplacerTirets=True):
#     string = unidecode(string.lower())
#     for signe in ponctuation:
#         string = string.replace(signe,"")
#     string = string.replace("'"," ")
#     if (remplacerTirets == True):
#         string = string.replace("-"," ")
#     if (remplacerEspaces == True):
#         string = string.replace(" ","")
#     return string
#
# def nettoyageTitrePourControle(titre):
#     titre = nettoyage(titre,True)
#     return titre
#
# def nettoyageTitrePourRecherche(titre):
#     titre = nettoyage(titre,False)
#     titre = titre.split(" ")
#     titre = [mot for mot in titre if len(mot) > 1]
#     titre = " ".join(titre)
#     return titre
#
# def nettoyage_lettresISBN(isbn):
#     isbn = unidecode(isbn.lower())
#     char_cle = "0123456789xX"
#     for signe in ponctuation:
#         isbn = isbn.replace(signe,"")
#     prefix = isbn[0:-1]
#     cle = isbn[-1]
#     for lettre in lettres:
#         prefix = prefix.replace(lettre, "")
#     if (cle in char_cle):
#         cle = cle.upper()
#     else:
#         cle = ""
#     return prefix+cle
#
# def nettoyageIsbnPourControle(isbn):
#     isbn = nettoyage(isbn)
#     if (isbn != ""):
#         isbn = nettoyage_lettresISBN(isbn)
#     if (len(isbn) < 10):
#         isbn = ""
#     elif (isbn[0:3] == "978" or isbn[0:3] == "979"):
#         isbn = isbn[3:12]
#     else:
#         isbn = isbn[0:10]
#     return isbn
#
# def nettoyageIssnPourControle(issn):
#     issn = nettoyage(issn).replace(" ","")
#     if (issn != ""):
#         issn = nettoyage_lettresISBN(issn)
#     if (len(issn) < 8):
#         issn = ""
#     else:
#         issn = issn[0:8]
#     return issn
#
# def nettoyageAuteur(auteur,justeunmot=True):
#     listeMots = [" par "," avec "," by "," Mr. "," M. "," Mme "," Mrs "]
#     for mot in listeMots:
#         auteur = auteur.replace(mot,"")
#     for chiffre in listeChiffres:
#         auteur = auteur.replace(chiffre,"")
#     auteur = nettoyage(auteur.lower(),False)
#     auteur = auteur.split(" ")
#     auteur = sorted(auteur,key=len,reverse=True)
#     auteur = [auteur1 for auteur1 in auteur if len(auteur1) > 1]
#     if (auteur is not None and auteur != []):
#         if (justeunmot==True):
#             auteur = auteur[0]
#         else:
#             auteur = " ".join(auteur)
#     else:
#         auteur = ""
#     return auteur
#
# def nettoyageDate(date):
#     date = unidecode(date.lower())
#     for lettre in lettres:
#         date = date.replace(lettre,"")
#     for signe in ponctuation:
#         date = date.split(signe)
#         date = " ".join(annee for annee in date if annee != "")
#     return date
#
# def nettoyageTome(numeroTome):
#     if (numeroTome):
#         numeroTome = unidecode(numeroTome.lower())
#         for lettre in lettres:
#             numeroTome = numeroTome.replace(lettre,"")
#         for signe in ponctuation:
#             numeroTome = numeroTome.split(signe)
#             numeroTome = "~".join(numero for numero in numeroTome)
#         numeroTome = numeroTome.split("~")
#         numeroTome = [numero for numero in numeroTome if numero != ""]
#         if (numeroTome != []):
#             numeroTome = numeroTome[-1]
#         numeroTome = ltrim(numeroTome)
#     return numeroTome
#
#
# def nettoyagePubPlace(pubPlace) :
#     """Nettoyage du lieu de publication"""
#     pubPlace = unidecode(pubPlace.lower())
#     for chiffre in listeChiffres:
#         pubPlace = pubPlace.replace(chiffre,"")
#     for signe in ponctuation:
#         pubPlace = pubPlace.split(signe)
#         pubPlace = " ".join(mot for mot in pubPlace if mot != "")
#     return pubPlace
# =============================================================================

#Si la recherche NNB avec comporaison Mots du titre n'a rien donné, on recherche sur N° interne BnF + Auteur (en ne gardant que le mot le plus long du champ Auteur)
def relancerNNBAuteur(NumNot,systemid,isbn,titre,auteur,date):
    listeArk = []
    if (auteur != "" and auteur is not None):
        urlSRU = funcs.url_requete_sru('bib.author all "' + auteur + '" and bib.otherid all "' + systemid + '"')
        (test,pageSRU) = funcs.testURLetreeParse(urlSRU)
        if (test == True):
            for record in pageSRU.xpath("//srw:records/srw:record", namespaces=main.ns):
                ark = record.find("srw:recordIdentifier", namespaces=main.ns).text
                NumNotices2methode[NumNot].append("N° sys FRBNF + Auteur")
                listeArk.append(ark)
    listeArk = ",".join([ark for ark in listeArk if ark != ""])
    return listeArk



#Quand on a trouvé l'ancien numéro système dans une notice BnF :
#on compare l'ISBN de la notice de la Bibliothèque avec celui de la BnF pour voir si ça colle
#à défaut, on compare les titres (puis demi-titres)
def comparerBibBnf(NumNot,ark_current,systemid,isbn,titre,auteur,date,origineComparaison):
    ark = ""
    url = funcs.url_requete_sru('bib.persistentid all "' + ark_current + '"')
    (test,recordBNF) = funcs.testURLetreeParse(url)
    if (test == True):
        ark =  comparaisonIsbn(NumNot,ark_current,systemid,isbn,titre,auteur,date,recordBNF)
        if (ark == ""):
            ark = comparaisonTitres(NumNot,ark_current,systemid,isbn,titre,auteur,date,"",recordBNF,origineComparaison)
    return ark

def comparaisonIsbn(NumNot,ark_current,systemid,isbn,titre,auteur,date,recordBNF):
    ark = ""
    isbnBNF = ""
    sourceID = "ISBN"
    #Si le FRBNF de la notice source est présent comme ancien numéro de notice
    #dans la notice BnF, on compare les ISBN en 010, ou à défaut les EAN
    #ou à défaut les ISSN (il peut s'agir d'un périodique)
    isbnBNF = funcs.nettoyage(main.extract_subfield(recordBNF,"010","a",1))
    if (isbnBNF == ""):
        isbnBNF = funcs.nettoyage(main.extract_subfield(recordBNF,"038","a",1))
        sourceID = "EAN"
    if (isbnBNF == ""):
        isbnBNF = funcs.nettoyage(main.extract_subfield(recordBNF,"011","a",1))
        sourceID = "ISSN"
    if (isbn != "" and isbnBNF != ""):
        if (isbn in isbnBNF):
            ark = ark_current
            NumNotices2methode[NumNot].append("N° sys FRBNF + contrôle " + sourceID)
    return ark

def comparaisonTitres(NumNot,ark_current,systemid,isbn,titre,auteur,date,numeroTome,recordBNF,origineComparaison):
    ark = comparaisonTitres_sous_zone(NumNot,ark_current,systemid,isbn,titre,auteur,date,recordBNF,origineComparaison,"200$a")
    if (ark == ""):
        ark = comparaisonTitres_sous_zone(NumNot,ark_current,systemid,isbn,titre,auteur,date,recordBNF,origineComparaison,"200$e")
    if (ark == ""):
        ark = comparaisonTitres_sous_zone(NumNot,ark_current,systemid,isbn,titre,auteur,date,recordBNF,origineComparaison,"200$i")
    if (ark == ""):
        ark = comparaisonTitres_sous_zone(NumNot,ark_current,systemid,isbn,titre,auteur,date,recordBNF,origineComparaison,"750$a")
    if (ark == ""):
        ark = comparaisonTitres_sous_zone(NumNot,ark_current,systemid,isbn,titre,auteur,date,recordBNF,origineComparaison,"753$a")
    if (ark == ""):
        ark = comparaisonTitres_sous_zone(NumNot,ark_current,systemid,isbn,titre,auteur,date,recordBNF,origineComparaison,"500$a")
    if (ark == ""):
        ark = comparaisonTitres_sous_zone(NumNot,ark_current,systemid,isbn,titre,auteur,date,recordBNF,origineComparaison,"500$e")
    #if (ark == ""):
    #    ark = comparaisonTitres_sous_zone(NumNot,ark_current,systemid,isbn,titre,auteur,date,recordBNF,origineComparaison,"503$a")
    if (ark == ""):
        ark = comparaisonTitres_sous_zone(NumNot,ark_current,systemid,isbn,titre,auteur,date,recordBNF,origineComparaison,"503$e")
    if (ark == ""):
        ark = comparaisonTitres_sous_zone(NumNot,ark_current,systemid,isbn,titre,auteur,date,recordBNF,origineComparaison,"540$a")
    if (ark == ""):
        ark = comparaisonTitres_sous_zone(NumNot,ark_current,systemid,isbn,titre,auteur,date,recordBNF,origineComparaison,"540$e")
    if (ark == ""):
        ark = comparaisonTitres_sous_zone(NumNot,ark_current,systemid,isbn,titre,auteur,date,recordBNF,origineComparaison,"410$a")
    if (ark == ""):
        ark = comparaisonTitres_sous_zone(NumNot,ark_current,systemid,isbn,titre,auteur,date,recordBNF,origineComparaison,"225$a")
    if (ark == ""):
        ark = comparaisonTitres_sous_zone(NumNot,ark_current,systemid,isbn,titre,auteur,date,recordBNF,origineComparaison,"461$t")
    if (ark != "" and numeroTome != ""):
        ark = verificationTomaison(ark,numeroTome,recordBNF)
    if (ark != "" and date != ""):
        if ("ISBN" in origineComparaison or "EAN" in origineComparaison or "commercial" in origineComparaison):
            ark = checkDate(ark,date,recordBNF)
    return ark


def verificationTomaison(ark,numeroTome,recordBNF):
    """Une fois qu'on a trouvé un ARK (via une recherche Titre-Auteur-Date,
    s'il y a un numéro de volume dans les données en entrée on va vérifier
    si on le retrouve bien dans une des zones où il pourrait se trouver :
    D'abord 200$h, 461$v
    Si ces deux zones sont vides, on va regarder les nombres dans la zone 200$a
    La comparaison se fait en normalisant les données de part en d'autres, pour n'avoir
    que des chiffres arabes sans 0 initial
    Conséquence : s'il y a un numéro de volume en entrée, le programme peut aller jusqu'à convertir
    tout ce qui ressemble à un chiffre romain dans la zone de titre"""
    liste_subfields_volume = ["200$h","200$u","461$v"]
    volumesBNF = ""
    for subf in liste_subfields_volume:
        volumesBNF += "~" + main.extract_subfield(recordBNF,subf.split("$")[0],subf.split("$")[1])
    volumesBNF = funcs.convert_volumes_to_int(volumesBNF)
    if (volumesBNF == ""):
        volumesBNF = main.extract_subfield(recordBNF,"200","a")
        volumesBNF = funcs.convert_volumes_to_int(volumesBNF)
        for lettre in lettres:
            volumesBNF = volumesBNF.replace(lettre, "~")
        volumesBNF = volumesBNF.split("~")
        volumesBNF = set(str(funcs.ltrim(nb)) for nb in volumesBNF if nb != "")
    if (volumesBNF != "" and numeroTome in volumesBNF):
        return ark
    else:
        return ""

def verificationTomaison_sous_zone(ark,numeroTome,numeroTomeBnF):
    """Vérifie si le numéro du tome en entrée est présent dans l'extraction des nombres de la sous-zone"""
    return ark,False

# =============================================================================
# def ltrim(nombre_texte):
#     "Supprime les 0 initiaux d'un nombre géré sous forme de chaîne de caractères"
#     while(len(nombre_texte) > 1 and nombre_texte[0] == "0"):
#         nombre_texte = nombre_texte[1:]
#     return nombre_texte
# =============================================================================

def checkDate(ark,date_init,recordBNF):
    ark_checked = ""
    dateBNF = []
    dateBNF_100 = unidecode(main.extract_subfield(recordBNF,"100","a",1,sep="~").lower())[9:13]
    if (len(dateBNF_100)>4):
        dateBNF_100 = dateBNF_100[0:4]
    if (main.RepresentsInt(dateBNF_100) is True):
        dateBNF_100  = int(dateBNF_100)
        dateBNF.extend([dateBNF_100 + 1, dateBNF_100-1])
    dateBNF.append(dateBNF_100)
    dateBNF_210d = unidecode(main.extract_subfield(recordBNF,"210","d",1,sep="~").lower())
    dateBNF_306a = unidecode(main.extract_subfield(recordBNF,"306","a",1,sep="~").lower())
    for lettre in lettres:
        dateBNF_210d = dateBNF_210d.replace(lettre,"~")
        dateBNF_306a = dateBNF_306a.replace(lettre,"~")
    for signe in ponctuation:
        dateBNF_210d = dateBNF_210d.replace(signe,"~")
        dateBNF_306a = dateBNF_306a.replace(signe,"~")
    dateBNF_210d = [el for el in dateBNF_210d.split("~") if el != ""]
    dateBNF_306a = [el for el in dateBNF_306a.split("~") if el != ""]
    for date in dateBNF_210d:
        if (main.RepresentsInt(date) is True):
            date = int(date)
            dateBNF.extend([date + 1, date-1])
    for date in dateBNF_306a:
        if (main.RepresentsInt(date) is True):
            date = int(date)
            dateBNF.extend([date + 1, date-1])
    dateBNF.extend(dateBNF_210d)
    dateBNF.extend(dateBNF_306a)
    dateBNF = " ".join([str(date) for date in dateBNF])
    if (len(str(date_init))>3 and str(date_init)[0:4] in dateBNF):
        ark_checked = ark
    return ark_checked


def comparaisonTitres_sous_zone(NumNot,ark_current,systemid,isbn,titre,auteur,date,recordBNF,origineComparaison,sous_zone):
    ark = ""
    field = sous_zone.split("$")[0]
    subfield = sous_zone.split("$")[1]
    titreBNF = funcs.nettoyageTitrePourControle(main.extract_subfield(recordBNF,field,subfield,1))
    if (titre != "" and titreBNF != ""):
        if (titre == titreBNF):
            ark = ark_current
            NumNotices2methode[NumNot].append(origineComparaison + " + contrôle Titre " + sous_zone)
            if (len(titre) < 5):
                NumNotices2methode[NumNot].append("[titre court]")
        elif(titre[0:round(len(titre)/2)] == titreBNF[0:round(len(titre)/2)]):
            ark = ark_current
            NumNotices2methode[NumNot].append(origineComparaison + " + contrôle Titre " + sous_zone)
            if (round(len(titre)/2)<10):
                NumNotices2methode[NumNot].append("[demi-titre" + "-" + str(round(len(titre)/2)) + "caractères]")
        elif(titreBNF in titre):
            NumNotices2methode[NumNot].append(origineComparaison + " + contrôle Titre BNF contenu dans titre initial")
            ark = ark_current
        elif (titre in titreBNF):
            NumNotices2methode[NumNot].append(origineComparaison + " + contrôle Titre initial contenu dans titre BNF")
            ark = ark_current
    elif (titre == ""):
        ark = ark_current
        NumNotices2methode[NumNot].append(origineComparaison + " + pas de titre initial pour comparer")
    return ark

#Recherche par n° système. Si le 3e paramètre est "False", c'est qu'on a pris uniquement le FRBNF initial, sans le tronquer.
#Dans ce cas, et si 0 résultat pertinent, on relance la recherche avec info tronqué
def systemid2ark(NumNot,systemid,tronque,isbn,titre,auteur,date):
    url = funcs.url_requete_sru('bib.otherid all "' + systemid + '"')
    #url = "http://catalogueservice.bnf.fr/SRU?version=1.2&operation=searchRetrieve&query=NumNotice%20any%20%22" + systemid + "%22&recordSchema=InterXMarc_Complet&maximumRecords=1000&startRecord=1"
    listeARK = []
    (test,page) = funcs.testURLetreeParse(url)
    if (test == True):
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
                                listeARK.append(comparerBibBnf(NumNot,ark_current,systemid,isbn,titre,auteur,date, "Ancien n° notice"))
    listeARK = ",".join([ark1 for ark1 in listeARK if ark1 != ''])

#Si pas de réponse, on fait la recherche SystemID + Auteur
    if (listeARK == ""):
        listeARK = relancerNNBAuteur(NumNot,systemid,isbn,titre,auteur,date)
    listeARK = ",".join([ark1 for ark1 in listeARK.split(",") if ark1 != ''])

#Si à l'issue d'une première requête sur le numéro système dont on a conservé la clé ne donne rien -> on recherche sur le numéro tronqué comme numéro système
    if (listeARK == "" and tronque == False):
        systemid_tronque = systemid[0:len(systemid)-1]
        systemid2ark(NumNot,systemid_tronque, True,isbn,titre,auteur,date)
    listeARK = ",".join([ark1 for ark1 in listeARK.split(",") if ark1 != ''])

    return listeARK

def rechercheNNB(input_record,nnb):
    ark = ""
    if (nnb.isdigit() is False):
        #pb_frbnf_source.write("\t".join[NumNot,nnb] + "\n")
        ark = "Pb FRBNF"
    elif (30000000 < int(nnb) < 50000000):
        url = funcs.url_requete_sru('bib.recordid any "' + nnb + '"')
        (test,page) = funcs.testURLetreeParse(url)
        if (test == True):
            for record in page.xpath("//srw:records/srw:record", namespaces=main.ns):
                ark_current = record.find("srw:recordIdentifier",namespaces=main.ns).text
                identifiant = ""
                if (input_record.type == "TEX"):
                    input_record.isbn.propre
                if (input_record.type == "VID" or input_record.type == "AUD"):
                    identifiant = input_record.ean.propre
                ark = comparerBibBnf(input_record.NumNot,ark_current,nnb,identifiant,input_record.titre_nett,input_record.auteur_nett,input_record.date_nett,"Numéro de notice")
    return ark

#Si le FRBNF n'a pas été trouvé, on le recherche comme numéro système -> pour ça on extrait le n° système
def oldfrbnf2ark(input_record):
    """Extrait du FRBNF le numéro système, d'abord sur 9 chiffres, puis sur 8 si besoin, avec un contrôle des résultats sur le contenu du titre ou sur l'auteur"""
    systemid = ""
    if (input_record.frbnf[0:5].upper() == "FRBNF"):
        systemid = input_record.frbnf[5:14]
    else:
        systemid = input_record.frbnf[4:13]

    ark = rechercheNNB(input_record,systemid[0:8])
    if (ark==""):
        ark = systemid2ark(input_record.NumNot,systemid,False,input_record.isbn.nett,input_record.titre_nett,input_record.auteur_nett,input_record.date_nett)
    return ark


def frbnf2ark(input_record):
    """Rechercher le FRBNF avec le préfixe "FRBN" ou "FRBNF". A défaut, lance d'autres fonctions pour lancer la recherche en utilisant uniquement le numéro, soit comme NNB/NNA, soit comme ancien numéro système (en zone 9XX)"""
    ark = ""
    if (input_record.frbnf[0:4].lower() == "frbn"):
        url = funcs.url_requete_sru('bib.otherid all "' + input_record.frbnf + '"')
        (test,page) = funcs.testURLetreeParse(url)
        if (test == True):
            nb_resultats = int(page.find("//srw:numberOfRecords", namespaces=main.ns).text)

            if (nb_resultats == 0):
                ark = oldfrbnf2ark(input_record)
            elif (nb_resultats == 1):
                ark = page.find("//srw:recordIdentifier", namespaces=main.ns).text
                if (ark !=""):
                    NumNotices2methode[input_record.NumNot].append("FRBNF > ARK")
            else:
                ark = ",".join([ark.text for ark in page.xpath("//srw:recordIdentifier", namespaces=main.ns)])
                if (ark != ""):
                    NumNotices2methode[input_record.NumNot].append("FRBNF > ARK")
    return ark


def row2file(liste_metadonnees,liste_reports):
    liste_metadonnees_to_report = [str(el) for el in liste_metadonnees]
    liste_reports[0].write("\t".join(liste_metadonnees_to_report ) + "\n")

def row2files(liste_metadonnees,liste_reports):
     #["NumNot","nbARK","ark trouvé","Méthode","ark initial","FRBNF","ISBN","EAN","Titre","auteur","date","Tome/Volume", "editeur"]
    liste_metadonnees_to_report = [str(el) for el in liste_metadonnees]
    nbARK = liste_metadonnees[1]
    ark = liste_metadonnees[2]
    if (ark == "Pb FRBNF"):
        liste_reports[0].write("\t".join(liste_metadonnees_to_report) + "\n")
    elif (nbARK == 0):
        liste_reports[1].write("\t".join(liste_metadonnees_to_report) + "\n")
    elif (nbARK == 1):
        liste_reports[2].write("\t".join(liste_metadonnees_to_report) + "\n")
    else:
        liste_reports[3].write("\t".join(liste_metadonnees_to_report) + "\n")

# =============================================================================
# def nettoyage_isbn(isbn):
#     isbn_nett = isbn.split(";")[0].split(",")[0].split("(")[0].split("[")[0]
#     isbn_nett = isbn_nett.replace("-","").replace(" ","")
#     isbn_nett = unidecode(isbn_nett)
#     for signe in ponctuation:
#         isbn_nett = isbn_nett.replace(signe,"")
#     isbn_nett = isbn_nett.lower()
#     for lettre in lettres_sauf_x:
#         isbn_nett = isbn_nett.replace(lettre,"")
#     return isbn_nett
#
# def conversionIsbn(isbn):
#     longueur = len(isbn)
#     isbnConverti = ""
#     if (longueur == 10):
#         isbnConverti = conversionIsbn1013(isbn)
#     elif (longueur == 13):
#         isbnConverti = conversionIsbn1310(isbn)
#     return isbnConverti
#
# #conversion isbn13 en isbn10
# def conversionIsbn1310(isbn):
#     if (isbn[0:3] == "978"):
#         prefix = isbn[3:-1]
#         check = check_digit_10(prefix)
#         return prefix + check
#     else:
#         return ""
#
# #conversion isbn10 en isbn13
# def conversionIsbn1013(isbn):
#     prefix = '978' + isbn[:-1]
#     check = check_digit_13(prefix)
#     return prefix + check
#
# def check_digit_10(isbn):
#     assert len(isbn) == 9
#     sum = 0
#     for i in range(len(isbn)):
#         c = int(isbn[i])
#         w = i + 1
#         sum += w * c
#     r = sum % 11
#     if (r == 10):
#         return 'X'
#     else:
#         return str(r)
#
# def check_digit_13(isbn):
#     assert len(isbn) == 12
#     sum = 0
#     for i in range(len(isbn)):
#         c = int(isbn[i])
#         if (i % 2):
#             w = 3
#         else:
#             w = 1
#         sum += w * c
#     r = 10 - (sum % 10)
#     if (r == 10):
#         return '0'
#     else:
#         return str(r)
# #==============================================================================
# # Fonctions pour convertir les chiffres romains en chiffres arabes (et l'inverse)
# # Utilisé pour comparer les volumaisons
# #==============================================================================
# numeral_map = tuple(zip(
#     (1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1),
#     ('M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I')
# ))
#
# def int_to_roman(i):
#     result = []
#     for integer, numeral in numeral_map:
#         count = i // integer
#         result.append(numeral * count)
#         i -= integer * count
#     return ''.join(result)
#
# def roman_to_int(n):
#     i = result = 0
#     for integer, numeral in numeral_map:
#         while n[i:i + len(numeral)] == numeral:
#             result += integer
#             i += len(numeral)
#     return result
#
# def convert_volumes_to_int(n):
#     for char in ponctuation:
#         n = n.replace(char,"-")
#     n = n.replace(" ","-")
#     liste_n = [e for e in n.split("-") if e != ""]
#     liste_n_convert = []
#     for n in liste_n:
#         try:
#             int(n)
#             liste_n_convert.append(n)
#         except ValueError:
#             c = roman_to_int(n)
#             if (c != 0):
#                 liste_n_convert.append(c)
#     liste_n_convert = set(ltrim(str(nb)) for nb in liste_n_convert if nb != "")
#     n_convert = " ".join([str(el) for el in list(liste_n_convert)])
#     return n_convert
#
# =============================================================================

def isbn2sru(NumNot,isbn,titre,auteur,date):
    urlSRU = funcs.url_requete_sru('bib.isbn all "' + isbn + '"')
    listeARK = []
    (test,resultats) = funcs.testURLetreeParse(urlSRU)
    if (test == True):
        for record in resultats.xpath("//srw:records/srw:record", namespaces=main.ns):
            ark_current = record.find("srw:recordIdentifier", namespaces=main.ns).text
            recordBNF_url = funcs.url_requete_sru('bib.persistentid all "' + ark_current + '"')
            (test,recordBNF) = funcs.testURLetreeParse(recordBNF_url)
            if (test == True):
                ark = comparaisonTitres(NumNot,ark_current,"",isbn,titre,auteur,date,"",recordBNF,"ISBN")
                #NumNotices2methode[NumNot].append("ISBN > ARK")
                listeARK.append(ark)
    listeARK = ",".join([ark for ark in listeARK if ark != ""])
    if (listeARK == "" and auteur != ""):
        listeARK = isbnauteur2sru(NumNot,isbn,titre,auteur,date)
    return listeARK

def isbnauteur2sru(NumNot,isbn,titre,auteur,date):
    """Si la recherche ISBN avec contrôle titre n'a rien donné, on recherche ISBN + le mot le plus long dans la zone "auteur", et pas de contrôle sur Titre ensuite"""
    motlongauteur = funcs.nettoyageAuteur(auteur, True)
    urlSRU = funcs.url_requete_sru('bib.isbn all "' + isbn + '" and bib.author all "' + motlongauteur + '"')
    listeARK = []
    (test,resultats) = funcs.testURLetreeParse(urlSRU)
    if (test == True):
        if (resultats.find("//srw:records/srw:record", namespaces=main.ns) is not None):
            NumNotices2methode[NumNot].append("ISBN + Auteur > ARK")
        for recordBNF in resultats.xpath("//srw:records/srw:record", namespaces=main.ns):
            ark_current = recordBNF.find("srw:recordIdentifier", namespaces=main.ns).text
            ark_current = checkDate(ark_current,date,recordBNF)
            listeARK.append(ark_current)
    listeARK = ",".join([ark for ark in listeARK if ark != ""])
    return listeARK

def eanauteur2sru(NumNot,ean,titre,auteur,date):
    """Si la recherche EAN avec contrôle titre n'a rien donné, on recherche EAN + le mot le plus long dans la zone "auteur", et pas de contrôle sur Titre ensuite"""
    motlongauteur = funcs.nettoyageAuteur(auteur, True)
    urlSRU = funcs.url_requete_sru('bib.ean all "' + ean + '" + bib.author all "' + motlongauteur + '"')
    listeARK = []
    (test,resultats) = funcs.testURLetreeParse(urlSRU)
    if (test == True):
        if (resultats.find("//srw:records/srw:record", namespaces=main.ns) is not None):
            NumNotices2methode[NumNot].append("EAN + Auteur > ARK")
        for record in resultats.xpath("//srw:records/srw:record", namespaces=main.ns):
            ark_current = record.find("srw:recordIdentifier", namespaces=main.ns).text
            listeARK.append(ark_current)
    listeARK = ",".join([ark for ark in listeARK if ark != ""])
    return listeARK

#def testURLetreeParse(url):
#    test = True
#    resultat = ""
#    try:
#        resultat = etree.parse(request.urlopen(url))
#    except etree.XMLSyntaxError as err:
#        print(url)
#        print(err)
#        url_access_pbs.append([url,"etree.XMLSyntaxError"])
#        test = False
#    except etree.ParseError as err:
#        print(url)
#        print(err)
#        test = False
#        url_access_pbs.append([url,"etree.ParseError"])
#    except error.URLError as err:
#        print(url)
#        print(err)
#        test = False
#        url_access_pbs.append([url,"urllib.error.URLError"])
#    except ConnectionResetError as err:
#        print(url)
#        print(err)
#        test = False
#        url_access_pbs.append([url,"ConnectionResetError"])
#    except TimeoutError as err:
#        print(url)
#        print(err)
#        test = False
#        url_access_pbs.append([url,"TimeoutError"])
#    except http.client.RemoteDisconnected as err:
#        print(url)
#        print(err)
#        test = False
#        url_access_pbs.append([url,"http.client.RemoteDisconnected"])
#    except http.client.BadStatusLine as err:
#        print(url)
#        print(err)
#        test = False
#        url_access_pbs.append([url,"http.client.BadStatusLine"])
#    except ConnectionAbortedError as err:
#        print(url)
#        print(err)
#        test = False
#        url_access_pbs.append([url,"ConnectionAbortedError"])
#    return (test,resultat)
#
#
#def testURLurlopen(url):
#    test = True
#    resultat = ""
#    try:
#        resultat = request.urlopen(url)
#    except etree.XMLSyntaxError as err:
#        print(url)
#        print(err)
#        url_access_pbs.append([url,"etree.XMLSyntaxError"])
#        test = False
#    except etree.ParseError as err:
#        print(url)
#        print(err)
#        test = False
#        url_access_pbs.append([url,"etree.ParseError"])
#    except error.URLError as err:
#        print(url)
#        print(err)
#        test = False
#        url_access_pbs.append([url,"urllib.error.URLError"])
#    except ConnectionResetError as err:
#        print(url)
#        print(err)
#        test = False
#        url_access_pbs.append([url,"ConnectionResetError"])
#    except TimeoutError as err:
#        print(url)
#        print(err)
#        test = False
#        url_access_pbs.append([url,"TimeoutError"])
#    except http.client.RemoteDisconnected as err:
#        print(url)
#        print(err)
#        test = False
#        url_access_pbs.append([url,"http.client.RemoteDisconnected"])
#    except http.client.BadStatusLine as err:
#        print(url)
#        print(err)
#        test = False
#        url_access_pbs.append([url,"http.client.BadStatusLine"])
#    except ConnectionAbortedError as err:
#        print(url)
#        print(err)
#        test = False
#        url_access_pbs.append([url,"ConnectionAbortedError"])
#    return (test,resultat)


#Si l'ISBN n'a été trouvé ni dans l'index ISBN, ni dans l'index EAN
#on le recherche dans tous les champs (not. les données d'exemplaires, pour des
#réimpressions achetées par un département de la Direction des collections de la BnF)
def isbn_anywhere2sru(NumNot,isbn,titre,auteur,date):
    urlSRU = funcs.url_requete_sru('bib.anywhere all "' + isbn + '"')
    test,resultat = funcs.testURLetreeParse(urlSRU)
    listeARK = []
    if (test == True):
        for record in resultat.xpath("//srw:records/srw:record", namespaces=main.ns):
            ark_current = record.find("srw:recordIdentifier", namespaces=main.ns).text
            recordBNF_url = funcs.url_requete_sru('bib.persistentid all "' + ark_current)
            (test2,recordBNF) = funcs.testURLetreeParse(recordBNF_url)
            if (test2 == True):
                ark = comparaisonTitres(NumNot,ark_current,"",isbn,titre,auteur,date,"",recordBNF,"ISBN dans toute la notice")
                #NumNotices2methode[NumNot].append("ISBN anywhere > ARK")
                listeARK.append(ark)
    listeARK = ",".join([ark for ark in listeARK if ark != ""])
    return listeARK


#def testURLretrieve(url):
#    test = True
#    try:
#        request.urlretrieve(url)
#    except error.HTTPError as err:
#        test = False
#    except error.URLError as err:
#        test = False
#    except http.client.RemoteDisconnected as err:
#        test = False
#    except ConnectionAbortedError as err:
#        test = False
#    return test
#

def isbn2sudoc(input_record):
    """A partir d'un ISBN, recherche dans le Sudoc. Pour chaque notice trouvée, on regarde sur la notice
    Sudoc a un ARK BnF ou un FRBNF, auquel cas on convertit le PPN en ARK. Sinon, on garde le(s) PPN"""
    url = "https://www.sudoc.fr/services/isbn2ppn/" + input_record.isbn.propre
    Listeppn = []
    isbnTrouve = funcs.testURLretrieve(url)
    ark = []
    if (isbnTrouve == True):
        (test,resultats) = funcs.testURLetreeParse(url)
        if (test == True):
            if (resultats.find("//ppn") is not None):
                NumNotices2methode[input_record.NumNot].append("ISBN > PPN")
            for ppn in resultats.xpath("//ppn"):
                ppn_val = ppn.text
                Listeppn.append("PPN" + ppn_val)
                ark.append(ppn2ark(input_record.NumNot,ppn_val,input_record.isbn.propre,input_record.titre_nett,input_record.auteur_nett,input_record.date_nett))
            if (ark == []):
                url = "https://www.sudoc.fr/services/isbn2ppn/" + input_record.isbn.converti
                isbnTrouve = funcs.testURLretrieve(url)
                if (isbnTrouve == True):
                    (test,resultats) = funcs.testURLetreeParse(url)
                    if (test == True):
                        for ppn in resultats.xpath("//ppn"):
                            ppn_val = ppn.text
                            Listeppn.append("PPN" + ppn_val)
                            ark = ppn2ark(input_record.NumNot,ppn_val,input_record.isbn.converti,input_record.titre_nett,input_record.auteur_nett,input_record.date_nett)
                            if (Listeppn != []):
                                add_to_conversionIsbn(input_record.NumNot,input_record.isbn.propre,input_record.isbn.converti,True)
    #Si on trouve un PPN, on ouvre la notice pour voir s'il n'y a pas un ARK déclaré comme équivalent --> dans ce cas on récupère l'ARK
    Listeppn = ",".join([ppn for ppn in Listeppn if ppn != ""])
    ark = ",".join([ark1 for ark1 in ark if ark1 != ""])
    if (ark != ""):
        return ark
    else:
        return Listeppn

def ean2sudoc(NumNot,ean_propre,titre_nett,auteur_nett,date_nett):
    """A partir d'un EAN, recherche dans le Sudoc. Pour chaque notice trouvée, on regarde sur la notice
    Sudoc a un ARK BnF ou un FRBNF, auquel cas on convertit le PPN en ARK. Sinon, on garde le(s) PPN"""
    url = "https://www.sudoc.fr/services/ean2ppn/" + ean_propre
    Listeppn = []
    eanTrouve = funcs.testURLretrieve(url)
    ark = []
    if (eanTrouve == True):
        (test,resultats) = funcs.testURLetreeParse(url)
        if (test == True):
            for ppn in resultats.xpath("//ppn"):
                ppn_val = ppn.text
                Listeppn.append("PPN" + ppn_val)
                NumNotices2methode[NumNot].append("EAN > PPN")
                ark.append(ppn2ark(NumNot,ppn_val,ean_propre,titre_nett,auteur_nett,date_nett))
    #Si on trouve un PPN, on ouvre la notice pour voir s'il n'y a pas un ARK déclaré comme équivalent --> dans ce cas on récupère l'ARK
    Listeppn = ",".join([ppn for ppn in Listeppn if ppn != ""])
    ark = ",".join([ark1 for ark1 in ark if ark1 != ""])
    if (ark != ""):
        return ark
    else:
        return Listeppn


def ppn2ark(NumNot,ppn,isbn,titre,auteur,date):
    ark = ""
    url = "http://www.sudoc.fr/" + ppn + ".rdf"
    (test,record) = funcs.testURLetreeParse(url)
    if (test == True):
        for sameAs in record.xpath("//owl:sameAs",namespaces=main.nsSudoc):
            resource = sameAs.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource")
            if (resource.find("ark:/12148/")>0):
                ark = resource[24:46]
                NumNotices2methode[NumNot].append("PPN > ARK")
        if (ark == ""):
            for frbnf in record.xpath("//bnf-onto:FRBNF",namespaces=main.nsSudoc):
                frbnf_val = frbnf.text
                NumNotices2methode[NumNot].append("PPN > FRBNF")
                temp_record = Bib_record([NumNot,frbnf_val,"",isbn,"",titre,auteur,date,"",""],1)
                ark = frbnf2ark(temp_record)
    return ark

def add_to_conversionIsbn(NumNot,isbn_init,isbn_trouve,via_Sudoc=False):
    NumNotices_conversionISBN[NumNot]["isbn initial"] = isbn_init
    NumNotices_conversionISBN[NumNot]["isbn trouvé"] = isbn_trouve
    NumNotices_conversionISBN[NumNot]["via Sudoc"] = str(via_Sudoc)


def isbn2ark(NumNot,isbn_init,isbn_propre,isbn_converti,titre_nett,auteur_nett,date_nett):
    #Recherche sur l'ISBN tel que saisi dans la source
    resultatsIsbn2ARK = isbn2sru(NumNot,isbn_init,titre_nett,auteur_nett,date_nett)

    #Requête sur l'ISBN dans le SRU, avec contrôle sur Titre ou auteur
    if (resultatsIsbn2ARK == "" and isbn_init != isbn_propre):
        resultatsIsbn2ARK = isbn2sru(NumNot,isbn_propre,titre_nett,auteur_nett,date_nett)

    #isbnConverti = conversionIsbn(input_record.isbn.propre)
#Si pas de résultats : on convertit l'ISBN en 10 ou 13 et on relance une recherche dans le catalogue BnF
    if (resultatsIsbn2ARK == ""):
        resultatsIsbn2ARK = isbn2sru(NumNot,isbn_converti,titre_nett,auteur_nett,date_nett)
        if (resultatsIsbn2ARK != ""):
            add_to_conversionIsbn(NumNot,isbn_init,isbn_converti,False)
#Si pas de résultats et ISBN 13 : on recherche sur EAN
    if (resultatsIsbn2ARK == "" and len(isbn_propre)==13):
        resultatsIsbn2ARK = ean2ark(NumNot,isbn_propre,titre_nett,auteur_nett,date_nett)
    if (resultatsIsbn2ARK == "" and len(isbn_converti) == 13):
        resultatsIsbn2ARK = ean2ark(NumNot,isbn_converti,titre_nett,auteur_nett,date_nett)
        if (resultatsIsbn2ARK != ""):
            add_to_conversionIsbn(NumNot,isbn_init,isbn_converti,False)

#Si pas de résultats et ISBN 13 : on recherche l'ISBN dans tous les champs (dont les données d'exemplaire)
    if (resultatsIsbn2ARK == ""):
        resultatsIsbn2ARK = isbn_anywhere2sru(NumNot,isbn_propre,titre_nett,auteur_nett,date_nett)
    if (resultatsIsbn2ARK == "" and len(isbn_converti) == 13):
        resultatsIsbn2ARK = isbn_anywhere2sru(NumNot,isbn_converti,titre_nett,auteur_nett,date_nett)
        if (resultatsIsbn2ARK != ""):
            add_to_conversionIsbn(NumNot,isbn_init,isbn_converti,False)

    return resultatsIsbn2ARK

def issn2ark(NumNot,issn_init,issn,titre,auteur,date):
    listeArk  = issn2sru(NumNot,issn_init)
    if (listeArk == ""):
        listeArk = issn2sru(NumNot,issn)
    return listeArk

def issn2sru(NumNot,issn):
    url = funcs.url_requete_sru('bib.issn adj "' + issn + '"')
    listeArk = []
    (test,pageSRU) = funcs.testURLetreeParse(url)
    if (test == True):
        for record in pageSRU.xpath("//srw:records/srw:record", namespaces=main.ns):
            ark = record.find("srw:recordIdentifier", namespaces=main.ns).text
            typeNotice = record.find("srw:recordData/mxc:record/mxc:leader",namespaces=main.ns).text[7]
            if (typeNotice == "s"):
                NumNotices2methode[NumNot].append("ISSN")
                listeArk.append(ark)
    listeArk = ",".join([ark for ark in listeArk if ark != ""])
    return listeArk

def issn2sudoc(NumNot,issn_init,issn_nett, titre, auteur, date):
    """A partir d'un ISSN, recherche dans le Sudoc. Pour chaque notice trouvée, on regarde sur la notice
    Sudoc a un ARK BnF ou un FRBNF, auquel cas on convertit le PPN en ARK. Sinon, on garde le(s) PPN"""
    url = "https://www.sudoc.fr/services/issn2ppn/" + issn_nett
    Listeppn = []
    issnTrouve = funcs.testURLretrieve(url)
    ark = []
    if (issnTrouve == True):
        (test,resultats) = funcs.testURLetreeParse(url)
        if (test == True):
            if (resultats.find("//ppn") is not None):
                NumNotices2methode[NumNot].append("ISSN > PPN")
            for ppn in resultats.xpath("//ppn"):
                ppn_val = ppn.text
                Listeppn.append("PPN" + ppn_val)
                ark.append(ppn2ark(NumNot,ppn_val,issn_nett,titre,auteur,date))
    #Si on trouve un PPN, on ouvre la notice pour voir s'il n'y a pas un ARK déclaré comme équivalent --> dans ce cas on récupère l'ARK
    Listeppn = ",".join([ppn for ppn in Listeppn if ppn != ""])
    ark = ",".join([ark1 for ark1 in ark if ark1 != ""])
    if (ark != ""):
        return ark
    else:
        return Listeppn



def ark2metas(ark, unidec=True):
    recordBNF_url = funcs.url_requete_sru('bib.persistentid any "' + ark + '"')
    (test,record) = funcs.testURLetreeParse(recordBNF_url)
    titre = ""
    premierauteurPrenom = ""
    premierauteurNom = ""
    tousauteurs = ""
    date = ""
    if (test == True):
        if (record.find("//mxc:datafield[@tag='200']/mxc:subfield[@code='a']", namespaces=main.ns) is not None):
            titre = record.find("//mxc:datafield[@tag='200']/mxc:subfield[@code='a']", namespaces=main.ns).text
        if (record.find("//mxc:datafield[@tag='200']/mxc:subfield[@code='e']", namespaces=main.ns) is not None):
            titre = titre + ", " + record.find("//mxc:datafield[@tag='200']/mxc:subfield[@code='e']", namespaces=main.ns).text
        if (record.find("//mxc:datafield[@tag='700']/mxc:subfield[@code='a']", namespaces=main.ns) is not None):
            premierauteurNom = record.find("//mxc:datafield[@tag='700']/mxc:subfield[@code='a']", namespaces=main.ns).text
        if (record.find("//mxc:datafield[@tag='700']/mxc:subfield[@code='b']", namespaces=main.ns) is not None):
            premierauteurPrenom = record.find("//mxc:datafield[@tag='700']/mxc:subfield[@code='b']", namespaces=main.ns).text
        if (premierauteurNom  == ""):
            if (record.find("//mxc:datafield[@tag='710']/mxc:subfield[@code='a']", namespaces=main.ns) is not None):
                premierauteurNom = record.find("//mxc:datafield[@tag='710']/mxc:subfield[@code='a']", namespaces=main.ns).text
        if (record.find("//mxc:datafield[@tag='200']/mxc:subfield[@code='f']", namespaces=main.ns) is not None):
            tousauteurs = record.find("//mxc:datafield[@tag='200']/mxc:subfield[@code='f']", namespaces=main.ns).text
        if (record.find("//mxc:datafield[@tag='210']/mxc:subfield[@code='d']", namespaces=main.ns) is not None):
            date = record.find("//mxc:datafield[@tag='210']/mxc:subfield[@code='d']", namespaces=main.ns).text
    metas = [titre,premierauteurPrenom,premierauteurNom,tousauteurs,date]
    if (unidec == True):
        metas = [unidecode(meta) for meta in metas]
    return metas



def ppn2metas(ppn):
    url = "https://www.sudoc.fr/" + ppn + ".rdf"
    (test,record) = funcs.testURLetreeParse(url)
    titre = ""
    premierauteurPrenom = ""
    premierauteurNom = ""
    tousauteurs = ""
    if (test == True):
        if (record.find("//dc:title",namespaces=main.nsSudoc) is not None):
            titre = unidecode(record.find("//dc:title",namespaces=main.nsSudoc).text).split("[")[0].split("/")[0]
            tousauteurs = unidecode(record.find("//dc:title",namespaces=main.nsSudoc).text).split("/")[1]
            if (titre[0:5] == tousauteurs[0:5]):
                tousauteurs = ""
        if (record.find("//marcrel:aut/foaf:Person/foaf:name",namespaces=main.nsSudoc) is not None):
            premierauteurNom = unidecode(record.find("//marcrel:aut/foaf:Person/foaf:name",namespaces=main.nsSudoc).text).split(",")[0]
            if (record.find("//marcrel:aut/foaf:Person/foaf:name",namespaces=main.nsSudoc).text.find(",") > 0):
                premierauteurPrenom = unidecode(record.find("//marcrel:aut/foaf:Person/foaf:name",namespaces=main.nsSudoc).text).split(",")[1]
            if (premierauteurPrenom.find("(") > 0):
                premierauteurPrenom = premierauteurPrenom.split("(")[0]
    return [titre,premierauteurPrenom,premierauteurNom,tousauteurs]

#def tad2ark(NumNot,titre,auteur,auteur_nett,date_nett,numeroTome,typeRecord,typeDoc="a",anywhere=False,pubPlace_nett="", annee_plus_trois = False):
def tad2ark(input_record, anywhere=False, annee_plus_trois=False):
    "Fonction d'alignement par Titre-Auteur-Date (et contrôles sur type Notice, sur n° de volume si nécessaire)"
#En entrée : le numéro de notice, le titre (qu'il faut nettoyer pour la recherche)
#L'auteur = zone auteur initiale, ou à défaut auteur_nett
#date_nett
    #print(NumNot,titre,auteur,auteur_nett,date_nett,numeroTome,typeRecord,typeDoc,anywhere,pubPlace_nett, annee_plus_trois)
    listeArk = []
    #Cas des périodiques = on récupère uniquement la première date
    #Si elle est sur moins de 4 caractères (19.. devenu 19, 196u devenu 196)
    #   -> on tronque
    date_nett = input_record.date_nett
    if (input_record.intermarc_type_record == "s" and annee_plus_trois == False):
        date_nett = input_record.date_debut
    if (len(str(date_nett)) < 4 and date_nett != ""):
        date_nett += "*"
    param_date = "all"
    #Si on cherche l'année de début de périodique en élargissant à une fourchette de dates
    #3 ans avant et 3 ans après
    if (annee_plus_trois == True):
        param_date = "any"
        date_nett = input_record.dates_elargies_perios
    if (input_record.titre.recherche != ""):
        auteur = input_record.auteur
        auteur_nett = input_record.auteur_nett
        pubPlace_nett = input_record.pubPlace_nett
        if (input_record.auteur == ""):
            auteur = "-"
        if (date_nett == ""):
            date_nett = "-"
        if (auteur_nett == ""):
            auteur_nett = "-"
        if (pubPlace_nett == ""):
            pubPlace_nett = "-"
        url = funcs.url_requete_sru('bib.title all "' + input_record.titre.recherche + '" and bib.author all "' + auteur + '" and bib.date ' + param_date + ' "' + date_nett + '" and bib.publisher all "' + pubPlace_nett + '" and bib.doctype any "' + input_record.intermarc_type_doc + '"')
        if (anywhere == True):
            url = funcs.url_requete_sru('bib.anywhere all "' + input_record.titre.recherche + ' ' + auteur + ' ' + pubPlace_nett + '" and bib.anywhere ' + param_date + ' "' + date_nett + '" and bib.doctype any "' + input_record.intermarc_type_doc + '"')
        (test,results) = funcs.testURLetreeParse(url)
        index = ""
        if (results != "" and results.find("//srw:numberOfRecords", namespaces=main.ns).text == "0"):
            url = funcs.url_requete_sru('bib.title all "' + input_record.titre.recherche + '" and bib.author all "' + auteur_nett + '" and bib.date ' + param_date + ' "' + date_nett + '" and bib.publisher all "' + pubPlace_nett + '" and bib.doctype any "' + input_record.intermarc_type_doc + '"')
            if (anywhere == True):
                url = funcs.url_requete_sru('bib.anywhere all "' + input_record.titre.recherche + ' ' + auteur_nett + ' ' + pubPlace_nett + '" and bib.anywhere ' + param_date + ' "' + date_nett + '" and bib.doctype any "' + input_record.intermarc_type_doc + '"')
                index = " dans toute la notice"
            (test,results) = funcs.testURLetreeParse(url)
        if (test):
            i = 1
            total_rec = int(results.find("//srw:numberOfRecords", namespaces=main.ns).text)
            for record in results.xpath("//srw:recordIdentifier",namespaces=main.ns):
                ark_current = record.text
                if (int(results.find("//srw:numberOfRecords", namespaces=main.ns).text) > 100):
                    print("    ", input_record.NumNot, "-", ark_current, "".join([str(i), "/", str(total_rec), " (limite max 1000)"]))
                    i += 1
                #print(NumNot + " : " + ark_current)
                recordBNF_url = funcs.url_requete_sru('bib.persistentid all "' + ark_current + '"')
                (test,recordBNF) = funcs.testURLetreeParse(recordBNF_url)
                if (test == True):
                    if (recordBNF.find("//mxc:record/mxc:leader",namespaces=main.ns) is not None and recordBNF.find("//mxc:record/mxc:leader",namespaces=main.ns).text is not None):
                        typeRecord_current = recordBNF.find("//mxc:record/mxc:leader",namespaces=main.ns).text[7]
                        if (typeRecord_current == input_record.intermarc_type_record):
                            ark = comparaisonTitres(input_record.NumNot,ark_current,"","",input_record.titre.controles,auteur,date_nett,input_record.tome_nett,recordBNF,"Titre-Auteur-Date" + index)
                            if (date_nett != ""):
                                ark = checkDate(ark,date_nett,recordBNF)
                            if (ark != ""):
                                listeArk.append(ark)
                                methode = "Titre-Auteur-Date"
                                if (auteur == "-" and date_nett == "-"):
                                    methode = "Titre"
                                elif (auteur == "-"):
                                    methode = "Titre-Date"
                                elif (date_nett == "-"):
                                    methode = "Titre-Auteur"
                                NumNotices2methode[input_record.NumNot].append(methode)
                                if ("*" in date_nett):
                                    NumNotices2methode[input_record.NumNot].append("Date début tronquée")
                                if (annee_plus_trois == True):
                                    NumNotices2methode[input_record.NumNot].append("Date début +/- 3 ans")
    listeArk = ",".join(ark for ark in listeArk if ark != "")
    #Si la liste retournée est vide, et qu'on est sur des périodiques
    # et que la date
    if (listeArk == "" and input_record.intermarc_type_record == "s" and annee_plus_trois == False):
        listeArk = tad2ark(input_record, anywhere=False, annee_plus_trois=True)
    return listeArk

def tad2ppn(NumNot,titre,auteur,auteur_nett,date,typeRecord):
    #Recherche dans DoMyBiblio : Titre & Auteur dans tous champs, Date dans un champ spécifique
    Listeppn = []
    ark = []
    titre = funcs.nettoyageTitrePourRecherche(titre).replace(" ","+")
    auteur_nett = auteur_nett.replace(" ","+")
    typeRecord4DoMyBiblio = "all"
    """all (pour tous les types de document),
           B (pour les livres),
           T (pour les périodiques),
           Y (pour les thèses version de soutenance),
           V (pour le matériel audio-visuel)"""
    typeRecordDic = {"monimpr":"B","cddvd":"V","perimpr":"T"}
    if (typeRecord in typeRecordDic):
        typeRecord4DoMyBiblio = typeRecordDic[typeRecord]
    url = "".join(["http://domybiblio.net/search/search_api.php?type_search=all&q=",
                   urllib.parse.quote(" ".join([titre, auteur_nett])),
                   "&type_doc=",
                   typeRecord4DoMyBiblio,
                   "&period=",
                   date,
                   "&pageID=1&wp=true&idref=true&loc=true"])

    (test,results) = funcs.testURLetreeParse(url)
    if (test == True):
        nb_results = str(results.find(".//results").text)
        for record in results.xpath("//records/record"):
            ppn = record.find("identifier").text
            NumNotices2methode[NumNot].append("Titre-Auteur-Date DoMyBiblio")
            Listeppn.append("PPN" + ppn)
            ark.append(ppn2ark(NumNot,ppn,"",titre,auteur,date))
        if (nb_results < 11):
            tad2ppn_pages_suivantes(NumNot,titre,auteur,auteur_nett,date,typeRecord,url,nb_results,2,Listeppn,ark)
    #Si on trouve un PPN, on ouvre la notice pour voir s'il n'y a pas un ARK déclaré comme équivalent --> dans ce cas on récupère l'ARK
    Listeppn = ",".join([ppn for ppn in Listeppn if ppn != ""])
    ark = ",".join([ark1 for ark1 in ark if ark1 != ""])
    if (ark != ""):
        return ark
    else:
        return Listeppn

def tad2ppn_pages_suivantes(NumNot,titre,auteur,auteur_nett,date,typeRecord,url,nb_results,pageID,Listeppn,ark):
    url = url + "pageID=" + pageID
    (test,results) = funcs.testURLetreeParse(url)
    for record in results.xpath("//records/record"):
        ppn = record.find("identifier").text
        NumNotices2methode[NumNot].append("Titre-Auteur-Date DoMyBiblio")
        Listeppn.append("PPN" + ppn)
        ark.append(ppn2ark(NumNot,ppn,"",titre,auteur,date))
    if (nb_results >= pageID*10):
        tad2ppn_pages_suivantes(NumNot,titre,auteur,auteur_nett,date,typeRecord,url,nb_results,pageID+1)

def checkTypeRecord(ark,typeRecord_attendu):
    url = funcs.url_requete_sru('bib.ark any "' + ark + '"')
    #print(url)
    ark_checked = ""
    (test,record) = funcs.testURLetreeParse(url)
    if (test == True):
        typeRecord = record.find("//srw:recordData/mxc:record/mxc:leader",namespaces=main.ns).text[7]
        if (typeRecord == typeRecord_attendu):
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

def extract_meta(recordBNF,field_subfield,occ="all",anl=False):
    assert field_subfield.find("$") == 3
    assert len(field_subfield) == 5
    field = field_subfield.split("$")[0]
    subfield = field_subfield.split("$")[1]
    value = []
    path = "//srw:recordData/mxc:record/mxc:datafield[@tag='" + field + "']/mxc:subfield[@code='"+ subfield + "']"
    for elem in recordBNF.xpath(path,namespaces = main.ns):
        if (elem.text is not None):
            value.append(elem.text)
    if (occ == "first"):
        value = value[0]
    elif (occ == "all"):
        value = " ".join(value)
    return value

# def url_requete_sru(query,recordSchema="unimarcxchange",maximumRecords="1000",startRecord="1"):
#    url = main.urlSRUroot + urllib.parse.quote(query) +"&recordSchema=" + recordSchema + "&maximumRecords=" + maximumRecords + "&startRecord=" + startRecord + "&origin=bibliostratus"
#    return url


def ark2recordBNF(ark,typeRecord="bib"):
    url = funcs.url_requete_sru(typeRecord + '.persistentid any "' + ark + '"')
    (test,recordBNF) = funcs.testURLetreeParse(url)
    return (test,recordBNF)

def ean2ark(NumNot,ean,titre,auteur,date):
    listeARK = []
    url = funcs.url_requete_sru('bib.ean all "' + ean + '"')
    (test,results) = funcs.testURLetreeParse(url)
    if (test == True):
        for record in results.xpath("//srw:records/srw:record",namespaces=main.ns):
            if (record.find("srw:recordIdentifier",namespaces=main.ns) is not None):
                ark_current = record.find("srw:recordIdentifier",namespaces=main.ns).text
                (test2,recordBNF) = ark2recordBNF(ark_current)
                if (test2 ==  True):
                    ark = comparaisonTitres(NumNot,ark_current,"",ean,titre,auteur,date,"",recordBNF, "EAN")
                    if (ark != ""):
                        NumNotices2methode[NumNot].append("EAN > ARK")
                    listeARK.append(ark)
    listeARK = ",".join([ark for ark in listeARK if ark != ""])
    if (listeARK == "" and auteur != ""):
        listeARK = eanauteur2sru(NumNot,ean,titre,auteur,date)

    return listeARK

def nettoyage_no_commercial(no_commercial_propre):
    no_commercial_propre = unidecode(no_commercial_propre.lower())
    return no_commercial_propre

def no_commercial2ark(NumNot,no_commercial,titre,auteur,date,anywhere=False, publisher=""):
    no_commercial = no_commercial.strip(" ")
    url = funcs.url_requete_sru('bib.comref  all "' + no_commercial + '"')
    if (" " in no_commercial):
        no_commercial_source = " ".join([mot for mot in no_commercial.split(" ")[0:-1]])
        no_commercial_id = no_commercial.split(" ")[-1]
        url = funcs.url_requete_sru('bib.anywhere all "' + no_commercial_source + '" and bib.comref  all "' + no_commercial_id + '"')
    if (anywhere == True):
        url = funcs.url_requete_sru('bib.anywhere  all "' + no_commercial + '"')
    ark = ""
    (test,results) = funcs.testURLetreeParse(url)
    if (test == True):
        for record in results.xpath("//srw:records/srw:record",namespaces=main.ns):
            ark_current = record.find("srw:recordIdentifier",namespaces=main.ns).text
            (test2, recordBNF) = ark2recordBNF(ark_current)
            if (test2 == True):
                ark = controleNoCommercial(NumNot,ark_current,no_commercial,titre,auteur,date,recordBNF)
    return ark

def controleNoCommercial(NumNot,ark_current,no_commercial,titre,auteur,date,recordBNF):
    ark = ""
    no_commercialBNF = " ".join([nettoyage_no_commercial(extract_meta(recordBNF,"071$b")), nettoyage_no_commercial(extract_meta(recordBNF,"071$a"))])
    if (no_commercial != "" and no_commercialBNF != ""):
        if (no_commercial == no_commercialBNF or no_commercial in no_commercialBNF):
            ark = comparaisonTitres(NumNot,ark_current,"",no_commercial,titre,auteur,date,"",recordBNF, "No commercial")
            if (ark != ""):
                NumNotices2methode[NumNot].append("No commercial")
        elif (no_commercialBNF in no_commercial):
            ark = comparaisonTitres(NumNot,ark_current,"",no_commercial,titre,auteur,date,"",recordBNF, "No commercial")
            if (ark != ""):
                NumNotices2methode[NumNot].append("No commercial")
    return ark

#Si on a coché "Récupérer les données bibliographiques" : ouverture de la notice BIB de l'ARK et renvoie d'une liste de métadonnées
def ark2metadc(ark):
#Attention : la variable 'ark' peut contenir plusieurs ark séparés par des virgules
    listeARK = ark.split(",")

    #On récupére tous les titres de chaque ARK, puis tous les auteurs
    titlesList = []
    PremierAuteurPrenomList = []
    PremierAuteurNomList = []
    tousAuteursList = []
    dateList = []
    for ark in listeARK:
        metas_ark = ark2metas(ark,False)
        titlesList.append(metas_ark[0])
        PremierAuteurPrenomList.append(metas_ark[1])
        PremierAuteurNomList.append(metas_ark[2])
        tousAuteursList.append(metas_ark[3])
        dateList.append(metas_ark[4])
    titlesList = "|".join(titlesList)
    PremierAuteurPrenomList = "|".join(PremierAuteurPrenomList)
    PremierAuteurNomList = "|".join(PremierAuteurNomList)
    tousAuteursList = "|".join(tousAuteursList)
    dateList = "|".join(dateList)
    metas = [titlesList,PremierAuteurPrenomList,PremierAuteurNomList,tousAuteursList,dateList]
    return metas

def extract_cols_from_row(row,liste):
        nb_cols = len(row)
        i = 0
        liste_values = []
        for el in liste:
            if (i<nb_cols):
                liste_values.append(row[i])
            else:
                liste_values.append("")
            i += 1
        return tuple(liste_values)

def record2dic(row,option):
    """A partir d'une, et de l'indication de l'option "type de notice" (TEX, VID, AUD, PER)
    renvoi d'un dictionnaire fournissant les valeurs des différents champs"""
    input_record = Bib_record(row, option)
    return input_record

def item2ark_by_id(input_record):
    """Tronc commun de fonctions d'alignement, applicables pour tous les types de notices
    Par identifiant international : EAN, ISBN, N° commercial, ISSN"""
    ark = ""

    if (input_record.ark_init != ""):
        ark = ark2ark(input_record)

    #A défaut, recherche de l'ARK à partir du FRBNF (+ contrôles sur ISBN, ou Titre, ou Auteur)
    if (ark == "" and input_record.frbnf != ""):
        ark = frbnf2ark(input_record)
        ark = ",".join([ark1 for ark1 in ark.split(",") if ark1 != ''])

    #A défaut, recherche sur EAN
    if (ark == "" and input_record.ean.nett != ""):
        ark = ean2ark(input_record.NumNot,input_record.ean.propre,
                      input_record.titre_nett,
                      input_record.auteur_nett,
                      input_record.date_nett)

    #Si la recherche EAN + contrôles Titre/Date n'a rien donné -> on cherche EAN seul
    if (ark == "" and input_record.ean.nett != ""):
        ark = ean2ark(input_record.NumNot,input_record.ean.propre,"","","")


    #A défaut, recherche sur ISBN
    #Si plusieurs résultats, contrôle sur l'auteur
    if (ark == "" and input_record.isbn.nett != ""):
        ark = isbn2ark(input_record.NumNot,input_record.isbn.init, input_record.isbn.propre,input_record.isbn.converti,
                       input_record.titre_nett, input_record.auteur_nett, input_record.date_nett)


    #Si la recherche ISBN + contrôle Titre/Date n'a rien donné -> on cherche ISBN seul
    if (ark == "" and input_record.isbn.nett != ""):
        ark = isbn2ark(input_record.NumNot,input_record.isbn.init,input_record.isbn.propre,"","","")

    #A défaut, recherche sur no_commercial
    if (ark == "" and input_record.no_commercial != ""):
        ark = no_commercial2ark(input_record.NumNot,input_record.no_commercial_propre,input_record.titre_nett,input_record.auteur_nett,input_record.date_nett,False, input_record.publisher_nett)

    #A défaut, recherche sur ISSN
    if (ark == "" and input_record.issn.propre != ""):
        ark = issn2ark(input_record.NumNot,input_record.issn.init,input_record.issn.propre,input_record.titre_nett,input_record.auteur_nett,input_record.date_nett)
    return ark


def item2ppn_by_id(input_record):
    """Tronc commun de fonctions d'alignement, applicables pour tous les types de notices
    Quand l'option "BnF" d'abord a été choisie"""
    ark = ""

    #Si pas de résultats : on relance une recherche dans le Sudoc
    if (ark == ""):
        ark = ean2sudoc(input_record.NumNot,input_record.ean.propre,
                        input_record.titre_nett,input_record.auteur_nett,input_record.date_nett)

    #Si pas de résultats : on relance une recherche dans le Sudoc avec l'EAN seul
    if (ark == ""):
        ark = ean2sudoc(input_record.NumNot,input_record.ean.propre,"","","")
    if (ark == ""):
        ark = isbn2sudoc(input_record)
    if (ark == ""):
        ark = issn2sudoc(input_record.NumNot, input_record.issn.init,
                         input_record.issn.propre,
                         input_record.titre.controles,
                         input_record.auteur_nett, input_record.date_nett)


    return ark

def item2ark_by_keywords(input_record):
    """Alignement par mots clés"""
    ark = ""
    #A défaut, recherche sur Titre-Auteur-Date
    if (ark == "" and input_record.titre != ""):
        ark = tad2ark(input_record, False, False)
        #print("1." + NumNot + " : " + ark)
    if (ark == "" and input_record.titre != ""):
        ark = tad2ark(input_record, True, False)

    return ark

def item2id(row,n,form_bib2ark,parametres,liste_reports):
    """Pour chaque ligne : constitution d'une notice et règles d'alignement
    propres à ce type de notice"""
    if (n == 0):
        assert main.control_columns_number(form_bib2ark,row,parametres["header_columns_init"])
    if (n%100 == 0):
        main.check_access2apis(n,dict_check_apis)
    #print(row)

    input_record = Bib_record(row,parametres["type_doc_bib"])
    ark = ""
    #Si option 1 : on aligne sur les ID en commençant par la BnF, puis par le Sudoc
    # Si aucun résultat -> recherche Titre-Auteur-Date à la BnF
    # Si option 2 : on commence par le Sudoc, puis par la BnF
    if (parametres["preferences_alignement"] == 1):
        ark = item2ark_by_id(input_record)
        if (ark == ""):
            ark = item2ppn_by_id(input_record)
    else:
        ark = item2ppn_by_id(input_record)
        if (ark == ""):
            ark = item2ark_by_id(input_record)
    if (ark == ""):
            ark = item2ark_by_keywords(input_record)

    print(str(n) + ". " + input_record.NumNot + " : " + ark)
    nbARK = len(ark.split(","))
    if (ark == ""):
        nbARK = 0
    if (ark == "Pb FRBNF"):
        nb_notices_nb_ARK["Pb FRBNF"] += 1
    else:
        nb_notices_nb_ARK[nbARK] += 1
    typeConversionNumNot = ""
    if (input_record.NumNot in NumNotices2methode):
        typeConversionNumNot = ",".join(NumNotices2methode[input_record.NumNot])
        if (len(set(NumNotices2methode[input_record.NumNot])) == 1):
            typeConversionNumNot = list(set(NumNotices2methode[input_record.NumNot]))[0]
    liste_metadonnees = [input_record.NumNot,nbARK,ark,typeConversionNumNot] + input_record.metas_init
    if (parametres["meta_bib"] == 1):
        liste_metadonnees.extend(ark2metadc(ark))
    if (parametres["file_nb"] ==  1):
        row2file(liste_metadonnees,liste_reports)
    elif(parametres["file_nb"] ==  2):
        row2files(liste_metadonnees,liste_reports)

def file2row(form_bib2ark,zone_controles, entry_filename, liste_reports, parametres):
    """Récupération du contenu du fichier et application des règles d'alignement
    ligne à ligne"""
    header_columns_dic = {
            1 : ["NumNot","nbARK","ark trouvé","Méthode","ark initial","FRBNF","ISBN","EAN","Titre","auteur","date","Tome/Volume", "editeur"],
            2 : ["NumNot","nbARK","ark trouvé","Méthode","ark initial","FRBNF","EAN","no commercial propre","titre","auteur","date", "editeur"],
            3 : ["NumNot","nbARK","ark trouvé","Méthode","ark initial","FRBNF","EAN","no commercial propre","titre","auteur","date", "editeur"],
            4 : ["NumNot","nbARK","ark trouvé","Méthode","ark initial","frbnf","ISSN","titre","auteur","date","lieu"]
            }
    header_columns = header_columns_dic[parametres["type_doc_bib"]]
    if (parametres["meta_bib"] == 1):
        header_columns.extend(["[BnF] Titre","[BnF] 1er auteur Prénom","[BnF] 1er auteur Nom","[BnF] Tous auteurs","[BnF] Date"])
    if (parametres["file_nb"] ==  1):
        row2file(header_columns,liste_reports)
    elif(parametres["file_nb"] ==  2):
        row2files(header_columns,liste_reports)
    n = 0
    with open(entry_filename, newline='\n',encoding="utf-8") as csvfile:
        entry_file = csv.reader(csvfile, delimiter='\t')
        try:
            next(entry_file)
        except UnicodeDecodeError:
            main.popup_errors(form_bib2ark,main.errors["pb_input_utf8"],"Comment modifier l'encodage du fichier","https://github.com/Transition-bibliographique/bibliostratus/wiki/2-%5BBlanc%5D-:-alignement-des-donn%C3%A9es-bibliographiques-avec-la-BnF#erreur-dencodage-dans-le-fichier-en-entr%C3%A9e")
        for row in entry_file:
            item2id(row,n,form_bib2ark,parametres,liste_reports)
            n += 1

#==============================================================================
#
# def monimpr_item(row,n,form_bib2ark,parametres,liste_reports):
#     """Alignement pour 1 item (1 ligne) monographie imprimée"""
#     if (n == 0):
#         assert main.control_columns_number(form_bib2ark,row,header_columns_init_monimpr)
#     if (n%100 == 0):
#         main.check_access2apis(n,dict_check_apis)
#     #print(row)
#
#     input_record = Bib_record(row,1)
#     ark = ""
#     if (input_record.ark_init != ""):
#         ark = ark2ark(input_record)
#
#     #A défaut, recherche de l'ARK à partir du FRBNF (+ contrôles sur ISBN, ou Titre, ou Auteur)
#     if (ark == "" and input_record.frbnf != ""):
#         ark = frbnf2ark(input_record)
#         ark = ",".join([ark1 for ark1 in ark.split(",") if ark1 != ''])
#     #A défaut, recherche sur ISBN
#     #Si plusieurs résultats, contrôle sur l'auteur
#     if (ark == "" and input_record.isbn.nett != ""):
#         ark = isbn2ark(input_record.NumNot,input_record.isbn.init, input_record.isbn.propre,input_record.isbn.converti,
#                        input_record.titre_nett, input_record.auteur_nett, input_record.date_nett)
#
#     #Si la recherche ISBN + contrôle Titre/Date n'a rien donné -> on cherche ISBN seul
#     if (ark == "" and input_record.isbn.nett != ""):
#         ark = isbn2ark(input_record.NumNot,input_record.isbn.init,input_record.isbn_propre,"","","")
#
#     #Si pas de résultats : on relance une recherche dans le Sudoc
#     if (ark == "" and input_record.isbn.nett != ""):
#         ark = isbn2sudoc(input_record)
#
#     #A défaut, recherche sur EAN
#     if (ark == "" and input_record.ean.nett != ""):
#         ark = ean2ark(input_record.NumNot,input_record.ean.propre,
#                       input_record.titre_nett,
#                       input_record.auteur_nett,
#                       input_record.date_nett)
#
#     #Si la recherche EAN + contrôles Titre/Date n'a rien donné -> on cherche EAN seul
#     if (ark == "" and input_record.ean.nett != ""):
#         ark = ean2ark(input_record.NumNot,input_record.ean.propre,"","","")
#
#     #Si pas de résultats : on relance une recherche dans le Sudoc
#     if (ark == ""):
#         ark = ean2sudoc(input_record.NumNot,input_record.ean.propre,
#                         input_record.titre_nett,input_record.auteur_nett,input_record.date_nett)
#
#     #Si pas de résultats : on relance une recherche dans le Sudoc avec l'EAN seul
#     if (ark == ""):
#         ark = ean2sudoc(input_record.NumNot,input_record.ean.propre,"","","")
#
#
#     #A défaut, recherche sur Titre-Auteur-Date
#     if (ark == "" and input_record.titre != ""):
#         ark = tad2ark(input_record, False, False)
#         #print("1." + NumNot + " : " + ark)
#     if (ark == "" and input_record.titre != ""):
#         ark = tad2ark(input_record, True, False)
#
#     """if (ark == "" and titre != ""):
#         ark = tad2ppn(NumNot,titre,auteur,auteur_nett,date,"monimpr")"""
#
#     print(str(n) + ". " + input_record.NumNot + " : " + ark)
#     nbARK = len(ark.split(","))
#     if (ark == ""):
#         nbARK = 0
#     if (ark == "Pb FRBNF"):
#         nb_notices_nb_ARK["Pb FRBNF"] += 1
#     else:
#         nb_notices_nb_ARK[nbARK] += 1
#     typeConversionNumNot = ""
#     if (input_record.NumNot in NumNotices2methode):
#         typeConversionNumNot = ",".join(NumNotices2methode[input_record.NumNot])
#         if (len(set(NumNotices2methode[input_record.NumNot])) == 1):
#             typeConversionNumNot = list(set(NumNotices2methode[input_record.NumNot]))[0]
#     liste_metadonnees = [input_record.NumNot,nbARK,ark,typeConversionNumNot] + input_record.metas_init
#     if (parametres["meta_bib"] == 1):
#         liste_metadonnees.extend(ark2metadc(ark))
#     if (parametres["file_nb"] ==  1):
#         row2file(liste_metadonnees,liste_reports)
#     elif(parametres["file_nb"] ==  2):
#         row2files(liste_metadonnees,liste_reports)
#
# def monimpr(form_bib2ark, zone_controles, entry_filename, liste_reports, parametres):
#     header_columns = ["NumNot","nbARK","ark trouvé","Méthode","ark initial","FRBNF","ISBN","EAN","Titre","auteur","date","Tome/Volume", "editeur"]
#     if (parametres["meta_bib"] == 1):
#         header_columns.extend(["[BnF] Titre","[BnF] 1er auteur Prénom","[BnF] 1er auteur Nom","[BnF] Tous auteurs","[BnF] Date"])
#     if (parametres["file_nb"] ==  1):
#         row2file(header_columns,liste_reports)
#     elif(parametres["file_nb"] ==  2):
#         row2files(header_columns,liste_reports)
#     n = 0
#     with open(entry_filename, newline='\n',encoding="utf-8") as csvfile:
#         entry_file = csv.reader(csvfile, delimiter='\t')
#         try:
#             next(entry_file)
#         except UnicodeDecodeError:
#             main.popup_errors(form_bib2ark,main.errors["pb_input_utf8"],"Comment modifier l'encodage du fichier","https://github.com/Transition-bibliographique/bibliostratus/wiki/2-%5BBlanc%5D-:-alignement-des-donn%C3%A9es-bibliographiques-avec-la-BnF#erreur-dencodage-dans-le-fichier-en-entr%C3%A9e")
#         for row in entry_file:
#             monimpr_item(row,n,form_bib2ark,parametres,liste_reports)
#             n += 1
#
# def dvd_item(row,n,form_bib2ark,parametres,liste_reports):
#     if (n == 0):
#         assert main.control_columns_number(form_bib2ark,row,header_columns_init_cddvd)
#     if (n%100 == 0):
#         main.check_access2apis(n,dict_check_apis)
#
#     input_record = Bib_record(row,2)
#
#     #Actualisation de l'ARK à partir de l'ARK
#     ark = ""
#     if (input_record.ark_init != ""):
#         ark = ark2ark(input_record)
#
#     #A défaut, recherche de l'ARK à partir du FRBNF (+ contrôles sur ISBN, ou Titre, ou Auteur)
#     elif (input_record.frbnf != ""):
#         ark = frbnf2ark(input_record)
#         ark = ",".join([ark1 for ark1 in ark.split(",") if ark1 != ''])
#     #A défaut, recherche sur EAN
#     #Si plusieurs résultats, contrôle sur l'auteur
#     if (ark == "" and input_record.ean.nett != ""):
#         ark = ean2ark(input_record.NumNot,input_record.ean.propre,input_record.titre_nett,input_record.auteur_nett,input_record.date_nett)
#     #Si la recherche EAN + contrôle n'a rien donné -> on cherche EAN seul
#     if (ark == "" and input_record.ean.nett != ""):
#         ark = ean2ark(input_record.NumNot,input_record.ean.propre,"","","")
#
#     #A défaut, recherche sur no_commercial
#     if (ark == "" and input_record.no_commercial != ""):
#         ark = no_commercial2ark(input_record.NumNot,input_record.no_commercial_propre,input_record.titre_nett,input_record.auteur_nett,input_record.date_nett,False, input_record.publisher_nett)
#
#     #Si pas de résultats : on relance une recherche dans le Sudoc
#     if (ark == "" and input_record.ean.nett != ""):
#         ark = ean2sudoc(input_record.NumNot,input_record.ean.propre,input_record.titre_nett,input_record.auteur_nett,input_record.date_nett)
#     #Si pas de résultats : on relance une recherche dans le Sudoc
#     if (ark == "" and input_record.ean.nett != ""):
#         ark = ean2sudoc(input_record.NumNot,input_record.ean.propre,"","","")
#
#
#     #Si la recherche N° commercial + contrôle n'a rien donné -> on cherche N° commercial seul
#     #if (ark == "" and no_commercial != ""):
#     #    ark = no_commercial2ark(NumNot,no_commercial_propre,"","","",False, "")
#
#     #Si la recherche sur bib.comref n'a rien donné -> recherche du numéro partout dans la notice
#     #if (ark == "" and no_commercial != ""):
#     #    ark = no_commercial2ark(NumNot,no_commercial_propre,titre_nett,auteur_nett,date_nett,True, publisher_nett)
#
#     #A défaut, recherche sur Titre-Auteur-Date
#     if (ark == "" and input_record.titre_nett != ""):
#         ark = tad2ark(input_record, False, False)
#     #A défaut, on recherche Titre-Auteur dans tous champs (+Date comme date)
#     if (ark == "" and input_record.titre_nett != ""):
#         ark = tad2ark(input_record, True, False)
#     """
#     if (ark == "" and titre != ""):
#         ark = tad2ppn(NumNot,titre,auteur,auteur_nett,date,"cddvd")
#     """
#     print(str(n) + "." + input_record.NumNot + " : " + ark)
#     nbARK = len(ark.split(","))
#     if (ark == ""):
#         nbARK = 0
#     if (ark == "Pb FRBNF"):
#         nb_notices_nb_ARK["Pb FRBNF"] += 1
#     else:
#         nb_notices_nb_ARK[nbARK] += 1
#
#     typeConversionNumNot = ""
#     if (input_record.NumNot in NumNotices2methode):
#         typeConversionNumNot = ",".join(NumNotices2methode[input_record.NumNot])
#         if (len(set(NumNotices2methode[input_record.NumNot])) == 1):
#             typeConversionNumNot = list(set(NumNotices2methode[input_record.NumNot]))[0]
#     liste_metadonnees = [input_record.NumNot,nbARK,ark,typeConversionNumNot] + input_record.metas_init
#     if (parametres["meta_bib"] == 1):
#         liste_metadonnees.extend(ark2metadc(ark))
#     if (parametres["file_nb"] ==  1):
#         row2file(liste_metadonnees,liste_reports)
#     elif(parametres["file_nb"] ==  2):
#         row2files(liste_metadonnees,liste_reports)
#
# def dvd(form_bib2ark, zone_controles, entry_filename, liste_reports, parametres):
#     header_columns = ["NumNot","nbARK","ark trouvé","Méthode","ark initial","FRBNF","EAN","no_commercial_propre","titre","auteur","date", "editeur"]
#     if (parametres["meta_bib"] == 1):
#         header_columns.extend(["[BnF] Titre","[BnF] 1er auteur Prénom","[BnF] 1er auteur Nom","[BnF] Tous auteurs","[BnF] Date"])
#     if (parametres["file_nb"] ==  1):
#         row2file(header_columns,liste_reports)
#     elif(parametres["file_nb"] ==  2):
#         row2files(header_columns,liste_reports)
#     #results2file(nb_fichiers_a_produire)
#     n = 0
#     with open(entry_filename, newline='\n',encoding="utf-8") as csvfile:
#         entry_file = csv.reader(csvfile, delimiter='\t')
#         try:
#             next(entry_file)
#         except UnicodeDecodeError:
#             main.popup_errors(form_bib2ark,main.errors["pb_input_utf8"],"Comment modifier l'encodage du fichier","https://github.com/Transition-bibliographique/bibliostratus/wiki/2-%5BBlanc%5D-:-alignement-des-donn%C3%A9es-bibliographiques-avec-la-BnF#erreur-dencodage-dans-le-fichier-en-entr%C3%A9e")
#         for row in entry_file:
#             dvd_item(row,n,form_bib2ark,parametres,liste_reports)
#             n += 1
#
# def cd_item(row,n,form_bib2ark,parametres,liste_reports):
#     if (n == 0):
#         assert main.control_columns_number(form_bib2ark,row,header_columns_init_cddvd)
#     if (n%100 == 0):
#         main.check_access2apis(n,dict_check_apis)
#
#     input_record = Bib_record(row,3)
#     #Actualisation de l'ARK à partir de l'ARK
#     ark = ""
#     if (input_record.ark_init != ""):
#         ark = ark2ark(input_record)
#
#     #A défaut, recherche de l'ARK à partir du FRBNF (+ contrôles sur ISBN, ou Titre, ou Auteur)
#     elif (input_record.frbnf != ""):
#         ark = frbnf2ark(input_record)
#         ark = ",".join([ark1 for ark1 in ark.split(",") if ark1 != ''])
#     #A défaut, recherche sur EAN
#     #Si plusieurs résultats, contrôle sur l'auteur
#     if (ark == "" and input_record.ean.nett != ""):
#         ark = ean2ark(input_record.NumNot,input_record.ean.propre,input_record.titre_nett,input_record.auteur_nett,input_record.date_nett)
#     #Si la recherche EAN + contrôle n'a rien donné -> on cherche EAN seul
#     if (ark == "" and input_record.ean.nett != ""):
#         ark = ean2ark(input_record.NumNot,input_record.ean.propre,"","","")
#
#     #A défaut, recherche sur no_commercial
#     if (ark == "" and input_record.no_commercial != ""):
#         ark = no_commercial2ark(input_record.NumNot,input_record.no_commercial_propre,input_record.titre_nett,input_record.auteur_nett,input_record.date_nett,False, input_record.publisher_nett)
#
#     #Si la recherche N° commercial + contrôle n'a rien donné -> on cherche N° commercial seul
#     #if (ark == "" and no_commercial != ""):
#     #    ark = no_commercial2ark(NumNot,no_commercial_propre,"","","",False, "")
#
#     #Si la recherche sur bib.comref n'a rien donné -> recherche du numéro partout dans la notice
#     #if (ark == "" and no_commercial != ""):
#     #    ark = no_commercial2ark(NumNot,no_commercial_propre,titre_nett,auteur_nett,date_nett,True, publisher_nett)
#
#     #A défaut, recherche sur Titre-Auteur-Date
#     if (ark == "" and input_record.titre != ""):
#         ark = tad2ark(input_record, False, False)
#     #A défaut, on recherche Titre-Auteur dans tous champs (+Date comme date)
#     if (ark == "" and input_record.titre != ""):
#         ark = tad2ark(input_record, True, False)
#     """
#     if (ark == "" and titre != ""):
#         ark = tad2ppn(NumNot,titre,auteur,auteur_nett,date,"cddvd")
#     """
#     print(str(n) + "." + input_record.NumNot + " : " + ark)
#     nbARK = len(ark.split(","))
#     if (ark == ""):
#         nbARK = 0
#     if (ark == "Pb FRBNF"):
#         nb_notices_nb_ARK["Pb FRBNF"] += 1
#     else:
#         nb_notices_nb_ARK[nbARK] += 1
#
#     typeConversionNumNot = ""
#     if (input_record.NumNot in NumNotices2methode):
#         typeConversionNumNot = ",".join(NumNotices2methode[input_record.NumNot])
#         if (len(set(NumNotices2methode[input_record.NumNot])) == 1):
#             typeConversionNumNot = list(set(NumNotices2methode[input_record.NumNot]))[0]
#     liste_metadonnees = [input_record.NumNot,nbARK,ark,typeConversionNumNot] + input_record.metas_init
#     if (parametres["meta_bib"] == 1):
#         liste_metadonnees.extend(ark2metadc(ark))
#     if (parametres["file_nb"] ==  1):
#         row2file(liste_metadonnees,liste_reports)
#     elif(parametres["file_nb"] ==  2):
#         row2files(liste_metadonnees,liste_reports)
#
# def cd(form_bib2ark, zone_controles, entry_filename, liste_reports, parametres):
#     header_columns = ["NumNot","nbARK","ark trouvé","Méthode","ark initial","FRBNF","EAN","no_commercial_propre","titre","auteur","date", "editeur"]
#     if (parametres["meta_bib"] == 1):
#         header_columns.extend(["[BnF] Titre","[BnF] 1er auteur Prénom","[BnF] 1er auteur Nom","[BnF] Tous auteurs","[BnF] Date"])
#     if (parametres["file_nb"] ==  1):
#         row2file(header_columns,liste_reports)
#     elif(parametres["file_nb"] ==  2):
#         row2files(header_columns,liste_reports)
#     #results2file(nb_fichiers_a_produire)
#     n = 0
#     with open(entry_filename, newline='\n',encoding="utf-8") as csvfile:
#         entry_file = csv.reader(csvfile, delimiter='\t')
#         try:
#             next(entry_file)
#         except UnicodeDecodeError:
#             main.popup_errors(form_bib2ark,main.errors["pb_input_utf8"],"Comment modifier l'encodage du fichier","https://github.com/Transition-bibliographique/bibliostratus/wiki/2-%5BBlanc%5D-:-alignement-des-donn%C3%A9es-bibliographiques-avec-la-BnF#erreur-dencodage-dans-le-fichier-en-entr%C3%A9e")
#         for row in entry_file:
#             cd_item(row,n,form_bib2ark,parametres,liste_reports)
#             n += 1
#
#
#
# def perimpr_item(row,n,form_bib2ark,parametres,liste_reports):
#     if (n == 0):
#         assert main.control_columns_number(form_bib2ark,row,header_columns_init_perimpr)
#     if (n%100 == 0):
#         main.check_access2apis(n,dict_check_apis)
#     #print(row)
#     input_record = Bib_record(row,4)
#     #Actualisation de l'ARK à partir de l'ARK
#     ark = ""
#     if (input_record.ark_init != ""):
#         ark = ark2ark(input_record)
#
#     #A défaut, recherche de l'ARK à partir du FRBNF (+ contrôles sur ISBN, ou Titre, ou Auteur)
#     if (ark == "" and input_record.frbnf != ""):
#         ark = frbnf2ark(input_record)
#         ark = ",".join(ark1 for ark1 in ark.split(",") if ark1 != '')
#     #A défaut, recherche sur ISSN
#     if (ark == "" and input_record.issn.nett != ""):
#         ark = issn2ark(input_record.NumNot,input_record.issn.init,input_record.issn.propre,input_record.titre_nett,input_record.auteur_nett,input_record.date_nett)
#     #A défaut, recherche sur Titre-Auteur-Date
#     if (ark == "" and input_record.titre != ""):
#         ark = tad2ark(input_record, False, False)
#     #A défaut, recherche sur T-A-D tous mots
#     if (ark == "" and input_record.titre != ""):
#         ark = tad2ark(input_record, True, False)
#     print(str(n) + ". " + input_record.NumNot + " : " + ark)
#     nbARK = len(ark.split(","))
#     if (ark == ""):
#         nbARK = 0
#     if (ark == "Pb FRBNF"):
#         nb_notices_nb_ARK["Pb FRBNF"] += 1
#     else:
#         nb_notices_nb_ARK[nbARK] += 1
#
#     typeConversionNumNot = ""
#     if (input_record.NumNot in NumNotices2methode):
#         typeConversionNumNot = ",".join(NumNotices2methode[input_record.NumNot])
#         if (len(set(NumNotices2methode[input_record.NumNot])) == 1):
#             typeConversionNumNot = list(set(NumNotices2methode[input_record.NumNot]))[0]
#     liste_metadonnees = [input_record.NumNot,nbARK,ark,typeConversionNumNot] + input_record.metas_init
#     if (parametres["meta_bib"] == 1):
#         liste_metadonnees.extend(ark2metadc(ark))
#     if (parametres["file_nb"] ==  1):
#         row2file(liste_metadonnees,liste_reports)
#     elif(parametres["file_nb"]  ==  2):
#         row2files(liste_metadonnees,liste_reports)
#
#
# #Si option du formulaire = périodiques imprimés
# def perimpr(form_bib2ark, zone_controles, entry_filename, liste_reports, parametres):
#     header_columns = ["NumNot","nbARK","ark trouvé","Méthode","ark initial","frbnf","ISSN","titre","auteur","date","lieu"]
#     if (parametres["meta_bib"] == 1):
#         header_columns.extend(["[BnF] Titre","[BnF] 1er auteur Prénom","[BnF] 1er auteur Nom","[BnF] Tous auteurs","[BnF] Date"])
#     if (parametres["file_nb"] ==  1):
#         row2file(header_columns,liste_reports)
#     elif(parametres["file_nb"] ==  2):
#         row2files(header_columns,liste_reports)
#     n = 0
#     with open(entry_filename, newline='\n',encoding="utf-8") as csvfile:
#         entry_file = csv.reader(csvfile, delimiter='\t')
#         try:
#             next(entry_file)
#         except UnicodeDecodeError:
#             main.popup_errors(form_bib2ark,main.errors["pb_input_utf8"],"Comment modifier l'encodage du fichier","https://github.com/Transition-bibliographique/bibliostratus/wiki/2-%5BBlanc%5D-:-alignement-des-donn%C3%A9es-bibliographiques-avec-la-BnF#erreur-dencodage-dans-le-fichier-en-entr%C3%A9e")
#         for row in entry_file:
#             perimpr_item(row,n,form_bib2ark,parametres,liste_reports)
#             n += 1

def launch(form_bib2ark,zone_controles, entry_filename, type_doc_bib, preferences_alignement, file_nb, meta_bib, id_traitement):

    #Préférences alignement : 1 = BnF d'abord, puis Sudoc. 2 : Sudoc d'abord, puis BnF
    header_columns_init_dic = { 1: header_columns_init_monimpr,
                               2 : header_columns_init_cddvd,
                               3 : header_columns_init_cddvd,
                               4 : header_columns_init_perimpr}
    parametres = {"meta_bib":meta_bib,
                  "type_doc_bib":type_doc_bib,
                  "file_nb":file_nb,
                  "id_traitement":id_traitement,
                  "header_columns_init":header_columns_init_dic[type_doc_bib],
                  "preferences_alignement":preferences_alignement}
    main.check_file_name(form_bib2ark, entry_filename)

    #results2file(nb_fichiers_a_produire)
    #print("type_doc_bib : ", type_doc_bib)
    #print("file_nb : ",file_nb)
    #print("id_traitement : ", id_traitement)
    liste_reports = create_reports(id_traitement, file_nb)
    file2row(form_bib2ark,zone_controles, entry_filename, liste_reports, parametres)
#==============================================================================
#      if (type_doc_bib == 1):
#          monimpr(form_bib2ark,zone_controles, entry_filename, liste_reports, parametres)
#      elif (type_doc_bib == 2):
#          dvd(form_bib2ark,zone_controles, entry_filename, liste_reports, parametres)
#      elif (type_doc_bib == 3):
#          cd(form_bib2ark,zone_controles, entry_filename, liste_reports, parametres)
#      elif (type_doc_bib == 4):
#          perimpr(form_bib2ark,zone_controles, entry_filename, liste_reports, parametres)
#
#      else:
#          print("Erreur : type de document non reconnu")
#
#==============================================================================
    fin_traitements(form_bib2ark,liste_reports,nb_notices_nb_ARK)
#
#==============================================================================

def fin_traitements(form_bib2ark,liste_reports,nb_notices_nb_ARK):
    stats_extraction(liste_reports,nb_notices_nb_ARK)
    url_access_pbs_report(liste_reports)
    check_access_to_apis(liste_reports)
    typesConversionARK(liste_reports)
    print("Programme terminé")
    form_bib2ark.destroy()
    for file in liste_reports:
        file.close()



def stats_extraction(liste_reports,nb_notices_nb_ARK):
    """Ecriture des rapports de statistiques générales d'alignements"""
    for key in nb_notices_nb_ARK:
        liste_reports[-1].write(str(key) + "\t" + str(nb_notices_nb_ARK[key]) + "\n")
    """if ("Pb FRBNF" in sorted(nb_notices_nb_ARK)):
        nb_notices_nb_ARK[-2] = nb_notices_nb_ARK.pop('Pb FRBNF')"""
    """plt.bar(list(nb_notices_nb_ARK.keys()), nb_notices_nb_ARK.values(), color='skyblue')
    plt.show()"""

def url_access_pbs_report(liste_reports):
    """A la suite des stats générales, liste des erreurs rencontrées (plantage URL) + ISBN différents en entrée et en sortie"""
    if (len(url_access_pbs) > 0):
        liste_reports[-1].write("\n\nProblème d'accès à certaines URL :\nURL\tType de problème\n")
        for pb in url_access_pbs:
            liste_reports[-1].write("\t".join(pb) + "\n")
    if (len(NumNotices_conversionISBN) > 0):
        liste_reports[-1].write("".join(["\n\n",10*"-","\n"]))
        liste_reports[-1].write("Liste des notices dont l'ISBN en entrée est différent de celui dans la notice trouvée\n")
        liste_reports[-1].write("\t".join(["NumNotice",
                                                "ISBN initial",
                                                "ISBN converti",
                                                "Notice trouvée dans le Sudoc ?",
                                                ]) + "\n")
        for record in NumNotices_conversionISBN:
            liste_reports[-1].write("\t".join([record,
                                                NumNotices_conversionISBN[record]["isbn initial"],
                                                NumNotices_conversionISBN[record]["isbn trouvé"],
                                                NumNotices_conversionISBN[record]["via Sudoc"],
                                                ]) + "\n")
def check_access_to_apis(liste_reports):
    """Contrôles réguliers de l'accès aux API Abes et BnF -> enregistrés dans
    le dictionnaire dict_check_apis.
    Si celui-ci contient au moins un "False", on génère une rubrique
    dans le rapport Stats"""
    if (False in dict_check_apis["testAbes"]):
        liste_reports[-1].write("\n\nProblème d'accès aux API Abes\n")
        for key in dict_check_apis["testAbes"]:
            if (dict_check_apis["testAbes"][key] is False):
                liste_reports[-1].write("".join([str(key)," : API Abes down\n"]))
    if (False in dict_check_apis["testBnF"]):
        liste_reports[-1].write("\n\nProblème d'accès aux API BnF\n")
        for key in dict_check_apis["testBnF"]:
            if (dict_check_apis["testBnF"][key] is False):
                liste_reports[-1].write("".join([str(key)," : API BnF down\n"]))


def typesConversionARK(liste_reports):
    """Dans un rapport spécifique, pour chaque notice en entrée, mention de la méthode d'alignement (ISBN, ISNI, etc.)"""
    """for key in NumNotices2methode:
        value = " / ".join(NumNotices2methode[key])
        liste_reports[-1].write(key + "\t" + value + "\n")"""

def annuler(form_bib2ark):
    """Fermeture du formulaire (bouton "Annuler")"""
    form_bib2ark.destroy()


#==============================================================================
# def check_last_compilation(programID):
#     """Compare pour un programme donné le numéro de version du fichier en cours et la dernière version indiquée comme telle en ligne. Renvoie une liste à deux éléments : n° de la dernière version publiée ; affichage du bouton de téléchargement (True/False)"""
#     programID_last_compilation = 0
#     display_update_button = False
#     url = "https://raw.githubusercontent.com/Lully/bnf-sru/master/last_compilations.json"
#     last_compilations = request.urlopen(url)
#     reader = codecs.getreader("utf-8")
#     last_compilations = json.load(reader(last_compilations))["last_compilations"][0]
#     if (programID in last_compilations):
#         programID_last_compilation = last_compilations[programID]
#     if (programID_last_compilation > version):
#         display_update_button = True
#     return [programID_last_compilation,display_update_button]
#
#==============================================================================
#La vérification de la dernière version n'est faite que si le programme est lancé en standalone
#last_version = [0,False]

#==============================================================================
# def download_last_update():
#     """Fournit l'URL de téléchargement de la dernière version"""
#     url = "https://github.com/Transition-bibliographique/bibliostratus/blob/master/noticesbib2arkBnF.py"
#     webbrowser.open(url)
#==============================================================================
#==============================================================================
# Création de la boîte de dialogue
#==============================================================================

def radioButton_lienExample(frame,variable_button,val,couleur_fond,text1,text2,link):
    packButton = tk.Frame(frame, bg=couleur_fond)
    packButton.pack(anchor="w")
    line1 = tk.Frame(packButton, bg=couleur_fond)
    line1.pack(anchor="w")
    tk.Radiobutton(line1,bg=couleur_fond,
                   text=text1,
                   variable=variable_button, value=val, justify="left").pack(anchor="w", side="left")
    if (link != ""):
        tk.Label(line1,text="  ",bg=couleur_fond).pack(anchor="w", side="left")
        example_ico = tk.Button(line1, bd=0, justify="left", font="Arial 7 underline",
                                    text="exemple", fg="#0000ff", bg=couleur_fond, command=lambda: main.click2url(link))
        example_ico.pack(anchor="w", side="left")
    if (text2 != ""):
        line2 = tk.Frame(packButton, bg=couleur_fond)
        line2.pack(anchor="w")
        tk.Label(line2, bg=couleur_fond, text="      "+text2, justify="left").pack(anchor="w")


def formulaire_noticesbib2arkBnF(master,access_to_network=True, last_version=[0,False]):
    """Affichage du formulaire : disposition des zones, options, etc."""
    couleur_fond = "white"
    couleur_bouton = "#acacac"

    [form_bib2ark,
     zone_alert_explications,
     zone_access2programs,
     zone_actions,
     zone_ok_help_cancel,
     zone_notes] = main.form_generic_frames(master,"Programme d'alignement de données bibliographiques avec la BnF",
                                      couleur_fond,couleur_bouton,
                                      access_to_network)

    cadre_input = tk.Frame(zone_actions, highlightthickness=2, highlightbackground=couleur_bouton, relief="groove", height=150, padx=10,bg=couleur_fond)
    cadre_input.pack(side="left")
    cadre_input_header = tk.Frame(cadre_input,bg=couleur_fond)
    cadre_input_header.pack(anchor="w")
    cadre_input_file = tk.Frame(cadre_input,bg=couleur_fond)
    cadre_input_file.pack(anchor="w")
    cadre_input_infos_format = tk.Frame(cadre_input,bg=couleur_fond)
    cadre_input_infos_format.pack(anchor="w")
    cadre_input_type_docs = tk.Frame(cadre_input,bg=couleur_fond)
    cadre_input_type_docs.pack(anchor="w")

    cadre_input_type_docs_zone = tk.Frame(cadre_input_type_docs,bg=couleur_fond)
    cadre_input_type_docs_zone.pack(anchor="w")
    cadre_input_type_docs_explications = tk.Frame(cadre_input_type_docs,bg=couleur_fond)
    cadre_input_type_docs_explications.pack(anchor="w")


    cadre_inter = tk.Frame(zone_actions, borderwidth=0, padx=10,bg=couleur_fond)
    cadre_inter.pack(side="left")
    tk.Label(cadre_inter, text=" ",bg=couleur_fond).pack()

    cadre_output = tk.Frame(zone_actions, highlightthickness=2, highlightbackground=couleur_bouton, relief="groove", height=150, padx=10,bg=couleur_fond)
    cadre_output.pack(side="left", anchor="w")
    cadre_output_header = tk.Frame(cadre_output,bg=couleur_fond)
    cadre_output_header.pack(anchor="w")
    cadre_output_nb_fichier = tk.Frame(cadre_output,bg=couleur_fond)
    cadre_output_nb_fichier.pack(side="left", anchor="w")

    cadre_output_nb_fichiers_zone = tk.Frame(cadre_output_nb_fichier,bg=couleur_fond)
    cadre_output_nb_fichiers_zone.pack(anchor="w")
    cadre_output_nb_fichiers_explications = tk.Frame(cadre_output_nb_fichier,bg=couleur_fond)
    cadre_output_nb_fichiers_explications.pack(anchor="w")

    cadre_output_id_traitement = tk.Frame(cadre_output, padx=20,bg=couleur_fond)
    cadre_output_id_traitement.pack(side="left", anchor="w")

    zone_notes_message_en_cours = tk.Frame(zone_notes, padx=20,bg=couleur_fond)
    zone_notes_message_en_cours.pack()


#==============================================================================
# Message d'alerte dans le formulaire si besoin
#==============================================================================
#    tk.Label(zone_alert_explications, text="Attention : format MON IMPR avec une colonne supplémentaire en entrée (EAN)",
#             bg=couleur_fond,  fg="red").pack()

    #définition input URL (u)
    tk.Label(cadre_input_header,bg=couleur_fond, fg=couleur_bouton, text="En entrée :", justify="left", font="bold").pack()

    tk.Label(cadre_input_file,bg=couleur_fond, text="Fichier contenant les notices :\n\n").pack(side="left")
    """entry_filename = tk.Entry(cadre_input_file, width=40, bd=2)
    entry_filename.pack(side="left")
    entry_filename.focus_set()"""
    main.download_zone(cadre_input_file, "Sélectionner un fichier\nSéparateur TAB, Encodage UTF-8",entry_file_list,couleur_fond,zone_notes)

    #tk.Label(cadre_input_infos_format,bg=couleur_fond, text=4*"\t"+"Séparateur TAB, Encodage UTF-8", justify="right").pack(anchor="s")


    tk.Label(cadre_input_type_docs_zone,bg=couleur_fond, text="Type de documents  ", font="Arial 10 bold", justify="left").pack(anchor="w", side="left")

    type_doc_bib = tk.IntVar()
    radioButton_lienExample(cadre_input_type_docs,type_doc_bib,1,couleur_fond,
                            "[TEX] Monographies texte",
                            "(Colonnes : " + " | ".join(header_columns_init_monimpr) + ")",
                            "https://raw.githubusercontent.com/Transition-bibliographique/bibliostratus/master/examples/mon_impr.tsv")
    radioButton_lienExample(cadre_input_type_docs,type_doc_bib,2,couleur_fond,
                            "[VID] Audiovisuel (DVD)",
                            "(" + " | ".join(header_columns_init_cddvd) + ")",
                            "")
    radioButton_lienExample(cadre_input_type_docs,type_doc_bib,3,couleur_fond,
                            "[AUD] Enregistrements sonores",
                            "(" + " | ".join(header_columns_init_cddvd) + ")",
                            "https://raw.githubusercontent.com/Transition-bibliographique/bibliostratus/master/examples/audio.tsv")
    radioButton_lienExample(cadre_input_type_docs,type_doc_bib,4,couleur_fond,
                            "[PER] Périodiques",
                            "(" + " | ".join(header_columns_init_perimpr) + ")",
                            "https://raw.githubusercontent.com/Transition-bibliographique/bibliostratus/master/examples/per.tsv")
    type_doc_bib.set(1)

    tk.Label(cadre_input_type_docs,bg=couleur_fond, text="\nPréférences", font="Arial 10 bold",
             justify="left").pack(anchor="w")
    preferences_alignement = tk.IntVar()
    radioButton_lienExample(cadre_input_type_docs,preferences_alignement,1,couleur_fond,
                            "Essayer d'abord l'alignement BnF",
                            "",
                            "")
    radioButton_lienExample(cadre_input_type_docs,preferences_alignement,2,couleur_fond,
                            "Essayer d'abord l'alignement Sudoc",
                            "",
                            "")
    preferences_alignement.set(1)


    #Choix du format
    tk.Label(cadre_output_header,bg=couleur_fond, fg=couleur_bouton,text="En sortie :", font="bold").pack(anchor="w")
    tk.Label(cadre_output_nb_fichiers_zone, bg=couleur_fond, font="Arial 10 bold", text="Nombre de fichiers  ").pack(anchor="w", side="left")
    file_nb = tk.IntVar()
    """file_nb = tk.Entry(cadre_output_nb_fichiers_zone, width=3, bd=2)
    file_nb.pack(anchor="w", side="left")
    tk.Label(cadre_output_nb_fichiers_explications, bg=couleur_fond,text="1 = 1 fichier d'alignements\n2 = Plusieurs fichiers (0 ARK trouvé / 1 ARK / Plusieurs ARK)",
                                   justify="left").pack(anchor="w")"""


    tk.Radiobutton(cadre_output_nb_fichier,bg=couleur_fond, text="1 fichier", variable=file_nb , value=1, justify="left").pack(anchor="w")
    tk.Radiobutton(cadre_output_nb_fichier,bg=couleur_fond, text="Plusieurs fichiers\n(Pb / 0 / 1 / plusieurs ARK trouvés)", justify="left", variable=file_nb , value=2).pack(anchor="w")
    file_nb.set(1)
    #Récupérer les métadonnées BIB (dublin core)
    tk.Label(cadre_output_nb_fichier,bg=couleur_fond, fg=couleur_bouton, text="\n").pack()
    meta_bib = tk.IntVar()
    meta_bib_check = tk.Checkbutton(cadre_output_nb_fichier, bg=couleur_fond,
                       text="Récupérer les métadonnées\nbibliographiques BnF [Dublin Core]",
                       variable=meta_bib, justify="left")
    meta_bib_check.pack(anchor="w")
    tk.Label(cadre_output_nb_fichier,text="\n"*14, bg=couleur_fond).pack()



    #Ajout (optionnel) d'un identifiant de traitement
    tk.Label(cadre_output_id_traitement,bg=couleur_fond, text="\n\n\n").pack()
    tk.Label(cadre_output_id_traitement,bg=couleur_fond, text="Préfixe fichiers en sortie").pack()
    id_traitement = tk.Entry(cadre_output_id_traitement, width=20, bd=2)
    id_traitement.pack()
    tk.Label(cadre_output_id_traitement,bg=couleur_fond, text="\n\n\n").pack()



    #Bouton de validation

    b = tk.Button(zone_ok_help_cancel, bg=couleur_bouton, fg="white", font="Arial 10 bold",
                  text = "Aligner les\nnotices BIB",
                  command = lambda: launch(form_bib2ark,zone_controles,
                                           entry_file_list[0], type_doc_bib.get(),
                                           preferences_alignement.get(),
                                           file_nb.get(), meta_bib.get(),
                                           id_traitement.get()), borderwidth=5 ,padx=10, pady=10, width=10, height=4)
    b.pack()

    tk.Label(zone_ok_help_cancel, font="bold", text="", bg=couleur_fond).pack()

    call4help = tk.Button(zone_ok_help_cancel,
                          text=main.texte_bouton_help,
                          command=lambda: main.click2url(main.url_online_help),
                          pady=5, padx=5, width=12)
    call4help.pack()
    tk.Label(zone_ok_help_cancel, text="\n",bg=couleur_fond, font="Arial 1 normal").pack()

    forum_button = tk.Button(zone_ok_help_cancel,
                          text=main.texte_bouton_forum,
                          command=lambda: main.click2url(main.url_forum_aide),
                          pady=5, padx=5, width=12)
    forum_button.pack()

    tk.Label(zone_ok_help_cancel, text="\n",bg=couleur_fond, font="Arial 4 normal").pack()
    cancel = tk.Button(zone_ok_help_cancel, text="Annuler",bg=couleur_fond, command=lambda: main.annuler(form_bib2ark), pady=10, padx=5, width=12)
    cancel.pack()

    zone_version = tk.Frame(zone_notes, bg=couleur_fond)
    zone_version.pack()
    tk.Label(zone_version, text = "BiblioStratus - Version " + str(main.version) + " - " + main.lastupdate, bg=couleur_fond).pack()

    zone_controles = tk.Frame(zone_notes, bg=couleur_fond)
    zone_controles.pack()

    """if (main.last_version[1] == True):
        download_update = tk.Button(zone_notes, text = "Télécharger la version " + str(main.last_version[0]), command=download_last_update)
        download_update.pack()"""


    tk.mainloop()

if __name__ == '__main__':
    access_to_network = main.check_access_to_network()
    last_version = [0,False]
    #if(access_to_network is True):
    #    last_version = check_last_compilation(programID)
    main.formulaire_main(access_to_network, last_version)
    #formulaire_noticesbib2arkBnF(access_to_network,last_version)

