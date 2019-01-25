# coding: utf-8

"""
Expérimentation recherche titre-auteur-date dans le Sudoc
via SolR total
https://www.sudoc.fr/SolrBiblio/SolrTotal_V3.htm

https://www.sudoc.fr/SolrBiblioProxy/SolrProxy?
q=BB200.B200Sa:+(bleu+histoire+couleur)
&version=2.2
&start=0&rows=50
&indent=on
&fl=B001_BS,B200.B200Sa_BS,id,A001_AS,A003_AS,A004_AS,
&solrService=SolrTotalV2

Comparer
0 résultat : https://www.sudoc.fr/SolrBiblioProxy/SolrProxy?q=BB200.B200Sa:%20(histoire%20AND%20couleur%20AND%20bleu)%20OR%20BB200.B200Se:%20(histoire%20AND%20couleur%20AND%20bleu)&version=2.2&start=0&rows=50&indent=on&fl=A001_AS,B001_BS,B200.B200Sa_BS,id,ppn_z,B200.B200Sa_BS,B200.B200Sd_BS,B200.B200Se_BS,B200.B200Sf_BS,&solrService=SolrTotalV2
X résultats : https://www.sudoc.fr/SolrBiblioProxy/SolrProxy?q=BB200.B200Sa:(histoire+couleur+bleu)&version=2.2&start=0&rows=50&indent=on&fl=A001_AS,B001_BS,B200.B200Sa_BS,id,ppn_z,B200.B200Sa_BS,B200.B200Sd_BS,B200.B200Se_BS,B200.B200Sf_BS,&solrService=SolrTotalV2
X résultats : https://www.sudoc.fr/SolrBiblioProxy/SolrProxy?q=BB200.B200Sa:(histoire+couleur+bleu)%20OR%20BB200.B200Se:(histoire+couleur+bleu)&version=2.2&start=0&rows=50&indent=on&fl=A001_AS,B001_BS,B200.B200Sa_BS,id,ppn_z,B200.B200Sa_BS,B200.B200Sd_BS,B200.B200Se_BS,B200.B200Sf_BS,&solrService=SolrTotalV2
"""


def tad2ppn(input_record, parametres):
    """
    Recherche par mots clés dans le Sudoc en parsant les pages HTML
    """    
    typeRecord4Sudoc = ""
    """vide (pour tous les types de document),
           B (pour les livres),
           T (pour les périodiques),
           Y (pour les thèses version de soutenance),
           V (pour le matériel audio-visuel)
           K (pour les cartes"""
    typeRecordDic = {"TEX": "B", "VID": "V", "AUD": "V", "PER": "T",
                     "CP": "K"}
    url = "http://www.sudoc.abes.fr//DB=2.1/SET=18/TTL=1/CMD?ACT=SRCHM\
&MATCFILTER=Y&MATCSET=Y&NOSCAN=Y&PARSE_MNEMONICS=N&PARSE_OPWORDS=N&PARSE_OLDSETS=N\
&IMPLAND=Y&ACT0=SRCHA&screen_mode=Recherche\
&IKT0=1004&TRM0=" + urllib.parse.quote(input_record.auteur_nett) + "\
&ACT1=*&IKT1=4&TRM1=" + urllib.parse.quote(input_record.titre.recherche) + "\
&ACT2=*&IKT2=1016&TRM2=&ACT3=*&IKT3=1016&TRM3=&SRT=YOP" + "\
&ADI_TAA=&ADI_LND=&ADI_JVU=" + urllib.parse.quote(input_record.date_nett) + "\
& ADI_MAT = " + typeRecordDic[input_record.type]
    url = url.replace("ADI_MAT=B", "ADI_MAT=B&ADI_MAT=Y")
    url = url.replace("ADI_MAT=N", "ADI_MAT=N&ADI_MAT=G")
    listePPN = urlsudoc2ppn(url)
    listePPN = check_sudoc_results(input_record, listePPN)
    return listePPN
