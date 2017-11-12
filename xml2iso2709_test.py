# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 20:02:28 2017

@author: Lully

Test de création d'un fichier iso2709 à partir de notices MarcXML
"""

from lxml import etree
import pymarc as mc

entry_filename = "2rec.xml"
output = mc.MARCWriter(open("2rec.iso2709","wb"))

collection = mc.marcxml.parse_xml_to_array(entry_filename, strict=False)
for record in collection:
    print(type(record))
    #record_Rec = record.as_marc21
    output.write(record)