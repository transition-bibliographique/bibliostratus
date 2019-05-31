# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 09:22:21 2018

@author: Lully

Librairie de fonctions d'extraction de notices BnF ou Abes 
à partir d'un identifiant (PPN Sudoc, PPN IdRef, ARK BnF, NNB/NNA BnF)

Les PPN doivent être préfixés : "PPN", "https://www.idref.fr/", 
ou "https://www.sudoc.fr"

Les ARK BnF doivent être préfixés "ark:/12148" 
(mais "ark" peut être précédé d'un espace nommant : 
"http://catalogue.bnf.fr", etc.)

Les fonctions ci-dessous exploitent 
    - l'identifiant pour déterminer l'agence concernée, la plateforme
    - le format à utiliser (Dublin Core, Intermarc, Unimarc)
    - les zones (Marc) ou éléments d'information (Dublin Core) à extraire
pour générer, pour chaque ligne, une liste de métadonnées correspondant à
la combinaison des 3 informations ci-dessus

Si aucune URL n'est définie, c'est le SRU BnF qui est interrogé
Par défaut (paramètres non précisés)
    - format : Unimarc
    - 1000 premiers résultats rapatriés

Exemples de requêtes :
results = SRU_result(query="bib.title any 'france moyen age'")
results.list_identifiers : liste des identifiants (type list())
results.dict_records : clé = l'identifiant, valeur = dictionnaire 
        results.dict_records[clé] = notice en XML

"""

from lxml import etree
from lxml.html import parse
import urllib.parse
from urllib import request, error
import http.client
from collections import defaultdict
import re
from copy import deepcopy


ns_bnf = {"srw":"http://www.loc.gov/zing/srw/", 
          "m":"http://catalogue.bnf.fr/namespaces/InterXMarc",
          "mn":"http://catalogue.bnf.fr/namespaces/motsnotices",
          "mxc":"info:lc/xmlns/marcxchange-v2",
          "dc":"http://purl.org/dc/elements/1.1/",
          "oai_dc":"http://www.openarchives.org/OAI/2.0/oai_dc/"}

ns_abes = {
    "bibo" : "http://purl.org/ontology/bibo/",
    "bio" : "http://purl.org/vocab/bio/0.1/",
    "bnf-onto" : "http://data.bnf.fr/ontology/bnf-onto/",
    "dbpedia-owl" : "http://dbpedia.org/ontology/",
    "dbpprop" : "http://dbpedia.org/property/",
    "dc" : "http://purl.org/dc/elements/1.1/",
    "dcterms" : "http://purl.org/dc/terms/",
    "dctype" : "http://purl.org/dc/dcmitype/",
    "fb" : "http://rdf.freebase.com/ns/",
    "foaf" : "http://xmlns.com/foaf/0.1/",
    "frbr" : "http://purl.org/vocab/frbr/core#",
    "gr" : "http://purl.org/goodrelations/v1#",
    "isbd" : "http://iflastandards.info/ns/isbd/elements/",
    "isni" : "http://isni.org/ontology#",
    "marcrel" : "http://id.loc.gov/vocabulary/relators/",
    "owl" : "http://www.w3.org/2002/07/owl#",
    "rdac" : "http://rdaregistry.info/Elements/c/",
    "rdae" : "http://rdaregistry.info/Elements/e/",
    "rdaelements" : "http://rdvocab.info/Elements/",
    "rdafrbr1" : "http://rdvocab.info/RDARelationshipsWEMI/",
    "rdafrbr2" : "http://RDVocab.info/uri/schema/FRBRentitiesRDA/",
    "rdai" : "http://rdaregistry.info/Elements/i/",
    "rdam" : "http://rdaregistry.info/Elements/m/",
    "rdau" : "http://rdaregistry.info/Elements/u/",
    "rdaw" : "http://rdaregistry.info/Elements/w/",
    "rdf" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs" : "http://www.w3.org/2000/01/rdf-schema#",
    "skos" : "http://www.w3.org/2004/02/skos/core#"
    }

srubnf_url = "http://catalogue.bnf.fr/api/SRU?"

class SRU_result:
    """"Résultat d'une requête SRU

    Les paramètres sont sous forme de dictionnaire : nom: valeur
    Problème (ou pas ?) : l'instance de classe stocke tous les résultats
    de la requête. Il vaut mieux ne s'en servir que quand il y en a peu
    (processus d'alignement)"""

    def __init__(self, query, url_sru_root=srubnf_url, parametres={}, get_all_records=False):  # Notre méthode constructeur
#==============================================================================
# Valeurs par défaut pour les paramètres de l'URL de requête SRU
#==============================================================================
        if ("recordSchema" not in parametres):
            parametres["recordSchema"] = "unimarcxchange"
        if ("version" not in parametres):
            parametres["version"] = "1.2"
        if ("operation" not in parametres):
            parametres["operation"] = "searchRetrieve"
        if ("maximumRecords" not in parametres):
            parametres["maximumRecords"] = "1000"
        if ("startRecord" not in parametres):
            parametres["startRecord"] = "1"
        if ("namespaces" not in parametres):
            parametres["namespaces"] = ns_bnf
        self.parametres = parametres
        url_param = f"query={urllib.parse.quote(query)}&" 
        url_param += "&".join([
                        "=".join([key, urllib.parse.quote(parametres[key])])
                         for key in parametres if key != "namespaces"
                        ])
        self.url = "".join([url_sru_root, url_param])
        self.test, self.result_first = testURLetreeParse(self.url)
        self.result = [self.result_first]
        self.list_identifiers = []
        self.dict_records = defaultdict()
        self.nb_results = 0
        self.errors = ""
        self.multipages = False
        if (self.test):
#==============================================================================
#             Récupération des erreurs éventuelles dans la requête
#==============================================================================
            if (self.result[0].find("//srw:diagnostics",
                namespaces=parametres["namespaces"]) is not None):
                for err in self.result[0].xpath("//srw:diagnostics/srw:diagnostic",
                                                namespaces=parametres["namespaces"]):
                    for el in err.xpath(".", namespaces=parametres["namespaces"]):
                        self.errors += el.tag + " : " + el.text + "\n"
#==============================================================================
#           Récupération du nombre de résultats
#           S'il y a des résultats au-delà de la première page,
#           on active la pagination des résultats pour tout récupérer
#           Le résultat est stocké dans un dictionnaire
#           dont les clés sont les numéros de notices, 
#           et la valeur le contenu du srx:recordData/*
#==============================================================================
            self.nb_results = 0
            if (self.result[0].find("//srw:numberOfRecords", 
                                                namespaces=parametres["namespaces"]
                                                ) is not None):
                self.nb_results = int(self.result[0].find("//srw:numberOfRecords", 
                                                namespaces=parametres["namespaces"]
                                                ).text)
            self.multipages = self.nb_results > (int(parametres["startRecord"])+int(parametres["maximumRecords"])-1)
            if (get_all_records and self.multipages):
                j = int(parametres["startRecord"])
                while (j+int(parametres["maximumRecords"]) <= self.nb_results):
                    parametres["startRecords"] = str(int(parametres["startRecord"])+int(parametres["maximumRecords"]))
                    url_next_page = url_sru_root + "&".join([
                        "=".join([key, urllib.parse.quote(parametres[key])])
                         for key in parametres if key != "namespaces"
                        ])
                    (test_next, next_page) = testURLetreeParse(url_next_page)
                    if (test_next):
                        self.result.append(next_page)
                    j += int(parametres["maximumRecords"])
#==============================================================================
#           Après avoir agrégé toutes les pages de résultats dans self.result
#           on stocke dans le dict_records l'ensemble des résultats
#==============================================================================
            for page in self.result:
                for record in page.xpath("//srw:record", 
                                                    namespaces=parametres["namespaces"]):
                    identifier = ""
                    if (record.find("srw:recordIdentifier", 
                        namespaces=parametres["namespaces"]) is not None):
                        identifier = record.find("srw:recordIdentifier", 
                                                 namespaces=parametres["namespaces"]).text
                    elif (record.find(".//*[@tag='001']") is not None):
                        identifier = record.find(".//*[@tag='001']").text
                    full_record = record.find("srw:recordData/*",
                                            namespaces=parametres["namespaces"])
                    self.dict_records[identifier] = full_record
                    self.list_identifiers.append(identifier)
            

    def __str__(self):
        """Méthode permettant d'afficher plus joliment notre objet"""
        return "url: {}".format(self.url)
        return "nb_results: {}".format(self.nb_results)
        return "errors: {}".format(self.errors)

class Record2metas:
    """Métadonnées (à partir d'une notice et d'une liste de zones)
    renvoyées sous forme de tableau
    Il faut voir si la notice est une notice BnF ou Abes"""
    def __init__(self, identifier, XMLrecord, zones):  
        self.init = XMLrecord
        self.str = etree.tostring(XMLrecord, pretty_print=True)
        liste_zones = zones.split(";")
        self.format = "marc"
        if ("dc:" in zones):
            self.format = "dc"
        self.recordtype, self.doctype, self.entity_type = extract_docrecordtype(XMLrecord, self.format)
        self.docrecordtype = self.doctype + self.recordtype
        self.metas = []
        self.source = ""
        if ("ark:/12148" in identifier):
            self.source = "bnf"
        elif ("sudoc" in identifier 
              or "idref" in identifier
              or "ppn" in identifier.lower()):
            self.source = "abes"
        elif(re.fullmatch("\d\d\d\d\d\d\d\d", identifier) is not None):
            self.source = "bnf"
            
        if (self.source == "bnf" and self.format == "marc"):
            for zone in liste_zones:
                self.metas.append(extract_bnf_meta_marc(XMLrecord, 
                                                        zone))
        elif (self.source == "bnf" and self.format == "dc"):
            for el in liste_zones:
                self.metas.append(extract_bnf_meta_dc(XMLrecord, 
                                                        zone))        
        elif (self.source == "abes" and self.format == "marc"):
            for el in liste_zones:
                self.metas.append(extract_abes_meta_marc(XMLrecord, 
                                                        zone))
        elif (self.source == "abes" and self.format == "dc"):
            for el in liste_zones:
                self.metas.append(extract_abes_meta_dc(XMLrecord, 
                                                        zone))

    def __str__(self):
        """Méthode permettant d'afficher plus joliment notre objet"""
        return "{}".format(self.metas)


def sruquery2results(url, urlroot=srubnf_url):
    """
    Fonction utile pour les requêtes avec un grand nombre de résultats
    Permet de générer un SRU_result par page, 
    jusqu'à atteindre le nombre total de résultats
    """
    params = {}
    url_root, param_str = url.split("?")
    param_list = param_str.split("&")
    for el in param_list:
        params[el.split("=")[0]] = el.split("=")[1]
    query = urllib.parse.unquote(params.pop("query"))
    nb_results = SRU_result(query, url_root, parametres={"maximumRecords": "1"})
    i = 1
    while (i < nb_results):
        params_current = deepcopy(params)
        params_current["maximumRecords"] = "1000"
        params_current["startRecord"] = str(i)
        results = SRU_result(query, url_root, params_current)
     

def testURLetreeParse(url, print_error = True):
    """Essaie d'ouvrir l'URL et attend un résultat XML
    Renvoie 2 variable : résultat du test (True / False) et le fichier
    renvoyé par l'URL"""
    test = True
    resultat = ""
    try:
        resultat = etree.parse(request.urlopen(url))
    except etree.XMLSyntaxError as err:
        if (print_error):
            print(url)
            print(err)
 
        test = False
    except etree.ParseError as err:
        if (print_error):
            print(url)
            print(err)
        test = False
 
    except error.URLError as err:
        if (print_error):
            print(url)
            print(err)
        test = False
 
    except ConnectionResetError as err:
        if (print_error):
            print(url)
            print(err)
        test = False
 
    except TimeoutError as err:
        if (print_error):
            print(url)
            print(err)
        test = False
 
    except http.client.RemoteDisconnected as err:
        if (print_error):
            print(url)
            print(err)
        test = False
 
    except http.client.BadStatusLine as err:
        if (print_error):
            print(url)
            print(err)
        test = False
 
    except ConnectionAbortedError as err:
        if (print_error):
            print(url)
            print(err)
        test = False
 
    return (test,resultat)

def retrieveURL(url):
    page = etree.Element("default")
    try:
        page = etree.parse(url)
    except OSError:
        print("Page non ouverte, erreur Serveur")
    except etree.XMLSyntaxError:
        print("Erreur conformité XML")
    return page


#==============================================================================
#  Fonctions d'extraction des métadonnées
#==============================================================================

def extract_docrecordtype(XMLrecord, rec_format):
    """Fonction de récupération du type de notice et type de document
    rec_format peut prendre 2 valeurs: 'marc' et 'dc' """
    val_003 = ""
    leader = ""
    doctype = ""
    recordtype = ""
    entity_type = ""
    format_attribute = XMLrecord.get("format")
    if format_attribute is not None:
        format_attribute = format_attribute.lower()
    type_attribute = XMLrecord.get("type")
    if type_attribute:
        type_attribute = type_attribute.lower()
    if (rec_format == "marc"):
        for element in XMLrecord:
            if ("leader" in element.tag):
                leader = element.text
            if element.get("tag") == "003":
                val_003 = element.text
        if (val_003 != ""
            and format_attribute != "intermarc"):
            #Alors c'est de l'Unimarc
            if ("sudoc" in val_003):
            #Unimarc Bib
                doctype,recordtype = leader[6], leader[7]
                entity_type = "B"
            elif ("ark:/12148" in val_003 and int(val_003[-9:-1])>=3):
            #Unimarc Bib
                doctype,recordtype = leader[6], leader[7]
                entity_type = "B"
            elif ("idref" in val_003):
            #Unimarc AUT
                recordtype = leader[9]
                entity_type = "A"
            elif ("ark:/12148" in val_003 and int(val_003[-9:-1])<3):
            #Unimarc AUT
                recordtype = leader[9]
                entity_type = "A"
        elif type_attribute:
            #C'est de l'intermarc (BnF)
            entity_type = type_attribute[0].upper()
            if (entity_type == "B"
               and len(leader) > 8):
                #Intermarc BIB
                recordtype, doctype = leader[8], leader[22]
            elif (entity_type == "A"
                  and len(leader) > 8):
                recordtype = leader[8]
                
    elif (rec_format == "dc"):
        entity_type = "B"
        
    return (doctype, recordtype, entity_type)




def field2listsubfields(field):
    """
    Récupère la liste des noms des sous-zones pour une zone donnée
    """
    liste_subf = []
    for subf in field.xpath("*"):
        liste_subf.append(subf.get("code"))
    liste_subf = " ".join(liste_subf)
    return liste_subf



def field2subfield(field, subfield, nb_occ="all", sep="~"):
    path = "*[@code='" + subfield + "']"
    listeValues = []
    if (nb_occ == "first" or nb_occ == 1):
        if (field.find(path) is not None and
                field.find(path).text is not None):
            val = field.find(path).text
            listeValues.append(val)
    else:
        for occ in field.xpath(path):
            if (occ.text is not None):
                listeValues.append(occ.text)
    listeValues = sep.join(listeValues)
    return listeValues

def field2value(field):
    try:
        value = " ".join([" ".join(["$" + el.get("code"), el.text]) for el in field.xpath("*")])
    except ValueError:
        value = ""
    return value


def extract_bnf_meta_marc(record, zone):
    """
    Ancien nom de la fonction, qui depuis a été généricisée
    """
    value = record2fieldvalue(record, zone)
    return value


def record2fieldvalue(record, zone):
    #Pour chaque zone indiquée dans le formulaire, séparée par un point-virgule, on applique le traitement ci-dessous
    value = ""
    field = ""
    subfields = []
    if (zone.find("$") > 0):
        #si la zone contient une précision de sous-zone
        zone_ss_zones = zone.split("$")
        field = zone_ss_zones[0]
        fieldPath = ".//*[@tag='" + field + "']"
        i = 0
        for field in record.xpath(fieldPath):
            i = i+1
            j = 0
            for subfield in zone_ss_zones[1:]:
                sep = ""
                if (i > 1 and j == 0):
                    sep = "~"
                j = j+1
                subfields.append(subfield)
                subfieldpath = "*[@code='"+subfield+"']"
                if (field.find(subfieldpath) is not None):
                    if (field.find(subfieldpath).text != ""):
                        valtmp = field.find(subfieldpath).text
                        #valtmp = field.find(subfieldpath).text.encode("utf-8").decode("utf-8", "ignore")
                        prefixe = ""
                        if (len(zone_ss_zones) > 2):
                            prefixe = " $" + subfield + " "
                        value = str(value) + str(sep) + str(prefixe) + str(valtmp)
    else:
        #si pas de sous-zone précisée
        field = zone
        path = ""
        if (field == "000"):
            path = ".//*[local-name()='leader']"
        else:
            path = ".//*[@tag='" + field + "']"
        i = 0        
        for field in record.xpath(path):
            i = i+1
            j = 0
            if (field.find("*", namespaces=ns_bnf) is not None):
                sep = ""
                for subfield in field.xpath("*"):
                    sep = ""
                    if (i > 1 and j == 0):
                        sep = "~"
                    #print (subfield.get("code") + " : " + str(j) + " // sep : " + sep)
                    j = j+1
                    valuesubfield = ""
                    if (subfield.text != ""):
                        valuesubfield = str(subfield.text)
                        if (valuesubfield == "None"):
                            valuesubfield = ""
                    value = value + sep + " $" + subfield.get("code") + " " + valuesubfield
            else:
                value = field.find(".").text
    if (value != ""):
        if (value[0] == "~"):
            value = value[1:]
    return value


def extract_bnf_meta_dc(record,zone):
    #Pour chaque zone indiquée dans le formulaire, séparée par un point-virgule, on applique le traitement ci-dessous
    value = []
    for element in record.xpath(zone, namespaces=ns_bnf):
        value.append(element.text)
    value = "~".join(value)
    return value.strip()


def extract_abes_meta_marc(record,zone):
    #Pour chaque zone indiquée dans le formulaire, séparée par un point-virgule, on applique le traitement ci-dessous
    value = ""
    field = ""
    subfields = []
    if (zone.find("$") > 0):
        #si la zone contient une précision de sous-zone
        zone_ss_zones = zone.split("$")
        field = zone_ss_zones[0]
        fieldPath = "datafield[@tag='" + field + "']"
        i = 0
        for field in record.xpath(fieldPath):
            i = i+1
            j = 0
            for subfield in zone_ss_zones[1:]:
                sep = ""
                if (i > 1 and j == 0):
                    sep = "~"
                j = j+1
                subfields.append(subfield)
                subfieldpath = "subfield[@code='"+subfield+"']"
                if (field.find(subfieldpath) is not None):
                    if (field.find(subfieldpath).text != ""):
                        valtmp = field.find(subfieldpath).text
                        #valtmp = field.find(subfieldpath,namespaces=ns_bnf).text.encode("utf-8").decode("utf-8", "ignore")
                        prefixe = ""
                        if (len(zone_ss_zones) > 2):
                            prefixe = " $" + subfield + " "
                        value = str(value) + str(sep) + str(prefixe) + str(valtmp)
    else:
        #si pas de sous-zone précisée
        field = zone
        field_tag = ""
        if (field == "001" or field == "008" or field == "009"):
            field_tag="controlfield"
        else:
            field_tag = "datafield"
        path = ""
        if (field == "000"):
            path = "leader"
        else:
            path = field_tag + "[@tag='" + field + "']"
        i = 0        
        for field in record.xpath(path):
            i = i+1
            j = 0
            if (field.find("subfield") is not None):
                sep = ""
                for subfield in field.xpath("subfield"):
                    sep = ""
                    if (i > 1 and j == 0):
                        sep = "~"
                    j = j+1
                    valuesubfield = ""
                    if (subfield.text != ""):
                        valuesubfield = str(subfield.text)
                        if (valuesubfield == "None"):
                            valuesubfield = ""
                    value = value + sep + " $" + subfield.get("code") + " " + valuesubfield
            else:
                value = field.find(".").text
    if (value != ""):
        if (value[0] == "~"):
            value = value[1:]
    return value.strip()

def extract_abes_meta_dc(record,zone):
    #Pour chaque zone indiquée dans le formulaire, séparée par un point-virgule, on applique le traitement ci-dessous
    value = []
    zone = "//" + zone
    for element in record.xpath(zone, namespaces=ns_abes):
        value.append(element.text)
    value = "~".join(value)
    return value.strip()


def nna2bibliees(ark):
    nbBIBliees = "0"
    url = "http://catalogue.bnf.fr/" + ark
    page = parse(url)
    hrefPath = "//a[@title='Voir toutes les notices liées']"
    if (page.xpath(hrefPath) is not None):
        if (len(page.xpath(hrefPath)) > 0):
            nbBIBliees = str(page.xpath(hrefPath)[0].text)
            nbBIBliees = nbBIBliees[31:].replace(")","")
        #print(url + " : " + nbBIBliees)
    return nbBIBliees


def abesrecord2meta(recordId, record, parametres):
    metas = []
    nn = recordId
    typenotice = ""
    if (record.find("leader") is not None):
        leader = record.find("leader").text
        if ("unimarc" in parametres["format_records"]):
            typenotice = leader[6] + leader[7] 
        elif ("intermarc" in parametres["format_records"]):
            typenotice = leader[22] + leader[8]
    listeZones = parametres["zones"].split(";")
    colonnes_communes = ["PPN"+recordId, nn, typenotice]
    for el in listeZones:
        if ("marc" in parametres["format_records"]):
            metas.append(extract_abes_meta_marc(record, el))
        else:
            metas.append(extract_abes_meta_dc(record, el))
    if (parametres["BIBliees"] == 1):
        nbBibliees = nna2bibliees(recordId)
        colonnes_communes.append(nbBibliees)
    line_resultats = "\t".join(colonnes_communes) + "\t" + "\t".join(metas)
    return line_resultats


def bnfrecord2meta(recordId, record, parametres):
    metas = []
    nn = recordId
    typenotice = ""
    if ("ark" in recordId):
        nn = recordId[recordId.find("ark")+13:-1]
    if (record.find("mxc:leader", namespaces=ns_bnf) is not None):
        leader = record.find("mxc:leader", namespaces=ns_bnf).text
        if ("unimarc" in parametres["format_records"]):
            typenotice = leader[6] + leader[7] 
        elif ("intermarc" in parametres["format_records"]):
            typenotice = leader[22] + leader[8]
    listeZones = parametres["zones"].split(";")
    colonnes_communes = [recordId,nn,typenotice]
    for el in listeZones:
        if ("marc" in parametres["format_records"]):
            metas.append(extract_bnf_meta_marc(record,el))
        else:
            metas.append(extract_bnf_meta_dc(record,el))
    if (parametres["BIBliees"] == 1):
        nbBibliees = nna2bibliees(recordId)
        colonnes_communes.append(nbBibliees)
    line_resultats = "\t".join(colonnes_communes) + "\t" + "\t".join(metas)
    return line_resultats

def ark2meta(recordId,IDtype,parametres):
    #TypeEntite= "B" pour notices Biblio, "A" pour notices d'autorité
    add_sparse_validated = ""
    if (parametres["typeEntite"] == "aut."):
        add_sparse_validated = urllib.parse.quote(' and aut.status any "sparse validated"')
    urlSRU = ""
    nn = recordId
    ark = recordId
    if (IDtype == "ark"):
        nn = recordId[13:21]
    line_resultats = ""
    query = parametres["typeEntite"] + "persistentid%20any%20%22" + recordId + "%22" + add_sparse_validated
    if (IDtype == "NN"):
        query = parametres["typeEntite"] + "recordId%20any%20%22" + nn + "%22" + add_sparse_validated 
    urlSRU = srubnf_url + query + "&recordSchema=" + parametres["format_records"]
    
    (test,page) = testURLetreeParse(urlSRU)    
    if (test):
        if (IDtype == "NN" and page.find("//srw:recordIdentifier",namespaces=ns_bnf) is not None):
            ark = page.find("//srw:recordIdentifier",namespaces=ns_bnf).text
        if (page.find("//srw:recordData/oai_dc:dc", namespaces=ns_bnf) is not None):
            record = page.xpath("//srw:recordData/oai_dc:dc",namespaces=ns_bnf)[0]
            line_resultats = bnfrecord2meta(ark,record,parametres)
        if (page.find("//srw:recordData/mxc:record", namespaces=ns_bnf) is not None):
            record = page.xpath("//srw:recordData/mxc:record",namespaces=ns_bnf)[0]
            line_resultats = bnfrecord2meta(ark,record,parametres)

    return line_resultats


def get_abes_record(ID, parametres):
    """A partir d'un identifiant PPN (IdRef / Sudoc), permet d'identifier si
    la notice est à récupérer sur IdRef ou sur le Sudoc"""
    platform = ""
    record = ""
    id_nett = ID.upper().split("/")[-1].replace("PPN","")

    if ("marc" in parametres["format_records"]):
        (test,record) = testURLetreeParse("https://www.sudoc.fr/" + id_nett + ".xml",False)
        if (test):
            platform = "https://www.sudoc.fr/"
        else:
            (test,record) = testURLetreeParse("https://www.idref.fr/" + id_nett + ".xml")
            if (test):
                platform = "https://www.idref.fr/"
    elif ("dublincore" in parametres["format_records"]):
        (test,record) = testURLetreeParse("https://www.sudoc.fr/" + id_nett + ".rdf",False)
        if (test):
            platform = "https://www.sudoc.fr/"
        else:
            (test,record) = testURLetreeParse("https://www.idref.fr/" + id_nett + ".rdf")
            if (test):
                platform = "https://www.idref.fr/"
    return (id_nett, test,record,platform)


def url2params(url):
    """
    Extrait les paramètres de requête du SRU à partir de l'URL
    Renvoie 
        - l'URL racine
        - la requête (query)
        - un dictionnaire des autres paramètres
    """
    url_root = url.split("?")[0]
    param = url.replace(url_root + "?", "")
    url_root += "?"
    param = param.split("&")
    param_list = [el.split("=") for el in param]
    param_dict = {}
    for el in param_list:
        param_dict[el[0]] = el[1]
    query = param_dict.pop("query", None)
    if query is not None:
        query = urllib.parse.unquote(query)
    return query, url_root, param_dict


def url2entity_type(url):
    entity_type = "bib."
    if ("aut." in url):
        entity_type= "aut."
    return entity_type
    
def extract_1_info_from_SRU(page,element,datatype = str):
    """Récupère le nombre de résultats"""
    val = ""
    if (datatype == int):
        val = 0
    path = ".//" + element
    if (page.find(path, namespaces=ns_bnf) is not None):
        val = page.find(path, namespaces=ns_bnf).text
        if (datatype == int):
            val = int(val)
    return val

def url2format_records(url):
    format_records = "unimarcxchange"
    if ("recordSchema=unimarcxchange-anl" in url):
        format_records = "unimarcxchange-anl"
    elif ("recordSchema=intermarcxchange" in url):
        format_records = "intermarcxchange"
    elif ("recordSchema=dublincore" in url):
        format_records = "dublincore"
    return format_records



def query2nbresults(url):
    if ("&maximumRecords" in url):
        url = re.sub("maximumRecords=(\d+)", "maximumRecords=1", url)
    else:
        url += "&maximumRecords=1"
    query, url_root, params = url2params(url)
    nb_results = SRU_result(query, url_root, params).nb_results
    return nb_results