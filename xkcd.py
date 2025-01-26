import requests
import os
import re
from PIL import Image, ImageOps

class Downloader:
    def __init__(self, start, end, invert_colours):
        self.start = start
        self.end = end
        self.invert_colours = invert_colours
        self.image_path = None

    def keywords(self, start, end):
        if start == "latest" or end == "latest":
            latest_url = "https://xkcd.com/info.0.json"
            response = requests.get(latest_url)
            response.raise_for_status()
            latest_comic = response.json()['num']
            if start == "latest":
                start = latest_comic
            else:
                start = int(start)
            if end == "latest":
                end = latest_comic
            else:
                end = int(end)
        else:
            start = int(start)
            end = int(end)
        return start, end
    
    def sanitise(self, title):
        title = title.lower()
        title = re.sub(r'[^a-zA-Z0-9_]', '', title)
        return title

    def rescale(self):
        with Image.open(self.image_path) as img:
            if img.height > 500:
                aspect_ratio = img.width / img.height
                width = int(500 * aspect_ratio)
                resized_img = img.resize((width, 500), Image.LANCZOS)
            else:
                resized_img = img
            final_img = Image.new("RGB", (1920, 1080), (255, 255, 255))
            offset = (1920 - resized_img.width) // 2
            final_img.paste(resized_img, (offset, 290))
            final_img.save(self.image_path)

    def invert(self):
        with Image.open(self.image_path) as img:
            img = img.convert("RGB")
            inverted_img = ImageOps.invert(img)
            inverted_img.save(self.image_path)

    def download(self):
        os.makedirs('xkcd', exist_ok=True)
        for xkcd_number in range(self.start, self.end + 1):
            try:
                url = f"https://xkcd.com/{xkcd_number}/info.0.json"
                response = requests.get(url)
                response.raise_for_status()
                xkcd_data = response.json()
                xkcd_title = xkcd_data['title']
                xkcd_img_url = xkcd_data['img']
                img_response = requests.get(xkcd_img_url)
                img_response.raise_for_status()
                self.image_path = os.path.join('xkcd', f"{xkcd_number} - {self.sanitise(xkcd_title)}_dark.png")
                with open(self.image_path, 'wb') as img_file:
                    img_file.write(img_response.content)
                self.rescale()
                if self.invert_colours:
                    self.invert()
                print(f"Downloaded #{xkcd_number}: {xkcd_title}")
            except Exception as e:
                print(f"Failed to process #{xkcd_number}: {e}")

if __name__ == "__main__":
    start = input("Start: ")
    end = input("End: ")
    invert_colours = input("Dark mode [y/n]: ").strip().lower() == "y"
    downloader = Downloader(start, end, invert_colours)
    downloader.start, downloader.end = downloader.keywords(start, end)
    downloader.download()
