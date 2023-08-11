import cv2
import face_recognition
import os

# 介绍：
# 1.遍历指定文件夹,读取jpg/png/jpeg格式的图片文件,保存图片路径到列表。
# 2.对图片路径列表排序,确保顺序与文件名一致。
# 3.循环读取每张原始图片,使用OpenCV检测人脸区域。
# 4.如果检测到人脸,则计算人脸坐标,根据坐标裁剪图像。
# 5.调整裁剪图像大小为统一尺寸300x400。
# 6.生成输出图片的路径默认为读取照片文件夹下创建的‘output’文件夹。


# 指定文件夹路径读取证件照片
folder_path = '/Users/calvin/Desktop/test/'

# 初始化一个空列表用来保存图片路径
img_path_list = [] 

# 定义文件名索引
i = 0

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
    cv2.imwrite(folder_path + 'output/' + file_name_without_ext + '.jpg', face_img_resized)

    # 保存结果图片
    print('源文件名：' + file_path + '，裁剪后的文件名：' + folder_path + 'output/' + file_name_without_ext + '.jpg' + '已保存')

