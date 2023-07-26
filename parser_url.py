import requests
from bs4 import BeautifulSoup
import time


def get_links_from_page(url, class_name):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        links = []
        for link in soup.find_all("a", href=True, class_=class_name):
            links.append(link["href"])
        return links
    except requests.exceptions.HTTPError as e:
        print(f"Ошибка при загрузке страницы {url}: {e}")
        return []


def parse_all_urls(base_url, class_name):
    page_number = 1
    all_links = []

    url = f"{base_url}/"
    page_links = get_links_from_page(url, class_name)
    all_links.extend(page_links)

    while True:
        url = f"{base_url}/page-{page_number}/"
        page_links = get_links_from_page(url, class_name)

        if not page_links:
            break

        all_links.extend(page_links)
        page_number += 1
        # Ограничитель страниц. Если нужно парсить все страницы - закоментировать.
        if page_number > 2:
            break
        # Задержка в 1 секунду между запросами. Если задержка не нужна закоментировать.
        # time.sleep(1)

    return all_links


def choose_category():
    print("Выберите раздел из которого выполнять парсинг:")
    print("1 - Плитные материалы")
    print("2 - Мебельная фурнитура")
    print("3 - Столешницы и степанели")
    print("4 - Двери и гард.системы")
    print("5 - Стекла и зеркала")
    print("6 - Освещение для мебели")
    print("7 - Производственные услуги")

    while True:
        choice = input("Введите число от 1 до 7: ")
        if choice in ["1", "2", "3", "4", "5", "6", "7"]:
            return choice
        print("Некорректный ввод. Пожалуйста, выберите число от 1 до 7.")


category_choices = {
    "1": "https://viyar.ua/catalog/plitnye_materialy",
    "2": "https://viyar.ua/catalog/mebelnaya_furnitura",
    "3": "https://viyar.ua/ua/catalog/stoleshnitsy_stenpaneli",
    "4": "https://viyar.ua/ua/catalog/razdvizhnye_sistemy",
    "5": "https://viyar.ua/catalog/stekla_zerkala",
    "6": "https://viyar.ua/catalog/osveshchenie_dlya_mebeli",
    "7": "https://viyar.ua/catalog/uslugi",

}

choice = choose_category()
base_url = category_choices[choice]
class_name = "text text--link"
all_urls = parse_all_urls(base_url, class_name)

with open("url.txt", "w") as file:
    for url in all_urls:
        file.write("https://viyar.ua" + url + "\n")
