import re
from typing import ClassVar


class ResponseProcessor:
    """Processes response data for paket lists, including filtering by prefix, cleaning, simplifying quota descriptions, and formatting final response."""

    default_regexs_replacement: ClassVar[list[str]] = [
        r"\b(DAYS?|HARI)\b",
        r"(\d+)\s*GB",
        r"(\d+)\s*D",
        r"\bINTERNET\b",
    ]

    def __init__(
        self, prefix_filter: str = "", regexs_replacement: list[str] | None = None
    ):
        """Initialize the processor with optional comma-separated prefix filter and regex list."""
        self.prefixes = [
            p.strip().upper() for p in prefix_filter.split(",") if p.strip()
        ]
        self.regexs_replacement = regexs_replacement or self.default_regexs_replacement

    def clean_quota_parts(self, quota: str) -> str:
        """Cleans quota string by removing text before '/' and extra spaces."""
        parts = []
        for part in quota.split(","):
            if "/" in part:
                parts.append(part.split("/", 1)[1].strip())
            else:
                parts.append(part.strip())
        return ", ".join(p for p in parts if p)

    def simplify_quota_words(self, quota: str) -> str:
        """Simplifies quota string by replacing certain words and formatting using dynamic regex list."""
        if not quota or not str(quota).strip():
            return ""
        # Apply each regex in order; for demo, use fixed replacements for each pattern
        for regex in self.regexs_replacement:
            if regex == r"\b(DAYS?|HARI)\b":
                quota = re.sub(regex, "D", quota, flags=re.IGNORECASE)
            elif regex == r"(\d+)\s*GB":
                quota = re.sub(regex, r"\1GB", quota, flags=re.IGNORECASE)
            elif regex == r"(\d+)\s*D":
                quota = re.sub(regex, r"\1D", quota, flags=re.IGNORECASE)
            elif regex == r"\bINTERNET\b":
                quota = re.sub(regex, "Net", quota, flags=re.IGNORECASE)
            else:
                quota = re.sub(regex, "", quota, flags=re.IGNORECASE)
        quota = re.sub(r"\s+", " ", quota).strip()
        return quota

    def process(self, paket_list: list[dict]) -> list[dict]:
        """Processes a list of paket dictionaries by filtering, cleaning, and simplifying quota fields.

        This method applies the following transformations to each paket dictionary:
        - Filters out paket entries based on the specified prefix.
        - Cleans and simplifies the quota description.

        Args:
            paket_list (list[dict]): List of paket dictionaries to process.

        Returns:
            list[dict]: List of processed paket dictionaries.
        """
        result = []
        for paket in paket_list:
            processed = {
                k: v.upper() if isinstance(v, str) else v for k, v in paket.items()
            }
            if any(
                str(processed.get("productName", "")).startswith(prefix)
                for prefix in self.prefixes
            ):
                continue

            raw_quota = str(processed.get("quota", ""))
            cleaned = self.clean_quota_parts(raw_quota)
            simplified = self.simplify_quota_words(cleaned)
            processed["quota"] = simplified
            result.append(processed)
        return result

    def to_response_string(
        self,
        result: list[dict],
        trxid: str,
        to: str,
        category: str = "paket",
        sort_by_name: bool = False,
    ) -> str:
        """Format hasil menjadi satu string line untuk response.

        Format: trxid=...&to=...&status=success&message=listpaket in {category} : {result}
        """
        if sort_by_name:
            result = sorted(result, key=lambda p: str(p.get("productName", "")).lower())
        parts = []
        for p in result:
            pid = f"@{str(p.get('productId', '')).strip()}"
            name = str(p.get("productName", "")).strip()
            quota = str(p.get("quota", "")).strip() or "-"
            total = str(p.get("total_", "")).strip()
            parts.append(f"{pid}#{name}({quota})#{total}")
        final = "".join(parts)
        return f"trxid={trxid}&to={to}&status=success&message=listpaket in {category} : {final}"
