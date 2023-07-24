import requests
from bs4 import BeautifulSoup
import csv
import codecs


def parse_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Извлечение article
        article_tag = soup.find("sup", class_="product__title-sup m680--none")
        article = article_tag.find_next(
            "span", class_="product__title-sup-value").text.strip() if article_tag else ""

        # Извлечение product_name (была изменена переменная name на product_name)
        product_name = soup.find(
            "h1", class_="product__title-text").text.strip() if soup.find("h1", class_="product__title-text") else ""

        # Извлечение length, width и depth
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

        # Извлечение price и unit
        price_tag = soup.find(
            "span", class_="product-price__cost")
        price = price_tag.text.strip() if price_tag else ""
        unit_tag = price_tag.find_next(
            "sup", class_="product-price__title-sup") if price_tag else ""
        unit = unit_tag.text.strip() if unit_tag else ""

        # Извлечение path_item
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


# Чтение url из файла url.txt
with open("url.txt", "r") as f:
    urls = f.read().splitlines()

# Создание файла csv для записи результатов
with open("data.csv", "w", newline="", encoding="utf_8_sig") as csvfile:
    fieldnames = ["Артикул материала", "Наименование материала", "Наименование группы",
                  "Единица измерения", "Стоимость", "Длина", "Ширина", "Толщина", "Толщина2"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
    writer.writeheader()

    for url in urls:
        # Парсинг данных для каждого url
        parsed_data = parse_page(url)

        if parsed_data:
            # Запись результатов в файл csv
            # Преобразование и форматирование чисел перед записью в файл csv
            price = float(parsed_data["price"].replace(
                " ", "").replace(",", "."))
            length = float(parsed_data["characteristics"].get("length", "").replace(" ", "").replace(
                ",", ".")) if parsed_data["characteristics"].get("length", "") else 0.0
            width = float(parsed_data["characteristics"].get("width", "").replace(" ", "").replace(
                ",", ".")) if parsed_data["characteristics"].get("width", "") else 0.0
            depth = float(parsed_data["characteristics"].get("depth", "").replace(" ", "").replace(
                ",", ".")) if parsed_data["characteristics"].get("depth", "") else 0.0
            writer.writerow({
                "Артикул материала": parsed_data["article"] if parsed_data else "",
                "Наименование материала": parsed_data["product_name"] if parsed_data else "",
                "Наименование группы": parsed_data["path_item"] if parsed_data else "",
                "Единица измерения": parsed_data["unit"].replace("₴/", "") if parsed_data else "",
                "Стоимость": format_float_with_comma(price) if parsed_data else "",
                "Длина": format_float_with_comma(length) if parsed_data else "",
                "Ширина": format_float_with_comma(width) if parsed_data else "",
                "Толщина": format_float_with_comma(depth) if parsed_data else "",
                "Толщина2": format_float_with_comma(depth) if parsed_data else "",
            })
