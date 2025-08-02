import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


class ConcurrentPaketETL:
    COMMON_REMOVE_KEYWORDS = [
        "DATA NATIONAL/",
        "LOCAL DATA/",
        "DATA DPI/",
        "SMS ONNET/",
        "VOICE ONNET/",
    ]

    REPLACE_KEYWORDS = ["VIDEO", "VAS", "FITA", "COUPON"]

    def __init__(self):
        pass

    def _upper_all(self, paket_list):
        return [
            {
                k: (v.upper().strip(" ,\t") if isinstance(v, str) else v)
                for k, v in paket.items()
            }
            for paket in paket_list
        ]

    def _remove_redundant_keywords(self, text):
        cleaned = text
        for rem in self.COMMON_REMOVE_KEYWORDS:
            cleaned = cleaned.replace(rem.upper(), "")
        return cleaned

    def _replace_keyword(self, text):
        for keyword in self.REPLACE_KEYWORDS:
            if keyword in text:
                return f"Bonus {keyword.lower()}"
        return None

    def _capitalize_words(self, text):
        return " ".join(word.capitalize() for word in text.split())

    def _process_quota_part(self, part, seen):
        cleaned = part.strip().upper()
        cleaned = self._remove_redundant_keywords(cleaned)
        replaced = self._replace_keyword(cleaned)
        label = replaced if replaced else None
        if label:
            if label not in seen:
                seen.add(label)
                return label
        else:
            cleaned_result = cleaned.strip()
            if cleaned_result:
                cap = self._capitalize_words(cleaned_result)
                if cap not in seen:
                    seen.add(cap)
                    return cap
        return None

    def clean_quota(self, quota):
        seen = set()
        parts = []
        for p in str(quota).split(","):
            result = self._process_quota_part(p, seen)
            if result:
                parts.append(result)
        result = "+".join(parts).strip()
        return " ".join(result.split()) if result else ""

    def _clean_single_paket(self, paket):
        p = paket.copy()
        if "quota" in p and isinstance(p["quota"], str):
            p["quota"] = self.clean_quota(p["quota"])
        return p

    def clean_concurrent(self, paket_list, workers=None):
        uppered = self._upper_all(paket_list)
        if workers is None:
            workers = os.cpu_count()
        with ThreadPoolExecutor(max_workers=workers) as executor:
            cleaned = list(executor.map(self._clean_single_paket, uppered))
        return cleaned

    def format_response(self, paket_list, sort_by_name=True):
        if sort_by_name:
            paket_list = sorted(
                paket_list, key=lambda x: str(x.get("productName", "")).lower()
            )
        result = []
        for paket in paket_list:
            pid = f"@{str(paket.get('productId', '-')).strip(' ,\t')}"
            pname = str(paket.get("productName", "")).strip(" ,\t")
            quota = str(paket.get("quota", "")).strip(" ,\t")
            total = str(paket.get("total_", "")).strip(" ,\t")
            part = f"{pid}#{pname}({quota})#{total}"
            result.append(part)
        return "".join(result)


# === TEST ===
if __name__ == "__main__":
    import time

    etl = ConcurrentPaketETL()
    data = json.loads(Path("experiment/HVCDATA.json").read_text(encoding="utf-8"))
    print("INFO    : [Load and clean HVCDATA.json] Starting...")
    print(f"INFO    : Input: {len(data['paket'])} produk")

    start = time.perf_counter()
    result = etl.clean_concurrent(data["paket"])
    response = etl.format_response(result)
    end = time.perf_counter()

    print(f"INFO    : Output: {len(result)} produk, {len(response)} char")
    print("INFO    : Output satu baris:")
    print(f"INFO    : {response[:200]}...")
    print(
        f"INFO    : [Load and clean HVCDATA.json] Done. Waktu eksekusi: {end - start:.4f} detik"
    )
