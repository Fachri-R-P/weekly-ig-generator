import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"

W, H = 1080, 1350 #ukuran feeds
PAD = 90 # padding
BG_ATAS = (66, 104, 184)   # biru royal (atas gradasi)
BG_BAWAH = (30, 52, 112)   # biru lebih gelap (bawah gradasi)
AKSEN = (255, 214, 102)    # kuning hangat, kontras dengan biru
PUTIH = (255, 255, 255)
REDUP = (208, 224, 250)    # biru muda untuk teks sekunder

FONT_BOLD = [
    "C:/Windows/Fonts/segoeuib.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
FONT_REG = [
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

def load_font(daftar, ukuran):
    for path in daftar:
        if Path(path).exists():
            return ImageFont.truetype(path, ukuran)
    return ImageFont.load_default(ukuran)

# memotong teks jadi beberapa baris
def wrap(draw, teks, font, lebar_maks):
    baris, sekarang = [], ""
    for kata in teks.split():
        coba = f"{sekarang} {kata}".strip()
        if draw.textlength(coba, font=font) <= lebar_maks:
            sekarang = coba
        else:
            baris.append(sekarang)
            sekarang = kata
    if sekarang:
        baris.append(sekarang)
    return baris

def gambar_teks(draw, teks, font, y, warna, jarak=1.3):
    for baris in wrap(draw, teks, font, W - 2 * PAD):
        draw.text((PAD, y), baris, font=font, fill=warna)
        y += int(font.size * jarak)
    return y

def latar():
    # latar gradasi: atas BG_ATAS -> bawah BG_BAWAH
    mask = Image.linear_gradient("L").resize((W, H))
    return Image.composite(Image.new("RGB", (W, H), BG_BAWAH),
                           Image.new("RGB", (W, H), BG_ATAS), mask)

def kepala(d, nomor, total):
    d.text((PAD, 80), "RumahKita", font=load_font(FONT_BOLD, 30), fill=AKSEN)
    d.text((W - PAD - 90, 80), f"{nomor}/{total}", font=load_font(FONT_REG, 30), fill=REDUP)
    d.rectangle([PAD, 140, PAD + 120, 148], fill=AKSEN)

def buat_slide(nomor, total, slide, media):
    img = latar()
    d = ImageDraw.Draw(img)

    kepala(d, nomor, total)

    # isi
    hook = nomor == 1
    f_judul = load_font(FONT_BOLD, 84 if hook else 64)
    f_isi = load_font(FONT_REG, 42)
    y = gambar_teks(d, slide["judul"], f_judul, 260, PUTIH, jarak=1.2)
    gambar_teks(d, slide["isi"], f_isi, y + 50, REDUP if hook else PUTIH)

    # footer
    d.text((PAD, H - 110), f"Sumber: {media}", font=load_font(FONT_REG, 30), fill=REDUP)
    if nomor < total:   # petunjuk geser, tidak ditampilkan di slide terakhir
        d.text((W - PAD, H - 110), "Geser →", font=load_font(FONT_BOLD, 30), fill=AKSEN, anchor="ra")
    return img

def slide_kuis(nomor, total, kuis):
    """Slide penutup: polling opini dengan pilihan A/B/C."""
    img = latar()
    d = ImageDraw.Draw(img)
    kepala(d, nomor, total)

    y = gambar_teks(d, "Menurutmu?", load_font(FONT_BOLD, 84), 260, AKSEN, jarak=1.2)
    y = gambar_teks(d, kuis["pertanyaan"], load_font(FONT_BOLD, 48), y + 20, PUTIH, jarak=1.25)
    y += 50

    f_pilihan = load_font(FONT_REG, 40)
    f_huruf = load_font(FONT_BOLD, 40)
    teks_x = PAD + 130                      # ruang untuk lingkaran huruf
    lebar_teks = W - PAD - teks_x - 30
    for huruf, pilihan in zip("ABC", kuis["pilihan"]):
        baris = wrap(d, pilihan, f_pilihan, lebar_teks)
        tinggi = max(110, len(baris) * 54 + 50)
        d.rounded_rectangle([PAD, y, W - PAD, y + tinggi], radius=30,
                            fill=(52, 86, 160), outline=AKSEN, width=3)
        cy = y + tinggi // 2
        d.ellipse([PAD + 28, cy - 36, PAD + 100, cy + 36], fill=AKSEN)
        d.text((PAD + 64, cy), huruf, font=f_huruf, fill=BG_BAWAH, anchor="mm")
        ty = cy - (len(baris) * 54) // 2 + 4
        for b in baris:
            d.text((teks_x, ty), b, font=f_pilihan, fill=PUTIH)
            ty += 54
        y += tinggi + 26

    d.text((PAD, H - 110), "Jawab di kolom komentar ya!", font=load_font(FONT_REG, 30), fill=REDUP)
    return img

def main():
    data = json.loads((OUT / "hasil.json").read_text(encoding="utf-8"))
    media = data["sumber_artikel"]["media"]
    slides = data["konten"]["slides"]
    kuis = data["konten"].get("kuis")        # hasil lama mungkin belum punya kuis
    total = len(slides) + (1 if kuis else 0)
    for i, s in enumerate(slides, start=1):
        path = OUT / f"slide_{i}.png"
        buat_slide(i, total, s, media).save(path)
        print("Tersimpan:", path)
    if kuis:
        path = OUT / f"slide_{total}.png"
        slide_kuis(total, total, kuis).save(path)
        print("Tersimpan:", path)

if __name__ == "__main__":
    main()