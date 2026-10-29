"""Smoke-test harness for the Zoommer parser (no live API calls).

This script exercises the refactored architecture with a mocked API:
  1. DB model factory + table creation
  2. Session-based read-modify-write upsert
  3. Pagination + defensive extraction
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from datetime import date

import db_model  # noqa: E402
from db_conn import ConnectionDB  # noqa: E402


# ---------------------------------------------------------------------------
# Mock API
# ---------------------------------------------------------------------------
class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class FakeZoommerAPI:
    BASE_URL = "https://zoommer.ge"
    API_URL = "https://zoommer.ge/api/proxy/v1/Products/v3"

    def __init__(self, pages: list[dict]):
        self.pages = pages
        self._page_index = 0
        self.calls = []

    def _get(self, url, params):
        self.calls.append((url, params))
        page = self.pages[self._page_index % len(self.pages)]
        self._page_index += 1
        return FakeResponse(page)

    def get_products(self, params):
        return self._get(self.API_URL, params).json()




def _test():
    # 1. Model factory (real SQLAlchemy declarative models)
    model = db_model.get_item_model("Headset buds")
    assert model.__name__ == "Headset budsItem"
    assert model.__tablename__ == "headset_buds"

    # 2. DB connection + upsert (real in-memory SQLite)
    db = ConnectionDB("sqlite:///:memory:")
    db.Item = model
    model.__table__.create(bind=db.engine, checkfirst=True)

    sample = [{"id": 1, "name": "a" * 80, "price": 100.0}]
    inserted, updated = db.upsert_products(sample)
    assert (inserted, updated) == (1, 0), (inserted, updated)

    # Re-insert same id -> should be an update
    inserted, updated = db.upsert_products(sample)
    assert (inserted, updated) == (0, 1), (inserted, updated)

    # 3. Defensive extraction via mocked API (single page, < pageSize -> no pagination)
    page1 = {
        "products": [
            {"id": 1, "name": "Headset 1", "price": 100.0},
            {"id": 2, "name": "Headset 2", "price": 200.0},
            {"name": "No ID item"},  # missing id -> should be skipped
        ]
    }

    api = FakeZoommerAPI([page1])
    from zoommer_class import Products

    scraper = Products(api, 1)
    data = scraper.fetch_filtered_data()
    assert len(data) == 2, f"expected 2 products (skipped no-id item), got {len(data)}"
    assert data[0] == {"id": 1, "name": "Headset 1", "price": 100.0}
    assert data[1] == {"id": 2, "name": "Headset 2", "price": 200.0}

    print("SMOKE TEST OK")
    print(f"  API calls: {len(api.calls)}")
    print(f"  DB upsert test: inserted=1 updated=0 (repeat: inserted=0 updated=1)")


if __name__ == "__main__":
    _test()
