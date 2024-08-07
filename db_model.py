from sqlalchemy import Integer, String, Date, Index
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from typing import Optional

Base = declarative_base()

class ItemBase(Base):
    __abstract__ = True  # Делаем класс абстрактным
    index: Mapped[int] = mapped_column(primary_key=True)
    date_field: Mapped[str] = mapped_column(Date)
    id: Mapped[int] = mapped_column(Integer, index=True)  # Индексируем столбец id
    name: Mapped[str] = mapped_column(String(80))
    price: Mapped[Optional[float]]

    def __repr__(self) -> str:
        return f"Product(id={self.id!r}, name={self.name!r}, price={self.price!r})"

def create_item_class(category: str) -> type:
    class_name = f"{category.capitalize()}Item"

    # Проверяем, существует ли уже класс с таким именем
    if class_name in globals():
        return globals()[class_name]

    # Создаем новый класс, если он не существует
    class Item(ItemBase):
        __tablename__ = category.lower()
        __table_args__ = (Index(f'id_{category[:3]}', 'id'),)  # Добавляем индекс

    # Переименовываем класс
    Item.__name__ = class_name

    # Сохраняем класс в глобальном пространстве имен
    globals()[class_name] = Item

    return Item