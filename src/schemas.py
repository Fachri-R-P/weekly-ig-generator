from pydantic import BaseModel, Field, field_validator


class Slide(BaseModel):
    judul: str = Field(min_length=3, max_length=70)
    isi: str = Field(min_length=10, max_length=500)


class Kuis(BaseModel):
    pertanyaan: str = Field(min_length=10, max_length=120)
    pilihan: list[str] = Field(min_length=2, max_length=3)

    @field_validator("pilihan")
    @classmethod
    def cek_pilihan(cls, v):
        # buang awalan "A." / "B)" kalau AI menambahkan sendiri, lalu cek panjang
        bersih = []
        for p in v:
            p = p.strip()
            if len(p) > 2 and p[0].upper() in "ABC" and p[1] in ".):":
                p = p[2:].strip()
            if not 1 <= len(p) <= 45:
                raise ValueError("setiap pilihan harus 1-45 karakter")
            bersih.append(p)
        return bersih


class Carousel(BaseModel):
    ringkasan: str = Field(min_length=20, max_length=600)
    slides: list[Slide] = Field(min_length=6, max_length=6)  # tepat 6 slide
    kuis: Kuis
    caption: str = Field(min_length=20, max_length=800)
    hashtags: list[str] = Field(min_length=5, max_length=15)

    @field_validator("hashtags")
    @classmethod
    # membuat fungsi cleaning hastag "# properti" -> "#properti"
    def clean_hashtag(cls, v):
        cleaned = []
        for h in v:
            h = h.strip().replace(" ", "")
            if not h.startswith("#"):
                h = "#" + h
            if len(h) > 1 and h not in cleaned:
                cleaned.append(h)
        return cleaned