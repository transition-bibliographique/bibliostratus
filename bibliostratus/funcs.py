# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 21:21:17 2018

@author: Lully
Fonctions et classes génériques pour Bibliostratus
"""

import http.client
import urllib.parse
from urllib import error, request

from lxml import etree
from unidecode import unidecode

from bibliostratus import main


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
    ">", ")", "}"
]

url_access_pbs = []


def nettoyage(string, remplacerEspaces=True, remplacerTirets=True):
    """nettoyage des chaines de caractères (titres, auteurs, isbn)

    suppression ponctuation, espaces (pour les titres et ISBN) et diacritiques"""
    string = unidecode(string.lower())
    for signe in ponctuation:
        string = string.replace(signe, "")
    string = string.replace("'", " ")
    string = " ".join([el for el in string.split(" ") if el != ""])
    if remplacerTirets:
        string = string.replace("-", " ")
    if remplacerEspaces:
        string = string.replace(" ", "")
    string = string.strip()
    return string


def nettoyage_lettresISBN(isbn):
    isbn = unidecode(isbn.lower())
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
    no_commercial_propre = unidecode(no_commercial_propre.lower())
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
    string = string.split(" ")
    string = [mot for mot in string if len(mot) > 1]
    string = " ".join(string)
    return string


def nettoyageDate(date):
    date = unidecode(date.lower())
    for lettre in lettres:
        date = date.replace(lettre, "")
    for signe in ponctuation:
        date = date.split(signe)
        date = " ".join(annee for annee in date if annee.strip(" ") != "")
    date = date.strip(" ")
    return date


def nettoyageTome(numeroTome):
    if (numeroTome):
        numeroTome = unidecode(numeroTome.lower())
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
    pubPlace = unidecode(pubPlace.lower())
    for chiffre in listeChiffres:
        pubPlace = pubPlace.replace(chiffre, "")
    for signe in ponctuation:
        pubPlace = pubPlace.split(signe)
        pubPlace = " ".join(mot.strip(" ")
                            for mot in pubPlace if mot.strip(" ") != "")
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
    isbn_nett = isbn_nett.replace("-", "").replace(" ", "")
    isbn_nett = unidecode(isbn_nett)
    for signe in ponctuation:
        isbn_nett = isbn_nett.replace(signe, "")
    isbn_nett = isbn_nett.lower()
    for lettre in lettres_sauf_x:
        isbn_nett = isbn_nett.replace(lettre, "")
    return isbn_nett


def nettoyage_isni(isni):
    if (isni[0:20] == "http://www.isni.org"):
        isni = isni[20:36]
    else:
        isni = nettoyage(isni)
    for lettre in lettres:
        isni = isni.replace(lettre, "")
    return isni


def nettoyageFRBNF(frbnf):
    frbnf_nett = ""
    if (frbnf[0:4].lower() == "frbn"):
        frbnf_nett = unidecode(frbnf.lower())
    for signe in ponctuation:
        frbnf_nett = frbnf_nett.split(signe)[0]
    return frbnf_nett


def conversionIsbn(isbn):
    longueur = len(isbn)
    isbnConverti = ""
    if (longueur == 10):
        isbnConverti = conversionIsbn1013(isbn)
    elif (longueur == 13):
        isbnConverti = conversionIsbn1310(isbn)
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
    # print(liste_n_convert, liste_n_convert2)
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


def testURLetreeParse(url):
    test = True
    resultat = ""
    try:
        resultat = etree.parse(request.urlopen(url))
    except etree.XMLSyntaxError as err:
        print(url)
        print(err)
        url_access_pbs.append([url, "etree.XMLSyntaxError"])
        test = False
    except etree.ParseError as err:
        print(url)
        print(err)
        test = False
        url_access_pbs.append([url, "etree.ParseError"])
    except error.URLError as err:
        print(url)
        print(err)
        test = False
        url_access_pbs.append([url, "urllib.error.URLError"])
    except ConnectionResetError as err:
        print(url)
        print(err)
        test = False
        url_access_pbs.append([url, "ConnectionResetError"])
    except TimeoutError as err:
        print(url)
        print(err)
        test = False
        url_access_pbs.append([url, "TimeoutError"])
    except http.client.RemoteDisconnected as err:
        print(url)
        print(err)
        test = False
        url_access_pbs.append([url, "http.client.RemoteDisconnected"])
    except http.client.BadStatusLine as err:
        print(url)
        print(err)
        test = False
        url_access_pbs.append([url, "http.client.BadStatusLine"])
    except ConnectionAbortedError as err:
        print(url)
        print(err)
        test = False
        url_access_pbs.append([url, "ConnectionAbortedError"])
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


def testURLurlopen(url):
    test = True
    resultat = ""
    try:
        resultat = request.urlopen(url)
    except etree.XMLSyntaxError as err:
        print(url)
        print(err)
        url_access_pbs.append([url, "etree.XMLSyntaxError"])
        test = False
    except etree.ParseError as err:
        print(url)
        print(err)
        test = False
        url_access_pbs.append([url, "etree.ParseError"])
    except error.URLError as err:
        print(url)
        print(err)
        test = False
        url_access_pbs.append([url, "urllib.error.URLError"])
    except ConnectionResetError as err:
        print(url)
        print(err)
        test = False
        url_access_pbs.append([url, "ConnectionResetError"])
    except TimeoutError as err:
        print(url)
        print(err)
        test = False
        url_access_pbs.append([url, "TimeoutError"])
    except http.client.RemoteDisconnected as err:
        print(url)
        print(err)
        test = False
        url_access_pbs.append([url, "http.client.RemoteDisconnected"])
    except http.client.BadStatusLine as err:
        print(url)
        print(err)
        test = False
        url_access_pbs.append([url, "http.client.BadStatusLine"])
    except ConnectionAbortedError as err:
        print(url)
        print(err)
        test = False
        url_access_pbs.append([url, "ConnectionAbortedError"])
    return (test, resultat)


def url_requete_sru(query, recordSchema="unimarcxchange",
                    maximumRecords="1000", startRecord="1"):
    url = main.urlSRUroot + urllib.parse.quote(query) + "&recordSchema=" + recordSchema + \
        "&maximumRecords=" + maximumRecords + "&startRecord=" + \
        startRecord + "&origin=bibliostratus"
    return url


class International_id:
    """Classe définissant les propriétés d'un identifiant bibliographique :
        ISBN, ISSN, EAN """

    def __init__(self, string):  # Notre méthode constructeur
        self.init = string
        self.nett = nettoyageIsbnPourControle(self.init)
        self.propre = nettoyage_isbn(self.init)
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
    """Classe pour les ISNI"""

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
        self.propre = nettoyage(self.init)

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
        self.frbnf = input_row[1]
        self.ark_init = input_row[2]
        self.isbn = International_id("")
        self.ean = International_id("")
        self.titre = ""
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
            self.no_commercial = International_id(input_row[4])
            self.titre = Titre(input_row[5])
            self.auteur = input_row[6]
            self.date = input_row[7]
            self.publisher = input_row[8]
        if (option_record == 4):
            self.type = "PER"
            self.intermarc_type_record = "s"
            self.intermarc_type_doc = "a"
            self.issn = International_id(input_row[3])
            self.titre = Titre(input_row[4])
            self.auteur = input_row[5]
            self.date = input_row[6]
            self.pubPlace = input_row[7]
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


class Aut_bib_record:
    """Classe définissant les propriétés d'une combinaison de métadonnées
    AUT + BIB, à partir d'une notice bibliographique, pour permettre
    un alignement sur la notice d'autorité"""

    def __init__(self, input_row, parametres):  # Notre méthode constructeur
        self.metas_init = input_row[1:]
        self.NumNot = input_row[0]
        self.frbnf = input_row[1]
