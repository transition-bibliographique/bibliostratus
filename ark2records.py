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

def callback():
    filename = entry_filename.get()
    format_BIB = ""
    if (format_records.get() == 1):
        format_BIB = "unimarcxchange"
    elif(format_records.get() == 2):
        format_BIB = "unimarcxchange-anl"
    elif(format_records.get() == 2):
        format_BIB = "intermarcxchange"
    elif(format_records.get() == 2):
        format_BIB = "intermarcxchange-anl"
    AUT = AUTliees.get()   
    bib_file_debut()
    if (AUT == 1):
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

def formulaire_ark2records():
    master = tk.Tk()
    master.config(padx=30, pady=20)
    master.title("Récupérer les notices BnF complètes à partir des ARK")
    master.iconbitmap(r'favicon.ico')
    
    #définition input URL (u)
    tk.Label(master, text="\nFichier contenant les ARK\n (1 par ligne)", justify="left").pack(side="left")
    entry_filename = tk.Entry(master, width=20, bd=2)
    entry_filename.pack(side="left")
    entry_filename.focus_set()
    
    #notices d'autorité liées
    AUTliees = tk.IntVar()
    b = tk.Checkbutton(master, text="Récupérer aussi les notices d'autorité liées", variable=AUTliees)
    b.pack(side="left",anchor=tk.SW)
    b.focus_set()
    
    #Choix du format
    tk.Label(master, text="\tEn sortie : ").pack(side="left")
    format_records = tk.IntVar()
    tk.Radiobutton(master, text="Unimarc", variable=format_records , value=1).pack(side="left")
    tk.Radiobutton(master, text="Unimarc avec ANL", justify="left", variable=format_records , value=2).pack(side="left")
    tk.Radiobutton(master, text="Intermarc", justify="left", variable=format_records , value=3).pack(side="left")
    tk.Radiobutton(master, text="Intermarc avec ANL", justify="left", variable=format_records , value=4).pack(side="left")
    format_records.set(1)
    
    #file_format.focus_set()
    b = tk.Button(master, text = "OK", width = 20, command = callback, borderwidth=1)
    b.pack()
    
    tk.mainloop()
    

if __name__ == '__main__':
    formulaire_ark2records()