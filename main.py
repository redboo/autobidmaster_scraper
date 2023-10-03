import glob
import json

import pandas as pd
import requests

DOWNLOADS_DIR = "downloads/"


def fetch_data():
    url = "https://www.autobidmaster.com/ru/data/v2/inventory/search?size=100&page=1&sort=sale_date&order=asc"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    }
    res = requests.get(url, headers=headers)
    with open("downloads/data.json", "w") as file:
        json.dump(
            res.json(),
            file,
            ensure_ascii=False,
        )


def process_data():
    files = glob.glob("downloads/*.json")
    for file in files:
        data = json.load(open(file, "r"))["lots"]
        df = pd.DataFrame(data)
        df.to_csv(file.replace(".json", ".csv"), index=False)


def main():
    fetch_data()
    process_data()


if __name__ == "__main__":
    main()
