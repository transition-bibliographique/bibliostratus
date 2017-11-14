# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 21:33:35 2017

@author: Lully
"""

import pymarc as mc

errors_list = []

def file2iso(filename):
    file = mc.MARCWriter(open("output_test.iso2709","w", encoding="utf-8"))
    collection = mc.marcxml.parse_xml(filename)
    for record in collection:
        try:
            file.write(record)
        except UnicodeEncodeError as err:
            errors_list.append(str(err))
file2iso("temp.xml")
            
print(errors_list)
