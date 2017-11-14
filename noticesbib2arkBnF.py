# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 18:30:30 2017

@author: Etienne Cavalié

Programme d'identification des ARK BnF à partir de numéros FRBNF

"""

from lxml import etree
from urllib import request
import urllib.parse
from unidecode import unidecode
import urllib.error as error
import csv
import tkinter as tk
from collections import defaultdict
import re
import webbrowser
import codecs
import json


#import matplotlib.pyplot as plt

version = 0.6
lastupdate = "10/11/2017"
programID = "noticesbib2arkBnF"

errors = {
        "no_internet" : "Attention : Le programme n'a pas d'accès à Internet.\nSi votre navigateur y a accès, vérifiez les paramètres de votre proxy"
        }


ns = {"srw":"http://www.loc.gov/zing/srw/", "mxc":"info:lc/xmlns/marcxchange-v2", "m":"http://catalogue.bnf.fr/namespaces/InterXMarc","mn":"http://catalogue.bnf.fr/namespaces/motsnotices"}
nsSudoc = {"rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bibo":"http://purl.org/ontology/bibo/", "dc":"http://purl.org/dc/elements/1.1/", "dcterms":"http://purl.org/dc/terms/", "rdafrbr1":"http://rdvocab.info/RDARelationshipsWEMI/", "marcrel":"http://id.loc.gov/vocabulary/relators/", "foaf":"http://xmlns.com/foaf/0.1/", "gr":"http://purl.org/goodrelations/v1#", "owl":"http://www.w3.org/2002/07/owl#", "isbd":"http://iflastandards.info/ns/isbd/elements/", "skos":"http://www.w3.org/2004/02/skos/core#", "rdafrbr2":"http://RDVocab.info/uri/schema/FRBRentitiesRDA/", "rdaelements":"http://rdvocab.info/Elements/", "rdac":"http://rdaregistry.info/Elements/c/", "rdau":"http://rdaregistry.info/Elements/u/", "rdaw":"http://rdaregistry.info/Elements/w/", "rdae":"http://rdaregistry.info/Elements/e/", "rdam":"http://rdaregistry.info/Elements/m/", "rdai":"http://rdaregistry.info/Elements/i/", "sudoc":"http://www.sudoc.fr/ns/", "bnf-onto":"http://data.bnf.fr/ontology/bnf-onto/"}

#Pour chaque notice, on recense la méthode qui a permis de récupérer le ou les ARK
NumNotices2methode = defaultdict(list)

#Quelques listes de signes à nettoyer
listeChiffres = ["0","1","2","3","4","5","6","7","8","9"]
lettres = ["a","b","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
ponctuation = [".",",",";",":","?","!","%","$","£","€","#","\\","\"","&","~","{","(","[","`","\\","_","@",")","]","}","=","+","*","\/","<",">",")","}"]

#Noms des fichiers en sortie


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


ns = {"srw":"http://www.loc.gov/zing/srw/", "mxc":"info:lc/xmlns/marcxchange-v2", "m":"http://catalogue.bnf.fr/namespaces/InterXMarc","mn":"http://catalogue.bnf.fr/namespaces/motsnotices"}
nsOCLC = {"xisbn": "http://worldcat.org/xid/isbn/"}
nsSudoc = {"rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bibo":"http://purl.org/ontology/bibo/", "dc":"http://purl.org/dc/elements/1.1/", "dcterms":"http://purl.org/dc/terms/", "rdafrbr1":"http://rdvocab.info/RDARelationshipsWEMI/", "marcrel":"http://id.loc.gov/vocabulary/relators/", "foaf":"http://xmlns.com/foaf/0.1/", "gr":"http://purl.org/goodrelations/v1#", "owl":"http://www.w3.org/2002/07/owl#", "isbd":"http://iflastandards.info/ns/isbd/elements/", "skos":"http://www.w3.org/2004/02/skos/core#", "rdafrbr2":"http://RDVocab.info/uri/schema/FRBRentitiesRDA/", "rdaelements":"http://rdvocab.info/Elements/", "rdac":"http://rdaregistry.info/Elements/c/", "rdau":"http://rdaregistry.info/Elements/u/", "rdaw":"http://rdaregistry.info/Elements/w/", "rdae":"http://rdaregistry.info/Elements/e/", "rdam":"http://rdaregistry.info/Elements/m/", "rdai":"http://rdaregistry.info/Elements/i/", "sudoc":"http://www.sudoc.fr/ns/", "bnf-onto":"http://data.bnf.fr/ontology/bnf-onto/"}

#fonction de mise à jour de l'ARK s'il existe un ARK
def ark2ark(NumNot,ark):
    url = "http://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query=bib.ark%20all%20%22" + urllib.parse.quote(ark) + "%22&recordSchema=unimarcxchange&maximumRecords=20&startRecord=1"
    page = etree.parse(url)
    nv_ark = ""
    if (page.find("//srw:recordIdentifier", namespaces=ns) is not None):
        nv_ark = page.find("//srw:recordIdentifier", namespaces=ns).text
        NumNotices2methode[NumNot].append("Actualisation ARK")
    return nv_ark

#nettoyage des chaines de caractères (titres, auteurs, isbn) : suppression ponctuation, espaces (pour les titres et ISBN) et diacritiques
def nettoyage(string,remplacerEspaces=True,remplacerTirets=True):
    string = unidecode(string.lower())
    for signe in ponctuation:
        string = string.replace(signe,"")
    string = string.replace("'"," ")
    if (remplacerEspaces == True):
        string = string.replace(" ","")
    if (remplacerTirets == True):
        string = string.replace("-","")
    return string

def nettoyageTitrePourControle(titre):
    titre = nettoyage(titre,True)
    return titre
    
def nettoyageTitrePourRecherche(titre):
    titre = nettoyage(titre,False)
    titre = nettoyageAuteur(titre,False)
    return titre
    

def nettoyageIsbnPourControle(isbn):
    isbn = nettoyage(isbn)
    if (len(isbn) < 10):
        isbn = ""
    elif (isbn[0:3] == "978" or isbn[0:3] == "979"):
        isbn = isbn[3:12]
    else:
        isbn = isbn[0:10]
    return isbn

def nettoyageAuteur(auteur,justeunmot=True):
    listeMots = ["par","avec","by","Mr.","M.","Mme","Mrs"]
    for mot in listeMots:
        auteur = auteur.replace(mot,"")
    for chiffre in listeChiffres:
        auteur = auteur.replace(chiffre,"")
    auteur = nettoyage(auteur.lower(),False)
    auteur = auteur.split(" ")
    auteur = sorted(auteur,key=len,reverse=True)
    auteur = [auteur1 for auteur1 in auteur if len(auteur1) > 1]
    if (auteur is not None and auteur != []):
        if (justeunmot==True):
            auteur = auteur[0]
        else:
            auteur = " ".join(auteur)
    else:
        auteur = ""
    return auteur

def nettoyageDate(date):
    date = unidecode(date.lower())
    for lettre in lettres:
        date.replace(lettre,"")
    for signe in ponctuation:
        date = date.split(signe)
        date = " ".join(annee for annee in date if annee != "")
    return date
    
    

#Si la recherche NNB avec comporaison Mots du titre n'a rien donné, on recherche sur N° interne BnF + Auteur (en ne gardant que le mot le plus long du champ Auteur)
def relancerNNBAuteur(NumNot,systemid,isbn,titre,auteur,date):
    listeArk = []
    if (auteur != "" and auteur is not None):
        urlSRU = "http://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query=bib.author%20all%20%22" + urllib.parse.quote(auteur) + "%22and%20bib.otherid%20all%20%22" + systemid + "%22&recordSchema=unimarcxchange&maximumRecords=1000&startRecord=1"
        pageSRU = etree.parse(urlSRU)
        for record in pageSRU.xpath("//srw:records/srw:record", namespaces=ns):
            ark = record.find("srw:recordIdentifier", namespaces=ns).text
            NumNotices2methode[NumNot].append("N° sys FRBNF + Auteur")
            listeArk.append(ark)
    listeArk = ",".join(listeArk)
    return listeArk
        
    

#Quand on a trouvé l'ancien numéro système dans une notice BnF : 
#on compare l'ISBN de la notice de la Bibliothèque avec celui de la BnF pour voir si ça colle
#à défaut, on compare les titres (puis demi-titres)
def comparerBibBnf(NumNot,ark_current,systemid,isbn,titre,auteur,date):
    ark = ""
    recordBNF = etree.parse("http://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query=bib.ark%20all%20%22" + urllib.parse.quote(ark_current) + "%22&recordSchema=unimarcxchange&maximumRecords=20&startRecord=1")
    ark =  comparaisonIsbn(NumNot,ark_current,systemid,isbn,titre,auteur,date,recordBNF)
    if (ark == ""):
        ark = comparaisonTitres(NumNot,ark_current,systemid,isbn,titre,auteur,date,recordBNF)
    return ark

def comparaisonIsbn(NumNot,ark_current,systemid,isbn,titre,auteur,date,recordBNF):
    ark = ""
    isbnBNF = ""
    if (recordBNF.find("//mxc:datafield[@tag='010']/mxc:subfield[@code='a']", namespaces=ns) is not None):
        isbnBNF = nettoyage(recordBNF.find("//mxc:datafield[@tag='010']/mxc:subfield[@code='a']", namespaces=ns).text)
    if (isbn != "" and isbnBNF != ""):
        if (isbn in isbnBNF):
            ark = ark_current
            NumNotices2methode[NumNot].append("N° sys FRBNF + contrôle ISBN")
    return ark

def comparaisonTitres(NumNot,ark_current,systemid,isbn,titre,auteur,date,recordBNF):
    ark = ""
    titreBNF = ""
    if (recordBNF.find("//mxc:datafield[@tag='200']/mxc:subfield[@code='a']", namespaces=ns) is not None):
        if (recordBNF.find("//mxc:datafield[@tag='200']/mxc:subfield[@code='a']", namespaces=ns).text is not None):
            titreBNF = nettoyage(recordBNF.find("//mxc:datafield[@tag='200']/mxc:subfield[@code='a']", namespaces=ns).text)
    if (titre != "" and titreBNF != ""):
        if (titre == titreBNF):
            ark = ark_current
            NumNotices2methode[NumNot].append("N° sys FRBNF ou Titre-Auteur-Date + contrôle Titre")
            if (len(titre) < 5):
                ark += "[titre court]"
        elif(titre[0:round(len(titre)/2)] == titreBNF[0:round(len(titre)/2)]):
            ark = ark_current
            NumNotices2methode[NumNot].append("N° sys FRBNF ou Titre-Auteur-Date + contrôle Titre")
            if (round(len(titre)/2)<10):
                ark += "[demi-titre" + "-" + str(round(len(titre)/2)) + "caractères]"
        elif(titre.find(titreBNF) > -1):
            NumNotices2methode[NumNot].append("N° sys FRBNF ou Titre-Auteur-Date + contrôle Titre BNF contenu dans titre initial")
            ark = ark_current
        elif (titreBNF.find(titre) > -1):
            NumNotices2methode[NumNot].append("N° sys FRBNF ou Titre-Auteur-Date + contrôle Titre initial contenu dans titre BNF")
            ark = ark_current
    return ark
            
    

#Recherche par n° système. Si le 3e paramètre est "False", c'est qu'on a pris uniquement le FRBNF initial, sans le tronquer. 
#Dans ce cas, et si 0 résultat pertinent, on relance la recherche avec info tronqué
def systemid2ark(NumNot,systemid,tronque,isbn,titre,auteur,date):
    url = "http://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query=bib.otherid%20all%20%22" + systemid + "%22&recordSchema=intermarcxchange&maximumRecords=1000&startRecord=1"
    #url = "http://catalogueservice.bnf.fr/SRU?version=1.2&operation=searchRetrieve&query=NumNotice%20any%20%22" + systemid + "%22&recordSchema=InterXMarc_Complet&maximumRecords=1000&startRecord=1"
    page = etree.parse(url)
    listeARK = []
    for record in page.xpath("//srw:records/srw:record", namespaces=ns):
        ark_current = record.find("srw:recordIdentifier",namespaces=ns).text
        for zone9XX in record.xpath("srw:recordData/mxc:record/mxc:datafield", namespaces=ns):
            #print(ark_current)
            tag = zone9XX.get("tag")
            if (tag[0:1] =="9"):
                if (zone9XX.find("mxc:subfield[@code='a']", namespaces=ns) is not None):
                    if (zone9XX.find("mxc:subfield[@code='a']", namespaces=ns).text is not None):
                        if (zone9XX.find("mxc:subfield[@code='a']", namespaces=ns).text == systemid):
                            #print(zone9XX.get("tag"))
                            listeARK.append(comparerBibBnf(NumNot,ark_current,systemid,isbn,titre,auteur,date))
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

def rechercheNNB(NumNot,nnb,isbn,titre,auteur,date):
    ark = ""
    if (nnb.isdigit() is False):
        #pb_frbnf_source.write("\t".join[NumNot,nnb] + "\n")
        ark = "Pb FRBNF"
    elif (int(nnb) > 30000000 and int(nnb) < 50000000):
        url = "http://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query=bib.recordid%20any%20%22" + nnb + "%22&recordSchema=unimarcxchange&maximumRecords=1000&startRecord=1"
        page = etree.parse(url)
        for record in page.xpath("//srw:records/srw:record", namespaces=ns):
            ark_current = record.find("srw:recordIdentifier",namespaces=ns).text
            ark = comparerBibBnf(NumNot,ark_current,nnb,isbn,titre,auteur,date)
    return ark

#Si le FRBNF n'a pas été trouvé, on le recherche comme numéro système -> pour ça on extrait le n° système
def oldfrbnf2ark(NumNot,frbnf,isbn,titre,auteur,date):
    systemid = ""
    if (frbnf[0:5].upper() == "FRBNF"):
        systemid = frbnf[5:14]
    else:
        systemid = frbnf[4:13]
    ark = rechercheNNB(NumNot,systemid[0:8],isbn,titre,auteur,date)
    if (ark==""):
        ark = systemid2ark(NumNot,systemid,False,isbn,titre,auteur,date)
    return ark


#Rechercher le FRBNF avec le préfixe    
def frbnf2ark(NumNot,frbnf,isbn,titre,auteur,date):
    url = "http://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query=bib.otherid%20all%20%22" + frbnf + "%22&recordSchema=unimarcxchange&maximumRecords=1000&startRecord=1"
    page = etree.parse(url)
    nb_resultats = int(page.find("//srw:numberOfRecords", namespaces=ns).text)
    ark = ""
    if (nb_resultats == 0):
        ark = oldfrbnf2ark(NumNot,frbnf,isbn,titre,auteur,date)
    elif (nb_resultats == 1):
        ark = page.find("//srw:recordIdentifier", namespaces=ns).text
        NumNotices2methode[NumNot].append("FRBNF")
    else:
        ark = ",".join([ark.text for ark in page.xpath("//srw:recordIdentifier", namespaces=ns)])
    return ark

        
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
        
def nettoyage_isbn(isbn):
    isbn_nett = isbn.split(";")[0].split(",")[0]
    isbn_nett = isbn_nett.replace("-","").replace(" ","")
    return isbn_nett
    
def conversionIsbn(isbn):
    longueur = len(isbn)
    isbnConverti = ""
    if (longueur == 10):
        isbnConverti == conversionIsbn1013(isbn)
    elif (longueur == 13):
        isbnConverti == conversionIsbn1310(isbn)    
    return isbnConverti

#conversion isbn13 en isbn10
def conversionIsbn1310(isbn):
    if (isbn[0:3] == "978"):
        prefix = isbn[3:-1]
        check = check_digit_10(prefix)
        return prefix + check
    else:
        return ""

#conversion isbn10 en isbn13
def conversionIsbn1013(isbn):
    prefix = '978' + isbn[:-1]
    check = check_digit_13(prefix)
    return prefix + check
    
def check_digit_10(isbn):
    assert len(isbn) == 9
    sum = 0
    for i in range(len(isbn)):
        c = int(isbn[i])
        w = i + 1
        sum += w * c
    r = sum % 11
    if (r == 10):
        return 'X'
    else: 
        return str(r)

def check_digit_13(isbn):
    assert len(isbn) == 12
    sum = 0
    for i in range(len(isbn)):
        c = int(isbn[i])
        if (i % 2):
            w = 3
        else: 
            w = 1
        sum += w * c
    r = 10 - (sum % 10)
    if (r == 10):
        return '0'
    else:
        return str(r)

def isbn2sru(NumNot,isbn,titre,auteur,date):
    urlSRU = "http://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query=bib.isbn%20all%20%22" + isbn + "%22"
    resultats = etree.parse(urlSRU)
    listeARK = []
    for record in resultats.xpath("//srw:record", namespaces=ns):
        ark_current = record.find("srw:recordIdentifier", namespaces=ns).text
        recordBNF = etree.parse("http://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query=bib.ark%20all%20%22" + urllib.parse.quote(ark_current) + "%22&recordSchema=unimarcxchange&maximumRecords=20&startRecord=1")
        ark = comparaisonTitres(NumNot,ark_current,"",isbn,titre,auteur,date,recordBNF)
        NumNotices2methode[NumNot].append("ISBN > ARK")
        listeARK.append(ark)
    listeARK = ",".join([ark for ark in listeARK if ark != ""])
    return listeARK

#Si l'ISBN n'a été trouvé ni dans l'index ISBN, ni dans l'index EAN
#on le recherche dans tous les champs (not. les données d'exemplaires, pour des 
#réimpressions achetées par un département de la Direction des collections de la BnF)
def isbn_anywhere2sru(NumNot,isbn,titre,auteur,date):
    urlSRU = "http://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query=bib.anywhere%20all%20%22" + isbn + "%22"
    resultats = etree.parse(urlSRU)
    listeARK = []
    for record in resultats.xpath("//srw:record", namespaces=ns):
        ark_current = record.find("srw:recordIdentifier", namespaces=ns).text
        recordBNF = etree.parse("http://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query=bib.ark%20all%20%22" + urllib.parse.quote(ark_current) + "%22&recordSchema=unimarcxchange&maximumRecords=20&startRecord=1")
        ark = comparaisonTitres(NumNot,ark_current,"",isbn,titre,auteur,date,recordBNF)
        NumNotices2methode[NumNot].append("ISBN anywhere > ARK")
        listeARK.append(ark)
    listeARK = ",".join([ark for ark in listeARK if ark != ""])
    return listeARK




def isbn2sudoc(NumNot,isbn,isbnConverti,titre,auteur):
    url = "https://www.sudoc.fr/services/isbn2ppn/" + isbn
    Listeppn = []

    #page = etree.parse(url)
    isbnTrouve = True
    ark = ""
    try:
        request.urlretrieve(url)
    except error.HTTPError as err:
        isbnTrouve = False
    if (isbnTrouve == True):
        resultats = etree.parse(request.urlopen(url))
        for ppn in resultats.xpath("//ppn"):
            ppn_val = resultats.find("//ppn").text
            Listeppn.append("PPN" + ppn_val)
            ark = ppn2ark(NumNot,ppn_val,isbn,titre,auteur)
        if (ark == ""):
            url = "https://www.sudoc.fr/services/isbn2ppn/" + isbnConverti
            try:
                request.urlretrieve(url)
            except error.HTTPError as err:
                isbnTrouve = False
            if (isbnTrouve == True):
                resultats = etree.parse(request.urlopen(url))
                for ppn in resultats.xpath("//ppn"):
                    ppn_val = resultats.find("//ppn").text
                    Listeppn.append("PPN" + ppn_val)
                    ark = ppn2ark(NumNot,ppn_val,isbnConverti,titre,auteur)
    #Si on trouve un PPN, on ouvre la notice pour voir s'il n'y a pas un ARK déclaré comme équivalent --> dans ce cas on récupère l'ARK
    Listeppn = ",".join(Listeppn)
    if (ark != ""):
        return ark
    else:
        return Listeppn

def ppn2ark(NumNot,ppn,isbn,titre,auteur):
    record = etree.parse(request.urlopen("http://www.sudoc.fr/" + ppn + ".rdf" ))
    ark = ""
    for sameAs in record.xpath("//owl:sameAs",namespaces=nsSudoc):
        resource = sameAs.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource")
        if (resource.find("ark:/12148/")>0):
            ark = resource[24:46]
            NumNotices2methode[NumNot].append("ISBN > PPN > ARK")
    if (ark == ""):
        for frbnf in record.xpath("//bnf-onto:FRBNF",namespaces=nsSudoc):
            frbnf_val = frbnf.text
            NumNotices2methode[NumNot].append("ISBN > PPN > FRBNF > ARK")
            ark = frbnf2ark(NumNot,frbnf_val,isbn,titre,auteur)
    return ark
  

def isbn2ark(NumNot,isbn,titre,auteur,date):
    #Requête sur l'ISBN dans le SRU, avec contrôle sur Titre ou auteur
    resultatsIsbn2ARK = isbn2sru(NumNot,isbn,titre,auteur,date)

    isbnConverti = conversionIsbn(isbn)
#Si pas de résultats : on convertit l'ISBN en 10 ou 13 et on relance une recherche dans le catalogue BnF
    if (resultatsIsbn2ARK == ""):
        resultatsIsbn2ARK = isbn2sru(NumNot,isbnConverti,titre,auteur,date)

#Si pas de résultats et ISBN 13 : on recherche sur EAN
    if (resultatsIsbn2ARK == "" and len(isbn)==13):
        resultatsIsbn2ARK = ean2ark(NumNot,isbn,titre,auteur,date)
    if (resultatsIsbn2ARK == "" and len(isbnConverti) == 13):
        resultatsIsbn2ARK = ean2ark(NumNot,isbnConverti,titre,auteur,date)

#Si pas de résultats et ISBN 13 : on recherche l'ISBN dans tous les champs (dont les données d'exemplaire)
    if (resultatsIsbn2ARK == ""):
        resultatsIsbn2ARK = isbn_anywhere2ark(NumNot,isbn,titre,auteur,date)
    if (resultatsIsbn2ARK == "" and len(isbnConverti) == 13):
        resultatsIsbn2ARK = isbn_anywhere2ark(NumNot,isbnConverti,titre,auteur,date)



#Si pas de résultats : on relance une recherche dans le Sudoc    
    if (resultatsIsbn2ARK == ""):
        resultatsIsbn2ARK = isbn2sudoc(NumNot,isbn,isbnConverti,titre,auteur)
    return resultatsIsbn2ARK

def ark2metas(ark):
    record = etree.parse("http://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query=bib.ark%20any%20%22" + urllib.parse.quote(ark) + "%22&recordSchema=unimarcxchange&maximumRecords=20&startRecord=1")
    titre = ""
    premierauteurPrenom = ""
    premierauteurNom = ""
    tousauteurs = ""
    if (record.find("//mxc:datafield[@tag='200']/mxc:subfield[@code='a']", namespaces=ns) is not None):
        titre = unidecode(record.find("//mxc:datafield[@tag='200']/mxc:subfield[@code='a']", namespaces=ns).text)
    if (record.find("//mxc:datafield[@tag='200']/mxc:subfield[@code='e']", namespaces=ns) is not None):
        titre = titre + ", " + unidecode(record.find("//mxc:datafield[@tag='200']/mxc:subfield[@code='e']", namespaces=ns).text)
    if (record.find("//mxc:datafield[@tag='700']/mxc:subfield[@code='a']", namespaces=ns) is not None):
        premierauteurNom = unidecode(record.find("//mxc:datafield[@tag='700']/mxc:subfield[@code='a']", namespaces=ns).text)
    if (record.find("//mxc:datafield[@tag='700']/mxc:subfield[@code='m']", namespaces=ns) is not None):
        premierauteurPrenom = unidecode(record.find("//mxc:datafield[@tag='700']/mxc:subfield[@code='m']", namespaces=ns).text)
    if (premierauteurNom  == ""):
        if (record.find("//mxc:datafield[@tag='710']/mxc:subfield[@code='a']", namespaces=ns) is not None):
            premierauteurNom = unidecode(record.find("//mxc:datafield[@tag='700']/mxc:subfield[@code='a']", namespaces=ns).text)
    if (record.find("//mxc:datafield[@tag='200']/mxc:subfield[@code='f']", namespaces=ns) is not None):
        tousauteurs = unidecode(record.find("//mxc:datafield[@tag='200']/mxc:subfield[@code='f']", namespaces=ns).text)

    return [titre,premierauteurPrenom,premierauteurNom,tousauteurs]
    
def ppn2metas(ppn):
    record = etree.parse(request.urlopen("https://www.sudoc.fr/" + ppn + ".rdf"))
    titre = ""
    premierauteurPrenom = ""
    premierauteurNom = ""
    tousauteurs = ""
    if (record.find("//dc:title",namespaces=nsSudoc) is not None):
        titre = unidecode(record.find("//dc:title",namespaces=nsSudoc).text).split("[")[0].split("/")[0]
        tousauteurs = unidecode(record.find("//dc:title",namespaces=nsSudoc).text).split("/")[1]
        if (titre[0:5] == tousauteurs[0:5]):
            tousauteurs = ""
    if (record.find("//marcrel:aut/foaf:Person/foaf:name",namespaces=nsSudoc) is not None):
        premierauteurNom = unidecode(record.find("//marcrel:aut/foaf:Person/foaf:name",namespaces=nsSudoc).text).split(",")[0]
        if (record.find("//marcrel:aut/foaf:Person/foaf:name",namespaces=nsSudoc).text.find(",") > 0):
            premierauteurPrenom = unidecode(record.find("//marcrel:aut/foaf:Person/foaf:name",namespaces=nsSudoc).text).split(",")[1]
        if (premierauteurPrenom.find("(") > 0):
            premierauteurPrenom = premierauteurPrenom.split("(")[0]
    return [titre,premierauteurPrenom,premierauteurNom,tousauteurs]
  
def tad2ark(NumNot,titre,auteur,auteur_nett,date_nett,anywhere=False):
#En entrée : le numéro de notice, le titre (qu'il faut nettoyer pour la recherche)
#L'auteur = zone auteur initiale, ou à défaut auteur_nett
#date_nett
    ark = []
    titre_propre = nettoyageTitrePourRecherche(titre)
    #print("titre propre : " + titre_propre)
    if (titre_propre != ""):
        if (auteur == ""):
            auteur = "-"
        if (date_nett == ""):
            date_nett = "-"
        if (auteur_nett == ""):
            auteur_nett = "-"
        url = "http://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query=bib.title%20all%20%22" + urllib.parse.quote(titre_propre) + "%22%20and%20bib.author%20all%20%22" + urllib.parse.quote(auteur) + "%22%20and%20bib.date%20all%20%22" + urllib.parse.quote(date_nett) + "%22&recordSchema=unimarcxchange&maximumRecords=20&startRecord=1"
        if (anywhere == True):
            url = "http://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query=bib.anywhere%20all%20%22" + urllib.parse.quote(titre_propre) + "%20" + urllib.parse.quote(auteur) + "%20" + urllib.parse.quote(date_nett) + "%22&recordSchema=unimarcxchange&maximumRecords=20&startRecord=1"
        #print(url)
        results = etree.parse(url)
        if (results.find("//srw:numberOfRecords", namespaces=ns) == "0"):
            url = "http://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query=bib.title%20all%20%22" + urllib.parse.quote(titre_propre) + "%22%20and%20bib.author%20all%20%22" + urllib.parse.quote(auteur_nett) + "%22%20and%20bib.date%20all%20%22" + urllib.parse.quote(date_nett) + "%22&recordSchema=unimarcxchange&maximumRecords=20&startRecord=1"
            if (anywhere == True):
                url = "http://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query=bib.anywhere%20all%20%22" + urllib.parse.quote(titre_propre) + "%20" + urllib.parse.quote(auteur_nett) + "%20" + urllib.parse.quote(date_nett) + "%22&recordSchema=unimarcxchange&maximumRecords=20&startRecord=1"
            results = etree.parse(url)
        for record in results.xpath("//srw:recordIdentifier",namespaces=ns):
            ark_current = record.text
            #print(NumNot + " : " + ark_current)
            recordBNF = etree.parse("http://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query=bib.ark%20all%20%22" + urllib.parse.quote(ark_current) + "%22&recordSchema=unimarcxchange&maximumRecords=20&startRecord=1")
            ark.append(comparaisonTitres(NumNot,ark_current,"","",nettoyageTitrePourControle(titre),auteur,date_nett,recordBNF))
            methode = "Titre-Auteur-Date"
            if (auteur == "-" and date_nett == "-"):
                methode = "Titre"
            elif (auteur == "-"):
                methode = "Titre-Date"
            elif (date_nett == "-"):
                methode = "Titre-Auteur"
            NumNotices2methode[NumNot].append(methode)
    ark = ",".join([ark1 for ark1 in ark if ark1 != ""])
    return ark

def extract_meta(recordBNF,field_subfield,occ="all",anl=False):
    assert field_subfield.find("$") == 3
    assert len(field_subfield) == 5
    field = field_subfield.split("$")[0]
    subfield = field_subfield.split("$")[1]
    value = []
    path = "//srw:recordData/mxc:record/mxc:datafield[@tag='" + field + "']/mxc:subfield[@code='"+ subfield + "']"
    for elem in recordBNF.xpath(path,namespaces = ns):
        if (elem.text is not None):
            value.append(elem.text)
    if (occ == "first"):
        value = value[0]
    elif (occ == "all"):
        value = " ".join(value)
    return value

def url_requete_sru(query,recordSchema="unimarcxchange",maximumRecords="1000",startRecord="1"):
    url = "http://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query="
    + urllib.parse.quote(query) 
    + "&recordSchema=" + recordSchema 
    + "&maximumRecords=" + maximumRecords
    + "&startRecord=" + startRecord
    return url


def ark2recordBNF(ark,typeRecord="bib"):
    url = url_requete_sru(typeRecord + '.ark any "' + ark + '"')
    recordBNF = etree.parse(url)
    return recordBNF

def ean2ark(NumNot,ean,titre,auteur,date):
    listeARK = []
    url = url_requete_sru('bib.ean all "' + ean + '"')
    results = etree.parse(url)
    for record in results.xpath("//srw:recordData",namespaces=ns):
        ark_current = record.find("srw:recordIdentifier",namespaces=ns).text
        recordBNF = ark2recordBNF(ark_current)
        ark = comparaisonTitres(NumNot,ark_current,"",ean,titre,auteur,date,recordBNF)
        NumNotices2methode[NumNot].append("EAN > ARK")
        listeARK.append(ark)
    listeARK = ",".join([ark for ark in listeARK if ark != ""])
    return listeARK

def nettoyage_no_commercial(no_commercial_propre):
    return no_commercial_propre
            
def no_commercial2ark(NumNot,no_commercial,titre,auteur,date):
    url = url_requete_sru('bib.anywhere  all "' + no_commercial + '"')
    results = etree.parse(url)
    for record in results.xpath("//srw:recordData",namespaces=ns):
        ark_current = record.find("srw:recordIdentifier",namespaces=ns).text
        recordBNF = ark2recordBNF(ark_current)
        ark = controleNoCommercial(NumNot,ark_current,no_commercial,titre,auteur,date,recordBNF)
    ark = ""
    return ark

def controleNoCommercial(NumNot,ark_current,no_commercial,titre,auteur,date,recordBNF):
    ark = ""
    no_commercialBNF = nettoyage_no_commercial(extract_meta(recordBNF,"071$a"))
    if (no_commercial != "" and no_commercialBNF != ""):
        if (no_commercial in no_commercialBNF):
            ark = ark_current
            NumNotices2methode[NumNot].append("N° sys FRBNF + contrôle No commercial")
        elif (no_commercialBNF in no_commercial):
            ark = ark_current
            NumNotices2methode[NumNot].append("N° sys FRBNF + contrôle No commercial")
    return ark


def monimpr(master, entry_filename, type_doc, file_nb, id_traitement, liste_reports):
    
    with open(entry_filename, newline='\n',encoding="utf-8") as csvfile:
        entry_file = csv.reader(csvfile, delimiter='\t')
        next(entry_file)
        for row in entry_file:
            #print(row)
            NumNot = row[0]
            frbnf = row[1]
            current_ark = row[2]
            isbn = row[3]
            isbn_nett = nettoyageIsbnPourControle(isbn)
            isbn_propre = nettoyage_isbn(isbn)
            ean = row[4]
            ean_nett = nettoyageIsbnPourControle(ean)
            ean_propre = nettoyage_isbn(ean)
            titre = row[5]
            titre_nett= nettoyageTitrePourControle(titre)
            auteur = row[6]
            auteur_nett = nettoyageAuteur(auteur)
            date = row[7]
            date_nett = nettoyageDate(date)
            #Actualisation de l'ARK à partir de l'ARK
            ark = ""
            if (current_ark != ""):
                ark = ark2ark(NumNot,current_ark)
            
            #A défaut, recherche de l'ARK à partir du FRBNF (+ contrôles sur ISBN, ou Titre, ou Auteur)
            elif (frbnf != ""):
                ark = frbnf2ark(NumNot,frbnf,isbn_nett,titre_nett,auteur_nett,date_nett)
                ark = ",".join([ark1 for ark1 in ark.split(",") if ark1 != ''])
            #A défaut, recherche sur ISBN
            #Si plusieurs résultats, contrôle sur l'auteur
            if (ark == "" and isbn_nett != ""):
                ark = isbn2ark(NumNot,isbn_propre,titre_nett,auteur_nett,date_nett)
            #A défaut, recherche sur EAN
            if (ark == "" and ean != ""):
                ark = ean2ark(NumNot,ean_propre,titre_nett,auteur_nett,date_nett)
            #A défaut, recherche sur Titre-Auteur-Date
            
            #A défaut, recherche sur Titre-Auteur-Date
            if (ark == "" and titre != ""):
                ark = tad2ark(NumNot,titre,auteur,auteur_nett,date_nett,False)
                #print("1." + NumNot + " : " + ark)
                """print(titre)
                print(titre_nett)
                print(auteur)
                print(auteur_nett)
                print(date)
                print(date_nett)"""
            if (ark == "" and titre != ""):
                ark = tad2ark(NumNot,titre,auteur,auteur_nett,date_nett,True)
            print(NumNot + " : " + ark)
            nbARK = len(ark.split(","))
            if (ark == ""):
                nbARK = 0   
            if (ark == "Pb FRBNF"):
                nb_notices_nb_ARK["Pb FRBNF"] += 1
            else:
                nb_notices_nb_ARK[nbARK] += 1
            liste_metadonnees = [nbARK,NumNot,ark,frbnf,current_ark,isbn_nett,ean_propre,titre_nett,auteur_nett,date_nett]
            if (file_nb.get() ==  1):
                row2file(liste_metadonnees,liste_reports)
            elif(file_nb.get() ==  2):
                row2files(liste_metadonnees,liste_reports)
        
        
def cddvd(master, entry_filename, type_doc, file_nb, id_traitement, liste_reports):
    
    #results2file(nb_fichiers_a_produire)
    
    with open(entry_filename, newline='\n',encoding="utf-8") as csvfile:
        entry_file = csv.reader(csvfile, delimiter='\t')
        next(entry_file)
        for row in entry_file:
            #print(row)
            NumNot = row[0]
            frbnf = row[1]
            current_ark = row[2]
            ean = row[3]
            ean_nett = nettoyageIsbnPourControle(ean)
            ean_propre = nettoyage_isbn(ean)
            no_commercial = row[4]
            no_commercial_propre = nettoyage_no_commercial(no_commercial)
            titre = row[5]
            titre_nett= nettoyageTitrePourControle(titre)
            auteur = row[6]
            auteur_nett = nettoyageAuteur(auteur)
            date = row[7]
            date_nett = nettoyageDate(date)
            #Actualisation de l'ARK à partir de l'ARK
            ark = ""
            if (current_ark != ""):
                ark = ark2ark(NumNot,current_ark)
            
            #A défaut, recherche de l'ARK à partir du FRBNF (+ contrôles sur ISBN, ou Titre, ou Auteur)
            elif (frbnf != ""):
                ark = frbnf2ark(NumNot,frbnf,ean_nett,titre_nett,auteur_nett,date_nett)
                ark = ",".join([ark1 for ark1 in ark.split(",") if ark1 != ''])
            #A défaut, recherche sur EAN
            #Si plusieurs résultats, contrôle sur l'auteur
            if (ark == "" and ean_nett != ""):
                ark = ean2ark(NumNot,ean_propre,titre_nett,auteur_nett,date_nett)
            #A défaut, recherche sur no_commercial
            if (ark == "" and no_commercial != ""):
                ark = no_commercial2ark(NumNot,no_commercial_propre,titre_nett,auteur_nett,date_nett)
                
            #A défaut, recherche sur Titre-Auteur-Date
            if (ark == "" and titre != ""):
                ark = tad2ark(NumNot,titre,auteur,auteur_nett,date_nett,False)
                #print("1." + NumNot + " : " + ark)
                """print(titre)
                print(titre_nett)
                print(auteur)
                print(auteur_nett)
                print(date)
                print(date_nett)"""
            if (ark == "" and titre != ""):
                ark = tad2ark(NumNot,titre,auteur,auteur_nett,date_nett,True)
            print(NumNot + " : " + ark)
            nbARK = len(ark.split(","))
            if (ark == ""):
                nbARK = 0   
            if (ark == "Pb FRBNF"):
                nb_notices_nb_ARK["Pb FRBNF"] += 1
            else:
                nb_notices_nb_ARK[nbARK] += 1
            liste_metadonnees = [nbARK,NumNot,ark,frbnf,current_ark,ean_nett,ean_propre,
                         no_commercial_propre,titre_nett,auteur_nett,date_nett]
            if (file_nb.get() ==  1):
                row2file(liste_metadonnees,liste_reports)
            elif(file_nb.get() ==  2):
                row2files(liste_metadonnees,liste_reports)
        
    

def launch(master, entry_filename, type_doc, file_nb, id_traitement):
    
    #results2file(nb_fichiers_a_produire)

    liste_reports = create_reports(id_traitement.get(), file_nb.get())    
    
    if (type_doc.get() == 1):
        monimpr(master, entry_filename.get(), type_doc, file_nb, id_traitement, liste_reports)
    elif (type_doc.get() == 2):
        cddvd(master, entry_filename.get(), type_doc, file_nb, id_traitement, liste_reports)
    else:
        print("Erreur : type de document non reconnu")
    
    fin_traitements(master,liste_reports)


def fin_traitements(master,liste_reports):
    stats_extraction(liste_reports)
    typesConversionARK(liste_reports)
    print("Programme terminé")
    master.destroy()



def stats_extraction(liste_reports):
    #print(nb_notices_nb_ARK)
    for key in nb_notices_nb_ARK:
        liste_reports[-2].write(str(key) + "\t" + str(nb_notices_nb_ARK[key]) + "\n")
    if ("Pb FRBNF" in nb_notices_nb_ARK):
        nb_notices_nb_ARK[-1] = nb_notices_nb_ARK.pop('Pb FRBNF')
    """plt.bar(list(nb_notices_nb_ARK.keys()), nb_notices_nb_ARK.values(), color='skyblue')
    plt.show()"""

def typesConversionARK(liste_reports):
    for key in NumNotices2methode:
        value = " / ".join(NumNotices2methode[key])
        liste_reports[-1].write(key + "\t" + value + "\n")

def click2help():
    url = "https://github.com/Lully/transbiblio"
    webbrowser.open_new(url)

def annuler(master):
    master.destroy()
    
def check_access_to_network():
    access_to_network = True
    try:
        request.urlopen("http://www.bnf.fr")
    except error.URLError:
        print("Pas de réseau internet")
        access_to_network = False
    return access_to_network


def check_last_compilation(programID):
    programID_last_compilation = 0
    display_update_button = False
    url = "https://raw.githubusercontent.com/Lully/bnf-sru/master/last_compilations.json"
    last_compilations = request.urlopen(url)
    reader = codecs.getreader("utf-8")
    last_compilations = json.load(reader(last_compilations))["last_compilations"][0]
    if (programID in last_compilations):
        programID_last_compilation = last_compilations[programID]
    if (programID_last_compilation > version):
        display_update_button = True
    return [programID_last_compilation,display_update_button]

#La vérification de la dernière version n'est faite que si le programme est lancé en standalone
#last_version = [0,False]

def download_last_update():
    url = "https://github.com/Lully/transbiblio/blob/master/noticesbib2arkBnF.py"
    webbrowser.open(url)
#==============================================================================
# Création de la boîte de dialogue
#==============================================================================

def formulaire_noticesbib2arkBnF(access_to_network=True, last_version=[0,False]):
    couleur_fond = "white"
    couleur_bouton = "#acacac"
    
    master = tk.Tk()
    master.config(padx=30, pady=20,bg=couleur_fond)
    master.title("Programme d'alignement de données bibliographiques avec la BnF")
    master.iconbitmap(r'favicon.ico')
    
    zone_alert_explications = tk.Frame(master, bg=couleur_fond, pady=10)
    zone_alert_explications.pack()
    
    zone_formulaire = tk.Frame(master, bg=couleur_fond)
    zone_formulaire.pack()
    zone_commentaires = tk.Frame(master, bg=couleur_fond, pady=10)
    zone_commentaires.pack()
    
    cadre_input = tk.Frame(zone_formulaire, highlightthickness=2, highlightbackground=couleur_bouton, relief="groove", height=150, padx=10,bg=couleur_fond)
    cadre_input.pack(side="left")
    cadre_input_header = tk.Frame(cadre_input,bg=couleur_fond)
    cadre_input_header.pack(anchor="w")
    cadre_input_file = tk.Frame(cadre_input,bg=couleur_fond)
    cadre_input_file.pack(anchor="w")
    cadre_input_infos_format = tk.Frame(cadre_input,bg=couleur_fond)
    cadre_input_infos_format.pack(anchor="w")
    cadre_input_type_docs = tk.Frame(cadre_input,bg=couleur_fond)
    cadre_input_type_docs.pack(anchor="w")
    
    cadre_inter = tk.Frame(master, borderwidth=0, padx=10,bg=couleur_fond)
    cadre_inter.pack(side="left")
    tk.Label(cadre_inter, text=" ",bg=couleur_fond).pack()
    
    cadre_output = tk.Frame(zone_formulaire, highlightthickness=2, highlightbackground=couleur_bouton, relief="groove", height=150, padx=10,bg=couleur_fond)
    cadre_output.pack(side="left", anchor="w")
    cadre_output_header = tk.Frame(cadre_output,bg=couleur_fond)
    cadre_output_header.pack(anchor="w")
    cadre_output_nb_fichier = tk.Frame(cadre_output,bg=couleur_fond)
    cadre_output_nb_fichier.pack(side="left", anchor="w")
    cadre_output_id_traitement = tk.Frame(cadre_output, padx=20,bg=couleur_fond)
    cadre_output_id_traitement.pack(side="left", anchor="w")
    
    cadre_valider = tk.Frame(zone_formulaire, borderwidth=0, relief="groove", height=150, padx=10,bg=couleur_fond)
    cadre_valider.pack(side="left")
    
    if (access_to_network == False):
        tk.Label(zone_alert_explications, text=errors["no_internet"], 
             bg=couleur_fond,  fg="red").pack()
    tk.Label(zone_alert_explications, text="Attention : format MON IMPR avec une colonne supplémentaire en entrée (EAN)", 
             bg=couleur_fond,  fg="red").pack()
    
    #définition input URL (u)
    tk.Label(cadre_input_header,bg=couleur_fond, fg=couleur_bouton, text="En entrée :", justify="left", font="bold").pack()
    
    tk.Label(cadre_input_file,bg=couleur_fond, text="Fichier contenant les notices : ").pack(side="left")
    entry_filename = tk.Entry(cadre_input_file, width=40, bd=2)
    entry_filename.pack(side="left")
    entry_filename.focus_set()
    
    tk.Label(cadre_input_infos_format,bg=couleur_fond, text="Séparateur TAB, Encodage UTF-8", justify="left").pack()
    
    
    tk.Label(cadre_input_type_docs,bg=couleur_fond, text="\nType de documents", anchor="w").pack(anchor="w")
    type_doc = tk.IntVar()
    tk.Radiobutton(cadre_input_type_docs,bg=couleur_fond, text="Documents imprimés (monographies)\nFormat : Num Not | FRBNF | ARK | ISBN | EAN | Titre | Auteur | Date", variable=type_doc , value=1, justify="left").pack(anchor="w")
    tk.Radiobutton(cadre_input_type_docs,bg=couleur_fond, text="Audiovisuel (CD / DVD)\nFormat : Num Not | FRBNF | ARK | EAN | N° commercial | Titre | Auteur | Date", variable=type_doc , value=2, justify="left").pack(anchor="w")
    type_doc.set(1)
    
    
    
    #Choix du format
    tk.Label(cadre_output_header,bg=couleur_fond, fg=couleur_bouton,text="En sortie :", font="bold").pack(anchor="w")
    file_nb = tk.IntVar()
    tk.Radiobutton(cadre_output_nb_fichier,bg=couleur_fond, text="1 fichier", variable=file_nb , value=1, justify="left").pack(anchor="w")
    tk.Radiobutton(cadre_output_nb_fichier,bg=couleur_fond, text="Plusieurs fichiers \n(Pb / 0 / 1 / plusieurs ARK trouvés)", justify="left", variable=file_nb , value=2).pack(anchor="w")
    file_nb.set(2)
    
    #Ajout (optionnel) d'un identifiant de traitement
    tk.Label(cadre_output_id_traitement,bg=couleur_fond, text="\n\n\n\n").pack()
    tk.Label(cadre_output_id_traitement,bg=couleur_fond, text="ID traitement (optionnel)").pack()
    id_traitement = tk.Entry(cadre_output_id_traitement, width=20, bd=2)
    id_traitement.pack()
    tk.Label(cadre_output_id_traitement,bg=couleur_fond, text="\n").pack()
    
    
    #Bouton de validation
    
    b = tk.Button(cadre_valider, bg=couleur_bouton, fg="white", font="bold", 
                  text = "OK", 
                  command = lambda: launch(master, entry_filename, type_doc, file_nb, id_traitement), borderwidth=5 ,padx=10, pady=10, width=10, height=4)
    b.pack()
    
    tk.Label(cadre_valider, font="bold", text="", bg=couleur_fond).pack()
    
    call4help = tk.Button(cadre_valider, text="Besoin d'aide ?", command=click2help, padx=10, pady=1, width=15)
    call4help.pack()
    
    cancel = tk.Button(cadre_valider, bg=couleur_fond, text="Annuler", command=lambda: annuler(master), padx=10, pady=1, width=15)
    cancel.pack()
    
    tk.Label(zone_commentaires, text = "Version " + str(version) + " - " + lastupdate, bg=couleur_fond).pack()
    
    if (last_version[1] == True):
        download_update = tk.Button(zone_commentaires, text = "Télécharger la version " + str(last_version[0]), command=download_last_update)
        download_update.pack()
    
    tk.mainloop()

if __name__ == '__main__':
    access_to_network = check_access_to_network()
    if(access_to_network is True):
        last_version = check_last_compilation(programID)
    formulaire_noticesbib2arkBnF(access_to_network,last_version)
    

