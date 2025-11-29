
import os
import django
import requests
from bs4 import BeautifulSoup
from time import sleep
import re
from urllib.parse import urlparse
from PIL import Image
import random
import string
from django.core.files import File

# 1. Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "castersinox.settings")
django.setup()

# 2. Import Django models
from core.models import Category, SubCategory, Product, ProductImage

headers = {"User-Agent": "Mozilla/5.0"}
session_requests = requests.Session()
URL_IN_STYLE = re.compile(r"url\(['\"]?(.*?)['\"]?\)")

def fetch_links(page_url, selector, pause=1):
    resp = session_requests.get(page_url, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    sleep(pause)
    return [a["href"] for el in soup.select(selector) if (a := el.find("a", href=True))]

def fetch_products(page_url, pause=1):
    resp = session_requests.get(page_url, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    sleep(pause)
    products = []
    for sec in soup.select("section.elementor-section"):
        title_el = sec.select_one("h4.elementor-heading-title")
        if not title_el:
            continue
        desc = sec.select_one("div.elementor-widget-text-editor p")
        features = [li.get_text(strip=True)
                    for li in sec.select("div.elementor-widget-toggle .elementor-tab-content ul li")]
        imgs = []
        if (img := sec.select_one("div.elementor-widget-image img")) and img.get("src"):
            imgs.append(img["src"])
        for slide in sec.select("div.elementor-carousel-image"):
            if m := URL_IN_STYLE.search(slide.get("style", "")):
                imgs.append(m.group(1))
        products.append({
            "title": title_el.get_text(strip=True),
            "description": desc.get_text(strip=True) if desc else "",
            "features": features,
            "images": imgs
        })
    return products

def get_category_name(url: str) -> str:
    segment = urlparse(url).path.rstrip("/").rsplit("/", 1)[-1]
    return segment.replace("-", " ").title()

def generate_random_digits(length=8):
    return ''.join(random.choices(string.digits, k=length))

def process_and_save_image(image_url: str, product_id: int, image_index: int) -> str:
    products_dir = "products"
    extra_dir = os.path.join(products_dir, "extra")
    product_folder = os.path.join(extra_dir, str(product_id))
    os.makedirs(product_folder, exist_ok=True)
    try:
        resp = requests.get(image_url, stream=True)
        resp.raise_for_status()
        img = Image.open(resp.raw)
        img = img.convert("RGBA")
        w, h = img.size
        target_w, target_h = 580, 760
        if h > w:
            new_h = target_h
            new_w = int(w * (new_h / h))
        else:
            new_w = target_w
            new_h = int(h * (new_w / w))
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
        canvas.paste(img, ((target_w - new_w)//2, (target_h - new_h)//2))
        filename = f"{generate_random_digits()}-{image_index}.png"
        path = os.path.join(product_folder, filename)
        canvas.save(path, "PNG")
        return path
    except Exception as e:
        print(f"Error processing image {image_url}: {e}")
        return None

def main():
    main_links = fetch_links(
        "https://casters.ro/produse/utilaje-carmangerie/",
        'div[class*="elementor-element-"].e-con-full.e-flex.e-con.e-child'
    )
    for main_url in main_links:
        cat_name = get_category_name(main_url)
        category, _ = Category.objects.get_or_create(name=cat_name)

        sub_links = fetch_links(main_url, "div.elementor-widget-call-to-action")
        urls_to_scrape = [main_url] + sub_links

        for url in urls_to_scrape:
            sub = None
            if url != main_url:
                sub_name = get_category_name(url)
                sub, _ = SubCategory.objects.get_or_create(
                    name=sub_name, defaults={"category": category})
            for pdata in fetch_products(url):
                product, created = Product.objects.get_or_create(
                    name=pdata["title"],
                    defaults={
                        "description": pdata["description"],
                        "features": pdata["features"],
                        "category": category,
                        "subcategory": sub
                    }
                )
                if not created:
                    product.description = pdata["description"]
                    product.features = pdata["features"]
                    product.category = category
                    product.subcategory = sub
                    product.save()

                for idx, img_url in enumerate(pdata["images"], 1):
                    img_path = process_and_save_image(img_url, product.id, idx)
                    if img_path:
                        with open(img_path, "rb") as f:
                            django_file = File(f)
                            pi = ProductImage(product=product)
                            pi.image.save(os.path.basename(img_path), django_file, save=True)

if __name__ == "__main__":
    main()
