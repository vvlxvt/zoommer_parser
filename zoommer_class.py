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
        "Hand Vacuum CLeaners": "1098",
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
        products = []
        page = 1
        while True:
            params = {
                "Page": str(page),
                "pageSize": 20,
                "Limit": "300",
                "MinPrice": 50,
                "MaxPrice": 5000,
                "NotInStock": "true",
                "CategoryId": self.CATS[self.category_name],
            }
            response = self.api.get_products(params)
            page_products = response.get("products", [])
            if not page_products:
                break
            for p in page_products:
                extracted = self._extract_product(p)
                if extracted:  # skip items without id
                    products.append(extracted)
            # Останавливаемся, если передано меньше страницы, чем pageSize
            if len(page_products) < 20:
                break
            page += 1
        return products

    @staticmethod
    def _extract_product(p: dict) -> dict:
        """Безопасное извлечение полей продукта."""
        product_id = p.get("id")
        if product_id is None:
            return {}
        return {
            "id": product_id,
            "name": p.get("name"),
            "price": p.get("price"),
        }
