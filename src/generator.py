import json
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq
from pydantic import ValidationError

from ambil_berita import ambil_berita_mingguan, normalisasi_judul
from isi_artikel import ambil_isi
from schemas import Carousel

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
PROMPT = (ROOT / "prompts" / "carousel_prompt.md").read_text(encoding="utf-8")
TERPAKAI = ROOT / "output" / "terpakai.json"
MAX_COBA_ARTIKEL = 15

# fungsi memanggil ai
def panggil_groq(client: Groq, pesan: list[dict]) -> str:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=pesan,
        temperature=0.3,
        response_format={"type": "json_object"},
    )
    return resp.choices[0].message.content

# manggil Groq, validasi kalau gagal validasi, coba sekali lagi dengan pesan erro
def buat_carousel(teks: str, judul: str) -> Carousel:
    
    client = Groq()  # membaca GROQ_API_KEY dari environment
    pesan = [
        {"role": "system", "content": PROMPT},
        {"role": "user", "content": f"JUDUL: {judul}\n\nTEKS ARTIKEL:\n{teks}"},
    ]
    mentah = panggil_groq(client, pesan)
    try:
        return Carousel.model_validate_json(mentah)
    except ValidationError as err:
        print("Validasi gagal, mencoba ulang:", err.error_count(), "error")
        pesan += [
            {"role": "assistant", "content": mentah},
            {"role": "user", "content": f"JSON tidak valid: {err}\nPerbaiki dan balas JSON saja."},
        ]
        return Carousel.model_validate_json(panggil_groq(client, pesan))

def load_used() -> set:
    if TERPAKAI.exists():
        return set(json.loads(TERPAKAI.read_text(encoding="utf-8")))
    return set()

def save_used(used: set) -> None:
    TERPAKAI.parent.mkdir(exist_ok=True)
    TERPAKAI.write_text(json.dumps(sorted(used)), encoding="utf-8")

def jalankan() -> dict:
    artikel_used = load_used()
    for artikel in ambil_berita_mingguan()[:MAX_COBA_ARTIKEL]:
        kunci = normalisasi_judul(artikel["judul"])
        if kunci in artikel_used:
            continue
        print("Mencoba:", artikel["judul"])
        hasil = ambil_isi(artikel["link"])
        if hasil:
            url_asli, teks = hasil
            break
    else:
        raise SystemExit("Tidak ada artikel dengan isi yang bisa diambil.")

    carousel = buat_carousel(teks, artikel["judul"])
    artikel_used.add(kunci)
    save_used(artikel_used)
    keluaran = {
        "sumber_artikel": {
            "judul": artikel["judul"],
            "media": artikel["sumber"],
            "tanggal": artikel["tanggal"],
            "url": url_asli,
        },
        "konten": carousel.model_dump(),
    }
    out = ROOT / "output"
    out.mkdir(exist_ok=True)
    (out / "hasil.json").write_text(json.dumps(keluaran, ensure_ascii=False, indent=2), encoding="utf-8")
    return keluaran


if __name__ == "__main__":
    data = jalankan()
    print(json.dumps(data, ensure_ascii=False, indent=2))
    print("\nTersimpan di output/hasil.json")
