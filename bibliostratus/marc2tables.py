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

from chardet.universaldetector import UniversalDetector
import pymarc as mc
from unidecode import unidecode

import main
import funcs
import noticesaut2arkBnF as aut2ark
import noticesbib2arkBnF as bib2ark


# Permet d'écrire dans une liste accessible au niveau général depuis le
# formulaire, et d'y accéder ensuite
entry_file_list = []
message_en_cours = []

output_directory_list = []

output_files_dict = defaultdict()
stats = defaultdict(int)

prefs = {}
with open('main/files/preferences.json', encoding="utf-8") as prefs_file:
    prefs = json.load(prefs_file)

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
    "{", "(", "[", "`", "\\", "_", "@", ")", "]", "}", "=", "+", "*", "\/", "<",
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
    text = re.sub("\s\s+", " ", text).strip()
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
    if (field_subfield.find("$") > -1):
        field = field_subfield.split("$")[0]
        subfield = field_subfield.split("$")[1]
        if (type(record) is etree._ElementTree):
            for f in record.xpath(f".//*[@tag='{field}']"):
                for subf in f.xpath(f".//*[@code='{subfield}']"):
                    val_list.append(subf.text)
        else:
            for f in record.get_fields(field):
                for subf in f.get_subfields(subfield):
                    val_list.append(subf)
        if (val_list != []):
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


def record2meta(record, liste_elements, alternate_list=[]):
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
    zone = " ".join(zone)
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
    authors = clean_punctation(authors)
    return authors


def aut2keywords(authors):
    authors = clean_punctation(authors)
    liste_authors = authors.split(" ")
    liste_authors = [el for el in liste_authors if el != ""]
    authors2keywords = set()
    for mot in liste_authors:
        authors2keywords.add(clean_accents_case(mot).strip())
    authors2keywords = " ".join(list(authors2keywords))
    return authors2keywords


def record2ark(f033a):
    ark = ""
    if (f033a.find("ark:/12148/") > -1):
        ark = f033a
    return ark


def record2frbnf(f035a):
    frbnf = []
    f035a = f035a.lower().split(";")
    for f035 in f035a:
        if (f035.find("frbn") > -1):
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
    test = True
    input_file = ""
    if (file_format == 1):
        file = open(entry_filename, "rb").read()
        if (len(file[0:3].decode(encoding)) == 1):
            file = file[3:]
            entry_filename = "temp_file_sans_bom.txt"
        temp_file = open("temp_file_sans_bom.txt", "wb")
        temp_file.write(file)
        temp_file.close()
    try:
        input_file = open(entry_filename, 'r',
                          encoding=encoding).read().split(u'\u001D')[0:-1]
    except UnicodeDecodeError:
        main.popup_errors(master, main.errors["format_fichier_en_entree"])
    try:
        os.remove("temp_file_sans_bom.txt")
    except FileNotFoundError:
        print("Fichier temporaire UTF8-sans BOM inutile")
    return (test, input_file)


def iso2tables(master, entry_filename, file_format, rec_format, id_traitement):
    # input_file_test = open(entry_filename,'rb').read()
    # print(chardet.detect(input_file_test).read())
    encoding = "iso-8859-1"
    if (file_format == 1):
        encoding = "utf-8"
    (test_file, input_file) = test_encoding_file(
        master, entry_filename, encoding, file_format)
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
                record2listemetas(id_traitement, record, rec_format)
    try:
        os.remove("temp_record.txt")
    except FileNotFoundError as err:
        print(err)
    stats["Nombre total de notices traitées"] = i


def xml2tables(master, entry_filename, rec_format, id_traitement):
    try:
        collection = mc.marcxml.parse_xml_to_array(
            entry_filename, strict=False)
        i = 0
        for record in collection:
            # print(record.leader)
            i += 1
            record2listemetas(id_traitement, record, rec_format)
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


def metas_from_marc21(record):
    title = record2title(
        record2meta(record, ["245$a", "245$e"])
    )
    keyTitle = record2title(
        record2meta(record, ["222$a"], ["200$a", "200$e"])
    )
    authors = record2authors(record2meta(record, [
        "100$a",
        "100$m",
        "110$a",
        "110$m",
        "700$a",
        "700$m",
        "710$a",
        "710$m",
    ],
        ["245$f"])
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
    frbnf = record2frbnf(record2meta(record, ["035$a"]))
    isbn = record2isbn(record2meta(record, ["020$a"]))
    issn = record2isbn(record2meta(record, ["022$a"]))
    ean = record2ean(record2meta(record, ["024$a"]))
    id_commercial_aud = record2id_commercial_aud(
        record2meta(record, ["073$a"]))
    return (
            title, keyTitle, authors,
            authors2keywords, date, numeroTome, publisher,
            pubPlace, scale,
            ark, frbnf, isbn, issn, ean, id_commercial_aud
            )


def metas_from_unimarc(record):
    title = record2title(
        record2meta(record, ["200$a", "200$e"])
    )
    keyTitle = record2title(
        record2meta(record, ["530$a"], ["200$a", "200$e"])
    )
    authors = record2authors(record2meta(record, [
        "700$a",
        "700$b",
        "710$a",
        "710$b",
        "701$a",
        "701$b",
        "711$a",
        "711$b",
        "702$a",
        "702$b",
        "712$a",
        "712$b"
    ],
        ["200$f"])
    )
    authors2keywords = aut2keywords(authors)
    date = record2date(record2meta(record, ["100$a"]), record2meta(
        record, ["210$d"], ["219$d", "219$i", "219$p"]))
    numeroTome = record2numeroTome(record2meta(record, ["200$h"], ["461$v"]))
    publisher = record2publisher(record2meta(record, ["210$c"]))
    pubPlace = record2pubPlace(record2meta(record, ["210$a"]))
    scale = record2scale(record2meta(record, ["123$b"], ["206$b"]))
    ark = record2ark(record2meta(record, ["033$a"]))
    frbnf = record2frbnf(record2meta(record, ["035$a"]))
    isbn = record2isbn(record2meta(record, ["010$a"]))
    issn = record2isbn(record2meta(record, ["011$a"]))
    ean = record2ean(record2meta(record, ["073$a"]))
    id_commercial_aud = record2id_commercial_aud(
        record2meta(record, ["071$b", "071$a"]))
    return (
            title, keyTitle, authors,
            authors2keywords, date,
            numeroTome, publisher, pubPlace, scale,
            ark, frbnf, isbn, issn, ean, id_commercial_aud
            )


def bibrecord2metas(numNot, doc_record, record, pref_format_file = True):
    """
    Le record est une notice pymarc.Record ou en XML
    Le paramètre pref_format_file permet de préciser
    que le format de préférence est à chercher dans
    le fichier preferences.json
    Sinon, Unimarc"""
    if (pref_format_file == True
        and prefs["marc2tables_input_format"]["value"] == "marc21"):
        (title, keyTitle, authors, authors2keywords,
         date, numeroTome, publisher, pubPlace, scale,
         ark, frbnf, isbn, issn, ean,
         id_commercial_aud) = metas_from_marc21(record)
    else:
        (title, keyTitle, authors, authors2keywords,
         date, numeroTome, publisher, pubPlace, scale,
         ark, frbnf, isbn, issn, ean,
         id_commercial_aud) = metas_from_unimarc(record)

    if (doc_record not in liste_fichiers):
        liste_fichiers.append(doc_record)
    if (doc_record == "am" or doc_record == "lm"):
        meta = [numNot, frbnf, ark, isbn, ean, title,
                authors2keywords, date, numeroTome, publisher]
    if (doc_record == "em"):
        meta = [numNot, frbnf, ark, isbn, ean, title,
                authors2keywords, date, publisher, scale]
    elif (doc_record == "im" or doc_record == "jm" or doc_record == "gm"):
        meta = [numNot, frbnf, ark, ean, id_commercial_aud,
                title, authors2keywords, date, publisher]
    elif (len(doc_record) > 1 and doc_record[1] == "s"):
        if (keyTitle == ""):
            meta = [numNot, frbnf, ark, issn, title,
                    authors2keywords, date, pubPlace]
        else:
            meta = [numNot, frbnf, ark, issn, keyTitle,
                    authors2keywords, date, pubPlace]
    else:
        meta = [numNot, frbnf, ark, isbn, ean, id_commercial_aud, issn,
                title, authors, date, numeroTome, publisher, pubPlace]
    return meta


def record2isniAUT(isni):
    return isni


def record2firstnameAUT(name):
    return name


def record2lastnameAUT(name):
    return name


def record2firstdateAUT(f103a, f200f):
    if (f103a[1:5] != "    "):
        return f103a[1:5]
    elif ("-" in f200f):
        return (f200f.split("-")[0])
    else:
        return f200f


def record2lastdateAUT(f103b, f200f):
    if (f103b[1:5] != "    "):
        return f103b[1:5]
    elif ("-" in f200f):
        return (f200f.split("-")[1])
    else:
        return f200f


def autrecord2metas(numNot, doc_record, record):
    ark = record2ark(record2meta(record, ["033$a"]))
    frbnf = record2frbnf(record2meta(record, ["035$a"]))
    isni = record2isniAUT(record2meta(record, ["010$a"]))
    firstname = record2lastnameAUT(record2meta(record, ["200$b"], ["210$b", "210$c"]))
    lastname = record2firstnameAUT(record2meta(record, ["200$a"], ["210$a"]))
    firstdate = record2firstdateAUT(record2meta(
        record, ["103$a"]), record2meta(record, ["200$f"]))
    lastdate = record2lastdateAUT(record2meta(
        record, ["103$b"]), record2meta(record, ["200$f"]))

    if (doc_record not in liste_fichiers):
        liste_fichiers.append(doc_record)
    meta = [numNot, frbnf, ark, isni, lastname, firstname, firstdate, lastdate]
    return meta


def bibfield2autmetas(numNot, doc_record, record, field):
    metas = []
    no_aut = subfields2firstocc(field.get_subfields("3"))
    no_bib = numNot
    ark = record2ark(record2meta(record, ["033$a"]))
    frbnf = record2frbnf(record2meta(record, ["035$a"]))
    title = record2title(
        record2meta(record, ["200$a", "200$e"])
    )
    pubDate = record2date(record2meta(record, ["100$a"]), record2meta(
        record, ["210$d"], ["219$d", "219$i", "219$p"]))
    isni = subfields2firstocc(field.get_subfields("o"))
    firstname = subfields2firstocc(field.get_subfields("b"))
    lastname = subfields2firstocc(field.get_subfields("a"))
    dates_aut = subfields2firstocc(field.get_subfields("f"))
    metas = [doc_record, no_aut, no_bib, ark, frbnf, title,
             pubDate, isni, lastname, firstname, dates_aut]
    return metas


def subfields2firstocc(subfields):
    if (subfields != []):
        return subfields[0]
    else:
        return ""


def bibrecord2autmetas(numNot, doc_record, record):
    fields2metas = []
    for f700 in record.get_fields("700"):
        fields2metas.append(bibfield2autmetas(numNot, "ca", record, f700))
    for f701 in record.get_fields("701"):
        fields2metas.append(bibfield2autmetas(numNot, "ca", record, f701))
    for f710 in record.get_fields("710"):
        fields2metas.append(bibfield2autmetas(numNot, "cb", record, f710))
    for f711 in record.get_fields("711"):
        fields2metas.append(bibfield2autmetas(numNot, "cb", record, f711))
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


def record2listemetas(id_traitement, record, rec_format=1):
    numNot = record2meta(record, ["001"])
    doctype, recordtype, doc_record = record2doc_recordtype(record.leader,
                                                     rec_format)
    meta = []
    if (rec_format == 2):
        meta = autrecord2metas(numNot, doc_record, record)
    elif(rec_format == 3):
        meta = bibrecord2autmetas(numNot, doc_record, record)
    else:
        meta = bibrecord2metas(numNot, doc_record, record)

    # print(meta)
    if (rec_format == 3):
        for aut in meta:
            doc_record = aut[0]
            if (doc_record in output_files_dict):
                stats[doc_record_type[doc_record]] += 1
                output_files_dict[doc_record].write("\t".join(aut[1:]) + "\n")
                print(doc_record, ' - ', aut[1])
            else:
                stats[doc_record_type[doc_record]] = 1
                output_files_dict[doc_record] = write_reports(
                    id_traitement, doc_record, rec_format)
                output_files_dict[doc_record].write("\t".join(aut[1:]) + "\n")
                print(doc_record, ' - ', aut[1])

    elif (doc_record in output_files_dict):
        if (meta[0] not in liste_notices_pb_encodage):
            stats[doc_record_type[doc_record]] += 1
            output_files_dict[doc_record].write("\t".join(meta) + "\n")
            print(doc_record, ' - ', meta[0])

    else:
        stats[doc_record_type[doc_record]] = 1
        output_files_dict[doc_record] = write_reports(
            id_traitement, doc_record, rec_format)
        output_files_dict[doc_record].write("\t".join(meta) + "\n")
        print(doc_record, ' - ', meta[0])

    # liste_resultats[doc_record].append(meta)


def write_reports(id_traitement, doc_record, rec_format):
    filename = doc_record_type[doc_record]
    header_columns = [
            "NumNotice", "FRBNF", "ARK", "ISBN", "EAN", "N° commercial",
            "ISSN", "Titre", "Auteur", "Date", "Tome-Volume", "Editeur",
            "Lieu de publication"]
    if (rec_format == 1):
        if (doc_record == "am" or doc_record == "lm"):
            filename = "TEX-" + filename
            header_columns = bib2ark.header_columns_init_monimpr
        elif (doc_record == "em"):
            header_columns = bib2ark.header_columns_init_cartes
            filename = "CAR-" + filename
        elif (doc_record == "gm"):
            header_columns = bib2ark.header_columns_init_cddvd
            filename = "VID-" + filename
        elif (doc_record == "im" or doc_record == "jm"):
            header_columns = bib2ark.header_columns_init_cddvd
            filename = "AUD-" + filename
        elif (len(doc_record) > 1 and doc_record[1] == "s"):
            header_columns = bib2ark.header_columns_init_perimpr
            filename = "PER-" + filename
    if (rec_format == 2):
        if (doc_record == "ca"):
            header_columns = aut2ark.header_columns_init_aut2aut
            filename = "PERS-" + filename
        if (doc_record == "cb"):
            header_columns = aut2ark.header_columns_init_aut2aut
            filename = "ORG-" + filename
    if (rec_format == 3):
        if (doc_record == "ca"):
            header_columns = aut2ark.header_columns_init_bib2aut

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
    encoding_errors(id_traitement)
    print("\n\n------------------------\n\nExtraction terminée\n\n")
    for key in stats:
        if ("Nombre" not in key):
            print(key + " : ", stats[key])
    print("\nNombre total de notices traitées : ",
          stats["Nombre total de notices traitées"])
    print("------------------------")
    form.destroy()


def launch(form, entry_filename, file_format, rec_format, output_ID, master):

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
    if (file_format == 1 or file_format == 3):
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

    cadre_input = tk.Frame(zone_actions, highlightthickness=2, highlightbackground=couleur_bouton,
                           relief="groove", height=150, padx=10, bg=couleur_fond)
    cadre_input.pack(side="left", anchor="w")
    cadre_input_header = tk.Frame(cadre_input, bg=couleur_fond)
    cadre_input_header.pack(anchor="w")
    cadre_input_file = tk.Frame(cadre_input, bg=couleur_fond)
    cadre_input_file.pack(anchor="w")
    cadre_input_file_name = tk.Frame(cadre_input_file, bg=couleur_fond)
    cadre_input_file_name.pack(side="left")
    cadre_input_file_browse = tk.Frame(cadre_input_file, bg=couleur_fond)
    cadre_input_file_browse.pack(side="left")
    cadre_input_infos_format = tk.Frame(cadre_input, bg=couleur_fond)
    cadre_input_infos_format.pack(side="left")

    cadre_input_type_docs_interstice1 = tk.Frame(cadre_input, bg=couleur_fond)
    cadre_input_type_docs_interstice1.pack(side="left")

    cadre_input_type_docs = tk.Frame(cadre_input, bg=couleur_fond)
    cadre_input_type_docs.pack(side="left")
    cadre_input_type_docs_interstice2 = tk.Frame(cadre_input, bg=couleur_fond)
    cadre_input_type_docs_interstice2.pack(side="left")
    cadre_input_type_rec = tk.Frame(cadre_input, bg=couleur_fond)
    cadre_input_type_rec.pack(side="left")

    cadre_inter = tk.Frame(zone_actions, borderwidth=0,
                           padx=10, bg=couleur_fond)
    cadre_inter.pack(side="left")
    tk.Label(cadre_inter, text=" ", bg=couleur_fond).pack()

    # =============================================================================
    #     Formulaire - Fichier en entrée
    # =============================================================================

    cadre_output = tk.Frame(zone_actions, highlightthickness=2, highlightbackground=couleur_bouton,
                            relief="groove", height=150, padx=10, bg=couleur_fond)
    cadre_output.pack(side="left")
    cadre_output_header = tk.Frame(cadre_output, bg=couleur_fond)
    cadre_output_header.pack(anchor="w")
    cadre_output_nom_fichiers = tk.Frame(cadre_output, bg=couleur_fond)
    cadre_output_nom_fichiers.pack(anchor="w")
    cadre_output_repertoire = tk.Frame(cadre_output, bg=couleur_fond)
    cadre_output_repertoire.pack(anchor="w")
    cadre_output_explications = tk.Frame(
        cadre_output, padx=20, bg=couleur_fond)
    cadre_output_explications.pack(anchor="w")

    cadre_output_message_en_cours = tk.Frame(
        cadre_output, padx=20, bg=couleur_fond)
    cadre_output_message_en_cours.pack(anchor="w")

    cadre_valider = tk.Frame(zone_ok_help_cancel, borderwidth=0,
                             relief="groove", height=150, padx=10, bg=couleur_fond)
    cadre_valider.pack(side="left")

    # définition input URL (u)
    tk.Label(cadre_input_header, bg=couleur_fond, fg=couleur_bouton,
             text="En entrée\n", justify="left", font="bold").pack(anchor="w")

    # tk.Label(
    #     cadre_input_file_name,
    #     bg=couleur_fond,
    #     text="Fichier contenant les notices : "
    # ).pack(side="left")
    """entry_filename = tk.Entry(cadre_input_file, width=40, bd=2)
    entry_filename.pack(side="left")
    entry_filename.focus_set()"""
    main.download_zone(
        cadre_input_file, "Sélectionner un fichier de notices Unimarc",
        entry_file_list, couleur_fond, cadre_output_message_en_cours
    )

    # tk.Button(
    #     cadre_input_file_browse,
    #     text="Sélectionner le fichier\ncontenant les notices",
    #     command=lambda: main.openfile(cadre_input_file_name, popup_filename),
    #     width=20
    # ).pack()

    # tk.Label(
    #     cadre_input_infos_format,
    #     bg=couleur_fond,
    #     text="Format MARC",
    #     anchor="w",
    #     justify="left"
    # ).pack(anchor="w")
    # marc_format = tk.IntVar()

    # bib2ark.radioButton_lienExample(
    #     cadre_input_infos_format, marc_format, 1, couleur_fond, "Unimarc", "",
    #     ""
    # )

    # tk.Radiobutton(
    #     cadre_input_infos_format,
    #     bg=couleur_fond,
    #     text="Marc21",
    #     variable=marc_format,
    #     value=2,
    #     anchor="w",
    #     justify="left"
    # ).pack(anchor="w")
    # marc_format.set(1)

    tk.Label(cadre_input_type_docs_interstice1, bg=couleur_fond,
             text="\t\t", justify="left").pack()

    tk.Label(cadre_input_type_docs, bg=couleur_fond, text="Format de fichier",
             anchor="w", justify="left", font="Arial 9 bold").pack(anchor="w")
    file_format = tk.IntVar()

    bib2ark.radioButton_lienExample(
        cadre_input_type_docs, file_format, 1, couleur_fond,
        "iso2709 encodé UTF-8", "",
        "main/examples/noticesbib.iso"  # noqa
    )
    tk.Radiobutton(
        cadre_input_type_docs,
        bg=couleur_fond,
        text="iso2709 encodé ISO-8859-1",
        variable=file_format,
        value=3,
        anchor="w",
        justify="left"
    ).pack(anchor="w")

    tk.Radiobutton(
        cadre_input_type_docs,
        bg=couleur_fond,
        text="Marc XML encodé UTF-8",
        variable=file_format,
        value=2,
        anchor="w",
        justify="left"
    ).pack(anchor="w")
    file_format.set(1)

    tk.Label(cadre_input_type_docs, bg=couleur_fond, text="\n",
             font="Arial 4", justify="left").pack()

    lien_help_encodage = tk.Button(
        cadre_input_type_docs,
        font="Arial 8 italic",
        border=0,
        text="Je ne sais pas / Je ne comprends pas",
        command=lambda: main.click2url(
            "https://github.com/Transition-bibliographique/bibliostratus/wiki/1-%5BBleu%5D-Pr%C3%A9parer-ses-donn%C3%A9es-pour-l'alignement-%C3%A0-partir-d'un-export-catalogue#lencodage-des-fichiers-en-entr%C3%A9e"  # noqa
        ),
    )
    lien_help_encodage.pack()
    tk.Label(cadre_input_type_docs, bg=couleur_fond, text="\n\n\n").pack()

    #    info_utf8 = tk.Label(cadre_input_type_docs,
    #                         bg=couleur_fond,justify="left", font="Arial 7 italic",
    #                         text="""Le fichier iso2709 doit être
    # en UTF-8 sans BOM.
    # En cas de problème,
    # convertissez-le en XML
    # avant de le passer dans ce module""")
    #    info_utf8.pack()

    tk.Label(cadre_input_type_docs_interstice2,
             bg=couleur_fond, text="\t", justify="left").pack()

    tk.Label(cadre_input_type_rec, bg=couleur_fond, text="\nType de notices",
             anchor="w", justify="left", font="Arial 9 bold").pack(anchor="w")
    rec_format = tk.IntVar()

    bib2ark.radioButton_lienExample(cadre_input_type_rec, rec_format, 1, couleur_fond,
                                    "bibliographiques",
                                    "",
                                    "")

    tk.Radiobutton(
        cadre_input_type_rec,
        bg=couleur_fond,
        text="autorités",
        variable=rec_format,
        value=2,
        anchor="w",
        justify="left"
    ).pack(anchor="w")
    tk.Label(
        cadre_input_type_rec, text="\n", bg=couleur_fond, font="Arial 1 normal"
    ).pack()
    tk.Radiobutton(
        cadre_input_type_rec,
        bg=couleur_fond,
        text="biblio - pour alignement Autorités",
        variable=rec_format,
        value=3,
        anchor="w",
        justify="left"
    ).pack(anchor="w")
    rec_format.set(1)

    tk.Label(cadre_input_type_rec, text="\n\n\n\n\n\n", bg=couleur_fond).pack()

    # =============================================================================
    #     Formulaire - Fichiers en sortie
    # =============================================================================
    #

    # Choix du format
    tk.Label(cadre_output_header, bg=couleur_fond, fg=couleur_bouton, font="bold",
             text="En sortie",
             justify="left").pack()
    tk.Label(cadre_output_nom_fichiers, bg=couleur_fond,
             text="Préfixe des fichiers en sortie : ",
             justify="left").pack(side="left")
    output_ID = tk.Entry(cadre_output_nom_fichiers, width=40, bd=2)
    output_ID.pack(side="left")

    # Sélection du répertoire en sortie
    # tk.Label(cadre_output_repertoire,text="\n",bg=couleur_fond).pack()
    # main.select_directory(
    #     cadre_output_repertoire, "Dossier où déposer les fichiers",
    #     output_directory_list, couleur_fond
    # )

    # Ajout (optionnel) d'un identifiant de traitement
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
    tk.Label(cadre_output_explications, bg=couleur_fond,
             text=message_fichiers_en_sortie,
             justify="left").pack()
    # explications.pack()

    # Bouton de validation

    b = tk.Button(cadre_valider, bg=couleur_bouton, fg="white", font="bold", text="OK",
                  command=lambda: launch(form, entry_file_list[0], file_format.get(
                  ), rec_format.get(), output_ID.get(), master),
                  borderwidth=5, padx=10, pady=10, width=10, height=4)
    b.pack()

    tk.Label(cadre_valider, font="bold", text="", bg=couleur_fond).pack()

    call4help = tk.Button(cadre_valider,
                          text=main.texte_bouton_help,
                          command=lambda: main.click2url(main.url_online_help),
                          pady=5, padx=5, width=12)
    call4help.pack()
    tk.Label(cadre_valider, text="\n", bg=couleur_fond,
             font="Arial 1 normal").pack()

    forum_button = tk.Button(cadre_valider,
                             text=main.texte_bouton_forum,
                             command=lambda: main.click2url(
                                 main.url_forum_aide),
                             pady=5, padx=5, width=12)
    forum_button.pack()

    tk.Label(cadre_valider, text="\n", bg=couleur_fond,
             font="Arial 4 normal").pack()
    cancel = tk.Button(cadre_valider, text="Annuler", bg=couleur_fond,
                       command=lambda: main.annuler(form), pady=10, padx=5, width=12)
    cancel.pack()

    tk.Label(zone_notes, text="Bibliostratus - Version " +
             str(main.version) + " - " + main.lastupdate, bg=couleur_fond).pack()

    # if (main.last_version[1] == True):
    #     download_update = tk.Button(
    #         zone_notes,
    #         text="Télécharger la version " + str(main.last_version[0]),
    #         command=download_last_update
    #     )
    #     download_update.pack()

    tk.mainloop()


if __name__ == '__main__':
    access_to_network = main.check_access_to_network()
    if(access_to_network is True):
        last_version = main.check_last_compilation(main.programID)
    main.formulaire_main(access_to_network, last_version)
    # formulaire_marc2tables(access_to_network,last_version)
