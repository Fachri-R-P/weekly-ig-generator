# mengambil ambil berita properti dari RSS, filter, dan hapus duplikat
import re
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

import feedparser

# Google News RSS: stabil, gratis, tanpa API key. Tambah query sesuai kebutuhan.
QUERIES = [
    "properti Indonesia",
    "harga rumah Jakarta",
    "KPR suku bunga Bank Indonesia",
    "apartemen Jakarta",
    "perumahan Indonesia",
    "rumah subsidi FLPP",
    "developer properti",
]

# Artikel harus memuat salah satu kata ini (filter relevansi)
KEYWORDS = ["properti", "rumah", "apartemen", "kpr", "hunian", "tanah",
            "developer", "perumahan", "rusun", "real estate"]

# Judul yang memuat kata ini dibuang (berita luar negeri / bukan properti)
KATA_ASING = ["portugal", "vietnam", "amerika", "china", "tiongkok", "inggris",
                "australia", "thailand", "malaysia", "singapura", "eropa", "jepang",
                "korea", "dubai", "india", "filipina", "spanyol", "kanada"]
KATA_NOISE = ["imigrasi", "wna", "pembunuhan", "kebakaran", "mayat",
                "ditangkap", "narkoba", "tewas"]

# Sumber yang memang berita luar negeri
SUMBER_DIBLOKIR = {"Vietnam.vn"}

# Maksimal upload berita
MAX_AGE_DAYS = 7


def feed_url(query: str) -> str:
    return (f"https://news.google.com/rss/search?q={quote(query)}"
            f"+when:{MAX_AGE_DAYS}d&hl=id&gl=ID&ceid=ID:id")


def normalisasi_judul(judul: str) -> str:
    # Buang ' - Nama Sumber' di akhir, huruf kecil, hapus simbol
    judul = judul.rsplit(" - ", 1)[0].lower()
    return re.sub(r"[^a-z0-9 ]", "", judul).strip()


def ambil_semua() -> list[dict]:
    batas = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)
    hasil = []
    for q in QUERIES:
        feed = feedparser.parse(feed_url(q))
        for e in feed.entries:
            if not getattr(e, "published_parsed", None):
                continue
            tanggal = datetime.fromtimestamp(time.mktime(e.published_parsed), timezone.utc)
            if tanggal < batas:
                continue
            hasil.append({
                "judul": e.title,
                "link": e.link,
                "sumber": getattr(getattr(e, "source", None), "title", "Tidak diketahui"),
                "tanggal": tanggal.isoformat(),
                "ringkasan_rss": re.sub(r"<[^>]+>", "", getattr(e, "summary", "")),
            })
    return hasil

# fungsi filter
def filter_relevan(artikel: list[dict]) -> list[dict]:
    hasil = []
    for a in artikel:
        judul = a["judul"].lower()
        if not any(k in judul for k in KEYWORDS):
            continue
        if any(k in judul for k in KATA_ASING + KATA_NOISE):
            continue
        if a["sumber"] in SUMBER_DIBLOKIR:
            continue
        hasil.append(a)
    return hasil


# menghapus berita duplikat
def hapus_duplikat(artikel: list[dict]) -> list[dict]:
    terlihat, unik = set(), []
    for a in artikel:
        kunci = normalisasi_judul(a["judul"])
        if kunci in terlihat:
            continue
        terlihat.add(kunci)
        unik.append(a)
    return unik


def ambil_berita_mingguan() -> list[dict]:
    artikel = ambil_semua()
    print("Setelah ambil: ", len(artikel))
    artikel = filter_relevan(artikel)
    print("Setelah filter: ", len(artikel))
    artikel = hapus_duplikat(artikel)
    print("Setelah hapus duplikat: ", len(artikel))
    return sorted(artikel, key=lambda a: a["tanggal"], reverse=True)


if __name__ == "__main__":
    berita = ambil_berita_mingguan()
    print(f"Ditemukan {len(berita)} artikel unik & relevan\n")
    for a in berita[:10]:
        print(f"- {a['judul']}\n  {a['sumber']} | {a['tanggal'][:10]}\n  {a['link']}\n")
