# ruff:noqa ANN001
class BasePaketETL:
    """Base class untuk ETL paket, reusable dan extensible."""

    def __init__(self, config=None):
        self.config = config or {}

    def filter_paket(self, paket_list):
        """Override di subclass jika perlu filter khusus."""
        return paket_list

    def clean_quota(self, quota):
        """Override di subclass jika perlu cleaning khusus."""
        return quota

    def _upper_all(self, paket_list):
        """Uppercase semua value string di setiap paket."""
        result = []
        for paket in paket_list:
            uppered = {
                k: (v.upper() if isinstance(v, str) else v) for k, v in paket.items()
            }
            result.append(uppered)
        return result

    def clean_paket_list(self, paket_list):
        """Contoh logic umum: filter, clean quota, lalu uppercase semua field string."""
        filtered = self.filter_paket(paket_list)
        cleaned = []
        for paket in filtered:
            p = paket.copy()
            if "quota" in p and isinstance(p["quota"], str):
                p["quota"] = self.clean_quota(p["quota"])
            cleaned.append(p)
        # Uppercase semua string field
        cleaned = self._upper_all(cleaned)
        return cleaned

    def format_response(self, paket_list):
        """Override jika format output berbeda."""
        # Contoh format sederhana
        return str(paket_list)
