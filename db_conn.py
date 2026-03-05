from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date
from db_model import create_item_class


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
