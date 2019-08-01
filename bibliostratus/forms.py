# coding: utf-8
"""
@author: Lully

Gestion des objets pour les formulaires

"""

import tkinter as tk
import tkinter.ttk as ttk


import ark2records


dict_formats_file = {1: "iso2709",
                     2: "XML",
                     3: "Certaines zones (sép : \";\")\n - fichier tabulé"}

liste_encoding = ["utf-8", "iso-5426", "iso-8859-1"]

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
        if title:
            tk.Label(frame, text=title, **title_options).pack(**title_pack)
        for val in dict_values:
            tk.Radiobutton(frame, variable=var,
                           text=dict_values[val], value=val,
                           **list_values_options).pack(**list_values_pack)
        var.set(1)

class Combobox:
    def __init__(self, frame, title, val, params):
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
        if title:
            tk.Label(frame, text=title, **title_options).pack(**title_pack)
        self.options = ttk.Combobox(frame, 
                                    values=val,
                                    **list_values_options)
        self.options.pack(**list_values_pack)
        self.options.set(val[0])


class FormOption:
    """
    Génère les options du formulaire selon leur type
    """
    def __init__(self, frame, var, type, title, values, params):  # Option de formulaire
        if type == "radioButton":
            RadioList(frame, var, title, values, params)

        if type == "Combobox":
            Combobox(frame, title, values, params)

form_ark2records_global = {"couleur_fond" : "#ffffff",
                           "couleur_bouton": "#99182D"}

form_ark2records = {"frame_output_options_format":
                    {  # Variable Type de fichier en sortie
                     "format_file":
                            {"title": "Format du fichier :",
                            "type": "radioButton",
                            "values": dict_formats_file,
                            "params" : {"title": {"options": {"bg": form_ark2records_global["couleur_fond"]},
                                                "pack": {"anchor": "nw"}},
                                        "values": {"options": {"bg": form_ark2records_global["couleur_fond"],
                                                            "justify": "left"},
                                                "pack": {"anchor": "nw"}}
                                        }
                            },
                      "xml_encoding_option":
                            {"title": "Si XML :",
                             "type": "Combobox",
                             "values": liste_encoding,
                             "params": {"title": {"options": {"bg": form_ark2records_global["couleur_fond"]},
                                                "pack": {"anchor": "nw"}},
                                        "values": {"pack": {"anchor": "nw"}}
                                        }}
                    }
                   }
                   
