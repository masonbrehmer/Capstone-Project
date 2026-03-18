import csv
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
INPUT_PATH = DATA_DIR / "combined_cards.csv"
OUTPUT_BASENAME = "combined_cards_dynamodb_batch"
BATCH_SIZE = 25
TABLE_NAME = "sports-card-capstone-card-data"


NUMERIC_FIELDS = {
    "price",
    "price_change_percent",
    "price_change_amount",
    "average_price",
    "min_sale_price",
    "max_sale_price",
    "volume_change_percent",
    "number_of_sales",
    "total_sales_amount",
}


def clean_decimal(value: str) -> str | None:
    text = (value or "").strip()
    if not text:
        return None

    try:
        return format(Decimal(text), "f")
    except InvalidOperation:
        return None

def to_dynamodb_item(row: dict[str, str]) -> dict[str, dict[str, str]]:
    price = clean_decimal(row.get("price", ""))
    if price is None:
        raise ValueError("Each row must have a valid price value")

    item: dict[str, dict[str, str]] = {
        "cardId": {"S": row.get("cardId", "").strip()},
        "player": {"S": row.get("player", "")},
        "card_name": {"S": row.get("card_name", "")},
        "grade": {"S": row.get("grade", "")},
        "date": {"S": row.get("date", "")},
        "price": {"N": price},
    }

    for field in NUMERIC_FIELDS:
        value = clean_decimal(row.get(field, ""))
        if value is not None:
            item[field] = {"N": value}

    last_sale_date = (row.get("last_sale_date") or "").strip()
    if last_sale_date:
        item["last_sale_date"] = {"S": last_sale_date}

    return item


def chunked(items: list[dict[str, object]], size: int) -> list[list[dict[str, object]]]:
    return [items[index:index + size] for index in range(0, len(items), size)]


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Combined dataset not found: {INPUT_PATH}")

    with INPUT_PATH.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        requests = [{"PutRequest": {"Item": to_dynamodb_item(row)}} for row in reader]

    batches = chunked(requests, BATCH_SIZE)

    for path in DATA_DIR.glob(f"{OUTPUT_BASENAME}_*.json"):
        path.unlink()

    for index, batch in enumerate(batches, start=1):
        output_path = DATA_DIR / f"{OUTPUT_BASENAME}_{index:03d}.json"
        payload = {TABLE_NAME: batch}
        with output_path.open("w", encoding="utf-8") as json_file:
            json.dump(payload, json_file, indent=2)

    print(
        f"Wrote {len(requests)} items into {len(batches)} DynamoDB batch file(s) "
        f"under {DATA_DIR}"
    )


if __name__ == "__main__":
    main()
