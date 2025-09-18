import os
import pandas as pd
import glob
import warnings
import re

# 设置文件夹路径
input_folder = '/Users/calvin/Documents/安财/2025（上）/学务/学院督导/处理临时文件夹/教务系统导出名单/'
teacher_data_path = '/Users/calvin/Documents/安财/2025（上）/学务/学院督导/基准材料/处理后教师名单.xlsx'
output_folder = '/Users/calvin/Documents/安财/2025（上）/学务/学院督导/处理临时文件夹'

# 忽略警告
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

# 查找所有 Excel 文件（.xls 或 .xlsx）
excel_files = glob.glob(os.path.join(input_folder, '*.xlsx')) + glob.glob(os.path.join(input_folder, '*.xls'))

# 用于存储所有表格数据
df_list = []

# 读取每个 Excel 文件并合并
for file in excel_files:
    df = pd.read_excel(file)
    df_list.append(df)

# 合并所有 DataFrame（假设每个文件的表头一致）
combined_df = pd.concat(df_list, ignore_index=True)

# 在合并后的 DataFrame 中替换校外教学点列中的"合肥兴业教学点"为"合肥通用教学点"
combined_df['校外教学点'] = combined_df['校外教学点'].replace('合肥兴业教学点', '合肥通用教学点')
combined_df['校外教学点'] = combined_df['校外教学点'].replace(r'(.*)函授站', r'\1教学点', regex=True)


# 保存合并后的数据到一个新的 Excel 文件
merged_file_path = os.path.join(output_folder, 'merged_file.xlsx')
combined_df.to_excel(merged_file_path, index=False)

print(f"合并完成！文件已保存至 {merged_file_path}")

# 读取教师名单数据
teacher_data = pd.read_excel(teacher_data_path)

# 清理和处理教师数据
teacher_data = teacher_data[['姓名', '负责的教学点', '督导专业']].dropna(subset=['负责的教学点'])
teacher_data.columns = ['Teacher_Name', 'Teaching_Point', 'Supervised_Subjects']

# 创建教师名称到教学点的映射
teacher_to_point = dict(zip(teacher_data['Teacher_Name'], teacher_data['Teaching_Point']))

# 读取合并后的学生数据
student_data = pd.read_excel(merged_file_path)

# 定义函数，根据教学点和专业匹配负责的老师
def find_teacher(row):
    filtered_teachers = teacher_data[teacher_data['Teaching_Point'] == row['校外教学点']]

    for _, teacher_row in filtered_teachers.iterrows():
        if re.search(row['专业'], teacher_row['Supervised_Subjects']):
            return teacher_row['Teacher_Name']

    other_subjects_teacher = filtered_teachers[filtered_teachers['Supervised_Subjects'] == '其他所有专业']
    if not other_subjects_teacher.empty:
        return other_subjects_teacher.iloc[0]['Teacher_Name']

    all_subjects_teacher = filtered_teachers[filtered_teachers['Supervised_Subjects'] == '全专业']
    if not all_subjects_teacher.empty:
        return all_subjects_teacher.iloc[0]['Teacher_Name']

    return "未找到老师"

# 将函数应用到学生数据中，新增一列 'Assigned_Teacher'
student_data['Assigned_Teacher'] = student_data.apply(find_teacher, axis=1)

# 将 '实际学习时长' 和 '完成比例' 列转换为数值类型
student_data['实际学习时长'] = pd.to_numeric(student_data['实际学习时长'], errors='coerce')
student_data['完成比例'] = pd.to_numeric(student_data['完成比例'], errors='coerce')

# 计算看课比例和看课完成比例（百分比格式）以及详细信息
def calculate_ratios(group):
    total_students = len(group)
    students_with_study_time = len(group[group['实际学习时长'] > 0])
    students_completed = len(group[group['完成比例'] == 100])

    study_ratio = (students_with_study_time / total_students * 100) if total_students > 0 else 0
    completion_ratio = (students_completed / total_students * 100) if total_students > 0 else 0

    teacher_name = group['Assigned_Teacher'].iloc[0]
    teaching_point = teacher_to_point.get(teacher_name, "未知教学点")

    return pd.Series({
        '教师姓名': teacher_name,
        '所属教学点': teaching_point,
        '负责学生总数': total_students,
        '看课非0数': students_with_study_time,
        '看课完成数': students_completed,
        '看课比例': f"{study_ratio:.2f}%",
        '看课完成比例': f"{completion_ratio:.2f}%"
    })

# 计算每个老师的看课比例统计
teacher_stats = student_data.groupby('Assigned_Teacher').apply(calculate_ratios).reset_index(drop=True)

# 保存学生详情信息表和看课比例统计表
student_details_path = os.path.join(output_folder, '学生详情信息表.xlsx')
teacher_stats_path = os.path.join(output_folder, '看课比例统计表.xlsx')

student_data.to_excel(student_details_path, index=False)
teacher_stats.to_excel(teacher_stats_path, index=False)

print("分析完成，已生成两个Excel文件。")
