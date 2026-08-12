import argparse
from datetime import datetime

from avito import build_search_url, fetch_html, load_saved_html, save_html
from excel import save_results_xlsx
from parser import filter_ads, is_empty_search_page, parse_ads, select_top_ads

ARTICLES = {
    "223112R020": "Прокладка головки блока цилиндра",
    "233002F700": "Балансирный вал в сборе",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Мини-парсер объявлений Avito по артикулам"
    )

    parser.add_argument(
        "--source",
        choices=["live", "file"],
        default="live",
        help="Источник HTML: live — Avito, file — сохранённые HTML",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = []

    base_url = None

    if args.source == "live":
        print("Установите в Avito необходимые фильтры:")
        print("- Москва и Московская область")
        print("- состояние: новое")
        print("- сортировка: сначала дешёвые")
        print()

        base_url = input("Вставьте полученный URL поиска Avito: ").strip()

        if not base_url:
            print("Ошибка: URL не указан.")
            return

    for article, product_name in ARTICLES.items():
        print(f"\nАртикул: {article}")
        print(f"Товар: {product_name}")

        checked_at = datetime.now().astimezone().isoformat(timespec="seconds")

        try:
            if args.source == "live":
                search_url = build_search_url(base_url, article)
                html = fetch_html(search_url)
                save_html(article, html)
            else:
                html = load_saved_html(article)

            ads = parse_ads(html)

            if not ads and not is_empty_search_page(html):
                raise ValueError("Страница получена, но поисковая выдача не распознана")

            filtered_ads = filter_ads(ads)
            top_ads = select_top_ads(filtered_ads)

            print(f"Карточек найдено: {len(ads)}")
            print(f"После фильтрации: {len(filtered_ads)}")
            print(f"Отобрано: {len(top_ads)}")

            if top_ads:
                for ad in top_ads:
                    results.append(
                        {
                            "article": article,
                            "search_query": article,
                            "title": ad["title"],
                            "price": ad["price"],
                            "location": ad["location"],
                            "condition": ad["condition"],
                            "url": ad["url"],
                            "price_rank": ad["price_rank"],
                            "checked_at": checked_at,
                            "status": "ok",
                            "error": None,
                        }
                    )
            else:
                results.append(
                    {
                        "article": article,
                        "search_query": article,
                        "title": None,
                        "price": None,
                        "location": None,
                        "condition": None,
                        "url": None,
                        "price_rank": None,
                        "checked_at": checked_at,
                        "status": "не найдено",
                        "error": None,
                    }
                )

        except Exception as error:
            results.append(
                {
                    "article": article,
                    "search_query": article,
                    "title": None,
                    "price": None,
                    "location": None,
                    "condition": None,
                    "url": None,
                    "price_rank": None,
                    "checked_at": checked_at,
                    "status": "ошибка",
                    "error": str(error),
                }
            )

            print(f"Ошибка: {error}")

    print("\nИтоговые строки:")

    for row in results:
        print(
            row["article"],
            row["price"],
            row["price_rank"],
            row["status"],
        )

    save_results_xlsx(results)

    print("\nРезультат сохранён в result.xlsx")


if __name__ == "__main__":
    main()
