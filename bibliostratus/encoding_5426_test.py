# coding: utf-8

"""
Test encodage
"""

import smc.bibencodings

texte = ["abcdefghijklmnopqrstéèêâöïùĐßþ"]

with open("test.txt", "wb") as file:
    for char in texte:
        file.write(char.encode("mab2"))
        
with open("test.txt", "r") as file:
    for line in file.readline():
        print(line)
