# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 13:42:07 2017

@author: BNF0017855

Avec Excel, récupération de la liste des fonctions du code de noticesbib2arkBnF,
pour ne garder, pour chaque fonction, que les fonctions qui y sont imbriquées Le
code ci-dessous permet de générer un arbre des opérations de noticesbib2arkBnF
en restituant cette imbrication
"""

# Liste des fonctions dans la version 0.92 du programme (22/12/2017)
liste_fonctions = {
    'create_reports': ['create_reports_1file', 'create_reports_files'],
    'ark2ark': ['testURLetreeParse'],
    'nettoyageTitrePourControle': ['nettoyage'],
    'nettoyageTitrePourRecherche': ['nettoyage', 'nettoyageAuteur'],
    'nettoyageIsbnPourControle': ['nettoyage', 'nettoyage_lettresISBN'],
    'nettoyageAuteur': ['nettoyage'],
    'relancerNNBAuteur': ['testURLetreeParse'],
    'comparerBibBnf':
        ['testURLetreeParse', 'comparaisonIsbn', 'comparaisonTitres'],
    'comparaisonIsbn': ['nettoyage'],
    'comparaisonTitres':
        [
            'comparaisonTitres_sous_zone', 'comparaisonTitres_sous_zone',
            'comparaisonTitres_sous_zone', 'comparaisonTitres_sous_zone'
        ],
    'comparaisonTitres_sous_zone': ['nettoyage'],
    'systemid2ark':
        [
            'testURLetreeParse', 'comparerBibBnf', 'relancerNNBAuteur',
            'systemid2ark'
        ],
    'rechercheNNB': ['testURLetreeParse', 'comparerBibBnf'],
    'oldfrbnf2ark': ['rechercheNNB', 'systemid2ark'],
    'frbnf2ark': ['testURLetreeParse', 'frbnf2arkoldfrbnf2ark'],
    'conversionIsbn': ['conversionIsbn1013', 'conversionIsbn1310'],
    'conversionIsbn1310': ['check_digit_10'],
    'conversionIsbn1013': ['check_digit_13'],
    'isbn2sru': ['testURLetreeParse', 'testURLetreeParse', 'comparaisonTitres'],
    'isbn_anywhere2sru':
        ['testURLetreeParse', 'testURLetreeParse', 'comparaisonTitres'],
    'isbn2sudoc':
        [
            'testURLretrieve', 'testURLetreeParse', 'ppn2ark',
            'testURLretrieve', 'testURLetreeParse', 'ppn2ark'
        ],
    'ppn2ark': ['testURLetreeParse', 'frbnf2ark'],
    'isbn2ark':
        [
            'isbn2sru', 'isbn2sru', 'conversionIsbn', 'isbn2sru', 'ean2ark',
            'ean2ark', 'isbn_anywhere2sru', 'isbn_anywhere2sru', 'isbn2sudoc'
        ],
    'ark2metas': ['testURLetreeParse'],
    'ppn2metas': ['testURLetreeParse'],
    'tad2ark':
        [
            'nettoyageTitrePourRecherche', 'testURLetreeParse',
            'testURLetreeParse', 'testURLetreeParse',
            'comparaisonTitresnettoyageTitrePourControle'
        ],
    'ark2recordBNF': ['url_requete_sru', 'testURLetreeParse'],
    'ean2ark':
        [
            'url_requete_sru', 'testURLetreeParse', 'ark2recordBNF',
            'comparaisonTitres'
        ],
    'no_commercial2ark':
        [
            'url_requete_sru', 'testURLetreeParse', 'ark2recordBNF',
            'controleNoCommercial'
        ],
    'controleNoCommercial': ['extract_metanettoyage_no_commercial'],
    'ark2metadc': ['ark2metas'],
    'monimpr':
        [
            'row2file', 'row2files', 'nettoyageIsbnPourControle',
            'nettoyage_isbn', 'nettoyageIsbnPourControle', 'nettoyage_isbn',
            'nettoyageTitrePourControle', 'nettoyageAuteur', 'nettoyageDate',
            'ark2ark', 'frbnf2ark', 'isbn2ark', 'ean2ark', 'tad2ark', 'tad2ark',
            'ark2metadc', 'row2file', 'row2files'
        ],
    'cddvd':
        [
            'row2file', 'row2files', 'nettoyageIsbnPourControle',
            'nettoyage_isbn', 'nettoyage_no_commercial',
            'nettoyageTitrePourControle', 'nettoyageAuteur', 'nettoyageDate',
            'ark2ark', 'frbnf2ark', 'ean2ark', 'no_commercial2ark', 'tad2ark',
            'tad2ark', 'ark2metadc', 'row2file', 'row2files'
        ],
    'launch': ['create_reports', 'monimpr', 'cddvd', 'fin_traitements'],
    'fin_traitements':
        ['stats_extraction', 'url_access_pbs_report', 'typesConversionARK'],
    'formulaire_noticesbib2arkBnF': ['launch', 'annuler']
}


def key2list(key, i):
    sep = i * " " + "|" + 2 * "-"
    print(sep + key)
    indentation = i + round(len(key) / 2) + 2
    if (key in liste_fonctions):
        for el in liste_fonctions[key]:
            key2list(el, indentation)
    else:
        return ""


key2list("formulaire_noticesbib2arkBnF", 0)
