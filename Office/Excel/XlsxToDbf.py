import pandas as pd
import dbf
import re

# Excel文件路径
xlsx_file = '/Users/calvin/Desktop/新生学籍异动/转专业/转专业dbf模板.xlsx'
# 输出的 DBF 文件路径
dbf_file = '/Users/calvin/Desktop/output_file.dbf'

# 读取 Excel 文件
df = pd.read_excel(xlsx_file, sheet_name='Sheet1')

def generate_field_name(original, existing_names):
    """
    生成合法且唯一的 DBF 字段名，规则：
      - 只允许字母、数字和下划线
      - 必须以字母开头，否则在前面添加 'F_'
      - 最大长度为 10 个字符
      - 如果重复则追加数字后缀
    """
    name = str(original)
    # 替换非法字符
    name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    # 如果不以字母开头，添加前缀
    if not name or not name[0].isalpha():
        name = "F_" + name
    if not name:
        name = "FIELD"
    # 截取前10个字符作为初始候选字段名
    candidate = name[:10]
    suffix = 1
    # 如果候选字段名已经存在，则追加数字后缀，确保不超过10个字符
    while candidate in existing_names:
        # 确保加后缀后不超过10个字符
        base = name[:10 - len(str(suffix))]
        candidate = base + str(suffix)
        suffix += 1
    return candidate

# 生成原始Excel列名到合法DBF字段名的映射
existing_names = set()
dbf_columns = {}
for col in df.columns:
    new_name = generate_field_name(col, existing_names)
    dbf_columns[col] = new_name
    existing_names.add(new_name)

# 构造字段规格字符串，格式示例："FIELD1 C(255);FIELD2 C(255);..."
field_specs = ';'.join([f"{dbf_columns[col]} C(255)" for col in df.columns])

# 创建新的 DBF 文件，指定 codepage 为 utf8
dbf_table = dbf.Table(dbf_file, field_specs, codepage='utf8')
dbf_table.open(mode=dbf.READ_WRITE)

# 将 Excel 数据逐行插入 DBF 文件
for _, row in df.iterrows():
    record_data = {dbf_columns[col]: str(row[col]) if pd.notna(row[col]) else '' for col in df.columns}
    dbf_table.append(record_data)

# 关闭 DBF 文件
dbf_table.close()

print(f"Excel 文件已成功转换为 DBF 文件，保存路径为 {dbf_file}")
