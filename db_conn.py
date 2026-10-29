from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date
from db_model import get_item_model


class ConnectionDB:
    def __init__(self, url):
        self.url = url
        # SQLite uses SingletonThreadPool by default, which does not accept
        # pool_size/max_overflow/pool_timeout. Pass them only for
        # non-SQLite engines (e.g. PostgreSQL).
        if url.startswith("sqlite"):
            self.engine = create_engine(
                url, echo=False, connect_args={"check_same_thread": False}
            )
        else:
            self.engine = create_engine(
                url,
                echo=False,
                pool_size=10,
                max_overflow=20,
                pool_timeout=30,
            )
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=True, bind=self.engine
        )

    def get_session(self):
        """Создание новой сессии"""
        return self.SessionLocal()

    def init_db(self, category):
        """Инициализация базы данных и создание всех таблиц"""
        self.Item = get_item_model(category)
        self.Item.__table__.create(bind=self.engine, checkfirst=True)
        print(f"таблица {self.Item.__name__} создана")

    def update_table(self, product):
        with self.SessionLocal() as session:
            session.merge(product)
            session.commit()

    def upsert_products(self, products: list[dict]) -> tuple[int, int]:
        """
        Вставляет новые записи и обновляет существующие одним транзакционным пулом.
        Возвращает (количество_вставленных, количество_обновлённых).
        """
        session = self.SessionLocal()
        inserted = 0
        updated = 0
        try:
            for item in products:
                item_id = item.get("id")
                name = item.get("name")
                price = item.get("price")

                if item_id is None or name is None or price is None:
                    continue

                existing = (
                    session.query(self.Item)
                    .filter_by(id=item_id)
                    .first()
                )
                if existing is not None:
                    existing.name = name[:80]
                    existing.price = price
                    existing.date_field = date.today()
                    updated += 1
                else:
                    record = self.Item(
                        id=item_id,
                        date_field=date.today(),
                        name=name[:80],
                        price=price,
                    )
                    session.add(record)
                    inserted += 1
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

        return inserted, updated

    def upload_from_base(self, cat: str, id: int):
        session = self.get_session()
        request_class = get_item_model(cat)
        product = session.query(request_class).filter_by(id=id).first()
        return product

    def check_prices(self, category):
        pass
