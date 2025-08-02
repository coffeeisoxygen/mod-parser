# ruff:noqa ANN001
class BasePaketETL:
    def _remove_redundant_keywords(self, text):
        """Remove all redundant keywords from text (case-insensitive)."""
        cleaned = text
        for rem in self.COMMON_REMOVE_KEYWORDS:
            cleaned = cleaned.replace(rem.upper(), "")
        return cleaned

    def _replace_keyword(self, text):
        """Replace keyword with 'Bonus {keyword.lower()}' if found, else None."""
        REPLACE_KEYWORDS = ["VIDEO", "VAS", "FITA", "COUPON"]
        for keyword in REPLACE_KEYWORDS:
            if keyword in text:
                return f"Bonus {keyword.lower()}"
        return None

    def _capitalize_words(self, text):
        """Capitalize each word in the text."""
        return " ".join(word.capitalize() for word in text.split())

    """Base class untuk ETL paket, reusable dan extensible."""

    # ===== Common redundant keywords (berlaku untuk semua subclass) =====
    COMMON_REMOVE_KEYWORDS = [
        "DATA NATIONAL/",
        "LOCAL DATA/",
        "DATA DPI/",
    ]

    def __init__(self, config=None):
        self.config = config or {}

    def _upper_all(self, paket_list):
        """Step 1: Uppercase dan strip semua value string di setiap paket."""
        result = []
        for paket in paket_list:
            uppered = {
                k: (v.upper().strip(" ,\t") if isinstance(v, str) else v)
                for k, v in paket.items()
            }
            result.append(uppered)
        return result

    def filter_paket(self, paket_list):
        """Step 2: Filter paket by productName prefix (override di subclass jika perlu)."""
        # Default: tidak ada filter, return semua paket
        return paket_list

    def clean_quota(self, quota):
        """
        Bersihkan dan normalisasi field quota dengan urutan modular:
        1. Uppercase & strip per part
        2. Remove redundant keyword
        3. Replace keyword (jika ada)
        4. Capitalize per kata
        5. Deduplikasi label
        6. Final join pakai '+' & strip
        """
        seen = set()
        parts = []
        for p in str(quota).split(","):
            cleaned = p.strip().upper()
            cleaned = self._remove_redundant_keywords(cleaned)
            replaced = self._replace_keyword(cleaned)
            label = replaced if replaced else None
            if label:
                if label not in seen:
                    parts.append(label)
                    seen.add(label)
            else:
                cleaned_result = cleaned.strip()
                if cleaned_result:
                    cap = self._capitalize_words(cleaned_result)
                    if cap not in seen:
                        parts.append(cap)
                        seen.add(cap)
        result = "+".join(parts).strip()
        return " ".join(result.split()) if result else ""

    def clean_paket_list(self, paket_list):
        """
        Pipeline ETL umum:
        1. Uppercase semua field string
        2. Filter paket (by productName prefix, jika ada)
        3. Clean quota (remove redundant keyword)
        """
        # Step 1: Uppercase dulu
        paket_list = self._upper_all(paket_list)
        # Step 2: Filter paket
        filtered = self.filter_paket(paket_list)
        # Step 3: Clean quota
        cleaned = []
        for paket in filtered:
            p = paket.copy()
            if "quota" in p and isinstance(p["quota"], str):
                p["quota"] = self.clean_quota(p["quota"])
            cleaned.append(p)
        return cleaned

    def format_response(self, paket_list):
        """
        Format output satu baris untuk semua kelas:
        id:productid#productname(quota)#total_#id:productid#productname(quota)#total_...
        """
        result = []
        for paket in paket_list:
            pid = f"@{str(paket.get('productId', '-')).strip(' ,\t')}"
            pname = str(paket.get("productName", "")).strip(" ,\t")
            quota = str(paket.get("quota", "")).strip(" ,\t")
            total = str(paket.get("total_", "")).strip(" ,\t")
            # Format: @productid#productname(quota)#total_ (tanpa '#' setelah total, antar paket langsung '@')
            part = f"{pid}#{pname}({quota})#{total}"
            result.append(part)
        # Gabungkan: hilangkan '#' sebelum '@' berikutnya, dan tidak ada '#' di akhir
        return "".join(result)
