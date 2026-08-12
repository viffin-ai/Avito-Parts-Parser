from openpyxl import Workbook
from openpyxl.styles import Font

COLUMNS = [
    "article",
    "search_query",
    "title",
    "price",
    "location",
    "condition",
    "url",
    "price_rank",
    "checked_at",
    "status",
    "error",
]


def save_results_xlsx(
    results: list[dict],
    filename: str = "result.xlsx",
) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "results"

    sheet.append(COLUMNS)

    for cell in sheet[1]:
        cell.font = Font(bold=True)

    for result in results:
        row = [result.get(column) for column in COLUMNS]
        sheet.append(row)

    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    column_widths = {
        "A": 16,
        "B": 16,
        "C": 45,
        "D": 12,
        "E": 18,
        "F": 14,
        "G": 50,
        "H": 12,
        "I": 28,
        "J": 14,
        "K": 35,
    }

    for column, width in column_widths.items():
        sheet.column_dimensions[column].width = width

    workbook.save(filename)
