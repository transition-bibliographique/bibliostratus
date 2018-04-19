# -*- coding: utf-8 -*-
"""
Created on Thu Apr 19 10:30:29 2018

@author: Lully
"""

filename = input("Nom du fichier : ")
file = open(filename,"rb").read()
if (len(file[0:3].decode("utf-8")) == 1):
    print("avec BOM")
    file = file[3:]
