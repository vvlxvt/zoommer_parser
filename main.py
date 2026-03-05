from datetime import date
from config import ZoommerAPI
from db_conn import ConnectionDB
from zoommer_class import Products


def main():
    api = ZoommerAPI()
    menu = "\n".join([f"{i}. {cat}" for i, cat in enumerate(Products.CATS, 1)])

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
            else:
                db = ConnectionDB(
                    "sqlite:///zoommer.db"
                )  # устанавливаю соединение с бд
                category = scraper.category_name
                db.init_db(category)  # устанавливаю соединение с таблицей

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

        except ValueError:
            print("Please enter a valid number.")
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
