# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 09:46:33 2017

@author: BNF0017855
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 09:43:05 2017

@author: BNF0017855
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 18:30:30 2017

@author: Etienne Cavalié

Conversion de fichiers XML ou iso2709 en tableaux pour alignements

"""

from lxml import etree
from urllib import request
import urllib.parse
from unidecode import unidecode
import urllib.error as error
import csv
import tkinter as tk
from collections import defaultdict
import re
import webbrowser
import codecs
import json
import noticesbib2arkBnF as bib2ark
import pymarc as mc


version = 0.01
programID = "marc2tables"
lastupdate = "10/11/2017"
last_version = [version, False]
# =============================================================================
# Gestion des mises à jour
# =============================================================================
def download_last_update():
    url = "https://github.com/Lully/transbiblio"
    webbrowser.open(url)


def iso2tables(entry_filename):
    with open(entry_filename, 'r', encoding="utf-8") as fh:
        reader = mc.MARCReader(fh)
        for record in reader:
            print(record.title())


def xml2tables(entry_filename):
    with open(entry_filename, 'r', encoding="utf-8") as fh:
        reader = mc.MARCReader(fh)
        for record in reader:
            print(record.title())

def click2help():
    webbrowser.open("http://bibliotheques.worpdress.com/")
def annuler(master):
    master.destroy()

def launch(entry_filename,file_format):
    if (file_format == 1):
        iso2tables(entry_filename)
    else:
        xml2tables(entry_filename)





def formulaire_marc2tables():
# =============================================================================
# Structure du formulaire - Cadres
# =============================================================================
    couleur_fond = "white"
    couleur_bouton = "#99182D"
    
    master = tk.Tk()
    master.config(padx=30, pady=20,bg=couleur_fond)
    master.title("Conversion de fichiers de notices Marc en tableaux")
    
    zone_formulaire = tk.Frame(master, bg=couleur_fond)
    zone_formulaire.pack()
    zone_commentaires = tk.Frame(master, bg=couleur_fond, pady=10)
    zone_commentaires.pack()
    
    cadre_input = tk.Frame(zone_formulaire, highlightthickness=2, highlightbackground=couleur_bouton, relief="groove", height=150, padx=10,bg=couleur_fond)
    cadre_input.pack(side="left")
    cadre_input_header = tk.Frame(cadre_input,bg=couleur_fond)
    cadre_input_header.pack()
    cadre_input_file = tk.Frame(cadre_input,bg=couleur_fond)
    cadre_input_file.pack()
    cadre_input_infos_format = tk.Frame(cadre_input,bg=couleur_fond)
    cadre_input_infos_format.pack()
    cadre_input_type_docs = tk.Frame(cadre_input,bg=couleur_fond)
    cadre_input_type_docs.pack()
    
    cadre_inter = tk.Frame(zone_formulaire, borderwidth=0, padx=10,bg=couleur_fond)
    cadre_inter.pack(side="left")
    tk.Label(cadre_inter, text=" ",bg=couleur_fond).pack()

#=============================================================================
#     Formulaire - Fichier en entrée
# =============================================================================
 
    cadre_output = tk.Frame(zone_formulaire, highlightthickness=2, highlightbackground=couleur_bouton, relief="groove", height=150, padx=10,bg=couleur_fond)
    cadre_output.pack(side="left")
    cadre_output_header = tk.Frame(cadre_output,bg=couleur_fond)
    cadre_output_header.pack()
    cadre_output_nom_fichiers = tk.Frame(cadre_output,bg=couleur_fond)
    cadre_output_nom_fichiers.pack()
    cadre_output_explications = tk.Frame(cadre_output, padx=20,bg=couleur_fond)
    cadre_output_explications.pack()
    
    cadre_valider = tk.Frame(zone_formulaire, borderwidth=0, relief="groove", height=150, padx=10,bg=couleur_fond)
    cadre_valider.pack(side="left")
    
    #définition input URL (u)
    tk.Label(cadre_input_header,bg=couleur_fond, fg=couleur_bouton, text="En entrée :                                                                                       ", justify="left", font="bold").pack()
    
    tk.Label(cadre_input_file,bg=couleur_fond, text="Fichier contenant les notices").pack(side="left")
    entry_filename = tk.Entry(cadre_input_file, width=40, bd=2)
    entry_filename.pack(side="left")
    entry_filename.focus_set()
    
    
    tk.Label(cadre_input_type_docs,bg=couleur_fond, text="\nFormat", anchor="w").pack()
    file_format = tk.IntVar()
    tk.Radiobutton(cadre_input_type_docs,bg=couleur_fond, text="iso2709", variable=file_format , value=1, justify="left").pack()
    tk.Radiobutton(cadre_input_type_docs,bg=couleur_fond, text="Marc XML", variable=file_format , value=2, justify="left").pack()
    file_format.set(1)
    
    tk.Label(cadre_input_type_docs, text="\n\n\n", bg=couleur_fond).pack()
    
# =============================================================================
#     Formulaire - Fichiers en sortie
# =============================================================================
# 
    
    #Choix du format
    tk.Label(cadre_output_header,bg=couleur_fond, fg=couleur_bouton,text="En sortie :                                                                              ", font="bold").pack()
    tk.Label(cadre_output_nom_fichiers,bg=couleur_fond, text="Identifiant des fichiers en sortie").pack(side="left")
    output_ID = tk.Entry(cadre_output_nom_fichiers, width=40, bd=2)
    output_ID.pack(side="left")
    
    #Ajout (optionnel) d'un identifiant de traitement
    message_fichiers_en_sortie = """
    Le programme va générer plusieurs fichiers, par type de document,
    en fonction du processus d'alignement avec les données de la BnF et des métadonnées utilisées pour cela :
    - monographies imprimées
    - périodiques
    - audiovisuel (CD/DVD)
    - autres non identifiés
    Pour faire cela, il utilise les informations en zones codées dans chaque notice Unimarc
    
    """
    tk.Label(cadre_output_explications,bg=couleur_fond, text=message_fichiers_en_sortie,
             anchor='nw').pack()
    
    
    
    
    #Bouton de validation
    
    b = tk.Button(cadre_valider, bg=couleur_bouton, fg="white", font="bold", text = "OK", command=lambda: launch(entry_filename.get(),file_format.get()), borderwidth=5 ,padx=10, pady=10, width=10, height=4)
    b.pack()
    
    tk.Label(cadre_valider, font="bold", text="", bg=couleur_fond).pack()
    
    call4help = tk.Button(cadre_valider, text="Besoin d'aide ?", command=click2help, padx=10, pady=1, width=15)
    call4help.pack()
    
    cancel = tk.Button(cadre_valider, bg=couleur_fond, text="Annuler", command=annuler, padx=10, pady=1, width=15)
    cancel.pack()
    
    tk.Label(zone_commentaires, text = "Version " + str(version) + " - " + lastupdate, bg=couleur_fond).pack()
    
    if (last_version[1] == True):
        download_update = tk.Button(zone_commentaires, text = "Télécharger la version " + str(last_version[0]), command=download_last_update)
        download_update.pack()
    
    tk.mainloop()

if __name__ == '__main__':
    formulaire_marc2tables()

