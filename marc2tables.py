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


from unidecode import unidecode
import urllib.error as error
import tkinter as tk
from collections import defaultdict
import re
import webbrowser
import noticesbib2arkBnF as bib2ark
import pymarc as mc
import main as main

version = 0.01
programID = "marc2tables"
lastupdate = "10/11/2017"
last_version = [version, False]

# =============================================================================
# Creation des fichiers résultats
# =============================================================================


def create_file_doc_record(doc_record, id_traitement):
    filename= "-".join([id_traitement, doc_record_type[doc_record]]) + ".txt"
    file = open(filename, "w", encoding="utf-8")
    return file

# =============================================================================
# Fonctions de nettoyage
# =============================================================================
chiffers = ["0","1","2","3","4","5","6","7","8","9"]
letters = ["a","b","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
punctation = [".",",",";",":","?","!","%","$","£","€","#","\\","\"","&","~","{","(","[","`","\\","_","@",")","]","}","=","+","*","\/","<",">",")","}"]
           
liste_fichiers = []
liste_resultats = defaultdict(list)
              
doctype = {"a":"texte",
               "b":"manuscrit",
               "c":"partition",
               "d":"partition manuscrite",
               "e":"carte",
               "f":"carte manuscrite",
               "g":"video",
               "i":"son - non musical",
               "j":"son - musique",
               "k":"image, dessin",
               "l":"ressource électronique",
               "m":"multimedia",
               "r":"objet"
               }
recordtype = {"a":"analytique",
               "i":"feuillets mobiles, etc",
               "m":"monographie",
               "s":"périodiques",
               "c":"collection"}

doc_record_type = defaultdict(str)
for doct in doctype:
    for recordt in recordtype:
        dcrec = doct + recordt
        dcrec_libelles = "-".join([doctype[doct],recordtype[recordt]])
        doc_record_type[dcrec] = dcrec_libelles
#suppression des signes de ponctuation
def clean_punctation(text):
    for char in punctation:
        text = text.replace(char, " ")
    return text

def clean_letters(text):
    for char in letters:
        text = text.replace(char, " ")
    return text

def clean_spaces(text):
    text = re.sub("\s\s+" , " ", text).strip()
    return text

def clean_accents_case(text):
    text = unidecode(text).lower()
    return text
# =============================================================================
# Définition des zones pour chaque élément
# =============================================================================

def record2doctype(label):
    return label[6]

def record2recordtype(label):
    return label[7]

def path2value(record, field_subfield):
    value = None
    val_list = []
    #print(field_subfield)
    if (field_subfield.find("$")>-1):
        field = field_subfield.split("$")[0]
        subfield = field_subfield.split("$")[1]
        for f in record.get_fields(field): 
            for subf in f.get_subfields(subfield):
                val_list.append(subf)
        if (val_list != []):
            value = ";".join(val_list)
    else:
        if (record[field_subfield] is not None and int(field_subfield) < 10):
            value = record[field_subfield].data
    return value




def record2meta(record, liste_elements, alternate_list=[]):
    zone = []
    for el in liste_elements:
        value = path2value(record, el)
        #print("record2meta : " + el + " / "  + str(value))
        if (value is not None):
            zone.append(value)
    #zone = [path2value(record, el) for el in liste_elements if path2value(record, el) is not None]
    if (zone == [] and alternate_list != []):
        for el in alternate_list:
            value = path2value(record, el)
            if (value is not None):
                zone.append(value)
        #zone = [path2value(record, el) for el in alternate_list if path2value(record, el) is not None]
    zone = " ".join(zone)
    #print(zone)
    return zone

def record2title(f200a_e):
    title = clean_spaces(f200a_e)
    title = clean_punctation(title)
    return title

def record2date(f100,f210d):
    date = ""
    if (isinstance(f100[13:17],int) == True):
        date = f100[13:17]
    else:
        date = f210d
    date = clean_punctation(date)
    date = clean_letters(date)
    date = clean_spaces(date)
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
        if (f035.find("frbn")>-1):
            frbnf.append(f035)
    frbnf = ";".join(frbnf)
    return frbnf

def record2isbn(f010a):
    isbn = f010a
    return isbn

def record2ean(f038a):
    ean = f038a
    return ean

def record2issn(f011a):
    issn = f011a
    return issn

def record2id_commercial_aud(f073a):
    return f073a
# =============================================================================
# Gestion des mises à jour
# =============================================================================
def download_last_update():
    url = "https://github.com/Lully/transbiblio"
    webbrowser.open(url)


def iso2tables(entry_filename, id_traitement):
    with open(entry_filename, 'rb') as fh:
        collection = mc.MARCReader(fh)
        for record in collection:
            record2listemetas(record)
    

def xml2tables(entry_filename, id_traitement):
    collection = mc.marcxml.parse_xml_to_array(entry_filename, strict=False)
    for record in collection:
        record2listemetas(record)


def record2listemetas(record):
    numNot = record2meta(record,["001"])
    doctype = record2doctype(record.leader)
    recordtype = record2recordtype(record.leader)
   
    title = record2title(
                record2meta(record, ["200$a","200$e"])
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
    date = record2date(record2meta(record,["100"]), record2meta(record,["210$d"]))
    ark = record2ark(record2meta(record,["033$a"]))
    frbnf = record2frbnf(record2meta(record,["035$a"]))
    isbn = record2isbn(record2meta(record,["010$a"]))
    issn = record2isbn(record2meta(record,["011$a"]))
    ean =  record2ean(record2meta(record,["038$a"]))
    id_commercial_aud = record2id_commercial_aud(record2meta(record,["073$a"]))
    

    doc_record = doctype + recordtype
    doc_record = doc_record.strip()
    if (doc_record not in liste_fichiers):
        liste_fichiers.append(doc_record)
        
    meta = []
    if (doc_record == "am"):
        meta = [numNot,frbnf,ark,isbn,ean,title,authors, date]
    if (doc_record == "jm"):
        meta = [numNot,frbnf,ark,ean,id_commercial_aud,title,authors2keywords,date]
    if (doc_record == "as"):
        meta = [numNot,frbnf,ark,issn,title,authors, date]
    print(meta)
    liste_resultats[doc_record].append(meta)
            
def write_reports(id_traitement):
    for doc_record in liste_resultats:
        file = create_file_doc_record(doc_record, id_traitement)
        for record in liste_resultats[doc_record]:
            file.write("\t".join(record) + "\n")            

    
def end_of_treatments(master,id_traitement):
    write_reports(id_traitement)
    master.destroy()


def launch(master,entry_filename,file_format, output_ID):
    main.generic_input_controls(entry_filename)
    if (file_format == 1):
        iso2tables(entry_filename, output_ID)
    else:
        xml2tables(entry_filename, output_ID)
    end_of_treatments(master,output_ID)


def formulaire_marc2tables(access_to_network=True, last_version=[version, False]):
# =============================================================================
# Structure du formulaire - Cadres
# =============================================================================
    couleur_fond = "white"
    couleur_bouton = "#2D4991"
    #couleur_bouton = "#99182D"
    
    [master,
     zone_alert_explications,
     zone_access2programs,
     zone_actions,
     zone_ok_help_cancel,
     zone_notes] = main.form_generic_frames("Conversion de fichiers de notices MARC en tableaux",
                                      couleur_fond,couleur_bouton,
                                      access_to_network)
    
    
    cadre_input = tk.Frame(zone_actions, highlightthickness=2, highlightbackground=couleur_bouton, relief="groove", height=150, padx=10,bg=couleur_fond)
    cadre_input.pack(side="left", anchor="w")
    cadre_input_header = tk.Frame(cadre_input,bg=couleur_fond)
    cadre_input_header.pack(anchor="w")
    cadre_input_file = tk.Frame(cadre_input,bg=couleur_fond)
    cadre_input_file.pack(anchor="w")
    cadre_input_infos_format = tk.Frame(cadre_input,bg=couleur_fond)
    cadre_input_infos_format.pack(anchor="w")
    cadre_input_type_docs = tk.Frame(cadre_input,bg=couleur_fond)
    cadre_input_type_docs.pack(anchor="w")
    
    cadre_inter = tk.Frame(zone_actions, borderwidth=0, padx=10,bg=couleur_fond)
    cadre_inter.pack(side="left")
    tk.Label(cadre_inter, text=" ",bg=couleur_fond).pack()


#=============================================================================
#     Formulaire - Fichier en entrée
# =============================================================================
 
    cadre_output = tk.Frame(zone_actions, highlightthickness=2, highlightbackground=couleur_bouton, relief="groove", height=150, padx=10,bg=couleur_fond)
    cadre_output.pack(side="left")
    cadre_output_header = tk.Frame(cadre_output,bg=couleur_fond)
    cadre_output_header.pack(anchor="w")
    cadre_output_nom_fichiers = tk.Frame(cadre_output,bg=couleur_fond)
    cadre_output_nom_fichiers.pack(anchor="w")
    cadre_output_explications = tk.Frame(cadre_output, padx=20,bg=couleur_fond)
    cadre_output_explications.pack(anchor="w")
    
    cadre_valider = tk.Frame(zone_ok_help_cancel, borderwidth=0, relief="groove", height=150, padx=10,bg=couleur_fond)
    cadre_valider.pack(side="left")
    
    #définition input URL (u)
    tk.Label(cadre_input_header,bg=couleur_fond, fg=couleur_bouton, text="En entrée :", justify="left", font="bold").pack(anchor="w")
    
    tk.Label(cadre_input_file,bg=couleur_fond, text="Fichier contenant les notices : ").pack(side="left")
    entry_filename = tk.Entry(cadre_input_file, width=40, bd=2)
    entry_filename.pack(side="left")
    entry_filename.focus_set()
    
    
    tk.Label(cadre_input_type_docs,bg=couleur_fond, text="\nFormat", 
             anchor="w", justify="left").pack(anchor="w")
    file_format = tk.IntVar()
    tk.Radiobutton(cadre_input_type_docs,bg=couleur_fond, text="iso2709", variable=file_format, value=1,
                   anchor="w",justify="left").pack(anchor="w")
    tk.Radiobutton(cadre_input_type_docs,bg=couleur_fond, text="Marc XML", variable=file_format, value=2,
                   anchor="w", justify="left").pack(anchor="w")
    file_format.set(1)
    
    tk.Label(cadre_input_type_docs, text="\n\n\n", bg=couleur_fond).pack()
    
# =============================================================================
#     Formulaire - Fichiers en sortie
# =============================================================================
# 
    
    #Choix du format
    tk.Label(cadre_output_header,bg=couleur_fond, fg=couleur_bouton, font="bold", 
             text="En sortie :", 
             justify="left").pack()
    tk.Label(cadre_output_nom_fichiers,bg=couleur_fond, 
             text="Identifiant des fichiers en sortie : ", 
             justify="left").pack(side="left")
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
    tk.Label(cadre_output_explications,bg=couleur_fond, 
             text=message_fichiers_en_sortie,
             justify="left").pack()
    #explications.pack()
    
    
    
    
    #Bouton de validation
    
    b = tk.Button(cadre_valider, bg=couleur_bouton, fg="white", font="bold", text = "OK", command=lambda: launch(master,entry_filename.get(),file_format.get(), output_ID.get()), borderwidth=5 ,padx=10, pady=10, width=10, height=4)
    b.pack()
    
    tk.Label(cadre_valider, font="bold", text="", bg=couleur_fond).pack()
    
    call4help = tk.Button(cadre_valider, text="Besoin d'aide ?", command=lambda: main.click2help("https://github.com/Lully/transbiblio"), padx=10, pady=1, width=15)
    call4help.pack()
    
    cancel = tk.Button(cadre_valider, bg=couleur_fond, text="Annuler", command=lambda: main.annuler(master), padx=10, pady=1, width=15)
    cancel.pack()
    
    tk.Label(zone_notes, text = "Version " + str(version) + " - " + lastupdate, bg=couleur_fond).pack()
    
    if (last_version[1] == True):
        download_update = tk.Button(zone_notes, text = "Télécharger la version " + str(last_version[0]), command=download_last_update)
        download_update.pack()
    
    tk.mainloop()

if __name__ == '__main__':
    access_to_network = main.check_access_to_network()
    if(access_to_network is True):
        last_version = main.check_last_compilation(programID)
    formulaire_marc2tables(access_to_network,last_version)

