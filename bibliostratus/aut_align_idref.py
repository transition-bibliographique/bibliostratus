
# coding: utf-8

"""
Module d'alignement de notices d'autorité avec le Sudoc
En entrée, une funcs.Aut_record

A intégrer prochainement dans 
noticesaut2ark

Exemple de requête sur nom, prénom et date de naissance
avec type d'autorité "a" (personne physique)
https://www.idref.fr/Sru/Solr?q=persname_t:%22Hugo%20Victor%201802%22%20AND%20recordtype_z:a&sort=score%20desc&version=2.2&start=0&rows=30&indent=on
"""

import funcs

def aut2ppn_by_id(input_record,parametres):
    """
    Alignement par identifiant ISNI
    (l'ARK BnF ne peut pas -- encore -- être utilisé dans IdRef
    comme critère de recherche)
    """
    Liste_ppn = ""
    if (ark == "" and input_record.isni.propre != ""):
        ark = isni2ark(input_record.NumNot, input_record.isni.propre)
    if (ark == "" and input_record.frbnf.propre != ""):
        ark = frbnfAut2arkAut(input_record)
    return ark

    return Liste_ppn

def aut2ppn_by_accesspoint(input_record, parametres):
    Liste_ppn = ""
    return Liste_ppn