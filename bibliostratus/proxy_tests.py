# coding: utf-8

from urllib import request, error
from http import cookiejar
from urllib.parse import urlparse
import requests

def with_requests():
    proxies = {
        'http': 'fw_in.bnf.fr:8080',
        'https': 'fw_in.bnf.fr:8080',
    }
    proxies = {}
    s = requests.Session()
    s.proxies = proxies
    r = s.get("http://catalogue.bnf.fr/api/SRU?query=bib.subject2bib%20any%20%2211931023%22&recordSchema=intermarcxchange&version=1.2&operation=searchRetrieve&maximumRecords=10&startRecord=1")
    print(r.text)
    


def proxy_opener():
    """
    Utilisation du proxy pour les requêtes HTTP/HTTPS
    """
    proxies = {"https": "fw_in.bnf.fr:8080",
               "http": "fw_in.bnf.fr:8080"}
    proxy_handler = request.ProxyHandler(proxies)
    # construct a new opener using your proxy settings
    opener = request.build_opener(proxy_handler)
    # install the opener on the module-level
    request.install_opener(opener)
    test = request.urlopen("https://www.google.fr")
    html = test.read()
    print(html)


def proxyurllib():

    # disable proxy by passing an empty
    proxy_handler = request.ProxyHandler({"https_proxy": "http://fw_in.bnf.fr:8080",
               "http_proxy": "https://fw_in.bnf.fr:8080"})
    # alertnatively you could set a proxy for http with
    # proxy_handler = request.ProxyHandler({'http': 'http://www.example.com:3128/'})

    opener = request.build_opener(proxy_handler)

    url = 'http://www.example.org'

    # open the website with the opener
    req = opener.open(url)
    data = req.read().decode('utf8')
    print(data)

proxy_opener()