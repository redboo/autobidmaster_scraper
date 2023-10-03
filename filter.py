import requests
from loguru import logger


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
        logger.error(f"Ошибка запроса. Статус код: {response.status_code}")
        return None


if __name__ == "__main__":
    log_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    logger.add(sink=lambda message: print(message), level="DEBUG", format=log_format, colorize=True, enqueue=True)

    autobidmaster_data = get_autobidmaster_data()

    if autobidmaster_data:
        logger.info("Данные успешно получены: %s", autobidmaster_data)
    else:
        logger.error("Не удалось получить данные с сайта.")
