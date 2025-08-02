import json
from pathlib import Path


class QuotaETL:
    # ======= Konfigurasi filter dan keyword =======
    REPLACE_KEYWORDS = ["VIDEO", "VAS", "FITA"]
    REMOVE_KEYWORDS = [
        "DATA NATIONAL/",
        "LOCAL DATA/",
        "DATA DPI/",
        "DATA VIDEO/",  # tambahan dari sample
    ]  # keyword yang akan dihapus dari quota (case insensitive)
    DROP_PRODUCTNAME_PREFIX = ["nonton hemat", "trend micro", "ProtekSi"]

    # ======= ETL Quota (cleaning & normalization) =======
    @classmethod
    def clean_quota(cls, quota: str) -> str:
        """Bersihkan dan normalisasi field quota dengan urutan:

        1. Uppercase untuk normalisasi
        2. Remove redundant keyword
        3. Replace keyword
        5. Cleanup spasi/koma
        6. Return hasil
        """
        parts = []
        for p in quota.split(","):
            # Step 1: Uppercase dan strip untuk normalisasi
            cleaned = p.strip().upper()

            # Step 2: Remove redundant keywords (case insensitive)
            for rem in cls.REMOVE_KEYWORDS:
                cleaned = cleaned.replace(rem.upper(), "")

            # Step 3: Replace keyword (jika ditemukan REPLACE_KEYWORDS)
            found_keyword = None
            for keyword in cls.REPLACE_KEYWORDS:
                if keyword in cleaned:
                    found_keyword = keyword
                    break

            if found_keyword:
                # Ganti dengan 'Bonus {keyword}' (user-friendly lowercase)
                parts.append(f"Bonus {found_keyword.lower()}")
            else:
                # Step 5: Cleanup per part dan kembalikan ke case normal
                cleaned_result = cleaned.strip()
                if cleaned_result:  # hanya tambah jika tidak kosong
                    # Normalize case: capitalize first letter of each word
                    parts.append(
                        " ".join(word.capitalize() for word in cleaned_result.split())
                    )

        # Step 5: Final cleanup - join dan hilangkan spasi ganda
        # Step 6: Return hasil akhir
        result = ", ".join(parts).strip()
        return " ".join(result.split()) if result else ""

    # ======= Step 4: Format Output Akhir Paket =======
    @staticmethod
    def format_paket_output(paket: dict) -> str:
        """Step 4: Format output akhir satu paket dengan separator |.

        productId dibungkus # dan dipisah dengan | untuk setiap field.
        """
        pid = f"#{paket['productId'].strip()}#" if paket.get("productId") else ""
        pname = paket.get("productName", "").strip()
        quota = paket.get("quota", "").rstrip(", ").strip()
        total = str(paket.get("total_", "")).strip()
        return f"{pid}|{pname}|{quota}|{total}"

    # ======= ETL Paket List =======
    @classmethod
    def clean_paket_list(cls, paket_list: list[dict]) -> list[dict]:
        """Bersihkan dan filter list paket sesuai urutan ETL:
        1. Filter productName prefix
        2-3. Bersihkan quota (remove & replace keywords)
        4. Format akan dilakukan di format_paket_output
        """
        cleaned = []
        for paket in paket_list:
            # Step 1: Filter productName prefix (skip paket yang tidak diinginkan)
            pname = str(paket.get("productName", "")).strip().lower()
            if any(pname.startswith(prefix) for prefix in cls.DROP_PRODUCTNAME_PREFIX):
                continue

            # Step 2-3: ETL quota (remove redundant & replace keywords)
            p = paket.copy()
            if "quota" in p and isinstance(p["quota"], str):
                p["quota"] = cls.clean_quota(p["quota"])

            # Ambil field penting dan strip semua (persiapan untuk Step 4: Format output)
            short = {
                k: str(p[k]).strip().rstrip(",") if k in p else ""
                for k in ("productId", "productName", "quota", "total_")
            }
            cleaned.append(short)
        return cleaned


if __name__ == "__main__":
    # Load sample.json
    sample_path = Path(__file__).parent / "sample.json"
    with open(sample_path, encoding="utf-8") as f:
        data = json.load(f)
    paket_list = data.get("paket", [])
    # Hitung jumlah karakter pada sample.json (asli)
    with open(sample_path, encoding="utf-8") as f:
        raw_json = f.read()
    print(f"sample json char = {len(raw_json)} char")

    cleaned = QuotaETL.clean_paket_list(paket_list)
    # Gabungkan hasil ETL jadi satu baris string (paket dipisah |)
    result_line = "|".join(QuotaETL.format_paket_output(p) for p in cleaned)
    print("\nresult :\n")
    print(result_line)
    print(f"\nresult char = {len(result_line)} char")
