import os
import pandas as pd
import glob
import warnings

# 设置文件夹路径
folder_path = '/Users/calvin/Desktop/test/'

# 忽略警告
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

# 查找所有 Excel 文件（.xls 或 .xlsx）
excel_files = glob.glob(os.path.join(folder_path, '*.xlsx')) + glob.glob(os.path.join(folder_path, '*.xls'))

# 用于存储所有表格数据
df_list = []

# 读取每个 Excel 文件并合并
for file in excel_files:
    # 读取当前 Excel 文件
    df = pd.read_excel(file)
    # 将当前文件的 DataFrame 添加到列表
    df_list.append(df)

# 合并所有 DataFrame（假设每个文件的表头一致）
combined_df = pd.concat(df_list, ignore_index=True)

# 保存合并后的数据到一个新的 Excel 文件
combined_df.to_excel('/Users/calvin/Desktop/test/merged_file.xlsx', index=False)

print("合并完成！")
