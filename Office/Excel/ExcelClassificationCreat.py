import pandas as pd

def split_excel_by_column(input_file, output_folder, column_name):
    # 读取Excel文件
    df = pd.read_excel(input_file)

    # 按照指定列的数值进行分类
    groups = df.groupby(column_name)

    # 遍历每个分类
    for group_name, group_data in groups:
        # 创建一个新的Excel文件
        output_file = f"{output_folder}/{group_name}.xlsx"
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            # 将当前分类的数据写入新的Excel工作表中
            group_data.to_excel(writer, index=False, float_format='%.0f')

# 输入文件路径
input_file_path = '/Users/calvin/Desktop/sourse.xlsx'

# 输出文件夹路径
output_folder_path = '/Users/calvin/Desktop/outputdir'

# 指定按照哪一列分类
column_name_to_split = '校外教学点'


# 调用函数进行分类和复制
split_excel_by_column(input_file_path, output_folder_path, column_name_to_split)



