# coding: utf-8

"""
Module d'alignement de notices d'autorité avec le Sudoc
En entrée, une funcs.Aut_record

A intégrer prochainement dans 
noticesaut2ark
"""
import urllib.parse
import os, ssl


from lxml import etree
import pymarc as mc

import funcs
import aut2id
import marc2tables


# Ajout exception SSL pour éviter
# plantages en interrogeant les API IdRef
# (HTTPS sans certificat)
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl, '_create_unverified_context', None)): 
    ssl._create_default_https_context = ssl._create_unverified_context


def aut2ppn_by_id(input_record, parametres):
    """
    Alignement par identifiant ISNI
    (l'ARK BnF ne peut pas -- encore -- être utilisé dans IdRef
    comme critère de recherche)
    """
    Liste_ppn = ""
    if (input_record.isni.propre != ""):
        Liste_ppn = isni2ppn(input_record, input_record.isni.propre, parametres)
    if (Liste_ppn == "" and aut2id.nettoyageArk(input_record.ark_init) != ""):
        Liste_ppn = autArk2ppn(input_record, aut2id.nettoyageArk(input_record.ark_init))
    if Liste_ppn:
        input_record.alignment_method.append("ARK > PPN")
    return Liste_ppn


def autArk2ppn(input_record, ark_nett):
    Liste_ppn = []
    url = f"https://www.idref.fr/services/ark2idref/http://catalogue.bnf.fr/{ark_nett}"
    (test, result) = funcs.testURLetreeParse(url, display=False)
    if test:
        for ppn in result.xpath("//ppn"):
            Liste_ppn.append(ppn.text)    
    Liste_ppn = ",".join(["PPN" + el for el in Liste_ppn if el])
    return Liste_ppn


def idrefAut2arkAut(input_record, base="idref"):
    liste_ark = []
    url = f"https://www.{base}.fr/{input_record.ppn.propre}.xml"
    # print(url)
    (test, result) = funcs.testURLetreeParse(url, display=False)
    
    if test:
        for f033 in result.xpath("//*[@tag='033']"):
            val = funcs.field2subfield(f033, "a")
            if ("ark:/12148/" in val):
                val = val[val.find("ark:/12148/"):]
                liste_ark.append(val)
        if (liste_ark):
            input_record.alignment_method.append("PPN > ARK")
        if (liste_ark == []
           and result.find("//*[@tag='035']") is not None
           and "frbn" in funcs.record2fieldvalue(result, "035$a").lower()):
            aut_record = funcs.XML2record(result, 2).record
            #print(aut_record.metadata)
            liste_ark.extend(aut2id.frbnfAut2arkAut(aut_record).split(","))
            if (liste_ark):
                input_record.alignment_method.append("PPN > FBRNF > ARK")
    liste_ark = ",".join(liste_ark)
    return liste_ark


def aut2ppn_by_accesspoint(input_record, parametres):
    """
    Exemple de requête sur nom, prénom et date de naissance
    avec type d'autorité "a" (personne physique)
    https://www.idref.fr/Sru/Solr?q=persname_t:%22Hugo%20Victor%201802%22%20AND%20recordtype_z:a&sort=score%20desc&version=2.2&start=0&rows=30&indent=on

    """
    # Conversion du code (1 lettre) de type d'entité
    # en nom d'index pour la recherche par point d'accès
    aut_type_dict = {
        "a" : "persname",
        "b" : "corpname"
    }
    Liste_ppn = []
    query = ['"',input_record.lastname.propre, input_record.firstname.propre,'"']
    query_date = ""
    if (input_record.firstdate.propre and len(input_record.firstdate.propre) > 3):
        query_date = urllib.parse.quote(" AND " + aut_type_dict[parametres["type_aut"]] + '_t:"' + input_record.firstdate.propre + '"')
    elif (input_record.lastdate.propre and len(input_record.lastdate.propre) > 3):
        query_date = urllib.parse.quote(" AND " + aut_type_dict[parametres["type_aut"]] + '_t:"' + input_record.lastdate.propre + '"')
    url = "".join(["https://www.idref.fr/Sru/Solr?q=" + aut_type_dict[parametres["type_aut"]] + "_t:",
                   urllib.parse.quote(" ".join(query)),
                   query_date,
                   "%20AND%20recordtype_z:" + parametres["type_aut"] + "&sort=score%20desc&version=2.2&start=0&rows=1000"])
    (test, results) = funcs.testURLetreeParse(url)
    if test:
        for record in results.xpath("//doc"):
            ppn = record.find("str[@name='ppn_z']").text
            ppn = check_idref_record(ppn, input_record, ppn2idrefrecord(ppn, parametres), parametres)
            if ppn:
                Liste_ppn.append(ppn)
    Liste_ppn = ",".join(["PPN" + el for el in Liste_ppn])
    if (Liste_ppn):
        input_record.alignment_method.append("Point d'accès > PPN")
    return Liste_ppn


def check_idref_record(ppn, input_record, idref_record, parametres):
    """
    Compare une notice d'autorité en entrée (class Aut_record)
    et une notice IdRef (class Aut_record aussi)
    Reprendre ici
    """
    test = True
    if test:
        return ppn
    else:
        return ""


def ppn2idrefrecord(ppn, parametres):
    """
    A partir d'un PPN IdRef, récupère la notice en MARC
    et la convertit en Aut_record
    """
    metas = ppn2metasAut(ppn, parametres)
    record = funcs.Aut_record(metas, {})
    return record


def ppn2metasAut(ppn, parametres={"type_aut":"a"}):
    """
    A partir d'un PPN, génère une ligne de métadonnées 
    telles qu'attendues par le module d'alignement
    pour générer
    """
    url = f"https://www.idref.fr/{ppn}.xml"
    line = []
    #Si le fichier en entrée est composé de notices d'autorité
    # PEP (a) ou ORG (b) : on s'attend à avoir 8 éléments
    if ("type_aut" not in parametres
        or parametres["type_aut"] == "a" 
        or parametres["type_aut"] == "b"):
        line = ["","","","","","","",""]
    (test, record) = funcs.testURLetreeParse(url)
    if (test):
        leader = record.find(".//leader").text
        doctype, recordtype, doc_record = marc2tables.record2doc_recordtype(leader, 2)
        line = marc2tables.autrecord2metas(ppn, doc_record, record)
    return line


def isni2ppn(input_record, isni_id, parametres, origine="isni"):
    Liste_ppn = []
    url = "https://www.idref.fr/services/isni2idref/" + isni_id
    (test, page) = funcs.testURLetreeParse(url, display=False)
    if test:
        for ppn in page.xpath("//ppn"):
            Liste_ppn.append(ppn.text)
    Liste_ppn = ",".join(["PPN"+el for el in Liste_ppn if el])
    if Liste_ppn:
        input_record.alignment_method.append(origine)
    return Liste_ppn
