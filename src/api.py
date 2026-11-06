import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

import generator
import render

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"

app = FastAPI(title="Weekly IG Generator Rumah123")

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/generate")
def generate():
    try:
        hasil = generator.jalankan()
    except SystemExit as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gagal generate: {e}")

    render.main()
    hasil["slides_url"] = [f"/slides/{i}" for i in range(1, 7)]
    return hasil

@app.get("/result")
def result():
    f = OUT / "hasil.json"
    if not f.exists():
        raise HTTPException(status_code=404, detail="Belum ada hasil, /generate dulu")
    return json.loads(f.read_text(encoding="utf-8"))

@app.get("/slides/{nomor}")
def slide(nomor: int):
    f = OUT / f"slide_{nomor}.png"
    if not f.exists():
        raise HTTPException(status_code=404, detail="Slide tidak ditemukan")
    return FileResponse(f, media_type="image/png")