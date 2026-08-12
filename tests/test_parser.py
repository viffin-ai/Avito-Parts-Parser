from parser import filter_ads, parse_ads, select_top_ads


def test_empty_html_returns_no_ads() -> None:
    ads = parse_ads("<html></html>")

    assert ads == []


def test_ad_without_price_is_filtered_out() -> None:
    html = """
    <div data-marker="item" data-item-id="1">
        <a data-marker="item-title" href="/moskva/test_1">
            Тестовая деталь
        </a>
        <span>Новое</span>
        <span data-marker="item-price-value">Цена не указана</span>
    </div>
    """

    ads = parse_ads(html)
    filtered_ads = filter_ads(ads)

    assert filtered_ads == []


def test_used_ad_is_filtered_out() -> None:
    html = """
    <div data-marker="item" data-item-id="1">
        <a data-marker="item-title" href="/moskva/test_1">
            Тестовая деталь
        </a>
        <span>Б/у</span>
        <span data-marker="item-price-value">5 000 ₽</span>
    </div>
    """

    ads = parse_ads(html)
    filtered_ads = filter_ads(ads)

    assert filtered_ads == []


def test_wrong_region_is_filtered_out() -> None:
    html = """
    <div data-marker="item" data-item-id="1">
        <a data-marker="item-title" href="/kazan/test_1">
            Тестовая деталь
        </a>
        <span>Новое</span>
        <span data-marker="item-price-value">5 000 ₽</span>
    </div>
    """

    ads = parse_ads(html)
    filtered_ads = filter_ads(ads)

    assert filtered_ads == []


def test_duplicates_are_removed_and_ads_sorted_by_price() -> None:
    ads = [
        {
            "ad_id": "1",
            "title": "Деталь 1",
            "price": 5000,
            "location": "Москва",
            "condition": "Новое",
            "url": "https://www.avito.ru/moskva/test_1",
        },
        {
            "ad_id": "2",
            "title": "Деталь 2",
            "price": 3000,
            "location": "Москва",
            "condition": "Новое",
            "url": "https://www.avito.ru/moskva/test_2",
        },
        {
            "ad_id": "1",
            "title": "Дубликат детали 1",
            "price": 5000,
            "location": "Москва",
            "condition": "Новое",
            "url": "https://www.avito.ru/moskva/test_1",
        },
    ]

    result = select_top_ads(ads)

    assert len(result) == 2
    assert [ad["ad_id"] for ad in result] == ["2", "1"]
    assert [ad["price"] for ad in result] == [3000, 5000]
    assert [ad["price_rank"] for ad in result] == [1, 2]


def test_ad_without_condition_is_filtered_out() -> None:
    html = """
    <div data-marker="item" data-item-id="1">
        <a data-marker="item-title" href="/moskva/test_1">
            Тестовая деталь
        </a>
        <span data-marker="item-price-value">5 000 ₽</span>
    </div>
    """

    ads = parse_ads(html)
    filtered_ads = filter_ads(ads)

    assert filtered_ads == []


def test_only_five_cheapest_ads_are_selected() -> None:
    ads = []

    for index, price in enumerate([6000, 1000, 5000, 2000, 4000, 3000], start=1):
        ads.append(
            {
                "ad_id": str(index),
                "title": f"Деталь {index}",
                "price": price,
                "location": "Москва",
                "condition": "Новое",
                "url": f"https://www.avito.ru/moskva/test_{index}",
            }
        )

    result = select_top_ads(ads)

    assert len(result) == 5
    assert [ad["price"] for ad in result] == [
        1000,
        2000,
        3000,
        4000,
        5000,
    ]
    assert [ad["price_rank"] for ad in result] == [1, 2, 3, 4, 5]
