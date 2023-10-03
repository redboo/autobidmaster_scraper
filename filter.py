import logging

import requests

# Настройка логгирования
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)


def get_autobidmaster_data():
    headers = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    }

    reqUrl = "https://www.autobidmaster.com/ru/data/v2/inventory/search/filters?custom_search=featured-run_and_drive"

    payload = ""

    response = requests.get(reqUrl, data=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Ошибка запроса. Статус код: {response.status_code}")
        return None


if __name__ == "__main__":
    autobidmaster_data = get_autobidmaster_data()

    if autobidmaster_data:
        # logging.info("Данные успешно получены: %s", autobidmaster_data)
        logging.info("Данные успешно получены: ")
    else:
        logging.error("Не удалось получить данные с сайта.")
