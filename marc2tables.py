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

Programme d'identification des ARK BnF à partir de numéros FRBNF

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

def launch():
    print("OK")

def formulaire_marc2tables():
    couleur_fond = "white"
    couleur_bouton = "#2D4991"
    
    master = tk.Tk()
    master.config(padx=30, pady=20,bg=couleur_fond)
    master.title("Programme d'alignement de données bibliographiques avec la BnF")
    
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
    
    cadre_inter = tk.Frame(master, borderwidth=0, padx=10,bg=couleur_fond)
    cadre_inter.pack(side="left")
    tk.Label(cadre_inter, text=" ",bg=couleur_fond).pack()
    
    cadre_output = tk.Frame(zone_formulaire, highlightthickness=2, highlightbackground=couleur_bouton, relief="groove", height=150, padx=10,bg=couleur_fond)
    cadre_output.pack(side="left")
    cadre_output_header = tk.Frame(cadre_output,bg=couleur_fond)
    cadre_output_header.pack()
    cadre_output_nb_fichier = tk.Frame(cadre_output,bg=couleur_fond)
    cadre_output_nb_fichier.pack(side="left")
    cadre_output_id_traitement = tk.Frame(cadre_output, padx=20,bg=couleur_fond)
    cadre_output_id_traitement.pack(side="left")
    
    cadre_valider = tk.Frame(zone_formulaire, borderwidth=0, relief="groove", height=150, padx=10,bg=couleur_fond)
    cadre_valider.pack(side="left")
    
    #définition input URL (u)
    tk.Label(cadre_input_header,bg=couleur_fond, fg=couleur_bouton, text="En entrée :                                                                                       ", justify="left", font="bold").pack()
    
    tk.Label(cadre_input_file,bg=couleur_fond, text="Fichier contenant les notices         ").pack(side="left")
    entry_filename = tk.Entry(cadre_input_file, width=40, bd=2)
    entry_filename.pack(side="left")
    entry_filename.focus_set()
    
    tk.Label(cadre_input_infos_format,bg=couleur_fond, text="                Séparateur TAB, Encodage UTF-8", justify="left").pack()
    
    
    tk.Label(cadre_input_type_docs,bg=couleur_fond, text="\nType de documents                                                                                                           ", anchor="w").pack()
    type_doc = tk.IntVar()
    tk.Radiobutton(cadre_input_type_docs,bg=couleur_fond, text="Documents imprimés (monographies)\nFormat : Num Not | FRBNF | ARK | ISBN | Titre | Auteur | Date                             ", variable=type_doc , value=1, justify="left").pack()
    tk.Radiobutton(cadre_input_type_docs,bg=couleur_fond, text="Audiovisuel (CD / DVD)\nFormat : Num Not | FRBNF | ARK | EAN | N° commercial | Titre | Auteur | Date", variable=type_doc , value=2, justify="left").pack()
    type_doc.set(1)
    
    
    
    #Choix du format
    tk.Label(cadre_output_header,bg=couleur_fond, fg=couleur_bouton,text="En sortie :                                                                              ", font="bold").pack()
    file_nb = tk.IntVar()
    tk.Radiobutton(cadre_output_nb_fichier,bg=couleur_fond, text="1 fichier                                               ", variable=file_nb , value=1, justify="left").pack()
    tk.Radiobutton(cadre_output_nb_fichier,bg=couleur_fond, text="Plusieurs fichiers \n(Pb / 0 / 1 / plusieurs ARK trouvés)", justify="left", variable=file_nb , value=2).pack()
    file_nb.set(2)
    
    #Ajout (optionnel) d'un identifiant de traitement
    tk.Label(cadre_output_id_traitement,bg=couleur_fond, text="\n\n\n\n").pack()
    tk.Label(cadre_output_id_traitement,bg=couleur_fond, text="ID traitement (optionnel)").pack()
    id_traitement = tk.Entry(cadre_output_id_traitement, width=20, bd=2)
    id_traitement.pack()
    tk.Label(cadre_output_id_traitement,bg=couleur_fond, text="\n").pack()
    
    
    #Bouton de validation
    
    b = tk.Button(cadre_valider, bg=couleur_bouton, fg="white", font="bold", text = "OK", command = launch, borderwidth=5 ,padx=10, pady=10, width=10, height=4)
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

