# Парсер данных с Autobidmaster

Этот скрипт позволяет скачивать данные о продаже автомобилей с сайта Autobidmaster и их изображения.

## Используемые технологии

* aiohttp
* asyncio
* pandas
* selenium

## Python и Git

Перед началом установки убедитесь, что у вас уже установлены Python и Git. Вы можете проверить это, запустив следующие команды в командной строке (терминале):

1. Проверка версии Python:

    ```bash
    python --version
    ```

    Если Python установлен, вы увидите версию Python. Если Python не установлен, следуйте [инструкциям по установке Python](https://telegra.ph/Kak-ustanovit-Python-na-razlichnyh-operacionnyh-sistemah-11-01).

2. Проверка версии Git:

    ```bash
    git --version
    ```

    Если Git установлен, вы увидите версию Git. Если Git не установлен, следуйте [документации по установке Git](https://git-scm.com/book/ru/v2/%D0%92%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5-%D0%A3%D1%81%D1%82%D0%B0%D0%BD%D0%BE%D0%B2%D0%BA%D0%B0-Git).

## Установка

1. Клонируйте репозиторий на свой компьютер:

    ```bash
    git clone https://github.com/redboo/autobidmaster_scrapper.git
    ```

2. Перейдите в папку проекта:

    ```bash
    cd autobidmaster_scrapper
    ```

3. Создайте виртуальную среду Python:

   * **Для Unix-подобных систем (Linux, macOS):**

     ```bash
     python3 -m venv env
     source env/bin/activate
     ```

   * **Для Windows:**

     ```bash
     python -m venv env
     .\env\Scripts\activate
     ```

    > Примечание: При использовании виртуальной среды Python (`source env/bin/activate`), не забудьте активировать ее перед началом работы и деактивировать после использования с помощью команд `source env/bin/activate` и `deactivate` соответственно.

4. Установите зависимости:

    ```bash
    pip install -r requirements.txt
    ```

## Использование

1. Убедитесь, что у вас установлены Chrome и ChromeDriver. [Инструкция по установке ChromeDriver](https://sites.google.com/chromium.org/driver/getting-started)

2. Создайте файл `.env` на основе [`default.env`](default.env) и заполните свои учетные данные авторизации на сайте:

    ```ini
    EMAIL=ваш_электронный_адрес
    PASSWORD=ваш_пароль
    ```

3. Запустите скрипт из командной строки, указав количество страниц для обработки (по умолчанию 1):

    ```bash
    python run.py количество_страниц [--ext расширение_файла]
    ```

    Пример:

    ```bash
    python run.py 2 --ext csv
    ```

    По умолчанию результат сохраняется в формате xlsx. Вы можете указать `--ext csv` для сохранения в формате CSV.

4. После завершения работы скрипта, вы найдете данные в папке `downloads`.

## Обновление репозитория Git

Если вы хотите обновить локальную копию репозитория до последней версии, выполните следующие команды в командной строке внутри папки проекта:

```bash
git pull origin main
```

## Лицензия

[GNU GPLv3](LICENSE)
