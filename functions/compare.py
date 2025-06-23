# ✅ Script đối chiếu gene từ mô hình cạnh tranh ngoài với OncoKB, PubMed, và mart_biotool

import pandas as pd
import os

# B1: Đọc file dữ liệu
#model_file = "../new_output_multi_Beta_opt/Human Gene Regulatory Network - Input.csv"
model_file = "../Output_test/INF10000_EPS0.05_DELTA0.2_ITER50_TOL0.0001_NBETA2/Human cancer signaling - Input.csv"  # File mô hình cạnh tranh
oncokb_file = "../Cancer gene OncoKB30012025.xlsx"  # File OncoKB dạng Excel
pubmed_file = "../Clinical.xlsx"
mart_file = "../mart_biotool.txt"

model_result = pd.read_csv(model_file)
oncokb = pd.read_excel(oncokb_file)
pubmed = pd.read_excel(pubmed_file)
mart = pd.read_csv(mart_file, sep="\t")  # mart_biotool có dạng tab-separated

# B2: Hàm tìm PubmedID từ PubMed

def get_pubmed_info(gene):
    symbol_match = pubmed[pubmed['Symbol'] == gene]
    alias_match = pubmed[pubmed['Alias symbol'].fillna('').str.split(', ').apply(lambda x: gene in x)]
    if not symbol_match.empty:
        row = symbol_match.iloc[0]
        return row['PubmedID']
    elif not alias_match.empty:
        row = alias_match.iloc[0]
        return row['PubmedID']
    else:
        return ""

# B2.1: Hàm tìm Ensembl ID từ PubMed và mart_biotool

def get_ensembl_id(gene, aliases):
    # Ưu tiên lấy từ PubMed
    symbol_match = pubmed[pubmed['Symbol'] == gene]
    alias_match = pubmed[pubmed['Alias symbol'].fillna('').str.split(', ').apply(lambda x: gene in x)]
    if not symbol_match.empty:
        return symbol_match.iloc[0]['Ensembl ID']
    elif not alias_match.empty:
        return alias_match.iloc[0]['Ensembl ID']
    else:
        # Nếu không có trong PubMed, kiểm tra mart_biotool với gene và aliases
        possible_names = [gene] + aliases
        for name in possible_names:
            mart_match = mart[mart['Gene name'] == name]
            if not mart_match.empty:
                return mart_match.iloc[0]['Gene stable ID']
        return ""  # Giữ nguyên Alpha_Node nếu không tìm được

# B3: Hàm đối chiếu OncoKB
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

# B4: Tạo bảng kết quả
output = []
for _, row in model_result.sort_values(by="Total_Support", ascending=False).iterrows():
    gene = row['Alpha_Node']
    total_support = row['Total_Support']

    symbol, alias, is_oncogene, is_tsg, in_oncokb = check_oncokb(gene)
    pubmed_id = get_pubmed_info(gene)
    ensembl_id = get_ensembl_id(symbol, alias.split(', ') if isinstance(alias, str) else [])

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

# B5: Lưu file kết quả
output_name = os.path.basename(model_file).replace(".csv", "_Annotated.csv")
os.makedirs("../final_results_3", exist_ok=True)
output_df.to_csv(f"../final_results_3/{output_name}", index=False)
print(f"✅ Đã lưu file kết quả vào ../final_results_3/{output_name}")
