import json
from pathlib import Path
from typing import Any

from base_etl import BasePaketETL

# Add import for LoggerManager and LogConfig
from src.mlogger import LogConfig, LoggerManager, logger_progress


def main() -> None:
    # Setup logging
    logger_manager: LoggerManager = LoggerManager(
        LogConfig(level="INFO", to_terminal=True)
    )
    logger_manager.setup()

    # Track process timing using log_block context manager
    with LoggerManager.log_block("Load and clean HVCDATA.json", level="INFO"):
        # Load sample HVCDATA.json
        file_path: Path = Path(__file__).parent / "HVCDATA.json"
        try:
            with file_path.open(encoding="utf-8") as f:
                data: dict[str, Any] = json.load(f)
        except FileNotFoundError:
            print(
                f"File '{file_path}' tidak ditemukan. Pastikan file tersebut ada di direktori yang sama dengan script ini."
            )
            exit(1)

        paket_list: list[dict[str, Any]] = data.get("paket", [])
        etl: BasePaketETL = BasePaketETL()

        # Contoh progress bar dengan logger_progress
        logger_progress.bind(end="").info("Cleaning: ")
        cleaned: list[dict[str, Any]] = []
        for i, row in enumerate(paket_list, 1):
            cleaned.append(etl.clean_paket_list([row])[0])
            logger_progress.opt(raw=True).info(".")
        logger_progress.opt(raw=True).info("\n")

        logger_progress.info("Contoh hasil clean_paket_list (5 data pertama):")
        for row in cleaned[:5]:
            logger_progress.info(f"Hasil: {row}")


if __name__ == "__main__":
    main()
