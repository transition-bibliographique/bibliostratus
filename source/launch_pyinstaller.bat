:: 1.Lance la compilation du code source
:: 2. Nettoie le répertoire build, renomme dist en "alignement-donnees-bnf" et y place le raccourci pour le lancement du fichier
:: 3. Compresse le répertoire obtenu
:: 4. Supprime le répertoire initial "alignement-donnees-bnf" 
pyinstaller main.py
rd /s /q build
copy alignement-donnees-bnf.bat dist
rename dist alignement-donnees-bnf
"C:\Program Files\7-Zip\7z" a -tzip ..\bin\alignement-donnees-bnf_X.XX_win64_py3.6.zip alignement-donnees-bnf/
rd /s /q alignement-donnees-bnf