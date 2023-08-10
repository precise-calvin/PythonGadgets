# 中文转拼音说明：
1. 本程序使用了第三方库pypinyin，使用前请确保已经安装pypinyin库.(安装方法：命令行运行 pip install pypinyin)

---
第五行的style参数有以下几种样式可以选择:
```
NORMAL - 普通风格,输出汉字拼音。默认风格。
TONE - 输出汉字拼音与声调。比如:zhōng
TONE2 - 输出汉字拼音与声调数字。比如:zho1ng
TONE3 - 输出汉语拼音与声调标记数字。比如:zhong1
INITIALS - 只输出汉字拼音首字母。比如:z
FIRST_LETTER - 只输出拼音的第一个字母。比如:z
FINALS - 输出汉字拼音 finals 部分。比如:ong
FINALS_TONE - 输出 finals 及其声调。比如:ong1
FINALS_TONE2 - 输出 finals 及声调数字。比如:o1ng
FINALS_TONE3 - 输出 finals 及声调数字。比如:ong1
```
---
首字母大写格式有以下几种样式可以选择:
修改第23行的uppercaseLogo = ‘1’改为以下几种样式:
```
‘ 1 ’: 默认样式，不做处理
‘ 2 ’: 每个单词的首字母全都大写
’ 3 ‘: 首字母大写，其余字母小写
```