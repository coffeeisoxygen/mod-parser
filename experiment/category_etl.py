from experiment.base_etl import BasePaketETL


class DataPaketETL(BasePaketETL):
    """ETL khusus untuk kategori DATA."""

    pass


class VoiceSmsPaketETL(BasePaketETL):
    """ETL khusus untuk kategori VOICE_SMS."""

    pass


class DigitalOtherPaketETL(BasePaketETL):
    """ETL khusus untuk kategori DIGITAL_OTHER."""

    pass


class DigitalMusicPaketETL(BasePaketETL):
    """ETL khusus untuk kategori DIGITAL_MUSIC."""

    pass


class DigitalGamePaketETL(BasePaketETL):
    """ETL khusus untuk kategori DIGITAL_GAME."""

    pass


class RoamingPaketETL(BasePaketETL):
    """ETL khusus untuk kategori ROAMING."""

    pass


class VfPaketETL(BasePaketETL):
    """ETL khusus untuk kategori VF."""

    pass


class ByuPaketETL(BasePaketETL):
    """ETL khusus untuk kategori BYU."""

    pass


class HvcVoiceSmsPaketETL(BasePaketETL):
    """ETL khusus untuk kategori HVC_VOICE_SMS."""

    pass
