import io
import re
from typing import Optional
from config import settings


def _emv_compute_crc16(payload: str) -> str:
    """Calcula CRC16-CCITT para o payload PIX."""
    crc = 0xFFFF
    for byte in payload.encode("utf-8"):
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0x8408
            else:
                crc >>= 1
    return format(crc, "04X")


def _emv_field(tag: str, value: str) -> str:
    """Formata campo EMV com tag + tamanho + valor."""
    size = len(value.encode("utf-8"))
    return f"{tag}{size:02d}{value}"


def gerar_brcode(
    pix_key: str,
    merchant_name: str = "PyPizzas",
    merchant_city: str = "Sao Paulo",
    amount: Optional[float] = None,
    txid: str = "***",
    description: Optional[str] = None,
) -> str:
    key = re.sub(r"\s*\(.*?\)", "", pix_key).strip()

    gui = _emv_field("00", "br.gov.bcb.pix")
    key_field = _emv_field("01", key)

    if description:
        key_field += _emv_field("02", description[:40])

    merchant_account = _emv_field("26", gui + key_field)

    payload = "000201"
    payload += merchant_account
    payload += _emv_field("52", "0000")
    payload += _emv_field("53", "986")

    if amount is not None and amount > 0:
        payload += _emv_field("54", f"{amount:.2f}")

    payload += _emv_field("58", "BR")
    payload += _emv_field("59", merchant_name[:25])
    payload += _emv_field("60", merchant_city[:15])

    txid_field = _emv_field("05", txid[:25])
    payload += _emv_field("62", txid_field)

    payload += "6304"
    crc = _emv_compute_crc16(payload)
    return payload + crc


def gerar_qrcode_png(brcode: str) -> Optional[bytes]:
    """Gera imagem PNG do QR Code a partir do BR Code."""
    try:
        import qrcode
        from qrcode.image.styledpil import StyledPilImage
        from qrcode.image.styles.moduledrawers import RoundedModuleDrawer

        qr = qrcode.QRCode(box_size=10, border=2)
        qr.add_data(brcode)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf.getvalue()
    except ImportError:
        return None


def gerar_pix_payload(
    amount: Optional[float] = None, description: Optional[str] = None
) -> str:
    return gerar_brcode(
        pix_key=settings.pix_key,
        merchant_name="PyPizzas",
        merchant_city="Sao Paulo",
        amount=amount,
        txid="***",
        description=description,
    )


def gerar_pix_qrcode(
    amount: Optional[float] = None, description: Optional[str] = None
) -> Optional[bytes]:
    brcode = gerar_pix_payload(amount, description)
    return gerar_qrcode_png(brcode)
