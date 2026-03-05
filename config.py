import requests
from typing import Any, Dict


class ZoommerAPI:
    BASE_URL = "https://zoommer.ge"
    API_URL = "https://zoommer.ge/api/proxy/v1/Products/v3"

    def __init__(self):
        self.session = requests.Session()
        self._init_session()

    def _init_session(self):
        try:
            self.session.get(self.BASE_URL, timeout=10)
            token = self.session.cookies.get("zoommer-access_token")

            self.session.headers.update(
                {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Referer": "https://zoommer.ge/en",
                    "Accept": "application/json",
                }
            )

            if token:
                self.session.headers.update({"Authorization": f"Bearer {token}"})
        except requests.RequestException as e:
            print(f"Connection Error: {e}")

    def get_products(self, params: Dict[str, Any]) -> Any:
        response = self.session.get(self.API_URL, params=params)
        response.raise_for_status()
        return response.json()


api = ZoommerAPI()
