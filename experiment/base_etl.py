# ruff:noqa ANN001
class BasePaketETL:
    """Base class untuk ETL paket, reusable dan extensible."""

    # ===== Common redundant keywords (berlaku untuk semua subclass) =====
    COMMON_REMOVE_KEYWORDS = [
        "DATA NATIONAL/",
        "LOCAL DATA/",
    ]

    def __init__(self, config=None):
        self.config = config or {}

    def _upper_all(self, paket_list):
        """Step 1: Uppercase semua value string di setiap paket."""
        result = []
        for paket in paket_list:
            uppered = {
                k: (v.upper() if isinstance(v, str) else v) for k, v in paket.items()
            }
            result.append(uppered)
        return result

    def filter_paket(self, paket_list):
        """Step 2: Filter paket by productName prefix (override di subclass jika perlu)."""
        # Default: tidak ada filter, return semua paket
        return paket_list

    def clean_quota(self, quota):
        """Step 3: Hapus redundant keyword umum dari quota. Override di subclass jika perlu cleaning khusus tambahan."""
        cleaned = quota
        for rem in self.COMMON_REMOVE_KEYWORDS:
            cleaned = cleaned.replace(rem, "")
        return cleaned

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
        parts = []
        for paket in paket_list:
            pid = f"id:{paket.get('productId', '-')}"

            pname = paket.get("productName", "")
            quota = paket.get("quota", "")
            total = str(paket.get("total_", ""))
            # Format: id:productid#productname(quota)#total_
            part = f"{pid}#{pname}({quota})#{total}"
            parts.append(part)
        return "#".join(parts)
