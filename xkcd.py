import requests
import os
import re
from PIL import Image, ImageOps

def sanitise(title):
    title = title.lower()
    title = re.sub(r'[^a-zA-Z0-9_]', '', title)
    return title

def rescale(image_path, output_path):
    with Image.open(image_path) as img:
        if img.height > 500:
            aspect_ratio = img.width / img.height
            width = int(500 * aspect_ratio)
            resized_img = img.resize((width, 500), Image.LANCZOS)
        else:
            resized_img = img
        final_img = Image.new("RGB", (1920, 1080), (255, 255, 255))
        offset = (1920 - resized_img.width) // 2
        final_img.paste(resized_img, (offset, 290))
        final_img.save(output_path)
        # print(f'Rescaled: {output_path}')

def invert(image_path, output_path):
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        inverted_img = ImageOps.invert(img)
        inverted_img.save(output_path)
        # print(f'Inverted colors: {output_path}')

def light(start, end):
    os.makedirs('xkcd', exist_ok=True)
    for xkcd_number in range(start, end + 1):
        try:
            url = f"https://xkcd.com/{xkcd_number}/info.0.json"
            response = requests.get(url)
            response.raise_for_status()
            xkcd_data = response.json()
            xkcd_title = xkcd_data['title']
            xkcd_img_url = xkcd_data['img']
            img_response = requests.get(xkcd_img_url)
            img_response.raise_for_status()
            img_filename = os.path.join('xkcd', f"{xkcd_number} - {sanitise(xkcd_title)}.png")
            with open(img_filename, 'wb') as img_file:
                img_file.write(img_response.content)
            rescale(img_filename, img_filename)
            print(f"Downloaded #{xkcd_number}: {xkcd_title}")
        except Exception as e:
            print(f"Failed to process #{xkcd_number}: {e}")
        
def dark(start, end):
    os.makedirs('xkcd_dark', exist_ok=True)
    for xkcd_number in range(start, end + 1):
        try:
            url = f"https://xkcd.com/{xkcd_number}/info.0.json"
            response = requests.get(url)
            response.raise_for_status()
            xkcd_data = response.json()
            xkcd_title = xkcd_data['title']
            xkcd_img_url = xkcd_data['img']
            img_response = requests.get(xkcd_img_url)
            img_response.raise_for_status()
            img_filename = os.path.join('xkcd_dark', f"{xkcd_number} - {sanitise(xkcd_title)}_dark.png")
            with open(img_filename, 'wb') as img_file:
                img_file.write(img_response.content)
            rescale(img_filename, img_filename)
            invert(img_filename, img_filename)
            print(f"Downloaded #{xkcd_number}: {xkcd_title}")
        except Exception as e:
            print(f"Failed to process #{xkcd_number}: {e}")

def download_range(start, end, invert):
    if invert:
        dark(start, end)
    else:
        light(start, end)
        
if __name__ == "__main__":
    start = int(input("Start: "))
    end = int(input("End: "))
    invert_colours = input("Dark mode [y/n]: ").strip().lower() == "y"
    download_range(start, end, invert_colours)
