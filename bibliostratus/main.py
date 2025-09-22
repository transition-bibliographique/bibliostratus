# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 18:30:30 2017

@author: Etienne Cavalié

Programme de manipulations de données liées à la Transition bibliographique pour
les bibliothèques françaises

"""

import codecs
import os
import json
import re
#from pkg_resources import py2_warn
import tkinter as tk
import webbrowser
from tkinter import filedialog
from urllib import error, request

from udecode import udecode

import __init__ as init

NUM_PARALLEL = 20

import ark2records
import funcs
import marc2tables
import aut2id
import bib2id
import forms
import edit_preferences as settings

from multiprocessing import freeze_support

version = init.version
version_suffix = ["", f".RC{init.version_suffix}"][len(init.version_suffix) > 0]  # Si init.version_suffix est renseigné, on l'ajoute au numéro de version avec mention ".RC"
lastupdate = init.lastupdate
programID = init.programID

# Ajout du fichier preferences.json
def load_preferences():
    current_dir = os.path.abspath(__file__)
    if "/" in current_dir:
        current_dir = "/".join(current_dir.split("/")[:-1])
    elif "\\" in current_dir:
        current_dir = "\\".join(current_dir.split("\\")[:-1])
    prefs_file_name = os.path.join(current_dir, 'main/files/preferences.json')
    try:
        with open(prefs_file_name, encoding="utf-8") as prefs_file:
            prefs = json.load(prefs_file)
    except FileNotFoundError:
        try:
            prefs_file_name = os.path.join(current_dir, 'main/files/preferences.default')
            with open(prefs_file_name, encoding="utf-8") as prefs_file:
                prefs = json.load(prefs_file)
        except FileNotFoundError:
            prefs = {}
    return prefs, prefs_file_name


prefs, prefs_file_name = load_preferences()



"""if "num_parallel" in prefs:
    NUM_PARALLEL = prefs["num_parallel"]["value"]"""



ns = {
    "srw": "http://www.loc.gov/zing/srw/",
    "mxc": "info:lc/xmlns/marcxchange-v2",
    "m": "http://catalogue.bnf.fr/namespaces/InterXMarc",
    "mn": "http://catalogue.bnf.fr/namespaces/motsnotices"
}
nsSudoc = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "bibo": "http://purl.org/ontology/bibo/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "rdafrbr1": "http://rdvocab.info/RDARelationshipsWEMI/",
    "marcrel": "http://id.loc.gov/vocabulary/relators/",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "gr": "http://purl.org/goodrelations/v1#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "isbd": "http://iflastandards.info/ns/isbd/elements/",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "rdafrbr2": "http://RDVocab.info/uri/schema/FRBRentitiesRDA/",
    "rdaelements": "http://rdvocab.info/Elements/",
    "rdac": "http://rdaregistry.info/Elements/c/",
    "rdau": "http://rdaregistry.info/Elements/u/",
    "rdaw": "http://rdaregistry.info/Elements/w/",
    "rdae": "http://rdaregistry.info/Elements/e/",
    "rdam": "http://rdaregistry.info/Elements/m/",
    "rdai": "http://rdaregistry.info/Elements/i/",
    "sudoc": "http://www.sudoc.fr/ns/",
    "bnf-onto": "http://data.bnf.fr/ontology/bnf-onto/"
}

ns_sruSudoc = {"srw": "http://www.loc.gov/zing/srw/", "dc": "http://purl.org/dc/elements/1.1/",}

nsisni = {
    'srw': 'http://www.loc.gov/zing/srw/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'diag': 'http://www.loc.gov/zing/srw/diagnostic/',
    'xcql': 'http://www.loc.gov/zing/cql/xcql/'
}
urlSRUroot = "https://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query="
urlAbesroot = "https://www.sudoc.abes.fr/cbs/sru/?"

url_online_help = "https://github.com/Transition-bibliographique/bibliostratus/wiki"
texte_bouton_help = "Documentation\nen ligne"



chiffers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
letters = [
    "a", "b", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p",
    "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"
]
punctuation = [
    ".", ",", ";", ":", "?", "!", "%", "$", "£", "€", "#", "\\", "\"", "&", "~",
    "{", "(", "[", "`", r"\\", "_", "@", ")", "]", "}", "=", "+", "*", r"/", "<",
    ">", ")", "}"
]

errors = {
    "no_internet":
        "Attention : Le programme n'a pas d'accès à Internet.\nSi votre navigateur y a accès, vérifiez les paramètres de votre proxy",  # noqa
    "nb_colonnes_incorrect":
        "Le fichier contient un nombre insuffisant de colonnes.\n\nVérifiez les options indiquées dans le formulaire ou le format du fichier en entrée",  # noqa
    "pb_input_utf8":
        "Erreur d'encodage constatée\n\nLe fichier en entrée doit être en UTF-8 sans BOM.",
    "pb_input_utf8_marcEdit":
        """Erreur d'encodage constatée :
        Le fichier en entrée doit être en UTF-8 sans BOM.

        Si vous utilisez un fichier iso2709, convertissez-le d'abord en XML avec MarcEdit""",
    "format_fichier_en_entree":
        """Erreur dans le traitement

Vérifier les options choisies\npour le format de fichier en entrée

Si l'erreur persiste, convertissez le fichier dans un autre format avec MarcEdit"""
}

output_directory = [""]

def click2url(url):
    webbrowser.open(url)


def annuler(master):
    if master is not None:
        master.destroy()

def select_output_directory_button():
    # Allow user to select a directory and store it in global var
    # called folder_path
    global output_directory
    directory_name = []
    directory_name[0] = filedialog.askdirectory()
    folder_path.set(directory_name[0])
    return directory_name


def proxy_opener():
    """
    Utilisation du proxy pour les requêtes HTTP/HTTPS
    """
    proxies = {}
    http_params = ["http_proxy", "https_proxy"]    
    for param in http_params:
        protocole = param.split("_")[0]
        proxies[protocole] = prefs[param]["URL"]
        if (prefs[param]["login"]
           and prefs[param]["mot de passe"]):
            urlroot = prefs[param]["URL"].replace('http://', '').replace('https://', '')
            proxies[protocole] = f'{prefs[param]["login"]}:{prefs[param]["mot de passe"]}@{urlroot}'
    proxy_handler = request.ProxyHandler(proxies)
    # construct a new opener using your proxy settings
    opener = request.build_opener(proxy_handler)
    # install the opener on the module-level
    request.install_opener(opener)


def check_last_compilation(programID):
    programID_last_compilation = 0
    display_update_button = False
    url = "https://raw.githubusercontent.com/Transition-bibliographique/bibliostratus/master/bibliostratus/last_compilations.json"  # noqa
    try:
        last_compilations = request.urlopen(url)
        reader = codecs.getreader("utf-8")
        last_compilations = json.load(reader(last_compilations))[
            "last_compilations"][0]
        if (programID in last_compilations):
            programID_last_compilation = last_compilations[programID]
        if (programID_last_compilation > version):
            display_update_button = True
    except error.URLError:
        print("Erreur réseau : échec pour la vérification des mises à jour")
    return [programID_last_compilation, display_update_button]


def download_last_update(
        url="https://github.com/Transition-bibliographique/bibliostratus/tree/master/bin"):
    webbrowser.open(url)


def display_headers_in_form(headers_list):
    """
    Génère l'affichage de la liste des en-têtes
    de colonne dans un formulaire, en gérant le retour à la ligne si besoin
    """
    splitter = 75
    line = " | ".join(headers_list)
    if (len(line) > splitter
       and "|" in line[splitter:]):
        line_begin, line_end = line[:splitter], line[splitter:]
        adjust, line_end = line_end[:line_end.find("|")], line_end[line_end.find("|")+1:].strip()
        line_begin = line_begin + adjust + "|"
        line = line_begin + "\n" + " "*45 + line_end
    line = f"(Colonnes : {line})"
    return line

def check_access_to_network():
    access_to_network = True
    try:
        test = request.urlopen("http://catalogue.bnf.fr/api").status
        if (test == 404):
            access_to_network = False
    except error.URLError:
        print("Pas de réseau internet")
        access_to_network = False
    return access_to_network



def check_access2apis(i, dict_report):
    """Vérification de la disponibilité du SRU BnF et des API Abes
    (en supposant que si une requête d'exemple fonctionne, tout fonctionne"""
    testBnF = True
    testAbes = True
    dict_report["testAbes"]["name"] = "API Abes"
    dict_report["testAbes"]["global"] = True
    dict_report["testBnF"]["name"] = "API BnF"
    dict_report["testBnF"]["global"] = True
    testBnF = funcs.testURLretrieve(
        "https://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query=bib.recordid%20all%20%2230000001%22&recordSchema=unimarcxchange&maximumRecords=20&startRecord=1")  # noqa
    testAbes = funcs.testURLretrieve(
        "https://www.sudoc.fr/services/isbn2ppn/0195141156")
    dict_report["testAbes"][i] = testAbes
    dict_report["testBnF"][i] = testBnF
    if testAbes is False:
        dict_report["testAbes"]["global"] = False
    if testBnF is False:
        dict_report["testBnF"]["global"] = False


def clean_string(string, replaceSpaces=False, replaceTirets=False):
    """
    Nettoyage d'une chaîne de caractères: accents, ponctuations, majuscules
    En option : 
        - suppression des espaces
        - suppression des tirets
    """
    string = udecode(string.lower())
    for sign in punctuation:
        string = string.replace(sign, " ")
    string = string.replace("'", " ")
    if replaceTirets:
        string = string.replace("-", " ")
    if replaceSpaces:
        string = string.replace(" ", "")
    string = ' '.join(s for s in string.split() if s != "")
    string = string.strip()
    return string


def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def field2subfield(field, subfield, nb_occ="all", sep="~"):
    path = "*[@code='" + subfield + "']"
    listeValues = []
    if (nb_occ == "first" or nb_occ == 1):
        if (field.find(path, namespaces=ns) is not None and
                field.find(path, namespaces=ns).text is not None):
            val = field.find(path, namespaces=ns).text
            listeValues.append(val)
    else:
        for occ in field.xpath(path, namespaces=ns):
            if (occ.text is not None):
                listeValues.append(occ.text)
    listeValues = sep.join(listeValues)
    return listeValues


def extract_leader(record, pos=None):
    path = './/*[local-name()="leader"]'
    leader_val = ""
    for leader in record.xpath(path):
        leader_val = leader.text
    if (pos is not None
       and RepresentsInt(pos)
       and len(leader_val)+2 > pos):
        return leader_val[pos]
    else:
        return leader_val


def extract_subfield(record, field, subfield, nb_occ="all", sep="~"):
    path = ".//*[@tag='" + field + \
        "']/*[@code='" + subfield + "']"
    listeValues = []
    if (nb_occ == "first" or nb_occ == 1):
        if (record.find(path, namespaces=ns) is not None and
                record.find(path, namespaces=ns).text is not None):
            val = record.find(path, namespaces=ns).text
            listeValues.append(val)
    else:
        for occ in record.xpath(path, namespaces=ns):
            if (occ.text is not None):
                listeValues.append(occ.text)
    listeValues = sep.join(listeValues)
    return listeValues


def form_saut_de_ligne(frame, couleur_fond="#ffffff", nb_sauts=1):
    tk.Label(frame, text="\n"*nb_sauts, bg=couleur_fond).pack()


def form_generic_frames(master, title, couleur_fond,
                        couleur_bordure, access_to_network):
    # ----------------------------------------------------
    # |                    Frame                         |
    # |            zone_alert_explications               |
    # ----------------------------------------------------
    # |                    Frame                         |
    # |             zone_access2programs                 |
    # |                                                  |
    # |              Frame           |       Frame       |
    # |           zone_actions       |  zone_help_cancel |
    # ----------------------------------------------------
    # |                    Frame                         |
    # |                  zone_notes                      |
    # ----------------------------------------------------
    # master = tk.Tk()
    form = tk.Toplevel(master)
    form.config(padx=10, pady=10, bg=couleur_fond)
    form.title(title)
    try:
        form.iconbitmap(r'main/files/favicon.ico')
    except tk.TclError:
        favicone = "rien"  # noqa

    zone_alert_explications = tk.Frame(form, bg=couleur_fond, pady=10)
    zone_alert_explications.pack()

    zone_access2programs = tk.Frame(form, bg=couleur_fond)
    zone_access2programs.pack()
    zone_actions = tk.Frame(zone_access2programs, bg=couleur_fond)
    zone_actions.pack(side="left")
    zone_ok_help_cancel = tk.Frame(zone_access2programs, bg=couleur_fond)
    zone_ok_help_cancel.pack(side="left")
    zone_notes = tk.Frame(form, bg=couleur_fond, pady=10)
    zone_notes.pack()

    if (access_to_network is False):
        tk.Label(zone_alert_explications, text=errors["no_internet"],
                 bg=couleur_fond, fg="red").pack()

    return [form,
            zone_alert_explications,
            zone_access2programs,
            zone_actions,
            zone_ok_help_cancel,
            zone_notes]


def main_form_frames(title, couleur_fond, couleur_bordure, access_to_network):
    # ----------------------------------------------------
    # |                    Frame                         |
    # |            zone_alert_explications               |
    # ----------------------------------------------------
    # |                    Frame                         |
    # |             zone_access2programs                 |
    # |                                                  |
    # |              Frame           |       Frame       |
    # |           zone_actions       |  zone_help_cancel |
    # ----------------------------------------------------
    # |                    Frame                         |
    # |                  zone_notes                      |
    # ----------------------------------------------------
    master = tk.Tk()
    master.config(padx=10, pady=10, bg=couleur_fond)
    master.title(title)
    try:
        master.iconbitmap(r'main/files/favicon.ico')
    except tk.TclError:
        favicone = "rien"  # noqa

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

    if (access_to_network is False):
        tk.Label(zone_alert_explications, text=errors["no_internet"],
                 bg=couleur_fond, fg="red").pack()

    return [master,
            zone_alert_explications,
            zone_access2programs,
            zone_actions,
            zone_ok_help_cancel,
            zone_notes]


def generic_input_controls(master, filename):
    check_file_name(master, filename)


def check_file_utf8(master, filename):
    try:
        open(filename, "r", encoding="utf-8")
    except FileNotFoundError:
        popup_errors(master, "Le fichier " + filename + " n'existe pas")
    except UnicodeDecodeError:
        popup_errors(master, errors["pb_input_utf8"])


def check_file_name(master, filename):
    if filename:
        try:
            open(filename, "r")
        except FileNotFoundError:
            popup_errors(master, "Le fichier " + filename + " n'existe pas")
    else:
        popup_errors(master, "Merci d'indiquer un nom de fichier en entrée")
        raise


def control_columns_number(master, row, headers_columns):
    """Vérifie le nombre de colonnes dans le fichier en entrée"""
    last_col = len(headers_columns) - 1
    test = True
    try:
        row[last_col]
    except IndexError as err:
        test = False
    try:
        assert test
    except AssertionError:
        i = 0
        message = ""
        for col in headers_columns:
            val = ""
            if (len(row) >= i + 1):
                val = row[i]
            message = message + col + " : " + val + "\n"
            i += 1
        message = errors["nb_colonnes_incorrect"] + \
            "\n\n\nFormat attendu - Ligne 1 :\n\n" + message
        popup_errors(master, message)
    return test


def popup_errors(master, text, online_help_text="", online_help_link=""):
    if master is not None:
        couleur_fond = "white"
        couleur_bordure = "red"
        [master,
        zone_alert_explications,
        zone_access2programs,
        zone_actions,
        zone_ok_help_cancel,
        zone_notes] = form_generic_frames(master, "Alerte", couleur_fond, couleur_bordure, True)
        tk.Label(zone_access2programs, text=text, fg=couleur_bordure,
                font="bold", bg=couleur_fond, padx=20, pady=20).pack()
        if (online_help_text != ""):
            help_button = tk.Button(zone_access2programs, bd=2, justify="left", font="Arial 10 italic",
                                    bg="#ffffff",
                                    padx=5, pady=5,
                                    text=online_help_text, command=lambda: click2url(online_help_link))
            help_button.pack()
        tk.Label(zone_access2programs, bg=couleur_fond, text="\n").pack()
        cancel = tk.Button(zone_access2programs, text="Fermer",
                        command=lambda: annuler(master), padx=10, pady=1, width=15)
        cancel.pack()
    else:
        print("\n".join([text, online_help_text, online_help_link]))


def openfile(frame, liste, background_color="white"):
    liste = []
    liste.append(filedialog.askopenfilename(title='Sélectionner un fichier'))
    filename_print = liste[0].split("/")[-1].split("\\")[-1]
    tk.Label(frame, text=filename_print, bg=background_color).pack()


def download_button(frame, text, frame_selected, text_path,
                    couleur_fond, file_entry_list, 
                    zone_message_en_cours="",
                    type_action="select_file"):
    global output_directory
    if (file_entry_list != []):
        text_path.delete(0.0, 1000.3)
    filename = filedialog.askopenfilename(
        parent=frame, title="Sélectionner un fichier")
    if (file_entry_list == []):
        file_entry_list.append(filename)
    else:
        file_entry_list[0] = filename
    text_path.insert(0.0, path_truncator(filename, 40))
    texte = """Après avoir lancé le traitement,
vous pourrez suivre sa progression sur le terminal (fenêtre écran noir).

Cette fenêtre se fermera automatiquement à la fin du programme"""
    if (zone_message_en_cours != ""):
        zone_message_en_cours.insert(0.0, texte)



def path_truncator(text, max_length):
    """
    Fonction qui restructure un texte (chemin vers un 
    fichier ou un répertoire) sur plusieurs lignes
    """
    if (len(text) > max_length):
        max_length = max_length-8
        return text[0:6] + "....." + text[-max_length:]
    else:
        return text


def download_zone(frame, text_bouton, file_entry_list,
                  couleur_fond, cadre_output_message_en_cours="",
                  type_action="select_file",
                  widthb=[50, 70]):
    frame_button = tk.Frame(frame)
    frame_button.pack()
    frame_selected = tk.Frame(frame)
    frame_selected.pack()
    display_selected = tk.Text(
        frame_selected, height=1, width=widthb[0],
        bg=couleur_fond, bd=0, font="Arial 9 bold")
    display_selected.pack()
    zone_message_en_cours = ""
    if (cadre_output_message_en_cours != ""):
        zone_message_en_cours = tk.Text(cadre_output_message_en_cours,
                                        height=5,
                                        width=widthb[1], fg="red",
                                        bg=couleur_fond, bd=0, 
                                        font="Arial 9 bold")
        zone_message_en_cours.pack()
    if (type_action == "askdirectory"):
        select_filename_button = tk.Button(
            frame_button,
            command=lambda:select_directory_button(
                                frame, text_bouton, 
                                frame_selected,
                                display_selected,
                                "#ffffff",
                                output_directory),
            text=text_bouton,
            padx=10,
            pady=10,
        )
    else:
        select_filename_button = tk.Button(
            frame_button,
            command=lambda: download_button(
                frame,
                text_bouton,
                frame_selected,
                display_selected,
                "#ffffff",
                file_entry_list,
                zone_message_en_cours,
                type_action
            ),
            text=text_bouton,
            padx=10,
            pady=10,
        )
    select_filename_button.pack()


def select_directory_button(
        frame, text, frame_selected, text_path, couleur_fond, directory_list):
    if (directory_list != []):
        text_path.delete(0.0, 1000.3)
    filename = filedialog.askdirectory(
        parent=frame, title="Sélectionner un dossier")
    #tk.folder_path.set(filename)
    if (directory_list == []):
        directory_list.append(filename)
    else:
        directory_list[0] = filename
    text_path.insert(0.0, path_truncator(filename, 40))



def message_programme_en_cours(
        master, access_to_network=True, couleur_fond="#ffffff"):
    texte = """Le programme est en cours d'exécution.
Vous pouvez suivre sa progression sur le terminal (écran noir).

Cette fenêtre se fermera toute seule à la fin du programme
et sa fermeture signifiera que le programme est arrivée à la fin du traitement"""
    # zone_message.insert(0.0,texte)
    couleur_bouton = "#efefef"
    [form,
     zone_alert_explications,
     zone_access2programs,
     zone_actions,
     zone_ok_help_cancel,
     zone_notes] = form_generic_frames(master, "Traitement en cours",
                                       couleur_fond, couleur_bouton,
                                       access_to_network)
    a = tk.Label(zone_alert_explications, text=texte)
    a.pack()
    # form.mainloop()
    return form


def formulaire_main(access_to_network, last_version):
    couleur_fond = "white"
    couleur_bouton = "#e1e1e1"

    [master,
     zone_alert_explications,
     zone_access2programs,
     zone_actions,
     zone_ok_help_cancel,
     zone_notes] = main_form_frames(
         "Bibliostratus : Stratégie d'alignement d'URIs pour la Transition bibliographique",
         couleur_fond,
         couleur_bouton, access_to_network)

    
    frame_left = tk.Frame(zone_actions, bg=couleur_fond, pady=0, padx=0)
    frame_left.pack(side="left", anchor="w")

    frame_logo = tk.Frame(frame_left, highlightbackground=couleur_fond,
                          highlightcolor=couleur_fond,
                          bg=couleur_fond, pady=0, padx=0)
    frame_logo.pack(anchor="center")

    logo = tk.PhotoImage(file="main/files/logo_bbs.png")
    logo = logo.zoom(50) #with 250, I ended up running out of memory
    logo = logo.subsample(50) #mechanically, here it is adjusted to 32 instead of 320
    zone_logo = tk.Label(frame_logo, image=logo, borderwidth=0)
    zone_logo.image = logo
    zone_logo.pack(anchor="center")

    frame1 = tk.Frame(frame_left, highlightthickness=2,
                      highlightbackground=couleur_bouton, bg=couleur_fond, pady=20, padx=20)
    frame1.pack()

    frame2 = tk.Frame(zone_actions, highlightthickness=0,
                      highlightbackground=couleur_bouton, bg=couleur_fond, pady=20, padx=5)
    frame2.pack(side="left", anchor="w")

    frame3 = tk.Frame(zone_actions, highlightthickness=2,
                      highlightbackground=couleur_bouton, bg=couleur_fond, pady=20, padx=20)
    frame3.pack(side="left")

    frame_help_cancel = tk.Frame(
        zone_ok_help_cancel, bg=couleur_fond, pady=10, padx=10)
    frame_help_cancel.pack()

    # =============================================================================
    #   Module blanc : aligner ses données bibliographiques ou AUT
    # =============================================================================
    tk.Label(frame1, text="Aligner des données bibliographiques",
             bg=couleur_fond, fg="#365B43", font="Arial 11 bold").pack(anchor="w")
    tk.Label(frame1, text="\n", font="Arial 2 bold", bg=couleur_fond).pack()

    bib2arkButton = tk.Button(
        frame1,
        text="Aligner ses données  BIB\n avec la BnF ou le Sudoc\nà partir de fichiers tableaux",
        command=lambda: bib2id.form_bib2id(
            master, access_to_network, [0, False]
        ),
        padx=40,
        pady=47,
        bg="#fefefe",
        font="Arial 9 bold",
    )
    bib2arkButton.pack()

    tk.Label(frame1, text="\n", bg=couleur_fond, font="Arial 3 normal").pack()

    aut2arkButton = tk.Button(
        frame1, text="Aligner ses données AUT ",
        command=lambda: aut2id.form_aut2id(master, access_to_network, [0, False]),
        padx=55, pady=25, bg="#fefefe", font="Arial 8 normal")
    aut2arkButton.pack()

    #tk.Label(frame1, text="\n\n", bg=couleur_fond).pack()

    tk.Label(frame2, text="\n\n", bg=couleur_fond).pack()
    # =============================================================================
    #     Module bleu : convertir un fichier MARC en tables
    # =============================================================================
    tk.Label(frame3, text="Outils d'accompagnement", bg=couleur_fond,
             fg="#365B43", font="Arial 11 bold").pack(anchor="w")
    tk.Label(frame3, text="\n", bg=couleur_fond, font="Arial 4 normal").pack()

    tk.Label(frame3, text="Avant alignement", bg=couleur_fond,
             fg="#2D4991", font="Arial 10 bold").pack(anchor="w")

    tk.Label(frame3, text="Préparer ses données",
             bg=couleur_fond, fg="#365B43", font="Arial 9 bold").pack(anchor="w")
    tk.Label(frame3, text="(constitution de tableaux\nà partir d'un export catalogue)",
             bg=couleur_fond, fg="#365B43", font="Arial 9 normal", justify="left").pack(anchor="w")

    marc2tableButton = tk.Button(frame3, text="Convertir un fichier Unimarc\n en tableaux",
                                 command=lambda: marc2tables.formulaire_marc2tables(
                                     master, access_to_network),
                                 padx=10, pady=10, bg="#2D4991", fg="white")
    marc2tableButton.pack()

    # ☺tk.Label(frame3,text="\n",bg=couleur_fond).pack()

    tk.Label(
        frame3,
        text="\n" + "-" * 50,
        bg=couleur_fond,
        fg="#a1a1a1").pack()
    # =============================================================================
    #    Module rouge : exporter des notices à partir d'une liste d'ARK
    # =============================================================================
    tk.Label(frame3, text="Après alignement", bg=couleur_fond,
             fg="#99182D", font="Arial 10 bold").pack(anchor="w")
    tk.Label(frame3, text="Exporter les notices après alignement",
             bg=couleur_fond, fg="#365B43", font="Arial 9 bold").pack(anchor="w")

    ark2recordsButton = tk.Button(frame3, text="Exporter des notices BnF / Abes\nà partir d'une liste d'identifiants\n(ARK / PPN)",
                                  command=lambda: ark2records.formulaire_ark2records(
                                      master, access_to_network, [0, False]),
                                  padx=10, pady=10, bg="#99182D", fg="white")
    ark2recordsButton.pack()

    forms.add_saut_de_ligne(frame3)

    tk.Label(zone_ok_help_cancel, text=" ", pady=5, bg=couleur_fond).pack()

    call4help = tk.Button(frame_help_cancel,
                          text=texte_bouton_help,
                          command=lambda: click2url(url_online_help),
                          pady=25, padx=5, width=12)
    call4help.pack()
    tk.Label(frame_help_cancel, text="\n",
             bg=couleur_fond, font="Arial 1 normal").pack()
    
    forum_button = forms.forum_button(frame_help_cancel)
    forum_button.pack()

    forms.add_saut_de_ligne(frame_help_cancel)
    cancel = tk.Button(frame_help_cancel, text="Annuler", bg=couleur_fond,
                       command=lambda: annuler(master), pady=45, padx=5, width=12)
    cancel.pack()

    tk.Label(frame_help_cancel, text="\n\nPréférences",
             bg=couleur_fond, font="Arial 8 normal").pack()
    edit_settings_img = tk.PhotoImage(file='main/files/settings.png')
    edit_settings_button = tk.Button(frame_help_cancel,
                                     image=edit_settings_img,
                                     command=lambda: settings.edit_preferences(
                                                                   master,
                                                                   prefs_file_name,
                                                                   access_to_network,
                                                                   last_version
                                                                  ),
                                     padx=0,
                                     pady=0,
                                     bg="white",
                                     font="Arial 9 bold",)
    edit_settings_button.pack()

    tk.Label(zone_notes, text="Bibliostratus - Version " +
             f"{str(version)}{version_suffix}" + " - " + lastupdate, bg=couleur_fond).pack()
    if "gmb" in prefs and prefs["gmb"]["value"] == "1":
        tk.Label(zone_notes, text="Option Gallica Marque Blanche", bg="#afafaf").pack()


    if last_version[1]:
        download_update = tk.Button(
            zone_notes,
            text="Télécharger la version " + str(last_version[0]),
            command=download_last_update
        )
        download_update.pack()
        url_release_notes = (
            "https://github.com/transition-bibliographique/bibliostratus/blob/master/release_notes.md#"  # noqa
            + "version-" + str(last_version[0]).replace(".", "")
        )
        release_notes = tk.Button(
            zone_notes,
            bg=couleur_fond,
            font="Arial 8 bold italic",
            border=0,
            text="Liste des nouveautés",
            command=lambda: download_last_update(url_release_notes)
        )
        release_notes.pack()

    tk.mainloop()

def check_proxy():
    if ("http_proxy" in prefs and prefs["http_proxy"]["URL"]) or ("https_proxy" in prefs and prefs["https_proxy"]["URL"]):
        proxy_opener()

if __name__ == '__main__':
    check_proxy()
    freeze_support()
    forms.default_launch()
