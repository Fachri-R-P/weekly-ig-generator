import trafilatura
from googlenewsdecoder import gnewsdecoder

MIN_PANJANG = 1500   
MAX_PANJANG = 6000   


def ambil_isi(link: str) -> tuple[str, str] | None:
    try:
        url = gnewsdecoder(link, interval=1).get("decoded_url")
        if not url:
            return None
        teks = trafilatura.extract(trafilatura.fetch_url(url))
    except Exception:
        return None
    if not teks or len(teks) < MIN_PANJANG:
        return None
    return url, teks[:MAX_PANJANG]
