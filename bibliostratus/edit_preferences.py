# coding: utf-8

"""
Edition du fichier de préférences
"""

import tkinter as tkinter

def edit_preferences(master_frame):
    prefs_update = launch_form_prefs(master_frame)

def launch_form_prefs(master_frame):
    couleur_fond = "white"
    couleur_bouton = "#2D4991"
    [form,
     zone_alert_explications,
     zone_access2programs,
     zone_actions,
     zone_ok_help_cancel,
     zone_notes] = main.form_generic_frames(master_frame,
                                            "Editer les préférences",
                                            couleur_fond, couleur_bouton,
                                            True)

 
    prefs = {}
    with open('main/files/preferences.json', "rb", encoding="utf-8") as prefs_file:
        prefs = json.load(prefs_file)
    for pref in prefs:
        pref2fields(pref)
    tk.mainloop()

def pref2fields(pref):
    tk.Label(bg=couleur_fond,
            text=pref["description"],
            justify="left").pack(side="left")
    value = tk.Entry(bg=couleur_fond,
            justify="left").pack(side="left")
    value.insert(pref["value"],)

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
    edit_prefs_Button = tk.Button(
        frame1,
        text="Editer les préférences",
        command=lambda: edit_preferences(
            master, True, [0, False]
        ),
        padx=40,
        pady=47,
        bg="#fefefe",
        font="Arial 9 bold",
    )
    edit_prefs_Button.pack()
    tk.mainloop()


if __name__ == "__main__"