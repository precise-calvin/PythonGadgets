import pandas as pd
from dbfread import DBF

# 读取 .dbf 文件
dbf_file = '/Users/calvin/Desktop/stru_blrxzg.dbf'
# Excel文件路径
xlsx_file = '/Users/calvin/Desktop/output_file.xlsx'
table = DBF(dbf_file)

# 将 dbf 文件转换为 DataFrame
records = list(table)  # 获取所有记录
df = pd.DataFrame(records)

with pd.ExcelWriter(xlsx_file, engine='xlsxwriter') as writer:
    # 将 DataFrame 写入 Excel
    df.to_excel(writer, index=False, sheet_name='Sheet1')

    # 设置所有单元格格式为文本
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    # 遍历每列，设置格式
    for col_num, column in enumerate(df.columns.values):
        worksheet.set_column(col_num, col_num, 20, workbook.add_format({'num_format': '@'}))

print(f"DBF 文件已成功转换为 {xlsx_file}")