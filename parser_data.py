import requests
from bs4 import BeautifulSoup
import csv
import codecs
import re


def parse_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        article_tag = soup.find("sup", class_="product__title-sup m680--none")
        article = article_tag.find_next(
            "span", class_="product__title-sup-value").text.strip() if article_tag else ""

        product_name = soup.find(
            "h1", class_="product__title-text").text.strip() if soup.find("h1", class_="product__title-text") else ""

        characteristics = {}
        char_sections = soup.find_all(
            "div", class_="product-info__content-section")
        for section in char_sections:
            name_tag = section.find(
                "div", class_="product-info__content-substatus-name")
            value_tag = section.find("div", class_="text")
            if name_tag and value_tag:
                name = name_tag.text.strip()
                value = value_tag.text.strip()
                if name == "Довжина, мм:":
                    characteristics["length"] = value
                elif name == "Ширина, мм:":
                    characteristics["width"] = value
                elif name == "Товщина, мм:":
                    characteristics["depth"] = value

        price_tag = soup.find(
            "span", class_="product-price__cost")
        price = price_tag.text.strip() if price_tag else ""
        unit_tag = price_tag.find_next(
            "sup", class_="product-price__title-sup") if price_tag else ""
        unit = unit_tag.text.strip() if unit_tag else ""

        path_item_tag = soup.find(
            "section", class_="main__section breadcrumbs-section")
        path_item = ""
        if path_item_tag:
            path_item = "/".join([item.text.strip()
                                 for item in path_item_tag.find_all("a", class_="breadcrumbs__link")][2:])

        return {
            "article": article,
            "product_name": product_name,
            "path_item": path_item,
            "characteristics": characteristics,
            "price": price,
            "unit": unit,

        }

    except requests.exceptions.RequestException as e:
        print("Ошибка при загрузке страницы:", e)
        return None


def format_float_with_comma(number):
    return f"{number:.2f}".replace(".", ",")


def extract_texture(product_name):

    pattern = r"\b(?:[A-Za-z]{1,}\s*\d{1,}(?:\s*\w{1,})?)\b"
    matches = re.findall(pattern, product_name)
    if matches:
        texture = matches[0].replace(" ", "").replace("/", "")
        return f"{texture}.jpg"
    return ""


def extract_texture_surface(path_item):
    if path_item:
        items = path_item.split("/")
        return items[-1].strip()
    return ""


with open("url.txt", "r") as f:
    urls = f.read().splitlines()


with open("data.csv", "w", newline="", encoding="utf_8_sig") as csvfile:
    fieldnames = ["Артикул материала", "Наименование материала", "Наименование группы",
                  "Единица измерения", "Стоимость", "Длина", "Ширина", "Толщина", "Обозначение", "Текстура", "Толщина2"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
    writer.writeheader()

    for url in urls:

        parsed_data = parse_page(url)

        if parsed_data:

            price = float(parsed_data["price"].replace(
                " ", "").replace(",", "."))
            length = float(parsed_data["characteristics"].get("length", "").replace(" ", "").replace(
                ",", ".")) if parsed_data["characteristics"].get("length", "") else 0.0
            width = float(parsed_data["characteristics"].get("width", "").replace(" ", "").replace(
                ",", ".")) if parsed_data["characteristics"].get("width", "") else 0.0
            depth = float(parsed_data["characteristics"].get("depth", "").replace(" ", "").replace(
                ",", ".")) if parsed_data["characteristics"].get("depth", "") else 0.0
            texture = extract_texture(parsed_data["product_name"])
            texture_surface = extract_texture_surface(parsed_data["path_item"])

            writer.writerow({
                "Артикул материала": parsed_data["article"] if parsed_data else "",
                "Наименование материала": parsed_data["product_name"] if parsed_data else "",
                "Наименование группы": parsed_data["path_item"] if parsed_data else "",
                "Единица измерения": parsed_data["unit"].replace("₴/", "") if parsed_data else "",
                "Стоимость": format_float_with_comma(price) if parsed_data else "",
                "Длина": format_float_with_comma(length) if parsed_data else "",
                "Ширина": format_float_with_comma(width) if parsed_data else "",
                "Толщина": format_float_with_comma(depth) if parsed_data else "",
                "Обозначение": format_float_with_comma(depth) + " мм" if parsed_data else "",
                "Текстура": texture_surface + "\\" + texture if texture and texture_surface else "",
                "Толщина2": format_float_with_comma(depth) if parsed_data else "",
            })
