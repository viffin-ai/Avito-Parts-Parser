import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag

AVITO_BASE_URL = "https://www.avito.ru"


def parse_price(item: Tag) -> int | None:
    price_element = item.select_one('[data-marker="item-price-value"]')

    if price_element is None:
        return None

    price_text = price_element.get_text(" ", strip=True)
    digits = re.sub(r"\D", "", price_text)

    if not digits:
        return None

    return int(digits)


def parse_condition(item: Tag) -> str | None:
    condition = item.find(
        string=lambda text: text is not None and text.strip() == "Новое"
    )

    if condition is None:
        return None

    return "Новое"


def parse_item(item: Tag) -> dict[str, str | int | None]:
    title_element = item.select_one('[data-marker="item-title"]')

    title = None
    url = None

    if title_element is not None:
        title = title_element.get_text(" ", strip=True)

        href = title_element.get("href")
        if isinstance(href, str):
            url = urljoin(AVITO_BASE_URL, href)

    ad_id = item.get("data-item-id")

    if not isinstance(ad_id, str):
        ad_id = None

    location_slug = parse_location_slug(url)

    return {
        "ad_id": ad_id,
        "title": title,
        "price": parse_price(item),
        "location_slug": location_slug,
        "location": format_location(location_slug),
        "condition": parse_condition(item),
        "url": url,
    }


def parse_ads(html: str) -> list[dict[str, str | int | None]]:
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select('[data-marker="item"]')

    return [parse_item(item) for item in items]


def is_empty_search_page(html: str) -> bool:
    soup = BeautifulSoup(html, "html.parser")
    page_text = soup.get_text(" ", strip=True).lower()

    empty_messages = (
        "ничего не найдено",
        "объявлений не найдено",
        "по вашему запросу ничего не найдено",
    )

    return any(message in page_text for message in empty_messages)


def parse_location_slug(url: str | None) -> str | None:
    if url is None:
        return None

    path_parts = urlparse(url).path.strip("/").split("/")

    if not path_parts or not path_parts[0]:
        return None

    return path_parts[0]


def is_allowed_location(location_slug: str | None) -> bool:
    if location_slug is None:
        return False

    if location_slug == "moskva":
        return True

    if location_slug.startswith("moskovskaya_oblast_"):
        return True

    return location_slug in {
        "balashiha",
    }


def format_location(location_slug: str | None) -> str | None:
    if location_slug == "moskva":
        return "Москва"

    if location_slug == "balashiha":
        return "Балашиха, Московская область"

    if location_slug and location_slug.startswith("moskovskaya_oblast_"):
        return "Московская область"

    return None


def select_ads(
    ads: list[dict[str, str | int | None]],
    limit: int = 5,
) -> list[dict[str, str | int | None]]:
    filtered_ads = []

    for ad in ads:
        if ad["condition"] != "Новое":
            continue

        if not is_allowed_location(ad["location"]):
            continue

        if not isinstance(ad["price"], int):
            continue

        filtered_ads.append(ad)

    return filtered_ads


def filter_ads(
    ads: list[dict[str, str | int | None]],
) -> list[dict[str, str | int | None]]:
    filtered_ads = []

    for ad in ads:
        if not isinstance(ad["title"], str) or not ad["title"].strip():
            continue

        if not isinstance(ad["url"], str) or not ad["url"].strip():
            continue

        if ad["condition"] != "Новое":
            continue

        if not is_allowed_location(ad["location_slug"]):
            continue

        if not isinstance(ad["price"], int):
            continue

        filtered_ads.append(ad)

    return filtered_ads


def select_top_ads(
    ads: list[dict[str, str | int | None]],
    limit: int = 5,
) -> list[dict[str, str | int | None]]:
    unique_ads = []
    seen_ids = set()

    for ad in ads:
        unique_key = ad["ad_id"] or ad["url"]

        if unique_key is None:
            continue

        if unique_key in seen_ids:
            continue

        seen_ids.add(unique_key)
        unique_ads.append(ad)

    sorted_ads = sorted(
        unique_ads,
        key=lambda ad: int(ad["price"]),
    )

    top_ads = sorted_ads[:limit]

    for rank, ad in enumerate(top_ads, start=1):
        ad["price_rank"] = rank

    return top_ads
