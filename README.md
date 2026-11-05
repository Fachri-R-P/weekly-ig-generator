# Weekly IG Generator

Program Python yang mengubah berita properti Indonesia menjadi **carousel Instagram 6 slide** secara otomatis: dari mencari berita, merangkumnya dengan AI, sampai menghasilkan gambar PNG siap unggah.

## Cara kerja

```
ambil_berita.py → isi_artikel.py → generator.py → render.py
 cari berita       ambil isi         buat konten     buat gambar
 (Google News)     artikel           dengan AI       slide_1..6.png
                                     + validasi
```

1. **`src/ambil_berita.py`**: mengambil berita 7 hari terakhir dari Google News RSS, menyaring yang relevan dengan kata kunci properti, dan membuang judul ganda.
2. **`src/isi_artikel.py`**: membuka link asli artikel dan mengekstrak teksnya (dengan `trafilatura`). Artikel yang gagal diambil atau terlalu pendek dilewati.
3. **`src/generator.py`**: mengirim teks artikel ke model AI di Groq dengan instruksi dari `prompts/carousel_prompt.md`, lalu memvalidasi jawabannya. Jika tidak valid, AI diminta memperbaiki sekali. Hasilnya disimpan ke `output/hasil.json`.
4. **`src/schemas.py`**: aturan validasi (Pydantic) untuk jawaban AI: tepat 6 slide, batas panjang teks, 5–15 hashtag yang dirapikan otomatis.
5. **`src/render.py`**: membaca `hasil.json` dan menggambar tiap slide menjadi PNG 1080x1350 (rasio 4:5) dengan Pillow.

## Menjaga akurasi konten

AI hanya boleh memakai fakta dari teks artikel (aturan ada di prompt). Selain itu jawaban AI selalu divalidasi oleh `schemas.py` sebelum dipakai, sehingga format yang melanggar aturan tidak sampai ke tahap gambar.

## Instalasi

Butuh Python 3.10 atau lebih baru.

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Salin `.env.example` menjadi `.env`, lalu isi API key Groq (gratis di https://console.groq.com):

```
GROQ_API_KEY=isi_api_key_groq_kamu
GROQ_MODEL=nama_model_groq     # opsional; bawaan: llama-3.3-70b-versatile
```

## Cara menjalankan

Jalankan dari folder utama proyek:

```bash
python src/generator.py    # cari berita, buat konten, simpan output/hasil.json
python src/render.py       # buat output/slide_1.png ... slide_6.png
```

Untuk mencoba bagian pengambil berita saja:

```bash
python src/ambil_berita.py
```

## Struktur folder

```
weekly-ig-generator/
├── src/
│   ├── ambil_berita.py
│   ├── isi_artikel.py
│   ├── generator.py
│   ├── schemas.py
│   └── render.py
├── prompts/
│   └── carousel_prompt.md
├── output/               # hasil (tidak masuk git)
├── requirements.txt
└── .env.example
```

## Keterbatasan saat ini

- Filter berita hanya mengecek kata kunci di judul, belum memastikan beritanya tentang Indonesia.
- Deteksi duplikat hanya menangkap judul yang hampir identik.
- Satu jalan menghasilkan satu carousel dari satu artikel.
- Percobaan ulang ke AI hanya sekali; kegagalan jaringan atau batas API belum ditangani khusus.
- Font diambil dari folder font sistem (Windows/Linux), jadi tampilan bisa sedikit berbeda antar komputer.

## Rencana pengembangan

- Logo dan foto latar properti pada slide.
- Desain khusus untuk slide pembuka (hook) dan penutup (ajakan follow).
- Filter berita khusus Indonesia.

## Teknologi

Python, feedparser, trafilatura, Groq API, Pydantic, Pillow.
