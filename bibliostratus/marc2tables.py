# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 18:30:30 2017
 
@author: Etienne Cavalié

Conversion de fichiers XML ou iso2709 en tableaux pour alignements

"""


import os
import re
import tkinter as tk
import webbrowser
import xml
from lxml import etree

from collections import defaultdict
import json
from random import randrange

from chardet.universaldetector import UniversalDetector
import pymarc as mc
from unidecode import unidecode

import main
import funcs
import bib2id
import aut2id
import forms


# Permet d'écrire dans une liste accessible au niveau général depuis le
# formulaire, et d'y accéder ensuite
entry_file_list = []
message_en_cours = []

output_directory_list = []

output_files_dict = defaultdict()
stats = defaultdict(int)

prefs = {}
try:
    with open('main/files/preferences.json', encoding="utf-8") as prefs_file:
        prefs = json.load(prefs_file)
except FileNotFoundError:
    pass

# =============================================================================
# Creation des fichiers résultats
# =============================================================================
popup_filename = []
liste_notices_pb_encodage = []


def create_file_doc_record(filename, id_traitement):
    filename = "-".join([id_traitement, filename]) + ".txt"
    file = open(filename, "w", encoding="utf-8")
    return file


# =============================================================================
# Fonctions de nettoyage
# =============================================================================
chiffers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
letters = [
    "a", "b", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p",
    "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"
]
punctation = [
    ".", ",", ";", ":", "?", "!", "%", "$", "£", "€", "#", "\\", "\"", "&", "~",
    "{", "(", "[", "`", "\\", "_", "@", ")", "]", "}", "=", "+", "*", "/", "<",
    ">", ")", "}"
]

liste_fichiers = []
liste_resultats = defaultdict(list)

doctype = {"a": "texte",
           "b": "manuscrit",
           "c": "partition",
           "d": "partition manuscrite",
           "e": "carte",
           "f": "carte manuscrite",
           "g": "video",
           "i": "son - non musical",
           "j": "son - musique",
           "k": "image, dessin",
           "l": "ressource électronique",
           "m": "multimedia",
           "r": "objet"
           }
recordtype = {"a": "analytique",
              "i": "feuillets mobiles, etc",
              "m": "monographie",
              "s": "périodiques",
              "c": "collection"}


doctypeAUT = {
    "c": "autorité",

}
recordtypeAUT = {"a": "personne",
                 "b": "collectivite",
                 "c": "nom-geographique",
                 "d": "marque",
                 "e": "famille",
                 "f": "titre-uniforme",
                 "g": "rubrique-de-classement",
                 "h": "auteur-titre",
                 "i": "auteur-rubrique-de-classement",
                 "j": "nom-commun",
                 "k": "lieu-d-edition",
                 "l": "forme-genre"
                 }


doc_record_type = defaultdict(str)

# suppression des signes de ponctuation


def clean_punctation(text):
    text = text.replace("\\'", "'")
    for char in punctation:
        text = text.replace(char, " ")
    return text


def clean_letters(text):
    text = funcs.unidecode_local(text.lower())
    for char in letters:
        text = text.replace(char, " ")
    return text


def clean_spaces(text):
    text = re.sub(r"\s\s+", " ", text).strip()
    return text


def clean_accents_case(text):
    text = unidecode(text).lower()
    return text
# =============================================================================
# Définition des zones pour chaque élément
# =============================================================================


def record2doctype(label, rec_format=1):
    if (rec_format == 2):
        return "c"
    else:
        return label[6]


def record2recordtype(label, rec_format=1):
    if (rec_format == 2):
        return label[9]
    else:
        return label[7]


def path2value(record, field_subfield):
    value = None
    val_list = []
    # print(field_subfield)
    if ("$" in field_subfield):
        field = field_subfield.split("$")[0]
        subfields = field_subfield.split("$")[1:]
        if (type(record) is etree._ElementTree):
            for f in record.xpath(f".//*[@tag='{field}']"):
                field_value = []
                for subf in subfields:
                    for subf_occurrence in f.xpath(f"*[@code='{subf}']"):
                        field_value.append(subf_occurrence.text)
                field_value = " ".join(field_value)
                val_list.append(field_value)
        else:
            for f in record.get_fields(field):
                field_value = []
                for subf in subfields:
                    for subf_occurrence in f.get_subfields(subf):
                        field_value.append(subf_occurrence)
                field_value = " ".join(field_value)
                val_list.append(field_value)
        value = ";".join(val_list)
    else:
        if (type(record) is etree._ElementTree):
            if record.find(f".//*[@tag='{field_subfield}']"):
                value = record.find(f".//*[@tag='{field_subfield}']").text
        else:
            if (record[field_subfield] is not None 
                and int(field_subfield) < 10):
                value = record[field_subfield].data
    return value


def record2meta(record, liste_elements, alternate_list=[], sep=" "):
    zone = []
    for el in liste_elements:
        value = path2value(record, el)
        # print("record2meta : " + el + " / "  + str(value))
        if (value is not None):
            zone.append(value)
    # zone = [path2value(record, el) for el in liste_elements if path2value(record, el) is not None]
    if (zone == [] and alternate_list != []):
        for el in alternate_list:
            value = path2value(record, el)
            if (value is not None):
                zone.append(value)
        # zone = [
        #     path2value(record, el)
        #     for el in alternate_list
        #     if path2value(record, el) is not None
        # ]
    zone = sep.join(zone)
    # print(zone)
    return zone


def record2title(f200a_e):
    title = clean_spaces(f200a_e)
    title = clean_punctation(title)
    return title


def record2date(coded_field, f210d, format="unimarc"):
    date = ""
    extract_coded_date = coded_field[9:13]
    if (format == "marc21"):
        extract_coded_date = coded_field[7:11]
    if main.RepresentsInt(extract_coded_date):
        date = extract_coded_date
    else:
        date = f210d
    date = clean_punctation(date)
    date = date.replace("°", "").replace("-", " ")
    date = clean_letters(date)
    date = clean_spaces(date)
    date = " ".join([el for el in date.split() if len(el) > 2])
    return date


def record2authors(value_fields):
    authors = clean_spaces(value_fields).strip()
    #authors = clean_punctation(authors)
    authors = ";".join([el for el in authors.split(";") if el])
    return authors


def aut2keywords(authors):
    #authors = clean_punctation(authors)
    liste_authors = authors.split(" ")
    liste_authors = " ".join([el for el in liste_authors if el != ""])
    """authors2keywords = set()
    for mot in liste_authors:
        authors2keywords.add(clean_accents_case(mot).strip())
    authors2keywords = " ".join(list(authors2keywords))"""
    return liste_authors


def record2ark(f033a):
    ark = ""
    if (f033a.find("ark:/12148/") > -1):
        ark = f033a
    return ark


def record2frbnf(f035a):
    frbnf = []
    f035a = f035a.lower().split(";")
    for f035 in f035a:
        if ("frbn" in f035
            or "ppn" in f035):
            frbnf.append(f035)
    frbnf = ";".join(frbnf)
    return frbnf


def record2isbn(f010a):
    isbn = f010a
    return isbn


def record2ean(f038a):
    ean = f038a
    return ean


def record2pubPlace(f210a):
    pubPlace = f210a
    return pubPlace

def record2scale(f123a):
    scale = f123a
    if (":" in scale):
        # C'est alors la zone non codée (texte libre)
        scale = scale.split(":")[1]
        for char in funcs.ponctuation:
            if (char != "," and char != "."):
                scale = scale.split(char)[0]
        scale = scale.replace(" ", "").replace(".", "").replace(",", "")                
    if not main.RepresentsInt(scale):
        scale = ""
    return f123a

def record2publisher(f210c):
    publisher = clean_spaces(f210c)
    publisher = clean_punctation(publisher)
    return publisher


def record2numeroTome(f200h):
    numeroTome = f200h
    return numeroTome


def record2issn(f011a):
    issn = f011a
    return issn


def record2id_commercial_aud(f073a):
    return f073a
# =============================================================================
# Gestion des mises à jour
# =============================================================================


def download_last_update():
    url = "https://github.com/Transition-bibliographique/bibliostratus/"
    webbrowser.open(url)


def testchardet(filename):
    detector = UniversalDetector()
    for line in open(filename, 'rb'):
        detector.feed(line)
        if (detector.done):
            break
    detector.close()
    print("detector\n\n")
    print(detector.result)


def alerte_bom(err):
    if ("\xef\xbb\xbf" in err.lower()):
        print("""Le fichier est en UTF-8 BOM
Ouvrez-le dans un éditeur de texte (par exemple avec Notepad++)
pour le convertir en UTF-8 (sans BOM).
""")


def detect_errors_encoding_iso(collection):
    test = True
    record = ""
    try:
        for rec in collection:
            record = rec
    except ValueError as err:
        test = False
    except mc.exceptions.RecordLengthInvalid as err:
        NumNot = record2meta(record, ["001"])
        liste_notices_pb_encodage.append(NumNot)
    return (test, record)


def test_encoding_file(master, entry_filename, encoding, file_format):
    # Récupérer le contenu du fichier en entrée
    # Si les premiers caractères du fichier décrivent son encodage (BOM)
    # alors on ouvre un fichier temporaire où on réécrit le contenu du fichier initial
    # sauf le BOM qui est retiré du contenu
    test = True
    input_file = ""
    random_nr = str(randrange(1000))
    temp_filename = f"temp_file_sans_bom{random_nr}.txt"
    current_dir = ""
    if (file_format == 1):
        file = open(entry_filename, "rb").read()
        current_dir = os.path.dirname(os.path.realpath(entry_filename))        
        temp_filename = os.path.join(current_dir, temp_filename)
        if (len(file[0:3].decode(encoding)) == 1):
            file = file[3:]
            entry_filename = temp_filename
        temp_file = open(temp_filename, "wb")
        temp_file.write(file)
        temp_file.close()
    try:
        input_file = open(entry_filename, 'r',
                          encoding=encoding).read().split(u'\u001D')[0:-1]
    except UnicodeDecodeError:
        main.popup_errors(master, main.errors["format_fichier_en_entree"])
    try:
        os.remove(temp_filename)
    except FileNotFoundError:
        pass
        # print("Fichier temporaire UTF8-sans BOM inutile")
    return (test, input_file)


def iso2tables(master, entry_filename, file_format,
               rec_format, id_traitement,
               display=True):
    # input_file_test = open(entry_filename,'rb').read()
    # print(chardet.detect(input_file_test).read())
    encoding = "iso-8859-1"
    if (file_format == 1):
        encoding = "utf-8"
    (test_file, input_file) = test_encoding_file(master, entry_filename, encoding, file_format)
    assert test_file

    temp_list = [el + u'\u001D' for el in input_file]
    i = 0
    for rec in temp_list:
        i += 1
        outputfilename = "temp_record.txt"
        outputfile = open(outputfilename, "w", encoding="utf-8")

        outputfile.write(rec)
        outputfile.close()
        with open(outputfilename, 'rb') as fh:
            collection = mc.MARCReader(fh)
            if (file_format == 1):
                collection.force_utf8 = True
            (test, record) = detect_errors_encoding_iso(collection)
            if (test):
                record_metas, doc_record = record2listemetas(record, rec_format)
                record_metas2report(record_metas, doc_record, rec_format,
                                    id_traitement, display)
    try:
        os.remove("temp_record.txt")
    except FileNotFoundError as err:
        print(err)
    stats["Nombre total de notices traitées"] = i
    return output_files_dict


def xml2tables(master, entry_filename, rec_format, id_traitement):
    try:
        collection = mc.marcxml.parse_xml_to_array(
            entry_filename, strict=False)
        i = 0
        for record in collection:
            # print(record.leader)
            i += 1
            record_metas, doc_record = record2listemetas(record, rec_format)
            record_metas2report(record_metas, doc_record, rec_format, id_traitement)
        stats["Nombre total de notices traitées"] = i
    except xml.sax._exceptions.SAXParseException:
        message = """Le fichier XML """ + entry_filename + """ n'est pas encodé en UTF-8.
Veuillez ouvrir ce fichier avec un logiciel (exemple : Notepad++)
qui permet de modifier l'encodage du fichier pour le passer
en UTF-8 avant de le mettre en entrée du logiciel"""
        print(message)
        error_file = open(id_traitement + "-errors.txt", "w", encoding="utf-8")
        error_file.write(message)
        error_file.close()


def bib_metas_from_marc21(record):
    title = record2title(
        record2meta(record, ["245$a", "245$e"])
    )
    keyTitle = record2title(
        record2meta(record, ["222$a"], ["200$a", "200$e"])
    )
    global_title = record2title(
        record2meta(record, ["490$a"], ["245$a", "245$e"])
    )
    part_title = ""
    if (global_title == part_title):
        part_title = ""
    authors = record2authors(record2meta(record, [
        "100$a$m",
        "110$a$m",
        "700$a$m",
        "710$a$m",
    ],
        ["245$f"],
        sep=";")
    )
    authors2keywords = aut2keywords(authors)
    date = record2date(record2meta(
                       record, ["008"]), record2meta(record, ["260$c"]),
                       "marc21")
    numeroTome = record2numeroTome(record2meta(record, ["245$n"], ["490$v"]))
    publisher = record2publisher(record2meta(record, ["260$b"]))
    pubPlace = record2pubPlace(record2meta(record, ["260$a"]))
    scale = record2scale(record2meta(record, ["034$b"], ["255$a"]))
    ark = record2ark(record2meta(record, ["033$a"]))
    frbnf = record2frbnf(record2meta(record, ["035$a"], ["801$h"]))
    isbn = record2isbn(record2meta(record, ["020$a"]))
    issn = record2isbn(record2meta(record, ["022$a"]))
    ean = record2ean(record2meta(record, ["024$a"]))
    id_commercial_aud = record2id_commercial_aud(
        record2meta(record, ["073$a"]))
    return (
            title, keyTitle, global_title, part_title,
            authors, authors2keywords, date, numeroTome,
            publisher, pubPlace, scale,
            ark, frbnf, isbn, issn, ean, 
            id_commercial_aud
            )





def bib_metas_from_unimarc(record):
    """
    Définition des zones Marc correspondant aux différentes métadonnées
    """
    title = record2title(
        record2meta(record, ["200$a", "200$e"])
    )
    keyTitle = record2title(
        record2meta(record, ["530$a"], ["200$a", "200$e"])
    )
    global_title = record2title(
        record2meta(record, ["225$a"], ["200$a", "200$e"])
    )
    part_title = record2title(
        record2meta(record, ["464$t"], ["200$a", "200$e"])
    )
    if (global_title == part_title):
        part_title = ""
    authors = record2authors(record2meta(record, [
        "700$a$b",
        "710$a$b",
        "701$a$b",
        "711$a$b",
        "702$a$b",
        "712$a$b",
    ],
        ["200$f"],
        sep=";")
    )
    authors2keywords = aut2keywords(authors)
    date = record2date(record2meta(record, ["100$a"]), record2meta(
        record, ["210$d"], ["219$d", "219$i", "219$p"]))
    numeroTome = record2numeroTome(record2meta(record, ["200$h"], ["461$v"]))
    publisher = record2publisher(record2meta(record, ["210$c"]))
    pubPlace = record2pubPlace(record2meta(record, ["210$a"]))
    scale = record2scale(record2meta(record, ["123$b"], ["206$b"]))
    ark = record2ark(record2meta(record, ["033$a"]))
    frbnf = record2frbnf(record2meta(record, ["035$a"], ["801$h"]))
    isbn = record2isbn(record2meta(record, ["010$a"]))
    issn = record2isbn(record2meta(record, ["011$a"]))
    ean = record2ean(record2meta(record, ["073$a"]))
    id_commercial_aud = record2id_commercial_aud(
        record2meta(record, ["071$b", "071$a"]))
    return (
            title, keyTitle, global_title, part_title,
            authors, authors2keywords, date, numeroTome,
            publisher, pubPlace, scale,
            ark, frbnf, isbn, issn, ean, 
            id_commercial_aud
            )


def bibrecord2metas(numNot, doc_record, record,
                    pref_format_file=True, all_metas=False):
    """
    Le record est une notice pymarc.Record ou en XML
    Le paramètre pref_format_file permet de préciser
    que le format de préférence est à chercher dans
    le fichier preferences.json
    Sinon, Unimarc"""
    if (pref_format_file
       and "marc2tables_input_format" in main.prefs
       and main.prefs["marc2tables_input_format"]["value"] == "marc21"):
        (title, keyTitle, global_title, part_title,
         authors, authors2keywords,
         date, numeroTome, publisher, pubPlace, scale,
         ark, frbnf, isbn, issn, ean,
         id_commercial_aud) = bib_metas_from_marc21(record)
    else:
        (title, keyTitle, global_title, part_title,
         authors, authors2keywords,
         date, numeroTome, publisher, pubPlace, scale,
         ark, frbnf, isbn, issn, ean,
         id_commercial_aud) = bib_metas_from_unimarc(record)
    if (doc_record not in liste_fichiers):
        liste_fichiers.append(doc_record)
    metas = []
    all_metadata = [numNot, frbnf, ark, isbn, ean, id_commercial_aud, issn,
                    title, authors, date, numeroTome, publisher, pubPlace]
    if all_metas:
        metas = all_metadata
    elif (doc_record == "am" or doc_record == "lm"):
        metas = [numNot, frbnf, ark, isbn, ean, title,
                 authors2keywords, date, numeroTome, publisher]
    elif (doc_record == "em"):
        metas = [numNot, frbnf, ark, isbn, ean, title,
                 authors2keywords, date, publisher, scale]
    elif (doc_record == "im" or doc_record == "jm" or doc_record == "gm"):
        metas = [numNot, frbnf, ark, ean, id_commercial_aud,
                 title, authors2keywords, date, publisher]
    elif (doc_record == "cm"):
        metas = [numNot, frbnf, ark, ean, id_commercial_aud,
                 global_title, part_title, authors2keywords, date, publisher]
    elif (len(doc_record) > 1 and doc_record[1] == "s"):
        if (keyTitle == ""):
            metas = [numNot, frbnf, ark, issn, title,
                     authors2keywords, date, pubPlace]
        else:
            metas = [numNot, frbnf, ark, issn, keyTitle,
                     authors2keywords, date, pubPlace]
    else:
        metas = [numNot, frbnf, ark, isbn, ean, id_commercial_aud, issn,
                title, authors, date, numeroTome, publisher, pubPlace]
    # meta.append(doc_record)
    return metas


def record2isniAUT(isni):
    return isni


def record2firstnameAUT(name):
    return name


def record2lastnameAUT(name):
    return name


def record2firstnameAUT_marc21(name):
    if ',' in name:
        return name.split(",")[1]
    else:
        return name

def record2lastnameAUT_marc21(name):
    if ',' in name:
        return name.split(",")[0]
    else:
        return name


def record2firstdateAUT(f103a, f200f):
    if (f103a[1:5] != "    "):
        return f103a[1:5]
    elif ("-" in f200f):
        return (f200f.split("-")[0])
    else:
        return f200f

def record2firstdateAUT_marc21(date):
    return date
    

def record2lastdateAUT(f103b, f200f):
    if (f103b[1:5] != "    "):
        return f103b[1:5]
    elif ("-" in f200f):
        return (f200f.split("-")[1])
    else:
        return f200f


def record2lastdateAUT_marc21(date):
    return date

def autrecord2metas(numNot, doc_record, record,
                    pref_format_file=True,
                    all_metas=False):
    """  Le record est une notice pymarc.Record ou en XML
    Le paramètre pref_format_file permet de préciser
    que le format de préférence est à chercher dans
    le fichier preferences.json
    Sinon, Unimarc """
    
    if (pref_format_file
       and "marc2tables_input_format" in main.prefs
       and main.prefs["marc2tables_input_format"]["value"] == "marc21"):
        (ark, frbnf, isni, firstname,
         lastname, firstdate,
         lastdate, doc_record) = aut_metas_from_marc21(record)
    else:
        (ark, frbnf, isni, firstname,
         lastname, firstdate,
         lastdate) = aut_metas_from_unimarc(record)
    if (doc_record not in liste_fichiers):
        liste_fichiers.append(doc_record)
    meta = [numNot, frbnf, ark, isni, lastname, firstname, firstdate, lastdate]
    return meta


def aut_metas_from_unimarc(record):
    ark = record2ark(record2meta(record, ["033$a"]))
    frbnf = record2frbnf(record2meta(record, ["035$a"]))
    isni = record2isniAUT(record2meta(record, ["010$a"]))
    firstname = record2lastnameAUT(record2meta(record, ["200$b"], ["210$b", "210$c"]))
    lastname = record2firstnameAUT(record2meta(record, ["200$a"], ["210$a"]))
    firstdate = record2firstdateAUT(record2meta(
        record, ["103$a"]), record2meta(record, ["200$f"]))
    lastdate = record2lastdateAUT(record2meta(
        record, ["103$b"]), record2meta(record, ["200$f"]))
    return (ark, frbnf, isni, firstname,
            lastname, firstdate, lastdate)


def aut_metas_from_marc21(record):
    ark = record2ark(record2meta(record, ["035$a"]))
    frbnf = record2frbnf(record2meta(record, ["035$a"]))
    isni = record2isniAUT(record2meta(record, ["024$a"]))
    if re.fullmatch(r"\d{16}", isni) is None:
        isni = ""
    firstname = record2lastnameAUT_marc21(record2meta(record, ["100$a"], ["110$a", "111$a"]))
    lastname = record2firstnameAUT_marc21(record2meta(record, ["100$a"], ["110$b", "111$b"]))
    firstdate = record2firstdateAUT_marc21(record2meta(record, ["046$f"], ["046$q", "111$d"]))
    lastdate = record2lastdateAUT_marc21(record2meta(record, ["046$g"], ["046$r"]))
    if (record2meta(record, ["110$a"])
       or record2meta(record, ["111$a"])):
        doc_record = "cb"
    elif (record2meta(record, ["100$a"])):
        doc_record = "ca"
    else:
        doc_record = "c "
    return (ark, frbnf, isni, firstname,
            lastname, firstdate, lastdate, doc_record)


def bibfield2autmetas(numNot, doc_record, record, field):
    metas = []
    if ("marc2tables_input_format" in main.prefs   
       and main.prefs["marc2tables_input_format"]["value"] == "marc21"):
        metas = bibfield2autmetas_from_marc21(numNot, doc_record, record, field)
    else:
        metas = bibfield2autmetas_from_unimarc(numNot, doc_record, record, field)
    return metas        


def bibfield2autmetas_from_unimarc(numNot, doc_record, record, field):
    metas = []
    no_aut = subfields2firstocc(field.get_subfields("3"))
    no_bib = numNot
    ark = record2ark(record2meta(record, ["033$a"]))
    frbnf = record2frbnf(record2meta(record, ["035$a"]))
    isbn = record2title(
        record2meta(record, ["010$a"], ["073$a"])
    )
    title = record2title(
        record2meta(record, ["200$a", "200$e"])
    )
    pubDate = record2date(record2meta(record, ["100$a"]), record2meta(
        record, ["210$d"], ["219$d", "219$i", "219$p"]))
    isni = subfields2firstocc(field.get_subfields("o"))
    firstname = subfields2firstocc(field.get_subfields("b"))
    lastname = subfields2firstocc(field.get_subfields("a"))
    dates_aut = subfields2firstocc(field.get_subfields("f"))
    metas = [doc_record, no_aut, no_bib, ark, frbnf, isbn, title,
             pubDate, isni, lastname, firstname, dates_aut]
    return metas


def bibfield2autmetas_from_marc21(numNot, doc_record, record, field):
    metas = []
    no_aut = subfields2firstocc(field.get_subfields("3"))
    no_bib = numNot
    ark = record2ark(record2meta(record, ["033$a"]))
    frbnf = record2frbnf(record2meta(record, ["035$a"]))
    isbn = record2title(
        record2meta(record, ["020$a"], ["024$a"])
    )
    title = record2title(
        record2meta(record, ["245$a", "245$e"])
    )
    pubDate = record2date(record2meta(record, ["008"]), record2meta(
        record, ["264$c"]), format="marc21")
    isni = subfields2firstocc(field.get_subfields("o"))
    firstname = subfields2firstocc(field.get_subfields("b"))
    lastname = subfields2firstocc(field.get_subfields("a"))
    if ("marc2tables_input_format" in main.prefs   
       and main.prefs["marc2tables_input_format"]["value"] == "marc21"
       and "," in lastname and firstname == ""):
        field_a = lastname
        lastname = field_a.split(",")[0]
        firstname = ", ".join(field_a.split(",")[1:])
    dates_aut = subfields2firstocc(field.get_subfields("d"))
    metas = [doc_record, no_aut, no_bib, ark, frbnf, isbn, title,
             pubDate, isni, lastname, firstname, dates_aut]
    return metas


def subfields2firstocc(subfields):
    if (subfields != []):
        return subfields[0]
    else:
        return ""


def bibrecord2autmetas(numNot, doc_record, record, all_metas=False):
    fields2metas = []
    for f700 in record.get_fields("700"):
        fields2metas.append(bibfield2autmetas(numNot, "ca", record, f700))
    for f701 in record.get_fields("701"):
        fields2metas.append(bibfield2autmetas(numNot, "ca", record, f701))
    for f702 in record.get_fields("702"):
        fields2metas.append(bibfield2autmetas(numNot, "ca", record, f702))
    for f710 in record.get_fields("710"):
        fields2metas.append(bibfield2autmetas(numNot, "cb", record, f710))
    for f711 in record.get_fields("711"):
        fields2metas.append(bibfield2autmetas(numNot, "cb", record, f711))
    for f712 in record.get_fields("712"):
        fields2metas.append(bibfield2autmetas(numNot, "cb", record, f712))
    if ("marc2tables_input_format" in main.prefs
       and main.prefs["marc2tables_input_format"]["value"] == "marc21"):
        for f100 in record.get_fields("100"):
            fields2metas.append(bibfield2autmetas(numNot, "ca", record, f100))
        for f110 in record.get_fields("100"):
            fields2metas.append(bibfield2autmetas(numNot, "cb", record, f110))
    return fields2metas


def record2doc_recordtype(leader, rec_format):
    """Récupération de la combinaison
    type de document + type de notice
    à partir du label"""
    doctype = record2doctype(leader, rec_format)
    recordtype = record2recordtype(leader, rec_format)
    doc_record = doctype + recordtype
    doc_record = doc_record.strip()
    return doctype, recordtype, doc_record


def record2listemetas(record, rec_format=1, all_metas=False):
    """
    Pour une notice en entrée, renvoie une sélection de métadonnées
    Si all_metas is True : renvoie toutes les métadonnées
    """
    numNot = record2meta(record, ["001"])
    doctype, recordtype, doc_record = record2doc_recordtype(record.leader,
                                                            rec_format)
    meta = []
    if (rec_format == 2):
        meta = autrecord2metas(numNot, doc_record, record, all_metas=all_metas)
    elif(rec_format == 3):
        meta = bibrecord2autmetas(numNot, doc_record, record, all_metas=all_metas)
    else:
        meta = bibrecord2metas(numNot, doc_record, record, all_metas=all_metas)

    return meta, doc_record
    # liste_resultats[doc_record].append(meta)

def rameaurecord2accesspoint(record):
    """
    A partir d'une notice Rameau (record est de type pymarc.Record)
    génération du point d'accès selon la syntaxe Rameau
    """
    dict_mapping_accesspoint = {
            'a': '\1',
            'a b f x': '\1, \2 (\3) -- \4', 
            'a y': '\1 -- \2',
            'a y x': '\1 -- \2 -- \3',
            'a y y': '\1 -- \2 -- \3',
            'a b x': '\1. \2 -- \3',
            'a x x': '\1 -- \2 -- \3',
            'a c b x': '\1. \3 (\2) -- \4',
            'a y z': '\1 -- \2 -- \3',
            'a c': '\1 (\2)',
            'a c f x': '\1 (\2 ; \3) -- \4',
            'a b c x': '\1. \2 (\3) -- \4',
            'a x y': '\1 -- \2 -- \3',
            'a b c': '\1, \2 (\3)',
            'a y y z': '\1 -- \2 -- \3 -- \4',
            'a z x': '\1 -- \3 -- \2',
            'a b x x': '\1. \2 -- \3 -- \4',
            'a c x x': '\1 (\2) -- \3 -- \4',
            'a b d x': '\1, \2 \3 -- \4',
            'a f x': '\1 (\2) -- \3',
            'a b c b x': '\1. \2 (\3) -- \5'
            }
    tag = ""
    field_value = []
    subfields_list = []
    for field in record:
        if field[0] == "2":
            tag = field
            for subfield in record[field]:
                subfields_list.append(subfield)
                field_value.append(f"#{subfield} {record[field][subfield]}")
    subfields_list = " ".join(subfields_list)
    field_value = " ".join(field_value)
    accesspoint_template = ""
    accesspoint = ""
    if (subfields_list in dict_mapping_accesspoint):
        accesspoint_template = dict_mapping_accesspoint[subfields_list]
        accesspoint_template = "#" + accesspoint_template.replace(" ", " (.+) #") + " (.+)"
        accesspoint = re.sub(accesspoint_template, field_value)
    return accesspoint

def record_metas2report(record_metas, doc_record, rec_format,
                        id_traitement, display=True):
    """
    une fois récupérées les métadonnées propres à chaque type de notice
    (grâce à la fonction record2listemetas())
    on les envoie dans un fichier de résultats, par type de doc
    """
    if (rec_format == 3):
        for aut in record_metas:
            doc_record = aut[0]
            if (doc_record in output_files_dict):
                stats[doc_record_type[doc_record]] += 1
                output_files_dict[doc_record].write("\t".join(aut[1:]) + "\n")
                if (display):
                    print(doc_record, ' - ', aut[1])
            else:
                stats[doc_record_type[doc_record]] = 1
                output_files_dict[doc_record] = write_reports(
                    funcs.id_traitement2path(id_traitement), doc_record, rec_format)
                output_files_dict[doc_record].write("\t".join(aut[1:]) + "\n")
                if (display):
                    print(doc_record, ' - ', aut[1])

    elif (doc_record in output_files_dict):
        if (record_metas[0] not in liste_notices_pb_encodage):
            stats[doc_record_type[doc_record]] += 1
            output_files_dict[doc_record].write("\t".join(record_metas) + "\n")
            if (display):
                print(doc_record, ' - ', record_metas[0])

    else:
        stats[doc_record_type[doc_record]] = 1
        output_files_dict[doc_record] = write_reports(
            funcs.id_traitement2path(id_traitement), doc_record, rec_format)
        output_files_dict[doc_record].write("\t".join(record_metas) + "\n")
        if (display):
            print(doc_record, ' - ', record_metas[0])




def write_reports(id_traitement, doc_record, rec_format):
    filename = doc_record_type[doc_record]
    header_columns = [
            "NumNotice", "FRBNF", "ARK", "ISBN", "EAN", "N° commercial",
            "ISSN", "Titre", "Auteur", "Date", "Tome-Volume", "Editeur",
            "Lieu de publication"]
    if (rec_format == 1):
        if (doc_record == "am" or doc_record == "lm"):
            filename = "TEX-" + filename
            header_columns = bib2id.header_columns_init_monimpr
        elif (doc_record == "em"):
            header_columns = bib2id.header_columns_init_cartes
            filename = "CAR-" + filename
        elif (doc_record == "cm"):
            header_columns = bib2id.header_columns_init_partitions
            filename = "PAR-" + filename
        elif (doc_record == "gm"):
            header_columns = bib2id.header_columns_init_cddvd
            filename = "VID-" + filename
        elif (doc_record == "im" or doc_record == "jm"):
            header_columns = bib2id.header_columns_init_cddvd
            filename = "AUD-" + filename
        elif (len(doc_record) > 1 and doc_record[1] == "s"):
            header_columns = bib2id.header_columns_init_perimpr
            filename = "PER-" + filename
    if (rec_format == 2):
        if (doc_record == "ca"):
            header_columns = aut2id.header_columns_init_aut2aut
            filename = "PERS-" + filename
        if (doc_record == "cb"):
            header_columns = aut2id.header_columns_init_aut2aut
            filename = "ORG-" + filename
    if (rec_format == 3):
        if (doc_record == "ca" or doc_record == "cb"):
            header_columns = aut2id.header_columns_init_bib2aut

    file = create_file_doc_record(filename, id_traitement)
    file.write("\t".join(header_columns) + "\n")
    return file


def encoding_errors(id_traitement):
    """Génération d'un fichier listant les numéros de notices avec problème d'encodage"""
    if (liste_notices_pb_encodage != []):
        encoding_errors_file = open(
            id_traitement + "-ALERT-notices_pb_encodage.txt", "w", encoding="utf-8")
        encoding_errors_file.write("""Le logiciel a trouvé des problèmes d'encodage dans les notices suivantes
Elles n'ont pas été exportées dans les tableaux\n\n""")
        encoding_errors_file.write(
            str(len(liste_notices_pb_encodage)) + " notice(s) concernée(s)\n\n")
        print("\n\nNotices ayant un problème d'encodage (caractère non conforme UTF-8)\n")
        for NumNot in liste_notices_pb_encodage:
            encoding_errors_file.write(NumNot + "\n")
            print(NumNot)
        print("""\n\nNous vous recommandons de convertir votre fichier
en XML avec encodage UTF-8, en utilisant pour cela MarcEdit\n
https://github.com/Transition-bibliographique/bibliostratus/wiki/1-%5BBleu%5D-Pr%C3%A9parer-ses-donn%C3%A9es-pour-l'alignement-%C3%A0-partir-d'un-export-catalogue#un-probl%C3%A8me-dencodage--passez-en-xml-avec-marcedit\n""")  # noqa
        print("Consultez le fichier " + id_traitement +
              "-ALERT-notices_pb_encodage.txt")
        encoding_errors_file.close()


def end_of_treatments(form, id_traitement):
    for file in output_files_dict:
        output_files_dict[file].close()
    id_traitement = os.path.join(main.output_directory[0], id_traitement)
    encoding_errors(id_traitement)
    main.output_directory = [""]
    print("\n\n------------------------\n\nExtraction terminée\n\n")
    for key in stats:
        if ("Nombre" not in key):
            print(key + " : ", stats[key])
    print("\nNombre total de notices traitées : ",
          stats["Nombre total de notices traitées"])
    print("------------------------")
    if form is not None:
        form.destroy()


def launch(entry_filename, file_format, rec_format, output_ID, master=None, form=None):
    """Lancement du programme après validation
    du formulaire de conversion d 'un fichier MARC en tableaux"""
    if entry_filename == []:
        main.popup_errors(form, "Merci d'indiquer un nom de fichier en entrée")
        raise
    else:
        entry_filename = entry_filename[0]
    try:
        [entry_filename, file_format,
         rec_format, output_ID] = [str(entry_filename), int(file_format),
                                   int(rec_format), str(output_ID)]
    except ValueError as err:
        print("\n\nDonnées en entrée erronées\n")
        print(err)
    main.check_file_name(form, entry_filename)
    # popup_en_cours = main.message_programme_en_cours(form)

    # Notices BIB : Type de document / type de notice
    if (rec_format == 1):
        for doct in doctype:
            for recordt in recordtype:
                dcrec = doct + recordt
                doct_libelle = doct
                if (doct in doctype):
                    doct_libelle = doctype[doct]
                recordt_libelle = recordt
                if (recordt in recordtype):
                    recordt_libelle = recordtype[recordt]
                dcrec_libelles = "-".join([doct_libelle, recordt_libelle])
                doc_record_type[dcrec] = dcrec_libelles
    # Notices AUT : type d'autorité
    else:
        doct = "c"
        for recordt in recordtypeAUT:
            dcrec = doct + recordt
            doct_libelle = doct
            if (doct in doctypeAUT):
                doct_libelle = doctypeAUT[doct]
            recordt_libelle = recordt
            if (recordt in recordtypeAUT):
                recordt_libelle = recordtypeAUT[recordt]
            dcrec_libelles = "-".join([doct_libelle, recordt_libelle])
            doc_record_type[dcrec] = dcrec_libelles
    print("Fichier en entrée : ", entry_filename)
    if (file_format == 1 or file_format == 2):
        iso2tables(master, entry_filename, file_format, rec_format, output_ID)
    else:
        xml2tables(master, entry_filename, rec_format, output_ID)
    end_of_treatments(form, output_ID)


def formulaire_marc2tables(
        master, access_to_network=True, last_version=[0.0, False]):
    # =============================================================================
    # Structure du formulaire - Cadres
    # =============================================================================
    couleur_fond = "white"
    couleur_bouton = "#2D4991"
    # couleur_bouton = "#99182D"

    [form,
     zone_alert_explications,
     zone_access2programs,
     zone_actions,
     zone_ok_help_cancel,
     zone_notes] = main.form_generic_frames(master,
                                            "Conversion de fichiers de notices Unimarc en tableaux",
                                            couleur_fond, couleur_bouton,
                                            access_to_network)

    frame_input = tk.Frame(zone_actions, highlightthickness=2, highlightbackground=couleur_bouton,
                           relief="groove", height=150, padx=10, bg=couleur_fond)
    frame_input.pack(side="left", anchor="w")
    frame_input_header = tk.Frame(frame_input, bg=couleur_fond)
    frame_input_header.pack(anchor="w")
    frame_input_file = tk.Frame(frame_input, bg=couleur_fond)
    frame_input_file.pack(anchor="w")
    frame_input_file_name = tk.Frame(frame_input_file, bg=couleur_fond)
    frame_input_file_name.pack(side="left")
    frame_input_file_browse = tk.Frame(frame_input_file, bg=couleur_fond)
    frame_input_file_browse.pack(side="left")
    frame_input_infos_format = tk.Frame(frame_input, bg=couleur_fond)
    frame_input_infos_format.pack(side="left")

    frame_input_type_docs = tk.Frame(frame_input, bg=couleur_fond)
    frame_input_type_docs.pack(anchor="w")
    frame_input_type_rec = tk.Frame(frame_input, bg=couleur_fond)
    frame_input_type_rec.pack(anchor="w")

    frame_inter = tk.Frame(zone_actions, borderwidth=0,
                           padx=10, bg=couleur_fond)
    frame_inter.pack(side="left")


    # =============================================================================
    #     Formulaire - Fichier en entrée
    # =============================================================================

    frame_output = tk.Frame(zone_actions, highlightthickness=2, highlightbackground=couleur_bouton,
                            relief="groove", height=120, padx=10, bg=couleur_fond)
    frame_output.pack(side="left")
    frame_output_header = tk.Frame(frame_output, bg=couleur_fond)
    frame_output_header.pack(anchor="w")
    frame_output_nom_fichiers = tk.Frame(frame_output, bg=couleur_fond)
    frame_output_nom_fichiers.pack(anchor="w")
    frame_output_directory = tk.Frame(frame_output, bg=couleur_fond)
    frame_output_directory.pack(anchor="w")
    frame_outputID = tk.Frame(frame_output, bg=couleur_fond)
    frame_outputID.pack(anchor="w")
    frame_output_explications = tk.Frame(frame_output, bg=couleur_fond)
    frame_output_explications.pack(anchor="w")

    frame_output_message_en_cours = tk.Frame(
        zone_notes, padx=20, bg=couleur_fond)
    frame_output_message_en_cours.pack(anchor="w")

    frame_valider = tk.Frame(zone_ok_help_cancel, borderwidth=0,
                             relief="groove", height=150, padx=10, bg=couleur_fond)
    frame_valider.pack(side="left")

    # définition input URL (u)
    tk.Label(frame_inter, text=" ", bg=couleur_fond).pack()
    tk.Label(frame_input_header, bg=couleur_fond, fg=couleur_bouton,
             text="En entrée\n", justify="left", font="bold").pack(anchor="w")

    main.download_zone(
        frame_input_file, "Sélectionner un fichier de notices Unimarc",
        entry_file_list, couleur_fond, frame_output_message_en_cours
    )

    tk.Label(frame_output_header, bg=couleur_fond, fg=couleur_bouton, font="bold",
             text="En sortie",
             justify="left").pack()

    main.download_zone(
        frame_output_directory,
        "Sélectionner un dossier de destination",
        main.output_directory,
        couleur_fond,
        type_action="askdirectory",
        widthb = [40,1]
    )


    # Format du fichier
    file_format = tk.IntVar()
    file_format.set(1)

    # Type de notices
    rec_format = tk.IntVar()
    rec_format.set(1)

    outputID = forms.Entry(frame_outputID,
                        forms.form_ark2records["frame_outputID"]["outputID"]["title"],
                        forms.form_ark2records["frame_outputID"]["outputID"]["params"])

    frame2var = [{"frame": frame_input_type_docs,
                  "name": "frame_input_type_docs",
                  "variables": [["file_format", file_format]]},
                 {"frame": frame_input_type_rec,
                  "name": "frame_input_type_rec",
                  "variables":[["rec_format", rec_format]]}
                ]
    forms.display_options(frame2var, forms.form_marc2tables)

    #forms.add_saut_de_ligne(frame_input_type_docs)

    lien_help_encodage = tk.Button(
        frame_input_type_docs,
        font="Arial 8 italic",
        border=0,
        text="Je ne sais pas / Je ne comprends pas",
        command=lambda: main.click2url(
            "https://github.com/Transition-bibliographique/bibliostratus/wiki/1-%5BBleu%5D-Pr%C3%A9parer-ses-donn%C3%A9es-pour-l'alignement-%C3%A0-partir-d'un-export-catalogue#lencodage-des-fichiers-en-entr%C3%A9e"  # noqa
        ),
    ).pack()

    forms.add_saut_de_ligne(frame_input_type_docs)
    #forms.add_saut_de_ligne(frame_input_type_docs_interstice2)
    #forms.add_saut_de_ligne(frame_input_type_rec, 11)


    message_fichiers_en_sortie = """
  Le programme va générer plusieurs fichiers, par type de document,
  en fonction du processus d'alignement avec les données de la BnF
  et des métadonnées utilisées pour cela :
        - code TEX : monographies
        - code VID : audiovisuel (CD/DVD)
        - code PER : périodiques
        - autres non prévus pour le module d'alignement (blanc)
  Les codes indiquent l'option d'alignement à choisir dans le module blanc
  S'il n'y a pas de code, le fichier ne peut être chargé tel quel dans le module
  blanc : il faut au moins reprendre les colonnes.

  Pour répartir les notices en fichiers, le programme utilise les informations
  présentes dans les zones codées de chaque notice Unimarc
  
  """
    tk.Label(frame_output_explications, bg=couleur_fond,
             text=message_fichiers_en_sortie,
             justify="left").pack()
    # explications.pack()

    # Bouton de validation

    b = tk.Button(frame_valider, bg=couleur_bouton, fg="white", font="bold", text="OK",
                  command=lambda: launch(entry_file_list,
                                         file_format.get(),
                                         rec_format.get(),
                                         outputID.value.get(),
                                         master, form),
                  borderwidth=5, padx=10, pady=10, width=10, height=4)
    b.pack()

    tk.Label(frame_valider, font="bold", text="", bg=couleur_fond).pack()

    call4help = tk.Button(frame_valider,
                          text=main.texte_bouton_help,
                          command=lambda: main.click2url(main.url_online_help),
                          pady=5, padx=5, width=12)
    call4help.pack()
    tk.Label(frame_valider, text="\n", bg=couleur_fond,
             font="Arial 1 normal").pack()

    forum_button = forms.forum_button(frame_valider)
    forum_button.pack()

    tk.Label(frame_valider, text="\n", bg=couleur_fond,
             font="Arial 4 normal").pack()
    cancel = tk.Button(frame_valider, text="Annuler", bg=couleur_fond,
                       command=lambda: main.annuler(form), pady=10, padx=5, width=12)
    cancel.pack()

    forms.footer(zone_notes, couleur_fond)


    tk.mainloop()


if __name__ == '__main__':
    forms.default_launch()
