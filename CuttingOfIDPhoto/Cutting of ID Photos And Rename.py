import cv2
import face_recognition
import os

# 介绍：
# 从文本文件中读取身份证号,并将身份证号作为图片名称保存，以此来解决裁剪后的图片顺序和身份证号顺序不一致的问题。

# 1.读取指定文件夹下的图片文件路径。
# 2.从文本文件中读取身份证号,保存到名字列表。
# 3.对图片路径排序,保证顺序一致。
# 4.遍历图片,读取身份证号并检查是否重复。
# 5.如果发现重复身份证号,则打印日志并跳过当前图片的裁剪。
# 6.否则调用OpenCV进行人脸检测、裁剪、调整大小。
# 7.构造输出图片路径和名称,使用身份证号作为图片名称保存。
# 8.打印裁剪后图片的保存路径。

# 指定文件夹路径读取证件照片
folder_path = '/Users/calvin/Desktop/test/'

# 初始化一个空列表用来保存图片路径
img_path_list = [] 

#初始化一个空列表用来保存图片名字
img_name_list = []

# 定义文件名索引
i = 0

# 读取/Users/calvin/Desktop/imagename.txt下的图片名字
with open('/Users/calvin/Desktop/imagename.txt', 'r') as f:
    for line in f.readlines():
        img_name_list.append(line.strip('\n'))

# 遍历文件夹下所有文件，将图片路径保存到列表中
for file_name in os.listdir(folder_path):
    # 拼接完整的图片路径
    img_path = os.path.join(folder_path, file_name)
    if img_path.lower().endswith('.jpg') or img_path.lower().endswith('.png') or img_path.lower().endswith('.jpeg') :
        img_path_list.append(os.path.join(folder_path, file_name))
    else:
        print(f'{img_path}不是一个图片文件')
        continue

# 对集合中的图片路径进行排序，保证图片顺序和文件名顺序一致，排序规则是文件名从小到大
img_path_list.sort()

# 遍历图片路径列表，读取图片并裁剪
for file_path in img_path_list:
    # 读取集合中的图片名字
    new_img_name = img_name_list[i]

    # 自增一下
    i = i + 1

    if img_name_list.count(new_img_name) > 1 and img_name_list.index(new_img_name) < i-1:
        print(new_img_name + '重复的身份证号，已跳过')
        continue
    
    # 检测人脸位置
    img = cv2.imread(file_path)
    locations = face_recognition.face_locations(img)
    if not locations:
      print(file_path + '未检测到人脸')
      continue

    # 获取人脸位置坐标
    top, right, bottom, left = locations[0]

    # 计算人脸宽度和高度
    width = right - left
    height = bottom - top

    # 根据人脸位置裁剪图片
    face_img = img[top - 400:bottom + 400 , left - 300 :right + 300]

    # 调整人脸大小
    face_img_resized = cv2.resize(face_img, (300, 400))

    # 去除文件名后缀并截取文件名
    file_name_without_ext = os.path.splitext(os.path.basename(file_path))[0]

    # 保存图片
    cv2.imwrite(folder_path + '/output/' + new_img_name + '.jpg', face_img_resized)

    # 打印日志
    print('源文件名：' + file_path + '，裁剪后的文件名：' + folder_path + 'output/' + new_img_name + '.jpg' + '已保存')

