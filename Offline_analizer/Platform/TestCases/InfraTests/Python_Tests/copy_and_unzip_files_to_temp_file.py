import os
import shutil
import py7zr
import tempfile

"""
Script Name: copy_and_unzip_files_to_temp_file.py
Description: This script is designed to copy and unzip files to a temporary directory.
Author: [Your Name]
Date: [Date]
"""


def copy_file_to_temp(src_file):
    """
    Copies a file to a specified temporary directory.
    :param src_file: Path to the source file.
    :return: Path to the copied file in the specified temporary directory.
    """
    temp_dir = r"C:\TOOLS\Gen6_parcer\temp_folder"
    
    # Ensure the directory exists
    os.makedirs(temp_dir, exist_ok=True)
    
    # Copy the file to the temp directory
    dest_file = os.path.join(temp_dir, os.path.basename(src_file))
    shutil.copy(src_file, dest_file)
    return dest_file

def unzip_file(zip_file, extract_to=None):
    """
    Unzips a 7z file to a specified directory or the same directory as the .7z file.
    :param zip_file: Path to the 7z file.
    :param extract_to: Directory to extract files to. If None, the same directory as the .7z file is used.
    :return: Path to the directory where files were extracted.
    """
    if extract_to is None:
        # Use the same directory as the .7z file
        extract_to = os.path.dirname(zip_file)
    
    # Ensure the extraction directory exists
    os.makedirs(extract_to, exist_ok=True)
    
    # Extract the .7z file
    with py7zr.SevenZipFile(zip_file, mode='r') as archive:
        archive.extractall(path=extract_to)
    
    return extract_to

def main():
    """
    Main function to demonstrate file copying and unzipping.
    """
    # Example usage
    input_folder = r"\\abtvdfs2.de.bosch.com\ismdfs\ida\abt\radar\PJ_RA6\01_MeasData\01_Release\Alfa14.1\RA6_Alfa_14_1_RC1\250407_Alfa14_1_3R_13Mix_E220d_FCFLFR"  # Replace with your folder path
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            src_file = os.path.join(root, file)
            if file.endswith('MF4.7z'):
                try:
                    copied_file = copy_file_to_temp(src_file)
                    print(f"File copied to: {copied_file}")

                    extracted_dir = unzip_file(copied_file)
                    print(f"Files extracted to: {extracted_dir}")
                except Exception as e:
                    print(f"An error occurred with file {src_file}: {e}")

print("script completed!")

if __name__ == "__main__":
    main()