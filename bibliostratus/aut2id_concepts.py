# -*- coding: utf-8 -*-
"""
Alignement des concepts Rameau
par point d'accès

"""
 
import csv
from unidecode import unidecode
from lxml import etree
import http.client
from urllib import request
import urllib.parse
import urllib.error as error
from collections import defaultdict
from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions

def ram2ark_by_accesspoint(input_record, parametres):
    """
    Renvoie la liste des ARK à partir d'une requête SPARQL
    ark est de type string (liste d'ARK séparés par des virgules)
    """
    ark, methode = accesspoint2sparql(input_record.accesspoint,
                                      parametres)
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
    query = rameau_construct_sparql_query(accesspoint,
                                          "skos:prefLabel")
    ark = extract_sparql_results(sparql2results(query),
                                 "concept",
                                 "sous_ensemble_Rameau",
                                 list,
                                 parametres)
    if ark:
        methode = "Point d'accès > SPARQL (prefLabel)"
    else:
        query = rameau_construct_sparql_query(accesspoint,
                                              "skos:altLabel")
        ark = extract_sparql_results(sparql2results(query),
                                     "concept",
                                     "sous_ensemble_Rameau",
                                     list,
                                     parametres={})
        if ark:
            methode = "Point d'accès > SPARQL (altLabel)"
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
    dict_type_ram = {
        "r160": "Personnage",
        "r161": "Collectivité",
        "r163": "Titre propre d’anonyme",
        "r164": "Publications en série",
        "r165": "Titre uniforme textuel",
        "r166": "Nom commun",
        "r167": "Nom géographique",
        "r168": "Subdivision chronologique",
    }
    liste_uri = []
    dict_uri = {}
    for el in sparql_dataset:
        ark = el.get(key).get("value").replace("#about","")
        ark = ark[ark.find("ark"):]
        value = el.get(val).get("value").split("/")[-1]
        liste_uri.append(ark)
        dict_uri[ark] = value
        if (parametres and "type_notices_rameau" in parametres)
            if (value in dict_type_ram):
                parametres["type_notices_rameau"][ark] = dict_type_ram[value]
            else:
                parametres["type_notices_rameau"][ark] = value
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