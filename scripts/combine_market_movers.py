import csv
import re
import uuid
from decimal import Decimal, InvalidOperation
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
INPUT_GLOB = "market-movers-export-*.csv"
OUTPUT_PATH = DATA_DIR / "combined_cards.csv"


COLUMN_RENAMES = {
    "Card": "card_name",
    "Grade": "grade",
    "Price Change %": "price_change_percent",
    "Price Change $": "price_change_amount",
    "Starting Price": "starting_price",
    "Last Sale": "last_sale",
    "Avg": "average_price",
    "Min Sale": "min_sale_price",
    "Max Sale": "max_sale_price",
    "Volume Change %": "volume_change_percent",
    "# of Sales": "number_of_sales",
    "Total Sales $": "total_sales_amount",
}

SOURCE_NUMERIC_COLUMNS = {
    "price_change_percent",
    "price_change_amount",
    "last_sale_price",
    "average_price",
    "min_sale_price",
    "max_sale_price",
    "volume_change_percent",
    "number_of_sales",
    "total_sales_amount",
}

CANONICAL_FIELD_ORDER = [
    "cardId",
    "player",
    "card_name",
    "grade",
    "date",
    "price",
    "price_change_amount",
    "price_change_percent",
    "average_price",
    "min_sale_price",
    "max_sale_price",
    "total_sales_amount",
    "number_of_sales",
    "volume_change_percent",
    "last_sale_date",
]


def standardize_header(header: str) -> str:
    renamed = COLUMN_RENAMES.get(header, header)
    cleaned = re.sub(r"[^a-z0-9]+", "_", renamed.lower()).strip("_")
    return cleaned


def extract_date_from_filename(path: Path) -> str:
    match = re.search(r"(\d{8})", path.stem)
    if not match:
        raise ValueError(f"Could not extract YYYYMMDD date from filename: {path.name}")
    return match.group(1)


def parse_decimal(value: str) -> str:
    if value is None:
        return ""

    cleaned = value.strip()
    if not cleaned:
        return ""

    negative = cleaned.startswith("-")
    normalized = (
        cleaned.replace("$", "")
        .replace(",", "")
        .replace("%", "")
        .replace("(", "")
        .replace(")", "")
        .strip()
    )

    if normalized.startswith("-"):
        negative = True
        normalized = normalized[1:]

    try:
        decimal_value = Decimal(normalized)
    except InvalidOperation:
        return ""

    if negative and decimal_value > 0:
        decimal_value = -decimal_value

    return format(decimal_value, "f")


def choose_price(last_sale_price: str, average_price: str) -> str:
    if last_sale_price:
        return last_sale_price
    if average_price:
        return average_price
    raise ValueError("Each row must have a valid last_sale_price or average_price to populate price")


def split_last_sale(value: str) -> tuple[str, str]:
    if not value:
        return "", ""

    match = re.match(r"\s*([$,\-\d\.]+)\s*(?:\(([^)]+)\))?\s*$", value)
    if not match:
        return "", ""

    price = parse_decimal(match.group(1))
    sale_date = match.group(2).strip() if match.group(2) else ""
    return price, sale_date


def row_is_empty(row: dict[str, str]) -> bool:
    return all(not str(value).strip() for value in row.values())


def extract_player(card_name: str) -> str:
    text = (card_name or "").strip()
    if not text:
        return ""

    match = re.match(r"^(.*?)(?=\s\d{4}\b)", text)
    if match:
        return match.group(1).strip()
    return text


def normalize_row(raw_row: dict[str, str], source_date: str) -> dict[str, str]:
    standardized_row = {
        standardize_header(key): (value or "").strip() for key, value in raw_row.items()
    }

    if row_is_empty(standardized_row):
        return {}

    last_sale_price, last_sale_date = split_last_sale(standardized_row.get("last_sale", ""))
    parsed_numeric_values = {
        column: parse_decimal(standardized_row.get(column, ""))
        for column in SOURCE_NUMERIC_COLUMNS
    }
    price = choose_price(last_sale_price, parsed_numeric_values["average_price"])

    return {
        "cardId": str(uuid.uuid4()),
        "player": extract_player(standardized_row.get("card_name", "")),
        "card_name": standardized_row.get("card_name", ""),
        "grade": standardized_row.get("grade", ""),
        "date": source_date,
        "price": price,
        "price_change_amount": parsed_numeric_values["price_change_amount"],
        "price_change_percent": parsed_numeric_values["price_change_percent"],
        "average_price": parsed_numeric_values["average_price"],
        "min_sale_price": parsed_numeric_values["min_sale_price"],
        "max_sale_price": parsed_numeric_values["max_sale_price"],
        "total_sales_amount": parsed_numeric_values["total_sales_amount"],
        "number_of_sales": parsed_numeric_values["number_of_sales"],
        "volume_change_percent": parsed_numeric_values["volume_change_percent"],
        "last_sale_date": last_sale_date,
    }


def main() -> None:
    input_paths = sorted(DATA_DIR.glob(INPUT_GLOB))
    if not input_paths:
        raise FileNotFoundError(f"No files matched {INPUT_GLOB} in {DATA_DIR}")

    combined_rows: list[dict[str, str]] = []
    for path in input_paths:
        source_date = extract_date_from_filename(path)
        with path.open("r", newline="", encoding="utf-8-sig") as csv_file:
            reader = csv.DictReader(csv_file)
            for raw_row in reader:
                normalized_row = normalize_row(raw_row, source_date)
                if not normalized_row:
                    continue
                combined_rows.append(normalized_row)

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CANONICAL_FIELD_ORDER)
        writer.writeheader()
        writer.writerows(combined_rows)

    print(f"Wrote {len(combined_rows)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
