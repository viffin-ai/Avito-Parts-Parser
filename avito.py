from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import requests


def build_search_url(base_url: str, search_query: str) -> str:
    """
    Заменяет поисковый параметр q в готовом URL Avito,
    сохраняя остальные параметры фильтрации.
    """
    parsed_url = urlparse(base_url)

    query_params = parse_qsl(
        parsed_url.query,
        keep_blank_values=True,
    )

    query_params = [(key, value) for key, value in query_params if key != "q"]

    query_params.append(("q", search_query))

    new_query = urlencode(query_params)

    return urlunparse(parsed_url._replace(query=new_query))


REQUEST_TIMEOUT = 10


def fetch_html(url: str) -> str:
    """
    Выполняет обычный HTTP-запрос и возвращает HTML страницы.

    Если Avito возвращает HTTP-ошибку или возникает сетевая проблема,
    requests выбрасывает исключение. Обход блокировок не выполняется.
    """
    response = requests.get(
        url,
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    return response.text


INPUT_HTML_DIR = Path("input_html")


def save_html(article: str, html: str) -> Path:
    INPUT_HTML_DIR.mkdir(exist_ok=True)

    file_path = INPUT_HTML_DIR / f"{article}.html"
    file_path.write_text(html, encoding="utf-8")

    return file_path


def load_saved_html(article: str) -> str:
    file_path = INPUT_HTML_DIR / f"{article}.html"

    return file_path.read_text(encoding="utf-8")
