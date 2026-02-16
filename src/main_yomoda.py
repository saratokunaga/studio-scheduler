from src.adapters.yomoda.fetch import fetch_all
from src.adapters.yomoda.parser import parse_all
from src.adapters.yomoda.search import search


TARGET_DATE = "2026-02-17"
TARGET_TIME = "10:00"
TARGET_PERIOD = "day"


def main():

    print("Fetching...")

    raw_all = fetch_all(headless=True)

    print("Parsing...")

    parsed = parse_all(raw_all)

    print("Searching...")

    result = search(
        parsed,
        date=TARGET_DATE,
        time=TARGET_TIME,
        period=TARGET_PERIOD,
    )

    print("\nAvailable studios:\n")

    for r in result:

        print(r["studio"], r["date"], r["time"])


if __name__ == "__main__":
    main()
