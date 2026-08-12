"""Restaurant search client.

Supports:
- Dummy data (use_dummy_gourmet=True)
- Lovvit OpenSearch API (use_dummy_gourmet=False, lovvit_api_key set)
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from src.config import settings
from src.models.restaurant import Area, Genre, Restaurant
from src.tracing import log_input, trace_step

logger = logging.getLogger(__name__)

# ─── Dummy data ───────────────────────────────────────────────────────

DUMMY_RESTAURANTS: list[Restaurant] = [
    Restaurant(
        id="J001111111",
        name="トラットリア ミラノ",
        address="東京都渋谷区道玄坂1-2-3",
        lat=35.6595,
        lng=139.7004,
        genre="イタリアン",
        sub_genre="パスタ",
        budget="〜3000円",
        budget_average="2500円",
        open_hours="11:30〜15:00 17:00〜23:00",
        close="無休",
        access="渋谷駅徒歩5分",
        photo_url="https://imgfp.hotp.jp/IMGH/00/00/P033990000/P033990000_238.jpg",
        url="https://www.hotpepper.jp/",
        private_room=True,
        card_accepted=True,
        wifi=True,
        parking=False,
        pet_friendly=False,
        child_friendly=True,
    ),
    Restaurant(
        id="J002222222",
        name="寿司 銀座いちばん",
        address="東京都渋谷区渋谷2-4-5",
        lat=35.6600,
        lng=139.7010,
        genre="寿司",
        sub_genre="江戸前寿司",
        budget="〜5000円",
        budget_average="4000円",
        open_hours="12:00〜14:00 18:00〜22:00",
        close="日曜・祝日",
        access="渋谷駅徒歩3分",
        photo_url="https://imgfp.hotp.jp/IMGH/00/00/P033990000/P033990000_238.jpg",
        url="https://www.hotpepper.jp/",
        private_room=True,
        card_accepted=True,
        wifi=True,
        parking=False,
        pet_friendly=False,
        child_friendly=False,
    ),
    Restaurant(
        id="J003333333",
        name="居酒屋 渋谷の隠れ家",
        address="東京都渋谷区宇田川町10-11",
        lat=35.6580,
        lng=139.6980,
        genre="居酒屋",
        sub_genre="和食",
        budget="〜2000円",
        budget_average="1500円",
        open_hours="17:00〜翌2:00",
        close="無休",
        access="渋谷駅徒歩7分",
        photo_url="https://imgfp.hotp.jp/IMGH/00/00/P033990000/P033990000_238.jpg",
        url="https://www.hotpepper.jp/",
        private_room=True,
        card_accepted=True,
        wifi=True,
        parking=True,
        pet_friendly=False,
        child_friendly=True,
    ),
]

DUMMY_GENRES: list[Genre] = [
    Genre(code="G001", name="イタリアン"),
    Genre(code="G002", name="寿司"),
    Genre(code="G003", name="居酒屋"),
    Genre(code="G004", name="フレンチ"),
    Genre(code="G005", name="日本料理"),
]

DUMMY_AREAS: list[Area] = [
    Area(code="SA001", name="渋谷"),
    Area(code="SA002", name="表参道"),
    Area(code="SA003", name="新宿"),
    Area(code="SA004", name="銀座"),
    Area(code="SA005", name="六本木"),
]

DUMMY_BUDGETS: list[dict[str, str]] = [
    {"code": "B001", "name": "〜1000円", "average": "800円"},
    {"code": "B002", "name": "〜2000円", "average": "1500円"},
    {"code": "B003", "name": "〜3000円", "average": "2500円"},
    {"code": "B004", "name": "〜5000円", "average": "4000円"},
]


def _parse_lovvit_restaurant(item: dict[str, Any]) -> Restaurant:
    """Parse a single item from the Lovvit OpenSearch API response."""
    # Flexible field mapping — API may use different keys
    def _get(obj: Any, *keys: str, default: str = "") -> str:
        for k in keys:
            if isinstance(obj, dict) and obj.get(k) is not None:
                return str(obj[k])
        return default

    def _get_float(obj: Any, *keys: str) -> float | None:
        for k in keys:
            if isinstance(obj, dict) and obj.get(k) is not None:
                try:
                    return float(obj[k])
                except (TypeError, ValueError):
                    pass
        return None

    # Nested location (e.g. location.lat, location.lng)
    loc = item.get("location") or item.get("coordinates") or {}
    lat = _get_float(item, "lat", "latitude") or _get_float(loc, "lat", "latitude")
    lng = _get_float(item, "lng", "lng", "lon", "longitude") or _get_float(loc, "lng", "lng", "lon", "longitude")

    return Restaurant(
        id=_get(item, "id", "_id", "restaurant_id"),
        name=_get(item, "name", "title", "restaurant_name"),
        address=_get(item, "address", "address_formatted"),
        lat=lat,
        lng=lng,
        genre=_get(item, "genre", "category", "cuisine", "genre_name"),
        sub_genre=_get(item, "sub_genre", "sub_category"),
        budget=_get(item, "budget", "price_range", "budget_range"),
        budget_average=_get(item, "budget_average", "average_price"),
        open_hours=_get(item, "open_hours", "opening_hours", "open"),
        close=_get(item, "close", "closed"),
        access=_get(item, "access", "nearest_station"),
        photo_url=_get(item, "photo_url", "image", "photo", "image_url"),
        url=_get(item, "url", "link", "website"),
        private_room=bool(item.get("private_room") or item.get("has_private_room")),
        card_accepted=bool(item.get("card_accepted") or item.get("accepts_card")),
        wifi=bool(item.get("wifi") or item.get("has_wifi")),
        parking=bool(item.get("parking") or item.get("has_parking")),
        pet_friendly=bool(item.get("pet_friendly") or item.get("pet")),
        child_friendly=bool(item.get("child_friendly") or item.get("child")),
    )


class HotPepperClient:
    """Restaurant search client (Lovvit OpenSearch or dummy)."""

    def __init__(self) -> None:
        self.client = httpx.AsyncClient(timeout=15.0)

    async def close(self) -> None:
        await self.client.aclose()

    # ─── Core search ──────────────────────────────────────────────────

    async def search_restaurants(
        self,
        *,
        keyword: str | None = None,
        genre: str | None = None,
        large_area: str | None = None,
        middle_area: str | None = None,
        small_area: str | None = None,
        area_keyword: str | None = None,
        genre_keyword: str | None = None,
        budget: str | None = None,
        lat: float | None = None,
        lng: float | None = None,
        range_level: int | None = None,
        private_room: bool = False,
        card: bool = False,
        wifi: bool = False,
        lunch: bool = False,
        midnight: bool = False,
        pet: bool = False,
        child: bool = False,
        parking: bool = False,
        free_drink: bool = False,
        free_food: bool = False,
        count: int = 10,
        start: int = 1,
    ) -> list[Restaurant]:
        """Search restaurants with flexible filters.

        Returns a list of Restaurant models parsed from the API response.
        Uses Lovvit OpenSearch when lovvit_api_key is set, else HotPepper.
        """
        query_parts = [p for p in (area_keyword, genre_keyword, keyword, middle_area, genre) if p]
        query = " ".join(str(p) for p in query_parts) if query_parts else "default"
        log_input("tool_search_restaurants", query)
        async with trace_step("tool_search_restaurants", source="lovvit" if settings.lovvit_api_key else "dummy"):
            if settings.use_dummy_gourmet:
                return DUMMY_RESTAURANTS[:count]

            if settings.lovvit_api_key:
                return await self._search_lovvit(
                    keyword=keyword,
                    genre=genre,
                    middle_area=middle_area,
                    area_keyword=area_keyword,
                    genre_keyword=genre_keyword,
                    count=count,
                    start=start,
                )

            logger.warning("No API configured (use_dummy_gourmet=false, lovvit_api_key not set); falling back to dummy")
            return DUMMY_RESTAURANTS[:count]

    async def _search_lovvit(
        self,
        *,
        keyword: str | None = None,
        genre: str | None = None,
        middle_area: str | None = None,
        area_keyword: str | None = None,
        genre_keyword: str | None = None,
        count: int = 10,
        start: int = 1,
    ) -> list[Restaurant]:
        """Search via Lovvit OpenSearch restaurant API."""
        url = settings.lovvit_restaurant_search_url
        page = (start - 1) // count + 1
        # Prefer natural keywords for Lovvit; fall back to codes
        query_parts = [p for p in (area_keyword, genre_keyword, keyword, middle_area, genre) if p]
        query = " ".join(str(p) for p in query_parts) if query_parts else "東京"

        payload: dict[str, Any] = {
            "query": query,
            "pagination": {"page": page, "limit": min(count, 100)},
        }

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "X-API-Key": settings.lovvit_api_key,
        }

        logger.debug("Lovvit request: query=%r", query)
        resp = await self.client.post(url, json=payload, headers=headers)
        if resp.status_code not in (200, 201):
            logger.warning("Lovvit API error: %s %s", resp.status_code, resp.text[:200])
        resp.raise_for_status()
        data: dict[str, Any] = resp.json()

        # Handle error responses (e.g. {"statusCode": 403, "message": "..."})
        if data.get("statusCode") and data.get("statusCode") >= 400:
            logger.warning("Lovvit API returned error: %s", data.get("message", data))
            return []

        items = (
            data.get("data")
            or data.get("results")
            or data.get("restaurants")
            or data.get("items")
            or []
        )
        if isinstance(items, dict) and "items" in items:
            items = items["items"]
        if not isinstance(items, list):
            items = []

        return [_parse_lovvit_restaurant(item) for item in items[:count]]

    async def get_restaurant_by_id(self, restaurant_id: str) -> Restaurant | None:
        """Fetch a single restaurant by ID."""
        if settings.use_dummy_gourmet:
            for r in DUMMY_RESTAURANTS:
                if r.id == restaurant_id:
                    return r
            return DUMMY_RESTAURANTS[0] if DUMMY_RESTAURANTS else None

        if settings.lovvit_api_key:
            result = await self._search_lovvit(keyword=restaurant_id, count=1)
            for r in result:
                if r.id == restaurant_id:
                    return r
            return result[0] if result else None

        return DUMMY_RESTAURANTS[0] if DUMMY_RESTAURANTS else None

    # ─── Lookup helpers ───────────────────────────────────────────────

    async def search_genres(self, keyword: str | None = None) -> list[Genre]:
        """Look up genre codes, optionally filtered by keyword (dummy data for Lovvit)."""
        if keyword:
            return [g for g in DUMMY_GENRES if keyword.lower() in g.name.lower()]
        return DUMMY_GENRES

    async def search_large_areas(self, keyword: str | None = None) -> list[Area]:
        """Look up large area codes (dummy data for Lovvit)."""
        if keyword:
            return [a for a in DUMMY_AREAS if keyword.lower() in a.name.lower()]
        return DUMMY_AREAS

    async def search_middle_areas(
        self, keyword: str | None = None, large_area: str | None = None
    ) -> list[Area]:
        """Look up middle area codes (dummy data for Lovvit)."""
        if keyword:
            return [a for a in DUMMY_AREAS if keyword.lower() in a.name.lower()]
        return DUMMY_AREAS

    async def search_small_areas(
        self, keyword: str | None = None, middle_area: str | None = None
    ) -> list[Area]:
        """Look up small area codes (dummy data for Lovvit)."""
        if keyword:
            return [a for a in DUMMY_AREAS if keyword.lower() in a.name.lower()]
        return DUMMY_AREAS

    async def get_budget_master(self) -> list[dict[str, str]]:
        """Get the dinner budget code master list (dummy data for Lovvit)."""
        return DUMMY_BUDGETS

