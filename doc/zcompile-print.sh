#!/bin/bash

# Name der Hauptdatei ohne Erweiterung
MAIN="mainprint"

# Liste der temporären Dateiendungen
TEMP_EXTENSIONS="aux bbl bcf blg fdb_latexmk fls lof lol lot out xml toc"

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
pdflatex -interaction=nonstopmode mainprint.mtex
biber mainprint
pdflatex -interaction=nonstopmode mainprint.mtex
pdflatex -interaction=nonstopmode mainprint.mtex

# Nachher aufräumen
clean

echo "Fertig: ${MAIN}.pdf wurde erzeugt."
