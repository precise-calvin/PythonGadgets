import cv2
import face_recognition
import os
# 读取证件照片
# 指定文件夹路径 
folder_path = '/Users/calvin/Desktop/test/'

# 初始化一个空列表用来保存图片路径
img_path_list = [] 

#初始化一个空列表用来保存图片名字
img_name_list = []

# 定义文件名索引
i   =   0

# 读取/Users/calvin/Desktop/imagename.txt下的图片名字
with open('/Users/calvin/Desktop/imagename.txt', 'r') as f:
    for line in f.readlines():
        img_name_list.append(line.strip('\n'))


# 将文件夹下的图片按照名称排序
img_name_list.sort()

# 遍历文件夹下所有文件，将图片路径保存到列表中
for file_name in os.listdir(folder_path):
    # 拼接完整的图片路径
    img_path = os.path.join(folder_path, file_name)
    if img_path.lower().endswith('.jpg') or img_path.lower().endswith('.png') or img_path.lower().endswith('.jpeg') :
        img_path_list.append(os.path.join(folder_path, file_name))
    else:
        print(f'{img_path}不是一个图片文件')
        continue
    
# 遍历图片路径列表，读取图片并裁剪
for file_name in img_path_list:
    
    # 读取集合中的图片名字
    new_img_name = img_name_list[i]

    # 自增一下
    i = i + 1

    # # 拼接完整的图片路径
    # img_path = os.path.join(folder_path, file_name)
    
        # 检测人脸位置
    img = cv2.imread(file_name)
    locations = face_recognition.face_locations(img)
    if not locations:
      print(file_name + '未检测到人脸')
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

    # 保存结果图片
    print('正在保存' + file_name)
    # 去除文件后缀
    # file_name_without_ext = os.path.splitext(file_name)[0]
    cv2.imwrite(folder_path + '/output/' + new_img_name + '.jpg', face_img_resized)

