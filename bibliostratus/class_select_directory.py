# coding: utf-8

import os
from tkinter import filedialog


class SelectDirectory(frame, text, bg_color):
    selected_directory = [""]

    frame_directory_selection = tk.Frame(frame, 
                      bg=couleur_fond, pady=5, padx=20)
    frame_directory_selection.pack()
    output_filepath = os.path.join(selected_directory[0], outputfilename)
    def download_zone(frame, text, selected_directory,
                  bg_color):
        frame_button = tk.Frame(frame)
        frame_button.pack()
        frame_selected = tk.Frame(frame)
        frame_selected.pack()
        display_selected = tk.Text(
            frame_selected, height=3, width=50, 
            bg=couleur_fond, bd=0, font="Arial 9 bold")
        display_selected.pack()
        # bouton_telecharger = download_button(frame,"Sélectionner un fichier","#ffffff")
        select_filename_button = tk.Button(
            frame_button,
            command=lambda: download_button(
                frame,
                text_bouton,
                frame_selected,
                display_selected,
                "#ffffff",
                selected_directory,
            ),
            text=text_bouton,
            padx=10,
            pady=10,
        )
        select_filename_button.pack()


    def download_button(frame, text, frame_selected, text_path,
                        couleur_fond, selected_directory):
        if (selected_directory != []):
            text_path.delete(0.0, 1000.3)
        filename = filedialog.askdirectory(
            parent=frame, title="Sélectionner un répertoire"
            )
        selected_directory[0] = filename
    text_path.insert(0.0, filename)