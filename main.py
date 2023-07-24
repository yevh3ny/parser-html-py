import requests
from bs4 import BeautifulSoup
import logging

# Настройка логгирования
logging.basicConfig(filename='parser.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def parse_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        data = []
        for item in soup.select('.item'):
            article = item.select_one('.article').text.strip()
            name = item.select_one('.name').text.strip()
            group_number = item.select_one('.group-number').text.strip()
            group_name = item.select_one('.group-name').text.strip()
            unit = item.select_one('.unit').text.strip()
            cost = item.select_one('.cost').text.strip()
            coefficient = item.select_one('.coefficient').text.strip()
            length = item.select_one('.length').text.strip()
            width = item.select_one('.width').text.strip()
            thickness = item.select_one('.thickness').text.strip()

            data.append(
                f"{article};{name};{group_number};{group_name};{unit};{cost};{coefficient};{length};{width};{thickness}")

        return data
    except requests.exceptions.RequestException as e:
        # Запись ошибки в лог с дополнительной информацией
        logging.error(f"Произошла ошибка при запросе к странице: {e}")
        return []
    except Exception as ex:
        # Запись общей ошибки в лог с дополнительной информацией
        logging.exception("Произошла неизвестная ошибка при парсинге данных:")
        return []


def save_to_file(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("Артикул материала;Наименование материала;Номер группы;Наименование группы;Единица измерения;Стоимость;Коэффициент;Длина;Ширина;Толщина;\n")
        for item in data:
            f.write(item + "\n")


if __name__ == "__main__":
    url = "https://viyar.ua/ua/catalog/"  # Замените на адрес своего сайта
    output_file = "parsed_data.csv"  # Укажите имя файла для сохранения данных

    data = parse_data(url)
    if data:
        save_to_file(data, output_file)
        logging.info("Данные успешно спарсены и сохранены в файл.")
    else:
        logging.warning("Произошла ошибка при парсинге данных.")
