# -*- coding: utf-8 -*-
"""
Created on Sat Mar 31 15:51:25 2018

@author: Lully
"""
import pymarc as mc

def path2value(record, field_subfield):
    value = None
    val_list = []
    #print(field_subfield)
    if (field_subfield.find("$")>-1):
        field = field_subfield.split("$")[0]
        subfield = field_subfield.split("$")[1]
        for f in record.get_fields(field): 
            for subf in f.get_subfields(subfield):
                val_list.append(subf)
        if (val_list != []):
            value = ";".join(val_list)
    else:
        if (record[field_subfield] is not None and int(field_subfield) < 10):
            value = record[field_subfield].data
    return value

def record2meta(record, liste_elements, alternate_list=[]):
    zone = []
    for el in liste_elements:
        value = path2value(record, el)
        #print("record2meta : " + el + " / "  + str(value))
        if (value is not None):
            zone.append(value)
    #zone = [path2value(record, el) for el in liste_elements if path2value(record, el) is not None]
    if (zone == [] and alternate_list != []):
        for el in alternate_list:
            value = path2value(record, el)
            if (value is not None):
                zone.append(value)
        #zone = [path2value(record, el) for el in alternate_list if path2value(record, el) is not None]
    zone = " ".join(zone)
    #print(zone)
    return zone


input_file = open('../noticesbib.txt','r',encoding="utf-8").read().split(u'\u001D')[0:-1]
test = [el + u'\u001D' for el in input_file]
i = 1
for el in test:
    outputfilename = "reciso"+str(i)+".txt"
    outputfile = open(outputfilename, "wb")
    outputfile.write(el.encode("utf-8"))
    outputfile.close()
    with open(outputfilename, 'rb') as fh:
        collection = mc.MARCReader(fh)
        try:
            for record in collection:
                secondfilename = open("secondfile"+str(i) + ".txt","w",encoding="utf-8")
                title = record2meta(record,["200$a"])
                secondfilename.write(title)
                secondfilename.close()
        except mc.exceptions.RecordLengthInvalid as err:
            print(err)
            pass
    i += 1