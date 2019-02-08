# coding: utf-8

"""
Edition du fichier de préférences
"""
import os
import json
import tkinter as tk

import main

def edit_preferences(master_frame, prefs_file_name, access_to_network, last_version):
    couleur_fond = "white"
    couleur_bouton = "#5F7C88"
    [form,
     zone_alert_explications,
     zone_access2programs,
     zone_actions,
     zone_ok_help_cancel,
     zone_notes] = main.form_generic_frames(master_frame,
                                            "Editer les préférences",
                                            couleur_fond, couleur_bouton,
                                            True)
    zone_alert_explications.pack(anchor="w")
    tk.Label(zone_alert_explications, text="Editer les préférences\n",
             font="Arial 12 bold", fg=couleur_bouton, bg=couleur_fond).pack(side="left")

    liste_frame = tk.Frame(zone_actions, bg=couleur_fond)
    liste_frame.pack()
    footer = tk.Frame(zone_notes, bg=couleur_fond)
    prefs = {}
    dic_frames = {}
    i = 0
    with open(prefs_file_name, "r", encoding="utf-8") as prefs_file:
        prefs = json.load(prefs_file)
    for pref in prefs:
        pref_frame = tk.Frame(liste_frame, bg=couleur_fond)
        pref_frame.pack(anchor="w")
        dic_frames[i] = {}
        dic_frames[i]["name"] = pref
        dic_frames[i]["description"] = prefs[pref]["description"]
        dic_frames[i]['frame'] = pref_frame
        i += 1
    i = 0

    for pref in prefs:
        dic_frames[i]["value"] = pref2fields(dic_frames[i]["frame"], pref, prefs, couleur_fond, couleur_bouton)
        i += 1
    save = tk.Button(zone_notes, bg=couleur_bouton, fg="white", text="Enregistrer mes préférences",
                     pady=10, padx=10, font="Arial 10 bold",
                     command=lambda: save_preferences(dic_frames, prefs_file_name, form))
    save.pack(side="left")
    tk.Label(zone_notes, bg=couleur_fond, text=" "*30).pack(side="left")
    reset_default = tk.Button(zone_notes, text="Restaurer les paramètres par défaut",
                              pady=12,
                              command=lambda: reset(prefs_file_name, form))
    reset_default.pack(side="left")
    tk.mainloop()

def reset(prefs_file_name, form):
    try:
        os.remove("main/files/preferences.json")
    except FileNotFoundError:
        pass
    form.destroy()

def save_preferences(dic_frames, prefs_file_name, form):
    """
    Enregistrement des nouvelles valeurs dans le fichier des préférences
    """
    prefs_file_name = "main/files/preferences.json"
    i = 0
    with open(prefs_file_name, "w", encoding="utf-8") as prefs_file:
        prefs_file.write("{\n")
        for pref in dic_frames:
            try:
                dic_frames[pref]["value"] = int(dic_frames[pref]["value"].get())
            except ValueError:
                dic_frames[pref]["value"] = dic_frames[pref]["value"].get()
            except AttributeError:
                pass
            i += 1
            text = f'    "{dic_frames[pref]["name"]}": ' + "{\n"
            text += f'{" "*8}"description": "{dic_frames[pref]["description"]}",\n'
            if ("proxy" in dic_frames[pref]["name"]):
                text += f'{" "*8}"URL": "{dic_frames[pref]["value"][0].get()}",\n'
                text += f'{" "*8}"login": "{dic_frames[pref]["value"][1].get()}",\n'
                text += f'{" "*8}"mot de passe": "{dic_frames[pref]["value"][2].get()}"\n'
            elif ("value" in dic_frames[pref]
                  and type(dic_frames[pref]["value"]) is int):
                text += f'{" "*8}"value": {dic_frames[pref]["value"]}\n'
            else:
                text += f'{" "*8}"value": "{dic_frames[pref]["value"]}"\n'
            text += '        }'
            if (i < len(dic_frames)):
                text += ",\n"
            prefs_file.write(text)
        prefs_file.write("}")
    main.check_proxy()
    form.destroy()

def pref2fields(frame_pref, preference_name, prefs,
                couleur_fond, couleur_bouton):
    """
    Pour chaque variable du fichier de préférences, ajout d'une ligne
    dans le formulaire d'édition
    """
    label = preference_name + " "*(35-len(preference_name))
    tk.Label(frame_pref, bg=couleur_fond,
             text=label, fg=couleur_bouton,
             justify="left",
             font="Arial 9 bold").pack(side="left",
                                       anchor="n")
    tk.Message(frame_pref, bg=couleur_fond,
               text=prefs[preference_name]["description"],
               justify="left", padx=30,
               width=300).pack(side="left", anchor="n")
    if ("proxy" in preference_name):
        tk.Label(frame_pref, bg=couleur_fond,
             text="URL",
             justify="left",
             font="Arial 9 bold").pack(side="left",
                                       anchor="n")
        urlroot = tk.Entry(frame_pref, bg=couleur_fond,
                        justify="left")
        urlroot.pack(side="left", anchor="n")
        urlroot.insert(0, str(prefs[preference_name]["URL"]))

        tk.Label(frame_pref, bg=couleur_fond,
             text="login",
             justify="left",
             font="Arial 9 bold").pack(side="left",
                                       anchor="n")
        login = tk.Entry(frame_pref, bg=couleur_fond,
                        justify="left")
        login.pack(side="left", anchor="n")
        login.insert(0, str(prefs[preference_name]["login"]))

        tk.Label(frame_pref, bg=couleur_fond,
             text="Mot de passe",
             justify="left",
             font="Arial 9 bold").pack(side="left",
                                       anchor="n")
        password = tk.Entry(frame_pref, bg=couleur_fond,
                        justify="left")
        password.pack(side="left", anchor="n")
        password.insert(0, str(prefs[preference_name]["mot de passe"]))

        value = [urlroot, login, password]
    else:
        value = tk.Entry(frame_pref, bg=couleur_fond,
                        justify="left")
        value.pack(side="left")
        value.insert(0, str(prefs[preference_name]["value"]))
    tk.Label(frame_pref, text="\n", bg=couleur_fond).pack()
    return value
    


def formulaire_main(prefs_file_name, access_to_network, last_version):
    """
    Création d'un formulaire test qui contient un bouton
    ouvrant le formulaire d'édition des préférences
    """
    couleur_fond = "white"
    couleur_bouton = "#e1e1e1"
    [master,
     zone_alert_explications,
     zone_access2programs,
     zone_actions,
     zone_ok_help_cancel,
     zone_notes] = main.main_form_frames(
         "Bibliostratus : Stratégie d'alignement d'URIs pour la Transition bibliographique",
         couleur_fond,
         couleur_bouton, access_to_network)
    frame1 = tk.Frame(master)
    frame1.pack()
    edit_prefs_Button = tk.Button(
                                  frame1,
                                  text="Editer les préférences",
                                  command=lambda: edit_preferences(
                                                                   master,
                                                                   prefs_file_name,
                                                                   access_to_network,
                                                                   last_version
                                                                  ),
                                  padx=40,
                                  pady=47,
                                  bg="#fefefe",
                                  font="Arial 9 bold",
                                 )
    edit_prefs_Button.pack()
    tk.mainloop()


if __name__ == "__main__":
    prefs_file_name = 'main/files/preferences.json'
    if not(os.path.isfile(prefs_file_name)):
        prefs_file_name = 'main/files/preferences.default'
    formulaire_main(prefs_file_name, True, [0, False])