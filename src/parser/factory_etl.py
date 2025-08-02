from src.parser.base_etl import BasePaketETL
from src.parser.category_etl import (
    ByuPaketETL,
    DataPaketETL,
    DigitalGamePaketETL,
    DigitalMusicPaketETL,
    DigitalOtherPaketETL,
    HvcVoiceSmsPaketETL,
    RoamingPaketETL,
    VfPaketETL,
    VoiceSmsPaketETL,
)


def get_etl_by_category(category: str):
    """Factory function untuk memilih ETL class sesuai kategori.

    Tambahkan mapping baru jika ada kategori lain.
    """
    category = (category or "").upper()
    mapping = {
        "DATA": DataPaketETL,
        "VOICE_SMS": VoiceSmsPaketETL,
        "DIGITAL_OTHER": DigitalOtherPaketETL,
        "DIGITAL_MUSIC": DigitalMusicPaketETL,
        "DIGITAL_GAME": DigitalGamePaketETL,
        "ROAMING": RoamingPaketETL,
        "VF": VfPaketETL,
        "BYU": ByuPaketETL,
        "HVC_VOICE_SMS": HvcVoiceSmsPaketETL,
    }
    if category in mapping:
        return mapping[category]()
    return BasePaketETL()
