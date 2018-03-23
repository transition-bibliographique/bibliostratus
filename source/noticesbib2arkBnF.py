# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 18:30:30 2017

@author: Etienne Cavalié

Programme d'identification des ARK BnF à partir de numéros FRBNF

Reprendre à la fonction issn2ark
Puis modifier le formulaire pour proposer l'option "Périodiques"
 + définir les colonnes (date ?)

"""

from lxml import etree
from urllib import request
import urllib.parse
from unidecode import unidecode
import urllib.error as error
import csv
import tkinter as tk
from collections import defaultdict
import webbrowser
import codecs
import json
import http.client
import main as main


#import matplotlib.pyplot as plt

version = 0.92
lastupdate = "29/12/2017"
programID = "noticesbib2arkBnF"



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
    url = url_requete_sru('bib.persistentid all "' + ark + '"')
    (test,page) = testURLetreeParse(url)
    nv_ark = ""
    if (test == True):
        if (page.find("//srw:recordIdentifier", namespaces=main.ns) is not None):
            nv_ark = page.find("//srw:recordIdentifier", namespaces=main.ns).text
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
        string = string.replace("-"," ")
    return string

def nettoyageTitrePourControle(titre):
    titre = nettoyage(titre,True)
    return titre
    
def nettoyageTitrePourRecherche(titre):
    titre = nettoyage(titre,False)
    titre = titre.split(" ")
    titre = [mot for mot in titre if len(mot) > 1]
    titre = " ".join(titre)
    return titre
    
def nettoyage_lettresISBN(isbn):
    isbn = isbn.lower()
    prefix = isbn[0:-1]
    cle = isbn[-1]
    for lettre in lettres:
        prefix = prefix.replace(lettre, "")
    if (cle == "0" 
        or cle == "1" 
        or cle == "2" 
        or cle == "3" 
        or cle == "4" 
        or cle == "5"
        or cle == "6"
        or cle == "7"
        or cle == "8"
        or cle == "9"):
        cle = cle
    elif (cle == "x"):
        cle = "X"
    else:
        cle = ""
    return prefix+cle

def nettoyageIsbnPourControle(isbn):
    isbn = nettoyage(isbn).replace(" ","")
    if (isbn != ""):
        isbn = nettoyage_lettresISBN(isbn)
    if (len(isbn) < 10):
        isbn = ""
    elif (isbn[0:3] == "978" or isbn[0:3] == "979"):
        isbn = isbn[3:12]
    else:
        isbn = isbn[0:10]
    return isbn

def nettoyageIssnPourControle(issn):
    issn = nettoyage(issn).replace(" ","")
    if (issn != ""):
        issn = nettoyage_lettresISBN(issn)
    if (len(issn) < 8):
        issn = ""
    else:
        issn = issn[0:8]
    return issn

def nettoyageAuteur(auteur,justeunmot=True):
    listeMots = [" par "," avec "," by "," Mr. "," M. "," Mme "," Mrs "]
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
        date = date.replace(lettre,"")
    for signe in ponctuation:
        date = date.split(signe)
        date = " ".join(annee for annee in date if annee != "")
    return date

def nettoyageTome(numeroTome):
    if (numeroTome):
        numeroTome = unidecode(numeroTome.lower())
        for lettre in lettres:
            numeroTome = numeroTome.replace(lettre,"")
        for signe in ponctuation:
            numeroTome = numeroTome.split(signe)
            numeroTome = "~".join(numero for numero in numeroTome)
        numeroTome = numeroTome.split("~")
        numeroTome = [numero for numero in numeroTome if numero != ""]
        if (numeroTome != []):
            numeroTome = numeroTome[-1]
        numeroTome = ltrim(numeroTome)
    return numeroTome

    
def nettoyagePubPlace(pubPlace) :
    """Nettoyage du lieu de publication"""
    pubPlace = unidecode(pubPlace.lower())
    for chiffre in listeChiffres:
        pubPlace = pubPlace.replace(chiffre,"")
    for signe in ponctuation:
        pubPlace = pubPlace.split(signe)
        pubPlace = " ".join(mot for mot in pubPlace if mot != "")
    return pubPlace

#Si la recherche NNB avec comporaison Mots du titre n'a rien donné, on recherche sur N° interne BnF + Auteur (en ne gardant que le mot le plus long du champ Auteur)
def relancerNNBAuteur(NumNot,systemid,isbn,titre,auteur,date):
    listeArk = []
    if (auteur != "" and auteur is not None):
        urlSRU = url_requete_sru('bib.author all "' + auteur + '" and bib.otherid all "' + systemid + '"')
        (test,pageSRU) = testURLetreeParse(urlSRU)
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
    url = url_requete_sru('bib.persistentid all "' + ark_current + '"')
    (test,recordBNF) = testURLetreeParse(url)
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
    isbnBNF = nettoyage(main.extract_subfield(recordBNF,"010","a",1))
    if (isbnBNF == ""):
        isbnBNF = nettoyage(main.extract_subfield(recordBNF,"038","a",1))
        sourceID = "EAN"
    if (isbnBNF == ""):
        isbnBNF = nettoyage(main.extract_subfield(recordBNF,"011","a",1))
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
    if (ark == ""):
        ark = comparaisonTitres_sous_zone(NumNot,ark_current,systemid,isbn,titre,auteur,date,recordBNF,origineComparaison,"503$a")
    if (ark == ""):
        ark = comparaisonTitres_sous_zone(NumNot,ark_current,systemid,isbn,titre,auteur,date,recordBNF,origineComparaison,"503$e")
    if (ark == ""):
        ark = comparaisonTitres_sous_zone(NumNot,ark_current,systemid,isbn,titre,auteur,date,recordBNF,origineComparaison,"540$a")
    if (ark == ""):
        ark = comparaisonTitres_sous_zone(NumNot,ark_current,systemid,isbn,titre,auteur,date,recordBNF,origineComparaison,"540$e")
    if (ark == ""):
        ark = comparaisonTitres_sous_zone(NumNot,ark_current,systemid,isbn,titre,auteur,date,recordBNF,origineComparaison,"416$a")
    if (ark == ""):
        ark = comparaisonTitres_sous_zone(NumNot,ark_current,systemid,isbn,titre,auteur,date,recordBNF,origineComparaison,"225$a")
    if (ark != "" and numeroTome != ""):
        ark = verificationTomaison(ark,numeroTome,recordBNF)
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
    volumesBNF = convert_volumes_to_int(volumesBNF)
    if (volumesBNF == ""):
        volumesBNF = main.extract_subfield(recordBNF,"200","a")
        volumesBNF = convert_volumes_to_int(volumesBNF)
        for lettre in lettres:
            volumesBNF = volumesBNF.replace(lettre, "~")
        volumesBNF = volumesBNF.split("~")
        volumesBNF = set(str(ltrim(nb)) for nb in volumesBNF if nb != "")
    if (volumesBNF != "" and numeroTome in volumesBNF):
        return ark
    else:
        return ""

def verificationTomaison_sous_zone(ark,numeroTome,numeroTomeBnF):
    """Vérifie si le numéro du tome en entrée est présent dans l'extraction des nombres de la sous-zone"""
    return ark,False

def ltrim(nombre_texte):
    "Supprime les 0 initiaux d'un nombre géré sous forme de chaîne de caractères"
    while(len(nombre_texte) > 1 and nombre_texte[0] == "0"):
        nombre_texte = nombre_texte[1:]
    return nombre_texte

def comparaisonTitres_sous_zone(NumNot,ark_current,systemid,isbn,titre,auteur,date,recordBNF,origineComparaison,sous_zone):
    ark = ""
    field = sous_zone.split("$")[0]
    subfield = sous_zone.split("$")[1]
    titreBNF = nettoyageTitrePourControle(main.extract_subfield(recordBNF,field,subfield,1))
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
        elif(titre.find(titreBNF) > -1):
            NumNotices2methode[NumNot].append(origineComparaison + " + contrôle Titre BNF contenu dans titre initial")
            ark = ark_current
        elif (titreBNF.find(titre) > -1):
            NumNotices2methode[NumNot].append(origineComparaison + " + contrôle Titre initial contenu dans titre BNF")
            ark = ark_current
    elif (titre == ""):
        ark = ark_current
        NumNotices2methode[NumNot].append(origineComparaison + " + pas de titre initial pour comparer")
    return ark

#Recherche par n° système. Si le 3e paramètre est "False", c'est qu'on a pris uniquement le FRBNF initial, sans le tronquer. 
#Dans ce cas, et si 0 résultat pertinent, on relance la recherche avec info tronqué
def systemid2ark(NumNot,systemid,tronque,isbn,titre,auteur,date):
    url = url_requete_sru('bib.otherid all "' + systemid + '"')
    #url = "http://catalogueservice.bnf.fr/SRU?version=1.2&operation=searchRetrieve&query=NumNotice%20any%20%22" + systemid + "%22&recordSchema=InterXMarc_Complet&maximumRecords=1000&startRecord=1"
    listeARK = []
    (test,page) = testURLetreeParse(url)
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

def rechercheNNB(NumNot,nnb,isbn,titre,auteur,date):
    ark = ""
    if (nnb.isdigit() is False):
        #pb_frbnf_source.write("\t".join[NumNot,nnb] + "\n")
        ark = "Pb FRBNF"
    elif (30000000 < int(nnb) < 50000000):
        url = url_requete_sru('bib.recordid any "' + nnb + '"')
        (test,page) = testURLetreeParse(url)
        if (test == True):
            for record in page.xpath("//srw:records/srw:record", namespaces=main.ns):
                ark_current = record.find("srw:recordIdentifier",namespaces=main.ns).text
                ark = comparerBibBnf(NumNot,ark_current,nnb,isbn,titre,auteur,date,"Numéro de notice")
    return ark

#Si le FRBNF n'a pas été trouvé, on le recherche comme numéro système -> pour ça on extrait le n° système
def oldfrbnf2ark(NumNot,frbnf,isbn,titre,auteur,date):
    """Extrait du FRBNF le numéro système, d'abord sur 9 chiffres, puis sur 8 si besoin, avec un contrôle des résultats sur le contenu du titre ou sur l'auteur"""
    systemid = ""
    if (frbnf[0:5].upper() == "FRBNF"):
        systemid = frbnf[5:14]
    else:
        systemid = frbnf[4:13]
    ark = rechercheNNB(NumNot,systemid[0:8],isbn,titre,auteur,date)
    if (ark==""):
        ark = systemid2ark(NumNot,systemid,False,isbn,titre,auteur,date)
    return ark

 
def frbnf2ark(NumNot,frbnf,isbn,titre,auteur,date):
    """Rechercher le FRBNF avec le préfixe "FRBN" ou "FRBNF". A défaut, lance d'autres fonctions pour lancer la recherche en utilisant uniquement le numéro, soit comme NNB/NNA, soit comme ancien numéro système (en zone 9XX)"""
    ark = ""
    if (frbnf[0:4].lower() == "frbn"):
        url = url_requete_sru('bib.otherid all "' + frbnf + '"')
        (test,page) = testURLetreeParse(url)
        if (test == True):
            nb_resultats = int(page.find("//srw:numberOfRecords", namespaces=main.ns).text)
            
            if (nb_resultats == 0):
                ark = oldfrbnf2ark(NumNot,frbnf,isbn,titre,auteur,date)
            elif (nb_resultats == 1):
                ark = page.find("//srw:recordIdentifier", namespaces=main.ns).text
                NumNotices2methode[NumNot].append("FRBNF > ARK")
            else:
                ark = ",".join([ark.text for ark in page.xpath("//srw:recordIdentifier", namespaces=main.ns)])
                NumNotices2methode[NumNot].append("FRBNF > ARK")
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
    isbn_nett = isbn.split(";")[0].split(",")[0].split("(")[0].split("[")[0]
    isbn_nett = isbn_nett.replace("-","").replace(" ","")
    for signe in ponctuation:
        isbn_nett.replace(signe,"")
    isbn_nett = unidecode(isbn_nett)
    for lettre in lettres_sauf_x:
        isbn_nett.replace(lettre,"")
    return isbn_nett
    
def conversionIsbn(isbn):
    longueur = len(isbn)
    isbnConverti = ""
    if (longueur == 10):
        isbnConverti = conversionIsbn1013(isbn)
    elif (longueur == 13):
        isbnConverti = conversionIsbn1310(isbn)
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
#==============================================================================
# Fonctions pour convertir les chiffres romains en chiffres arabes (et l'inverse)
# Utilisé pour comparer les volumaisons
#==============================================================================
numeral_map = tuple(zip(
    (1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1),
    ('M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I')
))

def int_to_roman(i):
    result = []
    for integer, numeral in numeral_map:
        count = i // integer
        result.append(numeral * count)
        i -= integer * count
    return ''.join(result)

def roman_to_int(n):
    i = result = 0
    for integer, numeral in numeral_map:
        while n[i:i + len(numeral)] == numeral:
            result += integer
            i += len(numeral)
    return result

def convert_volumes_to_int(n):
    for char in ponctuation:
        n = n.replace(char,"-")
    n = n.replace(" ","-")
    liste_n = [e for e in n.split("-") if e != ""]
    liste_n_convert = []
    for n in liste_n:
        try:
            int(n)
            liste_n_convert.append(n)
        except ValueError:
            c = roman_to_int(n)
            if (c != 0):
                liste_n_convert.append(c)
    liste_n_convert = set(ltrim(str(nb)) for nb in liste_n_convert if nb != "")
    n_convert = " ".join([str(el) for el in list(liste_n_convert)])
    return n_convert


def isbn2sru(NumNot,isbn,titre,auteur,date):
    urlSRU = url_requete_sru('bib.isbn all "' + isbn + '"')
    listeARK = []
    (test,resultats) = testURLetreeParse(urlSRU)
    if (test == True):
        for record in resultats.xpath("//srw:records/srw:record", namespaces=main.ns):
            ark_current = record.find("srw:recordIdentifier", namespaces=main.ns).text
            recordBNF_url = url_requete_sru('bib.persistentid all "' + ark_current + '"')
            (test,recordBNF) = testURLetreeParse(recordBNF_url)
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
    motlongauteur = nettoyageAuteur(auteur, True)
    urlSRU = url_requete_sru('bib.isbn all "' + isbn + '" and bib.author all "' + motlongauteur + '"')
    listeARK = []
    (test,resultats) = testURLetreeParse(urlSRU)
    if (test == True):
        if (resultats.find("//srw:records/srw:record", namespaces=main.ns) is not None):
            NumNotices2methode[NumNot].append("ISBN + Auteur > ARK")
        for record in resultats.xpath("//srw:records/srw:record", namespaces=main.ns):
            ark_current = record.find("srw:recordIdentifier", namespaces=main.ns).text
            listeARK.append(ark_current)
    listeARK = ",".join([ark for ark in listeARK if ark != ""])
    return listeARK

def eanauteur2sru(NumNot,ean,titre,auteur,date):
    """Si la recherche EAN avec contrôle titre n'a rien donné, on recherche EAN + le mot le plus long dans la zone "auteur", et pas de contrôle sur Titre ensuite"""
    motlongauteur = nettoyageAuteur(auteur, True)
    urlSRU = url_requete_sru('bib.ean all "' + ean + '" + bib.author all "' + motlongauteur + '"')
    listeARK = []
    (test,resultats) = testURLetreeParse(urlSRU)
    if (test == True):
        if (resultats.find("//srw:records/srw:record", namespaces=main.ns) is not None):
            NumNotices2methode[NumNot].append("EAN + Auteur > ARK")
        for record in resultats.xpath("//srw:records/srw:record", namespaces=main.ns):
            ark_current = record.find("srw:recordIdentifier", namespaces=main.ns).text
            listeARK.append(ark_current)
    listeARK = ",".join([ark for ark in listeARK if ark != ""])
    return listeARK

def testURLetreeParse(url):
    test = True
    resultat = ""
    try:
        resultat = etree.parse(request.urlopen(url))
    except etree.XMLSyntaxError as err:
        print(url)
        print(err)
        url_access_pbs.append([url,"etree.XMLSyntaxError"])
        test = False
    except etree.ParseError as err:
        print(url)
        print(err)
        test = False
        url_access_pbs.append([url,"etree.ParseError"])
    except error.URLError as err:
        print(url)
        print(err)
        test = False
        url_access_pbs.append([url,"urllib.error.URLError"])
    except ConnectionResetError as err:
        print(url)
        print(err)
        test = False
        url_access_pbs.append([url,"ConnectionResetError"])
    except TimeoutError as err:
        print(url)
        print(err)
        test = False
        url_access_pbs.append([url,"TimeoutError"])
    except http.client.RemoteDisconnected as err:
        print(url)
        print(err)
        test = False
        url_access_pbs.append([url,"http.client.RemoteDisconnected"])
    except http.client.BadStatusLine as err:
        print(url)
        print(err)
        test = False
        url_access_pbs.append([url,"http.client.BadStatusLine"])
    return (test,resultat)


def testURLurlopen(url):
    test = True
    resultat = ""
    try:
        resultat = request.urlopen(url)
    except etree.XMLSyntaxError as err:
        print(url)
        print(err)
        url_access_pbs.append([url,"etree.XMLSyntaxError"])
        test = False
    except etree.ParseError as err:
        print(url)
        print(err)
        test = False
        url_access_pbs.append([url,"etree.ParseError"])
    except error.URLError as err:
        print(url)
        print(err)
        test = False
        url_access_pbs.append([url,"urllib.error.URLError"])
    except ConnectionResetError as err:
        print(url)
        print(err)
        test = False
        url_access_pbs.append([url,"ConnectionResetError"])
    except TimeoutError as err:
        print(url)
        print(err)
        test = False
        url_access_pbs.append([url,"TimeoutError"])
    except http.client.RemoteDisconnected as err:
        print(url)
        print(err)
        test = False
        url_access_pbs.append([url,"http.client.RemoteDisconnected"])
    except http.client.BadStatusLine as err:
        print(url)
        print(err)
        test = False
        url_access_pbs.append([url,"http.client.BadStatusLine"])
    return (test,resultat)

#Si l'ISBN n'a été trouvé ni dans l'index ISBN, ni dans l'index EAN
#on le recherche dans tous les champs (not. les données d'exemplaires, pour des 
#réimpressions achetées par un département de la Direction des collections de la BnF)
def isbn_anywhere2sru(NumNot,isbn,titre,auteur,date):
    urlSRU = url_requete_sru('bib.anywhere all "' + isbn + '"')
    test,resultat = testURLetreeParse(urlSRU)
    listeARK = []
    if (test == True):
        for record in resultat.xpath("//srw:records/srw:record", namespaces=main.ns):
            ark_current = record.find("srw:recordIdentifier", namespaces=main.ns).text
            recordBNF_url = url_requete_sru('bib.persistentid all "' + ark_current)
            (test2,recordBNF) = testURLetreeParse(recordBNF_url)
            if (test2 == True):
                ark = comparaisonTitres(NumNot,ark_current,"",isbn,titre,auteur,date,"",recordBNF,"ISBN dans toute la notice")
                #NumNotices2methode[NumNot].append("ISBN anywhere > ARK")
                listeARK.append(ark)
    listeARK = ",".join([ark for ark in listeARK if ark != ""])
    return listeARK


def testURLretrieve(url):
    test = True
    try:
        request.urlretrieve(url)
    except error.HTTPError as err:
        test = False
    except error.URLError as err:
        test = False
    except http.client.RemoteDisconnected as err:
        test = False
    return test


def isbn2sudoc(NumNot,isbn,isbnConverti,titre,auteur,date):
    """A partir d'un ISBN, recherche dans le Sudoc. Pour chaque notice trouvée, on regarde sur la notice
    Sudoc a un ARK BnF ou un FRBNF, auquel cas on convertit le PPN en ARK. Sinon, on garde le(s) PPN"""
    url = "https://www.sudoc.fr/services/isbn2ppn/" + isbn
    Listeppn = []
    isbnTrouve = testURLretrieve(url)
    ark = []
    if (isbnTrouve == True):
        (test,resultats) = testURLetreeParse(url)
        if (test == True):
            if (resultats.find("//ppn") is not None):
                NumNotices2methode[NumNot].append("ISBN > PPN")                
            for ppn in resultats.xpath("//ppn"):
                ppn_val = ppn.text
                Listeppn.append("PPN" + ppn_val)
                ark.append(ppn2ark(NumNot,ppn_val,isbn,titre,auteur,date))
            if (ark == []):
                url = "https://www.sudoc.fr/services/isbn2ppn/" + isbnConverti
                isbnTrouve = testURLretrieve(url)
                if (isbnTrouve == True):
                    (test,resultats) = testURLetreeParse(url)
                    if (test == True):
                        for ppn in resultats.xpath("//ppn"):
                            ppn_val = ppn.text
                            Listeppn.append("PPN" + ppn_val)
                            ark = ppn2ark(NumNot,ppn_val,isbnConverti,titre,auteur,date)
                            if (Listeppn != []):
                                add_to_conversionIsbn(NumNot,isbn,isbnConverti,True)
    #Si on trouve un PPN, on ouvre la notice pour voir s'il n'y a pas un ARK déclaré comme équivalent --> dans ce cas on récupère l'ARK
    Listeppn = ",".join([ppn for ppn in Listeppn if ppn != ""])
    ark = ",".join([ark1 for ark1 in ark if ark1 != ""])
    if (ark != ""):
        return ark
    else:
        return Listeppn

def ean2sudoc(NumNot,ean,titre,auteur,date):
    """A partir d'un EAN, recherche dans le Sudoc. Pour chaque notice trouvée, on regarde sur la notice
    Sudoc a un ARK BnF ou un FRBNF, auquel cas on convertit le PPN en ARK. Sinon, on garde le(s) PPN"""
    url = "https://www.sudoc.fr/services/ean2ppn/" + ean
    Listeppn = []
    eanTrouve = testURLretrieve(url)
    ark = []
    if (eanTrouve == True):
        (test,resultats) = testURLetreeParse(url)
        if (test == True):
            for ppn in resultats.xpath("//ppn"):
                ppn_val = ppn.text
                Listeppn.append("PPN" + ppn_val)
                NumNotices2methode[NumNot].append("EAN > PPN")
                ark.append(ppn2ark(NumNot,ppn_val,ean,titre,auteur,date))
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
    (test,record) = testURLetreeParse(url)
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
                ark = frbnf2ark(NumNot,frbnf_val,isbn,titre,auteur,date)
    return ark

def add_to_conversionIsbn(NumNot,isbn_init,isbn_trouve,via_Sudoc=False):
    NumNotices_conversionISBN[NumNot]["isbn initial"] = isbn_init
    NumNotices_conversionISBN[NumNot]["isbn trouvé"] = isbn_trouve
    NumNotices_conversionISBN[NumNot]["via Sudoc"] = str(via_Sudoc)

def isbn2ark(NumNot,isbn_init,isbn,titre,auteur,date):
    #Recherche sur l'ISBN tel que saisi dans la source
    resultatsIsbn2ARK = isbn2sru(NumNot,isbn_init,titre,auteur,date)
    
    #Requête sur l'ISBN dans le SRU, avec contrôle sur Titre ou auteur
    if (resultatsIsbn2ARK == "" and isbn_init != isbn):
        resultatsIsbn2ARK = isbn2sru(NumNot,isbn,titre,auteur,date)

    isbnConverti = conversionIsbn(isbn)
#Si pas de résultats : on convertit l'ISBN en 10 ou 13 et on relance une recherche dans le catalogue BnF
    if (resultatsIsbn2ARK == ""):
        resultatsIsbn2ARK = isbn2sru(NumNot,isbnConverti,titre,auteur,date)
        if (resultatsIsbn2ARK != ""):
            add_to_conversionIsbn(NumNot,isbn_init,isbnConverti,False)
#Si pas de résultats et ISBN 13 : on recherche sur EAN
    if (resultatsIsbn2ARK == "" and len(isbn)==13):
        resultatsIsbn2ARK = ean2ark(NumNot,isbn,titre,auteur,date)
    if (resultatsIsbn2ARK == "" and len(isbnConverti) == 13):
        resultatsIsbn2ARK = ean2ark(NumNot,isbnConverti,titre,auteur,date)
        if (resultatsIsbn2ARK != ""):
            add_to_conversionIsbn(NumNot,isbn_init,isbnConverti,False)

#Si pas de résultats et ISBN 13 : on recherche l'ISBN dans tous les champs (dont les données d'exemplaire)
    if (resultatsIsbn2ARK == ""):
        resultatsIsbn2ARK = isbn_anywhere2sru(NumNot,isbn,titre,auteur,date)
    if (resultatsIsbn2ARK == "" and len(isbnConverti) == 13):
        resultatsIsbn2ARK = isbn_anywhere2sru(NumNot,isbnConverti,titre,auteur,date)
        if (resultatsIsbn2ARK != ""):
            add_to_conversionIsbn(NumNot,isbn_init,isbnConverti,False)

#Si pas de résultats : on relance une recherche dans le Sudoc    
    if (resultatsIsbn2ARK == ""):
        resultatsIsbn2ARK = isbn2sudoc(NumNot,isbn,isbnConverti,titre,auteur,date)
    return resultatsIsbn2ARK

def issn2ark(NumNot,issn_init,issn,titre,auteur,date):
    listeArk  = issn2sru(NumNot,issn_init)
    if (listeArk == ""):
        listeArk = issn2sru(NumNot,issn)
    if (listeArk == ""):
        listeArk = issn2sudoc(NumNot, issn_init, issn, titre, auteur, date)
    return listeArk 

def issn2sru(NumNot,issn):
    url = url_requete_sru('bib.issn all "' + issn + '"')
    listeArk = []
    (test,pageSRU) = testURLetreeParse(url)
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
    issnTrouve = testURLretrieve(url)
    ark = []
    if (issnTrouve == True):
        (test,resultats) = testURLetreeParse(url)
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
    recordBNF_url = url_requete_sru('bib.persistentid any "' + ark + '"')
    (test,record) = testURLetreeParse(recordBNF_url)
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
    (test,record) = testURLetreeParse(url)
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
  
def tad2ark(NumNot,titre,auteur,auteur_nett,date_nett,numeroTome,typeRecord,typeDoc="a",anywhere=False,pubPlace_nett="", annee_plus_trois = False):
    "Fonction d'alignement par Titre-Auteur-Date (et contrôles sur type Notice, sur n° de volume si nécessaire)"
#En entrée : le numéro de notice, le titre (qu'il faut nettoyer pour la recherche)
#L'auteur = zone auteur initiale, ou à défaut auteur_nett
#date_nett
    #print(NumNot,titre,auteur,auteur_nett,date_nett,numeroTome,typeRecord,typeDoc,anywhere,pubPlace_nett, annee_plus_trois)
    listeArk = []
    titre_propre = nettoyageTitrePourRecherche(titre)
    #Cas des périodiques = on récupère uniquement la première date
    #Si elle est sur moins de 4 caractères (19.. devenu 19, 196u devenu 196)
    #   -> on tronque
    if (typeRecord == "s" and annee_plus_trois == False):
        date_nett = datePerios(date_nett)
    if (len(str(date_nett)) < 4):
        date_nett += "*"
    param_date = "all"
    #Si on cherche l'année de début de périodique en élargissant à une fourchette de dates
    #3 ans avant et 3 ans après
    if (annee_plus_trois == True):
        param_date = "any"
    if (titre_propre != ""):
        if (auteur == ""):
            auteur = "-"
        if (date_nett == ""):
            date_nett = "-"
        if (auteur_nett == ""):
            auteur_nett = "-"
        if (pubPlace_nett == ""):
            pubPlace_nett = "-"
        url = url_requete_sru('bib.title all "' + titre_propre + '" and bib.author all "' + auteur + '" and bib.date ' + param_date + ' "' + date_nett + '" and bib.publisher all "' + pubPlace_nett + '" and bib.doctype any "' + typeDoc + '"')
        if (anywhere == True):
            url = url_requete_sru('bib.anywhere all "' + titre_propre + ' ' + auteur + ' ' + pubPlace_nett + '" and bib.anywhere ' + param_date + ' "' + date_nett + '" and bib.doctype any "' + typeDoc + '"')
        
        (test,results) = testURLetreeParse(url)
        index = ""
        if (results != "" and results.find("//srw:numberOfRecords", namespaces=main.ns).text == "0"):
            url = url_requete_sru('bib.title all "' + titre_propre + '" and bib.author all "' + auteur_nett + '" and bib.date ' + param_date + ' "' + date_nett + '" and bib.publisher all "' + pubPlace_nett + '" and bib.doctype any "' + typeDoc + '"')
            if (anywhere == True):
                url = url_requete_sru('bib.anywhere all "' + titre_propre + ' ' + auteur_nett + ' ' + pubPlace_nett + '" and bib.anywhere ' + param_date + ' "' + date_nett + '" and bib.doctype any "' + typeDoc + '"')
                index = " dans toute la notice"
            (test,results) = testURLetreeParse(url)
        if (test == True):
            i = 1
            total_rec = int(results.find("//srw:numberOfRecords", namespaces=main.ns).text)
            for record in results.xpath("//srw:recordIdentifier",namespaces=main.ns):
                ark_current = record.text
                if (int(results.find("//srw:numberOfRecords", namespaces=main.ns).text) > 100):
                    print("    ", NumNot, "-", ark_current, "".join([str(i), "/", str(total_rec), " (limite max 1000)"]))
                    i += 1
                #print(NumNot + " : " + ark_current)
                recordBNF_url = url_requete_sru('bib.persistentid all "' + ark_current + '"')
                (test,recordBNF) = testURLetreeParse(recordBNF_url)
                if (test == True):
                    if (recordBNF.find("//mxc:record/mxc:leader",namespaces=main.ns) is not None and recordBNF.find("//mxc:record/mxc:leader",namespaces=main.ns).text is not None):
                        typeRecord_current = recordBNF.find("//mxc:record/mxc:leader",namespaces=main.ns).text[7]
                        if (typeRecord_current == typeRecord):
                            listeArk.append(comparaisonTitres(NumNot,ark_current,"","",nettoyageTitrePourControle(titre),auteur,date_nett,numeroTome,recordBNF,"Titre-Auteur-Date" + index))
                            methode = "Titre-Auteur-Date"
                            if (auteur == "-" and date_nett == "-"):
                                methode = "Titre"
                            elif (auteur == "-"):
                                methode = "Titre-Date"
                            elif (date_nett == "-"):
                                methode = "Titre-Auteur"
                            NumNotices2methode[NumNot].append(methode)
                            if ("*" in date_nett):
                                NumNotices2methode[NumNot].append("Date début tronquée")
                            if (annee_plus_trois == True):
                                NumNotices2methode[NumNot].append("Date début +/- 3 ans")
    listeArk = ",".join(ark for ark in listeArk if ark != "")
    #Si la liste retournée est vide, et qu'on est sur des périodiques
    # et que la date 
    if (len(str(date_nett)) == 4 
            and "*" not in date_nett
            and listeArk == "" 
            and typeRecord == "s" 
            and annee_plus_trois == False):
        date = elargirDatesPerios(int(date_nett))
        listeArk = tad2ark(NumNot,titre,auteur,auteur_nett,date,numeroTome,typeRecord,typeDoc,anywhere,pubPlace_nett,True)
    return listeArk

def tad2ppn(NumNot,titre,auteur,auteur_nett,date,typeRecord):
    #Recherche dans DoMyBiblio : Titre & Auteur dans tous champs, Date dans un champ spécifique
    Listeppn = []
    ark = []
    titre = nettoyageTitrePourRecherche(titre).replace(" ","+")
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
    print(url)
    (test,results) = testURLetreeParse(url)
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
    (test,results) = testURLetreeParse(url)
    for record in results.xpath("//records/record"):
        ppn = record.find("identifier").text
        NumNotices2methode[NumNot].append("Titre-Auteur-Date DoMyBiblio")
        Listeppn.append("PPN" + ppn)
        ark.append(ppn2ark(NumNot,ppn,"",titre,auteur,date))
    if (nb_results >= pageID*10):
        tad2ppn_pages_suivantes(NumNot,titre,auteur,auteur_nett,date,typeRecord,url,nb_results,pageID+1)

def checkTypeRecord(ark,typeRecord_attendu):
    url = url_requete_sru('bib.ark any "' + ark + '"')
    print(url)
    ark_checked = ""
    (test,record) = testURLetreeParse(url)
    if (test == True):
        typeRecord = record.find("//srw:recordData/mxc:record/mxc:leader",namespaces=main.ns).text[7]
        if (typeRecord == typeRecord_attendu):
            ark_checked = ark
    return ark_checked

def datePerios(date):
    """Requête sur la date en élargissant sa valeur aux dates approximatives"""
    date = date.split(" ")
    date = date[0]
    return date

def elargirDatesPerios(n):
    j = n-4
    liste = []
    i = 1
    while (i < 8):
        liste.append(j+i)
        i += 1
    return " ".join([str(el) for el in liste])

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

def url_requete_sru(query,recordSchema="unimarcxchange",maximumRecords="1000",startRecord="1"):
    url = main.urlSRUroot + urllib.parse.quote(query) +"&recordSchema=" + recordSchema + "&maximumRecords=" + maximumRecords + "&startRecord=" + startRecord
    return url


def ark2recordBNF(ark,typeRecord="bib"):
    url = url_requete_sru(typeRecord + '.persistentid any "' + ark + '"')
    (test,recordBNF) = testURLetreeParse(url)
    return (test,recordBNF)

def ean2ark(NumNot,ean,titre,auteur,date):
    listeARK = []
    url = url_requete_sru('bib.ean all "' + ean + '"')
    (test,results) = testURLetreeParse(url)
    if (test == True):
        for record in results.xpath("//srw:records/srw:record",namespaces=main.ns):
            if (record.find("srw:recordIdentifier",namespaces=main.ns) is not None):
                ark_current = record.find("srw:recordIdentifier",namespaces=main.ns).text
                (test2,recordBNF) = ark2recordBNF(ark_current)
                if (test2 ==  True):
                    ark = comparaisonTitres(NumNot,ark_current,"",ean,titre,auteur,date,"",recordBNF, "EAN")
                    NumNotices2methode[NumNot].append("EAN > ARK")
                    listeARK.append(ark)
    listeARK = ",".join([ark for ark in listeARK if ark != ""])
    if (listeARK == "" and auteur != ""):
        listeARK = eanauteur2sru(NumNot,ean,titre,auteur,date)

#Si pas de résultats : on relance une recherche dans le Sudoc    
    if (listeARK == ""):
        listeARK = ean2sudoc(NumNot,ean,titre,auteur,date)
    return listeARK

def nettoyage_no_commercial(no_commercial_propre):
    return no_commercial_propre
            
def no_commercial2ark(NumNot,no_commercial,titre,auteur,date,anywhere=False, publisher=""):
    url = url_requete_sru('bib.comref  all "' + no_commercial + '"')
    if (anywhere == True):
        url = url_requete_sru('bib.anywhere  all "' + no_commercial + '"')
    ark = ""
    (test,results) = testURLetreeParse(url)
    if (test == True):
        for record in results.xpath("//srw:records/srw:record",namespaces=main.ns):
            ark_current = record.find("srw:recordIdentifier",namespaces=main.ns).text
            (test2, recordBNF) = ark2recordBNF(ark_current)
            if (test2 == True):
                ark = controleNoCommercial(NumNot,ark_current,no_commercial,titre,auteur,date,recordBNF)
    return ark

def controleNoCommercial(NumNot,ark_current,no_commercial,titre,auteur,date,recordBNF):
    ark = ""
    no_commercialBNF = nettoyage_no_commercial(extract_meta(recordBNF,"071$a"))
    if (no_commercial != "" and no_commercialBNF != ""):
        if (no_commercial in no_commercialBNF):
            ark = ark_current
            NumNotices2methode[NumNot].append("No commercial")
        elif (no_commercialBNF in no_commercial):
            ark = ark_current
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

def monimpr(form_bib2ark, zone_controles, entry_filename, type_doc_bib, file_nb, id_traitement, liste_reports, meta_bib):
    
    header_columns = ["NumNot","nbARK","ark trouvé","Méthode","ark initial","FRBNF","ISBN","EAN","Titre","auteur","date","Tome/Volume", "editeur"]
    if (meta_bib == 1):
        header_columns.extend(["[BnF] Titre","[BnF] 1er auteur Prénom","[BnF] 1er auteur Nom","[BnF] Tous auteurs","[BnF] Date"])
    if (file_nb ==  1):
        row2file(header_columns,liste_reports)
    elif(file_nb ==  2):
        row2files(header_columns,liste_reports)
    n = 0
    with open(entry_filename, newline='\n',encoding="utf-8") as csvfile:
        entry_file = csv.reader(csvfile, delimiter='\t')
        try:
            next(entry_file)
        except UnicodeDecodeError:
            main.popup_errors(form_bib2ark,main.errors["pb_input_utf8"])
        for row in entry_file:
            if (n == 0):
                controls_columns(form_bib2ark, header_columns_init_monimpr, row)
            if (n%100 == 0):
                main.check_access2apis(n,dict_check_apis)
            n += 1
            #print(row)
            (NumNot,frbnf,current_ark,isbn,ean,titre,auteur,date,tome,publisher) = extract_cols_from_row(row,
                ["NumNot","frbnf","ark initial","isbn","ean","titre","auteur","date","tome","editeur"])
            
            isbn_nett = nettoyageIsbnPourControle(isbn)
            isbn_propre = nettoyage_isbn(isbn)
            ean_nett = nettoyageIsbnPourControle(ean)
            ean_propre = nettoyage_isbn(ean)
            titre_nett= nettoyageTitrePourControle(titre)
            auteur_nett = nettoyageAuteur(auteur, False)
            date_nett = nettoyageDate(date)
            tome_nett = convert_volumes_to_int(tome)
            publisher_nett = nettoyageAuteur(publisher, False)
            if (publisher_nett == ""):
                publisher_nett = publisher
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
                ark = isbn2ark(NumNot,isbn,isbn_propre,titre_nett,auteur_nett,date_nett)
            #A défaut, recherche sur EAN
            if (ark == "" and ean != ""):
                ark = ean2ark(NumNot,ean_propre,titre_nett,auteur_nett,date_nett)
            #A défaut, recherche sur Titre-Auteur-Date
            
            #A défaut, recherche sur Titre-Auteur-Date
            if (ark == "" and titre != ""):
                ark = tad2ark(NumNot,titre,auteur,auteur_nett,date_nett,tome_nett,"m","a", False, publisher_nett)
                #print("1." + NumNot + " : " + ark)
            if (ark == "" and titre != ""):
                ark = tad2ark(NumNot,titre,auteur,auteur_nett,date_nett,tome_nett,"m","a",True, publisher_nett)
            
            """if (ark == "" and titre != ""):
                ark = tad2ppn(NumNot,titre,auteur,auteur_nett,date,"monimpr")"""
            
            print(str(n) + ". " + NumNot + " : " + ark)
            nbARK = len(ark.split(","))
            if (ark == ""):
                nbARK = 0   
            if (ark == "Pb FRBNF"):
                nb_notices_nb_ARK["Pb FRBNF"] += 1
            else:
                nb_notices_nb_ARK[nbARK] += 1
            typeConversionNumNot = ""
            if (NumNot in NumNotices2methode):
                typeConversionNumNot = ",".join(NumNotices2methode[NumNot])
            liste_metadonnees = [NumNot,nbARK,ark,typeConversionNumNot,current_ark,frbnf,isbn,ean,titre,auteur,date,tome, publisher]
            if (meta_bib == 1):
                liste_metadonnees.extend(ark2metadc(ark))
            if (file_nb ==  1):
                row2file(liste_metadonnees,liste_reports)
            elif(file_nb ==  2):
                row2files(liste_metadonnees,liste_reports)
        

def cddvd(form_bib2ark, zone_controles, entry_filename, type_doc_bib, file_nb, id_traitement, liste_reports, meta_bib):
    header_columns = ["NumNot","nbARK","ark trouvé","Méthode","ark initial","FRBNF","EAN","no_commercial_propre","titre","auteur","date", "editeur"]
    if (meta_bib == 1):
        header_columns.extend(["[BnF] Titre","[BnF] 1er auteur Prénom","[BnF] 1er auteur Nom","[BnF] Tous auteurs","[BnF] Date"])
    if (file_nb ==  1):
        row2file(header_columns,liste_reports)
    elif(file_nb ==  2):
        row2files(header_columns,liste_reports)
    #results2file(nb_fichiers_a_produire)
    n = 0
    with open(entry_filename, newline='\n',encoding="utf-8") as csvfile:
        entry_file = csv.reader(csvfile, delimiter='\t')
        try:
            next(entry_file)
        except UnicodeDecodeError:
            main.popup_errors(form_bib2ark,main.errors["pb_input_utf8"])
        for row in entry_file:
            if (n == 0):
                controls_columns(form_bib2ark, header_columns_init_cddvd, row)
            #print(row)
            n += 1
            if (n%100 == 0):
                main.check_access2apis(n,dict_check_apis)
            (NumNot,frbnf,current_ark,ean,no_commercial,titre,auteur,date, publisher) = extract_cols_from_row(row,
                ["NumNot","frbnf","ark initial","ean","no_commercial","titre","auteur","date","editeur"])
            ean_nett = nettoyageIsbnPourControle(ean)
            ean_propre = nettoyage_isbn(ean)
            no_commercial_propre = nettoyage_no_commercial(no_commercial)
            titre_nett= nettoyageTitrePourControle(titre)
            auteur_nett = nettoyageAuteur(auteur,False)
            date_nett = nettoyageDate(date)
            publisher_nett = nettoyageAuteur(publisher, False)
            if (publisher_nett == ""):
                publisher_nett = publisher
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
                ark = no_commercial2ark(NumNot,no_commercial_propre,titre_nett,auteur_nett,date_nett,False, publisher_nett)
            #Si la recherche sur bib.comref n'a rien donné -> recherche du numéro partout dans la notice
            if (ark == "" and no_commercial != ""):
                ark = no_commercial2ark(NumNot,no_commercial_propre,titre_nett,auteur_nett,date_nett,True, publisher_nett)
                
            #A défaut, recherche sur Titre-Auteur-Date
            if (ark == "" and titre != ""):
                ark = tad2ark(NumNot,titre,auteur,auteur_nett,date_nett,"","m","g r h",False)
            #A défaut, on recherche Titre-Auteur dans tous champs (+Date comme date)
            if (ark == "" and titre != ""):
                ark = tad2ark(NumNot,titre,auteur,auteur_nett,date_nett,"","m","g r h",True)
            """
            if (ark == "" and titre != ""):
                ark = tad2ppn(NumNot,titre,auteur,auteur_nett,date,"cddvd")
            """
            print(str(n) + "." + NumNot + " : " + ark)
            nbARK = len(ark.split(","))
            if (ark == ""):
                nbARK = 0   
            if (ark == "Pb FRBNF"):
                nb_notices_nb_ARK["Pb FRBNF"] += 1
            else:
                nb_notices_nb_ARK[nbARK] += 1

            typeConversionNumNot = ""
            if (NumNot in NumNotices2methode):
                typeConversionNumNot = ">".join(NumNotices2methode[NumNot])
                
            liste_metadonnees = [NumNot,nbARK,ark,typeConversionNumNot,frbnf,current_ark,ean,
                         no_commercial_propre,titre,auteur,date, publisher]
            if (meta_bib == 1):
                liste_metadonnees.extend(ark2metadc(ark))
            if (file_nb ==  1):
                row2file(liste_metadonnees,liste_reports)
            elif(file_nb ==  2):
                row2files(liste_metadonnees,liste_reports)


#Si option du formulaire = périodiques imprimés
def perimpr(form_bib2ark, zone_controles, entry_filename, type_doc_bib, file_nb, id_traitement, liste_reports, meta_bib):
    header_columns = ["NumNot","nbARK","ark trouvé","Méthode","ark initial","frbnf","issn_nett","titre","auteur","date","lieu"]
    if (meta_bib == 1):
        header_columns.extend(["[BnF] Titre","[BnF] 1er auteur Prénom","[BnF] 1er auteur Nom","[BnF] Tous auteurs","[BnF] Date"])
    if (file_nb ==  1):
        row2file(header_columns,liste_reports)
    elif(file_nb ==  2):
        row2files(header_columns,liste_reports)
    n = 0
    with open(entry_filename, newline='\n',encoding="utf-8") as csvfile:
        entry_file = csv.reader(csvfile, delimiter='\t')
        try:
            next(entry_file)
        except UnicodeDecodeError:
            main.popup_errors(form_bib2ark,main.errors["pb_input_utf8"])
        for row in entry_file:
            n += 1
            if (n%100 == 0):
                main.check_access2apis(n,dict_check_apis)
            #print(row)
            (NumNot,frbnf,current_ark,issn,titre,auteur,date,pubPlace) = extract_cols_from_row(row,
                ["NumNot","frbnf","ark initial","issn","titre","auteur","date","lieu"])

            issn_nett = nettoyageIssnPourControle(issn)
            issn_propre = nettoyage_isbn(issn)
            titre_nett= nettoyageTitrePourControle(titre)
            auteur_nett = nettoyageAuteur(auteur,False)
            date_nett = nettoyageDate(date)
            pubPlace_nett = nettoyagePubPlace(pubPlace)
            #Actualisation de l'ARK à partir de l'ARK
            ark = ""
            if (current_ark != ""):
                ark = ark2ark(NumNot,current_ark)
            
            #A défaut, recherche de l'ARK à partir du FRBNF (+ contrôles sur ISBN, ou Titre, ou Auteur)
            elif (frbnf != ""):
                ark = frbnf2ark(NumNot,frbnf,issn_nett,titre_nett,auteur_nett,date_nett)
                ark = ",".join(ark1 for ark1 in ark.split(",") if ark1 != '')
            #A défaut, recherche sur ISSN
            if (ark == "" and issn_nett != ""):
                ark = issn2ark(NumNot,issn,issn_propre,titre_nett,auteur_nett,date_nett)
            #A défaut, recherche sur Titre-Auteur-Date
            if (ark == "" and titre != ""):
                ark = tad2ark(NumNot,titre,auteur,auteur_nett,date_nett,"","s","a",False,pubPlace_nett)
            #A défaut, recherche sur T-A-D tous mots
            if (ark == "" and titre != ""):
                ark = tad2ark(NumNot,titre,auteur,auteur_nett,date_nett,"","s","a",True,pubPlace_nett)
            print(str(n) + ". " + NumNot + " : " + ark)
            nbARK = len(ark.split(","))
            if (ark == ""):
                nbARK = 0   
            if (ark == "Pb FRBNF"):
                nb_notices_nb_ARK["Pb FRBNF"] += 1
            else:
                nb_notices_nb_ARK[nbARK] += 1
                                 
            typeConversionNumNot = ""
            if (NumNot in NumNotices2methode):
                typeConversionNumNot = ">".join(NumNotices2methode[NumNot])
            liste_metadonnees = [NumNot,nbARK,ark,typeConversionNumNot,frbnf,current_ark,issn_nett,titre,auteur,date]
            if (meta_bib == 1):
                liste_metadonnees.extend(ark2metadc(ark))
            if (file_nb ==  1):
                row2file(liste_metadonnees,liste_reports)
            elif(file_nb ==  2):
                row2files(liste_metadonnees,liste_reports)

def controls_columns(form, header_columns_init, row):
    """i = 0
    text = ""
    for el in header_columns_init:
        text += "\n" + el + " : "
        if (len(row) > i):
            text += row[i]
        i += 1
    main.popup_errors(form,text)  """  
    #tk.Label(zone_controles, text = row[0], bg = "white").pack()
    #print(row[0])

def launch(form_bib2ark,zone_controles, entry_filename, type_doc_bib, file_nb, meta_bib, id_traitement):
    main.check_file_name(form_bib2ark, entry_filename)
    
    #results2file(nb_fichiers_a_produire)
    #print("type_doc_bib : ", type_doc_bib)
    #print("file_nb : ",file_nb)
    #print("id_traitement : ", id_traitement)
    liste_reports = create_reports(id_traitement, file_nb)    
    
    if (type_doc_bib == 1):
        monimpr(form_bib2ark,zone_controles, entry_filename, type_doc_bib, file_nb, id_traitement, liste_reports, meta_bib)
    elif (type_doc_bib == 2):
        cddvd(form_bib2ark,zone_controles, entry_filename, type_doc_bib, file_nb, id_traitement, liste_reports, meta_bib)
    elif (type_doc_bib == 3):
        perimpr(form_bib2ark,zone_controles, entry_filename, type_doc_bib, file_nb, id_traitement, liste_reports, meta_bib)

    else:
        print("Erreur : type de document non reconnu")
    
    fin_traitements(form_bib2ark,liste_reports)


def fin_traitements(form_bib2ark,liste_reports):
    stats_extraction(liste_reports)
    url_access_pbs_report(liste_reports)
    check_access_to_apis(liste_reports)
    typesConversionARK(liste_reports)
    print("Programme terminé")
    form_bib2ark.destroy()



def stats_extraction(liste_reports):
    """Ecriture des rapports de statistiques générales d'alignements"""
    for key in nb_notices_nb_ARK:
        liste_reports[-2].write(str(key) + "\t" + str(nb_notices_nb_ARK[key]) + "\n")
    if ("Pb FRBNF" in sorted(nb_notices_nb_ARK)):
        nb_notices_nb_ARK[-1] = nb_notices_nb_ARK.pop('Pb FRBNF')
    """plt.bar(list(nb_notices_nb_ARK.keys()), nb_notices_nb_ARK.values(), color='skyblue')
    plt.show()"""

def url_access_pbs_report(liste_reports):
    """A la suite des stats générales, liste des erreurs rencontrées (plantage URL) + ISBN différents en entrée et en sortie"""
    if (len(url_access_pbs) > 0):
        liste_reports[-2].write("\n\nProblème d'accès à certaines URL :\nURL\tType de problème\n")
        for pb in url_access_pbs:
            liste_reports[-2].write("\t".join(pb) + "\n")
    if (len(NumNotices_conversionISBN) > 0):
        liste_reports[-2].write("".join(["\n\n",10*"-","\n"]))
        liste_reports[-2].write("Liste des notices dont l'ISBN en entrée est différent de celui dans la notice trouvée\n")
        liste_reports[-2].write("\t".join(["NumNotice",
                                                "ISBN initial",
                                                "ISBN converti",
                                                "Notice trouvée dans le Sudoc ?",
                                                ]) + "\n")
        for record in NumNotices_conversionISBN:
            liste_reports[-2].write("\t".join([record,
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
        liste_reports[-2].write("\n\nProblème d'accès aux API Abes\n")
        for key in dict_check_apis["testAbes"]:
            if (dict_check_apis["testAbes"][key] is False):
                liste_reports[-2].write("".join([str(key)," : API Abes down\n"]))
    if (False in dict_check_apis["testBnF"]):
        liste_reports[-2].write("\n\nProblème d'accès aux API BnF\n")
        for key in dict_check_apis["testBnF"]:
            if (dict_check_apis["testBnF"][key] is False):
                liste_reports[-2].write("".join([str(key)," : API BnF down\n"]))


def typesConversionARK(liste_reports):
    """Dans un rapport spécifique, pour chaque notice en entrée, mention de la méthode d'alignement (ISBN, ISNI, etc.)"""
    for key in NumNotices2methode:
        value = " / ".join(NumNotices2methode[key])
        liste_reports[-1].write(key + "\t" + value + "\n")

def click2help():
    """Fonction d'ouverture du navigateur pour avoir de l'aide sur le logiciel"""
    url = "https://github.com/Transition-bibliographique/alignements-donnees-bnf"
    webbrowser.open_new(url)

def annuler(form_bib2ark):
    """Fermeture du formulaire (bouton "Annuler")"""
    form_bib2ark.destroy()
    

def check_last_compilation(programID):
    """Compare pour un programme donné le numéro de version du fichier en cours et la dernière version indiquée comme telle en ligne. Renvoie une liste à deux éléments : n° de la dernière version publiée ; affichage du bouton de téléchargement (True/False)"""
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
    """Fournit l'URL de téléchargement de la dernière version"""
    url = "https://github.com/Transition-bibliographique/alignements-donnees-bnf/blob/master/noticesbib2arkBnF.py"
    webbrowser.open(url)
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
    example_ico = tk.Button(line1, bd=0, justify="left", font="Arial 7 italic",
                                    text="exemple", command=lambda: main.click2help(link))
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
    
    
#==============================================================================
# Message d'alerte dans le formulaire si besoin
#==============================================================================
#    tk.Label(zone_alert_explications, text="Attention : format MON IMPR avec une colonne supplémentaire en entrée (EAN)", 
#             bg=couleur_fond,  fg="red").pack()
    
    #définition input URL (u)
    tk.Label(cadre_input_header,bg=couleur_fond, fg=couleur_bouton, text="En entrée :", justify="left", font="bold").pack()
    
    tk.Label(cadre_input_file,bg=couleur_fond, text="Fichier contenant les notices : \n\n").pack(side="left")
    """entry_filename = tk.Entry(cadre_input_file, width=40, bd=2)
    entry_filename.pack(side="left")
    entry_filename.focus_set()"""
    main.download_zone(cadre_input_file, "Sélectionner un fichier\nSéparateur TAB, Encodage UTF-8",entry_file_list,couleur_fond)
    
    #tk.Label(cadre_input_infos_format,bg=couleur_fond, text=4*"\t"+"Séparateur TAB, Encodage UTF-8", justify="right").pack(anchor="s")
    
    
    tk.Label(cadre_input_type_docs_zone,bg=couleur_fond, text="Type de documents  ", font="Arial 10 bold", justify="left").pack(anchor="w", side="left")

    type_doc_bib = tk.IntVar()
    radioButton_lienExample(cadre_input_type_docs,type_doc_bib,1,couleur_fond,
                            "Documents imprimés (monographies)",
                            "(Colonnes : " + " | ".join(header_columns_init_monimpr) + ")",
                            "https://raw.githubusercontent.com/Transition-bibliographique/alignements-donnees-bnf/master/examples/mon_impr.tsv")
    radioButton_lienExample(cadre_input_type_docs,type_doc_bib,2,couleur_fond,
                            "Audiovisuel (CD / DVD)",
                            "(" + " | ".join(header_columns_init_cddvd) + ")",
                            "https://raw.githubusercontent.com/Transition-bibliographique/alignements-donnees-bnf/master/examples/adv.tsv")
    radioButton_lienExample(cadre_input_type_docs,type_doc_bib,3,couleur_fond,
                            "Périodiques",
                            "(" + " | ".join(header_columns_init_perimpr) + ")",
                            "https://raw.githubusercontent.com/Transition-bibliographique/alignements-donnees-bnf/master/examples/per.tsv")
    type_doc_bib.set(1)
    
    
    
    #Choix du format
    tk.Label(cadre_output_header,bg=couleur_fond, fg=couleur_bouton,text="En sortie :", font="bold").pack(anchor="w")
    tk.Label(cadre_output_nb_fichiers_zone, bg=couleur_fond, font="Arial 10 bold", text="Nombre de fichiers  ").pack(anchor="w", side="left")
    file_nb = tk.IntVar()
    """file_nb = tk.Entry(cadre_output_nb_fichiers_zone, width=3, bd=2)
    file_nb.pack(anchor="w", side="left")
    tk.Label(cadre_output_nb_fichiers_explications, bg=couleur_fond,text="1 = 1 fichier d'alignements\n2 = Plusieurs fichiers (0 ARK trouvé / 1 ARK / Plusieurs ARK)",
                                   justify="left").pack(anchor="w")"""


    tk.Radiobutton(cadre_output_nb_fichier,bg=couleur_fond, text="1 fichier", variable=file_nb , value=1, justify="left").pack(anchor="w")
    tk.Radiobutton(cadre_output_nb_fichier,bg=couleur_fond, text="Plusieurs fichiers \n(Pb / 0 / 1 / plusieurs ARK trouvés)", justify="left", variable=file_nb , value=2).pack(anchor="w")
    file_nb.set(1)
    #Récupérer les métadonnées BIB (dublin core)
    tk.Label(cadre_output_nb_fichier,bg=couleur_fond, fg=couleur_bouton, text="\n").pack()    
    meta_bib = tk.IntVar()
    meta_bib_check = tk.Checkbutton(cadre_output_nb_fichier, bg=couleur_fond, 
                       text="Récupérer les métadonnées\nbibliographiques BnF [Dublin Core]", 
                       variable=meta_bib, justify="left")
    meta_bib_check.pack(anchor="w")
    tk.Label(cadre_output_nb_fichier,text="\n\n\n\n\n", bg=couleur_fond).pack()


    
    #Ajout (optionnel) d'un identifiant de traitement
    tk.Label(cadre_output_id_traitement,bg=couleur_fond, text="\n\n\n").pack()
    tk.Label(cadre_output_id_traitement,bg=couleur_fond, text="ID traitement (optionnel)").pack()
    id_traitement = tk.Entry(cadre_output_id_traitement, width=20, bd=2)
    id_traitement.pack()
    tk.Label(cadre_output_id_traitement,bg=couleur_fond, text="\n\n\n").pack()
    
    
    
    #Bouton de validation
    
    b = tk.Button(zone_ok_help_cancel, bg=couleur_bouton, fg="white", font="Arial 10 bold", 
                  text = "Aligner les\nnotices BIB", 
                  command = lambda: launch(form_bib2ark,zone_controles , entry_file_list[0], type_doc_bib.get(), file_nb.get(), meta_bib.get(), id_traitement.get()), borderwidth=5 ,padx=10, pady=10, width=10, height=4)
    b.pack()
    
    tk.Label(zone_ok_help_cancel, font="bold", text="", bg=couleur_fond).pack()
    
    call4help = tk.Button(zone_ok_help_cancel, text="Besoin d'aide ?", command=click2help, padx=10, pady=1, width=15)
    call4help.pack()
    
    cancel = tk.Button(zone_ok_help_cancel, bg=couleur_fond, text="Annuler", command=lambda: annuler(form_bib2ark), padx=10, pady=1, width=15)
    cancel.pack()
    
    zone_version = tk.Frame(zone_notes, bg=couleur_fond)
    zone_version.pack()
    tk.Label(zone_version, text = "Version " + str(main.version) + " - " + lastupdate, bg=couleur_fond).pack()

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
    
