import pandas as pd
from dbfread import DBF

# 读取 Excel 文件
excel_file_path = '/Users/calvin/Desktop/test11212.xlsx'
df = pd.read_excel(excel_file_path)

# 保存为 DBF 文件
dbf_file_path = '/Users/calvin/Desktop/file.dbf'
df.to_dbf(dbf_file_path, index=False)

# 或者使用 dbfread 库加载并验证 DBF 文件
dbf_data = DBF(dbf_file_path)
for record in dbf_data:
    print(record)
