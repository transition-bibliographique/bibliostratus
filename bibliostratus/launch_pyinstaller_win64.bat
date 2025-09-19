:: 1.Lance la compilation du code source
:: 2. Nettoie le répertoire build, renomme dist en "bibliostratus" et y place le raccourci pour le lancement du fichier
:: 3. Compresse le répertoire obtenu
:: 4. Supprime le répertoire initial "bibliostratus" 
@echo off
set /p version_bbs="version: "
::pyinstaller main.py --exclude-module numpy --exclude-module pandas --exclude-module scipy  --exclude-module notebook  --exclude-module matplotlib
::pyinstaller main.py
pyinstaller main.spec
rd /s /q build
copy bibliostratus.bat dist
xcopy /S main\files dist\main\files\
del dist\main\files\preferences.json
xcopy /S main\examples dist\main\examples\
xcopy /S main\examples "dist\jeux de donnees\"
xcopy /S tcl dist\main\tcl\
rename dist bibliostratus
"C:\Program Files\7-Zip\7z" a -tzip ..\bin\bibliostratus_%version_bbs%_win64_py3.10.zip bibliostratus/
rd /s /q bibliostratus

set RC=RC
call set Replaced=%%version:%RC%=%%
If NOT "%version%"=="%Replaced%" (
    echo version RC
	copy ..\bin\bibliostratus_%version%_win64_py3.10.zip ..\bin\RC\bibliostratus_%version%_win64_py3.10.zip
	del ..\bin\bibliostratus_%version%_win64_py3.10.zip
) else (
     ::Version en prod
	 echo version en prod
	 copy ..\bin\bibliostratus_%version%_win64_py3.10.zip ..\bin\bibliostratus_latest_win64_py3.10.zip
)
