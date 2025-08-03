import re
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor


# Interface Segregation Principle (ISP) - Separate interfaces
class TextCleaner(ABC):
    @abstractmethod
    def clean_text(self, text: str) -> str:
        pass


class QuotaProcessor(ABC):
    @abstractmethod
    def process_quota(self, quota: str) -> str:
        pass


class ResponseFormatter(ABC):
    @abstractmethod
    def format_response(self, paket_list: list[dict], sort_by_name: bool = True) -> str:
        pass


# Single Responsibility Principle (SRP) - Each class has one job
class KeywordCleaner(TextCleaner):
    """Handles keyword removal and replacement operations."""

    def __init__(self):
        # Compile regex patterns for better performance
        self._remove_pattern = re.compile(
            r"|".join(
                re.escape(keyword)
                for keyword in [
                    "DATA NATIONAL/",
                    "LOCAL DATA/",
                    "DATA DPI/",
                    "SMS ONNET/",
                    "VOICE ONNET/",
                ]
            ),
            re.IGNORECASE,
        )

        self._replace_keywords = {"VIDEO", "VAS", "FITA", "COUPON"}
        self._whitespace_pattern = re.compile(r"\s+")

    def clean_text(self, text: str) -> str:
        """Clean text by removing redundant keywords and normalizing whitespace."""
        if not text or not isinstance(text, str):
            return ""

        # Single pass normalization
        cleaned = text.upper().strip(" ,\t")
        cleaned = self._remove_pattern.sub("", cleaned)
        cleaned = self._whitespace_pattern.sub(" ", cleaned).strip()

        return cleaned

    def get_replacement_label(self, text: str) -> str | None:
        """Check if text should be replaced with bonus label."""
        text_upper = text.upper()
        for keyword in self._replace_keywords:
            if keyword in text_upper:
                return f"Bonus {keyword.lower()}"
        return None


class QuotaCleaner(QuotaProcessor):
    """Handles quota string processing with deduplication."""

    def __init__(self, text_cleaner: TextCleaner):
        self._text_cleaner = text_cleaner

    def process_quota(self, quota: str) -> str:
        """Process quota string with efficient deduplication."""
        if not quota:
            return ""

        seen = set()
        parts = []

        for part in str(quota).split(","):
            processed_part = self._process_single_part(part.strip(), seen)
            if processed_part:
                parts.append(processed_part)

        return " ".join("+".join(parts).split()) if parts else ""

    def _process_single_part(self, part: str, seen: set[str]) -> str | None:
        """Process individual quota part."""
        if not part:
            return None

        cleaned = self._text_cleaner.clean_text(part)
        if not cleaned:
            return None

        # Check for replacement first
        if hasattr(self._text_cleaner, "get_replacement_label"):
            replacement = self._text_cleaner.get_replacement_label(cleaned)
            if replacement and replacement not in seen:
                seen.add(replacement)
                return replacement

        # Capitalize and deduplicate
        capitalized = " ".join(word.capitalize() for word in cleaned.split())
        if capitalized and capitalized not in seen:
            seen.add(capitalized)
            return capitalized

        return None


class PaketFormatter(ResponseFormatter):
    """Handles response formatting"""

    def format_response(self, paket_list: list[dict], sort_by_name: bool = True) -> str:
        """Format paket list into response string"""
        if sort_by_name:
            paket_list = sorted(
                paket_list, key=lambda x: str(x.get("productName", "")).lower()
            )

        # Use list comprehension for better performance
        formatted_parts = [self._format_single_paket(paket) for paket in paket_list]

        return "".join(formatted_parts)

    def _format_single_paket(self, paket: dict) -> str:
        """Format single paket entry"""
        pid = f"@{str(paket.get('productId', '-')).strip(' ,\t')}"
        pname = str(paket.get("productName", "")).strip(" ,\t")
        quota = str(paket.get("quota", "")).strip(" ,\t")
        total = str(paket.get("total_", "")).strip(" ,\t")
        return f"{pid}#{pname}({quota})#{total}"


# Dependency Inversion Principle (DIP) - Depend on abstractions
class OptimizedPaketETL:
    """Main ETL processor with dependency injection"""

    def __init__(
        self,
        text_cleaner: TextCleaner = None,
        quota_processor: QuotaProcessor = None,
        formatter: ResponseFormatter = None,
    ):
        # Dependency injection with defaults
        self._text_cleaner = text_cleaner or KeywordCleaner()
        self._quota_processor = quota_processor or QuotaCleaner(self._text_cleaner)
        self._formatter = formatter or PaketFormatter()

    def clean_concurrent(self, paket_list: list[dict], workers: int = 6) -> list[dict]:
        """Clean paket list using concurrent processing"""
        if not paket_list:
            return []

        with ThreadPoolExecutor(max_workers=workers) as executor:
            cleaned_pakets = list(executor.map(self._clean_single_paket, paket_list))

        return cleaned_pakets

    def _clean_single_paket(self, paket: dict) -> dict:
        """Clean single paket with optimized processing"""
        cleaned_paket = {}

        # Process each field efficiently
        for key, value in paket.items():
            if key == "quota" and isinstance(value, str):
                cleaned_paket[key] = self._quota_processor.process_quota(value)
            elif isinstance(value, str):
                # Normalize string fields in single pass
                cleaned_paket[key] = value.upper().strip(" ,\t")
            else:
                cleaned_paket[key] = value

        return cleaned_paket

    def format_response(self, paket_list: list[dict], sort_by_name: bool = True) -> str:
        """Format response using injected formatter"""
        return self._formatter.format_response(paket_list, sort_by_name)

    def process_pipeline(
        self, paket_list: list[dict], workers: int = 6, sort_by_name: bool = True
    ) -> str:
        """Complete processing pipeline"""
        cleaned = self.clean_concurrent(paket_list, workers)
        return self.format_response(cleaned, sort_by_name)


# Factory pattern for easy instantiation
class ETLFactory:
    @staticmethod
    def create_optimized_etl() -> OptimizedPaketETL:
        """Create optimized ETL with default components"""
        text_cleaner = KeywordCleaner()
        quota_processor = QuotaCleaner(text_cleaner)
        formatter = PaketFormatter()
        return OptimizedPaketETL(text_cleaner, quota_processor, formatter)


# --- Refactor: Tambahkan fungsi run_etl untuk profiling terpusat ---
def run_etl(data, workers=6, sort_by_name=True):
    """Jalankan ETL optimized v1 pada data dict (list paket).
    Return: (result_list, response_str)
    """
    etl_optimized = ETLFactory.create_optimized_etl()
    result_optimized = etl_optimized.clean_concurrent(data, workers=workers)
    response_optimized = etl_optimized.format_response(
        result_optimized, sort_by_name=sort_by_name
    )
    return result_optimized, response_optimized
