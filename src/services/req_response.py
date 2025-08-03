import re

from src.interfaces.ireq_response import IResponseProcessor
from src.mlogger import logger


class ResponseProcessor(IResponseProcessor):
    """Processes response data for paket lists, with config-driven filtering and quota simplification."""

    def __init__(
        self,
        exclude_product: bool = False,
        list_prefixes: list[str] | None = None,
        replace_with_regex: bool = False,
        list_regex_replacement: list[str] | None = None,
    ):
        self.exclude_product = exclude_product
        self.prefixes = [p.strip().upper() for p in (list_prefixes or [])]
        self.replace_with_regex = replace_with_regex
        self.regexs_replacement = list_regex_replacement or []
        self.logger = logger.bind(class_name="ResponseProcessor")

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
        """Simplifies quota string by applying regex replacements if enabled."""
        if not quota or not str(quota).strip():
            return ""
        if self.replace_with_regex and self.regexs_replacement:
            for regex in self.regexs_replacement:
                quota = re.sub(regex, "", quota, flags=re.IGNORECASE)
        quota = re.sub(r"\s+", " ", quota).strip()
        return quota

    def process(self, paket_list: list[dict]) -> list[dict]:
        """Processes a list of paket dictionaries by filtering and cleaning based on config flags."""
        self.logger.info("Processing paket_list", paket_list=paket_list)
        # Log total char and product before processing
        before_total_product = len(paket_list)
        before_total_char = sum(len(str(p)) for p in paket_list)
        self.logger.info(
            "Before processing",
            total_char_before=before_total_char,
            total_product_before=before_total_product,
        )
        result = []
        for paket in paket_list:
            processed = {
                k: v.upper() if isinstance(v, str) else v for k, v in paket.items()
            }
            if (
                self.exclude_product
                and self.prefixes
                and any(
                    str(processed.get("productName", "")).startswith(prefix)
                    for prefix in self.prefixes
                )
            ):
                continue
            raw_quota = str(processed.get("quota", ""))
            cleaned = self.clean_quota_parts(raw_quota)
            simplified = self.simplify_quota_words(cleaned)
            processed["quota"] = simplified
            result.append(processed)
        # Log total char and product after processing
        after_total_product = len(result)
        after_total_char = sum(len(str(p)) for p in result)
        self.logger.info(
            "After processing",
            total_char_after=after_total_char,
            total_product_after=after_total_product,
        )
        self.logger.info("Processed result", result=result)
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
        self.logger.info(
            "Formatting response string",
            result=result,
            trxid=trxid,
            to=to,
            category=category,
        )
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
        response_str = f"trxid={trxid}&to={to}&status=success&message=listpaket in {category} : {final}"
        self.logger.info("Response string created", response=response_str)
        return response_str
