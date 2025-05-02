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
import tkinter.ttk as ttk
import urllib.parse
from copy import deepcopy
from joblib import Parallel, delayed
import multiprocessing

import pymarc as mc
from lxml import etree
import smc.bibencodings

import funcs
import main
import bib2id
import forms
import sru


NUM_PARALLEL = 20    # Nombre de notices à exporter simultanément


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
        if "inter" in parametres["format_BIB"]:
            parametres["format_BIB"] = "intermarcxchange"    
        else:
            parametres["format_BIB"] = "unimarcxchange"
        url = "http://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query=" + query + \
            "&recordSchema=" + parametres["format_BIB"] + \
            "&maximumRecords=20&startRecord=1&origin=bibliostratus&type_action=extract"
    elif (identifier.aligned_id.type == "ppn" and parametres["type_records"] == "bib"):
        url = "https://www.sudoc.fr/" + identifier.aligned_id.clean + ".xml"
    elif (identifier.aligned_id.type == "ppn" and parametres["type_records"] == "aut"):
        url = "https://www.idref.fr/" + identifier.aligned_id.clean + ".xml"
    # print(url)
    
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
    rewrited_record = etree.tostring(new_xml_record,
                                     encoding="utf-8").decode(encoding="utf-8")

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


def bib2aut(identifier, XMLrecord, parametres, multiprocess):
    """Si une des option "Récupérer les notices d'autorité liées" est cochée
    récupération des identifiants de ces AUT pour les récupérer"""
    source = "bnf"
    if (identifier.aligned_id.type == "ppn"):
        source = "sudoc"
    liste_nna = []
    listefields = []
    linked_aut_record = []
    format_marc = parametres["format_BIB"].split("x")[0]
    linked_aut_records = []
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
            # record2file(linked_identifier, XMLrec, parametres["aut_file"],
            #             parametres["format_file"], parametres)
            linked_aut_record.append([linked_identifier, XMLrec])
        elif (test and source == "idref" and record.find("leader") is not None):
                # record2file(f"PPN{nna}", record, parametres["aut_file"],
                #             parametres["format_file"], parametres)
            linked_aut_record.append([f"PPN{nna}", record])
        if multiprocess:
            for el in linked_aut_record:
                el[1] = etree.tostring(el[1])
        return linked_aut_record


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
        output_encoding = "utf-8"
        if ("xml_encoding_option" in parametres):
            output_encoding = parametres["xml_encoding_option"]
        filename = id_filename + ".xml"

        file = open(filename, "w", encoding=output_encoding)
        
        file.write(f"<?xml version='1.0' encoding='{output_encoding}'?>\n")
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


def record2file(identifier, XMLrec, file, format_file, parametres, dict_files):
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
        funcs.line2report(line, dict_files["bib_file"], display=False)
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


def extract1record(row, parametres, multiprocess=False):
    """
    Extraction d'une notice par son identifiant
    """
    identifier = funcs.Id4record(row, parametres)
    xml_record = None
    linked_aut_record = None
    if (len(identifier.aligned_id.clean) > 1 and (identifier.aligned_id.clean not in parametres["listeARK_BIB"] or parametres["correct_record_option"] != 1)):
        # On cherche à récupérer la notice uniquement si l'identifiant est fourni
        # ET (si la notice n'a pas déjà été récupérée OU c'est un fichier à 2 colonnes : alignement des 2 identifiants : origine et cible))
        parametres["listeARK_BIB"].append(identifier.aligned_id.clean)
        url_record = ark2url(identifier, parametres)
        if url_record:
            (test, page) = funcs.testURLetreeParse(url_record)
            if (test):
                nbResults = page2nbresults(page, identifier)
                # Si on part d'un ARK
                if (nbResults in ["1", "2"] and identifier.aligned_id.type == "ark"
                    and page.find("//srw:record/srw:recordData/mxc:record", namespaces=main.ns) is not None):
                    XMLrec = page.xpath(
                            "//srw:record/srw:recordData/mxc:record",
                            namespaces=main.ns)[0]
                    xml_record = XMLrec
                    """record2file(identifier, XMLrec,
                        parametres["bib_file"], 
                        parametres["format_file"],
                        parametres
                    )"""
                    if (parametres["AUTliees"] > 0):
                        linked_aut_record = bib2aut(identifier, XMLrec, parametres, multiprocess)
                # Si on part d'un PPN
                elif (nbResults == "1" and identifier.aligned_id.type == "ppn"):
                    for XMLrec in page.xpath("//record"):
                        xml_record = XMLrec
                        """record2file(identifier, XMLrec,
                                    parametres["bib_file"],
                                    parametres["format_file"],
                                    parametres)"""
                        if (parametres["AUTliees"] > 0):
                            linked_aut_record = bib2aut(identifier, XMLrec, parametres, multiprocess)
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
                                    xml_record = XMLrec
                                    """record2file(identifier, XMLrec,
                                                parametres["bib_file"],
                                                parametres["format_file"],
                                                parametres)"""
                                    if (parametres["AUTliees"] > 0):
                                        linked_aut_record = bib2aut(identifier, XMLrec, parametres, multiprocess)
    if multiprocess and xml_record is not None:
        xml_record = etree.tostring(xml_record) 
    return identifier, xml_record, linked_aut_record

def update_bib_ppn(ppn):
    url = f"https://www.sudoc.fr/services/merged/{ppn}"
    test, result = funcs.testURLetreeParse(url)
    if (test
       and result.find("//result/ppn") is not None):
        new_ppn = result.find("//result/ppn").text
        return new_ppn
    else:
        return None

def launch(filename, type_records_form, 
           correct_record_option, headers, AUTlieesAUT,
           AUTlieesSUB, AUTlieesWORK, outputID, 
           format_records=1, format_file=1,
           xml_encoding_option="utf-8",
           select_fields="",
           master=None, form=None):
    if filename == []:
        main.popup_errors(form, "Merci d'indiquer un nom de fichier en entrée")
        raise
    else:
        filename = filename[0]
    try:
        [filename, type_records_form,
         correct_record_option,
         headers, AUTlieesAUT,
         AUTlieesSUB, AUTlieesWORK,
         outputID, format_records,
         format_file, xml_encoding_option,
         select_fields] = [str(filename), int(type_records_form),
                           int(correct_record_option), int(headers),
                           int(AUTlieesAUT), int(AUTlieesSUB),
                           int(AUTlieesWORK), str(outputID),
                           int(format_records), int(format_file),
                           str(xml_encoding_option), str(select_fields)]
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
        "headers": headers,
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
        "xml_encoding_option": xml_encoding_option,
        "format_BIB": format_BIB,
        "select_fields": select_fields,
        "listeARK_BIB" : [],
        "listeNNA_AUT" : []
    }
    files = {}
    main.generic_input_controls(master, filename)
    bib_file = file_create(type_records, parametres)
    files["bib_file"] = bib_file
    if (parametres["AUTliees"] > 0):
        aut_file = file_create("aut", parametres)
        files["aut_file"] = aut_file
    file2extract(filename, parametres, files, master, form)
    file_fin(files["bib_file"], format_file)
    if (AUTliees == 1):
        file_fin(files['aut_file'], format_file)
    fin_traitements(form, outputID)


def file2extract(filename, parametres, files, master_form, ark2records_form):
    with open(filename, newline='\n', encoding="utf-8") as csvfile:
        entry_file = csv.reader(csvfile, delimiter='\t')
        if parametres["headers"]:
            next(entry_file, None)
        j = 0
        for rows in funcs.chunks_iter(entry_file, 10):
            if j == 0:
                check_nb_colonnes(rows[0], parametres, master_form)
                j += 1
            records = Parallel(n_jobs=NUM_PARALLEL, prefer="threads", backend="threading")(delayed(extract1record)(row, parametres, True) for row in rows)            
            for identifier, xml_record, linked_aut_records in records:
                print(str(j) + ". " + identifier.aligned_id.clean)
                try:
                    record2file(identifier, etree.fromstring(xml_record), files["bib_file"], 
                            parametres["format_file"], parametres, files)
                except ValueError as err:
                    errors_list.append([str(err), f"Problème d'accès à la notice : {identifier.aligned_id.clean}"])
                    print(f"Pas d'accès à la notice  {identifier.aligned_id.clean} {str(err)} : consulter le fichier d'erreurs {parametres['outputID']}-errors.txt")
                if linked_aut_records is not None:
                    for identifier, xml_record in linked_aut_records:
                        record2file(identifier, etree.fromstring(xml_record), files["aut_file"],
                                    parametres["format_file"], parametres, files)
                j += 1
     
    

def check_nb_colonnes(row, parametres, frame_master):
    """
    Vérifie s'il y a bien dans le fichier
    le nombre de colonnes indiquées dans le formulaire
    """
    nbcol = len(row)
    
    if parametres["correct_record_option"] != nbcol:
        alert = f"""Erreur dans les paramètres en entrée :
Nombre de colonnes dans le fichier : {nbcol}
Nombre de colonnes indiqué : {parametres["correct_record_option"]}"""
        main.popup_errors(frame_master, alert)


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
    frame_input_aut_file = tk.Frame(frame_input_aut, bg=couleur_fond)
    frame_input_aut_file.pack()
    frame_input_aut_headers = tk.Frame(frame_input_aut, bg=couleur_fond)
    frame_input_aut_headers.pack(anchor="w")
    frame_input_aut_liees = tk.Frame(frame_input_aut, bg=couleur_fond)
    frame_input_aut_liees.pack(anchor="w")

    frame_output = tk.Frame(zone_actions,
                            bg=couleur_fond, padx=10, pady=10,
                            highlightthickness=2, highlightbackground=couleur_bouton)
    frame_output.pack(side="left", anchor="w")
    frame_output_file = tk.Frame(frame_output, bg=couleur_fond, padx=10, pady=10)
    frame_output_file.pack()
    frame_output_options = tk.Frame(frame_output, bg=couleur_fond, padx=10, pady=10)
    frame_output_options.pack()
    frame_output_options_marc = tk.Frame(frame_output_options, bg=couleur_fond)
    frame_output_options_marc.pack(anchor="w")
    frame_output_options_format_global = tk.Frame(frame_output_options, bg=couleur_fond)
    frame_output_options_format_global.pack()
    frame_output_options_format = tk.Frame(frame_output_options_format_global, bg=couleur_fond)
    frame_output_options_format.pack(side="left", anchor="nw")
    frame_output_options_intermediaire = tk.Frame(frame_output_options_format_global, bg=couleur_fond)
    frame_output_options_intermediaire.pack(side="left", anchor="nw")
    frame_output_options_si_xml = tk.Frame(frame_output_options_format_global, bg=couleur_fond)
    frame_output_options_si_xml.pack(side="left", anchor="nw")
    
    frame_outputID = tk.Frame(frame_output, bg=couleur_fond)
    frame_outputID.pack(anchor="w")
    # forms.add_saut_de_ligne(frame_outputID)

    zone_notes_message_en_cours = tk.Frame(
        zone_notes, padx=20, bg=couleur_fond)
    zone_notes_message_en_cours.pack()

    


    main.download_zone(
        frame_input_file,
        "Sélectionner un fichier contenant\nune liste de n° de notices\nARK BnF ou PPN Abes\n(un numéro par ligne)",
        entry_file_list,
        couleur_fond,
        zone_notes_message_en_cours
        )

    main.download_zone(
                        frame_output_file,
                        "Sélectionner un dossier de destination",
                        main.output_directory,
                        couleur_fond,
                        type_action="askdirectory",
                        widthb = [40,1]
                        )

    type_records = tk.IntVar()          # ARK de BIB ou d'AUT ?
    correct_record_option = tk.IntVar() # 1 ou 2 colonnes ?
    headers = tk.IntVar()               # Fichier avec en-têtes ?
    headers.set(1)

    AUTlieesAUT = tk.IntVar()           # notices d'autorité liées
    AUTlieesSUB = tk.IntVar()
    AUTlieesWORK = tk.IntVar()

    format_records_choice = tk.IntVar() # Choix du format
    format_records_choice.set(1)
    format_file = tk.IntVar()
    format_file.set(1)
    
    frame2var = [{"frame": frame_input_aut_file,
                  "name": "frame_input_aut_file",
                  "variables": [["type_records", type_records],
                                ["correct_record_option", correct_record_option]]},
                 {"frame": frame_input_aut_headers,
                  "name": "frame_input_aut_headers",             
                   "variables": [["headers", headers]]},
                 {"frame": frame_input_aut_liees,
                  "name": "frame_input_aut_liees", 
                  "variables": [["AUTlieesAUT", AUTlieesAUT],
                                ["AUTlieesSUB", AUTlieesSUB],
                                ["AUTlieesWORK", AUTlieesWORK]]
                 },
                 {"frame": frame_output_options_format,
                  "name": "frame_output_options_format",
                  "variables": [["format_file", format_file]]
                 },
                 {"frame": frame_output_options_marc,
                  "name": "frame_output_options_marc",
                  "variables": [["format_records_choice", format_records_choice]]
                 }
                ]
    
    forms.display_options(frame2var, forms.form_ark2records)

    xml_encoding_option = forms.Combobox(frame_output_options_si_xml,
                                         forms.form_ark2records["frame_output_options_si_xml"]["xml_encoding_option"]["title"],
                                         forms.form_ark2records["frame_output_options_si_xml"]["xml_encoding_option"]["values"],
                                         forms.form_ark2records["frame_output_options_si_xml"]["xml_encoding_option"]["params"]
                                        )

    select_fields = forms.Entry(frame_output_options_si_xml,
                                forms.form_ark2records["frame_output_options_si_xml"]["select_fields"]["title"],
                                forms.form_ark2records["frame_output_options_si_xml"]["select_fields"]["params"])
    outputID = forms.Entry(frame_outputID,
                           forms.form_ark2records["frame_outputID"]["outputID"]["title"],
                           forms.form_ark2records["frame_outputID"]["outputID"]["params"])

    forms.add_saut_de_ligne(frame_input_aut_liees, nb_sauts=5)
    forms.add_saut_de_ligne(frame_output_options_intermediaire, nb_sauts=1)
    forms.add_saut_de_ligne(frame_outputID, nb_sauts=1)
    


    # file_format.focus_set()
    b = tk.Button(
        zone_ok_help_cancel,
        text="OK",
        command=lambda: launch(
            entry_file_list,
            type_records.get(),
            correct_record_option.get(),
            headers.get(),
            AUTlieesAUT.get(),
            AUTlieesSUB.get(),
            AUTlieesWORK.get(),
            outputID.value.get(),
            format_records_choice.get(),
            format_file.get(),
            xml_encoding_option.options.get(),
            select_fields.value.get(),
            master,
            form,
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
    
    forms.add_saut_de_ligne(zone_ok_help_cancel)

    forum_button = forms.forum_button(zone_ok_help_cancel)
    forum_button.pack()

    tk.Label(zone_ok_help_cancel, text="\n",
             bg=couleur_fond, font="Arial 4 normal").pack()
    cancel = tk.Button(zone_ok_help_cancel, text="Annuler", bg=couleur_fond,
                       command=lambda: main.annuler(form), pady=10, padx=5, width=12)
    cancel.pack()

    forms.footer(zone_notes, couleur_fond)

    tk.mainloop()


if __name__ == '__main__':
    multiprocessing.freeze_support()
    forms.default_launch()
