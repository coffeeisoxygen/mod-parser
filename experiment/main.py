import json
import sys
from pathlib import Path
from typing import Any

from loguru import logger

from experiment.hvc_etl import HVCDataPaketETL  # type: ignore


# --- Loguru bare setup with custom formatter for progress ---
def formatter(record):
    end = record["extra"].get("end", "\n")
    return "[{time:HH:mm:ss}] {message}" + end + "{exception}"


logger.remove()  # Remove default handler
logger.add(sys.stderr, format=formatter, level="INFO")


def main() -> None:
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

    logger.bind(end="").info("Cleaning: ")
    cleaned = []
    for i, row in enumerate(paket_list, 1):
        cleaned.append(etl.clean_paket_list([row])[0])
        logger.opt(raw=True).info(".")
    logger.opt(raw=True).info("\n")

    logger.info("Output satu baris:")
    logger.info(etl.format_response(cleaned))

    logger.info("[Load and clean HVCDATA.json] Done.")


if __name__ == "__main__":
    main()
