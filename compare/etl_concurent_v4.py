# 9. One-go ETL pipeline (final, efisien)
def process_all(paket_list, prefix_filter):
    """
    Proses ETL satu kali loop: uppercase, filter prefix, clean quota, simplify quota.
    Args:
        paket_list: list of dict
        prefix_filter: str, prefix dipisah koma
    Returns:
        list of dict hasil ETL
    """
    prefixes = [p.strip().upper() for p in prefix_filter.split(",") if p.strip()]
    result = []
    for paket in paket_list:
        # Uppercase semua value string
        new_paket = {
            k: v.upper() if isinstance(v, str) else v for k, v in paket.items()
        }
        # Filter prefix productName
        if any(
            str(new_paket.get("productName", "")).startswith(prefix)
            for prefix in prefixes
        ):
            continue
        # Clean quota
        quota = str(new_paket.get("quota", ""))
        parts = []
        for part in quota.split(","):
            if "/" in part:
                parts.append(part.split("/", 1)[1].strip())
            else:
                parts.append(part.strip())
        cleaned_quota = ", ".join([p for p in parts if p])
        # Simplify quota
        cleaned_quota = simplify_quota(cleaned_quota)
        new_paket["quota"] = cleaned_quota
        result.append(new_paket)
    return result


# ruff:noqa
# step by step analisis the logic and code then make the full implementation
import json
import re
from pathlib import Path
from typing import Any


# 1. Load data
def load_data(path):
    """Memuat data dari file JSON dan mengembalikan list paket."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data["paket"]


# 2. Print sample
def print_sample(data, label="Sample"):
    print(f"\n{label} (5 data awal):")
    for item in data[:5]:
        print(item)
    """
    Print 5 data awal dari list of dict, untuk tracking antar step.
    Args:
        data: list of dict
        label: str
    """


# 3. Count paket and char
def count_paket_and_char(paket_list):
    """Menghitung jumlah paket dan total karakter JSON dari paket_list."""
    total_product = len(paket_list)
    total_char = sum(len(json.dumps(item, ensure_ascii=False)) for item in paket_list)
    return total_product, total_char


# 4. Uppercase all text
def uppercase_all_text(paket_list):
    """
    Mengubah semua value string pada list of dict menjadi huruf kapital (flat, efisien).
    Return: list of dict dengan semua string upper.
    """
    return [
        {k: v.upper() if isinstance(v, str) else v for k, v in paket.items()}
        for paket in paket_list
    ]


# 5. Exclude product by name prefix
def exclude_product_by_name_prefix(paket_list, product_name):
    """
    Buang paket jika productName diawali salah satu prefix (case-insensitive, koma dipisah).
    Args:
        paket_list: list of dict
        product_name: str, prefix dipisah koma
    Return: list of dict
    """
    prefixes = [p.strip().upper() for p in product_name.split(",") if p.strip()]
    return [
        paket
        for paket in paket_list
        if not any(
            str(paket.get("productName", "")).upper().startswith(prefix)
            for prefix in prefixes
        )
    ]


# 6. Clean all quota & clean_quota
def clean_quota(quota: str) -> str:
    parts = []
    for part in quota.split(","):
        if "/" in part:
            parts.append(part.split("/", 1)[1].strip())
        else:
            parts.append(part.strip())
    return ", ".join([p for p in parts if p])


def clean_all_quota(paket_list):
    for paket in paket_list:
        paket["quota"] = clean_quota(str(paket.get("quota", "")))
    return paket_list


# 7. Simplify all quota & simplify_quota
def simplify_quota(quota: str) -> str:
    # 1. Ganti "DAYS" atau "DAY" atau "HARI" menjadi "D"
    quota = re.sub(r"\b(DAYS?|HARI)\b", "D", quota, flags=re.IGNORECASE)
    # 2. Hilangkan spasi antara angka dan satuan (misal: "1 GB" -> "1GB")
    quota = re.sub(r"(\d+)\s*GB", r"\1GB", quota, flags=re.IGNORECASE)
    # 3. Hilangkan spasi sebelum/antara angka dan "D" (misal: "3 D" -> "3D")
    quota = re.sub(r"(\d+)\s*D", r"\1D", quota, flags=re.IGNORECASE)
    # 4. Standarisasi kata "INTERNET" ke "Net"
    quota = re.sub(r"\bINTERNET\b", "Net", quota, flags=re.IGNORECASE)
    # 5. Hilangkan spasi berlebih
    quota = re.sub(r"\s+", " ", quota).strip()
    return quota


def simplify_all_quota(paket_list):
    for paket in paket_list:
        paket["quota"] = simplify_quota(str(paket.get("quota", "")))
    return paket_list


# 8. Format output
def format_output(paket_list):
    """
    Mengubah list of dict menjadi 1 baris string: #productid|productname(quota)|total#...
    Args:
        paket_list: list of dict
    Returns:
        str: hasil format 1 baris
    """
    parts = []
    for paket in paket_list:
        pid = str(paket.get("productId", "-")).strip()
        pname = str(paket.get("productName", "")).strip()
        quota = str(paket.get("quota", "")).strip()
        total = str(paket.get("total_", "")).strip()
        part = f"#{pid}|{pname}({quota})|{total}"
        parts.append(part)
    return "".join(parts)


HVCDATA_PATH = Path("experiment/HVCDATA.json")


def main():
    import cProfile
    import pstats
    import io

    # Stepwise pipeline profiling
    print("\n=== PROFILING: Stepwise Pipeline ===")
    pr1 = cProfile.Profile()
    pr1.enable()
    paket = load_data(Path("experiment/HVCDATA.json"))
    paket2 = uppercase_all_text(paket)
    filtered = exclude_product_by_name_prefix(paket2, "Facebook")
    cleaned_quota = clean_all_quota(filtered)
    simplified_quota = simplify_all_quota(cleaned_quota)
    output_str = format_output(simplified_quota)
    pr1.disable()
    s1 = io.StringIO()
    ps1 = pstats.Stats(pr1, stream=s1).sort_stats("cumulative")
    ps1.print_stats(10)
    print(s1.getvalue())

    print_sample(simplified_quota, "Setelah simplify_all_quota (quota)")
    print("\n=== OUTPUT AKHIR (stepwise, FULL) ===")
    print(output_str)
    print(f"\nTotal char akhir: {len(output_str)}")
    print(f"Total paket akhir: {len(simplified_quota)}")

    # One-go pipeline profiling
    print("\n=== PROFILING: One-go Pipeline ===")
    pr2 = cProfile.Profile()
    pr2.enable()
    onego = process_all(paket, "Facebook")
    output_str2 = format_output(onego)
    pr2.disable()
    s2 = io.StringIO()
    ps2 = pstats.Stats(pr2, stream=s2).sort_stats("cumulative")
    ps2.print_stats(10)
    print(s2.getvalue())

    print_sample(onego, "Setelah process_all (one-go)")
    print("\n=== OUTPUT AKHIR (one-go, FULL) ===")
    print(output_str2)
    print(f"\nTotal char akhir: {len(output_str2)}")
    print(f"Total paket akhir: {len(onego)}")


if __name__ == "__main__":
    main()
