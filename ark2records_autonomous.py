# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 17:55:32 2017

@author: Etienne Cavalié

A partir d'un fichier contenant une liste d'ARK de notices biblio, récupérer les notices complètes (en XML)
+ option pour récupérer les notices d'autorité
"""

import tkinter as tk
from lxml import etree
import urllib.parse
from urllib import request, error
import csv
import pymarc as mc
import os
import re
import codecs
import json
import webbrowser

version = 0.02
programID = "ark2records"
lastupdate = "12/11/2017"
last_version = [version, False]

access_to_network = True

ns = {"srw":"http://www.loc.gov/zing/srw/", "mxc":"info:lc/xmlns/marcxchange-v2", "m":"http://catalogue.bnf.fr/namespaces/InterXMarc","mn":"http://catalogue.bnf.fr/namespaces/motsnotices"}

listeARK_BIB = []
listeNNA_AUT = []
errors_list = []

dict_format_records={
        1:"unimarcxchange",
        2:"unimarcxchange-anl",
        3:"intermarcxchange",
        4:"intermarcxchange-anl"}
listefieldsLiensAUT = ["100","141","143","144","145",
                       "600","603","606","607","609","610","616","617",
                       "700","702","703","709","710","712","713","719","731"]


def ark2url(ark, type_record, format_BIB):
    query = type_record + '.persistentid any "' + ark + '"'
    if (type_record == "aut"):
        query += ' and aut.status any "sparse validated"'
    query = urllib.parse.quote(query)
    url = "http://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query=" + query + "&recordSchema=" + format_BIB + "&maximumRecords=20&startRecord=1"
    return url

def nn2url(nn, type_record, format_BIB):
    query = type_record + '.recordid any "' + nn + '"'
    if (type_record == "aut"):
        query += ' and aut.status any "sparse validated"'
    query = urllib.parse.quote(query)
    url = "http://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query=" + query + "&recordSchema=" + format_BIB + "&maximumRecords=20&startRecord=1"
    return url

def ark2record(ark, type_record, format_BIB, renvoyerNotice=False):
    url = ark2url(ark, type_record, format_BIB)
    try:
        etree.parse(request.urlopen(url))
    except error.URLerror:
        print("Pb d'accès à la notice " + ark)
    record = etree.parse(request.urlopen(url)).xpath("//srw:recordData/mxc:record",namespaces=ns)[0]
    if (renvoyerNotice == True):
        return record

def XMLrecord2string(record):
    record_str = str(etree.tostring(record))
    record_str = record_str.replace("b'","").replace("      '","\n").replace("\\n","\n").replace("\\t","\t").replace("\\r","\n")
    return (record_str)

def bib2aut(ark, aut_file, format_BIB, format_file):
    bib_record = ark2record(ark, "bib", "intermarcxchange", True)
    for field in listefieldsLiensAUT:
        path = '//mxc:datafield[@tag="' + field + '"]/mxc:subfield[@code="3"]'
        for datafield in bib_record.xpath(path, namespaces=ns):
            nna = datafield.text
            if (nna not in listeNNA_AUT):
                listeNNA_AUT.append(nna)
                url = nn2url(nna, "aut", format_BIB)
                try:
                    etree.parse(request.urlopen(url))
                except error.URLerror:
                    print("Pb d'accès à la notice " + nna)
                XMLrec = etree.parse(request.urlopen(url)).xpath("//srw:recordData/mxc:record",namespaces=ns)[0]
                record2file(aut_file, XMLrec, format_file)

   
def file_create(record_type, format_file, outputID):
    file = object
    id_filename = "-".join([outputID, record_type])
    if (format_file == 2):
        filename = id_filename + ".xml"
        file = open(filename, "w", encoding="utf-8")
        file.write("<?xml version='1.0'?>\n")
        file.write("<mxc:collection ")
        for key in ns:
            file.write(' xmlns:' + key + '="' + ns[key] + '"')
        file.write(">\n")
    else:
        filename = id_filename + ".iso2709"
        #file = mc.MARCWriter(codecs.open(filename,"wb",encoding="utf-8"))
        file = mc.MARCWriter(open(filename,"wb"))
    return file

def file_fin(file):
    file.write("</mxc:collection>")

def XMLrec2isorecord(XMLrec):
    XMLrec = XMLrec.replace("<mxc:","<").replace("</mxc:","</")
    XMLrec = "<collection>" + XMLrec + "</collection>"
    XMLrec = re.sub(r"<record[^>]+>",r"<record>",XMLrec)
    filename_temp = "temp.xml"
    file_temp = open(filename_temp,"w",encoding="utf-8")
    file_temp.write(XMLrec)
    return filename_temp

#test fonction de réencodage correct en UTF-8
def re_encode(record):
    record_reencode = record.as_dict()
    for field in record_reencode:
        if (subfields in field):
            for subfield in subfields:
                val = "subfield"
    print(record_reencode)
        #print(field.get_subfields.__str__)

def record2file(file, XMLrec, format_file):
    #Si sortie en iso2709
    if (format_file == 1):
        XMLrec_str = XMLrecord2string(XMLrec)
        filename_temp = XMLrec2isorecord(XMLrec_str)
        collection = mc.marcxml.parse_xml_to_array(filename_temp, strict=False)
        for record in collection:
            try:
                file.write(record)
            except UnicodeEncodeError as err:
#==============================================================================
#                 Gros pataquès insatisfaisant ici : écrire dans le fichier
#                 iso2709 une notice contenant des caractères non latins (grec, etc.)
#    Relire : https://groups.google.com/forum/#!topic/pymarc/Q444j3vY8LE
#==============================================================================
                #record_encoding = re_encode(record)
                errors_list.append([XMLrec_str, str(err)])
                record2 = str(record).encode("utf-8").decode("utf-8")
                print(record2)
                #file.write(record2)
            #file.write(record)
    #si sortie en XML
    if (format_file == 2):
        record = XMLrecord2string(XMLrec)
        file.write(record)

def generic_input_controls(filename):
    check_file_name(filename)
    
def check_file_name(filename):
    try:
        open(filename,"r")
    except FileNotFoundError:
        popup_errors("Le fichier " + filename + " n'existe pas")

def popup_errors(text):
    couleur_fond = "white"
    couleur_bordure = "red"
    [master,
            zone_alert_explications,
            zone_access2programs,
            zone_actions,
            zone_ok_help_cancel,
            zone_notes] = form_generic_frames("Alerte", couleur_fond, couleur_bordure,True)
    tk.Label(zone_access2programs, text=text, fg=couleur_bordure, 
             font="bold", bg=couleur_fond, padx=10, pady=10).pack()

def formulaire_main(access_to_network, last_version):
    couleur_fond = "white"
    couleur_bouton = "#e1e1e1"
    
    [master,
     zone_alert_explications,
     zone_access2programs,
     zone_actions,
     zone_ok_help_cancel,
     zone_notes] = form_generic_frames("La Transition bibliographique en chantant nous ouvre...",
                                      couleur_fond,
                                      couleur_bouton,access_to_network)

    if (access_to_network == False):
        tk.Label(zone_alert_explications, text=errors["no_internet"], 
                 bg=couleur_fond, fg="red").pack()
    
    frame1 = tk.Frame(zone_actions, highlightthickness=2, highlightbackground=couleur_bouton, bg=couleur_fond, pady=20, padx=20)
    frame1.pack(side="left")
    
    frame2 = tk.Frame(zone_actions, highlightthickness=2, highlightbackground=couleur_bouton, bg=couleur_fond, pady=20, padx=20)
    frame2.pack(side="left")
    
    frame3 = tk.Frame(zone_actions, highlightthickness=2, highlightbackground=couleur_bouton, bg=couleur_fond, pady=20, padx=20)
    frame3.pack(side="left")
    
    frame_help_cancel = tk.Frame(zone_ok_help_cancel, bg=couleur_fond, pady=10, padx=10)
    frame_help_cancel.pack()
    
    marc2tableButton = tk.Button(frame1, text = "Convertir un fichier Marc\n en tableaux", 
                                 command=lambda: marc2tables.formulaire_marc2tables(access_to_network), 
                                 padx=10,pady=10, bg="#2D4991",fg="white")
    marc2tableButton.pack()
    
    bib2arkButton = tk.Button(frame2, text = "Aligner ses données (tableaux)\n avec le catalogue BnF", command=bib2ark.formulaire_noticesbib2arkBnF, padx=10,pady=10, bg="#fefefe")
    bib2arkButton.pack()
    
    ark2recordsButton = tk.Button(frame3, text = "Exporter une liste d'ARK BnF\n en notices XML", 
                                  command=lambda: ark2records.formulaire_ark2records(access_to_network,[0,False]), 
                                  padx=10,pady=10, bg="#99182D", fg="white")
    ark2recordsButton.pack()

    call4help = tk.Button(zone_ok_help_cancel, text="Besoin d'aide ?", command=lambda: click2help("https://github.com/Lully/transbiblio"), pady=5, padx=5, width=12)
    call4help.pack()
    
    tk.Label(zone_ok_help_cancel,text=" ", pady=5, bg=couleur_fond).pack()
    
    cancel = tk.Button(frame_help_cancel, text="Annuler", command=lambda: annuler(master), pady=5, padx=5, width=12)
    cancel.pack()


    tk.Label(zone_notes, text = "Version " + str(version) + " - " + lastupdate, bg=couleur_fond).pack()

    
    if (last_version[1] == True):
        download_update = tk.Button(zone_notes, text = "Télécharger la version " + str(last_version[0]), command=download_last_update)
        download_update.pack()

    
    tk.mainloop()
    


def callback(master, filename, headers, AUTliees, outputID, format_records, format_file):
    generic_input_controls(filename)
    format_BIB = dict_format_records[format_records]
    bib_file = file_create("bib", format_file, outputID)
    if (AUTliees == 1):
        aut_file = file_create("aut", format_file, outputID)
    with open(filename, newline='\n',encoding="utf-8") as csvfile:
        entry_file = csv.reader(csvfile, delimiter='\t')
        if (headers == True):
            next(entry_file, None)
        for line in entry_file:
            ark = line[0]
            if (ark not in listeARK_BIB):
                print(ark)
                listeARK_BIB.append(ark)
                XMLrec = etree.parse(request.urlopen(ark2url(ark, "bib", format_BIB))).xpath("//srw:record/srw:recordData/mxc:record", namespaces=ns)[0]
                record2file(bib_file, XMLrec, format_file)
                if (AUTliees == 1):
                    bib2aut(ark, aut_file, format_BIB, format_file)
                
                    
        if (format_file == 2):
            file_fin(bib_file)
            if (AUTliees == 1):
                file_fin(aut_file)
    fin_traitements(master,outputID)

def errors_file(outputID):
    errors_file = open(outputID + "-errors.txt", "w", encoding="utf-8")
    for el in errors_list:
        errors_file.write(el[1] + "\n" + el[0] + "\n\n")
    
def fin_traitements(window,outputID):
    if (errors_list != []):
        errors_file(outputID)
    if (os.path.isfile("temp.xml") is True):
        os.remove("temp.xml")
    window.destroy()


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
   

def click2help(url):
    webbrowser.open(url)
def annuler(master):
    master.destroy()
    
def form_saut_de_ligne(frame, couleur_fond):
    tk.Label(frame, text="\n", bg=couleur_fond).pack()



#==============================================================================
# Création de la boîte de dialogue
#==============================================================================

def formulaire_ark2records(access_to_network=True,last_version=version):
    couleur_fond = "white"
    couleur_bouton = "#99182D"
    
    [master,
     zone_alert_explications,
     zone_access2programs,
     zone_actions,
     zone_ok_help_cancel,
     zone_notes] = form_generic_frames("Récupérer les notices complètes de la BnF à partir d'une liste d'ARK",
                                      couleur_fond,couleur_bouton,
                                      access_to_network)
    
    zone_ok_help_cancel.config(padx=10)
    
    frame_input = tk.Frame(zone_actions, 
                           bg=couleur_fond, padx=10, pady=10,
                           highlightthickness=2, highlightbackground=couleur_bouton)
    frame_input.pack(side="left", anchor="w", padx=10,pady=10)
    frame_input_file = tk.Frame(frame_input, bg=couleur_fond)
    frame_input_file.pack()
    frame_input_aut = tk.Frame(frame_input, bg=couleur_fond)
    frame_input_aut.pack()
    
    frame_output = tk.Frame(zone_actions, 
                           bg=couleur_fond, padx=10, pady=10,
                           highlightthickness=2, highlightbackground=couleur_bouton)
    frame_output.pack(side="left", anchor="w")
    frame_output_file = tk.Frame(frame_output, bg=couleur_fond, padx=10, pady=10)
    frame_output_file.pack(anchor="w")
    frame_output_options = tk.Frame(frame_output, bg=couleur_fond, padx=10, pady=10)
    frame_output_options.pack(anchor="w")
    frame_output_options_marc = tk.Frame(frame_output_options, bg=couleur_fond)
    frame_output_options_marc.pack(side="left", anchor="nw")
    frame_output_options_inter = tk.Frame(frame_output_options, bg=couleur_fond)
    frame_output_options_inter.pack(side="left")
    frame_output_options_format = tk.Frame(frame_output_options, bg=couleur_fond)
    frame_output_options_format.pack(side="left", anchor="nw")
    
    
    tk.Label(frame_input_file, text="Fichier contenant les ARK\n (1 par ligne)", 
             bg=couleur_fond, justify="left").pack(side="left", anchor="w")
    entry_filename = tk.Entry(frame_input_file, width=20, bd=2, bg=couleur_fond)
    entry_filename.pack(side="left")
    entry_filename.focus_set()
    
    tk.Label(frame_input_aut, text="\n", bg=couleur_fond).pack()
    #Fichier avec en-têtes ?
    headers = tk.IntVar()
    headerButton = tk.Checkbutton(frame_input_aut, text="Mon fichier a des en-têtes de colonne", 
                       variable=headers,
                       bg=couleur_fond, justify="left").pack(anchor="w")
    headers.set(1)
    #notices d'autorité liées
    AUTliees = tk.IntVar()
    b = tk.Checkbutton(frame_input_aut, text="Récupérer aussi les notices d'autorité liées", 
                       variable=AUTliees,
                       bg=couleur_fond, justify="left").pack(anchor="w")
    tk.Label(frame_input_aut, text="\n\n\n", bg=couleur_fond).pack()
    
    tk.Label(frame_output_file, text="ID de traitement (facultatif)",
             bg=couleur_fond).pack(side="left", anchor="w")
    outputID = tk.Entry(frame_output_file, bg=couleur_fond)
    outputID.pack(side="left", anchor="w")
    
    #Choix du format
    tk.Label(frame_output_options_marc, text="Notices à récupérer en :").pack(anchor="nw")
    format_records = tk.IntVar()
    tk.Radiobutton(frame_output_options_marc, text="Unimarc", variable=format_records , value=1, bg=couleur_fond).pack(anchor="nw")
    tk.Radiobutton(frame_output_options_marc, text="Unimarc avec ANL", justify="left", variable=format_records , value=2,bg=couleur_fond).pack(anchor="nw")
    tk.Radiobutton(frame_output_options_marc, text="Intermarc", justify="left", variable=format_records , value=3,bg=couleur_fond).pack(anchor="nw")
    tk.Radiobutton(frame_output_options_marc, text="Intermarc avec ANL", justify="left", variable=format_records , value=4,bg=couleur_fond).pack(anchor="nw")
    format_records.set(1)

    tk.Label(frame_output_options_inter, text="\t", bg=couleur_fond).pack(side="left")

    tk.Label(frame_output_options_format, text="Format du fichier :").pack(anchor="nw")    
    format_file = tk.IntVar()
    tk.Radiobutton(frame_output_options_format,bg=couleur_fond, 
                   text="iso2709", variable=format_file , value=1, justify="left").pack(anchor="nw")
    tk.Radiobutton(frame_output_options_format,bg=couleur_fond, 
                   text="Marc XML", variable=format_file , value=2, justify="left").pack(anchor="nw")
    format_file.set(1)
    
    
    #file_format.focus_set()
    b = tk.Button(zone_ok_help_cancel, text = "OK", 
                  command = lambda: callback(master, entry_filename.get(), headers.get(), AUTliees.get(), outputID.get(), format_records.get(), format_file.get()), 
                  width = 15, borderwidth=1, pady=20, fg="white",
                  bg=couleur_bouton)
    b.pack()
    
    form_saut_de_ligne(zone_ok_help_cancel, couleur_fond)
    call4help = tk.Button(zone_ok_help_cancel, text="Besoin d'aide ?", command=lambda: click2help("https://github.com/Lully/transbiblio"), padx=10, pady=1, width=15)
    call4help.pack()    
    cancel = tk.Button(zone_ok_help_cancel, bg=couleur_fond, text="Annuler", command=lambda: annuler(master), padx=10, pady=1, width=15)
    cancel.pack()

    tk.Label(zone_notes, text = "Version " + str(version) + " - " + lastupdate, bg=couleur_fond).pack()

    
    if (last_version[1] == True):
        download_update = tk.Button(zone_notes, text = "Télécharger la version " + str(last_version[0]), command=download_last_update)
        download_update.pack()
    
    tk.mainloop()

def download_last_update(url="https://github.com/Lully/transbiblio/"):
    url = "https://github.com/Lully/transbiblio/"
    webbrowser.open(url)

def form_generic_frames(title, couleur_fond, couleur_bordure,access_to_network):
#----------------------------------------------------
#|                    Frame                         |
#|            zone_alert_explications               |
#----------------------------------------------------
#|                    Frame                         |
#|             zone_access2programs                 |
#|                                                  |
#|              Frame           |       Frame       |
#|           zone_actions       |  zone_help_cancel |
#----------------------------------------------------
#|                    Frame                         |
#|                  zone_notes                      |
#----------------------------------------------------
    master = tk.Tk()
    master.config(padx=10,pady=10,bg=couleur_fond)
    master.title(title)
    
    zone_alert_explications = tk.Frame(master, bg=couleur_fond, pady=10)
    zone_alert_explications.pack()
    
    zone_access2programs = tk.Frame(master, bg=couleur_fond)
    zone_access2programs.pack()
    zone_actions = tk.Frame(zone_access2programs, bg=couleur_fond)
    zone_actions.pack(side="left")
    zone_ok_help_cancel = tk.Frame(zone_access2programs, bg=couleur_fond)
    zone_ok_help_cancel.pack(side="left")
    zone_notes = tk.Frame(master, bg=couleur_fond, pady=10)
    zone_notes.pack()

    if (access_to_network == False):
        tk.Label(zone_alert_explications, text=errors["no_internet"], 
                 bg=couleur_fond,  fg="red").pack()

    
    return [master,
            zone_alert_explications,
            zone_access2programs,
            zone_actions,
            zone_ok_help_cancel,
            zone_notes]


if __name__ == '__main__':
    #if(access_to_network is True):
    #    last_version = check_last_compilation(programID)
    formulaire_ark2records(True,[0.02, False])
