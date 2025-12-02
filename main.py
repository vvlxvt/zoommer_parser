from datetime import date

import requests, json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_model import create_item_class


class Products:
    """делает запрос на сайт zoommer для получения информации по категории товара"""

    headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'ka',
    'authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJBcGkiLCJpc3MiOiJodHRwczovL2FwaS56b29tbWVyLmdlIiwiZXhwIjoyMDgwMDI3MTk1LCJzdWIiOiJab29tZXJXZWIiLCJzY29wZSI6Ilpvb21lckFwaSIsImNsaWVudF9pZCI6Ilpvb21lcldlYiIsImlhdCI6MTc2NDY1Mjc5NSwibmJmIjoxNzY0NjUyNzk1fQ.moTI0NNL9ClQEOUmbQyTLpEmgf8-M1JdIlQtGqNggTA',
    'cache-control': 'no-cache',
    'dnt': '1',
    'origin': 'https://zoommer.ge',
    'os': 'web',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://zoommer.ge/',
    'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Mobile Safari/537.36',
    }

    cats = {
        "Headset buds": "846",
        "Mobile phones": "855",
        "SSD internal": "1084",
        "Self-care": "490",
        "laptops": "813",
        "Smart watches": "1174",
        "Portable speakers": "528",
        "Tablets": "877",
        "E-Books": "1086",
        "Blades": "1211",
        "Screen protectors": "569",
    }

    list_cats = list(cats.keys())

    def __init__(self, brand=None, index=None):
        self.brand = brand
        if index:
            self.category = self.list_cats[int(index) - 1]
        else:
            self.category = "855"
        self.id_category = self.cats.get(self.category, None)
        self.min_price = 50
        self.max_price = 5500

        self.params = {
            "Name": self.brand,
            "Page": "1",
            "Limit": "300",
            "MinPrice": self.min_price,
            "MaxPrice": self.max_price,
            "NotInStock": "true",
            "CategoryId": self.id_category,
        }

    def get_query_params(self):
        response = requests.get(
            "https://api.zoommer.ge/v1/Products/v3",
            params=self.params,
            headers=self.headers,
        ).json()
        # print(json.dumps(response, indent=4, ensure_ascii=False))
        result = response.get("products")
        return result

    def query_from_api(self) -> list:
        # request data from source
        products: list = self.get_query_params()
        keys_to_keep = ["id", "name", "price"]
        new_list = []
        for p in products:
            filtered_data = {key: p[key] for key in keys_to_keep if key in p}
            new_list.append(filtered_data)
        return new_list


class ConnectionDB:
    def __init__(self, url):
        self.url = url
        self.engine = create_engine(
            url, echo=False, pool_size=10, max_overflow=20, pool_timeout=30
        )
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=True, bind=self.engine
        )

    def get_session(self):
        """Создание новой сессии"""
        return self.SessionLocal()

    def init_db(self, category):
        """Инициализация базы данных и создание всех таблиц"""
        self.Item = create_item_class(category)
        self.Item.__table__.create(bind=self.engine, checkfirst=True)
        print(f"таблица {self.Item.__name__} создана")

    def update_table(self, product):
        with self.SessionLocal() as session:
            session.merge(product)
            session.commit()

    def dump2table(self, products):
        """сюда должен передаваться список словарей"""
        Pack = []
        with self.SessionLocal() as session:
            for item in products:
                id = item["id"]
                name = item["name"][:80]
                price = item["price"]
                Pack.append(
                    self.Item(
                        id=id,
                        date_field=date.today(),
                        name=name,
                        price=price,
                    )
                )
            session.add_all(Pack)
            session.commit()

    def upload_from_base(self, cat: str, id) -> dict:
        session = self.get_session()
        request_class = create_item_class(cat)
        product = session.query(request_class).filter_by(id=id).first()
        return product

    def check_prices(self, category):
        pass


def main():

    cats = Products.cats
    formatted_string = ""
    for index, c in enumerate(cats, start=1):
        formatted_string += f"{index}. {c}\n"

    while True:
        print(f"Введите категорию товара:\n{formatted_string}")
        category = input(">> ")

        print(f"Введите бренд товара:\n")
        brand = input(">> ").lower()

        zoommer = Products(brand=brand, index=category)  # получаю структуру для запроса
        data = zoommer.query_from_api()  # получаю список товаров из запроса
        category = zoommer.category

        db = ConnectionDB("sqlite:///zoommer.db")  # устанавливаю соединение с бд
        db.init_db(zoommer.category)  # устанавливаю соединение с таблицей

        new_prices = []
        new_records = []
        for d in data:
            # разбираю данные из запроса
            # если цена старая из дб дороже новой, то меняю цену на меньшую и при этом ставлю декущую дату
            if record := db.upload_from_base(category, d["id"]):
                if record.price != d["price"]:
                    print(
                        f'!New Price! {record.name[:30]} was {record.price} becomes {d["price"]}'
                    )
                    record.price = d["price"]
                    record.date_field = date.today()
                    db.update_table(record)

            else:
                element = dict(
                    id=d["id"],
                    date_field=date.today(),
                    name=d["name"],
                    price=d["price"],
                )
                new_records.append(element)
        if new_records:
            db.dump2table(new_records)


if __name__ == "__main__":
    main()
