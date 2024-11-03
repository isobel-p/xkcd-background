import requests
import os
import string
import re
from PIL import Image

def sanitise(title):
    title = title.lower()
    title = title.translate(str.maketrans('', '', string.punctuation))
    title = title.replace(' ', '_')
    title = re.sub(r'[^a-zA-Z0-9_]', '', title)
    return title

def rescale(image_path):
    with Image.open(image_path) as img:
        aspect_ratio = img.width / img.height
        width = int(500 * aspect_ratio)
        resized_img = img.resize((width, 500), Image.LANCZOS)
        final_img = Image.new("RGB", (1920, 1080), (255, 255, 255))
        offset = (1920 - width) // 2
        final_img.paste(resized_img, (offset, 290))
        final_img.save(image_path)
        print(f'Rescaled: {image_path}')

def download(xkcd_number):
    url = f"https://xkcd.com/{xkcd_number}/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    xkcd_data = response.json()
    xkcd_title = xkcd_data['title']
    xkcd_img_url = xkcd_data['img']
    img_response = requests.get(xkcd_img_url)
    img_response.raise_for_status()
    os.makedirs('xkcd', exist_ok=True)
    img_filename = os.path.join('xkcd', xkcd_img_url.split('/')[-1])
    with open(img_filename, 'wb') as img_file:
        img_file.write(img_response.content)
    rescale(f'xkcd\\{sanitise(xkcd_title)}.png')
    print(f"Downloaded #{xkcd_number}: {xkcd_title}")
    print(f"Saved to: {img_filename}")

def download_range(start, end):
    for xkcd_number in range(start, end + 1):
        download(xkcd_number)

if __name__ == "__main__":
    start = int(input("Start: "))
    end = int(input("End: "))
    download_range(start, end)
