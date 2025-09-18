import cv2
from PIL import Image
import os

# 处理照片，将学生的照片格式化，使其符合要求
# 要求：480x640，JPEG 格式，文件大小在 10KB 到 40KB 之间, DPI 为 300,人脸居中

def process_image(input_path, output_path):
    # 加载图像并转换为灰度
    image = cv2.imread(input_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 使用 OpenCV 的人脸检测
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) == 0:
        print(f"没有检测到人脸：{input_path}")
        return False

    # 取第一个检测到的人脸，假设只有一张脸
    x, y, w, h = faces[0]

    # 计算裁剪区域，使人脸居中
    center_x, center_y = x + w // 2, y + h // 2

    # 增大裁剪区域的宽度和高度
    crop_width = max(w * 2, 480)  # 至少保证宽度是 480
    crop_height = max(h * 2, 640)  # 至少保证高度是 640

    crop_x1 = max(center_x - crop_width // 2, 0)
    crop_y1 = max(center_y - crop_height // 2, 0)
    crop_x2 = min(center_x + crop_width // 2, image.shape[1])
    crop_y2 = min(center_y + crop_height // 2, image.shape[0])

    # 裁剪图像并调整为480x640
    cropped_image = image[crop_y1:crop_y2, crop_x1:crop_x2]
    resized_image = cv2.resize(cropped_image, (480, 640))

    # 使用 PIL 压缩并保存为 JPG
    pil_image = Image.fromarray(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB))
    quality = 100  # 初始质量设置

    # 设置 DPI，默认值为 300
    dpi = (300, 300)  # 修改 DPI 的字段

    # 调整文件大小在10KB到40KB之间
    while True:
        output = output_path
        pil_image.save(output, format='JPEG', quality=quality, dpi=dpi)  # 设置 DPI 参数
        file_size = os.path.getsize(output) / 1024  # 转换为 KB

        if 10 <= file_size <= 40:
            break
        elif file_size < 10:
            quality += 5
        else:
            quality -= 5

        if quality < 10:
            print(f"无法达到指定的文件大小要求：{output}")
            return False

    print(f"处理成功: {output}")
    return True

# 批量处理文件
input_folder = "/Users/calvin/Desktop/input"  # 输入文件夹
output_folder = "/Users/calvin/Desktop/output"  # 输出文件夹

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

for filename in os.listdir(input_folder):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, os.path.splitext(filename)[0] + ".jpg")
        process_image(input_path, output_path)
