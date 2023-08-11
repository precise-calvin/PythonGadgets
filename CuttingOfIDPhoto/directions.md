# 证件照区域识别裁剪说明：
1. 本程序使用python3编写，使用前请确保已经安装python3环境.
2. 本程序使用了第三方库:`cv2`与`face_recognition`，使用前请确保已安装.  
    安装方法：  
     1. 命令行运行 pip install opencv-python
     2. 命令行运行 pip install face_recognition
3. 1. `Cutting of ID Photos`文件 实现批量识别图片中的人脸区域并裁剪后输出
   2. `Cutting of ID Photos And Rename`文件 实现上述功能的同时，将裁剪后的图片按照顺序重命名
4. 代码逻辑详细介绍请看代码文件开头。