# coding: utf-8


"""
Expérimentation : CSV converter
pour sortir au choix du CSV tabulé ou avec virgules
"""

from stdf import input2outputfile
import csv


def convert_file(inputfilename, report, sep="t"):
    csv_writer = create_csv_writer(report, sep)
    with open(inputfilename, encoding="utf-8") as file:
        content = csv.reader(file, delimiter="\t")
        for row in content:
            csv_write(row, csv_writer)


def csv_write(row, csv_writer):
    csv_writer.writerow(row)


def create_csv_writer(report, sep):
    dict_sep = {"t": "\t",
                "v": ",",
                ",": ","}
    if sep == "":
        sep = "\t"
    elif sep[0] in dict_sep:
        sep = dict_sep[sep]
    else:
        sep = "\t"
    if sep == ",":
        csv_writer = csv.writer(report, delimiter=sep, quotechar='"',
                                quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
    else:
        csv_writer = csv.writer(report, delimiter=sep, quotechar='\t',
                                quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
    return csv_writer
    

if __name__ == "__main__":
    inputfilename = input("Nom du fichier en entrée : ")
    sep = input("Séparateur : virgule [v] ou tabulation [t] [t] : ")
    if sep == "":
        sep = "t"
    report = input2outputfile(inputfilename, "converti")
    convert_file(inputfilename, report, sep)