import argparse
import ast
import asyncio
import os
import random
import zipfile
from argparse import Namespace
from platform import system
from time import sleep

import aiohttp
import pandas as pd
from aiohttp import ClientSession
from dotenv import load_dotenv
from icecream import ic
from pandas import DataFrame
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from tqdm import tqdm

ic.disable()

load_dotenv()

EMAIL: str | None = os.getenv("EMAIL")
PASSWORD: str | None = os.getenv("PASSWORD")

DOWNLOADS_DIR = "downloads"
OUTPUT_FILE_PATH: str = os.path.join(DOWNLOADS_DIR, "data")
IMAGES_DIR: str = os.path.join(DOWNLOADS_DIR, "images")

BASE_URL = "https://www.autobidmaster.com/ru/"
PATH_TO_IMAGES = "images"


def initialize_driver() -> WebDriver:
    ic()
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver_directory: str = os.path.join(os.getcwd(), "driver")
    chromedriver_filename: str = "chromedriver.exe" if system() == "Windows" else "chromedriver"
    chromedriver_path: str = os.path.join(driver_directory, chromedriver_filename)

    service = ChromeService(executable_path=chromedriver_path)
    return webdriver.Chrome(service=service, options=options)


def save_to_file(dataframe: DataFrame, output_file_path: str) -> None:
    ic()
    extension: str = output_file_path.split(".")[-1].lower()

    if extension == "csv":
        dataframe.to_csv(output_file_path, index=False, encoding="utf-8")
    elif extension.lower() in {"excel", "xls", "xlsx"}:
        dataframe.to_excel(output_file_path, index=False)
    else:
        print(f"Неподдерживаемый формат файла: {extension}")
        raise


def fetch_data(driver: WebDriver, filter_params: dict[str, str | int], pages: int) -> DataFrame:
    ic()
    page = 1
    all_data = []

    progress_bar = tqdm(total=pages, desc="Скачивание страниц с данными", unit="page")
    while page < pages + 1:
        data_search_url: str = (
            f"{BASE_URL}data/v2/inventory/search?custom_search=quickpick-runs-and-drives%2F"
            f"year-{filter_params['year_range']}%2F&size={filter_params['page_size']}"
            f"&page={page}&sort={filter_params['sort_by']}&order={filter_params['sort_order']}"
        )

        driver.get(data_search_url)
        json_data = driver.execute_script("return JSON.parse(document.body.innerText);")

        total_cars = json_data.get("total", 0)
        all_data.extend(json_data.get("lots", []))

        page += 1
        if page * filter_params["page_size"] > total_cars:
            break

        progress_bar.update(1)

        sleep(random.uniform(1.0, 3.0))

    progress_bar.close()
    return pd.DataFrame(all_data)


def process_dataframe(df: DataFrame) -> DataFrame:
    ic()
    columns_to_keep: list[str] = [
        "vehicleCategory",
        "year",
        "make",
        "model",
        "modelGroup",
        "vin",
        "color",
        "description",
        "images",
        "primaryDamage",
        "secondaryDamage",
        "title",
        "odometerType",
        "odometerBrand",
        "engineSize",
        "drive",
        "transmission",
        "fuel",
        "id",
        "odometer",
        "cylinders",
        "saleStatusString",
        "locationName",
        "sold",
        "largeImage",
        "currentBid",
    ]

    try:
        df = df[columns_to_keep]
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        raise

    return df


async def download_image(session: ClientSession, image_url: str, file_path: str) -> None:
    async with session.get(image_url) as response:
        with open(file_path, "wb") as f:
            while True:
                chunk: bytes = await response.content.read(8192)
                if not chunk:
                    break
                f.write(chunk)


async def create_zip_archive(downloaded_files: list[str], output_folder: str) -> str:
    ic()
    zip_file_path: str = os.path.join(DOWNLOADS_DIR, "images.zip")

    if os.path.exists(zip_file_path):
        os.remove(zip_file_path)

    with zipfile.ZipFile(zip_file_path, "w") as zipf:
        for file_path in downloaded_files:
            zipf.write(file_path, arcname=os.path.join(output_folder, os.path.basename(file_path)))

    return os.path.abspath(zip_file_path)


async def download_images(images: list[str], output_folder: str = IMAGES_DIR) -> None:
    ic()
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    downloaded_files: list[str] = []

    async with aiohttp.ClientSession() as session:
        tasks = []
        for image_url in tqdm(images, desc="Скачивание изображений", unit="image"):
            file_name: str = os.path.join(output_folder, f"{image_url.split('/')[-1]}")
            downloaded_files.append(file_name)
            if not os.path.exists(file_name):
                tasks.append(download_image(session, image_url, file_name))

        await asyncio.gather(*tasks)

    output_archive: str = await create_zip_archive(downloaded_files, PATH_TO_IMAGES)

    print(f"{len(downloaded_files)} изображений добавлены в архив: {output_archive}")


def process_images(images: str) -> list[str]:
    def get_image_url(item) -> str:
        return item["hdr"] if item["hdr"] is not None else item["full"]

    return [get_image_url(item) for item in ast.literal_eval(images)]


def process_images_column(output_file_path: str) -> list[str]:
    ic()
    if output_file_path.lower().endswith(".csv"):
        df: DataFrame = pd.read_csv(output_file_path)
    elif output_file_path.lower().endswith(".xlsx") or output_file_path.lower().endswith(".xls"):
        df: DataFrame = pd.read_excel(output_file_path)
    else:
        print(f"Неподдерживаемый формат файла: {output_file_path}")
        raise

    df["images"] = df["images"].apply(process_images)
    all_images: list[str] = [image for sublist in df["images"] for image in sublist]

    df["images"] = df["images"].apply(
        lambda images: [f"{PATH_TO_IMAGES}/{os.path.basename(image_url)}" for image_url in images]
    )

    save_to_file(df, output_file_path)

    return all_images


async def main(pages: int, file_format: str) -> None:
    ic(pages, file_format)

    if not os.path.exists(DOWNLOADS_DIR):
        os.makedirs(DOWNLOADS_DIR)

    output_file: str = f"{OUTPUT_FILE_PATH}.{file_format}"
    driver: WebDriver = initialize_driver()

    try:
        script = """
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        """
        driver.execute_script(script)

        driver.minimize_window()
        driver.get(f"{BASE_URL}login")

        email_field: WebElement = driver.find_element(By.ID, "email")
        email_field.send_keys(EMAIL)

        password_field: WebElement = driver.find_element(By.ID, "password")
        password_field.send_keys(PASSWORD)
        password_field.send_keys(Keys.RETURN)
        sleep(2)

        filter_params: dict[str, str | int] = {
            "year_range": "2021-2024",
            "page_size": 100,
            "sort_by": "sale_date",
            "sort_order": "asc",
        }

        df: DataFrame = fetch_data(driver, filter_params, pages)
        df = process_dataframe(df)
        df.drop_duplicates(subset="vin", keep="first", inplace=True)
        save_to_file(df, output_file)
        image_list: list[str] = process_images_column(output_file)
        print(f"{len(df)} позиций сохранено в файле: {os.path.abspath(output_file)}")

        await download_images(image_list)

    except Exception as e:
        print(f"Произошла ошибка: {e}")

    finally:
        driver.close()
        driver.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Скраппинг данных с Autobidmaster")
    parser.add_argument("pages", type=int, nargs="?", default=1, help="Количество страниц для обработки")
    parser.add_argument(
        "--ext",
        type=str,
        choices=["csv", "excel", "xls", "xlsx"],
        default="xlsx",
        help="Расширение сохраняемого файла (по умолчанию: xlsx)",
    )
    args: Namespace = parser.parse_args()
    asyncio.run(main(args.pages, args.ext))
