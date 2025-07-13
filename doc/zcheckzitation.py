import os
import re


def find_tex_and_bib_files():
    tex_files = [f for f in os.listdir() if f.endswith(".tex")]
    bib_files = [f for f in os.listdir() if f.endswith(".bib")]
    return tex_files, bib_files


def extract_cite_keys_from_tex(files):
    cite_keys = set()
    cite_pattern = re.compile(r'\\cite[tp]?[a-zA-Z]*\{([^}]*)\}')

    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            matches = cite_pattern.findall(content)
            for group in matches:
                keys = [k.strip() for k in group.split(',')]
                cite_keys.update(keys)
    return cite_keys


def extract_keys_from_bib(files):
    bib_keys = set()
    bib_pattern = re.compile(r'@\w+\{([^,]+),')

    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            matches = bib_pattern.findall(content)
            for key in matches:
                bib_keys.add(key.strip())
    return bib_keys


def main():
    tex_files, bib_files = find_tex_and_bib_files()
    print(f"Gefundene .tex-Dateien: {tex_files}")
    print(f"Gefundene .bib-Dateien: {bib_files}")

    cite_keys = extract_cite_keys_from_tex(tex_files)
    bib_keys = extract_keys_from_bib(bib_files)

    print("\n--- Analyse ---")
    missing_in_bib = cite_keys - bib_keys
    unused_in_tex = bib_keys - cite_keys

    if missing_in_bib:
        print("\n❌ Zitate in .tex, aber nicht in .bib:")
        for key in sorted(missing_in_bib):
            print("  -", key)
    else:
        print("\n✅ Alle Zitate in .tex sind auch in .bib vorhanden.")

    if unused_in_tex:
        print("\n📄 Bib-Einträge, die nicht zitiert werden:")
        for key in sorted(unused_in_tex):
            print("  -", key)
    else:
        print("\n✅ Alle Bib-Einträge werden auch zitiert.")


if __name__ == "__main__":
    main()
