import cProfile
import io
import json
import pstats
import time
from pathlib import Path

# Import run_etl dari masing-masing approach
from compare.etl_concurent_v1 import run_etl as run_etl_v1
from compare.etl_concurent_v2 import run_etl as run_etl_v2
from compare.etl_concurent_v3 import run_etl as run_etl_v3

# path to HVCDATA.json
HVCDATA_PATH = Path("experiment/HVCDATA.json")


def load_data():
    with open(HVCDATA_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data["paket"]


def profile_etl(name, func, *args, **kwargs):
    print(f"\n=== Profiling: {name} ===")
    pr = cProfile.Profile()
    pr.enable()
    start = time.perf_counter()
    result, response = func(*args, **kwargs)
    end = time.perf_counter()
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
    ps.print_stats(15)
    print(f"Waktu eksekusi: {end - start:.4f} detik")
    print(
        f"Output: {len(result) if result is not None else '-'} produk, {len(response)} char"
    )
    print(f"Sample output: {response[:200]}...")
    print("Profiling summary:")
    print(s.getvalue())


if __name__ == "__main__":
    paket_data = load_data()

    # Profiling v1
    profile_etl("ETL v1 (OOP)", run_etl_v1, paket_data)

    # Profiling v2 (mode sequential)
    profile_etl(
        "ETL v2 (AlgorithmOptimized, sequential)",
        run_etl_v2,
        paket_data,
        mode="sequential",
    )

    # Profiling v2 (mode batched)
    profile_etl(
        "ETL v2 (AlgorithmOptimized, batched)",
        run_etl_v2,
        paket_data,
        mode="batched",
        batch_size=50,
    )

    # Profiling v3
    profile_etl("ETL v3 (Concurrent)", run_etl_v3, paket_data)
