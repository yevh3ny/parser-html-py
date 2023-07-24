import requests
from bs4 import BeautifulSoup

# URL страницы, которую нужно спарсить
url = "https://viyar.ua/catalog/cleaf_spigato_spigato_fa91_kora_2800kh2070kh18_18_6mm/"


def parse_page(url):
    try:
        # Загружаем HTML-код страницы с помощью библиотеки requests
        response = requests.get(url)
        response.raise_for_status()

        # Создаем объект BeautifulSoup для парсинга HTML
        soup = BeautifulSoup(response.content, "html.parser")

        # Начинаем парсинг данных со страницы
        # В данном примере предположим, что данные, которые вам нужны, находятся в определенных элементах.

        # Пример: извлечение названия продукта
        product_name = soup.find("h1", class_="product-name").text.strip()

        # Пример: извлечение цены продукта
        price = soup.find("span", class_="price").text.strip()

        # Пример: извлечение описания продукта
        description = soup.find("div", class_="description").text.strip()

        # Пример: извлечение изображения продукта
        image_url = soup.find("div", class_="product-item__gallery").img["src"]

        # Пример: извлечение характеристик продукта
        characteristics = {}
        char_rows = soup.find_all(
            "div", class_="product-item__characteristics__row")
        for row in char_rows:
            key = row.find(
                "span", class_="product-item__characteristics__key").text.strip()
            value = row.find(
                "span", class_="product-item__characteristics__value").text.strip()
            characteristics[key] = value

        # Возвращаем полученные данные
        return {
            "product_name": product_name,
            "price": price,
            "description": description,
            "image_url": image_url,
            "characteristics": characteristics,
        }

    except requests.exceptions.RequestException as e:
        print("Ошибка при загрузке страницы:", e)
        return None


# Вызываем функцию для парсинга страницы
parsed_data = parse_page(url)

# Выводим результаты парсинга
if parsed_data:
    print("Название продукта:", parsed_data["product_name"])
    print("Цена:", parsed_data["price"])
    print("Описание:", parsed_data["description"])
    print("Изображение:", parsed_data["image_url"])
    print("Характеристики:")
    for key, value in parsed_data["characteristics"].items():
        print(f"{key}: {value}")
