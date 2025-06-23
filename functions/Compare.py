# ✅ match_with_oncokb_pubmed(df, top_n=None) — đối chiếu OncoKB & PubMed cho tk_app
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

oncokb_file = os.path.join(BASE_DIR, "..", "Cancer gene OncoKB30012025.xlsx")
pubmed_file = os.path.join(BASE_DIR, "..", "Clinical.xlsx")
mart_file = os.path.join(BASE_DIR, "..", "mart_biotool.txt")

oncokb = pd.read_excel(oncokb_file)
pubmed = pd.read_excel(pubmed_file)
mart = pd.read_csv(mart_file, sep="\t")

def get_pubmed_info(gene):
    symbol_match = pubmed[pubmed['Symbol'] == gene]
    alias_match = pubmed[pubmed['Alias symbol'].fillna('').str.split(', ').apply(lambda x: gene in x)]
    if not symbol_match.empty:
        return symbol_match.iloc[0]['PubmedID']
    elif not alias_match.empty:
        return alias_match.iloc[0]['PubmedID']
    else:
        return ""

def get_ensembl_id(gene, aliases):
    symbol_match = pubmed[pubmed['Symbol'] == gene]
    alias_match = pubmed[pubmed['Alias symbol'].fillna('').str.split(', ').apply(lambda x: gene in x)]
    if not symbol_match.empty:
        return symbol_match.iloc[0]['Ensembl ID']
    elif not alias_match.empty:
        return alias_match.iloc[0]['Ensembl ID']
    else:
        for name in [gene] + aliases:
            mart_match = mart[mart['Gene name'] == name]
            if not mart_match.empty:
                return mart_match.iloc[0]['Gene stable ID']
        return ""

def check_oncokb(gene):
    symbol_match = oncokb[oncokb['Hugo Symbol'] == gene]
    alias_match = oncokb[oncokb['Gene Aliases'].fillna('').str.split(', ').apply(lambda x: gene in x)]
    if not symbol_match.empty:
        row = symbol_match.iloc[0]
        return row['Hugo Symbol'], row['Gene Aliases'], row['Is Oncogene'], row['Is Tumor Suppressor Gene'], True
    elif not alias_match.empty:
        row = alias_match.iloc[0]
        return row['Hugo Symbol'], row['Gene Aliases'], row['Is Oncogene'], row['Is Tumor Suppressor Gene'], True
    else:
        return gene, "", "", "", False

def match_with_oncokb_pubmed(df, top_n=None):
    if top_n:
        df = df.sort_values(by="Total_Support", ascending=False).head(top_n)

    output = []
    for _, row in df.iterrows():
        gene = row['Alpha_Node']
        total_support = row['Total_Support']

        symbol, alias, is_oncogene, is_tsg, in_oncokb = check_oncokb(gene)
        pubmed_id = get_pubmed_info(gene)
        ensembl_id = get_ensembl_id(symbol, alias.split(', ') if isinstance(alias, str) else [])

        output.append({
            "Alpha_Node": gene,
            "Ensembl ID": ensembl_id,
            "Symbol": symbol,
            "Alias symbol": alias,
            "Total_Support": total_support,
            "Is Oncogene": is_oncogene,
            "Is Tumor Suppressor Gene": is_tsg,
            "In OncoKB": in_oncokb,
            "PubmedID": pubmed_id
        })

    return pd.DataFrame(output)
