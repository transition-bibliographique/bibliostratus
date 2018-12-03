# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 21:21:17 2018

@author: Lully
Fonctions et classes génériques pour Bibliostratus
"""

import http.client
import urllib.parse
import os
import sys
import socket
import subprocess
import ssl
from urllib import error, request
import string
import json
import random
import datetime
import time

from lxml import etree
from lxml.html import parse
from collections import defaultdict
from unidecode import unidecode

import pymarc as mc

import main
import noticesaut2arkBnF as aut2ark
from udecode import udecode

# Ajout exception SSL pour éviter
# plantages en interrogeant les API IdRef
# (HTTPS sans certificat)
if (not os.environ.get('PYTHONHTTPSVERIFY', '')
   and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


# Ajout du fichier preferences.json, pour le cas où on souhaite
# injecter une liste de mots vides
prefs = {}
stop_words = []
try:
    with open('main/files/preferences.json', encoding="utf-8") as prefs_file:
        prefs = json.load(prefs_file)
except FileNotFoundError:
    pass

if (prefs
    and "stop_words" in prefs
    and "value" in prefs["stop_words"]
    and prefs["stop_words"]["value"]):
    try:
        stop_words_file = open(prefs["stop_words"]["value"], "r", encoding="utf-8")
        for row in stop_words_file:
            word = row.replace("\r", "").replace("\n", "").split("\t")[0]
            word = udecode(word.lower())
            stop_words.append(word)
        stop_words_file.close()
    except FileNotFoundError:
        pass

# Quelques listes de signes à nettoyer
listeChiffres = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
lettres = [
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o",
    "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"
]
lettres_sauf_x = [
    "a", "c", "b", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o",
    "p", "q", "r", "s", "t", "u", "v", "w", "y", "z"
]
ponctuation = [
    ".", ",", ";", ":", "?", "!", "%", "$", "£", "€", "#", "\\", "\"", "&", "~",
    "{", "(", "[", "`", "\\", "_", "@", ")", "]", "}", "=", "+", "*", "\/", "<",
    ">", ")", "}", "̊"
]

url_access_pbs = []


def unidecode_local(string):
    """personnalisation de la fonction unidecode,
    qui modifie aussi certains caractères de manière problématique
    par exemple :
    ° devient 'deg'
    """
    corr_temp_dict = {
        '°': '#deg#'
    }

    reverse_corr_temp_dict = defaultdict(str)
    for key in corr_temp_dict:
        reverse_corr_temp_dict[corr_temp_dict[key]] = key

    for char in corr_temp_dict:
        string = string.replace(char, corr_temp_dict[char])

    string = udecode(string)
    for char in reverse_corr_temp_dict:
        string = string.replace(char, reverse_corr_temp_dict[char])
    return string


def nettoyage(string, remplacerEspaces=True, remplacerTirets=True, remplacerApostrophe=True):
    """nettoyage des chaines de caractères (titres, auteurs, isbn)
    suppression ponctuation, espaces (pour les titres et ISBN) et diacritiques"""
    string = unidecode_local(string.lower())
    for signe in ponctuation:
        string = string.replace(signe, "")
    string = string.replace("\\'", "'")
    string = " ".join([el for el in string.split(" ") if el != ""])
    if remplacerTirets:
        string = string.replace("-", " ")
    if remplacerApostrophe:
        string = string.replace("'", " ")
    if remplacerEspaces:
        string = string.replace(" ", "")
    string = string.strip()
    return string


def clean_stop_words(string, list_stop_words, sep=" "):
    """Dans une chaîne de caractères 'string', on isole chaque mot
    et s'il s'agit d'un des stop words de la list_stop_words, on le supprime"""
    string_list = string.split(sep)
    string_list_corr = []
    for word in string_list:
        w = unidecode_local(word.lower())
        if w not in list_stop_words:
            string_list_corr.append(word)
    string_corr = sep.join(string_list_corr)
    return string_corr


def nettoyage_lettresISBN(isbn):
    isbn = unidecode_local(isbn.lower())
    char_cle = "0123456789xX"
    for signe in ponctuation:
        isbn = isbn.replace(signe, "")
    prefix = isbn[0:-1]
    cle = isbn[-1]
    for lettre in lettres:
        prefix = prefix.replace(lettre, "")
    if (cle in char_cle):
        cle = cle.upper()
    else:
        cle = ""
    return prefix + cle


def nettoyageIsbnPourControle(isbn):
    isbn = nettoyage(isbn)
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
    issn = nettoyage(issn).replace(" ", "")
    if (issn != ""):
        issn = nettoyage_lettresISBN(issn)
    if (len(issn) < 8):
        issn = ""
    else:
        issn = issn[0:8]
    return issn


def nettoyage_no_commercial(no_commercial_propre):
    no_commercial_propre = unidecode_local(no_commercial_propre.lower())
    no_commercial_propre = no_commercial_propre.strip(" ")
    return no_commercial_propre


def nettoyageAuteur(auteur, justeunmot=True):
    listeMots = [" par ", " avec ", " by ", " Mr. ", " M. ", " Mme ", " Mrs "]
    for mot in listeMots:
        auteur = auteur.replace(mot, "")
    for chiffre in listeChiffres:
        auteur = auteur.replace(chiffre, "")
    auteur = nettoyage(auteur.lower(), False)
    auteur = auteur.split(" ")
    auteur = sorted(auteur, key=len, reverse=True)
    auteur = [auteur1 for auteur1 in auteur if len(auteur1) > 1]
    if (auteur is not None and auteur != []):
        if justeunmot:
            auteur = auteur[0]
        else:
            auteur = " ".join(auteur)
    else:
        auteur = ""
    return auteur


def nettoyageTitrePourControle(string):
    string = nettoyage(string, True)
    return string


def nettoyageTitrePourRecherche(string):
    string = nettoyage(string, False)
    string = string.replace("/", " ")
    string = string.split(" ")
    string = [mot for mot in string if len(mot) > 1]
    string = " ".join(string)

    if (stop_words):
        string = clean_stop_words(string, stop_words, " ")
        string = clean_stop_words(string, stop_words, "-")

    return string


def nettoyageDate(date):
    # Suppression de tout ce qui n'est pas chiffre romain
    date = unidecode(unidecode_local(date.lower()))
    for lettre in lettres:
        date = date.replace(lettre, "")
    for signe in ponctuation:
        date = date.split(signe)
        date = " ".join(annee for annee in date if annee.strip(" ") != "")
    date = date.strip(" ")
    return date


def nettoyageTome(numeroTome):
    if (numeroTome):
        numeroTome = unidecode_local(numeroTome.lower())
        for lettre in lettres:
            numeroTome = numeroTome.replace(lettre, "")
        for signe in ponctuation:
            numeroTome = numeroTome.split(signe)
            numeroTome = "~".join(numero for numero in numeroTome)
        numeroTome = numeroTome.split("~")
        numeroTome = [numero for numero in numeroTome if numero != ""]
        if (numeroTome != []):
            numeroTome = numeroTome[-1]
            numeroTome = numeroTome.strip(" ")
        else:
            numeroTome = ""
        numeroTome = ltrim(numeroTome)
    return numeroTome


def nettoyagePubPlace(pubPlace):
    """Nettoyage du lieu de publication"""
    pubPlace = unidecode_local(pubPlace.lower())
    for chiffre in listeChiffres:
        pubPlace = pubPlace.replace(chiffre, "")
    for signe in ponctuation:
        pubPlace = pubPlace.split(signe)
        pubPlace = " ".join(mot.strip(" ") for mot in pubPlace if mot.strip(" ") != "")
    return pubPlace


def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def ltrim(nombre_texte):
    "Supprime les 0 initiaux d'un nombre géré sous forme de chaîne de caractères"
    while(len(nombre_texte) > 1 and nombre_texte[0] == "0"):
        nombre_texte = nombre_texte[1:]
    return nombre_texte


def nettoyage_isbn(isbn):
    isbn_nett = isbn.split(";")[0].split(",")[0].split("(")[0].split("[")[0]
    isbn_nett = isbn_nett.replace("-", "").replace(" ", "").replace("°", "")
    isbn_nett = unidecode_local(isbn_nett)
    for signe in ponctuation:
        isbn_nett = isbn_nett.replace(signe, "")
    isbn_nett = isbn_nett.lower()
    for lettre in lettres_sauf_x:
        isbn_nett = isbn_nett.replace(lettre, "")
    return isbn_nett


def nettoyage_isni(isni):
    isni = isni.split("/")[-1]
    if (isni[0:20] == "http://www.isni.org"):
        isni = isni[20:36]
    else:
        isni = nettoyage(isni)
    for lettre in lettres:
        isni = isni.replace(lettre, "")
    return isni


def nettoyageFRBNF(frbnf):
    frbnf_nett = ""
    frbnf = unidecode_local(frbnf.lower())
    if ("frbn" in frbnf):
        frbnf_nett = frbnf[frbnf.find("frbn"):]
        for signe in ponctuation:
            frbnf_nett = frbnf_nett.split(signe)[0]
    return frbnf_nett


def conversionIsbn(isbn):
    longueur = len(isbn)
    isbnConverti = ""
    if (longueur == 10):
        try:
            isbnConverti = conversionIsbn1013(isbn)
        except ValueError:
            isbnConverti = ""
    elif (longueur == 13):
        try:
            isbnConverti = conversionIsbn1310(isbn)
        except ValueError:
            isbnConverti = ""
    return isbnConverti

# conversion isbn13 en isbn10


def conversionIsbn1310(isbn):
    if (isbn[0:3] == "978"):
        prefix = isbn[3:-1]
        check = check_digit_10(prefix)
        return prefix + check
    else:
        return ""

# conversion isbn10 en isbn13


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


numeral_map = tuple(zip(
    (1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1),
    ('M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I')
))


def int_to_roman(i):
    """Conversion de chiffres arabers en chiffres romains"""
    result = []
    for integer, numeral in numeral_map:
        count = i // integer
        result.append(numeral * count)
        i -= integer * count
    return ''.join(result)


def roman_to_int(n):
    """Consersion de chiffres romains en chiffres arabes"""
    i = result = 0
    for integer, numeral in numeral_map:
        while n[i:i + len(numeral)] == numeral:
            result += integer
            i += len(numeral)
    return result


def convert_volumes_to_int(n):
    """nettoie la mention d'origine des numéros de tome/volume
    en ne conservant que le n° lui-même, au besoin converti
    des chiffres romains en chiffres arabes"""
    for char in ponctuation:
        n = n.replace(char, "-")
    n = n.replace(" ", "-")
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
    liste_n_convert2 = []
    for nb in liste_n_convert:
        val = ltrim(str(nb))
        if (val != "" and val not in liste_n_convert2):
            liste_n_convert2.append(val)
    n_convert = " ".join([str(el) for el in list(liste_n_convert2)])
    return n_convert


def datePerios(date):
    """Requête sur la date en élargissant sa valeur aux dates approximatives
    Ne conserve que la date de début"""
    date = date.split(" ")[0].split("-")[0]
    return date


def elargirDatesPerios(n):
    """Prendre les 3 années précédentes et les 3 années suivantes d'une date"""
    j = n - 4
    liste = []
    i = 1
    while (i < 8):
        liste.append(j + i)
        i += 1
    return " ".join([str(el) for el in liste])


def testURLetreeParse(url, display=True, param_timeout=None):
    test = True
    resultat = ""
    try:
        resultat = etree.parse(request.urlopen(url, timeout=param_timeout))
    except socket.timeout as err:
        test = False
        if (display):
            print(url)
            print(err, param_timeout, "sec")
    except etree.XMLSyntaxError as err:
        test = False
        if (display):
            print(url)
            print(err)
            url_access_pbs.append([url, "etree.XMLSyntaxError"])
    except etree.ParseError as err:
        test = False
        if (display):
            print(url)
            print(err)
            url_access_pbs.append([url, "etree.ParseError"])
    except error.URLError as err:
        test = False
        if (display):
            print(url)
            print(err)
            url_access_pbs.append([url, "urllib.error.URLError"])
    except ConnectionResetError as err:
        test = False
        if (display):
            print(url)
            print(err)
            url_access_pbs.append([url, "ConnectionResetError"])
    except TimeoutError as err:
        print(url)
        print(err)
        test = False
        url_access_pbs.append([url, "TimeoutError"])
    except http.client.RemoteDisconnected as err:
        test = False
        if (display):
            print(url)
            print(err)
            url_access_pbs.append([url, "http.client.RemoteDisconnected"])
    except http.client.BadStatusLine as err:
        test = False
        if (display):
            print(url)
            print(err)
            url_access_pbs.append([url, "http.client.BadStatusLine"])
    except ConnectionAbortedError as err:
        test = False
        if (display):
            print(url)
            print(err)
            url_access_pbs.append([url, "ConnectionAbortedError"])
    except error.HTTPError as err:
        test = False
        if (display):
            print(url)
            print(err)
            url_access_pbs.append([url, "urllib.error.HTTPError"])
    return (test, resultat)


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
    except ConnectionAbortedError as err:
        test = False
    return test


def testURLurlopen(url, display=True, timeout_def=5):
    test = True
    resultat = ""
    try:
        resultat = request.urlopen(url, timeout=timeout_def)
    except etree.XMLSyntaxError as err:
        if display:
            print(url)
            print(err)
        url_access_pbs.append([url, "etree.XMLSyntaxError"])
        test = False
    except etree.ParseError as err:
        if display:
            print(url)
            print(err)
        test = False
        url_access_pbs.append([url, "etree.ParseError"])
    except error.URLError as err:
        if display:
            print(url)
            print(err)
        test = False
        url_access_pbs.append([url, "urllib.error.URLError"])
    except ConnectionResetError as err:
        if display:
            print(url)
            print(err)
        test = False
        url_access_pbs.append([url, "ConnectionResetError"])
    except TimeoutError as err:
        if display:
            print(url)
            print(err)
        test = False
        url_access_pbs.append([url, "TimeoutError"])
    except http.client.RemoteDisconnected as err:
        if display:
            print(url)
            print(err)
        test = False
        url_access_pbs.append([url, "http.client.RemoteDisconnected"])
    except http.client.BadStatusLine as err:
        if display:
            print(url)
            print(err)
        test = False
        url_access_pbs.append([url, "http.client.BadStatusLine"])
    except ConnectionAbortedError as err:
        if display:
            print(url)
            print(err)
        test = False
        url_access_pbs.append([url, "ConnectionAbortedError"])
    except socket.timeout as err:
        test = False
        if display:
            print(err)
        url_access_pbs.append([url, "timeout > 5 secondes"])
    return (test, resultat)


def url_requete_sru(query, recordSchema="unimarcxchange",
                    maximumRecords="1000", startRecord="1"):
    url = main.urlSRUroot + urllib.parse.quote(query) + "&recordSchema=" + recordSchema + \
        "&maximumRecords=" + maximumRecords + "&startRecord=" + \
        startRecord + "&origin=bibliostratus"
    return url


def open_local_file(path):
    """Construit le chemin absolu vers un fichier en local
    Permet d'être correct à la fois en mode "code source"
    et en version précompilée """
    dirname = os.path.dirname(__file__)
    filepath = os.path.join(dirname, path)
    try:
        os.startfile(filepath)
    except FileNotFoundError:
        filepath = filepath.replace("main/examples", "examples").replace("/", "\\")
        os.startfile(filepath)
    except AttributeError:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filepath])


class International_id:
    """Classe définissant les propriétés d'un identifiant bibliographique :
        ISBN, ISSN, EAN """

    def __init__(self, string, conversion_option=True):  # Notre méthode constructeur
        self.init = string
        self.nett = nettoyageIsbnPourControle(self.init)
        self.propre = nettoyage_isbn(self.init)
        self.converti = ""
        if (conversion_option):
            self.converti = conversionIsbn(self.propre)

    def __str__(self):
        """Méthode permettant d'afficher plus joliment notre objet"""
        return "{}".format(self.init)


class Isni:
    """Classe pour les ISNI"""
    def __init__(self, string):  # Notre méthode constructeur
        self.init = string
        self.propre = nettoyage_isni(self.init)

    def __str__(self):
        """Méthode permettant d'afficher plus joliment notre objet"""
        return "{}".format(self.init)


class FRBNF:
    """Classe pour les FRBNF"""
    def __init__(self, string):  # Notre méthode constructeur
        self.init = string
        self.propre = nettoyageFRBNF(self.init)

    def __str__(self):
        """Méthode permettant d'afficher plus joliment notre objet"""
        return "{}".format(self.init)


class Date:
    """Classe pour les ISNI"""
    def __init__(self, string):  # Notre méthode constructeur
        self.init = string
        self.propre = nettoyageDate(self.init)

    def __str__(self):
        """Méthode permettant d'afficher plus joliment notre objet"""
        return "{}".format(self.init)


class Name:
    """Zone de titre"""

    def __init__(self, string):  # Notre méthode constructeur
        self.init = string
        self.propre = nettoyage(self.init, remplacerEspaces=False, remplacerTirets=False)
        self.nett = nettoyage(self.init, remplacerEspaces=True, remplacerTirets=True)

    def __str__(self):
        """Méthode permettant d'afficher plus joliment notre objet"""
        return "{}".format(self.init)


class Titre:
    """Zone de titre"""

    def __init__(self, string):  # Notre méthode constructeur
        self.init = string
        self.controles = nettoyageTitrePourControle(self.init)
        self.recherche = nettoyageTitrePourRecherche(self.init)

    def __str__(self):
        """Méthode permettant d'afficher plus joliment notre objet"""
        return "{}".format(self.init)


class Bib_record:
    """Classe définissant les propriétés d'une notice mise en entrée
    du module d'alignement"""

    def __init__(self, input_row, option_record):  # Notre méthode constructeur
        self.NumNot = input_row[0]
        self.frbnf = FRBNF(input_row[1])
        self.ark_init = input_row[2]
        self.isbn = International_id("")
        self.ean = International_id("")
        self.titre = Titre("")
        self.auteur = ""
        self.date = ""
        self.tome = ""
        self.publisher = ""
        self.no_commercial = International_id("")
        self.issn = International_id("")
        self.pubPlace = ""
        self.metas_init = input_row[1:]
        self.date_debut = ""
        self.dates_elargies_perios = ""
        self.scale = ""
        if (option_record == 1):
            self.type = "TEX"
            self.intermarc_type_doc = "a"
            self.intermarc_type_record = "m"
            self.isbn = International_id(input_row[3])
            self.ean = International_id(input_row[4])
            self.titre = Titre(input_row[5])
            self.auteur = input_row[6]
            self.date = input_row[7]
            self.tome = input_row[8]
            self.publisher = input_row[9]
        if (option_record == 2):
            self.type = "VID"
            self.intermarc_type_doc = "h r"
        if (option_record == 3):
            self.type = "AUD"
            self.intermarc_type_doc = "g r"
        if (option_record == 2 or option_record == 3):
            self.intermarc_type_record = "m"
            self.ean = International_id(input_row[3])
            self.no_commercial = International_id(input_row[4], False)
            self.titre = Titre(input_row[5])
            self.auteur = input_row[6]
            self.date = input_row[7]
            self.publisher = input_row[8]
        if (option_record == 4):
            self.type = "PER"
            self.intermarc_type_record = "s"
            self.intermarc_type_doc = "a"
            self.issn = International_id(input_row[3], False)
            self.titre = Titre(input_row[4])
            self.auteur = input_row[5]
            self.date = input_row[6]
            self.pubPlace = input_row[7]
        if (option_record == 5):
            self.type = "CP"
            self.intermarc_type_record = "m"
            self.intermarc_type_doc = "e"
            self.isbn = International_id(input_row[3])
            self.ean = International_id(input_row[4])
            self.titre = Titre(input_row[5])
            self.auteur = input_row[6]
            self.date = input_row[7]
            self.publisher = input_row[8]
            self.scale = input_row[9]
        self.titre_nett = nettoyageTitrePourControle(self.titre.init)
        self.auteur_nett = nettoyageAuteur(self.auteur, False)
        self.no_commercial_propre = nettoyage_no_commercial(
            self.no_commercial.init)
        self.date_nett = nettoyageDate(self.date)
        self.tome_nett = convert_volumes_to_int(self.tome)
        self.publisher_nett = nettoyageAuteur(self.publisher, False)
        if (self.publisher_nett == ""):
            self.publisher_nett = self.publisher
        self.pubPlace_nett = nettoyagePubPlace(self.pubPlace)
        self.date_debut = datePerios(self.date_nett)
        if RepresentsInt(self.date_debut):
            self.dates_elargies_perios = elargirDatesPerios(
                int(self.date_debut))

        # 11/11/2018 Nouvelle méthode (inscriptible) :
        # méthode d'alignement
        # (objectif : se passer du dictionnaire)
        self.alignment_method = []

class Aut_record:
    """Classe définissant les propriétés d'une notice d'autorité mise en entrée
    du module d'alignement aut2ark, à partir de notices AUT"""

    def __init__(self, input_row, parametres):  # Notre méthode constructeur
        self.metas_init = input_row[1:]
        self.NumNot = input_row[0]
        self.frbnf = FRBNF(input_row[1])
        self.ark_init = input_row[2]
        self.isni = Isni(input_row[3])
        self.lastname = Name(input_row[4])
        self.firstname = Name(input_row[5])
        self.firstdate = Date(input_row[6])
        self.lastdate = Date(input_row[7])
        self.alignment_method = []

class Bib_Aut_record:
    """Classe définissant les propriétés d'une notice bibliographique
    avec métadonnées AUT pour un alignement de la notice d'autorité
    grâce à la combinaison Titre + Auteur"""

    def __init__(self, input_row, parametres):  # Notre méthode constructeur
        self.metas_init = input_row[1:]
        self.NumNot = input_row[0]
        self.NumNot_bib = input_row[1]
        self.ark_bib_init = input_row[2]
        self.frbnf_bib = FRBNF(input_row[3])
        self.titre = Titre(input_row[4])
        self.pubdate = input_row[5]
        self.pubdate_nett = nettoyageDate(self.pubdate)
        self.isni = Isni(input_row[6])
        self.lastname = Name(input_row[7])
        self.firstname = Name(input_row[8])
        self.author_dates = input_row[9]
        self.alignment_method = []
    
        self.date_debut = self.author_dates
        if (self.date_debut.find("av") > 0):
            self.date_debut = self.date_debut[:self.date_debut.find("av")]
        elif (self.date_debut.find("-") > 0):
            date_debutdate_debut = self.date_debut[:self.date_debut.find("-")]
        self.date_debut = main.clean_string(self.date_debut, False, True)


class Alignment_result:
    """
    Gère les résultats d'un alignement : 
    le ou les identifiants trouvés, la méthode utilisée
    les données en entrée (dont le numéro de notice)
    """
    def __init__(self, input_record, ark, parametres):  # Notre méthode constructeur
        self.NumNot = input_record.NumNot
        self.ids_str = ark
        self.ids_list = self.ids_str.split(",")
        self.ids_list = [el for el in self.ids_list if el]
        self.nb_ids = len(self.ids_list)
        self.alignment_method_list = input_record.alignment_method
        if (len(list(set(input_record.alignment_method))) == 1):
            self.alignment_method_list = [input_record.alignment_method[0]]
        self.alignment_method_str = ",".join(self.alignment_method_list)
        self.liste_metadonnees = [
                                    input_record.NumNot,
                                    self.nb_ids,
                                    self.ids_str,
                                    self.alignment_method_str
                                ] + input_record.metas_init
    def __str__(self):
        """Méthode permettant d'afficher plus joliment notre objet"""
        return "{} : {}\nNombre d'ID trouvés : {}".format(self.NumNot, self.ids_str, self.nb_ids)


class Id4record:
    """
    Objet à partir d'une ligne en entrée du module rouge (ark2record)
    """
    def __init__(self, row, parametres={}): 
        self.NumNot = row[0]
        self.aligned_id = Aligned_id(row[-1])

    def __str__(self):
        """Méthode permettant d'afficher plus joliment notre objet"""
        return "NumNot : {}, ID : {}".format(self.NumNot, self.aligned_id.clean)

class Aligned_id:
    """
    Objet "identifiant BnF ou Sudoc/Idref"
    """
    def __init__(self, init): 
        self.init = init
        self.type = ""
        self.clean = init
        self.agency = ""
        if ("ppn" in init.lower()):
            self.type = "ppn"
            self.agency = "Abes"
            self.clean = init[3:]
        elif ("idref" in init.lower()
            or "sudoc" in init.lower()):
            self.agency = "Abes"
            self.type = "ppn"
            self.clean = init.split("/")[-1]
        if ("ark" in init):
            self.agency = "BNF"
            self.type = "ark"
            self.clean = init[init.find("ark"):]


def xml2pymarcrecord(xml_record):
    """
    Sert à récupérer un fichier en ligne, contenant
    une notice simple en XML (balise racine <record/>)
    pour générer un fichier local
    Renvoie le nom du fichier et le fichier lui-même
    Celui-ci est à fermer après traitement (hors fonction)
    """
    temp_name = ''.join(random.choice(string.ascii_lowercase) for _ in range(10))
    record_file = open(temp_name, "w", encoding="utf-8")
    record_file.write("<collection>")
    record_file.write(etree.tostring(xml_record).decode(encoding="utf-8"))
    record_file.write("</collection>")
    record_file.close()
    pymarc_record = mc.marcxml.parse_xml_to_array(temp_name, strict=False)[0]
    os.remove(temp_name)
    return pymarc_record



def domybiblio2ppn(keywords, date="", type_doc="", parametres={}):
    """
    Récupération d'une liste de PPN à partir de 
        - mots clés de la recherche (titre-auteur) : liste
        - date
        - type de documents (peut être vide)
        - paramètres
    """
    typeRecord4DoMyBiblio = "all"
    """all (pour tous les types de document),
           B (pour les livres),
           T (pour les périodiques),
           Y (pour les thèses version de soutenance),
           V (pour le matériel audio-visuel)"""
    typeRecordDic = {"TEX": "B", "VID": "V", "AUD": "V", "PER": "T", "THE": "Y"}
    if type_doc in typeRecordDic:
        typeRecord4DoMyBiblio = typeRecordDic[type_doc]
    kw = " ".join(keywords)
    Listeppn = []
    # On prévoit 2 URL : par défaut, requête sur l'API DoMyBiblio (XML)
    # Si plante > screenscraping de DoMyBiblio version HTML
    url1 = "".join(
        [
            "http://domybiblio.net/search/search_api.php?type_search=all&q=",
            urllib.parse.quote(kw),
            "&type_doc=",
            typeRecord4DoMyBiblio,
            "&period=",
            date,
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
            date,
            "&pageID=1&wp=false&idref=false&loc=false",
        ]
    )
    try:
        type_page = "xml"
        page = etree.parse(request.urlopen(url1, timeout=20))
    except ConnectionResetError:
        type_page = "html"
        test, result = testURLurlopen(url2, display=False)
        if (test):
            page = parse(result)
        else:
        #    print("erreur XML timeout, puis erreur HTML")
            type_page = ""
    except socket.timeout:
        type_page = "html"
        test, result = testURLurlopen(url2, display=False)
        if (test):
            page = parse(result)
        else:
        #    print("erreur XML timeout, puis erreur HTML")
            type_page = ""
    except urllib.error.HTTPError:
        type_page = "html"
        test, result = testURLurlopen(url2, display=False)
        if (test):
            page = parse(result)
        else:
            type_page = ""
        #    print("erreur XML HTTPerror, puis erreur HTML")
    except urllib.error.URLError:
        type_page = "html"
        test, result = testURLurlopen(url2, display=False)
        if (test):
            page = parse(result)
        else:
            type_page = ""
        #    print("erreur XML HTTPerror, puis erreur HTML")
    except etree.XMLSyntaxError:
        # problème de conformité XML du résultat
        type_page = "html"
        test, result = testURLurlopen(url2, display=False)
        if (test):
            page = parse(result)
        else:
            type_page = ""
    except http.client.RemoteDisconnected:
        type_page = ""
    if (type_page == "html"):
        liste_resultats = page.xpath("//li[@class='list-group-item']/a")
        for lien in liste_resultats:
            href = lien.get("href")
            ppn = "PPN" + href.split("/")[-1].split("&")[0].strip()
            if ("id=" in ppn):
                ppn = ppn[ppn.find("id="):].replace("id=", "").split("&")[0].strip()
            Listeppn.append(ppn)
    elif (type_page == "xml"):
        liste_resultats = page.xpath("//records/record")
        nb_results = int(page.find(".//results").text)
        for record in liste_resultats:
            ppn = record.find("identifier").text
            Listeppn.append(ppn)
        if nb_results > 10:
            domybiblio2ppn_pages_suivantes(
                kw, Listeppn, nb_results, 2,
                date, type_doc, parametres
            )
    # Si on trouve un PPN, on ouvre la notice pour voir s'il n'y a pas un ARK
    # déclaré comme équivalent --> dans ce cas on récupère l'ARK
    Listeppn = ",".join([ppn for ppn in Listeppn if ppn != ""])
    return Listeppn


def domybiblio2ppn_pages_suivantes(keywords, Listeppn, 
                                   nb_results, i,
                                   date, type_doc, parametres):
    """
    Récupération des résultats des pages suivantes de DoMyBiblio
    (au-delà du 10e résultat)
    """
    while (nb_results >= i*10):
        url = "".join([
            "http://domybiblio.net/search/search_api.php?type_search=all&q=",
            urllib.parse.quote(keywords),
            "&type_doc=", type_doc,
            "&period=", date,
            "&pageID=" + str(i) + "&wp=false&idref=false&loc=false"]
            )
        (test, results) = testURLetreeParse(url)
        if test:
            for record in results.xpath("//records/record"):
                ppn = "PPN" + record.find("identifier").text
                Listeppn.append(ppn)
        i += 1
    return Listeppn




def timestamp():
    """Renvoie l'horodatage sous la forme 
    2018-11-08 12:07:09.552751
    """
    timest = datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H-%M-%S")
    return timest

if __name__ == '__main__':
    access_to_network = main.check_access_to_network()
    if(access_to_network is True):
        last_version = main.check_last_compilation(main.programID)
    main.formulaire_main(access_to_network, last_version)
    # formulaire_marc2tables(access_to_network,last_version)
