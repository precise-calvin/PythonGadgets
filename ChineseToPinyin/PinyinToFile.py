from pypinyin import pinyin, Style

def convert_to_pinyin(name,uppercaseLogo):
    pinyin_temp = pinyin(name, style=Style.NORMAL)
    # 先转为字符串
    pinyin_temp = ' '.join([p[0] for p in pinyin_temp])

    if uppercaseLogo == 2:
        #  将每一个单词的的首字母都大写
        pinyin_temp = pinyin_temp.title()
    elif uppercaseLogo == 3:
        # 将首字母大写
        pinyin_temp = pinyin_temp.capitalize()
    return pinyin_temp


# 参数定义

input_filename = '/Users/calvin/Desktop/pinyin_input.txt'  # 指定输入文件路径

output_filename = '/Users/calvin/Desktop/pinyin_output.txt'  # 指定输出文件路径

uppercaseLogo = 1  # 是否将拼音首字母大写 1：不大写 2：全部大写 3：仅第一个大写

pinyin_names = []  # 用于存储转换后的拼音

with open(input_filename, 'r', encoding='utf-8') as input_file:
    names = input_file.read().splitlines()

for name in names:
    after_convert = convert_to_pinyin(name,uppercaseLogo)
    pinyin_names.append(after_convert)
    print(after_convert)

# 写入结果到指定文件中
with open(output_filename, 'w', encoding='utf-8') as output_file:
    for pinyin_name in pinyin_names:
        output_file.write(f'{pinyin_name}\n')

print("转换为汉语拼音后的结果已写入到：", output_filename)
