# -*- coding: utf-8 -*-

from unidecode import unidecode
from collections import defaultdict

def unidecode_local(string):
    """personnalisation de la fonction unidecode, 
    qui modifie aussi certains caractères de manière problématique
    par exemple : 
    ° devient 'deg' 
    """
    corr_temp_dict = {
        '°': '#deg#'
    }
    reverse_corr_temp_dict = defaultdict(str)
    for key in corr_temp_dict:
        reverse_corr_temp_dict[corr_temp_dict[key]] = key

    for char in corr_temp_dict:
        string = string.replace(char, corr_temp_dict[char])

    string = unidecode(string)
    for char in reverse_corr_temp_dict:
        string = string.replace(char, reverse_corr_temp_dict[char])
    return string

input_texte = input("texte à convertir : ")
normalized = unidecode_local(input_texte)
print(normalized)