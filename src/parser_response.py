from .mlogger import logger


def transform_list_paket_response(
    response_json: dict, trxid: str, tujuan: str, kolom: list[str] | None = None
) -> str:
    """Transformasi response list_paket menjadi format string.

    trxid=[trxid]&to=[tujuan]&message=list paket = #productId#productName#total_ ...
    Kolom: list kolom yang ingin ditampilkan, default ['productId', 'productName', 'total_']
    """
    with logger.contextualize(trxid=trxid, tujuan=tujuan):
        logger.debug(f"Raw response before transform: {response_json}")
    paket_list = response_json.get("paket", [])
    message_parts = []
    if not kolom:
        kolom = ["productId", "productName", "total_"]
    # Pastikan productId selalu di depan
    if "productId" not in kolom:
        kolom = ["productId", *kolom]
    for paket in paket_list:
        product_id = str(paket.get("productId", ""))
        # Ambil kolom lain selain productId
        other_values = [str(paket.get(k, "")) for k in kolom if k != "productId"]
        # Format: -productId#kolom1#kolom2-
        part = f"-{product_id}"
        if other_values:
            part += "#" + "#".join(other_values)
        part += "-"
        message_parts.append(part)
    # Gabungkan tanpa spasi antar paket, dan pastikan tidak ada double --
    message = "list paket = " + "".join(message_parts)
    # Hilangkan double dash jika ada (misal: -...--...-)
    while "--" in message:
        message = message.replace("--", "-")
    result = f"trxid={trxid}&to={tujuan}&message={message}"
    return result
