# -*- coding: utf-8 -*-
"""
Created on Wed Mar 14 15:33:19 2018

@author: Lully
"""

import tkinter as tk
from tkinter import filedialog
import csv

filenames = []

def download_button(frame, text,frame_selected,text_path,couleur_fond,file_entry_list):
    if (file_entry_list != []):
        text_path.delete(0.0,1000.3)
    filename = filedialog.askopenfilename(parent=frame,title=text)
    if (file_entry_list == []):
        file_entry_list.append(filename)
    else:
        file_entry_list[0] = filename
    text_path.insert(0.0,filename)
    
def download_zone(frame,file_entry_list):
    frame_button = tk.Frame(frame)
    frame_button.pack()
    frame_selected = tk.Frame(frame)
    frame_selected.pack()
    display_selected = tk.Text(frame_selected, height=3, width=40, bg="#ffffff")
    display_selected.pack()
    #bouton_telecharger = download_button(frame,"Sélectionner un fichier","#ffffff")
    select_filename_button = tk.Button(frame_button,command=lambda:download_button(frame, 
                                                    "Sélectionner un fichier",
                                                    frame_selected,display_selected,
                                                    "#ffffff", file_entry_list),
                                text="Sélectionner un fichier",
                                padx=10, pady=10)
    select_filename_button.pack()

    
def form_base():
    form = tk.Tk()
    frame_test = tk.Frame(form)
    frame_test.pack()
    download_zone(frame_test,filenames)

    tk.mainloop()
    
if __name__ == '__main__':
    form_base()
        