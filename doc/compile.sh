#!/bin/bash

# Name der Hauptdatei ohne Erweiterung
MAIN="main"

# Liste der temporären Dateiendungen
TEMP_EXTENSIONS="aux bbl bcf blg fdb_latexmk fls lof log lol lot out xml toc"

# Funktion zum Entfernen temporärer Dateien
clean() {
  echo "Entferne Hilfsdateien..."
  find . -name "*.aux" -type f -delete
  for ext in $TEMP_EXTENSIONS; do
    rm -f "${MAIN}.${ext}"
  done

  # Entferne erzeugte SVG-PDF-Hilfsdateien
  rm -f "${MAIN}-svg-*.pdf_tex" "${MAIN}-svg-*.pdf"

  # Lösche den svg-inkscape-Ordner, falls vorhanden
  if [ -d "svg-inkscape" ]; then
    echo "Lösche Ordner svg-inkscape/"
    rm -rf svg-inkscape
  fi
}

# Vorher aufräumen
clean

# Kompilieren
echo "Kompiliere LaTeX-Dokument..."
latexmk -pdf -bibtex -shell-escape "${MAIN}.tex"

# Nachher aufräumen
clean

echo "Fertig: ${MAIN}.pdf wurde erzeugt."
