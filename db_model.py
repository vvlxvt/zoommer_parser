from typing import Optional
from sqlalchemy import String, Date
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class Base(DeclarativeBase):
    pass
class ItemBase(Base):
    __abstract__ = True  # Делаем класс абстрактным
    index: Mapped[int] = mapped_column(primary_key=True)
    date_field: Mapped[str] = mapped_column(Date)
    id: Mapped[int]
    name: Mapped[str] = mapped_column(String(80))
    price: Mapped[Optional[float]]

    def __repr__(self) -> str:
        return f"Product(id={self.id!r}, name={self.name!r}, price={self.price!r})"


def create_item_class(category: str) -> type:
    subclasses = Base.__subclasses__()
    print(subclasses)
    class_name = f"{category.capitalize()}Item"

    # Проверяем, существует ли уже класс с таким именем
    if class_name in globals():
        return globals()[class_name]

    # Создаем новый класс, если он не существует
    class Item(ItemBase):
        __tablename__ = category.lower()

    # Переименовываем класс
    Item.__name__ = class_name

    # Сохраняем класс в глобальном пространстве имен
    globals()[class_name] = Item

    return Item