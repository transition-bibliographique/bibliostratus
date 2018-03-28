# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 18:30:30 2017

@author: Etienne Cavalié

Conversion de fichiers XML ou iso2709 en tableaux pour alignements

"""


from unidecode import unidecode
import urllib.error as error
import tkinter as tk
from tkinter import filedialog
from collections import defaultdict
import re
import webbrowser
import noticesbib2arkBnF as bib2ark
import noticesaut2arkBnF as aut2ark
import pymarc as mc
import main as main

version = 0.01
programID = "marc2tables"
lastupdate = "10/11/2017"
last_version = [version, False]

#Permet d'écrire dans une liste accessible au niveau général depuis le formulaire, et d'y accéder ensuite
entry_file_list = []
message_en_cours = []

output_directory_list = []

# =============================================================================
# Creation des fichiers résultats
# =============================================================================
popup_filename = []

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


doctypeAUT = {
               "c":"autorité",
               "n":"autorité",
               
               }
recordtypeAUT = {"a":"personne physique",
                 "b":"collectivité",
                 "c":"nom géographique Rameau",
                 "j":"nom commun Rameau"
               }



doc_record_type = defaultdict(str)

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

def record2doctype(label,rec_format=1):
    if (rec_format == 2):
        return label[5]
    else:
        return label[6]

def record2recordtype(label,rec_format=1):
    if (rec_format == 2):
        return label[9]
    else:
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

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False


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

def record2date(f100a,f210d):
    date = ""
    if (RepresentsInt(f100a[9:13]) == True):
        date = f100a[9:13]
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

def record2pubPlace(f210a):
    pubPlace = f210a
    return pubPlace

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
    url = "https://github.com/Transition-bibliographique/alignements-donnees-bnf/"
    webbrowser.open(url)


def iso2tables(master,entry_filename, rec_format, id_traitement):
    with open(entry_filename, 'rb') as fh:
        collection = mc.MARCReader(fh)
        collection.force_utf8 = True
        try:
            for record in collection:
                record2listemetas(record,rec_format)
        except mc.exceptions.RecordLengthInvalid as err:
            print("\n\n/*---------------------------------------------*\n\n")
            print(main.errors["pb_input_utf8"])
            print(err)
            print("\n\n*------------------------------------------------*/")
            main.popup_errors(master,main.errors["pb_input_utf8_marcEdit"], 
            "Aide en ligne : conversion iso2709 > XML",
            "https://github.com/Transition-bibliographique/alignements-donnees-bnf/wiki/1-%5BBleu%5D-Pr%C3%A9parer-ses-donn%C3%A9es-pour-l'alignement-%C3%A0-partir-d'un-export-catalogue#un-probl%C3%A8me-dencodage--passez-en-xml-avec-marcedit" 
            )
        

def xml2tables(master,entry_filename, rec_format, id_traitement):
    collection = mc.marcxml.parse_xml_to_array(entry_filename, strict=False)
    for record in collection:
        record2listemetas(record,rec_format)

def bibrecord2metas(numNot,doc_record,record):
    title = record2title(
                record2meta(record, ["200$a","200$e"])
                )
    keyTitle = record2title(
                record2meta(record, ["530$a"], ["200$a","200$e"])
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
    date = record2date(record2meta(record,["100$a"]), record2meta(record,["210$d"], ["219$d", "219$i", "219$p"]))
    numeroTome = record2numeroTome(record2meta(record,["200$h"], ["461$v"]))
    publisher = record2publisher(record2meta(record,["210$c"]))
    pubPlace = record2pubPlace(record2meta(record,["210$a"]))
    ark = record2ark(record2meta(record,["033$a"]))
    frbnf = record2frbnf(record2meta(record,["035$a"]))
    isbn = record2isbn(record2meta(record,["010$a"]))
    issn = record2isbn(record2meta(record,["011$a"]))
    ean =  record2ean(record2meta(record,["073$a"]))
    id_commercial_aud = record2id_commercial_aud(record2meta(record,["071$a"]))


    if (doc_record not in liste_fichiers):
        liste_fichiers.append(doc_record)
    if (doc_record == "am"):
        meta = [numNot,frbnf,ark,isbn,ean,title,authors2keywords, date, numeroTome, publisher]
    elif (doc_record == "im" or doc_record == "jm" or doc_record == "gm"):
        meta = [numNot,frbnf,ark,ean,id_commercial_aud,title,authors2keywords,date, publisher]
    elif (len(doc_record)>1 and doc_record[1] == "s"):
        if (keyTitle == ""):
            meta = [numNot, frbnf, ark, issn, title, authors2keywords, date, pubPlace]
        else:
            meta = [numNot, frbnf, ark, issn, keyTitle, authors2keywords, date, pubPlace]
    else:
        meta = [numNot, frbnf, ark, ean, title, authors, date]
    return meta

def record2isniAUT(isni):
    return isni

def record2firstnameAUT(name):
    return name

def record2lastnameAUT(name):
    return name

def record2firstdateAUT(f100a):
    return f100a[1:5]

def record2lastdateAUT(f100a):
    return f100a[1:5]

def autrecord2metas(numNot,doc_record,record):
    ark = record2ark(record2meta(record,["033$a"]))
    frbnf = record2frbnf(record2meta(record,["035$a"]))
    isni = record2isniAUT(record2meta(record,["010$a"]))
    firstname = record2firstnameAUT(record2meta(record,["200$a"],["210$a"]))
    lastname =  record2lastnameAUT(record2meta(record,["200$b"],["210$b"]))
    firstdate = record2firstdateAUT(record2meta(record,["103$a"]))
    lastdate = record2lastdateAUT(record2meta(record,["103$b"]))

    if (doc_record not in liste_fichiers):
        liste_fichiers.append(doc_record)
    meta = [numNot,frbnf,ark,isni,lastname,firstname,firstdate,lastdate]
    return meta   
    
def record2listemetas(record,rec_format=1):
    numNot = record2meta(record,["001"])
    doctype = record2doctype(record.leader,rec_format)
    recordtype = record2recordtype(record.leader,rec_format)
    
    doc_record = doctype + recordtype
    doc_record = doc_record.strip()
    meta = []
    if (rec_format == 2):
        meta = autrecord2metas(numNot,doc_record,record)
    else:
        meta = bibrecord2metas(numNot,doc_record,record)

    liste_resultats[doc_record].append(meta)
            
def write_reports(id_traitement):
    for doc_record in liste_resultats:
        if (doc_record == "am"):
            header_columns = bib2ark.header_columns_init_monimpr
        elif (doc_record == "im" or doc_record == "jm" or doc_record == "gm"):
            header_columns = bib2ark.header_columns_init_cddvd
        elif (doc_record == "ca"):
            header_columns = aut2ark.header_columns_init_aut2aut
        elif (len(doc_record)> 1 and doc_record[1] == "s"):
            header_columns = bib2ark.header_columns_init_perimpr
        else:
            header_columns = ["NumNotice","FRBNF","ARK","Autres métadonnées..."]
        file = create_file_doc_record(doc_record, id_traitement)
        file.write("\t".join(header_columns) + "\n")
        for record in liste_resultats[doc_record]:
            print(doc_record, ' - ', record[0])
            file.write("\t".join(record) + "\n")            

    
def end_of_treatments(form,id_traitement):
    write_reports(id_traitement)
    print("\n\n------------------------\n\nExtraction terminée\n\n------------------------")
    form.destroy()



def launch(form,entry_filename,file_format, rec_format, output_ID,master):
    
    main.check_file_name(form,entry_filename)
    #popup_en_cours = main.message_programme_en_cours(form)

    for doct in doctype:
        for recordt in recordtype:
            if (rec_format == 1):
                dcrec = doct + recordt
                doct_libelle = doct
                if (doct in doctype):
                    doct_libelle = doctype[doct]
                recordt_libelle = recordt
                if (recordt in recordtype):
                    recordt_libelle = recordtype[recordt]
                dcrec_libelles = "-".join([doct_libelle,recordt_libelle])
                doc_record_type[dcrec] = dcrec_libelles
            else:
                dcrec = doct + recordt
                doct_libelle = doct
                if (doct in doctypeAUT):
                    doct_libelle = doctypeAUT[doct]
                recordt_libelle = recordt
                if (recordt in recordtypeAUT):
                    recordt_libelle = recordtypeAUT[recordt]
                dcrec_libelles = "-".join([doct_libelle,recordt_libelle])
                doc_record_type[dcrec] = dcrec_libelles
                
    print("Fichier en entrée : ", entry_filename)
    if (file_format == 1):
        iso2tables(master,entry_filename, rec_format, output_ID)
    else:
        xml2tables(master,entry_filename, rec_format, output_ID)
    end_of_treatments(form,output_ID)



def formulaire_marc2tables(master,access_to_network=True, last_version=[version, False]):
# =============================================================================
# Structure du formulaire - Cadres
# =============================================================================
    couleur_fond = "white"
    couleur_bouton = "#2D4991"
    #couleur_bouton = "#99182D"
    
    [form,
     zone_alert_explications,
     zone_access2programs,
     zone_actions,
     zone_ok_help_cancel,
     zone_notes] = main.form_generic_frames(master,"Conversion de fichiers de notices MARC en tableaux",
                                      couleur_fond,couleur_bouton,
                                      access_to_network)
    
    
    cadre_input = tk.Frame(zone_actions, highlightthickness=2, highlightbackground=couleur_bouton, relief="groove", height=150, padx=10,bg=couleur_fond)
    cadre_input.pack(side="left", anchor="w")
    cadre_input_header = tk.Frame(cadre_input,bg=couleur_fond)
    cadre_input_header.pack(anchor="w")
    cadre_input_file = tk.Frame(cadre_input,bg=couleur_fond)
    cadre_input_file.pack(anchor="w")
    cadre_input_file_name = tk.Frame(cadre_input_file,bg=couleur_fond)
    cadre_input_file_name.pack(side="left")
    cadre_input_file_browse = tk.Frame(cadre_input_file,bg=couleur_fond)
    cadre_input_file_browse.pack(side="left")
    cadre_input_infos_format = tk.Frame(cadre_input,bg=couleur_fond)
    cadre_input_infos_format.pack(side="left")
    
    cadre_input_type_docs_interstice1 = tk.Frame(cadre_input,bg=couleur_fond)
    cadre_input_type_docs_interstice1.pack(side="left")
    
    cadre_input_type_docs = tk.Frame(cadre_input,bg=couleur_fond)
    cadre_input_type_docs.pack(side="left")
    cadre_input_type_docs_interstice2 = tk.Frame(cadre_input,bg=couleur_fond)
    cadre_input_type_docs_interstice2.pack(side="left")
    cadre_input_type_rec = tk.Frame(cadre_input,bg=couleur_fond)
    cadre_input_type_rec.pack(side="left")
    
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
    cadre_output_repertoire = tk.Frame(cadre_output,bg=couleur_fond)
    cadre_output_repertoire.pack(anchor="w")
    cadre_output_explications = tk.Frame(cadre_output, padx=20,bg=couleur_fond)
    cadre_output_explications.pack(anchor="w")

    cadre_output_message_en_cours = tk.Frame(cadre_output, padx=20,bg=couleur_fond)
    cadre_output_message_en_cours.pack(anchor="w")

    
    cadre_valider = tk.Frame(zone_ok_help_cancel, borderwidth=0, relief="groove", height=150, padx=10,bg=couleur_fond)
    cadre_valider.pack(side="left")
    
    #définition input URL (u)
    tk.Label(cadre_input_header,bg=couleur_fond, fg=couleur_bouton, text="En entrée :", justify="left", font="bold").pack(anchor="w")
    
    tk.Label(cadre_input_file_name,bg=couleur_fond, text="Fichier contenant les notices : ").pack(side="left")
    """entry_filename = tk.Entry(cadre_input_file, width=40, bd=2)
    entry_filename.pack(side="left")
    entry_filename.focus_set()"""
    main.download_zone(cadre_input_file, "Sélectionner un fichier\nde notices Marc",entry_file_list,couleur_fond,cadre_output_message_en_cours)
    
    #tk.Button(cadre_input_file_browse, text="Sélectionner le fichier\ncontenant les notices", command=lambda:main.openfile(cadre_input_file_name, popup_filename), width=20).pack()
    
    
    """tk.Label(cadre_input_infos_format,bg=couleur_fond, text="Format MARC", 
             anchor="w", justify="left").pack(anchor="w")
    marc_format = tk.IntVar()

    bib2ark.radioButton_lienExample(cadre_input_infos_format,marc_format,1,couleur_fond,
                            "Unimarc",
                            "",
                            "")

    tk.Radiobutton(cadre_input_infos_format,bg=couleur_fond, text="Marc21", variable=marc_format, value=2,
                   anchor="w", justify="left").pack(anchor="w")
    marc_format.set(1)"""
    
    tk.Label(cadre_input_type_docs_interstice1, bg=couleur_fond, text="\t\t", justify="left").pack()
    
    
    tk.Label(cadre_input_type_docs,bg=couleur_fond, text="Format de fichier", 
             anchor="w", justify="left").pack(anchor="w")
    file_format = tk.IntVar()

    bib2ark.radioButton_lienExample(cadre_input_type_docs,file_format,1,couleur_fond,
                            "iso2709",
                            "",
                            "https://github.com/Transition-bibliographique/alignements-donnees-bnf/blob/master/examples/noticesbib.iso")

    tk.Radiobutton(cadre_input_type_docs,bg=couleur_fond, text="Marc XML", variable=file_format, value=2,
                   anchor="w", justify="left").pack(anchor="w")
    file_format.set(1)
    
    tk.Label(cadre_input_type_docs_interstice2, bg=couleur_fond, text="\t\t", justify="left").pack()
    
    tk.Label(cadre_input_type_rec,bg=couleur_fond, text="\n\n\nType de notices", 
             anchor="w", justify="left").pack(anchor="w")
    rec_format = tk.IntVar()

    bib2ark.radioButton_lienExample(cadre_input_type_rec,rec_format,1,couleur_fond,
                            "bibliographiques",
                            "",
                            "")

    tk.Radiobutton(cadre_input_type_rec,bg=couleur_fond, text="autorités (personnes)", variable=rec_format, value=2,
                   anchor="w", justify="left").pack(anchor="w")
    rec_format.set(1)
    
    tk.Label(cadre_input_type_rec, text="\n\n", bg=couleur_fond).pack()
    
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

    #Sélection du répertoire en sortie
    #tk.Label(cadre_output_repertoire,text="\n",bg=couleur_fond).pack()
    #main.select_directory(cadre_output_repertoire, "Dossier où déposer les fichiers",output_directory_list,couleur_fond)
    

    
    #Ajout (optionnel) d'un identifiant de traitement
    message_fichiers_en_sortie = """
  Le programme va générer plusieurs fichiers, par type de document,
  en fonction du processus d'alignement avec les données de la BnF
  et des métadonnées utilisées pour cela :
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
    
    b = tk.Button(cadre_valider, bg=couleur_bouton, fg="white", font="bold", text = "OK", 
                  command=lambda:launch(form, entry_file_list[0], file_format.get(), rec_format.get(), output_ID.get(),master), 
                  borderwidth=5 ,padx=10, pady=10, width=10, height=4)
    b.pack()
    
    tk.Label(cadre_valider, font="bold", text="", bg=couleur_fond).pack()
    
    call4help = tk.Button(cadre_valider, text="Besoin d'aide ?", command=lambda: main.click2help("https://github.com/Transition-bibliographique/alignements-donnees-bnf/"), padx=10, pady=1, width=15)
    call4help.pack()
    
    cancel = tk.Button(cadre_valider, bg=couleur_fond, text="Annuler", command=lambda: main.annuler(form), padx=10, pady=1, width=15)
    cancel.pack()
    
    tk.Label(zone_notes, text = "Version " + str(main.version) + " - " + lastupdate, bg=couleur_fond).pack()
    
    """if (main.last_version[1] == True):
        download_update = tk.Button(zone_notes, text = "Télécharger la version " + str(main.last_version[0]), command=download_last_update)
        download_update.pack()"""

    tk.mainloop()

if __name__ == '__main__':
    access_to_network = main.check_access_to_network()
    #if(access_to_network is True):
    #    last_version = main.check_last_compilation(programID)
    main.formulaire_main(access_to_network, last_version)
    #formulaire_marc2tables(access_to_network,last_version)

