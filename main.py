import requests
from datetime import date
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from db_model import create_item_class


class Products:
    '''делает запрос на сайт zoommer для получения информации по категории товара'''
    headers = {'accept': 'application/json, text/plain, */*', 'accept-language': 'en',
        'authorization': 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjBFMDgxN0I0M0VGNDM0RDhGNkQ5MjgwNzM1NDczQjlEIiwidHlwIjoiYXQrand0In0.eyJuYmYiOjE3MjA1Mjg5OTgsImV4cCI6MjAzNTg4ODk5OCwiaXNzIjoiaHR0cHM6Ly9hcGkuem9vbW1lci5nZS8iLCJhdWQiOiJBcGkiLCJjbGllbnRfaWQiOiJab29tZXJXZWIiLCJqdGkiOiI1NzM2MzNERjE4QzZGQzEyRjc4QjdENTQ3RDZFNzVGMSIsImlhdCI6MTcyMDUyODk5OCwic2NvcGUiOlsiWm9vbWVyQXBpIl19.cy7VorJBud_9HwekdXhDq3OChIsaCxhQAFu8aw4rXzOBwLafN6SOlNP9aQXmA0bMOZ7KlY7urNnpDroppSg8dgP92v-klOImh4MvuwYySftHUC01_it7g9gif-cWKNa0Hr_xkYKDJA3SvupNt7EoaiwxemBrRB-rx72y9vrU_sNo5eQMVh1Ve9oWVINTqdjnbRfQDpEO3clR6JJdyjtqzjYi4VhNqPw0k-2OqwCs9MghfSF7ctsaqdL0Gpyg-Kn2BXozTG7vEq9JP1YIL4pDQJNnnpLhjfqXb4zNF9k4SumDxXigMMT2VQUqwxduaz7KQZSdwqKztO2Id9wFVC0DvA',
        'dnt': '1', 'origin': 'https://zoommer.ge', 'os': 'web', 'priority': 'u=1, i', 'referer': 'https://zoommer.ge/',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"', 'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36', }

    cats = {'Headset buds': '846',
            'Mobile phones':'855',
            'SSD internal': '1084',
            'Self-care': '490',
            'laptops': '813',
            'Smart watches': '1174',
            'Portable speakers': '528',}

    list_cats = list(cats.keys())

    def __init__(self, brand=None, index=None):
        self.brand = brand
        if index:
            self.category = self.list_cats[int(index)-1]
        else:
            self.category = '855'
        self.id_category = self.cats.get(self.category, None)
        self.min_price = 100
        self.max_price = 5500

        self.params = {
            'Name': self.brand,
            'Page': '1',
            'Limit': '300',
            'MinPrice': self.min_price,
            'MaxPrice': self.max_price,
            'NotInStock': 'true',
            'CategoryId': self.id_category,
        }


    def get_query_params(self):

        response = requests.get('https://api.zoommer.ge/v1/Products/v3',
                                params=self.params,
                                headers=self.headers).json()
        return response.get('products')


class ConnectionDB:
    def __init__(self, url):
        self.url = url
        self.engine = create_engine(url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_session(self):
        """Создание новой сессии"""
        return self.SessionLocal()

    def init_db(self, category):
        """Инициализация базы данных и создание всех таблиц"""
        self.Item = create_item_class(category)
        self.Item.__table__.create(bind=self.engine, checkfirst=True)
        print(f'таблица {self.Item.__name__} создана')

    def dump2table(self, products):
        Pack = []
        with self.SessionLocal() as session:
            session.query(self.Item).delete()
            session.commit()
            for item in products:
                id = item['id']
                model = item['name'][:80]
                price = item['price']
                Pack.append(self.Item(date_field = date.today(),id=id, name=model, price=price, ))
            print(f'найдено позиций {len(Pack)}\n')
            session.add_all(Pack)
            session.commit()

    def get_dict(self, cat):
        session = self.get_session()
        request_class = create_item_class(cat)
        products = session.query(request_class).all()
        print(products[0])



def main():
    cats = Products.cats
    formatted_string=''
    for index, c in enumerate(cats, start=1):
        formatted_string += f"{index}. {c}\n"

    while True:
        print(f"Введите категорию товара:\n{formatted_string}")
        category = input('>> ')
        print(f"Введите бренд товара:\n")
        brand = input('>> ').lower()
        quaries = Products(brand, category)
        category = quaries.category
        products = quaries.get_query_params()
        db = ConnectionDB('sqlite:///zoommer.db')
        db.init_db(category)
        db.dump2table(products)
        db.get_dict('laptops')


if __name__ == '__main__':
    main()


