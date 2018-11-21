# coding: utf-8

"""
Tests pour parser le site Sudoc sur la base d'une requête*
"""

import funcs
from lxml.html import parse
from lxml import etree

def urlsudoc2ppn(url):
    """
    Extrait l'ensemble des PPN (avec pagination des résultats)
    à partir d'une URL de requête dans le Sudoc
    """
    (test, page) = funcs.testURLurlopen(url)
    if test:
        page = parse(page)
        nb_results = extract_nb_results_from_sudoc_page(page)
        print(url, nb_results)
        if nb_results > 1000:
            nb_results = 1000
        if nb_results == 1:
            listePPN = [extractPPNfromrecord(page)]
        else:
            listePPN = extractPPNfromsudocpage(page)
        i = 11
        while nb_results > i:
            url_f = url + "&FRST=" + str(i)
            test, following_page = funcs.testURLurlopen(url_f)
            if test:
                following_page = parse(following_page)
                listePPN.extend(extractPPNfromsudocpage(following_page))
            i += 10
        return listePPN


def extractPPNfromrecord(page):
    """
    Si un seul résultat : l'URL Sudoc ouvre la notice détaillée
    --> on récupère le PPN dans le permalien
    """
    link = page.find("//link[@rel='canonical']").get("href")
    ppn = link.split("/")[-1]
    return ppn



def extract_nb_results_from_sudoc_page(html_page):
    """
    Renvoie le nombre de résultats affiché sur une page de résultats Sudoc
    html_page est le contenu parsé (avec lxml.html.parse()) d'une page HTML
    """
    nb_results = 0
    ligne_info = ""
    try:
        ligne_info = etree.tostring(html_page.find("//table[@summary='query info']/tr")).decode(encoding="utf-8")
    except ValueError:
        pass
    if ("<span>" in ligne_info):
        nb_results = ligne_info.split("<span>")[-1].split("&")[0]
        nb_results = int(nb_results)
    return nb_results


def extractPPNfromsudocpage(html_page):
    """
    Renvoie une liste de PPN 
    à partir du code HTML d'une liste de résultats Sudoc
    html_page est le contenu parsé (avec lxml.html.parse()) d'une page HTML
    """
    listePPN = []
    for inp in html_page.xpath("//input[@name]"):
        if inp.get("name").startswith("ppn"):
            ppn = inp.get("value")
            listePPN.append(ppn)
    return listePPN
