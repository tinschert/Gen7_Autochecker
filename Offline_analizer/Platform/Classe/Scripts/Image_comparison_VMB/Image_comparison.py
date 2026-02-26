"""
This program performs the following steps:
1. Imports necessary Python libraries.
2. Defines a function to get the latest image in a folder.
3. Defines a function to add text to an image and save it.
4. Resizes the images to the same dimensions.
5. Computes the absolute difference between the two images using OpenCV's cv2.absdiff function.
6. Blends the images with different transparency levels (0.3, 0.5, 0.7) and saves the results.
7. Saves the resulting difference image.

Required Python libraries:
- PIL (Pillow)
- os
- glob
- numpy
- cv2 (OpenCV)
"""

from PIL import Image, ImageDraw, ImageFont
import os
import glob
import numpy as np
import cv2

# Function to get the latest image in the folder
def get_latest_image(folder):
    image_files = glob.glob(os.path.join(folder, "*.png"))
    print(f"Image files found in {folder}: {image_files}")
    if not image_files:
        raise ValueError(f"No image files found in the folder {folder}.")
    latest_image = max(image_files, key=os.path.getctime)
    return latest_image

# Function to add text to an image and save it using OpenCV
def add_text_to_image(image_path, output_path, text, position="left"):
    image = cv2.imread(image_path)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.5
    font_color = (255, 255, 255)
    font_thickness = 2
    if position == "left":
        text_position = (10, image.shape[0] - 30)
    else:
        text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
        text_position = (image.shape[1] - text_size[0] - 10, image.shape[0] - 30)
    cv2.putText(image, text, text_position, font, font_scale, font_color, font_thickness)
    cv2.imwrite(output_path, image)
    print(f"Image with text saved to {output_path}")

def main_gui(vehicle_folder, vmb_folder, output_result_folder, selected_transparencies):
    """
    Main function for GUI to compare images from two folders and save the results.
    
    Parameters:
    vehicle_folder (str): Path to the folder containing vehicle images.
    vmb_folder (str): Path to the folder containing VMB images.
    output_result_folder (str): Path to the folder where output images will be saved.
    selected_transparencies (list): List of selected transparency values for image comparison.
    """
    
    image1_path = get_latest_image(vehicle_folder)
    image2_path = get_latest_image(vmb_folder)

    image1_name = os.path.basename(image1_path)
    image2_name = os.path.basename(image2_path)
    image2_base_name = image2_name.split('.')[0]
    output_folder = os.path.join(output_result_folder, image2_base_name)
    os.makedirs(output_folder, exist_ok=True)

    output_filename_base = os.path.join(output_folder, "processed_image_")

    print(f"Comparing {image1_path} with {image2_path}")

    img1 = cv2.imread(image1_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(image2_path, cv2.IMREAD_GRAYSCALE)

    if img1.shape != img2.shape:
        print(f"Resizing images to the same dimensions: {img1.shape} -> {img2.shape}")
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

    print(f"Image 1 pixel value at (0,0) before computing difference: {img1[0, 0]}")
    print(f"Image 2 pixel value at (0,0) before computing difference: {img2[0, 0]}")
    print(f"Image 1 pixel value at (100,100) before computing difference: {img1[100, 100]}")
    print(f"Image 2 pixel value at (100,100) before computing difference: {img2[100, 100]}")
    print(f"Image 1 pixel value at (200,200) before computing difference: {img1[200, 200]}")
    print(f"Image 2 pixel value at (200,200) before computing difference: {img2[200, 200]}")

    if 'Absolut diff' in selected_transparencies:
        diff = cv2.absdiff(img1, img2)

        diff_image_path = os.path.join(output_folder, "difference_image.png")
        cv2.imwrite(diff_image_path, diff)
        print(f"Difference image saved to {diff_image_path}")

        # Add text to the difference image
        diff_text = f"{image1_name} vs {image2_name} difference"
        add_text_to_image(diff_image_path, diff_image_path, diff_text, position="right")


    transperency_dict = {0.3: (0.3, 0.7),
                         0.5: (0.5, 0.5),
                         0.7: (0.7, 0.3)}

    blending_params = [transperency_dict[i] for i in selected_transparencies if i != 'Absolut diff']

    for i, (alpha, beta) in enumerate(blending_params):
        blended_image = cv2.addWeighted(img1, alpha, img2, beta, 0)
        resized_image = cv2.resize(blended_image, (1920, 1080))
        output_path = os.path.join(output_folder, f"blended_image_{alpha}.png")
        cv2.imwrite(output_path, resized_image)
        print(f"Blended image saved to {output_path}")

        # Add text to the blended image
        text = f"{image1_name} vs {image2_name} alpha {alpha}"
        add_text_to_image(output_path, output_path, text, position="right")


def main():
    folder1 = r"C:\VS Codes NT\Image comparison\Image\Vehiclepitcure"
    folder2 = r"C:\VS Codes NT\Image comparison\Image\VMBpicture"
    output_folder_base = r"C:\VS Codes NT\Image comparison\Image"

    print(f"Folder 1: {folder1}")
    print(f"Folder 2: {folder2}")

    image1_path = get_latest_image(folder1)
    image2_path = get_latest_image(folder2)

    image1_name = os.path.basename(image1_path)
    image2_name = os.path.basename(image2_path)
    image2_base_name = image2_name.split('.')[0]
    output_folder = os.path.join(output_folder_base, image2_base_name)
    os.makedirs(output_folder, exist_ok=True)

    output_filename_base = os.path.join(output_folder, "processed_image_")

    print(f"Comparing {image1_path} with {image2_path}")

    img1 = cv2.imread(image1_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(image2_path, cv2.IMREAD_GRAYSCALE)

    if img1.shape != img2.shape:
        print(f"Resizing images to the same dimensions: {img1.shape} -> {img2.shape}")
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

    print(f"Image 1 pixel value at (0,0) before computing difference: {img1[0, 0]}")
    print(f"Image 2 pixel value at (0,0) before computing difference: {img2[0, 0]}")
    print(f"Image 1 pixel value at (100,100) before computing difference: {img1[100, 100]}")
    print(f"Image 2 pixel value at (100,100) before computing difference: {img2[100, 100]}")
    print(f"Image 1 pixel value at (200,200) before computing difference: {img1[200, 200]}")
    print(f"Image 2 pixel value at (200,200) before computing difference: {img2[200, 200]}")

    diff = cv2.absdiff(img1, img2)

    diff_image_path = os.path.join(output_folder, "difference_image.png")
    cv2.imwrite(diff_image_path, diff)
    print(f"Difference image saved to {diff_image_path}")

    # Add text to the difference image
    diff_text = f"{image1_name} vs {image2_name} difference"
    add_text_to_image(diff_image_path, diff_image_path, diff_text, position="right")

    blending_params = [
        (0.3, 0.7),
        (0.5, 0.5),
        (0.7, 0.3)
    ]

    for i, (alpha, beta) in enumerate(blending_params):
        blended_image = cv2.addWeighted(img1, alpha, img2, beta, 0)
        resized_image = cv2.resize(blended_image, (1920, 1080))
        output_path = os.path.join(output_folder, f"blended_image_{alpha}.png")
        cv2.imwrite(output_path, resized_image)
        print(f"Blended image saved to {output_path}")

        # Add text to the blended image
        text = f"{image1_name} vs {image2_name} alpha {alpha}"
        add_text_to_image(output_path, output_path, text, position="right")

if __name__ == "__main__":
    main()