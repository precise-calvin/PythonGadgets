from pypinyin import pinyin, Style


def convert_to_pinyin(name):
    pinyin_list = pinyin(name, style=Style.NORMAL)
    pinyin_str = ' '.join([p[0] for p in pinyin_list])
    return pinyin_str


# 读取文件中的姓名并转换为拼音
input_filename = '/Users/calvin/Desktop/pinyin_input.txt'  # 指定输入文件路径
output_filename = '/Users/calvin/Desktop/pinyin_output.txt'  # 指定输出文件路径

with open(input_filename, 'r', encoding='utf-8') as input_file:
    names = input_file.read().splitlines()

pinyin_names = [convert_to_pinyin(name) for name in names]


print("转换为汉语拼音后的结果为：")
for pinyin_name in pinyin_names:
    print(pinyin_name)

# 写入结果到指定文件中
with open(output_filename, 'w', encoding='utf-8') as output_file:
    for pinyin_name in pinyin_names:
        output_file.write(f'{pinyin_name}\n')

print("转换为汉语拼音后的结果已写入到：", output_filename)
