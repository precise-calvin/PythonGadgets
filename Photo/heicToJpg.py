import os
import subprocess

def heic_to_jpg_folder(input_folder, output_folder):
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Iterate through all files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".heic") or filename.endswith(".HEIC"):
            # Construct the input and output file paths
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, os.path.splitext(filename)[0] + ".jpg")

            # Call heif-convert to convert HEIC to JPG
            subprocess.run(["heif-convert", input_path, output_path])

# Usage example
heic_to_jpg_folder('/Users/calvin/Public/input', '/Users/calvin/Public/output')
