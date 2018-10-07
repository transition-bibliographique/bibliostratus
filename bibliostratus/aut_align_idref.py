# coding: utf-8

"""
Module d'alignement de notices d'autorité avec le Sudoc
En entrée, une funcs.Aut_record

A intégrer prochainement dans 
noticesaut2ark
"""
import urllib.parse

import funcs

import noticesaut2arkBnF as aut2ark

def aut2ppn_by_id(input_record, parametres):
    """
    Alignement par identifiant ISNI
    (l'ARK BnF ne peut pas -- encore -- être utilisé dans IdRef
    comme critère de recherche)
    """
    Liste_ppn = ""
    if (input_record.isni.propre != ""):
        Liste_ppn = isni2ppn(input_record.NumNot, input_record.isni.propre)
    if (Liste_ppn == "" and aut2ark.nettoyageArk(input_record.ark_init) != ""):
        Liste_ppn = autArk2ppn(input_record.NumNot, aut2ark.nettoyageArk(input_record.ark_init))

    return Liste_ppn


def autArk2ppn(NumNot, ark_nett):
    Liste_ppn = []
    url = f"https://www.idref.fr/services/ark2idref/http://catalogue.bnf.fr/{ark_nett}"
    (test, result) = funcs.testURLetreeParse(url)
    if test:
        for ppn in result.xpath("//ppn"):
            Liste_ppn.append(ppn.text)    
    Liste_ppn = ",".join(["PPN" + el for el in Liste_ppn if el])
    return Liste_ppn


def isni2ppn(NumNot, isni):
    """
    Le jour où il existera une API permettant d'interroger
    IdRef par son ISNI, ce sera utilisé là...
    """
    Liste_ppn = []
    Liste_ppn = ",".join(["PPN"+el for el in Liste_ppn if el])
    return Liste_ppn


def aut2ppn_by_accesspoint(input_record, parametres):
    """
    Exemple de requête sur nom, prénom et date de naissance
    avec type d'autorité "a" (personne physique)
    https://www.idref.fr/Sru/Solr?q=persname_t:%22Hugo%20Victor%201802%22%20AND%20recordtype_z:a&sort=score%20desc&version=2.2&start=0&rows=30&indent=on

    """
    Liste_ppn = []
    query = [input_record.lastname.propre, input_record.firstname.propre]
    if (input_record.firstdate.propre):
        query.append(input_record.firstdate.propre)
    elif (input_record.lastdate.propre):
        query.append(input_record.lastdate.propre)
    url = "".join(["https://www.idref.fr/Sru/Solr?q=persname_t:%22",
                   urllib.parse.quote(" ".join(query)),
                   "%22%20AND%20recordtype_z:a&sort=score%20desc&version=2.2&start=0&rows=1000"])
    (test, results) = funcs.testURLetreeParse(url)
    if test:
        for record in results.xpath("//doc"):
            ppn = record.find("str[@name='ppn_z']").text
            Liste_ppn.append(ppn)
    Liste_ppn = ",".join(["PPN"+el for el in Liste_ppn])
    return Liste_ppn