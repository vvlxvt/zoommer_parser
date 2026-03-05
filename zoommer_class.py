from config import ZoommerAPI


class Products:
    CATS = {
        "Headset buds": "846",
        "Mobile phones": "855",
        "SSD internal": "1084",
        "Self-care": "490",
        "Laptops": "531",
        "Smart watches": "873",
        "Portable speakers": "528",
        "Tablets": "877",
        "E-Books": "1086",
        "Blades": "1211",
        "Screen protectors": "569",
    }

    def __init__(self, api: ZoommerAPI, selection_index: int):
        self.api = api
        cat_keys = list(self.CATS.keys())
        self.category_name = cat_keys[selection_index - 1]
        category_id = self.CATS[self.category_name]

        self.params = {
            "Page": "1",
            "pageSize": 20,
            "Limit": "300",
            "MinPrice": 50,
            "MaxPrice": 5000,
            "NotInStock": "true",
            "CategoryId": category_id,
        }

    def fetch_filtered_data(self) -> list:
        response = self.api.get_products(self.params)
        products = response.get("products", [])
        keys_to_keep = ["id", "name", "price"]
        return [{k: p[k] for k in keys_to_keep if k in p} for p in products]
