# coding: utf-8
"""
@author: Lully

Gestion des objets pour les formulaires

"""

import tkinter as tk
import tkinter.ttk as ttk
import os

import smc.bibencodings

import main
import aut2id
import ark2records
import funcs


url_forum_aide = "http://www.agorabib.fr/topic/3317-bibliostratus-mettre-en-correspondance-ses-notices-avec-celles-de-la-bnf/"  # noqa
texte_bouton_forum = "Forum\nutilisateurs"


dict_formats_file = {1: "iso2709",
                     2: "XML",
                     3: "Certaines zones (sép : \";\")\n - fichier tabulé"}

dict_format_records = {1: "Unimarc",
                       3: "Intermarc",
                       2: "[ARK BnF] Unimarc \navec notices analytiques",
                       4: "[ARK BnF] Intermarc \navec notices analytiques"}


ark2records_dict_type_records = {1:
                                {"line1": "N° de notices bibliographiques",
                                 "line2": "",
                                 "link": "main/examples/listeARKbib.tsv"
                                 },
                               2:
                                {"line1": "N° de notices d'autorités",
                                 "line2": "",
                                 "link": "main/examples/listeARKaut.tsv"
                                 }
                                }

ark2records_dict_correct_record_option = {1:
                                            {"line1": "Fichier d'1 colonne (1 ARK ou PPN par ligne)",
                                             "line2": "",
                                             "link": ""},
                                          2:
                                            {"line1": "Fichier à 2 colonnes (N° notice local | ARK ou PPN)",
                                             "line2": "pour réécrire les notices récupérées",
                                             "link": "main/examples/listeARKaut_2cols.tsv"},
                                             }

# liste_encoding = ["utf-8", "iso-5426", "iso-8859-1"]
liste_encoding = ["utf-8", "iso-8859-1"]

class RadioList:
    def __init__(self, frame, var, title, dict_values, params):  # Notre méthode constructeur
        """
        params est un dictionnaire doit contenir au moins 2 dictionnaires:
        params["title"]["options"]
        params["title"]["pack"]
        params["list_values"]["options"]
        params["list_values"]["pack"]
        exemple : 
        params = {"title":
                    {"options": {"bg": "#ffffff"}},
                    {"pack": {"anchor": "nw"}}},
                  "list_values":
                    {"options": {"bg": "white"},
                     "pack": "side": "left"}
                  }

        """
        [title_options, title_pack,
         list_values_options, list_values_pack] = form_options(params)
        if title:
            tk.Label(frame, text=title, **title_options).pack(**title_pack)
        for val in dict_values:
            if ("link" in dict_values[val]):
                couleur_fond = None
                if "bg" in list_values_options:
                    couleur_fond = list_values_options["bg"]
                radioButton_lienExample(frame, var, val,
                                        couleur_fond,
                                        dict_values[val]["line1"],
                                        dict_values[val]["line2"],
                                        dict_values[val]["link"])
            else:
                tk.Radiobutton(frame, variable=var,
                               text=dict_values[val], value=val,
                               **list_values_options).pack(**list_values_pack)
        var.set(1)

def form_options(params):
    title_options = {}
    title_pack = {}
    list_values_options = {}
    list_values_pack = {}
    if "title" in params:
        if "options" in params["title"]:
            title_options = params["title"]["options"]
        if "pack" in params["title"]:
            title_pack = params["title"]["pack"]
    if "values" in params:
        if "options" in params["values"]:
            list_values_options = params["values"]["options"]
        if "pack" in params["values"]:
            list_values_pack = params["values"]["pack"]
    return title_options, title_pack, list_values_options, list_values_pack

class CheckButton:
    def __init__(self, frame, title, var, line, params):
        [title_options, title_pack,
         list_values_options, list_values_pack] = form_options(params)
        if title:
            tk.Label(frame, text=title, **title_options).pack(**title_pack)
        tk.Checkbutton(frame, text=line, variable=var,
                       **list_values_options).pack(**list_values_pack)


def radioButton_lienExample(
    frame, variable_button, val, couleur_fond, text1, text2, link
):
    packButton = tk.Frame(frame, bg=couleur_fond)
    packButton.pack(anchor="w")
    line1 = tk.Frame(packButton, bg=couleur_fond)
    line1.pack(anchor="w")
    tk.Radiobutton(
        line1,
        bg=couleur_fond,
        text=text1,
        variable=variable_button,
        value=val,
        justify="left",
    ).pack(anchor="w", side="left")
    if link != "":
        tk.Label(line1, text="  ", bg=couleur_fond).pack(anchor="w", side="left")
        if "http" in link:
            example_ico = tk.Button(
                line1,
                bd=0,
                justify="left",
                font="Arial 7 underline",
                text="exemple",
                fg="#0000ff",
                bg=couleur_fond,
                command=lambda: main.click2url(link),
            )
        else:
            link = os.path.join(os.path.dirname(__file__), link)
            example_ico = tk.Button(
                line1,
                bd=0,
                justify="left",
                font="Arial 7 underline",
                text="exemple",
                fg="#0000ff",
                bg=couleur_fond,
                command=lambda: funcs.open_local_file(link),
            )
        example_ico.pack(anchor="w", side="left")
    if text2 != "":
        line2 = tk.Frame(packButton, bg=couleur_fond)
        line2.pack(anchor="w")
        tk.Label(line2, bg=couleur_fond, text="      " + text2, justify="left").pack(
            anchor="w"
        )


def forum_button(frame):
    button = tk.Button(frame, text=texte_bouton_forum,
              command=lambda: main.click2url(url_forum_aide),
              pady=5, padx=5, width=12)
    return button

class Combobox:
    def __init__(self, frame, title, val, params):
        [title_options, title_pack,
         list_values_options, list_values_pack] = form_options(params)
        if title:
            tk.Label(frame, text=title, **title_options).pack(**title_pack)
        self.options = ttk.Combobox(frame, 
                                    values=val,
                                    **list_values_options)
        self.options.pack(**list_values_pack)
        self.options.set(val[0])


class Entry:
    def __init__(self, frame, title, params):
        title_options = {}
        title_pack = {}
        value_options = {}
        value_pack = {}
        if "title" in params:
            if "options" in params["title"]:
                title_options = params["title"]["options"]
            if "pack" in params["title"]:
                title_pack = params["title"]["pack"]
        if "values" in params:
            if "options" in params["values"]:
                value_options = params["values"]["options"]
            if "pack" in params["values"]:
                value_pack = params["values"]["pack"]
        if title:
            tk.Label(frame, text=title, **title_options).pack(**title_pack)
        self.value = tk.Entry(frame, **value_options)
        self.value.pack(**value_pack)


class FormOption:
    """
    Génère les options du formulaire selon leur type
    """
    def __init__(self, frame, var, type, title, values, params):  # Option de formulaire
        if type == "radioButton":
            RadioList(frame, var, title, values, params)
        elif type == "checkButton":
            CheckButton(frame, title, var, values, params)
        elif type == "Combobox":
            Combobox(frame, title, values, params)




def footer(frame, couleur_fond):
    """
    génère le pied de page dans les formulaires
    """
    tk.Label(frame, text="Bibliostratus - Version " +
             str(main.version) + " - " + main.lastupdate, bg=couleur_fond).pack()


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


def display_options(frame2var, dict_params):
    """
    En entrée, un dictionnaire indiquant
    le nom des frames et les variables qu'il contient
    """
    for frame in frame2var:
        frame_name = frame["name"]
        for variable in frame["variables"]:
            variable_name = variable[0]
            params = dict_params[frame_name][variable_name]
            FormOption(frame["frame"],
                       variable[1],
                       params["type"],
                       params["title"],
                       params["values"],
                       params["params"]
                       )


def add_saut_de_ligne(frame, nb_sauts=1, couleur_fond="#ffffff"):
    tk.Label(frame, text="\n"*nb_sauts, bg=couleur_fond).pack()


def default_launch():
    access_to_network = main.check_access_to_network()
    last_version = [0, False]
    if(access_to_network is True):
        last_version = main.check_last_compilation(main.programID)
    main.formulaire_main(access_to_network, last_version)


form_ark2records_global = {"couleur_fond" : "#ffffff",
                           "couleur_bouton": "#99182D"}


form_ark_records_radio_default = {"title": {"options": {"bg": form_ark2records_global["couleur_fond"],
                                                        "font": "Arial 10 bold"},
                                                "pack": {"anchor": "nw"}},
                                        "values": {"options": {"bg": form_ark2records_global["couleur_fond"],
                                                            "justify": "left"},
                                                "pack": {"anchor": "nw"}}
                                 }
form_ark_records_entry_default = {"title": {"options": {"bg": form_ark2records_global["couleur_fond"],
                                                        "font": "Arial 10 bold"},
                                             "pack": {"anchor": "nw"}},
                                  "values": {"options": {"bg": form_ark2records_global["couleur_fond"],
                                                            "justify": "left"},
                                              "pack": {"anchor": "w", "side": "left"}}
                                 }
form_ark_records_checkbox_default = {"title": {"options": {"bg": form_ark2records_global["couleur_fond"],
                                                        "font": "Arial 10 bold"},
                                             "pack": {"anchor": "nw"}},
                                     "values": {"options": {"bg": form_ark2records_global["couleur_fond"],
                                                            "justify": "left"},
                                                "pack": {}
                                                }
                                    }     

form_ark_records_checkbox_inline_default = form_ark_records_checkbox_default
form_ark_records_checkbox_inline_default["values"]["pack"] = {"side": "left",
                                                              "anchor": "w"}
form_option_pack_default = {"title": {"options": {"bg": form_ark2records_global["couleur_fond"],
                                                  "font": "Arial 10 bold"},
                                      "pack": {"anchor": "nw"}},
                            "values": {"options": {"bg": form_ark2records_global["couleur_fond"],
                                                   "justify": "left"},
                                       "pack": {"anchor": "nw"}
                                      }
                            }     

form_ark2records = {"frame_input_aut_file":
                    {
                        "correct_record_option":
                            {"title": "-"*30,
                             "type": "radioButton",
                             "values": ark2records_dict_correct_record_option,
                             "params": form_ark_records_radio_default},
                        "type_records":
                            {"title": "-"*30,
                             "type": "radioButton",
                             "values": ark2records_dict_type_records,
                             "params": form_ark_records_radio_default}},
                    "frame_input_aut_headers":
                    {
                        "headers":
                            {"title": "-"*30,
                             "type": "checkButton",
                             "values": "Mon fichier a des en-têtes de colonne",
                             "params": form_ark_records_checkbox_default,
                             "default": 1}},
                    "frame_input_aut_liees":
                    {
                        "AUTlieesAUT":
                            {"title": "\nRécupérer aussi les notices d'autorité liées",
                             "type": "checkButton",
                             "values": "auteurs",
                             "params": form_ark_records_checkbox_inline_default,
                             "default": 1},
                        "AUTlieesSUB":
                            {"title": "",
                             "type": "checkButton",
                             "values": "sujets",
                             "params": form_ark_records_checkbox_inline_default,
                             "default": 1},
                        "AUTlieesWORK":
                            {"title": "",
                             "type": "checkButton",
                             "values": "oeuvres",
                             "params": form_ark_records_checkbox_inline_default,
                             "default": 1}
                             
                        
                    },
                    "frame_output_options_format":
                    {  # Variable Type de fichier en sortie
                     "format_file":
                            {"title": "Format du fichier :",
                             "type": "radioButton",
                             "values": dict_formats_file,
                             "params" : form_ark_records_radio_default
                            }
                    },
                    "frame_output_options_si_xml":
                        {
                        "xml_encoding_option":
                                {"title": "\n\nSi XML, encodage :",
                                "type": "Combobox",
                                "values": liste_encoding,
                                "params": {"title": {"options": {"bg": form_ark2records_global["couleur_fond"],
                                                     "font": "Arial 10 bold"},
                                                    "pack": {"anchor": "nw"}},
                                            "values": {"pack": {"anchor": "nw"}}
                                        }
                                },
                        "select_fields":
                                {"title": "Si tabulé : zones à récupérer",
                                "type": "Entry",
                                "params": form_ark_records_entry_default
                            }
                     },
                    "frame_output_options_marc":
                    {
                      "format_records_choice":
                            {"title": "Notices à récupérer en :",
                            "type": "radioButton",
                            "values": dict_format_records,
                            "params" : form_ark_records_radio_default
                            }
                    },
                    "frame_outputID":
                    {
                        "outputID":
                            {"title": "Préfixe fichier(s) en sortie",
                             "type": "Entry",
                             "params": form_ark_records_entry_default
                            }
                    }
                   }
                   

header_columns_init_aut2aut = [
    'N° Notice AUT', 'FRBNF', 'ARK', 'ISNI', 'Nom', 'Prénom',
    'Date de début', 'Date de fin'
]
header_columns_init_bib2aut = [
    "N° Notice AUT", "N° notice BIB", "ARK Bib", "FRBNF Bib", "ISBN/EAN", "Titre",
    "Date de publication", "ISNI", "Nom", "Prénom", "Dates auteur"
]

header_columns_init_rameau = [
    'N° Notice AUT', 'FRBNF', 'ARK', 'Point d\'accès Rameau'
]

aut2id_input_data_type = {1:
                            {"line1": "[PERS] Liste de notices Personnes",
                             "line2": display_headers_in_form(header_columns_init_aut2aut),
                             "link": "main/examples/aut_align_aut.tsv"
                                 },
                          2:
                            {"line1": "[ORG] Liste de notices Organisations",
                             "line2": display_headers_in_form(header_columns_init_aut2aut),
                             "link": ""},
                          3:
                            {"line1": "Liste de notices bibliographiques",
                             "line2": display_headers_in_form(header_columns_init_bib2aut),
                             "link": "main/examples/aut_align_bib.tsv"},
                          4:
                            {"line1": "Liste de notices Rameau",
                             "line2": display_headers_in_form(header_columns_init_rameau),
                             "link": ""}}

aut2id_input_preferences_alignement = {1: "Avec la BnF (et à défaut avec IdRef)",
                                       2: "Avec IdRef (et à défaut avec la BnF)"}

output_nb_files = {1: "1 fichier",
                          2: "Plusieurs fichiers \n(Pb / 0 / 1 / plusieurs ARK trouvés)"}

form_aut2id = {"frame_input_aut_headers":
                    {
                        "headers":
                            {"title": "",
                             "type": "checkButton",
                             "values": "Mon fichier a des en-têtes de colonne",
                             "params": form_ark_records_checkbox_default,
                             "default": 1},
                    },
                "frame_input_aut_input_data_type":
                    {"input_data_type":
                            {"title": "Type de données en entrée",
                             "type": "radioButton",
                             "values": aut2id_input_data_type,
                             "params": form_ark_records_checkbox_default,
                             "default": 1}
                    },
                "frame_input_aut_preferences":
                    {"preferences_alignement":
                            {"title": "\nAligner de préférence :",
                             "type": "radioButton",
                             "values": aut2id_input_preferences_alignement,
                             "params": form_option_pack_default,
                             "default": 1},
                     "isni_option":
                            {"title": "",
                            "type": "checkButton",
                            "values": "Relancer sur isni.org en cas d'absence de réponse",
                            "params": form_ark_records_checkbox_default,
                            "default": 1}},
                "frame_output_file":
                    {"file_nb":
                        {"title": "Nombre de fichiers en sortie",
                         "type": "radioButton",
                         "values": output_nb_files,
                         "params": form_option_pack_default,
                        },
                     "meta_bnf":
                        {"title": "\n",
                         "type": "checkButton",
                         "values": "Récupérer les métadonnées simples",
                         "params": form_option_pack_default,
                         "default": 0},
                    "outputID":
                        {"title": "\nPréfixe des fichiers en sortie",
                         "type": "Entry",
                         "params": form_option_pack_default
                        }
                    }
              }


header_columns_init_monimpr = [
    "Num Not",
    "FRBNF",
    "ARK",
    "ISBN",
    "EAN",
    "Titre",
    "Auteur",
    "Date",
    "Volume-Tome",
    "Editeur",
]
header_columns_init_cddvd = [
    "Num Not",
    "FRBNF",
    "ARK",
    "EAN",
    "N° commercial",
    "Titre",
    "Auteur",
    "Date",
    "Editeur",
]
header_columns_init_perimpr = [
    "Num Not",
    "FRBNF",
    "ARK",
    "ISSN",
    "Titre",
    "Auteur",
    "Date",
    "Lieu de publication",
]

header_columns_init_cartes = [
    "Num Not",
    "FRBNF",
    "ARK",
    "ISBN",
    "EAN",
    "Titre",
    "Auteur",
    "Date",
    "Editeur",
    "Echelle"
]

header_columns_init_partitions = [
    "Num Not",
    "FRBNF",
    "ARK",
    "EAN",
    "Référence commerciale",  #023$a en Intermarc, 071$a en Unimarc
    "Titre",
    "Titre de partie",
    "Auteur",
    "Date",
    "Editeur",
]


bib2id_type_doc_bib = {1:
                            {"line1": "[TEX] Monographies texte",
                             "line2": display_headers_in_form(header_columns_init_monimpr),
                             "link": "main/examples/mon_impr.tsv"
                                 },
                          2:
                            {"line1": "[VID] Audiovisuel (DVD)",
                             "line2": display_headers_in_form(header_columns_init_cddvd),
                             "link": ""},
                          3:
                            {"line1": "[AUD] Enregistrements sonores",
                             "line2": display_headers_in_form(header_columns_init_cddvd),
                             "link": "main/examples/audio.tsv"},
                          4:
                            {"line1": "[PER] Périodiques",
                             "line2": display_headers_in_form(header_columns_init_perimpr),
                             "link": "main/examples/per.tsv"},
                          5:
                            {"line1": "[CAR] Cartes",
                             "line2": display_headers_in_form(header_columns_init_cartes),
                             "link": ""},
                          6:
                            {"line1": "[PAR] Partitions",
                             "line2": display_headers_in_form(header_columns_init_partitions),
                             "link": ""},                              
                             }

bib2id_input_preferences_alignement = {1: "Avec la BnF (et à défaut avec le Sudoc)",
                                       2: "Avec le Sudoc (et à défaut avec la BnF)"}


form_bib2id = {"cadre_input_type_docs_zone":
                    {
                        "type_doc_bib":
                            {"title": "Type de documents",
                             "type": "radioButton",
                             "values": bib2id_type_doc_bib,
                             "params": form_option_pack_default,
                             "default": 1},
                    },
                "cadre_input_type_docs":
                    {
                            "preferences_alignement":
                                {"title": "Aligner de préférence :",
                                 "type": "radioButton",
                                 "values": bib2id_input_preferences_alignement,
                                 "params": form_option_pack_default},
                            "kwsudoc_option":
                                {"title": "",
                                 "type": "checkButton",
                                 "values": "+ Utiliser aussi la recherche par mots-clés dans le Sudoc \
(peut ralentir le programme) ",
                                 "params": form_option_pack_default,
                                 "default": 1}
                    },
                "cadre_output_nb_fichiers_zone":
                    {
                            "file_nb":
                                {"title": "Nombre de fichiers en sortie",
                                 "type": "radioButton",
                                 "values": output_nb_files,
                                 "params": form_option_pack_default,
                                 "default": 1},
                            "meta_bib":
                                {"title": "\n",
                                 "type": "checkButton",
                                 "values": "Récupérer les métadonnées simples",
                                 "params": form_option_pack_default,
                                 "default": 0}},
                "frame_outputID":
                    {
                            "outputID":
                                {"title": "\nPréfixe des fichiers en sortie",
                                 "type": "Entry",
                                 "params": form_option_pack_default
                                }
                    }
                }

marc2tables_file_format = {1:
                            {"line1": "iso2709 encodé UTF-8",
                             "line2": "",
                             "link": "main/examples/noticesbib.iso"},
                           2:
                            {"line1": "iso2709 encodé ISO-8859-1",
                             "line2": "",
                             "link": ""},
                           3:
                            {"line1": "Marc XML encodé UTF-8",
                             "line2": "",
                             "link": ""}}


marc2tables_rec_format = {1: "bibliographiques",
                          2: "autorités",
                          3: "bibliographiques pour alignement d'autorités"}

form_marc2tables = {"frame_input_type_docs":
                    
                      {"file_format":
                            {"title": "Format de fichier",
                             "type": "radioButton",
                             "values": marc2tables_file_format,
                             "params": form_option_pack_default,
                             "default": 1}},
                    "frame_input_type_rec":
                        {"rec_format":
                            {"title": "\nType de notices",
                             "type": "radioButton",
                             "values": marc2tables_rec_format,
                             "params": form_option_pack_default,
                             "default": 1}},
                    "frame_outputID":
                    {
                            "outputID":
                                {"title": "\nPréfixe des fichiers en sortie",
                                 "type": "Entry",
                                 "params": form_option_pack_default
                                }
                    }
                   }
