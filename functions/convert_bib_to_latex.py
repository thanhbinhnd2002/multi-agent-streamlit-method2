from pybtex.database.input import bibtex

# ✅ Đọc file .bib
parser = bibtex.Parser()
bib_data = parser.parse_file("1.bib")  # đổi tên file nếu cần

for key, entry in bib_data.entries.items():
    authors = entry.persons.get("author", [])
    author_str = ', '.join(["{} {}".format(p.last_names[0], p.first_names[0]) for p in authors])
    
    title = entry.fields.get("title", "").strip('{}')
    journal = entry.fields.get("journal", "")
    volume = entry.fields.get("volume", "")
    pages = entry.fields.get("pages", "")
    year = entry.fields.get("year", "")
    doi = entry.fields.get("doi", "")

    print(f"\\cite{{{key}}} {author_str}, “{title}”, \\textit{{{journal}}}, vol. {volume}, {year}, pp. {pages}.", end='')
    if doi:
        print(f" DOI: https://doi.org/{doi}")
    else:
        print()
