
from __future__ import annotations

import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

from artifact_tool import Workbook, SpreadsheetFile


OUTPUT_FILE = Path("computer_transactions_may_july_2026.xlsx")
RANDOM_SEED = 2026
TRANSACTIONS_PER_MONTH = 1000


# ---------------------------------------------------------------------
# Product setup
# May products are available in the initial mapping.
# June introduces new products.
# July introduces products in new categories/subcategories.
# ---------------------------------------------------------------------
MAY_PRODUCTS: List[Tuple[str, str, str, str, float]] = [
    ("Logitech", "MX Master 3S", "Computer Accessories", "Mouse", 8999),
    ("Logitech", "K380 Keyboard", "Computer Accessories", "Keyboard", 3299),
    ("Dell", "P2425H Monitor", "Displays", "Monitor", 18999),
    ("HP", "E24 G5 Monitor", "Displays", "Monitor", 21499),
    ("Kingston", "DataTraveler 64GB", "Storage", "USB Drive", 699),
    ("SanDisk", "Extreme Portable SSD 1TB", "Storage", "External SSD", 10499),
    ("Jabra", "Evolve2 40 Headset", "Audio", "Headset", 12499),
    ("Microsoft", "LifeCam HD-3000", "Video Accessories", "Webcam", 3499),
    ("TP-Link", "UE300 Ethernet Adapter", "Computer Accessories", "Adapter", 1199),
    ("Belkin", "USB-C 7-in-1 Hub", "Computer Accessories", "USB Hub", 6499),
]

JUNE_NEW_PRODUCTS: List[Tuple[str, str, str, str, float]] = [
    ("Lenovo", "ThinkVision T24i", "Displays", "Monitor", 22999),
    ("Logitech", "Brio 500 Webcam", "Video Accessories", "Webcam", 10999),
    ("Samsung", "T7 Shield SSD 2TB", "Storage", "External SSD", 17999),
]

JULY_NEW_PRODUCTS: List[Tuple[str, str, str, str, float]] = [
    ("Cisco", "CBS110 Network Switch", "Networking Equipment", "Network Switch", 8499),
    ("APC", "Back-UPS 1100VA", "Power and Backup", "UPS", 8999),
    ("Poly", "Studio P15 Video Bar", "Video Conferencing", "Conference Camera", 34999),
]


def product_key(make: str, name: str) -> str:
    """Create the simple lookup key used in both mapping and transactions."""
    return f"{make} {name}"


def generate_transactions(
    month: int,
    products: List[Tuple[str, str, str, str, float]],
    transaction_count: int,
) -> List[List[object]]:
    """Generate simple fictitious B2B transactions for one month."""
    start_date = datetime(2026, month, 1)
    next_month = datetime(2026, month + 1, 1) if month < 12 else datetime(2027, 1, 1)
    days_in_month = (next_month - start_date).days

    rows: List[List[object]] = []
    for number in range(1, transaction_count + 1):
        make, name, _, _, base_price = random.choice(products)
        transaction_date = start_date + timedelta(days=random.randint(0, days_in_month - 1))
        quantity = random.randint(1, 20)

        # Small price variation keeps the fictitious data realistic.
        unit_price = round(base_price * random.uniform(0.94, 1.06), 2)
        total_sales = round(quantity * unit_price, 2)

        rows.append([
            f"TXN-{month:02d}-{number:04d}",
            transaction_date,
            product_key(make, name),
            quantity,
            unit_price,
            total_sales,
        ])
    return rows


def build_final_mapping() -> List[List[str]]:
    """Return the final mapping after June and July products are added."""
    all_products = MAY_PRODUCTS + JUNE_NEW_PRODUCTS + JULY_NEW_PRODUCTS
    return [
        [product_key(make, name), main_category, subcategory]
        for make, name, main_category, subcategory, _ in all_products
    ]


def create_report(
    transactions_by_month: Dict[str, List[List[object]]],
    mapping_rows: List[List[str]],
) -> List[List[object]]:
    """Aggregate total sales by main category and subcategory for each month."""
    mapping_lookup = {
        row[0]: (row[1], row[2])
        for row in mapping_rows
    }

    totals: Dict[Tuple[str, str], Dict[str, float]] = {}

    for month_name, rows in transactions_by_month.items():
        for row in rows:
            key = row[2]
            total_sales = float(row[5])
            main_category, subcategory = mapping_lookup[key]
            category_key = (main_category, subcategory)

            if category_key not in totals:
                totals[category_key] = {
                    "May 2026": 0.0,
                    "June 2026": 0.0,
                    "July 2026": 0.0,
                }

            totals[category_key][month_name] += total_sales

    report_rows: List[List[object]] = []
    for (main_category, subcategory), month_totals in sorted(totals.items()):
        may_sales = round(month_totals["May 2026"], 2)
        june_sales = round(month_totals["June 2026"], 2)
        july_sales = round(month_totals["July 2026"], 2)

        report_rows.append([
            main_category,
            subcategory,
            may_sales,
            june_sales,
            july_sales,
            round(may_sales + june_sales + july_sales, 2),
        ])

    return report_rows


def format_table_sheet(sheet, used_range: str, date_column: str | None = None) -> None:
    """Apply simple professional formatting."""
    header = sheet.get_range(used_range.split(":")[0][0] + "1:" + used_range.split(":")[1][0] + "1")
    header.format = {
        "fill": "#1F4E78",
        "font": {"bold": True, "color": "#FFFFFF"},
        "horizontal_alignment": "center",
        "vertical_alignment": "center",
    }

    sheet.get_range(used_range).format.autofit_columns()
    sheet.freeze_panes.freeze_rows(1)

    if date_column:
        sheet.get_range(date_column).format.number_format = "yyyy-mm-dd"


def main() -> None:
    random.seed(RANDOM_SEED)

    may_transactions = generate_transactions(
        month=5,
        products=MAY_PRODUCTS,
        transaction_count=TRANSACTIONS_PER_MONTH,
    )

    june_transactions = generate_transactions(
        month=6,
        products=MAY_PRODUCTS + JUNE_NEW_PRODUCTS,
        transaction_count=TRANSACTIONS_PER_MONTH,
    )

    july_transactions = generate_transactions(
        month=7,
        products=MAY_PRODUCTS + JUNE_NEW_PRODUCTS + JULY_NEW_PRODUCTS,
        transaction_count=TRANSACTIONS_PER_MONTH,
    )

    final_mapping = build_final_mapping()

    transactions_by_month = {
        "May 2026": may_transactions,
        "June 2026": june_transactions,
        "July 2026": july_transactions,
    }
    report_rows = create_report(transactions_by_month, final_mapping)

    workbook = Workbook.create()

    # Sheet 1: Mapping
    mapping_sheet = workbook.worksheets.add("Product Mapping")
    mapping_data = [["Product Key", "Main Category", "Subcategory"]] + final_mapping
    mapping_sheet.get_range(f"A1:C{len(mapping_data)}").values = mapping_data
    format_table_sheet(mapping_sheet, f"A1:C{len(mapping_data)}")
    mapping_sheet.tables.add(
        f"A1:C{len(mapping_data)}",
        True,
        "ProductMappingTable",
    )

    # Sheets 2–4: Monthly transactions
    transaction_headers = [
        "Transaction ID",
        "Transaction Date",
        "Product Key",
        "Quantity",
        "Unit Price",
        "Total Sales",
    ]

    monthly_sheet_details = [
        ("May Transactions", may_transactions, "MayTransactionsTable"),
        ("June Transactions", june_transactions, "JuneTransactionsTable"),
        ("July Transactions", july_transactions, "JulyTransactionsTable"),
    ]

    for sheet_name, rows, table_name in monthly_sheet_details:
        sheet = workbook.worksheets.add(sheet_name)
        data = [transaction_headers] + rows
        sheet.get_range(f"A1:F{len(data)}").values = data
        format_table_sheet(sheet, f"A1:F{len(data)}", f"B2:B{len(data)}")
        sheet.get_range(f"D2:D{len(data)}").format.number_format = "0"
        sheet.get_range(f"E2:F{len(data)}").format.number_format = '#,##0.00'
        sheet.tables.add(f"A1:F{len(data)}", True, table_name)

    # Sheet 5: Final category report
    report_sheet = workbook.worksheets.add("Category Report")
    report_headers = [
        "Main Category",
        "Subcategory",
        "May 2026 Sales",
        "June 2026 Sales",
        "July 2026 Sales",
        "Total Sales",
    ]
    report_data = [report_headers] + report_rows
    report_sheet.get_range(f"A1:F{len(report_data)}").values = report_data
    format_table_sheet(report_sheet, f"A1:F{len(report_data)}")
    report_sheet.get_range(f"C2:F{len(report_data)}").format.number_format = '#,##0.00'
    report_sheet.tables.add(
        f"A1:F{len(report_data)}",
        True,
        "CategorySalesReportTable",
    )

    SpreadsheetFile.export_xlsx(workbook).save(str(OUTPUT_FILE))
    print(f"Created: {OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
