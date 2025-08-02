import json
import sys
from pathlib import Path
from typing import Any

from loguru import logger

from experiment.hvc_etl import HVCDataPaketETL  # type: ignore


# --- Loguru bare setup with custom formatter for progress ---
def formatter(record: dict[str, Any]) -> str:
    """Just formatting."""
    end = record["extra"].get("end", "\n")
    level_color = {
        "INFO": "<cyan>",
        "WARNING": "<yellow>",
        "ERROR": "<red>",
        "SUCCESS": "<green>",
        "DEBUG": "<blue>",
    }.get(record["level"].name, "")
    reset = "</>" if level_color else ""
    return f"{level_color}{{level: <8}}{reset}: {{message}}" + end + "{exception}"


logger.remove()  # Remove default handler
logger.add(sys.stderr, format=formatter, level="INFO", colorize=True, enqueue=True)  # type: ignore


def main() -> None:
    import time

    with logger.contextualize():
        logger.info("=== Start ETL HVCDATA.json ===")

    with logger.contextualize():
        logger.info("[Load and clean HVCDATA.json] Starting...")

    file_path = Path(__file__).parent / "HVCDATA.json"
    try:
        with file_path.open(encoding="utf-8") as f:
            data: dict[str, Any] = json.load(f)
    except FileNotFoundError:
        logger.error(
            f"File '{file_path}' tidak ditemukan. Pastikan file tersebut ada di direktori yang sama dengan script ini."
        )
        exit(1)

    paket_list = data.get("paket", [])
    etl = HVCDataPaketETL()

    # Info input
    input_char = len(json.dumps(paket_list))
    input_count = len(paket_list)
    logger.info(f"Input: {input_count} produk, {input_char} char")

    start_time = time.perf_counter()

    logger.bind(end="").info("Cleaning: ")
    cleaned = []
    for _i, row in enumerate(paket_list, 1):
        cleaned.append(etl.clean_paket_list([row])[0])
        logger.opt(raw=True).info(".")
    logger.opt(raw=True).info("\n")

    elapsed = time.perf_counter() - start_time

    # Info output
    output_char = len(etl.format_response(cleaned))
    output_count = len(cleaned)
    logger.info(f"Output: {output_count} produk, {output_char} char")

    logger.info("Output satu baris:")
    logger.info(etl.format_response(cleaned))

    logger.info(
        f"[Load and clean HVCDATA.json] Done. Waktu eksekusi: {elapsed:.4f} detik"
    )


if __name__ == "__main__":
    main()
