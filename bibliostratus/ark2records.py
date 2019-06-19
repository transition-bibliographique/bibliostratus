# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 17:55:32 2017

@author: Etienne Cavalié

A partir d'un fichier contenant une liste d'ARK de notices biblio, récupérer les
notices complètes (en XML)
+ option pour récupérer les notices d'autorité
"""

import csv
import random, string
import os
import re
import tkinter as tk
import urllib.parse
from copy import deepcopy

import pymarc as mc
from lxml import etree

import funcs
import main
import bib2id
import udecode
import sru


# Permet d'écrire dans une liste accessible au niveau général depuis le
# formulaire, et d'y accéder ensuite
entry_file_list = []

errors_list = []

dict_format_records = {
    1: "unimarcxchange",
    2: "unimarcxchange-anl",
    3: "intermarcxchange",
    4: "intermarcxchange-anl"}
listefieldsLiensAUT = {
    "unimarc": ["700", "701", "702", "703", "709", "710", "711", "712", "713", "719", "731"],
    "intermarc": ["100", "700", "702", "703", "709", "710", "712", "713", "719", "731"]}
listefieldsLiensSUB = {
    "unimarc": ["600", "603", "606", "607", "609", "610", "616", "617"],
    "intermarc": ["600", "603", "606", "607", "609", "610", "616", "617"]}
listefieldsLiensWORK = {
    "unimarc": ["500"],
    "intermarc": ["141", "144", "145"]}


def ark2url(identifier, parametres):
    """
    URL à partir d'un identifiant BnF ou Abes
    "identifier" est une instance de classe Id4record
    """
    url = ""
    if (identifier.aligned_id.type == "ark"):
        query = parametres["type_records"] + '.persistentid any "' + identifier.aligned_id.clean + '"'
        if (parametres["type_records"] == "aut"):
            query += ' and aut.status any "sparse validated"'
        query = urllib.parse.quote(query)
        url = "http://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query=" + query + \
            "&recordSchema=" + parametres["format_BIB"] + \
            "&maximumRecords=20&startRecord=1&origin=bibliostratus&type_action=extract"
    elif (identifier.aligned_id.type == "ppn" and parametres["type_records"] == "bib"):
        url = "https://www.sudoc.fr/" + identifier.aligned_id.clean + ".xml"
    elif (identifier.aligned_id.type == "ppn" and parametres["type_records"] == "aut"):
        url = "https://www.idref.fr/" + identifier.aligned_id.clean + ".xml"
    return url


def nn2url(nn, type_record, parametres, source="bnf"):
    if (source == "bnf"):
        query = type_record + '.recordid any "' + nn + '"'
        if (type_record == "aut"):
            query += ' and aut.status any "sparse validated"'
        query = urllib.parse.quote(query)
        url = "http://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query=" + \
            query + "&recordSchema=" + \
            parametres["format_BIB"] + "&maximumRecords=20&startRecord=1"
    elif (source == "sudoc"):
        url = "https://www.sudoc.fr/" + nn + ".xml"
    elif (source == "idref"):
        url = "https://www.idref.fr/" + nn + ".xml"
    return url


def XMLrecord2string(identifier, record, parametres):
    """
    Conversion de la notice XML (BnF ou Abes) en chaîne de caractère
    pour l'envoyer dans le fichier rapport
    Au passage, si pertinent, réécriture de la notice pour le contexte local
    """
    record_str = etree.tostring(record, encoding="utf-8").decode(encoding="utf-8")
    record_str = record_str.replace("<mxc:", "<").replace("</mxc:", "</")
    record_str = re.sub("<record[^>]+>", "<record>", record_str)
    if (parametres["correct_record_option"] == 2):
        record_str = correct_record(identifier, record_str, parametres)
    # record_str = udecode.replace_xml_entities(record_str)
    return record_str


def correct_record(identifier, record_str, parametres):
    """
    Réécriture de la notice de l'agence Abes ou BnF
    Zone 001 -> 035
    Zone 003 -> 033
    Numéro de notice initial --> 001

    Le record_str est la notice en MarcXML, en chaîne de caractères
    """
    rewrited_record = record_str
    xml_record = etree.fromstring(record_str)
    new_xml_record = etree.Element("record")
    agency_no = ""
    agency_uri = ""
    for field in xml_record.xpath(".//controlfield[@tag='001']"):
        agency_no = field.text
    for field in xml_record.xpath(".//controlfield[@tag='003']"):
        agency_uri = field.text
    add_033 = 0
    add_035 = 0
    for field in xml_record:
        if (field.tag == "leader"):
            new_xml_record.append(etree.fromstring(deepcopy(etree.tostring(field))))
        elif (field.tag == "controlfield" or field.tag == "datafield"):
            marc_tag = field.get("tag")
            if (marc_tag == "001"):
                new_001 = etree.Element("controlfield")
                new_001.set("tag", "001")
                new_001.text = identifier.NumNot
                new_xml_record.append(new_001)
            elif (int(marc_tag) > 33):
                if (int(marc_tag) > 35):
                    if (add_033 == 0):
                        add_033 = 1
                        if agency_uri:
                            new_033_str = """<datafield tag="033" ind1=" " ind2=" ">
        <subfield code="a">""" + agency_uri + """</subfield>
        </datafield>"""
                            new_xml_record.append(etree.fromstring(new_033_str))

                    if (add_035 == 0):
                        add_035 = 1
                        new_035_str = """<datafield tag="035" ind1=" " ind2=" ">
                    <subfield code="a">""" + agency_no + """</subfield>
                    </datafield>"""
                        new_xml_record.append(etree.fromstring(new_035_str))
                        new_xml_record.append(etree.fromstring(deepcopy(etree.tostring(field))))
                    elif (add_035):
                        new_xml_record.append(etree.fromstring(deepcopy(etree.tostring(field))))
                elif (add_033 == 0):
                    add_033 = 1
                    if agency_uri:
                        new_033_str = """<datafield tag="033" ind1=" " ind2=" ">
    <subfield code="a">""" + agency_uri + """</subfield>
    </datafield>"""
                        new_xml_record.append(etree.fromstring(new_033_str))
                        new_xml_record.append(etree.fromstring(deepcopy(etree.tostring(field))))
                else:
                    new_xml_record.append(etree.fromstring(deepcopy(etree.tostring(field))))
            elif (marc_tag != "003"):
                new_xml_record.append(etree.fromstring(deepcopy(etree.tostring(field))))
    
    rewrited_record = etree.tostring(
        new_xml_record,encoding="utf-8").decode(encoding="utf-8")

    return rewrited_record

def extract_nna_from_bib_record(record, field, source, parametres):
    """Extraction de la liste des identifiants d'auteurs à partir
    d'une zone de notice bib"""
    liste_nna = []
    path = f'//*[@tag="{field}"]/*[@code="3"]'
    for datafield in record.xpath(path):
        nna = datafield.text
        if (nna not in parametres["listeNNA_AUT"]):
            parametres["listeNNA_AUT"].append(nna)
            liste_nna.append(nna)
    return liste_nna


def bib2aut(identifier, XMLrecord, parametres):
    """Si une des option "Récupérer les notices d'autorité liées" est cochée
    récupération des identifiants de ces AUT pour les récupérer"""
    source = "bnf"
    if (identifier.aligned_id.type == "ppn"):
        source = "sudoc"
    liste_nna = []
    listefields = []
    format_marc = parametres["format_BIB"].split("x")[0]
    if (parametres["AUTlieesAUT"] == 1):
        listefields.extend(listefieldsLiensAUT[format_marc])
    if (parametres["AUTlieesSUB"] == 1):
        listefields.extend(listefieldsLiensSUB[format_marc])
    if (parametres["AUTlieesWORK"] == 1):
        listefields.extend(listefieldsLiensWORK[format_marc])
    for field in listefields:
        liste_nna.extend(extract_nna_from_bib_record(XMLrecord, field, 
                                                     source, parametres))
    for nna in liste_nna:
        if (source == "sudoc"):
            source = "idref"
        url = nn2url(nna, "aut", parametres, source)
        (test, record) = funcs.testURLetreeParse(url)
        if (test and source == "bnf" and record.find(
                "//srw:recordData/mxc:record", namespaces=main.ns) is not None):
            XMLrec = record.xpath(
                ".//srw:recordData/mxc:record", namespaces=main.ns
            )[0]
            linked_identifier = funcs.Id4record([record.find("//srw:recordIdentifier", namespaces=main.ns).text])
            record2file(linked_identifier, XMLrec, parametres["aut_file"],
                        parametres["format_file"], parametres)
        elif (test and source == "idref" and record.find("leader") is not None):
                record2file(f"PPN{nna}", record, parametres["aut_file"],
                            parametres["format_file"], parametres)


def file_create(record_type, parametres):
    """
    Création du fichier en sortie : XML, iso2709 ou tabulé
    """
    file = object
    id_filename = "-".join([parametres["outputID"], record_type])
    if (parametres["format_file"] == 3):
        filename = id_filename + ".txt"
        file = open(filename, "w", encoding="utf-8")
        headers = ["Numéro de notice", "Type de notice"] + parametres["select_fields"].split(";")
        funcs.line2report(headers, file, display=False)
    elif (parametres["format_file"] == 2):
        filename = id_filename + ".xml"
        file = open(filename, "w", encoding="utf-8")
        file.write("<?xml version='1.0' encoding='utf-8'?>\n")
        file.write("<collection>")
    else:
        filename = id_filename + ".iso2709"
        file = mc.MARCWriter(open(filename, "wb"))
    return file


def file_fin(file, format_file):
    if (format_file == 2):
        file.write("</collection>")
    file.close()


def XMLrec2isorecord(XMLrec):
    XMLrec = XMLrec.replace("<mxc:", "<").replace("</mxc:", "</")
    XMLrec = "<collection>" + XMLrec + "</collection>"
    XMLrec = re.sub(r"<record[^>]+>", r"<record>", XMLrec)
    filename_temp = ''.join([random.choice(string.ascii_lowercase) for i in range(5)]) + ".xml"
    file_temp = open(filename_temp, "w", encoding="utf-8")
    file_temp.write(XMLrec)
    file_temp.close()
    return filename_temp


def record2file(identifier, XMLrec, file, format_file, parametres):
    """
    Conversion de la notice XML trouvée en ligne 
    -> incrémentation dans le fichier en sortie
    Si option cochée, réécriture de la notice
    "identifier" est une instance de la classe Id4record
    """
    #Si fichier tabulé
    if (format_file == 3):
        doctype, recordtype, entity_type = sru.extract_docrecordtype(XMLrec, "marc")
        line = [identifier.NumNot, doctype+recordtype]
        for field in parametres["select_fields"].split(";"):
            value = sru.record2fieldvalue(XMLrec, field)
            line.append(value)
        funcs.line2report(line, parametres["bib_file"], display=False)
    # Si sortie en iso2709
    elif (format_file == 1):
        XMLrec_str = XMLrecord2string(identifier, XMLrec, parametres)
        filename_temp = XMLrec2isorecord(XMLrec_str)
        collection = mc.marcxml.parse_xml_to_array(filename_temp, strict=False)
        # collection.force_utf8 = True
        for record in collection:
            record.force_utf8 = True
            try:
                file.write(record)
            except UnicodeEncodeError as err:
                errors_list.append([XMLrec_str, str(err)])
        try:
            os.remove(filename_temp)
        except FileNotFoundError:
            pass
    # si sortie en XML
    if (format_file == 2):
        record = XMLrecord2string(identifier, XMLrec, parametres)
        file.write(record)


def page2nbresults(page, identifier):
    nbresults = "0"
    if (identifier.aligned_id.type == "ppn"):
        if (page.find("//leader") is not None):
            nbresults = "1"
    elif (page.find("//srw:numberOfRecords", namespaces=main.ns) is not None):
        nbresults = page.find("//srw:numberOfRecords", namespaces=main.ns).text
    return nbresults


def extract1record(row, j, form, headers, parametres):
    identifier = funcs.Id4record(row, parametres)
    if (len(identifier.aligned_id.clean) > 1 and identifier.aligned_id.clean not in parametres["listeARK_BIB"]):
        print(str(j) + ". " + identifier.aligned_id.clean)
        parametres["listeARK_BIB"].append(identifier.aligned_id.clean)
        url_record = ark2url(identifier, parametres)
        if url_record:
            (test, page) = funcs.testURLetreeParse(url_record)
            if (test):
                nbResults = page2nbresults(page, identifier)
                # Si on part d'un ARK
                if (nbResults == "1" and identifier.aligned_id.type == "ark"):
                    for XMLrec in page.xpath(
                            "//srw:record/srw:recordData/mxc:record",
                            namespaces=main.ns):
                        record2file(identifier, XMLrec,
                            parametres["bib_file"], 
                            parametres["format_file"],
                            parametres
                        )
                        if (parametres["AUTliees"] > 0):
                            bib2aut(identifier, XMLrec, parametres)
                # Si on part d'un PPN
                elif (nbResults == "1" and identifier.aligned_id.type == "ppn"):
                    for XMLrec in page.xpath("//record"):
                        record2file(identifier, XMLrec,
                                    parametres["bib_file"],
                                    parametres["format_file"],
                                    parametres)
                        if (parametres["AUTliees"] > 0):
                            bib2aut(identifier, XMLrec, parametres)
            elif (identifier.aligned_id.type == "ppn"
                  and parametres["type_records"] == "bib"):
                ppn_updated = update_bib_ppn(identifier.aligned_id.clean)
                if ppn_updated is not None:
                    print("Nouveau PPN :", ppn_updated)
                    errors_list.append([f"Fusion de notices Sudoc\t{identifier.aligned_id.init} disparu. Nouveau PPN : {ppn_updated}",
                                        ""])
                    identifier = funcs.Id4record([row[0], f"PPN{ppn_updated}"],
                                                 parametres)
                    parametres["listeARK_BIB"].append(identifier.aligned_id.clean)
                    url_record = ark2url(identifier, parametres)
                    if url_record:
                        (test, page) = funcs.testURLetreeParse(url_record)
                        if (test):
                            nbResults = page2nbresults(page, identifier)
                            if (nbResults == "1"):
                                for XMLrec in page.xpath("//record"):
                                    record2file(identifier, XMLrec,
                                                parametres["bib_file"],
                                                parametres["format_file"],
                                                parametres)
                                    if (parametres["AUTliees"] > 0):
                                        bib2aut(identifier, XMLrec, parametres)

def update_bib_ppn(ppn):
    url = f"https://www.sudoc.fr/services/merged/{ppn}"
    test, result = funcs.testURLetreeParse(url)
    if (test
       and result.find("//result/ppn") is not None):
        new_ppn = result.find("//result/ppn").text
        return new_ppn
    else:
        return None

def launch(master, form, filename, type_records_form, 
             correct_record_option, headers, AUTlieesAUT,
             AUTlieesSUB, AUTlieesWORK, outputID, 
             format_records=1, format_file=1, select_fields=""):
    try:
        [filename, type_records_form, correct_record_option,
        headers, AUTlieesAUT, AUTlieesSUB, AUTlieesWORK, outputID,
        format_records, format_file, select_fields] = [str(filename), int(type_records_form), 
                                                        int(correct_record_option),
                                                        int(headers),
                                                        int(AUTlieesAUT),
                                                        int(AUTlieesSUB), 
                                                        int(AUTlieesWORK), 
                                                        str(outputID),
                                                        int(format_records), 
                                                        int(format_file), 
                                                        str(select_fields)]
    except ValueError as err:
        print("\n\nDonnées en entrée erronées\n")
        print(err)

    AUTliees = AUTlieesAUT + AUTlieesSUB + AUTlieesWORK
    format_BIB = dict_format_records[format_records]
    outputID = funcs.id_traitement2path(outputID)
    type_records = "bib"
    if (type_records_form == 2):
        type_records = "aut"
    parametres = {
        "type_records": type_records,
        "correct_record_option": correct_record_option,
        "type_records_form": type_records_form,
        "AUTliees": AUTliees,
        "AUTlieesAUT": AUTlieesAUT,
        "AUTlieesSUB": AUTlieesSUB,
        "AUTlieesWORK": AUTlieesWORK,
        "outputID": outputID,
        "format_records": format_records,
        "format_file": format_file,
        "format_BIB": format_BIB,
        "select_fields": select_fields,
        "listeARK_BIB" : [],
        "listeNNA_AUT" : []
    }
    main.generic_input_controls(master, filename)

    bib_file = file_create(type_records, parametres)
    parametres["bib_file"] = bib_file
    if (parametres["AUTliees"] > 0):
        aut_file = file_create("aut", parametres)
        parametres["aut_file"] = aut_file
    with open(filename, newline='\n', encoding="utf-8") as csvfile:
        entry_file = csv.reader(csvfile, delimiter='\t')
        if headers:
            next(entry_file, None)
        j = 0
        for row in entry_file:
            extract1record(row, j, form, headers, parametres)
            j = j + 1

        file_fin(bib_file, format_file)
        if (AUTliees == 1):
            file_fin(aut_file, format_file)
    fin_traitements(form, outputID)


def errors_file(outputID):
    if errors_list:
        errors_file = open(outputID + "-errors.txt", "w", encoding="utf-8")
        for el in errors_list:
            errors_file.write(el[1] + "\n" + el[0] + "\n\n")
        errors_file.close()


def fin_traitements(window, outputID):
    if (errors_list != []):
        errors_file(outputID)
    print("Programme d'extraction de notices terminé")
    if window is not None:
        window.destroy()
    main.output_directory = [""]


# ==============================================================================
# Création de la boîte de dialogue
# ==============================================================================

def formulaire_ark2records(
        master, access_to_network=True, last_version=[0.0, False]):
    couleur_fond = "white"
    couleur_bouton = "#99182D"

    [form,
     zone_alert_explications,
     zone_access2programs,
     zone_actions,
     zone_ok_help_cancel,
     zone_notes] = main.form_generic_frames(
         master,
         "Bibliostratus : Récupérer les notices complètes BnF / Sudoc / IdRef à partir d'une liste de n° de notices",
         couleur_fond, couleur_bouton,
         access_to_network)

    zone_ok_help_cancel.config(padx=10)

    frame_input = tk.Frame(zone_actions,
                           bg=couleur_fond, padx=10, pady=10,
                           highlightthickness=2, highlightbackground=couleur_bouton)
    frame_input.pack(side="left", anchor="w", padx=10, pady=10)
    frame_input_file = tk.Frame(frame_input, bg=couleur_fond)
    frame_input_file.pack()
    frame_input_aut = tk.Frame(frame_input, bg=couleur_fond)
    frame_input_aut.pack()

    frame_output = tk.Frame(zone_actions,
                            bg=couleur_fond, padx=10, pady=10,
                            highlightthickness=2, highlightbackground=couleur_bouton)
    frame_output.pack(side="left", anchor="w")

    frame_output_options = tk.Frame(
        frame_output, bg=couleur_fond, padx=10, pady=10)
    frame_output_options.pack(anchor="w")
    frame_output_file = tk.Frame(
        frame_output, bg=couleur_fond, padx=10, pady=10)
    frame_output_file.pack(anchor="w")
    frame_output_options_marc = tk.Frame(frame_output_options, bg=couleur_fond)
    frame_output_options_marc.pack(side="left", anchor="nw")
    frame_output_options_inter = tk.Frame(
        frame_output_options, bg=couleur_fond)
    frame_output_options_inter.pack(side="left")
    frame_output_options_format = tk.Frame(
        frame_output_options, bg=couleur_fond)
    frame_output_options_format.pack(side="left", anchor="nw")

    zone_notes_message_en_cours = tk.Frame(
        zone_notes, padx=20, bg=couleur_fond)
    zone_notes_message_en_cours.pack()

    # tk.Label(frame_input_file, text="Fichier contenant les ARK\n (1 par ligne) \n\n",
    #         bg=couleur_fond, justify="left").pack(side="left", anchor="w")
    """entry_filename = tk.Entry(frame_input_file, width=20, bd=2, bg=couleur_fond)
    entry_filename.pack(side="left")
    entry_filename.focus_set() """
    
    main.download_zone(
                        frame_output_file,
                        "Sélectionner un dossier de destination",
                        main.output_directory,
                        couleur_fond,
                        type_action="askdirectory",
                        widthb = [40,1]
                        )

    main.download_zone(
        frame_input_file,
        "Sélectionner un fichier contenant\nune liste de n° de notices\nARK BnF ou PPN Abes\n(un numéro par ligne)",
        entry_file_list,
        couleur_fond,
        zone_notes_message_en_cours
        )

    tk.Label(frame_input_aut, text="\n", bg=couleur_fond).pack()

    # ARK de BIB ou d'AUT ?
    type_records = tk.IntVar()
    bib2id.radioButton_lienExample(
        frame_input_aut, type_records, 1, couleur_fond, "N° de notices bibliographiques",
        "",
        "main/examples/listeARKbib.tsv"  # noqa
    )
    bib2id.radioButton_lienExample(
        frame_input_aut, type_records, 2, couleur_fond, "N° de notices d'autorités",
        "",
        "main/examples/listeARKaut.tsv"  # noqa
    )
    type_records.set(1)

    tk.Label(frame_input_aut, text="-------------------",
             bg=couleur_fond).pack()


    # 1 ou 2 colonnes ?
    correct_record_option = tk.IntVar()
    bib2id.radioButton_lienExample(
        frame_input_aut, correct_record_option, 1, couleur_fond, "Fichier d'1 colonne (1 ARK ou PPN par ligne)", "", "")
    bib2id.radioButton_lienExample(
        frame_input_aut, correct_record_option, 2, couleur_fond, "Fichier à 2 colonnes (N° notice local | ARK ou PPN)\n\
pour réécrire les notices récupérées",
        "", "main/examples/listeARKaut_2cols.tsv")
    correct_record_option.set(1)

    tk.Label(frame_input_aut, text="-------------------",
             bg=couleur_fond).pack()

    # Fichier avec en-têtes ?
    headers = tk.IntVar()
    tk.Checkbutton(frame_input_aut, text="Mon fichier a des en-têtes de colonne",
                   variable=headers,
                   bg=couleur_fond, justify="left").pack(anchor="w")

    headers.set(1)

    # notices d'autorité liées
    tk.Label(frame_input_aut, text="Récupérer aussi les notices d'autorité liées",
             bg=couleur_fond, justify="left", font="Arial 9 bold").pack(anchor="w")
    AUTlieesAUT = tk.IntVar()
    tk.Checkbutton(frame_input_aut, text="auteurs",
                   variable=AUTlieesAUT,
                   bg=couleur_fond, justify="left").pack(anchor="w", side="left")
    # tk.Label(frame_input_aut, text="\n", bg=couleur_fond).pack()
    AUTlieesSUB = tk.IntVar()
    tk.Checkbutton(frame_input_aut, text="sujets",
                   variable=AUTlieesSUB,
                   bg=couleur_fond, justify="left").pack(anchor="w", side="left")
    AUTlieesWORK = tk.IntVar()
    tk.Checkbutton(frame_input_aut, text="oeuvres",
                   variable=AUTlieesWORK,
                   bg=couleur_fond, justify="left").pack(anchor="w", side="left")

    # Choix du format
    tk.Label(frame_output_options_marc,
             text="Notices à récupérer en :").pack(anchor="nw")
    format_records_choice = tk.IntVar()
    tk.Radiobutton(frame_output_options_marc, text="Unimarc",
                   variable=format_records_choice, value=1, bg=couleur_fond).pack(anchor="nw")
    tk.Radiobutton(frame_output_options_marc, text="Intermarc", justify="left",
                   variable=format_records_choice, value=3, bg=couleur_fond).pack(anchor="nw")
    tk.Radiobutton(
        frame_output_options_marc,
        text="[ARK BnF] Unimarc \navec notices analytiques",
        justify="left",
        variable=format_records_choice,
        value=2,
        bg=couleur_fond
    ).pack(anchor="nw")
    tk.Radiobutton(
        frame_output_options_marc,
        text="[ARK BnF] Intermarc \navec notices analytiques",
        justify="left",
        variable=format_records_choice,
        value=4,
        bg=couleur_fond
    ).pack(anchor="nw")
    format_records_choice.set(1)


    tk.Label(frame_output_file, text=" ",
             bg=couleur_fond).pack()

    # tk.Label(
    #     frame_output_options,
    #     text="\n\n",
    #     justify="left",
    #     variable=format_records_choice,
    #     value=4,
    #     bg=couleur_fond
    # ).pack()


    tk.Label(frame_output_file, text="Préfixe fichier(s) en sortie",
             bg=couleur_fond).pack(side="left", anchor="w")
    outputID = tk.Entry(frame_output_file, bg=couleur_fond)
    outputID.pack(side="left", anchor="w")
    tk.Label(frame_output_file, text="\n"*5,
             bg=couleur_fond).pack(side="left")

    tk.Label(frame_output_options_format,
             text="Format du fichier :").pack(anchor="nw")
    format_file = tk.IntVar()
    tk.Radiobutton(frame_output_options_format, bg=couleur_fond,
                   text="iso2709", variable=format_file, value=1, justify="left").pack(anchor="nw")
    tk.Radiobutton(frame_output_options_format, bg=couleur_fond,
                   text="Marc XML", variable=format_file, value=2, justify="left").pack(anchor="nw")
    tk.Radiobutton(
        frame_output_options_format,
        text="Certaines zones (sép : \";\")\n - fichier tabulé",
        justify="left",
        variable=format_file,
        value=3,
        bg=couleur_fond
    ).pack(anchor="nw")
    format_file.set(1)


    tk.Label(frame_output_options_format,
             text="\tZones à récupérer",
             bg=couleur_fond).pack()
    tk.Label(frame_output_options_format,
             text="\t",
             bg=couleur_fond).pack(side="left", anchor="w")
    select_fields = tk.Entry(frame_output_options_format, bg=couleur_fond)
    select_fields.pack(side="left", anchor="w")


    # file_format.focus_set()
    b = tk.Button(
        zone_ok_help_cancel,
        text="OK",
        command=lambda: launch(
            master,
            form,
            entry_file_list[0],
            type_records.get(),
            correct_record_option.get(),
            headers.get(),
            AUTlieesAUT.get(),
            AUTlieesSUB.get(),
            AUTlieesWORK.get(),
            outputID.get(),
            format_records_choice.get(),
            format_file.get(),
            select_fields.get()
        ),
        width=15,
        borderwidth=1,
        pady=20,
        fg="white",
        bg=couleur_bouton,
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

    forum_button = tk.Button(zone_ok_help_cancel,
                             text=main.texte_bouton_forum,
                             command=lambda: main.click2url(
                                 main.url_forum_aide),
                             pady=5, padx=5, width=12)
    forum_button.pack()

    tk.Label(zone_ok_help_cancel, text="\n",
             bg=couleur_fond, font="Arial 4 normal").pack()
    cancel = tk.Button(zone_ok_help_cancel, text="Annuler", bg=couleur_fond,
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
    # formulaire_ark2records(access_to_network,[version, False])
