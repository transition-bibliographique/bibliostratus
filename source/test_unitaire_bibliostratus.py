# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 13:05:22 2018

@author: Etienne Cavalié

Ensemble des tests unitaires sur un ensemble de fonctions utilisées par Bibliostratus
A lancer avec pytest
"""

import funcs
import main

#==============================================================================
# Tests des fonctions de nettoyage de chaînes de caractères 
#==============================================================================

def test_nettoyage(): 
    text = "Ça, c'est : l'été-du-siècle$" 
    assert funcs.nettoyage(text) == 'cacestletedusiecle' 
    assert funcs.nettoyage(text, remplacerEspaces=False) == 'ca c est l ete du siecle' 
    assert funcs.nettoyage(text, remplacerTirets=False) == 'cacestlete-du-siecle'
    
def test_isbn():
    """Vérifie que les ISBN en entrée de la classe ISBN sont correctement convertis"""
    isbn10 = funcs.International_id("2-84580-125-4")
    assert isbn10.propre == "2845801254"
    assert isbn10.converti == "9782845801257"
    assert isbn10.nett == "2845801254"
    
    isbndouble = funcs.International_id("2-84580-125-4;2-87153-145-5")
    assert isbndouble.propre == "2845801254"

    isbnfaux = funcs.International_id("2-")
    assert isbnfaux.nett == ""
    assert isbnfaux.propre == "2"
    assert isbnfaux.converti == ""

    isbnlettres = funcs.International_id("Br.")
    assert isbnlettres.nett == ""
    assert isbnlettres.propre == ""
    assert isbnlettres.converti == ""

def test_tomes():
    """Vérifie que les valeurs trouvées en entrée comme n° de tome
    ou volume sont correctement nettoyées"""
    case1 = "vol. 1"
    case2 = "tome XII"
    case3 = "tomes 1-5"
    assert funcs.convert_volumes_to_int(case1) == "1"
    assert funcs.convert_volumes_to_int(case2) == "12"
    assert funcs.convert_volumes_to_int(case3) == "1 5"

def test_dates():
    """Vérifie les différents traitements sur les dates"""
    
    #Nettoie la chaîne de caractère Date, généralement récupérée d'une 210$d (unimarc)
    assert funcs.nettoyageDate("DL 2017") == "2017"
    assert funcs.nettoyageDate("Impr. 1922") == "1922"
    assert funcs.nettoyageDate("Paris : Gallimard, 1930") == "1930"
    
    #Conserve uniquement la date de début
    assert funcs.datePerios("1925-1945") == "1925"
    
    #Date élargie aux 3 années antérieures et ultérieures
    assert funcs.elargirDatesPerios(1922) == "1919 1920 1921 1922 1923 1924 1925"
    
def test_titres():
    #Vérifications du traitement des titres
    titre1 = funcs.Titre("Au-delà de cette limite, votre ticket n'est plus valable")
    assert titre1.controles == "audeladecettelimitevotreticketnestplusvalable"
    assert titre1.recherche == "au dela de cette limite votre ticket est plus valable"
    
def test_cleaning_string():
    #Lieu de publication
    assert funcs.nettoyagePubPlace("Paris : Gallimard, 1930") == "paris gallimard"
    
                                  
#==============================================================================
# Contrôles des mécanismes de fonctionnement global du logiciel
#==============================================================================

def test_last_version():
    assert main.version >= main.check_last_compilation(main.programID)[0]
    
    
#==============================================================================
# Contrôles sur les alignements
#==============================================================================

def test_row_bib():
    #Vérifie que les métadonnées en entrée d'une notice BIB 
    #sont bien récupérées
    record = funcs.Bib_record(
                                [
                                "315756", "FRBNF435361100000003", "",
                                "978-2-213-67203-8", "", 
                                "Mon Paris, ma mémoire", "Morin Edgar", 
                                "DL 2013","","Fayard"
                                ],
                                1
                                )
    assert record.NumNot == "315756"
    assert record.frbnf == "FRBNF435361100000003"
    assert record.ark_init == ""
    assert record.isbn.init == "978-2-213-67203-8"
    assert record.ean.init == ""
    assert record.titre.init == "Mon Paris, ma mémoire"
    assert record.titre_nett == "monparismamemoire"
    assert record.auteur == "Morin Edgar"
    assert record.auteur_nett == "morin edgar"
    assert record.date_nett == "2013"
    assert record.publisher_nett == "fayard"