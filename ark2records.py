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
import csv
import pymarc as mc
import main as main


version = 0.01
programID = "ark2records"
lastupdate = "12/11/2017"
last_version = [version, False]


ns = {"srw":"http://www.loc.gov/zing/srw/", "mxc":"info:lc/xmlns/marcxchange-v2", "m":"http://catalogue.bnf.fr/namespaces/InterXMarc","mn":"http://catalogue.bnf.fr/namespaces/motsnotices"}

listeARK_BIB = []
listeNNA_AUT = []

def ark2record(ark,format_BIB,renvoyerNotice=False):
    url = "http://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query=bib.ark%20any%20%22" + urllib.parse.quote(ark) + "%22&recordSchema=" + format_BIB + "&maximumRecords=20&startRecord=1"
    records = etree.parse(url)
    for record in records.xpath("//srw:recordData/mxc:record",namespaces=ns):
        record2file(record)
    if (renvoyerNotice == True):
        return records

def record2string(record):
    record_str = str(etree.tostring(record))
    record_str = record_str.replace("b'","").replace("      '","\n").replace("\\n","\n").replace("\\t","\t").replace("\\r","\n")
    return (record_str)

def record2file(record):
    record_str = record2string(record)
    #print(record_str)
    record_type = record.get("type")
    if (record_type=="Bibliographic"):
        bib_records.write(record_str)
    elif(record_type=="Authority"):
        aut_records.write(record_str)

def ark2xml_aut(ark,format_BIB,aut_records):
    ark2record(ark,format_BIB)
    intermarc_record = ark2record(ark,"intermarcxchange",True)
    for field in listefieldsLiensAUT:
        path = '//mxc:datafield[@tag="' + field + '"]/mxc:subfield[@code="3"]'
        for datafield in intermarc_record.xpath(path, namespaces=ns):
            nna = datafield.text
            if (nna not in listeNNA_AUT):
                listeNNA_AUT.append(nna)
                url = "http://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query=aut.recordid%20all%20%22" + nna + "%22%20and%20aut.status%20any%20%22sparse%20validated%22&recordSchema=" + format_BIB + "&maximumRecords=20&startRecord=1"
                records = etree.parse(url)
                for record in records.xpath("//srw:recordData/mxc:record",namespaces=ns):
                    record2file(record)
            
    

def ark2xml(ark, format_BIB):
    ark2record(ark,format_BIB)
    
    
def bib_file_debut():
    bib_records.write("<?xml version='1.0'?>\n")
    bib_records.write("<mxc:collection ")
    for key in ns:
        bib_records.write(' xmlns:' + key + '="' + ns[key] + '"')
    bib_records.write(">\n")
def bib_file_fin():
    bib_records.write("</mxc:collection>")

def aut_file_debut():
    aut_records.write("<?xml version='1.0'?>\n")
    aut_records.write("<mxc:collection ")
    for key in ns:
        aut_records.write(' xmlns:' + key + '="' + ns[key] + '"')
    aut_records.write(">\n")
def aut_file_fin():
    aut_records.write("</mxc:collection>")

def callback(master, filename, AUTliees, outputID, format_records, format_file):
    format_BIB = ""
    if (format_records == 1):
        format_BIB = "unimarcxchange"
    elif(format_records == 2):
        format_BIB = "unimarcxchange-anl"
    elif(format_records == 3):
        format_BIB = "intermarcxchange"
    elif(format_records == 4):
        format_BIB = "intermarcxchange-anl"
    if (format_file == 2):
        bib_file_debut()
    if (AUTliees == 1):
        if (format_file == 2):
            aut_file_debut()
        with open(filename, newline='\n',encoding="utf-8") as csvfile:
            entry_file = csv.reader(csvfile, delimiter='\t')
            for line in entry_file:
                ark = line[0]
                if (ark not in listeARK_BIB):
                    listeARK_BIB.append(ark)
                    print(listeARK_BIB)
                    ark2xml_aut(ark,format_BIB,aut_records)
        aut_file_fin()
    else:
        with open(filename, newline='\n',encoding="utf-8") as csvfile:
            entry_file = csv.reader(csvfile, delimiter='\t')
            for line in entry_file:
                ark = line[0]
                if (ark not in listeARK_BIB):
                    print(ark)
                    listeARK_BIB.append(ark)
                    ark2xml(ark,format_BIB)
    bib_file_fin()
    print("\n\nProgramme terminé")
            
bib_records = open("noticesBIB.xml","w", encoding="utf-8")
aut_records = open("noticesAUT.xml","w", encoding="utf-8")
listefieldsLiensAUT = ["100","141","143","144","145",
                       "600","603","606","607","609","610","616","617",
                       "700","702","703","709","710","712","713","719","731"]
#==============================================================================
# Création de la boîte de dialogue
#==============================================================================

def formulaire_ark2records(access_to_network=True,last_version=version):
    couleur_fond = "white"
    couleur_bouton = "#a1a1a1"
    
    [master,
     zone_alert_explications,
     zone_access2programs,
     zone_actions,
     zone_ok_help_cancel,
     zone_notes] = main.form_generic_frames("Récupérer les notices complètes de la BnF à partir d'une liste d'ARK",
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
    #notices d'autorité liées
    AUTliees = tk.IntVar()
    b = tk.Checkbutton(frame_input_aut, text="Récupérer aussi les notices d'autorité liées", 
                       variable=AUTliees,
                       bg=couleur_fond, justify="left").pack(anchor="w")
    tk.Label(frame_input_aut, text="\n\n\n\n", bg=couleur_fond).pack()
    
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
                  command = lambda: callback(master, entry_filename.get(), AUTliees.get(), outputID.get(), format_records.get(), format_file.get()), 
                  width = 15, borderwidth=1, pady=20, fg="white",
                  bg=couleur_bouton)
    b.pack()
    
    main.form_saut_de_ligne(zone_ok_help_cancel, couleur_fond)
    call4help = tk.Button(zone_ok_help_cancel, text="Besoin d'aide ?", command=lambda: main.click2help("https://github.com/Lully/transbiblio"), padx=10, pady=1, width=15)
    call4help.pack()    
    cancel = tk.Button(zone_ok_help_cancel, bg=couleur_fond, text="Annuler", command=lambda: main.annuler(master), padx=10, pady=1, width=15)
    cancel.pack()

    
    tk.mainloop()
    

if __name__ == '__main__':
    access_to_network = main.check_access_to_network()
    if(access_to_network is True):
        last_version = main.check_last_compilation(programID)
    formulaire_ark2records(access_to_network,last_version)