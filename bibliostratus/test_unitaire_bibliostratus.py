# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 13:05:22 2018

@author: Etienne Cavalié

Ensemble des tests unitaires sur un ensemble de fonctions utilisées par Bibliostratus
A lancer avec pytest
"""
from collections import defaultdict
import os
import csv
import json

import funcs
import main
import aut2id_idref
import bib2id
import aut2id
import marc2tables
import ark2records


# =============================================================================
# Tests des fonctions de nettoyage de chaînes de caractères
# =============================================================================

try:
    os.remove("test.txt")
except FileNotFoundError:
    pass

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

    # Nettoie la chaîne de caractère Date, généralement récupérée d'une 210$d (unimarc)
    assert funcs.nettoyageDate("DL 2017") == "2017"
    assert funcs.nettoyageDate("Impr. 1922") == "1922"
    assert funcs.nettoyageDate("Paris : Gallimard, 1930") == "1930"

    # Conserve uniquement la date de début
    assert funcs.datePerios("1925-1945") == "1925"

    # Date élargie aux 3 années antérieures et ultérieures
    assert funcs.elargirDatesPerios(1922) == "1919 1920 1921 1922 1923 1924 1925"


def test_titres():
    # Vérifications du traitement des titres
    titre1 = funcs.Titre("Au-delà de cette limite, votre ticket n'est plus valable")
    assert titre1.controles == "audeladecettelimitevotreticketnestplusvalable"
    assert titre1.recherche == "au dela de cette limite votre ticket est plus valable"


def test_cleaning_string():
    # Lieu de publication
    assert funcs.nettoyagePubPlace("Paris : Gallimard, 1930") == "paris gallimard"


def test_clean_stop_words():
    list_stop_words = ['bon', 'mal', 'p.', 's.e.', 's. exc.', 'r.m.', 'r.p.',
                       'vte', 'melle', 'mlle', 'gal', 'dr', 'cte', 'mis', 'mgr',
                       'm.', 'mr', 'mme', 'mm.', 'mise', 'gl', 'ct', 'rev.p.',
                       'vve ', 've', 'n°', 'sainct', 'st', 'saincte', 'ste ',
                       'csse', 'ctesse']
    title = "Le Cte et la Ctesse de Valcourt à la chasse"
    title_stop = funcs.clean_stop_words(title, list_stop_words, " ")
    assert title_stop == "Le et la de Valcourt à la chasse"


# =============================================================================
# Contrôles des mécanismes de fonctionnement global du logiciel
# =============================================================================


def test_last_version():
    assert main.version >= main.check_last_compilation(main.programID)[0]


# =============================================================================
# Contrôles sur les alignements
# =============================================================================


def test_row_bib():
    # Vérifie que les métadonnées en entrée d'une notice BIB
    # sont bien récupérées
    record = funcs.Bib_record(
                                [
                                 "315756", "FRBNF435361100000003", "",
                                 "978-2-213-67203-8", "",
                                 "Mon Paris, ma mémoire", "Morin Edgar",
                                 "DL 2013", "", "Fayard"
                                ],
                                1
                              )
    record2 = funcs.Bib_record(
                                [
                                 "1/104953", "(moccam)frbnf43632681", 
                                 "", "978-2-7436-2583-2", "9782743625832", 
                                 "Faillir être flingué roman", "celine minard", 
                                 "2013(©)", "", "Payot   Rivages"
                                ],
                                1
                               )
    assert record.NumNot == "315756"
    assert record.frbnf.propre == "frbnf435361100000003"
    assert record.ark_init == ""
    assert record.isbn.init == "978-2-213-67203-8"
    assert record.ean.init == ""
    assert record.titre.init == "Mon Paris, ma mémoire"
    assert record.titre_nett == "monparismamemoire"
    assert record.auteur == "Morin Edgar"
    assert record.auteur_nett == "morin edgar"
    assert record.date_nett == "2013"
    assert record.publisher_nett == "fayard"
    assert record2.frbnf.propre == "frbnf43632681"


def test_alignement_bib():
    # Teste sur des notices bibliographiques
    # avec divers types de notices et d'options
    bib_records = {"TEX1": {"input_record": funcs.Bib_record(
                                [
                                 "315756", "", "",
                                 "978-2-213-67203-8", "",
                                 "Mon Paris, ma mémoire", "Morin Edgar",
                                 "DL 2013", "", "Fayard"
                                ],
                                1
                              )},
                   "TEX2": {"input_record": funcs.Bib_record(
                                [
                                 "1/104953", "", "",
                                 "978-2-7436-2583-2", "9782743625832", 
                                 "Faillir être flingué roman", "celine minard", 
                                 "2013(©)", "", "Payot   Rivages"
                                ],
                                1
                               )},
                   "AUD1": {"input_record": funcs.Bib_record(
                                [
                                 "754134", "", "", "", 
                                 "3329184688321", "La grande nuit de l 'Opéra  1958", 
                                 "maria georges mars callas jean-pierre paris lance choeur orchestre albert de national opera sebastian hurteau jacques", 
                                 "2010", "Institut national de l'audiovisuel"
                                ],
                                3
                               )},
                   "PER1": {"input_record": funcs.Bib_record(
                                ["616", "", "", "2267-8417", 
                                "Fisheye", "", "2013-", "Paris"],
                                4
                               )},
                   "PER2": {"input_record": funcs.Bib_record(
                                ["629", "FRBNF391212190000007", 
                                 "", "", "Arts magazine", "", "2005-2016", ""],
                                4
                               )}
                  }
    param_alignBnF = {"preferences_alignement":  1,
                  "kwsudoc_option": 1,
                  "meta_bib": 0,
                  "meta_bnf": 0,
                  "stats": defaultdict(int)}
    param_alignSudoc = {"preferences_alignement":  2,
                  "kwsudoc_option": 1,
                  "meta_bib": 1,
                  "meta_bnf": 0,
                  "stats": defaultdict(int)}
    for record in bib_records:
        param_alignBnF["type_doc_bib"] = bib_records[record]["input_record"].option_record
        param_alignSudoc["type_doc_bib"] = bib_records[record]["input_record"].option_record
        bib_records[record]["alignment_resultBnF"] = bib2id.item_alignement(bib_records[record]["input_record"], 
                                                                            param_alignBnF)
        bib_records[record]["alignment_resultSudoc"] = bib2id.item_alignement(bib_records[record]["input_record"], 
                                                                              param_alignSudoc)
    assert bib_records["TEX1"]["alignment_resultBnF"].alignment_method_str == "ISBN + contrôle Titre 200$a"
    assert bib_records["TEX1"]["alignment_resultBnF"].ids_str == "ark:/12148/cb43536110d"
    assert bib_records["TEX1"]["alignment_resultSudoc"].ids_str == "https://www.sudoc.fr/168081768"
    assert bib_records["AUD1"]["alignment_resultBnF"].ids_str == "ark:/12148/cb423235808"
    assert bib_records["AUD1"]["alignment_resultSudoc"].ids_str == "ark:/12148/cb423235808"
    assert bib_records["PER1"]["alignment_resultBnF"].alignment_method_str == "ISSN"
    assert bib_records["PER1"]["alignment_resultBnF"].ids_str == "ark:/12148/cb43619642w"
    assert bib_records["PER1"]["alignment_resultSudoc"].ids_str == "https://www.sudoc.fr/174256019"
    assert bib_records["PER2"]["alignment_resultBnF"].ids_str == "ark:/12148/cb39121219d"
    assert bib_records["PER2"]["alignment_resultBnF"].alignment_method_str == "Numéro de notice + contrôle Titre 200$a"
    assert bib_records["PER2"]["alignment_resultSudoc"].ids_str == "https://www.sudoc.fr/077575245"



def test_alignement_aut():
    # Teste sur des notices bibliographiques
    # avec divers types de notices et d'options
    param_alignBnF = {"preferences_alignement":  1,
                  "type_aut": "a",
                  "input_data_type": 1,
                  "meta_bnf": 1,
                  "kwsudoc_option": 1,
                  "isni_option": 1,
                  "stats": defaultdict(int)}
    param_alignIdRef = {"preferences_alignement":  2,
                  "type_aut": "a",
                  "input_data_type": 1,
                  "meta_bnf": 1,
                  "isni_option": 1,
                  "stats": defaultdict(int)}

    aut_records_bnf = {"PEP1": {"input_record":funcs.Aut_record(
                              ["26859041", "frbn00161413x;frbn000752960;frbnf119023327", 
                               "ark:/12148/cb11902332s", "", "Faulkner", "", "1897", "1962"], param_alignBnF)
                           },
                   "PEP2": {"input_record":funcs.Aut_record(
                              ["26829762", "", "http://catalogue.bnf.fr/ark:/12148/cb11900005k", 
                              "", "Devos", "", "1922", "2006"], param_alignBnF)
                           },
                   "PEP3": {"input_record":funcs.Aut_record(
                              ["26842548", "", "", "", "Duleu", "", 
                              "1909", "    "], param_alignBnF)
                           }
                  }
    aut_records_idref = {"PEP1": {"input_record":funcs.Aut_record(
                              ["26859041", "frbn00161413x", 
                               "", "", "Faulkner", "", "1897", "1962"], param_alignIdRef)
                           },
                         "PEP2": {"input_record":funcs.Aut_record(
                              ["26829762", "", "http://catalogue.bnf.fr/ark:/12148/cb11900005k", 
                              "", "Devos", "", "1922", "2006"], param_alignIdRef)
                           }
                        }
    for record in aut_records_bnf:
        aut_records_bnf[record]["alignment_result"] = aut2id.align_from_aut_alignment(aut_records_bnf[record]["input_record"], param_alignBnF)
    for record in aut_records_idref:
        aut_records_idref[record]["alignment_result"] = aut2id.align_from_aut_alignment(aut_records_idref[record]["input_record"], param_alignIdRef)
    # assert aut_records["PEP1"]["input_record"].alignment_method == ["N° sys FRBNF + Nom"]
    # assert aut_records["PEP1"]["alignment_resultBnF"].alignment_method_str == "N° sys FRBNF + Nom"
    assert aut_records_bnf["PEP1"]["alignment_result"].ids_str == "ark:/12148/cb11902332s"
    assert aut_records_idref["PEP1"]["alignment_result"].ids_str == "https://www.idref.fr/026859041"


def test_alignement_bib2aut():
    param_alignBnF = {"preferences_alignement":  1,
                  "type_aut": "a",
                  "input_data_type": 2,
                  "meta_bnf": 1,
                  "isni_option": 0,
                  "stats": defaultdict(int)}
    param_alignIdRef = {"preferences_alignement":  2,
                  "type_aut": "a",
                  "input_data_type": 2,
                  "meta_bnf": 1,
                  "isni_option": 0,
                  "stats": defaultdict(int)}
    listePEP = [["11907286", "cb34633458q", "", "34633458", "", "Les Révélations des couleurs éthériques de nos auras", "", "", "Henry", "Judith", ""],
              ["11918746", "cb37713742b", "", "", "", "Bleu", "", "0000 0001 1470 4939", "Pastoureau", "Michel", "1947-...."],
              ["11897572", "cb451711140", "", "", "", "Marseille", "", "", "Contrucci", "Jean", "1939-...."],
              ["14413819", "cb45108648x", "", "45108648", "", "La route de l'or bleu", "", "", "Bernard", "Daniel", "1948-...."]
             ]
    i = 1
    bib2aut_recordsBnF = defaultdict(dict)
    bib2aut_recordsIdRef = defaultdict(dict)
    for pep in listePEP:
        key = "PEP"+str(i)
        bib2aut_recordsBnF[key] = {"input_record":funcs.Bib_Aut_record(pep, param_alignBnF)}
        bib2aut_recordsIdRef[key] = {"input_record":funcs.Bib_Aut_record(pep, param_alignIdRef)}
        i += 1

  
    for record in bib2aut_recordsBnF:
        bib2aut_recordsBnF[record]["alignment_result"] = aut2id.align_from_bib_alignment(bib2aut_recordsBnF[record]["input_record"], param_alignBnF)
    for record in bib2aut_recordsIdRef:
        bib2aut_recordsIdRef[record]["alignment_result"] = aut2id.align_from_bib_alignment(bib2aut_recordsIdRef[record]["input_record"], param_alignIdRef)
    assert bib2aut_recordsBnF["PEP1"]["alignment_result"].ids_str == "ark:/12148/cb11907286n"
    assert bib2aut_recordsIdRef["PEP2"]["alignment_result"].ids_str == "https://www.idref.fr/027059952"

def test_ppnidref_to_row():
    """Vérifie la fonction ppn2metasAut :
    à partir d'un PPN, on récupère des données en
    entrée sous forme d'une liste à 8 items, structurée
    comme les fichiers en entrée des alignements d'autorités"""
    ppn = "026973065" # Jacques Le Goff (1924-2014)
    metas_row = aut2id_idref.ppn2metasAut(ppn)
    assert metas_row[4] == "Le Goff"
    assert metas_row[5] == "Jacques"
    assert metas_row[6] == "1924"
    assert metas_row[7] == "2014"


def test_domybiblio_1_answer():
    """
    Si une seule réponse de DoMyBiblio, l'API plante 
    et Bibliostratus parse alors la version HTML
    On vérifie que le PPN est correctement récupéré
    """
    record = funcs.Bib_record(
                                [
                                 "15108805", "", "",
                                 "", "",
                                 "Législation industrielle Licence 3ème année 1941/42",
                                 "amiaud andre",
                                 "1941", "", "Cours de droit"
                                ],
                                1
                              )
    param = {"preferences_alignement": 2}
    ppn = bib2id.tad2ppn(record, param)
    assert ppn == "https://www.sudoc.fr/015108805" or ppn == ""

def test_controle_011():
    """
    Recherche de périodique par ISSN dans le catalogue BnF
    Vérifie que le test sur la 011 est correct (True si 011$a, False sinon)
    Permet de vérifier au passage la conversion d'ARK en XMLrecord, 
    et l'extraction de sous-zones 
    """
    issn = "1254-728X"
    recordTrue = bib2id.id2record("ark:/12148/cb345079588")
    recordFalse = bib2id.id2record("ark:/12148/cb40172844d")
    testTrue = bib2id.check_issn_in_011a(recordTrue, issn)
    testFalse = bib2id.check_issn_in_011a(recordFalse, issn)
    assert testTrue is True
    assert testFalse is False


def test_convert_iso2tables():
    """
    Ouverture d'un fichier ISO2709 de notices BIB pour le convertir en fichier tabulé
    """
    dirpath = os.path.dirname(os.path.realpath(__file__))
    isofile_name = os.path.join(dirpath, "main", "examples", "noticesbib.iso")    
    liste_files = marc2tables.iso2tables(None, isofile_name, 1, 1, "pytest_iso", display=False)
    for file in liste_files:
        liste_files[file].close()
        """if ("TEX" not in liste_files[file].name):
            os.remove(liste_files[file].name)"""
    first_line_text = []
    with open("pytest_iso-TEX-.txt", "r", encoding="utf-8") as file:
        content = csv.reader(file, delimiter="\t")
        next(content)
        first_line_text = next(content)
    print("first_line_text")
    print(first_line_text)
    wanted = ['FRBNF427031150000009', 'frbnf427031150000009',
              '', '', '', 'Plan de Paris 2012',
              'Paris Service de la topographie et de la documentation foncière',
              '2012', '', 'Mairie de Paris']
    for i in range(0, len(first_line_text)):
        wanted_i = " ".join(sorted([el for el in wanted[i].split(" ")]))
        first_line_text_i = " ".join(sorted([el for el in first_line_text[i].split(" ")]))
        print(i, wanted_i, first_line_text_i)
        assert wanted_i == first_line_text_i
    for file in liste_files:
        try:
            os.remove(os.path.join(dirpath, liste_files[file].name))
        except FileNotFoundError:
            pass


def test_prefs_default():
    prefs = {}
    with open(main.prefs_file_name, encoding="utf-8") as prefs_file:
        prefs = json.load(prefs_file)


if __name__ == "__main__":
  test_convert_iso2tables()