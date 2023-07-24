import requests
from bs4 import BeautifulSoup
import csv


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

        return {
            "article": article,
            "product_name": product_name,  # Заменена переменная name на product_name
            "characteristics": characteristics,
            "price": price,
            "unit": unit,
        }

    except requests.exceptions.RequestException as e:
        print("Ошибка при загрузке страницы:", e)
        return None


# Чтение url из файла url.txt
with open("url.txt", "r") as f:
    urls = f.read().splitlines()

# Создание файла csv для записи результатов
with open("data.csv", "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["Код товара", "Название продукта",
                  "Единица измерения", "Цена", "Длина", "Ширина", "Толщина"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
    writer.writeheader()

    for url in urls:
        # Парсинг данных для каждого url
        parsed_data = parse_page(url)

        if parsed_data:
            # Запись результатов в файл csv
            writer.writerow({
                "Код товара": parsed_data["article"] if parsed_data else "",
                "Название продукта": parsed_data["product_name"] if parsed_data else "",
                "Единица измерения": parsed_data["unit"].replace("₴/", "") if parsed_data else "",
                "Цена": parsed_data["price"] if parsed_data else "",
                "Длина": parsed_data["characteristics"].get("length", "") if parsed_data else "",
                "Ширина": parsed_data["characteristics"].get("width", "") if parsed_data else "",
                "Толщина": parsed_data["characteristics"].get("depth", "") if parsed_data else "",
            })
