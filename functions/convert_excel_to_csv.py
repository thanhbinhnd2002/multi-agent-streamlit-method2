# 📌 Chuyển đổi file Excel OncoKB sang CSV để tiện xử lý
# 📥 Input: Cancer gene OncoKB30012025.xlsx
# 📤 Output: Cancer gene OncoKB30012025.csv

import pandas as pd
import os

# Đường dẫn tới file Excel (đã upload sẵn)
excel_file = "../HGRN.xlsx"

# Đọc dữ liệu từ Excel (chỉ lấy sheet đầu tiên)
df = pd.read_excel(excel_file)

# Xuất ra file CSV cùng tên
csv_file = os.path.splitext(excel_file)[0] + ".csv"
df.to_csv(csv_file, index=False)

print(f"✅ Đã chuyển đổi thành công! File CSV lưu tại: {csv_file}")
