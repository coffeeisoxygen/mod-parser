# ruff:noqa

import json
from collections import Counter

from src.mlogger import LoggerManager, logger

# --- Timer context manager dari LoggerManager ---
timer = LoggerManager.timer


@timer("Load sample.json", level="INFO")
def load_sample():
    with open("sample.json", encoding="utf-8") as f:
        return json.load(f)


@timer("Hitung total char", level="INFO")
def count_total_char():
    with open("sample.json", encoding="utf-8") as f:
        raw_content = f.read()
    return len(raw_content)


@timer("Hitung total paket", level="INFO")
def count_total_paket(data):
    return len(data.get("paket", []))


data = load_sample()
total_char = count_total_char()
total_paket = count_total_paket(data)

logger.info(f"Total char (raw sample.json): {total_char}")
logger.info(f"Total paket: {total_paket}")

# Ambil semua productName
product_names = [p.get("productName", "") for p in data.get("paket", [])]

# Hitung unique dan totalnya
counter = Counter(product_names)

print("Unique productName dan totalnya:")
for name, total in counter.items():
    print(f"{name}: {total}")

print(f"\nTotal unique productName: {len(counter)}")
