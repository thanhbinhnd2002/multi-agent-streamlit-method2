# ✅ Script đối chiếu gene từ mô hình cạnh tranh ngoài với OncoKB, PubMed, và mart_biotool
# ✅ Bổ sung tìm PubMedID cho các gene chưa có PubMedID (kể cả gene có trong OncoKB), không lưu file thừa

import pandas as pd
import os
from Bio import Entrez

# B1: Đọc file dữ liệu
model_file = "../output_multi_beta_pair_cpu/Human Gene Regulatory Network - Input_cpu_result.csv"
oncokb_file = "../Cancer gene OncoKB30012025.xlsx"
pubmed_file = "../Clinical.xlsx"
mart_file = "../mart_biotool.txt"

model_result = pd.read_csv(model_file)
oncokb = pd.read_excel(oncokb_file)
pubmed = pd.read_excel(pubmed_file)
mart = pd.read_csv(mart_file, sep="\t")

# B2: Hàm tìm PubmedID từ PubMed
Entrez.email = "phamthanhbinh2002nguyenkhuyen@gmail.com"

def search_pubmed_with_filter(gene_symbol):
    try:
        handle = Entrez.esearch(
            db="pubmed",
            term=f"{gene_symbol} AND cancer",
            retmax=5
        )
        record = Entrez.read(handle)
        handle.close()
        id_list = record["IdList"]

        # ✅ Lấy abstract của các bài báo
        filtered_ids = []
        if id_list:
            summaries = Entrez.efetch(db="pubmed", id=",".join(id_list), rettype="abstract", retmode="text").read()
            articles = summaries.split("\n\n")  # Phân tách các abstract
            for pmid, abstract in zip(id_list, articles):
                abstract_lower = abstract.lower()
                if gene_symbol.lower() in abstract_lower:
                    filtered_ids.append(pmid)
        return ", ".join(filtered_ids)

    except Exception as e:
        print(f"Lỗi với gene {gene_symbol}: {e}")
        return ""


# B3: Hàm lấy PubMedID từ PubMed (clinical)
def get_pubmed_info(gene):
    symbol_match = pubmed[pubmed['Symbol'] == gene]
    alias_match = pubmed[pubmed['Alias symbol'].fillna('').str.split(', ').apply(lambda x: gene in x)]
    if not symbol_match.empty:
        return symbol_match.iloc[0]['PubmedID']
    elif not alias_match.empty:
        return alias_match.iloc[0]['PubmedID']
    else:
        return ""

# B4: Hàm lấy Ensembl ID từ PubMed và mart_biotool
def get_ensembl_id(gene, aliases):
    symbol_match = pubmed[pubmed['Symbol'] == gene]
    alias_match = pubmed[pubmed['Alias symbol'].fillna('').str.split(', ').apply(lambda x: gene in x)]
    if not symbol_match.empty:
        return symbol_match.iloc[0]['Ensembl ID']
    elif not alias_match.empty:
        return alias_match.iloc[0]['Ensembl ID']
    else:
        possible_names = [gene] + aliases
        for name in possible_names:
            mart_match = mart[mart['Gene name'] == name]
            if not mart_match.empty:
                return mart_match.iloc[0]['Gene stable ID']
        return ""

# B5: Hàm đối chiếu OncoKB
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

# B6: Tạo bảng kết quả
output = []
for _, row in model_result.sort_values(by="Total_Support", ascending=False).iterrows():
    gene = row['Alpha_Node']
    total_support = row['Total_Support']

    symbol, alias, is_oncogene, is_tsg, in_oncokb = check_oncokb(gene)
    pubmed_id = get_pubmed_info(gene)
    ensembl_id = get_ensembl_id(symbol, alias.split(', ') if isinstance(alias, str) else [])

    # ✅ Nếu chưa có PubMedID thì tìm thêm qua Entrez API
    if pubmed_id == "":
        pubmed_id = search_pubmed_with_filter(symbol)

    output.append({
        "Ensembl ID": ensembl_id,
        "Symbol": symbol,
        "Alias symbol": alias,
        "Total_Support": total_support,
        "Is Oncogene": is_oncogene,
        "Is Tumor Suppressor Gene": is_tsg,
        "In OnkoKB": in_oncokb,
        "PubmedID": pubmed_id
    })

output_df = pd.DataFrame(output)

# B7: Lưu file hoàn thiện vào final_results_2
output_name = os.path.basename(model_file).replace(".csv", "_Annotated_Completed.csv")
os.makedirs("../final_results_pair", exist_ok=True)
output_df.to_csv(f"../final_results_pair/{output_name}", index=False)
print(f"✅ Đã lưu file hoàn thiện vào ../final_results_pair/{output_name}")
