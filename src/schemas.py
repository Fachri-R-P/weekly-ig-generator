from pydantic import BaseModel, Field, field_validator


class Slide(BaseModel):
    judul: str = Field(min_length=3, max_length=70)
    isi: str = Field(min_length=10, max_length=260)


class Carousel(BaseModel):
    ringkasan: str = Field(min_length=20, max_length=600)
    slides: list[Slide] = Field(min_length=6, max_length=6)  # tepat 6 slide
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