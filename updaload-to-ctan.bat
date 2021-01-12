

"C:\Program Files\7-Zip\7z.exe" a -tzip koldar-latex-commons-auto.zip *.tex *.pdf *.ins *.dtx

curl -H "Content-Type: application/x-www-form-urlencoded" -F "author=Massimo Bono" -F "description=Set of utilities I personally find useful" -F "email=massimobono1@gmail.com" -F "license=LaTeX Project Public License 1.3" -F "pkg=koldar-latex-commons" -F "summary=Set of utilities I personally find useful" -F "update=false" -F "uploader=Massimo Bono" -F "version=1.0.0" -F "data=@.\koldar-latex-commons.zip" -X POST "https://www.ctan.org/submit/validate"