# -*- coding: utf-8 -*-
"""
Alignement des concepts Rameau
par point d'accès

"""
 
import csv
import re
from lxml import etree
import http.client
from urllib import request
import urllib.parse
import urllib.error as error
from collections import defaultdict
from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions

import main
import sru

def ram2ark_by_accesspoint(input_record, parametres):
    """
    Renvoie la liste des ARK à partir d'une requête SPARQL
    ark est de type string (liste d'ARK séparés par des virgules)
    """
    ark, methode = accesspoint2sparql(input_record.accesspoint,
                                      parametres)
    if ark:
        input_record.alignment_method.append(methode)
    else:
        ark, methode = accesspoint2sru(input_record.accesspoint, parametres)    
    if ark:
        input_record.alignment_method.append(methode)
    return ark


def accesspoint2sparql(accesspoint, parametres={}):
    """
    Renvoie une liste d'ARK contenant comme clés 
    des identifiants, et comme valeurs
    le sous-ensemble Rameau auquel
    chaque ARK appartient
    """
    methode = ""
    ark = []
    query = rameau_construct_sparql_query(accesspoint,
                                          "skos:prefLabel")
    ark = extract_sparql_results(sparql2results(query),
                                 "concept",
                                 "sous_ensemble_Rameau",
                                 list,
                                 parametres)
    if ark:
        methode = "Point d'accès > SPARQL (prefLabel/forme retenue)"
    else:
        query = rameau_construct_sparql_query(accesspoint,
                                              "skos:altLabel")
        ark = extract_sparql_results(sparql2results(query),
                                     "concept",
                                     "sous_ensemble_Rameau",
                                     list,
                                     parametres)
        if ark:
            methode = "Point d'accès > SPARQL (altLabel/forme rejetée)"
    return ",".join(ark), methode


def sparql2results(query):
    """
    Exécute une requête Sparql
    """
    dataset = {}
    sparql = SPARQLWrapper("http://data.bnf.fr/sparql")
    sparql.setQuery(query)
    try:
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        dataset = results["results"]["bindings"]
    except error.HTTPError as err:
        print(err)
        print(query)
    except SPARQLExceptions.EndPointNotFound as err:
        print(err)
        print(query)
    return dataset

def extract_sparql_results(sparql_dataset, key, val, 
                           return_opt=list, parametres={}):
    liste_uri = []
    dict_uri = {}
    for el in sparql_dataset:
        ark = el.get(key).get("value").replace("#about","")
        ark = ark[ark.find("ark"):]
        value = el.get(val).get("value").split("/")[-1]
        liste_uri.append(ark)
        dict_uri[ark] = value
        add_type_rameau(ark, value, parametres)
    if return_opt == list:
        return liste_uri
    else:
        return dict_uri

def rameau_construct_sparql_query(accesspoint, label="skos:prefLabel"):
    """
    Construit la requête Sparql
    pour chercher l'URI correspondant au point d'accès
    la variable label peut être skos:prefLabel,
    skos:altLabel, ou éventuellement autre chose 
    """
    query = """PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    select distinct ?concept ?sous_ensemble_Rameau where {
        ?concept """ + f"{label} \"{accesspoint}\"" + """@fr.
        ?concept dcterms:isPartOf ?sous_ensemble_Rameau.
    }
    LIMIT 200
    """
    return query


def add_type_rameau(ark, typenotice, parametres):
    """
    Alimente, dans parametres{}, un sous-dictionnaire
    qui associe à chaque ARK son type d'entité Rameau
    """
    dict_type_ram = {
                     "r160": "Personnage",
                     "r161": "Collectivité",
                     "r163": "Titre propre d’anonyme",
                     "r164": "Publications en série",
                     "r165": "Titre uniforme textuel",
                     "r166": "Nom commun",
                     "r167": "Nom géographique",
                     "r168": "Subdivision chronologique",
                     "200": "Nom de personne",
                     "210": "Nom de collectivité",
                     "215": "Nom géographique",
                     "216": "Nom de marque",
                     "220": "Nom de famille",
                     "230": "Titre uniforme",
                     "240": "Auteur/titre",
                     "250": "Nom commun"
                    }
    if (parametres and "type_notices_rameau" in parametres):
        if (typenotice in dict_type_ram):
            parametres["type_notices_rameau"][ark] = dict_type_ram[typenotice]
        else:
            parametres["type_notices_rameau"][ark] = typenotice


def accesspoint2sru(accesspoint, parametres={}):
    """
    Rechercher le point d'accès dans les notices Rameau
    """
    accesspoint = main.clean_string(accesspoint, False, True)
    methode = []
    arks = []
    valid_tag = ""
    query = f"aut.accesspoint adj \"{accesspoint}\"\
and aut.status any \"sparse validated\"\
and aut.type all RAM"
    result = sru.SRU_result(query)
    for ark in result.dict_records:
        xml_record = result.dict_records[ark]
        tag = ""
        for field in xml_record:
            if (field.get("tag") is not None
               and field.get("tag").startswith("2")):
                tag = field.get("tag")
        f2XX = [el[el.find("$a"):]
                for el in sru.record2fieldvalue(xml_record, tag).split("~")]
        f4XX = [el[el.find("$a"):]
                for el in sru.record2fieldvalue(xml_record, f"4{tag[1:]}").split("~")]
        test = False
        for acc in f2XX:
            if test is False:
                acc = main.clean_string(re.sub(" \$. ", " ", acc[3:]), False, True)
                if acc == accesspoint:
                    arks.append(ark)
                    methode.append("SRU forme retenue")
                    valid_tag = tag
                    test = True
                    add_type_rameau(ark, tag, parametres)
        for acc in f4XX:
            if test is False:
                acc = main.clean_string(re.sub(" \$. ", " ", acc[3:]), False, True)
                if acc == accesspoint:
                    arks.append(ark)
                    methode.append("SRU forme rejetée")
                    valid_tag = f"4{tag:1}"
                    test = True
                    add_type_rameau(ark, tag, parametres)
    arks = ",".join(arks)
    methode = ",".join(methode)
    return arks, methode


