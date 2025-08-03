# ruff:noqa
# step by step analisis the logic and code then make the full implementation
import json
import re
from pathlib import Path
from typing import Any


# Regex simplifikasi quota
def simplify_quota(quota: str) -> str:
    # 1. Ganti "DAYS" atau "DAY" atau "HARI" menjadi "D"
    quota = re.sub(r"\b(DAYS?|HARI)\b", "D", quota, flags=re.IGNORECASE)
    # 2. Hilangkan spasi antara angka dan satuan (misal: "1 GB" -> "1GB")
    quota = re.sub(r"(\d+)\s*GB", r"\1GB", quota, flags=re.IGNORECASE)
    # 3. Hilangkan spasi sebelum/antara angka dan "D" (misal: "3 D" -> "3D")
    quota = re.sub(r"(\d+)\s*D", r"\1D", quota, flags=re.IGNORECASE)
    # 4. Standarisasi kata "NATIONAL" dan "NASIONAL" ke "NASIONAL"
    quota = re.sub(r"\bNATIONAL\b", "NASIONAL", quota, flags=re.IGNORECASE)
    # 5. Hilangkan spasi berlebih
    quota = re.sub(r"\s+", " ", quota).strip()
    return quota


def simplify_all_quota(paket_list):
    for paket in paket_list:
        paket["quota"] = simplify_quota(str(paket.get("quota", "")))
    return paket_list


def format_output(paket_list):
    """
    Mengubah list of dict menjadi 1 baris string: #productid|productname(quota)|total#...
    """
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


HVCDATA_PATH = Path("experiment/HVCDATA.json")


def load_data(path):
    """Memuat data dari file JSON dan mengembalikan list paket."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data["paket"]


def count_paket_and_char(paket_list):
    """Menghitung jumlah paket dan total karakter JSON dari paket_list."""
    total_product = len(paket_list)
    total_char = sum(len(json.dumps(item, ensure_ascii=False)) for item in paket_list)
    return total_product, total_char


def uppercase_all_text(paket_list):
    """
    Mengubah semua value string pada list of dict menjadi huruf kapital (flat, efisien).
    Return: list of dict dengan semua string upper.
    """
    return [
        {k: v.upper() if isinstance(v, str) else v for k, v in paket.items()}
        for paket in paket_list
    ]


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


# Bersihkan bagian sebelum '/' pada setiap part quota
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


# ## Place holder one go proses
# def process_all(paket_list, prefix_filter):
#     prefixes = [p.strip().upper() for p in prefix_filter.split(",") if p.strip()]
#     result = []
#     for paket in paket_list:
#         # Uppercase semua value string
#         new_paket = {
#             k: v.upper() if isinstance(v, str) else v for k, v in paket.items()
#         }
#         # Filter prefix productName
#         if any(
#             str(new_paket.get("productName", "")).startswith(prefix)
#             for prefix in prefixes
#         ):
#             continue
#         # Clean quota
#         quota = str(new_paket.get("quota", ""))
#         parts = []
#         for part in quota.split(","):
#             if "/" in part:
#                 parts.append(part.split("/", 1)[1].strip())
#             else:
#                 parts.append(part.strip())
#         new_paket["quota"] = ", ".join([p for p in parts if p])
#         result.append(new_paket)
#     return result


def main():
    # ini simulasi Load / Menerima Response dari API
    paket = load_data(Path("experiment/HVCDATA.json"))
    print_sample(paket, "Setelah load data")
    total_product, total_char = count_paket_and_char(paket)
    print(f"total char : {total_char}")
    print(f"total produk : {total_product}")

    # Proses pertama: uppercase semua teks
    paket = uppercase_all_text(paket)
    print_sample(paket, "Setelah uppercase_all_text")
    total_product, total_char = count_paket_and_char(paket)
    print(f"total char : {total_char}")
    print(f"total produk : {total_product}")

    # Proses Kedua: Buang Product yang tidak relevan
    # Contoh filter: buang produk yang nama depannya 'FACEBOOK', 'SUPER SERU INTERNET'
    filtered = exclude_product_by_name_prefix(paket, "Facebook")
    print_sample(filtered, "Setelah filter prefix")
    filtered_product, filtered_char = count_paket_and_char(filtered)
    print(f"total char : {filtered_char}")
    print(f"total produk : {filtered_product}")

    # Proses Ketiga: Bersihkan bagian sebelum '/' pada setiap part quota
    cleaned_quota = clean_all_quota(filtered)
    print_sample(cleaned_quota, "Setelah clean_all_quota (quota)")
    cleaned_product, cleaned_char = count_paket_and_char(cleaned_quota)
    print(f"total char : {cleaned_char}")
    print(f"total produk : {cleaned_product}")

    # Proses Keempat: Simplifikasi quota dengan regex
    simplified_quota = simplify_all_quota(cleaned_quota)
    print_sample(simplified_quota, "Setelah simplify_all_quota (quota)")

    # Proses terakhir: format output menjadi 1 baris string
    output_str = format_output(simplified_quota)
    print("\n=== OUTPUT AKHIR (1 baris, 1000 char pertama) ===")
    print(output_str[:1000] + ("..." if len(output_str) > 1000 else ""))


if __name__ == "__main__":
    # profiler = cProfile.Profile()
    # profiler.enable()
    main()  # Call the function you want to profile
    # profiler.disable()

    # stats = pstats.Stats(profiler)
    # stats.sort_stats("cumulative")  # Sort by cumulative time
    # stats.print_stats()
