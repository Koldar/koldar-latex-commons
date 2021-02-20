Installation
============

```
\usepackage{koldar-latex-commons}

\begin{document}
    Now use the utils. For instance, \code{foo}!
\end{document}
```

Build
=====

You can build it by yourself via the following commands:

```
pdflatex.exe .\koldar-latex-commons.ins
pdflatex.exe .\koldar-latex-commons.dtx
```

Or you can use `pmakeup` project to build the software. Install `pmakeup`software:

```
pip install pmakeup
```

then, use `pmakeup build` to build the sty file, `pmakeup doc` to build the dtx file and  `pmakeup ctan` to upload a new file version to CTAN.

Upload to CTAN
==============

Package a zip with the following content:

 - my-package
    - README.md
    - my-package.dtx
    - my-package.ins
    - my-package.pdf


To upload the first version:

```
curl 
    -H "Content-Type: application/x-www-form-urlencoded"
    -d '{"author":"Massimo Bono", "description": "Set of utilities I personally find useful", "email": "massimobono1@gmail.com", "license": "LaTeX Project Public License 1.3", "pkg":"koldar-latex-commons", "summary": "Set of utilities I personally find useful", "update": "false", "uploader": "Massimo Bono", "version": "1.0.0"}'
    -X POST
    -F 'data=@file.zip'
    "https://www.ctan.org/submit/validate"
```

To upload a new version of the same package:

```
curl 
    -H "Content-Type: application/x-www-form-urlencoded"
    -d '{"author":"Massimo Bono", "description": "Set of utilities I personally find useful", "email": "massimobono1@gmail.com", "license": "LaTeX Project Public License 1.3", "pkg":"koldar-latex-commons", "summary": "Set of utilities I personally find useful", "update": "true", "uploader": "Massimo Bono", "version": "<new_version>"}'
    -X POST
    -F 'data=@file.zip'
    "https://www.ctan.org/submit/validate"
```


