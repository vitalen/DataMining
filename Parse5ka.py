"""
Источник: https://5ka.ru/special_offers/
Задача организовать сбор данных,
необходимо иметь метод сохранения данных в .json файлы
результат: Данные скачиваются с источника,
при вызове метода/функции сохранения в файл скачанные данные сохраняются в Json вайлы,
для каждой категории товаров должен быть создан отдельный файл и
содержать товары исключительно соответсвующие данной категории.
пример структуры данных для файла:
нейминг ключей можно делать отличным от примера
{
"name": "имя категории",
"code": "Код соответсвующий категории (используется в запросах)",
"products": [{PRODUCT}, {PRODUCT}........] # список словарей товаров соответсвующих данной категории
}
"""

import json
import time
from pathlib import Path
import requests


class Parse5ka:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0"
    }
    params = {"records_per_page": 30, "page": 1, "categories": None}

    def __init__(self, url_products: str, url_categories: str, save_path: Path):
        self.url_products = url_products
        # + "?page=1&records_per_page=20"
        self.url_categories = url_categories
        self.save_path = save_path

    def _get_response(self, url, *args, **kwargs):
        while True:
            response = requests.get(url, *args, **kwargs)
            if response.status_code == 200:
                print(f"Request: {response.url}")
                return response
            time.sleep(2)

    def run(self):
        try:
            for category in self._get_response(self.url_categories, headers=self.headers).json():
                products = []
                for product in self._parse(self.url_products, category["parent_group_code"]):
                    products.append(product)
                file_path = self.save_path.joinpath(f'{category["parent_group_name"]}.json')
                self._save(category, products, file_path)
                print(f'{category["parent_group_name"]}')
        except Exception as e:
            print(e)

    def _parse(self, url: str, categorie: str):
        self.params["categories"] = categorie
        page = 1
        self.params["page"] = page
        while url:
            time.sleep(0.1)
            data = self._get_response(url, headers=self.headers, params=self.params).json()
            page += 1
            self.params["page"] = page
            url = url.replace("monolith", "5ka.ru") if data["next"] else None
            for product in data["results"]:
                yield product

    def _save(self, category: dict, products: list, file_path):
        data = dict()
        data["name"] = category["parent_group_name"]
        data["code"] = category["parent_group_code"]
        data["products"] = products
        file_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def get_save_path(dir_name):
    save_path = Path(__file__).parent.joinpath(dir_name)
    if not save_path.exists():
        save_path.mkdir()
    return save_path


if __name__ == "__main__":
    save_path = get_save_path("products")
    url_products = "https://5ka.ru/api/v2/special_offers/"
    url_categories = "https://5ka.ru/api/v2/categories/"
    parser = Parse5ka(url_products, url_categories, save_path)
    parser.run()
    print("Exit")
