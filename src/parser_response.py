import os

from dotenv import load_dotenv

from src.mlogger import logger


# ================== ENV PARSER UTILS ==================
def parse_env_list(
    key: str, default: str, upper: bool = False, lower: bool = False
) -> list[str]:
    """Parse comma-separated env variable to list, with optional upper/lower."""
    load_dotenv()
    val = os.getenv(key, default)
    items = [k.strip() for k in val.split(",") if k.strip()]
    if upper:
        return [k.upper() for k in items]
    if lower:
        return [k.lower() for k in items]
    return items


# ================== ETL CLASS ==================


# ================== ETL & FORMATTER CLASS ==================
class PaketETL:
    """ETL dan formatter untuk response paket, siap DI dan testable."""

    def __init__(self):
        self.replace_quota_keywords = parse_env_list(
            "REPLACE_KEYWORDS", "VIDEO,VAS,FITA", upper=True
        )
        self.remove_quota_keywords = parse_env_list(
            "REMOVE_KEYWORDS",
            "DATA NATIONAL/,LOCAL DATA/,DATA DPI/,DATA VIDEO/",
            upper=True,
        )
        self.DROP_PRODUCTNAME_PREFIX = parse_env_list(
            "DROP_PRODUCTNAME_PREFIX", "nonton hemat,trend micro,ProtekSi", lower=True
        )

    # --- Step 1: Filter paket by productName prefix ---
    def filter_paket(self, paket_list: list[dict]) -> list[dict]:
        """Filter paket yang productName-nya diawali prefix drop."""
        result = []
        for paket in paket_list:
            pname = str(paket.get("productName", "")).strip().lower()
            if any(pname.startswith(prefix) for prefix in self.DROP_PRODUCTNAME_PREFIX):
                continue
            result.append(paket)
        return result

    # --- Step 2: Remove redundant keyword in quota ---
    def remove_keywords(self, quota: str) -> str:
        cleaned = quota.strip().upper()
        for rem in self.remove_quota_keywords:
            cleaned = cleaned.replace(rem, "")
        return cleaned

    # --- Step 3: Replace keyword in quota ---
    def replace_keywords(self, cleaned: str) -> str | None:
        for keyword in self.replace_quota_keywords:
            if keyword in cleaned:
                return f"Bonus {keyword.lower()}"
        return None

    # --- Step 4: Cleanup and normalize quota part ---
    def cleanup_quota_part(self, cleaned: str) -> str:
        return " ".join(word.capitalize() for word in cleaned.strip().split())

    # --- Step 5: Clean and normalize full quota field ---
    def clean_quota(self, quota: str) -> str:
        parts = []
        for p in quota.split(","):
            cleaned = self.remove_keywords(p)
            replaced = self.replace_keywords(cleaned)
            if replaced:
                parts.append(replaced)
            else:
                cleaned_result = cleaned.strip()
                if cleaned_result:
                    parts.append(self.cleanup_quota_part(cleaned_result))
        result = ", ".join(parts).strip()
        return " ".join(result.split()) if result else ""

    # --- Step 6: Clean all paket (filter, clean quota, keep fields) ---
    def clean_paket_list(self, paket_list: list[dict]) -> list[dict]:
        filtered = self.filter_paket(paket_list)
        cleaned = []
        for paket in filtered:
            p = paket.copy()
            if "quota" in p and isinstance(p["quota"], str):
                p["quota"] = self.clean_quota(p["quota"])
            short = {
                k: str(p[k]).strip().rstrip(",") if k in p else ""
                for k in ("productId", "productName", "quota", "total_")
            }
            cleaned.append(short)
        return cleaned

    # --- Step 7: Format output string ---
    def format_response(
        self,
        response_json: dict,
        trxid: str,
        tujuan: str,
    ) -> str:
        """Format response list_paket menjadi string siap kirim.

        Output: #productid#productname|quota#Rptotal_#...
        """
        with logger.contextualize(trxid=trxid, tujuan=tujuan):
            logger.debug(f"Raw response before transform: {response_json}")
        paket_list = response_json.get("paket", [])
        cleaned_paket_list = self.clean_paket_list(paket_list)
        message_parts = []
        for paket in cleaned_paket_list:
            # Step 1: productId jadi id:productid
            pid = f"id:{paket['productId']}" if paket.get("productId") else "id:-"
            # Step 2: productName dan quota digabung dengan pipe
            pname = paket.get("productName", "")
            quota = paket.get("quota", "")
            name_quota = f"{pname}-{quota}"
            # Step 3: total_ tanpa Rp
            total = paket.get("total_", "")
            # Gabung sesuai format baru
            part = f"{pid}#{name_quota}#{total}"
            message_parts.append(part)
        message = "".join(message_parts)
        result = f"trxid={trxid}&to={tujuan}&status=success&message={message}"
        with logger.contextualize(trxid=trxid, tujuan=tujuan):
            logger.info(
                f"ETL transformation completed. Original pakets: {len(paket_list)}, After ETL: {len(cleaned_paket_list)}"
            )
        return result
