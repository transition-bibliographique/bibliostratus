# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 21:21:17 2018

@author: Lully
Fonctions et classes génériques pour Bibliostratus 
"""

import http.client
import urllib.parse
import re
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
import itertools as IT


from lxml import etree
from lxml.html import parse
from collections import defaultdict
from unidecode import unidecode

import pymarc as mc

import main
import marc2tables
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
    ".", ",", ";", ":", "?", "!", "%", "$", "£", "€", "#", '"', "&", "~",
    "{", "(", "[", "`", r"\\", "_", "@", ")", "]", "}", "=", "+", "*", r"/", "<",
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


def clean_string(string, replaceSpaces=False, replaceTirets=False):
    """
    Nettoyage d'une chaîne de caractères: accents, ponctuations, majuscules
    En option : 
        - suppression des espaces
        - suppression des tirets
    """
    punctuation = [
                   ".", ",", ";", ":", "?", "!", "%", "$", "£", "€", "#", '"', "&", "~",
                   "{", "(", "[", "`", r"\\", "_", "@", ")", "]", "}", "=", "+", "*", r"/", "<",
                   ">", ")", "}"
                  ]
    string = unidecode(string.lower())
    for sign in punctuation:
        string = string.replace(sign, " ")
    string = string.replace("'", " ")
    if replaceTirets:
        string = string.replace("-", " ")
    if replaceSpaces:
        string = string.replace(" ", "")
    string = ' '.join(s for s in string.split() if s != "")
    string = string.strip()
    return string


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


def convertnumbers_chars(string):
    """
    Convertit les nombres d'un titre (écrits en lettres) en chiffres
    Si rien ne correspond, essaye de convertir les chiffres en mots
    Si aucune conversion réalisée, renvoie un str vide
    """
    new_str = string2numbers(string)
    if new_str == "":
        new_str = numbers2string(string)
    return new_str


def numbers2string(string):
    """
    Dans une chaîne de caractères, remplace les nombres (chiffres)
    en mots
    Si aucun chiffre, renvoie un str vide
    """
    new_str = []
    string = main.clean_string(string).split()
    test = False
    for el in string:
        if RepresentsInt(el):
            str_val = int2strings(int(el))
            new_str.append(str_val)
            test = True
        else:
            new_str.append(el)
    new_str = " ".join(new_str)
    if test:
        return new_str
    else:
        return ""


def int2strings(number):
    """
    Conversion d'un nombre en mot
    """
    string = ""
    try:
        if (0 <= number <= 1000):
            string = main.clean_string(numbers2letters[number])
        elif (1000 < number < 999999):
            milliers = main.clean_string(numbers2letters[round(number/1000)]) + " mille"
            milliers = milliers.replace("un mille", "mille")
            unites = main.clean_string(numbers2letters[int(str(number)[-3:])])
            if (unites == "zero"):
                unites = ""
            string = " ".join([milliers, unites]).strip()
    except KeyError:
        pass
    string = string.replace("-", " ").strip()
    return string


def string2numbers(string):
    """
    Pour un groupe de mots : si plusieurs mots consécutifs renvoient un nombre, 
    additionner ces nombres
    SI aucun mot ne correspond à un nombre : renvoie une chaîne de caractères vide
    """
    string = main.clean_string(string).replace(" et une", " un").replace(" et un", " un")
    test = False
    convert_string_list = []
    for el in string.split(" "):
        conv_el = string2int(el)
        if conv_el:
            test = True
            convert_string_list.append(conv_el)            
        else:
            convert_string_list.append(el)
    i = 0
    for el in convert_string_list:
        if RepresentsInt(el):
            el = int(el)
            test_next = True
            while (test_next and i < len(convert_string_list)):
                try:
                    if (RepresentsInt(convert_string_list[i + 1])):
                        next_val = int(convert_string_list[i + 1])
                        if next_val > el:
                            el = next_val * el
                        else:
                            el = next_val + el
                        convert_string_list.pop(i+1)
                        convert_string_list[i] = el
                    else:
                        test_next = False
                except IndexError:
                    test_next = False
            else:
                test_next = False
        i += 1
    if test:
        return " ".join([str(el) for el in convert_string_list])
    else:
        return ""


def string2int(string):
    """
    Pour un mot donné, renvoie la version numérique 
    si ce mot correspond à un nombre entre 1 et 1000
    """
    new_str = ""
    string = main.clean_string(string, False, True)
    if string in letters2numbers:
        new_str = letters2numbers[string]
    return new_str


def nettoyageOpus(string):
    # supprime la mention d'opus si existe :
    regex = r" (opus |op\.|op ) ?\d+"
    pattern = re.compile(regex)
    new_str = ""
    if (pattern.search(string) is not None):
        new_str = string[:pattern.search(string).span()[0]] + " " + string[pattern.search(string).span()[1]:]
        new_str = nettoyageTitrePourRecherche(new_str)
    return new_str


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
    except TypeError:
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


def nettoyageIdRef(idref_id, base="idref.fr/"):
    idref_nett = ""
    idref_id = unidecode_local(idref_id.lower())
    if (base in idref_id):
        idref_nett = idref_id[idref_id.find(base) + 9:]
        if (len(idref_nett) > 8):
            idref_nett = idref_nett[:9]
        else:
            idref_nett = ""
    elif ("ppn" in idref_id):
        idref_nett = idref_id[idref_id.find("ppn") + 3:]
        if (len(idref_nett) > 8):
            idref_nett = idref_nett[:9]
        else:
            idref_nett = ""
    return idref_nett
    

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


def set_proxy_session():
    import requests
    proxies = {
        'http': prefs["http_proxy"]["value"],
        'https': prefs["https_proxy"]["value"]
    }
    s = requests.Session()
    s.proxies = proxies
    # r = s.get('https://api.ipify.org?format=json').json()
    # print(r['ip'])


def testURLetreeParse(url, display=True, param_timeout=None):
    test = True
    resultat = ""
    try:
        resultat = etree.parse(request.urlopen(url, timeout=param_timeout))
    except UnicodeEncodeError as err:
        test = False
        if (display):
            print(url)
            print(err, param_timeout, "UnicodeEncodeError")
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
    except socket.timeout as err:
        test = False
        if display:
            print(err)
        url_access_pbs.append([url, "timeout > 5 secondes"])
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

def id_traitement2path(id_traitement):
    """
    Construit le chemin des fichiers en sortie
    de Bibliostratus
    """
    if (main.output_directory != [""]):
        filepath = os.path.join(main.output_directory[0], id_traitement)
    else:
        filepath = id_traitement
    return filepath


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

class IdRef:
    """Classe pour les identifiants IdRef (propriété des notices d'AUT)"""
    def __init__(self, string):  # Notre méthode constructeur
        self.init = string
        self.propre = nettoyageIdRef(self.init, "idref.fr/")

    def __str__(self):
        """Méthode permettant d'afficher plus joliment notre objet"""
        return "{}".format(self.init)

class PPN:
    """Classe pour les identifiants IdRef (propriété des notices d'AUT)"""
    def __init__(self, string):  # Notre méthode constructeur
        self.init = string
        self.propre = nettoyageIdRef(self.init, "sudoc.fr/")

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
    """Zone de nom d'auteur"""

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
        self.recherche_nombres_convertis = convertnumbers_chars(self.init)
        self.recherche_sans_num_opus = nettoyageOpus(self.init)

    def __str__(self):
        """Méthode permettant d'afficher plus joliment notre objet"""
        return f"Valeur initiale : \"{self.init}\"\n\
    controles : {self.controles}\n\
    recherche : {self.recherche}\n\
    recherche_nombres_convertis : {self.recherche_nombres_convertis}\n\
    recherche_sans_num_opus : {self.recherche_sans_num_opus}"


class Bib_record:
    """Classe définissant les propriétés d'une notice mise en entrée
    du module d'alignement"""

    def __init__(self, input_row, option_record):  # Notre méthode constructeur
        self.input_row = input_row
        self.option_record = option_record
        self.NumNot = input_row[0]
        self.frbnf = FRBNF(input_row[1])
        self.ppn = PPN(input_row[1])
        self.ark_init = input_row[2]
        self.isbn = International_id("")
        self.ean = International_id("")
        self.titre = Titre("")
        self.soustitre = Titre("")
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
        if (option_record == 6):
            self.type = "PAR"
            self.intermarc_type_record = "m"
            self.intermarc_type_doc = "c"
            self.ean = International_id(input_row[3])
            self.no_commercial = International_id(input_row[4], False)
            self.titre = Titre(input_row[5])
            self.soustitre = Titre(input_row[6])
            self.auteur = input_row[7]
            self.date = input_row[8]
            self.publisher = input_row[9]
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
        self.ppn = IdRef(input_row[1])
        self.ark_init = input_row[2]
        self.isni = Isni("")
        self.lastname = Name("")
        self.firstname = Name("")
        self.firstdate = Date("")
        self.lastdate = Date("")
        self.accesspoint = ""
        self.alignment_method = []
        if ("input_data_type" in parametres
           and parametres["input_data_type"] == 4):
            self.accesspoint = input_row[3].strip()
        else:
            self.isni = Isni(input_row[3])
            self.lastname = Name(input_row[4])
            self.firstname = Name(input_row[5])
            self.firstdate = Date(input_row[6])
            self.lastdate = Date(input_row[7])
            

class Bib_Aut_record:
    """Classe définissant les propriétés d'une notice bibliographique
    avec métadonnées AUT pour un alignement de la notice d'autorité
    grâce à la combinaison Titre + Auteur"""

    def __init__(self, input_row, parametres):  # Notre méthode constructeur
        self.metas_init = input_row[1:]
        self.NumNot = input_row[0]
        self.type = None
        self.NumNot_bib = input_row[1]
        self.ark_bib_init = input_row[2]
        self.frbnf_bib = FRBNF(input_row[3])
        self.isbn_bib = International_id(input_row[4])
        self.isbn = International_id(input_row[4])
        self.ean = International_id(input_row[4])
        self.auteur = f"{input_row[9]} {input_row[8]}"
        self.date = input_row[6]
        self.tome = ""
        self.publisher = ""
        self.no_commercial = International_id("")
        self.issn = International_id("")
        self.pubPlace = ""
        self.titre = Titre(input_row[5])
        self.soustitre = Titre("")
        self.pubdate = input_row[6]
        self.pubdate_nett = nettoyageDate(self.pubdate)
        self.isni = Isni(input_row[7])
        self.lastname = Name(input_row[8])
        self.firstname = Name(input_row[9])
        self.author_dates = input_row[10]
        self.alignment_method = []
    
        self.date_debut = self.author_dates
        if (self.date_debut.find("av") > 0):
            self.date_debut = self.date_debut[:self.date_debut.find("av")]
        elif (self.date_debut.find("-") > 0):
            self.date_debut = self.date_debut[:self.date_debut.find("-")]
        self.date_debut = main.clean_string(self.date_debut, False, True)
    
    def __str__(self):
        return f"metas_init : {self.metas_init}\n\
NumNot : {self.NumNot}\n\
type : {self.type}\n\
NumNot_bib : {self.NumNot_bib}\n\
ark_bib_init : {self.ark_bib_init}\n\
frbnf_bib : {self.frbnf_bib}\n\
isbn_bib : {self.isbn_bib.init}\n\
titre : {self.titre.init}\n\
pubdate : {self.pubdate}\n\
pubdate_nett : {self.pubdate_nett}\n\
isni : {self.isni}\n\
lastname : {self.lastname}\n\
firstname : {self.firstname}\n\
author_dates : {self.author_dates}"

class XML2record:
    """
    En entrée, une notice MarcXML
    En sortie, fournit un objet Bib_record manipulable
    pour un alignement 
    record_type: 1 = BIB, 2 = AUT

    """
    def __init__(self, xml_record, record_type=1, all_metas=False):  # Notre méthode constructeur
        self.init = xml_record
        self.pymarc_record = xml2pymarcrecord(xml_record)
        self.doc_record = None
        if (record_type == 1):
            self.metadata, self.doc_record = marc2tables.record2listemetas(self.pymarc_record, 1,
                                                                           all_metas)
            self.record = Bib_record(self.metadata, record_type)
        else:
            self.metadata, self.doc_record = marc2tables.record2listemetas(self.pymarc_record, 2,
                                                                            )
            self.record = Aut_record(self.metadata, record_type)


class XMLaut2record:
    """
    En entrée, une notice MarcXML
    En sortie, fournit un objet Aut_record manipulable
    pour un alignement 
    """
    def __init__(self, xml_record):  # Notre méthode constructeur
        self.init = xml_record
        self.record_type = None
        self.metadata = marc2tables.record2listemetas(xml_record, 2)
        self.record = Aut_record(self.metadata, self.record_type)


class Alignment_result:
    """
    Gère les résultats d'un alignement : 
    le ou les identifiants trouvés, la méthode utilisée
    les données en entrée (dont le numéro de notice)
    """
    def __init__(self, input_record, ark, parametres):  # Notre méthode constructeur
        self.input_record = input_record
        self.NumNot = input_record.NumNot
        self.ids_str = ark
        self.ids_list = self.ids_str.split(",")
        self.ids_list = [el for el in self.ids_list if el]
        self.nb_ids = len(self.ids_list)
        self.alignment_method_list = input_record.alignment_method
        if (len(list(set(input_record.alignment_method))) == 1):
            self.alignment_method_list = [input_record.alignment_method[0]]
        self.alignment_method_str = ",".join(self.alignment_method_list)
        if (self.nb_ids == 0):
            self.alignment_method_str = ""
        self.liste_metadonnees = [
                                    input_record.NumNot,
                                    self.nb_ids,
                                    self.ids_str,
                                    self.alignment_method_str
                                ] 
        if ("type_notices_rameau" in parametres
           and parametres["input_data_type"] == 4):
            self.liste_metadonnees.append(id_rameau2type(ark, parametres["type_notices_rameau"]))
        self.liste_metadonnees.extend(input_record.metas_init)
    def __str__(self):
        """Méthode permettant d'afficher plus joliment notre objet"""
        return "{} : {}\nNombre d'ID trouvés : {}".format(self.NumNot, self.ids_str, self.nb_ids)


def id_rameau2type(arks, dict_ark2type_rameau):
    types = []
    for ark in arks.split(","):
        if ark in dict_ark2type_rameau:
            types.append(dict_ark2type_rameau[ark])
    types = ",".join(types)
    return types

class Id4record:
    """
    Objet à partir d'une ligne en entrée du module rouge (ark2record)
    """
    def __init__(self, row, parametres={}): 
        try:
            self.NumNot = row[0]
            self.aligned_id = Aligned_id(row[-1])
            self.dict_rec = {"record": None}
        except IndexError:
            self.NumNot = ""
            self.aligned_id = ""

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


def field2subfield(field, subfield, nb_occ="all", sep="~"):
    path = "*[@code='" + subfield + "']"
    listeValues = []
    if (nb_occ == "first" or nb_occ == 1):
        if (field.find(path) is not None and
                field.find(path).text is not None):
            val = field.find(path).text
            listeValues.append(val)
    else:
        for occ in field.xpath(path):
            if (occ.text is not None):
                listeValues.append(occ.text)
    listeValues = sep.join(listeValues)
    return listeValues


def field2value(field):
    try:
        value = " ".join([" ".join(["$" + el.get("code"), el.text]) for el in field.xpath("*")])
    except ValueError:
        value = ""
    return value


def record2fieldvalue(record, zone):
    #Pour chaque zone indiquée dans le formulaire, séparée par un point-virgule, on applique le traitement ci-dessous
    value = ""
    field = ""
    subfields = []
    if (zone.find("$") > 0):
        #si la zone contient une précision de sous-zone
        zone_ss_zones = zone.split("$")
        field = zone_ss_zones[0]
        fieldPath = ".//*[@tag='" + field + "']"
        i = 0
        for field in record.xpath(fieldPath):
            i = i+1
            j = 0
            for subfield in zone_ss_zones[1:]:
                sep = ""
                if (i > 1 and j == 0):
                    sep = "~"
                j = j+1
                subfields.append(subfield)
                subfieldpath = "*[@code='"+subfield+"']"
                if (field.find(subfieldpath) is not None):
                    if (field.find(subfieldpath).text != ""):
                        valtmp = field.find(subfieldpath).text
                        #valtmp = field.find(subfieldpath).text.encode("utf-8").decode("utf-8", "ignore")
                        prefixe = ""
                        if (len(zone_ss_zones) > 2):
                            prefixe = " $" + subfield + " "
                        value = str(value) + str(sep) + str(prefixe) + str(valtmp)
    else:
        #si pas de sous-zone précisée
        field = zone
        path = ""
        if (field == "000"):
            path = ".//*[local-name()='leader']"
        else:
            path = ".//*[@tag='" + field + "']"
        i = 0        
        for field in record.xpath(path):
            i = i+1
            j = 0
            if (field.find("*", namespaces=ns_bnf) is not None):
                sep = ""
                for subfield in field.xpath("*"):
                    sep = ""
                    if (i > 1 and j == 0):
                        sep = "~"
                    #print (subfield.get("code") + " : " + str(j) + " // sep : " + sep)
                    j = j+1
                    valuesubfield = ""
                    if (subfield.text != ""):
                        valuesubfield = str(subfield.text)
                        if (valuesubfield == "None"):
                            valuesubfield = ""
                    value = value + sep + " $" + subfield.get("code") + " " + valuesubfield
            else:
                value = field.find(".").text
    if (value != ""):
        if (value[0] == "~"):
            value = value[1:]
    return value.strip()


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



def line2report(line, report, i=0, display=True):
    """
    Envoie une line (liste) dans un fichier.
    Sauf demande contraire, affiche la ligne
    dans le terminal avec un compteur
    """
    if display:
        if i:
            print(i, line)
        else:
            print(line)
    report.write("\t".join(line) + "\n")


numbers2letters = {0: "Zéro",
1: "Un",
2: "Deux",
3: "Trois",
4: "Quatre",
5: "Cinq",
6: "Six",
7: "Sept",
8: "Huit",
9: "Neuf",
10: "Dix",
11: "Onze",
12: "Douze",
13: "Treize",
14: "Quatorze",
15: "Quinze",
16: "Seize",
17: "Dix-sept",
18: "Dix-huit",
19: "Dix-neuf",
20: "Vingt",
21: "Vingt et un",
22: "Vingt-deux",
23: "Vingt-trois",
24: "Vingt-quatre",
25: "Vingt-cinq",
26: "Vingt-six",
27: "Vingt-sept",
28: "Vingt-huit",
29: "Vingt-neuf",
30: "Trente",
31: "Trente et un",
32: "Trente-deux",
33: "Trente-trois",
34: "Trente-quatre",
35: "Trente-cinq",
36: "Trente-six",
37: "Trente-sept",
38: "Trente-huit",
39: "Trente-neuf",
40: "Quarante",
41: "Quarante et un",
42: "Quarante-deux",
43: "Quarante-trois",
44: "Quarante-quatre",
45: "Quarante-cinq",
46: "Quarante-six",
47: "Quarante-sept",
48: "Quarante-huit",
49: "Quarante-neuf",
50: "Cinquante",
51: "Cinquante et un",
52: "Cinquante-deux",
53: "Cinquante-trois",
54: "Cinquante-quatre",
55: "Cinquante-cinq",
56: "Cinquante-six",
57: "Cinquante-sept",
58: "Cinquante-huit",
59: "Cinquante-neuf",
60: "Soixante",
61: "Soixante et un",
62: "Soixante-deux",
63: "Soixante-trois",
64: "Soixante-quatre",
65: "Soixante-cinq",
66: "Soixante-six",
67: "Soixante-sept",
68: "Soixante-huit",
69: "Soixante-neuf",
70: "Soixante-dix",
71: "Soixante et onze",
72: "Soixante-douze",
73: "Soixante-treize",
74: "Soixante-quatorze",
75: "Soixante-quinze",
76: "Soixante-seize",
77: "Soixante-dix-sept",
78: "Soixante-dix-huit",
79: "Soixante-dix-neuf",
80: "Quatre-vingts",
81: "Quatre-vingt-un",
82: "Quatre-vingt-deux",
83: "Quatre-vingt-trois",
84: "Quatre-vingt-quatre",
85: "Quatre-vingt-cinq",
86: "Quatre-vingt-six",
87: "Quatre-vingt-sept",
88: "Quatre-vingt-huit",
89: "Quatre-vingt-neuf",
90: "Quatre-vingt-dix",
91: "Quatre-vingt-onze",
92: "Quatre-vingt-douze",
93: "Quatre-vingt-treize",
94: "Quatre-vingt-quatorze",
95: "Quatre-vingt-quinze",
96: "Quatre-vingt-seize",
97: "Quatre-vingt-dix-sept",
98: "Quatre-vingt-dix-huit",
99: "Quatre-vingt-dix-neuf",
100: "Cent",
101: "Cent un",
102: "Cent deux",
103: "Cent trois",
104: "Cent quatre",
105: "Cent cinq",
106: "Cent six",
107: "Cent sept",
108: "Cent huit",
109: "Cent neuf",
110: "Cent dix",
111: "Cent onze",
112: "Cent douze",
113: "Cent treize",
114: "Cent quatorze",
115: "Cent quinze",
116: "Cent seize",
117: "Cent dix-sept",
118: "Cent dix-huit",
119: "Cent dix-neuf",
120: "Cent vingt",
121: "Cent vingt et un",
122: "Cent vingt-deux",
123: "Cent vingt-trois",
124: "Cent vingt-quatre",
125: "Cent vingt-cinq",
126: "Cent vingt-six",
127: "Cent vingt-sept",
128: "Cent vingt-huit",
129: "Cent vingt-neuf",
130: "Cent trente",
131: "Cent trente et un",
132: "Cent trente-deux",
133: "Cent trente-trois",
134: "Cent trente-quatre",
135: "Cent trente-cinq",
136: "Cent trente-six",
137: "Cent trente-sept",
138: "Cent trente-huit",
139: "Cent trente-neuf",
140: "Cent quarante",
141: "Cent quarante et un",
142: "Cent quarante-deux",
143: "Cent quarante-trois",
144: "Cent quarante-quatre",
145: "Cent quarante-cinq",
146: "Cent quarante-six",
147: "Cent quarante-sept",
148: "Cent quarante-huit",
149: "Cent quarante-neuf",
150: "Cent cinquante",
151: "Cent cinquante et un",
152: "Cent cinquante-deux",
153: "Cent cinquante-trois",
154: "Cent cinquante-quatre",
155: "Cent cinquante-cinq",
156: "Cent cinquante-six",
157: "Cent cinquante-sept",
158: "Cent cinquante-huit",
159: "Cent cinquante-neuf",
160: "Cent soixante",
161: "Cent soixante et un",
162: "Cent soixante-deux",
163: "Cent soixante-trois",
164: "Cent soixante-quatre",
165: "Cent soixante-cinq",
166: "Cent soixante-six",
167: "Cent soixante-sept",
168: "Cent soixante-huit",
169: "Cent soixante-neuf",
170: "Cent soixante-dix",
171: "Cent soixante et onze",
172: "Cent soixante-douze",
173: "Cent soixante-treize",
174: "Cent soixante-quatorze",
175: "Cent soixante-quinze",
176: "Cent soixante-seize",
177: "Cent soixante-dix-sept",
178: "Cent soixante-dix-huit",
179: "Cent soixante-dix-neuf",
180: "Cent quatre-vingts",
181: "Cent quatre-vingt-un",
182: "Cent quatre-vingt-deux",
183: "Cent quatre-vingt-trois",
184: "Cent quatre-vingt-quatre",
185: "Cent quatre-vingt-cinq",
186: "Cent quatre-vingt-six",
187: "Cent quatre-vingt-sept",
188: "Cent quatre-vingt-huit",
189: "Cent quatre-vingt-neuf",
190: "Cent quatre-vingt-dix",
191: "Cent quatre-vingt-onze",
192: "Cent quatre-vingt-douze",
193: "Cent quatre-vingt-treize",
194: "Cent quatre-vingt-quatorze",
195: "Cent quatre-vingt-quinze",
196: "Cent quatre-vingt-seize",
197: "Cent quatre-vingt-dix-sept",
198: "Cent quatre-vingt-dix-huit",
199: "Cent quatre-vingt-dix-neuf",
200: "Deux cents",
201: "Deux cent un",
202: "Deux cent deux",
203: "Deux cent trois",
204: "Deux cent quatre",
205: "Deux cent cinq",
206: "Deux cent six",
207: "Deux cent sept",
208: "Deux cent huit",
209: "Deux cent neuf",
210: "Deux cent dix",
211: "Deux cent onze",
212: "Deux cent douze",
213: "Deux cent treize",
214: "Deux cent quatorze",
215: "Deux cent quinze",
216: "Deux cent seize",
217: "Deux cent dix-sept",
218: "Deux cent dix-huit",
219: "Deux cent dix-neuf",
220: "Deux cent vingt",
221: "Deux cent vingt et un",
222: "Deux cent vingt-deux",
223: "Deux cent vingt-trois",
224: "Deux cent vingt-quatre",
225: "Deux cent vingt-cinq",
226: "Deux cent vingt-six",
227: "Deux cent vingt-sept",
228: "Deux cent vingt-huit",
229: "Deux cent vingt-neuf",
230: "Deux cent trente",
231: "Deux cent trente et un",
232: "Deux cent trente-deux",
233: "Deux cent trente-trois",
234: "Deux cent trente-quatre",
235: "Deux cent trente-cinq",
236: "Deux cent trente-six",
237: "Deux cent trente-sept",
238: "Deux cent trente-huit",
239: "Deux cent trente-neuf",
240: "Deux cent quarante",
241: "Deux cent quarante et un",
242: "Deux cent quarante-deux",
243: "Deux cent quarante-trois",
244: "Deux cent quarante-quatre",
245: "Deux cent quarante-cinq",
246: "Deux cent quarante-six",
247: "Deux cent quarante-sept",
248: "Deux cent quarante-huit",
249: "Deux cent quarante-neuf",
250: "Deux cent cinquante",
251: "Deux cent cinquante et un",
252: "Deux cent cinquante-deux",
253: "Deux cent cinquante-trois",
254: "Deux cent cinquante-quatre",
255: "Deux cent cinquante-cinq",
256: "Deux cent cinquante-six",
257: "Deux cent cinquante-sept",
258: "Deux cent cinquante-huit",
259: "Deux cent cinquante-neuf",
260: "Deux cent soixante",
261: "Deux cent soixante et un",
262: "Deux cent soixante-deux",
263: "Deux cent soixante-trois",
264: "Deux cent soixante-quatre",
265: "Deux cent soixante-cinq",
266: "Deux cent soixante-six",
267: "Deux cent soixante-sept",
268: "Deux cent soixante-huit",
269: "Deux cent soixante-neuf",
270: "Deux cent soixante-dix",
271: "Deux cent soixante et onze",
272: "Deux cent soixante-douze",
273: "Deux cent soixante-treize",
274: "Deux cent soixante-quatorze",
275: "Deux cent soixante-quinze",
276: "Deux cent soixante-seize",
277: "Deux cent soixante-dix-sept",
278: "Deux cent soixante-dix-huit",
279: "Deux cent soixante-dix-neuf",
280: "Deux cent quatre-vingts",
281: "Deux cent quatre-vingt-un",
282: "Deux cent quatre-vingt-deux",
283: "Deux cent quatre-vingt-trois",
284: "Deux cent quatre-vingt-quatre",
285: "Deux cent quatre-vingt-cinq",
286: "Deux cent quatre-vingt-six",
287: "Deux cent quatre-vingt-sept",
288: "Deux cent quatre-vingt-huit",
289: "Deux cent quatre-vingt-neuf",
290: "Deux cent quatre-vingt-dix",
291: "Deux cent quatre-vingt-onze",
292: "Deux cent quatre-vingt-douze",
293: "Deux cent quatre-vingt-treize",
294: "Deux cent quatre-vingt-quatorze",
295: "Deux cent quatre-vingt-quinze",
296: "Deux cent quatre-vingt-seize",
297: "Deux cent quatre-vingt-dix-sept",
298: "Deux cent quatre-vingt-dix-huit",
299: "Deux cent quatre-vingt-dix-neuf",
300: "Trois cents",
301: "Trois cent un",
302: "Trois cent deux",
303: "Trois cent trois",
304: "Trois cent quatre",
305: "Trois cent cinq",
306: "Trois cent six",
307: "Trois cent sept",
308: "Trois cent huit",
309: "Trois cent neuf",
310: "Trois cent dix",
311: "Trois cent onze",
312: "Trois cent douze",
313: "Trois cent treize",
314: "Trois cent quatorze",
315: "Trois cent quinze",
316: "Trois cent seize",
317: "Trois cent dix-sept",
318: "Trois cent dix-huit",
319: "Trois cent dix-neuf",
320: "Trois cent vingt",
321: "Trois cent vingt et un",
322: "Trois cent vingt-deux",
323: "Trois cent vingt-trois",
324: "Trois cent vingt-quatre",
325: "Trois cent vingt-cinq",
326: "Trois cent vingt-six",
327: "Trois cent vingt-sept",
328: "Trois cent vingt-huit",
329: "Trois cent vingt-neuf",
330: "Trois cent trente",
331: "Trois cent trente et un",
332: "Trois cent trente-deux",
333: "Trois cent trente-trois",
334: "Trois cent trente-quatre",
335: "Trois cent trente-cinq",
336: "Trois cent trente-six",
337: "Trois cent trente-sept",
338: "Trois cent trente-huit",
339: "Trois cent trente-neuf",
340: "Trois cent quarante",
341: "Trois cent quarante et un",
342: "Trois cent quarante-deux",
343: "Trois cent quarante-trois",
344: "Trois cent quarante-quatre",
345: "Trois cent quarante-cinq",
346: "Trois cent quarante-six",
347: "Trois cent quarante-sept",
348: "Trois cent quarante-huit",
349: "Trois cent quarante-neuf",
350: "Trois cent cinquante",
351: "Trois cent cinquante et un",
352: "Trois cent cinquante-deux",
353: "Trois cent cinquante-trois",
354: "Trois cent cinquante-quatre",
355: "Trois cent cinquante-cinq",
356: "Trois cent cinquante-six",
357: "Trois cent cinquante-sept",
358: "Trois cent cinquante-huit",
359: "Trois cent cinquante-neuf",
360: "Trois cent soixante",
361: "Trois cent soixante et un",
362: "Trois cent soixante-deux",
363: "Trois cent soixante-trois",
364: "Trois cent soixante-quatre",
365: "Trois cent soixante-cinq",
366: "Trois cent soixante-six",
367: "Trois cent soixante-sept",
368: "Trois cent soixante-huit",
369: "Trois cent soixante-neuf",
370: "Trois cent soixante-dix",
371: "Trois cent soixante et onze",
372: "Trois cent soixante-douze",
373: "Trois cent soixante-treize",
374: "Trois cent soixante-quatorze",
375: "Trois cent soixante-quinze",
376: "Trois cent soixante-seize",
377: "Trois cent soixante-dix-sept",
378: "Trois cent soixante-dix-huit",
379: "Trois cent soixante-dix-neuf",
380: "Trois cent quatre-vingts",
381: "Trois cent quatre-vingt-un",
382: "Trois cent quatre-vingt-deux",
383: "Trois cent quatre-vingt-trois",
384: "Trois cent quatre-vingt-quatre",
385: "Trois cent quatre-vingt-cinq",
386: "Trois cent quatre-vingt-six",
387: "Trois cent quatre-vingt-sept",
388: "Trois cent quatre-vingt-huit",
389: "Trois cent quatre-vingt-neuf",
390: "Trois cent quatre-vingt-dix",
391: "Trois cent quatre-vingt-onze",
392: "Trois cent quatre-vingt-douze",
393: "Trois cent quatre-vingt-treize",
394: "Trois cent quatre-vingt-quatorze",
395: "Trois cent quatre-vingt-quinze",
396: "Trois cent quatre-vingt-seize",
397: "Trois cent quatre-vingt-dix-sept",
398: "Trois cent quatre-vingt-dix-huit",
399: "Trois cent quatre-vingt-dix-neuf",
400: "Quatre cents",
401: "Quatre cent un",
402: "Quatre cent deux",
403: "Quatre cent trois",
404: "Quatre cent quatre",
405: "Quatre cent cinq",
406: "Quatre cent six",
407: "Quatre cent sept",
408: "Quatre cent huit",
409: "Quatre cent neuf",
410: "Quatre cent dix",
411: "Quatre cent onze",
412: "Quatre cent douze",
413: "Quatre cent treize",
414: "Quatre cent quatorze",
415: "Quatre cent quinze",
416: "Quatre cent seize",
417: "Quatre cent dix-sept",
418: "Quatre cent dix-huit",
419: "Quatre cent dix-neuf",
420: "Quatre cent vingt",
421: "Quatre cent vingt et un",
422: "Quatre cent vingt-deux",
423: "Quatre cent vingt-trois",
424: "Quatre cent vingt-quatre",
425: "Quatre cent vingt-cinq",
426: "Quatre cent vingt-six",
427: "Quatre cent vingt-sept",
428: "Quatre cent vingt-huit",
429: "Quatre cent vingt-neuf",
430: "Quatre cent trente",
431: "Quatre cent trente et un",
432: "Quatre cent trente-deux",
433: "Quatre cent trente-trois",
434: "Quatre cent trente-quatre",
435: "Quatre cent trente-cinq",
436: "Quatre cent trente-six",
437: "Quatre cent trente-sept",
438: "Quatre cent trente-huit",
439: "Quatre cent trente-neuf",
440: "Quatre cent quarante",
441: "Quatre cent quarante et un",
442: "Quatre cent quarante-deux",
443: "Quatre cent quarante-trois",
444: "Quatre cent quarante-quatre",
445: "Quatre cent quarante-cinq",
446: "Quatre cent quarante-six",
447: "Quatre cent quarante-sept",
448: "Quatre cent quarante-huit",
449: "Quatre cent quarante-neuf",
450: "Quatre cent cinquante",
451: "Quatre cent cinquante et un",
452: "Quatre cent cinquante-deux",
453: "Quatre cent cinquante-trois",
454: "Quatre cent cinquante-quatre",
455: "Quatre cent cinquante-cinq",
456: "Quatre cent cinquante-six",
457: "Quatre cent cinquante-sept",
458: "Quatre cent cinquante-huit",
459: "Quatre cent cinquante-neuf",
460: "Quatre cent soixante",
461: "Quatre cent soixante et un",
462: "Quatre cent soixante-deux",
463: "Quatre cent soixante-trois",
464: "Quatre cent soixante-quatre",
465: "Quatre cent soixante-cinq",
466: "Quatre cent soixante-six",
467: "Quatre cent soixante-sept",
468: "Quatre cent soixante-huit",
469: "Quatre cent soixante-neuf",
470: "Quatre cent soixante-dix",
471: "Quatre cent soixante et onze",
472: "Quatre cent soixante-douze",
473: "Quatre cent soixante-treize",
474: "Quatre cent soixante-quatorze",
475: "Quatre cent soixante-quinze",
476: "Quatre cent soixante-seize",
477: "Quatre cent soixante-dix-sept",
478: "Quatre cent soixante-dix-huit",
479: "Quatre cent soixante-dix-neuf",
480: "Quatre cent quatre-vingts",
481: "Quatre cent quatre-vingt-un",
482: "Quatre cent quatre-vingt-deux",
483: "Quatre cent quatre-vingt-trois",
484: "Quatre cent quatre-vingt-quatre",
485: "Quatre cent quatre-vingt-cinq",
486: "Quatre cent quatre-vingt-six",
487: "Quatre cent quatre-vingt-sept",
488: "Quatre cent quatre-vingt-huit",
489: "Quatre cent quatre-vingt-neuf",
490: "Quatre cent quatre-vingt-dix",
491: "Quatre cent quatre-vingt-onze",
492: "Quatre cent quatre-vingt-douze",
493: "Quatre cent quatre-vingt-treize",
494: "Quatre cent quatre-vingt-quatorze",
495: "Quatre cent quatre-vingt-quinze",
496: "Quatre cent quatre-vingt-seize",
497: "Quatre cent quatre-vingt-dix-sept",
498: "Quatre cent quatre-vingt-dix-huit",
499: "Quatre cent quatre-vingt-dix-neuf",
500: "Cinq cents",
501: "Cinq cent un",
502: "Cinq cent deux",
503: "Cinq cent trois",
504: "Cinq cent quatre",
505: "Cinq cent cinq",
506: "Cinq cent six",
507: "Cinq cent sept",
508: "Cinq cent huit",
509: "Cinq cent neuf",
510: "Cinq cent dix",
511: "Cinq cent onze",
512: "Cinq cent douze",
513: "Cinq cent treize",
514: "Cinq cent quatorze",
515: "Cinq cent quinze",
516: "Cinq cent seize",
517: "Cinq cent dix-sept",
518: "Cinq cent dix-huit",
519: "Cinq cent dix-neuf",
520: "Cinq cent vingt",
521: "Cinq cent vingt et un",
522: "Cinq cent vingt-deux",
523: "Cinq cent vingt-trois",
524: "Cinq cent vingt-quatre",
525: "Cinq cent vingt-cinq",
526: "Cinq cent vingt-six",
527: "Cinq cent vingt-sept",
528: "Cinq cent vingt-huit",
529: "Cinq cent vingt-neuf",
530: "Cinq cent trente",
531: "Cinq cent trente et un",
532: "Cinq cent trente-deux",
533: "Cinq cent trente-trois",
534: "Cinq cent trente-quatre",
535: "Cinq cent trente-cinq",
536: "Cinq cent trente-six",
537: "Cinq cent trente-sept",
538: "Cinq cent trente-huit",
539: "Cinq cent trente-neuf",
540: "Cinq cent quarante",
541: "Cinq cent quarante et un",
542: "Cinq cent quarante-deux",
543: "Cinq cent quarante-trois",
544: "Cinq cent quarante-quatre",
545: "Cinq cent quarante-cinq",
546: "Cinq cent quarante-six",
547: "Cinq cent quarante-sept",
548: "Cinq cent quarante-huit",
549: "Cinq cent quarante-neuf",
550: "Cinq cent cinquante",
551: "Cinq cent cinquante et un",
552: "Cinq cent cinquante-deux",
553: "Cinq cent cinquante-trois",
554: "Cinq cent cinquante-quatre",
555: "Cinq cent cinquante-cinq",
556: "Cinq cent cinquante-six",
557: "Cinq cent cinquante-sept",
558: "Cinq cent cinquante-huit",
559: "Cinq cent cinquante-neuf",
560: "Cinq cent soixante",
561: "Cinq cent soixante et un",
562: "Cinq cent soixante-deux",
563: "Cinq cent soixante-trois",
564: "Cinq cent soixante-quatre",
565: "Cinq cent soixante-cinq",
566: "Cinq cent soixante-six",
567: "Cinq cent soixante-sept",
568: "Cinq cent soixante-huit",
569: "Cinq cent soixante-neuf",
570: "Cinq cent soixante-dix",
571: "Cinq cent soixante et onze",
572: "Cinq cent soixante-douze",
573: "Cinq cent soixante-treize",
574: "Cinq cent soixante-quatorze",
575: "Cinq cent soixante-quinze",
576: "Cinq cent soixante-seize",
577: "Cinq cent soixante-dix-sept",
578: "Cinq cent soixante-dix-huit",
579: "Cinq cent soixante-dix-neuf",
580: "Cinq cent quatre-vingts",
581: "Cinq cent quatre-vingt-un",
582: "Cinq cent quatre-vingt-deux",
583: "Cinq cent quatre-vingt-trois",
584: "Cinq cent quatre-vingt-quatre",
585: "Cinq cent quatre-vingt-cinq",
586: "Cinq cent quatre-vingt-six",
587: "Cinq cent quatre-vingt-sept",
588: "Cinq cent quatre-vingt-huit",
589: "Cinq cent quatre-vingt-neuf",
590: "Cinq cent quatre-vingt-dix",
591: "Cinq cent quatre-vingt-onze",
592: "Cinq cent quatre-vingt-douze",
593: "Cinq cent quatre-vingt-treize",
594: "Cinq cent quatre-vingt-quatorze",
595: "Cinq cent quatre-vingt-quinze",
596: "Cinq cent quatre-vingt-seize",
597: "Cinq cent quatre-vingt-dix-sept",
598: "Cinq cent quatre-vingt-dix-huit",
599: "Cinq cent quatre-vingt-dix-neuf",
600: "Six cents",
601: "Six cent un",
602: "Six cent deux",
603: "Six cent trois",
604: "Six cent quatre",
605: "Six cent cinq",
606: "Six cent six",
607: "Six cent sept",
608: "Six cent huit",
609: "Six cent neuf",
610: "Six cent dix",
611: "Six cent onze",
612: "Six cent douze",
613: "Six cent treize",
614: "Six cent quatorze",
615: "Six cent quinze",
616: "Six cent seize",
617: "Six cent dix-sept",
618: "Six cent dix-huit",
619: "Six cent dix-neuf",
620: "Six cent vingt",
621: "Six cent vingt et un",
622: "Six cent vingt-deux",
623: "Six cent vingt-trois",
624: "Six cent vingt-quatre",
625: "Six cent vingt-cinq",
626: "Six cent vingt-six",
627: "Six cent vingt-sept",
628: "Six cent vingt-huit",
629: "Six cent vingt-neuf",
630: "Six cent trente",
631: "Six cent trente et un",
632: "Six cent trente-deux",
633: "Six cent trente-trois",
634: "Six cent trente-quatre",
635: "Six cent trente-cinq",
636: "Six cent trente-six",
637: "Six cent trente-sept",
638: "Six cent trente-huit",
639: "Six cent trente-neuf",
640: "Six cent quarante",
641: "Six cent quarante et un",
642: "Six cent quarante-deux",
643: "Six cent quarante-trois",
644: "Six cent quarante-quatre",
645: "Six cent quarante-cinq",
646: "Six cent quarante-six",
647: "Six cent quarante-sept",
648: "Six cent quarante-huit",
649: "Six cent quarante-neuf",
650: "Six cent cinquante",
651: "Six cent cinquante et un",
652: "Six cent cinquante-deux",
653: "Six cent cinquante-trois",
654: "Six cent cinquante-quatre",
655: "Six cent cinquante-cinq",
656: "Six cent cinquante-six",
657: "Six cent cinquante-sept",
658: "Six cent cinquante-huit",
659: "Six cent cinquante-neuf",
660: "Six cent soixante",
661: "Six cent soixante et un",
662: "Six cent soixante-deux",
663: "Six cent soixante-trois",
664: "Six cent soixante-quatre",
665: "Six cent soixante-cinq",
666: "Six cent soixante-six",
667: "Six cent soixante-sept",
668: "Six cent soixante-huit",
669: "Six cent soixante-neuf",
670: "Six cent soixante-dix",
671: "Six cent soixante et onze",
672: "Six cent soixante-douze",
673: "Six cent soixante-treize",
674: "Six cent soixante-quatorze",
675: "Six cent soixante-quinze",
676: "Six cent soixante-seize",
677: "Six cent soixante-dix-sept",
678: "Six cent soixante-dix-huit",
679: "Six cent soixante-dix-neuf",
680: "Six cent quatre-vingts",
681: "Six cent quatre-vingt-un",
682: "Six cent quatre-vingt-deux",
683: "Six cent quatre-vingt-trois",
684: "Six cent quatre-vingt-quatre",
685: "Six cent quatre-vingt-cinq",
686: "Six cent quatre-vingt-six",
687: "Six cent quatre-vingt-sept",
688: "Six cent quatre-vingt-huit",
689: "Six cent quatre-vingt-neuf",
690: "Six cent quatre-vingt-dix",
691: "Six cent quatre-vingt-onze",
692: "Six cent quatre-vingt-douze",
693: "Six cent quatre-vingt-treize",
694: "Six cent quatre-vingt-quatorze",
695: "Six cent quatre-vingt-quinze",
696: "Six cent quatre-vingt-seize",
697: "Six cent quatre-vingt-dix-sept",
698: "Six cent quatre-vingt-dix-huit",
699: "Six cent quatre-vingt-dix-neuf",
700: "Sept cents",
701: "Sept cent un",
702: "Sept cent deux",
703: "Sept cent trois",
704: "Sept cent quatre",
705: "Sept cent cinq",
706: "Sept cent six",
707: "Sept cent sept",
708: "Sept cent huit",
709: "Sept cent neuf",
710: "Sept cent dix",
711: "Sept cent onze",
712: "Sept cent douze",
713: "Sept cent treize",
714: "Sept cent quatorze",
715: "Sept cent quinze",
716: "Sept cent seize",
717: "Sept cent dix-sept",
718: "Sept cent dix-huit",
719: "Sept cent dix-neuf",
720: "Sept cent vingt",
721: "Sept cent vingt et un",
722: "Sept cent vingt-deux",
723: "Sept cent vingt-trois",
724: "Sept cent vingt-quatre",
725: "Sept cent vingt-cinq",
726: "Sept cent vingt-six",
727: "Sept cent vingt-sept",
728: "Sept cent vingt-huit",
729: "Sept cent vingt-neuf",
730: "Sept cent trente",
731: "Sept cent trente et un",
732: "Sept cent trente-deux",
733: "Sept cent trente-trois",
734: "Sept cent trente-quatre",
735: "Sept cent trente-cinq",
736: "Sept cent trente-six",
737: "Sept cent trente-sept",
738: "Sept cent trente-huit",
739: "Sept cent trente-neuf",
740: "Sept cent quarante",
741: "Sept cent quarante et un",
742: "Sept cent quarante-deux",
743: "Sept cent quarante-trois",
744: "Sept cent quarante-quatre",
745: "Sept cent quarante-cinq",
746: "Sept cent quarante-six",
747: "Sept cent quarante-sept",
748: "Sept cent quarante-huit",
749: "Sept cent quarante-neuf",
750: "Sept cent cinquante",
751: "Sept cent cinquante et un",
752: "Sept cent cinquante-deux",
753: "Sept cent cinquante-trois",
754: "Sept cent cinquante-quatre",
755: "Sept cent cinquante-cinq",
756: "Sept cent cinquante-six",
757: "Sept cent cinquante-sept",
758: "Sept cent cinquante-huit",
759: "Sept cent cinquante-neuf",
760: "Sept cent soixante",
761: "Sept cent soixante et un",
762: "Sept cent soixante-deux",
763: "Sept cent soixante-trois",
764: "Sept cent soixante-quatre",
765: "Sept cent soixante-cinq",
766: "Sept cent soixante-six",
767: "Sept cent soixante-sept",
768: "Sept cent soixante-huit",
769: "Sept cent soixante-neuf",
770: "Sept cent soixante-dix",
771: "Sept cent soixante et onze",
772: "Sept cent soixante-douze",
773: "Sept cent soixante-treize",
774: "Sept cent soixante-quatorze",
775: "Sept cent soixante-quinze",
776: "Sept cent soixante-seize",
777: "Sept cent soixante-dix-sept",
778: "Sept cent soixante-dix-huit",
779: "Sept cent soixante-dix-neuf",
780: "Sept cent quatre-vingts",
781: "Sept cent quatre-vingt-un",
782: "Sept cent quatre-vingt-deux",
783: "Sept cent quatre-vingt-trois",
784: "Sept cent quatre-vingt-quatre",
785: "Sept cent quatre-vingt-cinq",
786: "Sept cent quatre-vingt-six",
787: "Sept cent quatre-vingt-sept",
788: "Sept cent quatre-vingt-huit",
789: "Sept cent quatre-vingt-neuf",
790: "Sept cent quatre-vingt-dix",
791: "Sept cent quatre-vingt-onze",
792: "Sept cent quatre-vingt-douze",
793: "Sept cent quatre-vingt-treize",
794: "Sept cent quatre-vingt-quatorze",
795: "Sept cent quatre-vingt-quinze",
796: "Sept cent quatre-vingt-seize",
797: "Sept cent quatre-vingt-dix-sept",
798: "Sept cent quatre-vingt-dix-huit",
799: "Sept cent quatre-vingt-dix-neuf",
800: "Huit cents",
801: "Huit cent un",
802: "Huit cent deux",
803: "Huit cent trois",
804: "Huit cent quatre",
805: "Huit cent cinq",
806: "Huit cent six",
807: "Huit cent sept",
808: "Huit cent huit",
809: "Huit cent neuf",
810: "Huit cent dix",
811: "Huit cent onze",
812: "Huit cent douze",
813: "Huit cent treize",
814: "Huit cent quatorze",
815: "Huit cent quinze",
816: "Huit cent seize",
817: "Huit cent dix-sept",
818: "Huit cent dix-huit",
819: "Huit cent dix-neuf",
820: "Huit cent vingt",
821: "Huit cent vingt et un",
822: "Huit cent vingt-deux",
823: "Huit cent vingt-trois",
824: "Huit cent vingt-quatre",
825: "Huit cent vingt-cinq",
826: "Huit cent vingt-six",
827: "Huit cent vingt-sept",
828: "Huit cent vingt-huit",
829: "Huit cent vingt-neuf",
830: "Huit cent trente",
831: "Huit cent trente et un",
832: "Huit cent trente-deux",
833: "Huit cent trente-trois",
834: "Huit cent trente-quatre",
835: "Huit cent trente-cinq",
836: "Huit cent trente-six",
837: "Huit cent trente-sept",
838: "Huit cent trente-huit",
839: "Huit cent trente-neuf",
840: "Huit cent quarante",
841: "Huit cent quarante et un",
842: "Huit cent quarante-deux",
843: "Huit cent quarante-trois",
844: "Huit cent quarante-quatre",
845: "Huit cent quarante-cinq",
846: "Huit cent quarante-six",
847: "Huit cent quarante-sept",
848: "Huit cent quarante-huit",
849: "Huit cent quarante-neuf",
850: "Huit cent cinquante",
851: "Huit cent cinquante et un",
852: "Huit cent cinquante-deux",
853: "Huit cent cinquante-trois",
854: "Huit cent cinquante-quatre",
855: "Huit cent cinquante-cinq",
856: "Huit cent cinquante-six",
857: "Huit cent cinquante-sept",
858: "Huit cent cinquante-huit",
859: "Huit cent cinquante-neuf",
860: "Huit cent soixante",
861: "Huit cent soixante et un",
862: "Huit cent soixante-deux",
863: "Huit cent soixante-trois",
864: "Huit cent soixante-quatre",
865: "Huit cent soixante-cinq",
866: "Huit cent soixante-six",
867: "Huit cent soixante-sept",
868: "Huit cent soixante-huit",
869: "Huit cent soixante-neuf",
870: "Huit cent soixante-dix",
871: "Huit cent soixante et onze",
872: "Huit cent soixante-douze",
873: "Huit cent soixante-treize",
874: "Huit cent soixante-quatorze",
875: "Huit cent soixante-quinze",
876: "Huit cent soixante-seize",
877: "Huit cent soixante-dix-sept",
878: "Huit cent soixante-dix-huit",
879: "Huit cent soixante-dix-neuf",
880: "Huit cent quatre-vingts",
881: "Huit cent quatre-vingt-un",
882: "Huit cent quatre-vingt-deux",
883: "Huit cent quatre-vingt-trois",
884: "Huit cent quatre-vingt-quatre",
885: "Huit cent quatre-vingt-cinq",
886: "Huit cent quatre-vingt-six",
887: "Huit cent quatre-vingt-sept",
888: "Huit cent quatre-vingt-huit",
889: "Huit cent quatre-vingt-neuf",
890: "Huit cent quatre-vingt-dix",
891: "Huit cent quatre-vingt-onze",
892: "Huit cent quatre-vingt-douze",
893: "Huit cent quatre-vingt-treize",
894: "Huit cent quatre-vingt-quatorze",
895: "Huit cent quatre-vingt-quinze",
896: "Huit cent quatre-vingt-seize",
897: "Huit cent quatre-vingt-dix-sept",
898: "Huit cent quatre-vingt-dix-huit",
899: "Huit cent quatre-vingt-dix-neuf",
900: "Neuf cents",
901: "Neuf cent un",
902: "Neuf cent deux",
903: "Neuf cent trois",
904: "Neuf cent quatre",
905: "Neuf cent cinq",
906: "Neuf cent six",
907: "Neuf cent sept",
908: "Neuf cent huit",
909: "Neuf cent neuf",
910: "Neuf cent dix",
911: "Neuf cent onze",
912: "Neuf cent douze",
913: "Neuf cent treize",
914: "Neuf cent quatorze",
915: "Neuf cent quinze",
916: "Neuf cent seize",
917: "Neuf cent dix-sept",
918: "Neuf cent dix-huit",
919: "Neuf cent dix-neuf",
920: "Neuf cent vingt",
921: "Neuf cent vingt et un",
922: "Neuf cent vingt-deux",
923: "Neuf cent vingt-trois",
924: "Neuf cent vingt-quatre",
925: "Neuf cent vingt-cinq",
926: "Neuf cent vingt-six",
927: "Neuf cent vingt-sept",
928: "Neuf cent vingt-huit",
929: "Neuf cent vingt-neuf",
930: "Neuf cent trente",
931: "Neuf cent trente et un",
932: "Neuf cent trente-deux",
933: "Neuf cent trente-trois",
934: "Neuf cent trente-quatre",
935: "Neuf cent trente-cinq",
936: "Neuf cent trente-six",
937: "Neuf cent trente-sept",
938: "Neuf cent trente-huit",
939: "Neuf cent trente-neuf",
940: "Neuf cent quarante",
941: "Neuf cent quarante et un",
942: "Neuf cent quarante-deux",
943: "Neuf cent quarante-trois",
944: "Neuf cent quarante-quatre",
945: "Neuf cent quarante-cinq",
946: "Neuf cent quarante-six",
947: "Neuf cent quarante-sept",
948: "Neuf cent quarante-huit",
949: "Neuf cent quarante-neuf",
950: "Neuf cent cinquante",
951: "Neuf cent cinquante et un",
952: "Neuf cent cinquante-deux",
953: "Neuf cent cinquante-trois",
954: "Neuf cent cinquante-quatre",
955: "Neuf cent cinquante-cinq",
956: "Neuf cent cinquante-six",
957: "Neuf cent cinquante-sept",
958: "Neuf cent cinquante-huit",
959: "Neuf cent cinquante-neuf",
960: "Neuf cent soixante",
961: "Neuf cent soixante et un",
962: "Neuf cent soixante-deux",
963: "Neuf cent soixante-trois",
964: "Neuf cent soixante-quatre",
965: "Neuf cent soixante-cinq",
966: "Neuf cent soixante-six",
967: "Neuf cent soixante-sept",
968: "Neuf cent soixante-huit",
969: "Neuf cent soixante-neuf",
970: "Neuf cent soixante-dix",
971: "Neuf cent soixante et onze",
972: "Neuf cent soixante-douze",
973: "Neuf cent soixante-treize",
974: "Neuf cent soixante-quatorze",
975: "Neuf cent soixante-quinze",
976: "Neuf cent soixante-seize",
977: "Neuf cent soixante-dix-sept",
978: "Neuf cent soixante-dix-huit",
979: "Neuf cent soixante-dix-neuf",
980: "Neuf cent quatre-vingts",
981: "Neuf cent quatre-vingt-un",
982: "Neuf cent quatre-vingt-deux",
983: "Neuf cent quatre-vingt-trois",
984: "Neuf cent quatre-vingt-quatre",
985: "Neuf cent quatre-vingt-cinq",
986: "Neuf cent quatre-vingt-six",
987: "Neuf cent quatre-vingt-sept",
988: "Neuf cent quatre-vingt-huit",
989: "Neuf cent quatre-vingt-neuf",
990: "Neuf cent quatre-vingt-dix",
991: "Neuf cent quatre-vingt-onze",
992: "Neuf cent quatre-vingt-douze",
993: "Neuf cent quatre-vingt-treize",
994: "Neuf cent quatre-vingt-quatorze",
995: "Neuf cent quatre-vingt-quinze",
996: "Neuf cent quatre-vingt-seize",
997: "Neuf cent quatre-vingt-dix-sept",
998: "Neuf cent quatre-vingt-dix-huit",
999: "Neuf cent quatre-vingt-dix-neuf",
1000: "mille"}


letters2numbers = {clean_string(numbers2letters[key]):key for key in numbers2letters}
letters2numbers["et un"] = 1
letters2numbers["et une"] = 1
letters2numbers["une"] = 1

roman_numbers = [
    "I",
    "II",
    "III",
    "IV",
    "V",
    "VI",
    "VII",
    "VIII",
    "IX",
    "X",
    "XI",
    "XII",
    "XIII",
    "XIV",
    "XV",
    "XVI",
    "XVII",
    "XVIII",
    "XIX",
    "XX",
    "XXI",
    "XXII",
    "XXIII",
    "XXIV",
    "XXV",
    "XXVI",
    "XXVII",
    "XXVIII",
    "XXIX",
    "XXX",
    "XXXI",
    "XXXII",
    "XXXIII",
    "XXXIV",
    "XXXV",
    "XXXVI",
    "XXXVII",
    "XXXVIII",
    "XXXIX",
    "XL",
    "XLI",
    "XLII",
    "XLIII",
    "XLIV",
    "XLV",
    "XLVI",
    "XLVII",
    "XLVIII",
    "XLIX",
    "L",
    "LI",
    "LII",
    "LIII",
    "LIV",
    "LV",
    "LVI",
    "LVII",
    "LVIII",
    "LIX",
    "LX",
    "LXI",
    "LXII",
    "LXIII",
    "LXIV",
    "LXV",
    "LXVI",
    "LXVII",
    "LXVIII",
    "LXIX",
    "LXX",
    "LXXI",
    "LXXII",
    "LXXIII",
    "LXXIV",
    "LXXV",
    "LXXVI",
    "LXXVII",
    "LXXVIII",
    "LXXIX",
    "LXXX",
    "LXXXI",
    "LXXXII",
    "LXXXIII",
    "LXXXIV",
    "LXXXV",
    "LXXXVI",
    "LXXXVII",
    "LXXXVIII",
    "LXXXIX",
    "XC",
    "XCI",
    "XCII",
    "XCIII",
    "XCIV",
    "XCV",
    "XCVI",
    "XCVII",
    "XCVIII",
    "XCIX",
    "C",
    "CI",
    "CII",
    "CIII",
    "CIV",
    "CV",
    "CVI",
    "CVII",
    "CVIII",
    "CIX",
    "CX",
    "CXI",
    "CXII",
    "CXIII",
    "CXIV",
    "CXV",
    "CXVI",
    "CXVII",
    "CXVIII",
    "CXIX",
    "CXX",
    "CXXI",
    "CXXII",
    "CXXIII",
    "CXXIV",
    "CXXV",
    "CXXVI",
    "CXXVII",
    "CXXVIII",
    "CXXIX",
    "CXXX",
    "CXXXI",
    "CXXXII",
    "CXXXIII",
    "CXXXIV",
    "CXXXV",
    "CXXXVI",
    "CXXXVII",
    "CXXXVIII",
    "CXXXIX",
    "CXL",
    "CXLI",
    "CXLII",
    "CXLIII",
    "CXLIV",
    "CXLV",
    "CXLVI",
    "CXLVII",
    "CXLVIII",
    "CXLIX",
    "CL",
    "CLI",
    "CLII",
    "CLIII",
    "CLIV",
    "CLV",
    "CLVI",
    "CLVII",
    "CLVIII",
    "CLIX",
    "CLX",
    "CLXI",
    "CLXII",
    "CLXIII",
    "CLXIV",
    "CLXV",
    "CLXVI",
    "CLXVII",
    "CLXVIII",
    "CLXIX",
    "CLXX",
    "CLXXI",
    "CLXXII",
    "CLXXIII",
    "CLXXIV",
    "CLXXV",
    "CLXXVI",
    "CLXXVII",
    "CLXXVIII",
    "CLXXIX",
    "CLXXX",
    "CLXXXI",
    "CLXXXII",
    "CLXXXIII",
    "CLXXXIV",
    "CLXXXV",
    "CLXXXVI",
    "CLXXXVII",
    "CLXXXVIII",
    "CLXXXIX",
    "CXC",
    "CXCI",
    "CXCII",
    "CXCIII",
    "CXCIV",
    "CXCV",
    "CXCVI",
    "CXCVII",
    "CXCVIII",
    "CXCIX",
    "CC",
    "CCI",
    "CCII",
    "CCIII",
    "CCIV",
    "CCV",
    "CCVI",
    "CCVII",
    "CCVIII",
    "CCIX",
    "CCX",
    "CCXI",
    "CCXII",
    "CCXIII",
    "CCXIV",
    "CCXV",
    "CCXVI",
    "CCXVII",
    "CCXVIII",
    "CCXIX",
    "CCXX",
    "CCXXI",
    "CCXXII",
    "CCXXIII",
    "CCXXIV",
    "CCXXV",
    "CCXXVI",
    "CCXXVII",
    "CCXXVIII",
    "CCXXIX",
    "CCXXX",
    "CCXXXI",
    "CCXXXII",
    "CCXXXIII",
    "CCXXXIV",
    "CCXXXV",
    "CCXXXVI",
    "CCXXXVII",
    "CCXXXVIII",
    "CCXXXIX",
    "CCXL",
    "CCXLI",
    "CCXLII",
    "CCXLIII",
    "CCXLIV",
    "CCXLV",
    "CCXLVI",
    "CCXLVII",
    "CCXLVIII",
    "CCXLIX",
    "CCL",
    "CCLI",
    "CCLII",
    "CCLIII",
    "CCLIV",
    "CCLV",
    "CCLVI",
    "CCLVII",
    "CCLVIII",
    "CCLIX",
    "CCLX",
    "CCLXI",
    "CCLXII",
    "CCLXIII",
    "CCLXIV",
    "CCLXV",
    "CCLXVI",
    "CCLXVII",
    "CCLXVIII",
    "CCLXIX",
    "CCLXX",
    "CCLXXI",
    "CCLXXII",
    "CCLXXIII",
    "CCLXXIV",
    "CCLXXV",
    "CCLXXVI",
    "CCLXXVII",
    "CCLXXVIII",
    "CCLXXIX",
    "CCLXXX",
    "CCLXXXI",
    "CCLXXXII",
    "CCLXXXIII",
    "CCLXXXIV",
    "CCLXXXV",
    "CCLXXXVI",
    "CCLXXXVII",
    "CCLXXXVIII",
    "CCLXXXIX",
    "CCXC",
    "CCXCI",
    "CCXCII",
    "CCXCIII",
    "CCXCIV",
    "CCXCV",
    "CCXCVI",
    "CCXCVII",
    "CCXCVIII",
    "CCXCIX",
    "CCC"
]


def cprint(thing):
    # Utilisation de la fonction cprint() pour faire des contrôles
    # lors du débugage du code, et pouvoir facilement retrouver
    # (et mettre en commentaire ou supprimer) ces lignes
    print(thing)


def chunks(lst, n):
    """
    Permet de découper les requêtes dans le SRU par 10.000 (donc de paralléliser 
    10 requêtes"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def chunks_iter(iterable, n):
    """
    Récupère le contenu d'un iterator par groupes de n éléments
    """
    iterable = iter(iterable)
    return iter(lambda: list(IT.islice(iterable, n)), [])


if __name__ == '__main__':
    access_to_network = main.check_access_to_network()
    if(access_to_network is True):
        last_version = main.check_last_compilation(main.programID)
    main.formulaire_main(access_to_network, last_version)
    # formulaire_marc2tables(access_to_network,last_version)
