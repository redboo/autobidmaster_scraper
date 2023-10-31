import requests
import ast
import json
import os
import random
from platform import system
from time import sleep

import click
import pandas as pd
from dotenv import load_dotenv
from icecream import ic
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

OUTPUT_FILE_PATH = "downloads/data.csv"
BASE_URL = "https://www.autobidmaster.com/ru/"


def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    current_directory = os.getcwd()
    driver_directory = os.path.join(current_directory, "driver")
    chromedriver_filename = "chromedriver.exe" if system() == "Windows" else "chromedriver"
    chromedriver_path = os.path.join(driver_directory, chromedriver_filename)

    service = ChromeService(executable_path=chromedriver_path)
    return webdriver.Chrome(service=service, options=options)


def save_to_csv(dataframe, output_file_path):
    dataframe.to_csv(output_file_path, index=False, encoding="utf-8")


def fetch_data(driver, filter_params, pages: int):
    page = 1
    all_data = []

    while page < pages + 1:
        data_search_url = f"{BASE_URL}data/v2/inventory/search?custom_search=quickpick-runs-and-drives%2Fyear-{filter_params['year_range']}%2F&size={filter_params['page_size']}&page={page}&sort={filter_params['sort_by']}&order={filter_params['sort_order']}"

        driver.get(data_search_url)
        json_data = driver.execute_script("return JSON.parse(document.body.innerText);")

        total_cars = json_data.get("total", 0)
        all_data.extend(json_data.get("lots", []))

        page += 1
        if page * filter_params["page_size"] > total_cars:
            break

        sleep(random.uniform(1.0, 3.0))

    return pd.DataFrame(all_data)


def process_dataframe(dataframe):
    columns_to_keep = [
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
        dataframe = dataframe[columns_to_keep]
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None

    return dataframe


def download_images(images, output_folder="downloads/images"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for image_url in images:
        try:
            file_name = os.path.join(output_folder, f"{image_url.split('/')[-1]}")
            if not os.path.exists(file_name):
                response = requests.get(image_url, stream=True)
                with open(file_name, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
            else:
                ic(f"Файл {file_name} уже существует. Пропускаем загрузку.")
        except Exception as e:
            ic(f"Ошибка при загрузке изображения {image_url}: {e}")


def process_images_column(df, output_file_path):
    df = pd.read_csv(output_file_path)
    df["images"] = df["images"].apply(lambda x: [item["hdr"] for item in ast.literal_eval(x)])
    save_to_csv(df, output_file_path)
    for image_list in df["images"]:
        download_images(image_list)


@click.command()
@click.argument("pages", type=int, default=1, required=False)
def main(pages: int = 1):
    driver = initialize_driver()

    try:
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            """
            },
        )

        driver.minimize_window()
        driver.get(f"{BASE_URL}login")

        email_field = driver.find_element(By.ID, "email")
        email_field.send_keys(EMAIL)

        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(PASSWORD)
        password_field.send_keys(Keys.RETURN)
        sleep(2)

        filter_params = {
            "year_range": "2021-2024",
            "page_size": 100,
            "sort_by": "sale_date",
            "sort_order": "asc",
        }

        df = fetch_data(driver, filter_params, pages)
        df = process_dataframe(df)
        save_to_csv(df, OUTPUT_FILE_PATH)
        process_images_column(df, OUTPUT_FILE_PATH)

    except Exception as e:
        print(f"Произошла ошибка: {e}")

    finally:
        driver.close()
        driver.quit()


if __name__ == "__main__":
    main()
