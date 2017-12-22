# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 09:43:05 2017

@author: BNF0017855
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 18:30:30 2017

@author: Etienne Cavalié

Programme de manipulations de données liées à la Transition bibliographique pour les bibliothèques françaises

"""

from lxml import etree
from urllib import request
import urllib.parse
from unidecode import unidecode
import urllib.error as error
import csv
import tkinter as tk
from tkinter import filedialog
from collections import defaultdict
import re
import webbrowser
import codecs
import json
import noticesbib2arkBnF as bib2ark
import marc2tables as marc2tables
import ark2records as ark2records

#import matplotlib.pyplot as plt

version = 0.03
lastupdate = "11/11/2017"
programID = "transbiblio"

ns = {"srw":"http://www.loc.gov/zing/srw/", "mxc":"info:lc/xmlns/marcxchange-v2", "m":"http://catalogue.bnf.fr/namespaces/InterXMarc","mn":"http://catalogue.bnf.fr/namespaces/motsnotices"}
nsSudoc = {"rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#", "bibo":"http://purl.org/ontology/bibo/", "dc":"http://purl.org/dc/elements/1.1/", "dcterms":"http://purl.org/dc/terms/", "rdafrbr1":"http://rdvocab.info/RDARelationshipsWEMI/", "marcrel":"http://id.loc.gov/vocabulary/relators/", "foaf":"http://xmlns.com/foaf/0.1/", "gr":"http://purl.org/goodrelations/v1#", "owl":"http://www.w3.org/2002/07/owl#", "isbd":"http://iflastandards.info/ns/isbd/elements/", "skos":"http://www.w3.org/2004/02/skos/core#", "rdafrbr2":"http://RDVocab.info/uri/schema/FRBRentitiesRDA/", "rdaelements":"http://rdvocab.info/Elements/", "rdac":"http://rdaregistry.info/Elements/c/", "rdau":"http://rdaregistry.info/Elements/u/", "rdaw":"http://rdaregistry.info/Elements/w/", "rdae":"http://rdaregistry.info/Elements/e/", "rdam":"http://rdaregistry.info/Elements/m/", "rdai":"http://rdaregistry.info/Elements/i/", "sudoc":"http://www.sudoc.fr/ns/", "bnf-onto":"http://data.bnf.fr/ontology/bnf-onto/"}


errors = {
        "no_internet" : "Attention : Le programme n'a pas d'accès à Internet.\nSi votre navigateur y a accès, vérifiez les paramètres de votre proxy"
        }

def click2help(url):
    webbrowser.open(url)
def annuler(master):
    master.destroy()

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

def download_last_update(url="https://github.com/Lully/transbiblio/"):
    url = "https://github.com/Lully/transbiblio/"
    webbrowser.open(url)

def check_access_to_network():
    access_to_network = True
    try:
        request.urlopen("http://www.bnf.fr")
    except error.URLError:
        print("Pas de réseau internet")
        access_to_network = False
    return access_to_network

def form_saut_de_ligne(frame, couleur_fond):
    tk.Label(frame, text="\n", bg=couleur_fond).pack()

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
    master.iconbitmap(r'favicon.ico')
    
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

#popup_filename = ""
    
def openfile(frame,liste,background_color="white"):
    liste = []
    liste.append(filedialog.askopenfilename(title='Sélectionner un fichier'))
    filename_print = liste[0].split("/")[-1].split("\\")[-1]
    tk.Label(frame,text=filename_print, bg=background_color).pack()


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
    
    bib2arkButton = tk.Button(frame2, text = "Aligner ses données (tableaux)\n avec le catalogue BnF", command=lambda: bib2ark.formulaire_noticesbib2arkBnF(access_to_network,[0,False]), padx=10,pady=10, bg="#fefefe")
    bib2arkButton.pack()
    
    ark2recordsButton = tk.Button(frame3, text = "Exporter une liste d'ARK BnF\n en notices XML", 
                                  command=lambda: ark2records.formulaire_ark2records(access_to_network,[0,False]), 
                                  padx=10,pady=10, bg="#99182D", fg="white")
    ark2recordsButton.pack()


    
    tk.Label(zone_ok_help_cancel,text=" ", pady=5, bg=couleur_fond).pack()
    

    call4help = tk.Button(frame_help_cancel, text="Besoin d'aide ?", command=lambda: click2help("https://github.com/Lully/transbiblio"), pady=5, padx=5, width=12)
    call4help.pack()
    cancel = tk.Button(frame_help_cancel, text="Annuler", command=lambda: annuler(master), pady=5, padx=5, width=12)
    cancel.pack()



    tk.Label(zone_notes, text = "Version " + str(version) + " - " + lastupdate, bg=couleur_fond).pack()

    
    if (last_version[1] == True):
        download_update = tk.Button(zone_notes, text = "Télécharger la version " + str(last_version[0]), command=download_last_update)
        download_update.pack()

    
    tk.mainloop()
    

if __name__ == '__main__':
    access_to_network = check_access_to_network()
    last_version = [0,False]
    if(access_to_network is True):
        last_version = check_last_compilation(programID)
    formulaire_main(access_to_network, last_version)
