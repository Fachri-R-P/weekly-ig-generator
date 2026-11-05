import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"

W, H = 1080, 1350 #ukuran feeds
PAD = 90 # padding
BG = (15, 23, 42) # BIRU GELAP
AKSEN = (250, 204, 21) # KUNING
PUTIH = (248, 250, 252)
ABU = (148, 163, 184)

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

def buat_slide(nomor, total, slide, media):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # logo di pojok
    logo = Image.open(ROOT / "assets" / "rumah123_logo.jpg").convert("RGBA")
    logo = logo.resize((120, 120))
    img.paste(logo, (W - PAD - 120, 60), logo)

    #header
    d.text((PAD, 80), "RumahKita", font=load_font(FONT_BOLD, 30), fill=AKSEN)
    d.text((W - PAD - 90, 80), f"{nomor}/{total}", font=load_font(FONT_REG, 30), fill=ABU)
    d.rectangle([PAD, 140, PAD + 120, 148], fill=AKSEN)

    # isi
    hook = nomor == 1
    f_judul = load_font(FONT_BOLD, 84 if hook else 64)
    f_isi = load_font(FONT_REG, 42)
    y = gambar_teks(d, slide["judul"], f_judul, 260, PUTIH, jarak=1.2)
    gambar_teks(d, slide["isi"], f_isi, y + 50, ABU if hook else PUTIH)

    # footer
    d.text((PAD, H - 110), f"Sumber: {media}", font=load_font(FONT_REG, 30), fill=ABU)
    return img

def main():
    data = json.loads((OUT / "hasil.json").read_text(encoding="utf-8"))
    media = data["sumber_artikel"]["media"]
    slides = data["konten"]["slides"]
    for i, s in enumerate(slides, start=1):
        path = OUT / f"slide_{i}.png"
        buat_slide(i, len(slides), s, media).save(path)
        print("Tersimpan:", path)

if __name__ == "__main__":
    main()