from datetime import date
from config import ZoommerAPI
from db_conn import ConnectionDB
from zoommer_class import Products


def main():
    api = ZoommerAPI()
    menu = "\n".join(f"{i}. {cat}" for i, cat in enumerate(Products.CATS, 1))

    while True:
        print(f"\n--- Zoommer Product Scraper ---")
        print(f"Select a category:\n{menu}")
        print("0. Exit")

        try:
            choice = int(input(">> "))
            if choice == 0:
                break
            if not (1 <= choice <= len(Products.CATS)):
                print("Invalid selection. Please choose a number from the list.")
                continue

            scraper = Products(api, choice)
            data = scraper.fetch_filtered_data()

            if not data:
                print("No products found in this category.")
                continue

            db = ConnectionDB("sqlite:///zoommer.db")
            category = scraper.category_name
            db.init_db(category)

            new_records = []
            for d in data:
                # Пропускаем записи без id (невалидные/плейсхолдеры)
                product_id = d.get("id")
                if product_id is None:
                    continue

                # Чистый "чтение-запись" в рамках одной сессии,
                # чтобы избежать race-условия TOCTOU.
                with db.SessionLocal() as session:
                    request_class = db.Item
                    product = (
                        session.query(request_class)
                        .filter_by(id=product_id)
                        .first()
                    )
                    if product is not None and product.price != d.get("price"):
                        print(
                            f"!New Price! {str(product.name)[:30]} was "
                            f"{product.price} becomes {d.get('price')}"
                        )
                        product.price = d.get("price")
                        product.date_field = date.today()
                        session.merge(product)
                        session.commit()
                    elif product is None:
                        new_records.append(
                            {
                                "id": product_id,
                                "date_field": date.today(),
                                "name": d.get("name"),
                                "price": d.get("price"),
                            }
                        )

            if new_records:
                inserted, updated = db.upsert_products(new_records)
                print(
                    f"Inserted: {inserted}, Updated: {updated}"
                )

        except ValueError:
            print("Please enter a valid number.")
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
