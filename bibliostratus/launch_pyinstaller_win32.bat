:: 1.Lance la compilation du code source
:: 2. Nettoie le répertoire build, renomme dist en "alignement-donnees-bnf" et y place le raccourci pour le lancement du fichier
:: 3. Compresse le répertoire obtenu
:: 4. Supprime le répertoire initial "alignement-donnees-bnf" 
@echo off
set /p version="version: "
python "C:\Anaconda\Lib\site-packages\PyInstaller-3.3.1\pyinstaller.py" "C:\Users\USER\Downloads\bibliostratus-master\bibliostratus\main.py"
rd /s /q build
copy bibliostratus.bat dist
xcopy /S main\files dist\main\files\
xcopy /S main\examples dist\main\examples\
rename dist bibliostratus
"C:\Program Files\7-Zip\7z" a -tzip ..\bin\bibliostratus_%version%_win32_py3.6.zip bibliostratus\
rd /s /q bibliostratus
