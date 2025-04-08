import pandas as pd
from dbfread import DBF
from chardet.universaldetector import UniversalDetector

# 自动检测文件编码
def detect_file_encoding(file_path):
    detector = UniversalDetector()
    with open(file_path, 'rb') as f:
        for line in f:
            detector.feed(line)
            if detector.done:
                break
        detector.close()
    return detector.result['encoding']

# 输入和输出文件路径
dbf_file = '/Users/calvin/Desktop/stru_blrxzg.dbf'
xlsx_file = '/Users/calvin/Desktop/output_file.xlsx'

# 检测编码
encoding = detect_file_encoding(dbf_file)
if not encoding:
    print("未检测到编码，默认使用 GBK")
    encoding = 'gbk'  # 设置默认值为 GBK
else:
    print(f"检测到的文件编码：{encoding}")

# 强制测试指定可能的编码（可选）
encoding = 'gbk'

try:
    # 读取 .dbf 文件
    table = DBF(dbf_file, encoding=encoding)
    records = list(table)  # 获取所有记录
    df = pd.DataFrame(records)

    # 将 DataFrame 写入 Excel 文件
    with pd.ExcelWriter(xlsx_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')

        # 设置所有单元格格式为文本
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        for col_num, column in enumerate(df.columns.values):
            worksheet.set_column(col_num, col_num, 20, workbook.add_format({'num_format': '@'}))

    print(f"DBF 文件已成功转换为 {xlsx_file}")

except UnicodeDecodeError as e:
    print(f"解码错误，请尝试手动指定编码！错误详情：{e}")
