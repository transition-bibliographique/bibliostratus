# Installer Bibliostratus sur Linux


## Installer python

```
$ apt install python3 python3-pip
```

## Vérifier la version 

```
$ python3 --version
```

## Installer les librairies

```
$ apt install python3-tk python3-unidecode 
$ pip3 install pymarc
$ pip3 install SPARQLWrapper
$ pip3 install lxml
$ pip3 install smc.bibencodings
```

## Lancer Bibliostratus

```
$ git clone <le depôt bibliostratus.git>
$ cd bibliostratus/bibliostratus
$ ./launch_bibliostratus.sh 
```

## Autre notice d'installation

* [Utiliser le code source plutôt que la version compilée](https://github.com/Transition-bibliographique/bibliostratus/wiki/Utiliser-le-code-source-plut%C3%B4t-que-la-version-compil%C3%A9e) - Windows
