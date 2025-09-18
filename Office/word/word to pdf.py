import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

def convert_to_pdf_unoconv(input_file):
    """使用 unoconv 将 Word 文件转换为 PDF"""
    command = ["unoconv", "-f", "pdf", input_file]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output_file = os.path.splitext(input_file)[0] + ".pdf"
    print(f"已转换: {os.path.basename(input_file)} -> {os.path.basename(output_file)}")

def convert_docs_in_folder(folder_path):
    """并行处理 .doc 和 .docx 文件的转换"""
    files_to_convert = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith((".doc", ".docx"))]

    # 获取CPU核心数并设置最大线程数
    max_threads = multiprocessing.cpu_count() * 4  # 设置为 CPU 核心数的 2 倍
    print(f"使用 {max_threads} 个并行线程进行转换")

    # 使用线程池并行处理文件转换，设置最大线程数
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        executor.map(convert_to_pdf_unoconv, files_to_convert)

    print("所有文件已转换完成！")

if __name__ == "__main__":
    folder_path = input("请输入文件夹路径：")
    if os.path.isdir(folder_path):
        convert_docs_in_folder(folder_path)
    else:
        print("提供的路径不是有效的文件夹。")
