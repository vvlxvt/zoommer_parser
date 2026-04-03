from sqlalchemy import Integer, String, Date, Index
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from typing import Optional

Base = declarative_base()
MODEL_CACHE = {}


class ItemBase(Base):
    __abstract__ = True  # Делаем класс абстрактным
    index: Mapped[int] = mapped_column(primary_key=True)
    date_field: Mapped[str] = mapped_column(Date)
    id: Mapped[int] = mapped_column(Integer, index=True)  # Индексируем столбец id
    name: Mapped[str] = mapped_column(String(80))
    price: Mapped[Optional[float]]

    def __repr__(self) -> str:
        return f"Product(id={self.id!r}, name={self.name!r}, price={self.price!r})"


def get_item_model(category: str):

    if category in MODEL_CACHE:
        return MODEL_CACHE[category]

    class_name = f"{category.capitalize()}Item"
    table_name = category.lower()

    attrs = {
        "__tablename__": table_name,
        "__table_args__": (Index(f"id_{category[:3]}", "id"),),
    }

    model = type(class_name, (ItemBase,), attrs)

    MODEL_CACHE[category] = model

    return model
