# -*- coding: utf-8 -*-
# Petit script qui relance une recherche sur le résultat HTML
# quand la requête sur l'API XML a renvoyé une erreur HTTP (parce que 1 seul résultat)

from lxml import etree
from lxml.html import parse
import urllib.request as request
import urllib.error

url1 = "http://domybiblio.net/search/search_api.php?type_search=all&q=mecanique+quantique+Gondran&type_doc=B"
url2 = "http://domybiblio.net/search/search.php?type_search=all&q=mecanique+quantique+Gondran&type_doc=B"
try:
    type_page = "xml"
    page = etree.parse(request.urlopen(url1))
except urllib.error.HTTPError:
    type_page = "html"
    page = parse(url2)
if (type_page == "html"):
    liste_resultats = page.xpath("//li[@class='list-group-item']/a")
    for lien in liste_resultats:
        href = lien.get("href")
        ppn = "PPN" + href[href.find("id=")+3:href.find("id=")+12]
        print(ppn)
