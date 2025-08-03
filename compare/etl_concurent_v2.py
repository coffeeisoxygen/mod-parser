import json
import re
from functools import lru_cache


class AlgorithmOptimizedETL:
    """Maximum logic optimization BEFORE hardware utilization
    Focus: Minimize operations, maximize algorithmic efficiency
    """

    def __init__(self):
        # Pre-compile all regex patterns (one-time cost)
        self._setup_patterns()

        # Pre-built lookup structures for O(1) operations
        self._setup_lookups()

        # Cache for expensive operations
        self._quota_cache = {}
        self._text_cache = {}

    def _setup_patterns(self):
        """Setup all regex patterns once"""
        # Single regex for all removals (more efficient than multiple replace calls)
        remove_keywords = [
            "DATA NATIONAL/",
            "LOCAL DATA/",
            "DATA DPI/",
            "SMS ONNET/",
            "VOICE ONNET/",
        ]

        # Combine all patterns into one for single-pass processing
        self._remove_pattern = re.compile(
            "|".join(re.escape(kw) for kw in remove_keywords), re.IGNORECASE
        )

        # Whitespace normalization pattern
        self._whitespace_pattern = re.compile(r"\s+")

        # Pattern to extract meaningful parts from quota strings
        self._quota_split_pattern = re.compile(r"[,+]")

    def _setup_lookups(self):
        """Pre-build lookup structures for O(1) operations"""
        self._replace_keywords = {"VIDEO", "VAS", "FITA", "COUPON"}

        # Pre-build bonus labels for instant lookup
        self._bonus_labels = {
            kw: f"Bonus {kw.lower()}" for kw in self._replace_keywords
        }

    @lru_cache(maxsize=512)  # Cache expensive text operations
    def _clean_text_cached(self, text: str) -> str:
        """Cached text cleaning for repeated patterns"""
        if not text:
            return ""

        # Single pass: upper + strip + remove keywords + normalize whitespace
        cleaned = text.upper().strip(" ,\t")
        cleaned = self._remove_pattern.sub("", cleaned)
        cleaned = self._whitespace_pattern.sub(" ", cleaned).strip()

        return cleaned

    @lru_cache(maxsize=256)  # Cache bonus label detection
    def _get_bonus_label_cached(self, text: str) -> str | None:
        """Cached bonus label detection"""
        text_upper = text.upper()
        for keyword in self._replace_keywords:
            if keyword in text_upper:
                return self._bonus_labels[keyword]
        return None

    def _process_quota_optimized(self, quota: str) -> str:
        """Optimized quota processing with minimal operations"""
        if not quota:
            return ""

        # Check cache first
        cache_key = quota
        if cache_key in self._quota_cache:
            return self._quota_cache[cache_key]

        # Process with minimal string operations
        seen = set()
        parts = []

        # Split once, process efficiently
        raw_parts = self._quota_split_pattern.split(str(quota))

        for part in raw_parts:
            if not part.strip():
                continue

            processed = self._process_quota_part_optimized(part.strip(), seen)
            if processed:
                parts.append(processed)

        result = " ".join("+".join(parts).split()) if parts else ""

        # Cache the result
        self._quota_cache[cache_key] = result
        return result

    def _process_quota_part_optimized(self, part: str, seen: set[str]) -> str | None:
        """Process single quota part with O(1) operations where possible"""
        cleaned = self._clean_text_cached(part)
        if not cleaned:
            return None

        # Check for bonus replacement first (O(1) lookup)
        bonus_label = self._get_bonus_label_cached(cleaned)
        if bonus_label and bonus_label not in seen:
            seen.add(bonus_label)
            return bonus_label

        # Capitalize efficiently
        capitalized = " ".join(word.capitalize() for word in cleaned.split())
        if capitalized and capitalized not in seen:
            seen.add(capitalized)
            return capitalized

        return None

    def _clean_single_paket_optimized(self, paket: dict) -> dict:
        """Optimized single paket processing"""
        # Pre-allocate result dict with known size
        result = {}

        for key, value in paket.items():
            if key == "quota" and isinstance(value, str):
                result[key] = self._process_quota_optimized(value)
            elif isinstance(value, str):
                # Use cached cleaning for repeated strings
                result[key] = self._clean_text_cached(value)
            else:
                result[key] = value

        return result

    def clean_sequential_optimized(self, paket_list: list[dict]) -> list[dict]:
        """Sequential processing with maximum algorithmic optimization"""
        if not paket_list:
            return []

        # Process with minimal overhead
        return [self._clean_single_paket_optimized(paket) for paket in paket_list]

    def clean_batched(
        self, paket_list: list[dict], batch_size: int = 100
    ) -> list[dict]:
        """Batch processing for memory-constrained environments"""
        if not paket_list:
            return []

        results = []

        # Process in batches to control memory usage
        for i in range(0, len(paket_list), batch_size):
            batch = paket_list[i : i + batch_size]
            batch_results = self.clean_sequential_optimized(batch)
            results.extend(batch_results)

            # Optional: Clear cache periodically to prevent memory buildup
            if i % (batch_size * 10) == 0:  # Every 10 batches
                self._quota_cache.clear()
                self._text_cache.clear()

        return results

    def format_response_optimized(
        self, paket_list: list[dict], sort_by_name: bool = True
    ) -> str:
        """Memory-efficient response formatting"""
        if not paket_list:
            return ""

        # Sort efficiently if needed
        if sort_by_name:
            paket_list.sort(key=lambda x: str(x.get("productName", "")).lower())

        # Build response with minimal string operations
        parts = []
        for paket in paket_list:
            # Pre-process all string operations
            pid = f"@{str(paket.get('productId', '-')).strip(' ,\t')}"
            pname = str(paket.get("productName", "")).strip(" ,\t")
            quota = str(paket.get("quota", "")).strip(" ,\t")
            total = str(paket.get("total_", "")).strip(" ,\t")

            parts.append(f"{pid}#{pname}({quota})#{total}")

        return "".join(parts)

    def process_with_memory_awareness(
        self, paket_list: list[dict], available_memory_mb: int = 256
    ) -> str:
        """Process with memory constraints in mind"""
        data_size = len(paket_list)

        # Estimate optimal batch size based on available memory
        # Rough estimation: each paket ~1KB, want to use ~50% of available memory
        estimated_batch_size = max(
            10, min(1000, (available_memory_mb * 512) // data_size)
        )

        print(
            f"INFO: Processing {data_size} items with batch size {estimated_batch_size}"
        )

        # Use batched processing for memory efficiency
        cleaned = self.clean_batched(paket_list, estimated_batch_size)
        return self.format_response_optimized(cleaned)

    def get_cache_stats(self) -> dict:
        """Get caching statistics for performance analysis"""
        return {
            "text_cache_size": len(self._text_cache),
            "quota_cache_size": len(self._quota_cache),
            "text_cache_info": self._clean_text_cached.cache_info(),
            "bonus_cache_info": self._get_bonus_label_cached.cache_info(),
        }

    def clear_caches(self):
        """Clear all caches to free memory"""
        self._quota_cache.clear()
        self._text_cache.clear()
        self._clean_text_cached.cache_clear()
        self._get_bonus_label_cached.cache_clear()


# Alternative: Stream processing for very large datasets
class StreamETL:
    """Stream processing for extremely large datasets that don't fit in memory"""

    def __init__(self):
        self.etl = AlgorithmOptimizedETL()

    def process_stream(self, input_file: str, output_file: str, chunk_size: int = 50):
        """Process JSON file in streams"""
        with open(input_file, encoding="utf-8") as infile:
            data = json.load(infile)

        paket_list = data.get("paket", [])

        with open(output_file, "w", encoding="utf-8") as outfile:
            outfile.write("")  # Initialize file

            # Process in chunks
            for i in range(0, len(paket_list), chunk_size):
                chunk = paket_list[i : i + chunk_size]
                cleaned_chunk = self.etl.clean_sequential_optimized(chunk)
                response_chunk = self.etl.format_response_optimized(
                    cleaned_chunk, sort_by_name=False
                )

                outfile.write(response_chunk)

                # Clear caches periodically
                if i % (chunk_size * 5) == 0:
                    self.etl.clear_caches()


# --- Refactor: Tambahkan fungsi run_etl untuk profiling terpusat ---
def run_etl(
    data, mode="sequential", batch_size=50, available_memory_mb=128, sort_by_name=True
):
    """Jalankan AlgorithmOptimizedETL pada data dict (list paket).
    mode: 'sequential', 'batched', 'memory_aware'
    Return: (result_list, response_str)
    """
    etl = AlgorithmOptimizedETL()
    if mode == "sequential":
        result = etl.clean_sequential_optimized(data)
        response = etl.format_response_optimized(result, sort_by_name=sort_by_name)
        return result, response
    elif mode == "batched":
        result = etl.clean_batched(data, batch_size=batch_size)
        response = etl.format_response_optimized(result, sort_by_name=sort_by_name)
        return result, response
    elif mode == "memory_aware":
        response = etl.process_with_memory_awareness(
            data, available_memory_mb=available_memory_mb
        )
        return None, response
    else:
        raise ValueError("Unknown mode for run_etl")
