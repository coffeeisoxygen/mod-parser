from experiment.base_etl import BasePaketETL
from experiment.hvc_etl import HVCDataPaketETL


def get_etl_by_category(category: str):
    """Factory function untuk memilih ETL class sesuai kategori.

    Tambahkan mapping baru jika ada kategori lain.
    """
    category = (category or "").upper()
    if category == "HVC_DATA":
        return HVCDataPaketETL()
    # Tambahkan kategori lain di sini jika perlu
    return BasePaketETL()
