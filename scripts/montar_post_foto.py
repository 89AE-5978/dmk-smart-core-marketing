"""Monta um post 1080x1350 a partir de uma foto, com a identidade visual DMK por cima.

Uso:
    .venv\\Scripts\\python scripts\\montar_post_foto.py FOTO [SAIDA] [--titulo "..."] [--subtitulo "..."]
Padrão de saída: manual/post-foto.jpg
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gerar_imagens as g  # noqa: E402

L, A = 1080, 1350
CIANO = g.hex_rgb("#29B6F6")
ESCURO = g.hex_rgb("#0A1522")


def montar(foto: Path, titulo: str, subtitulo: str) -> Image.Image:
    img = ImageOps.fit(ImageOps.exif_transpose(Image.open(foto)).convert("RGB"), (L, A), centering=(0.5, 0.35))

    # Degradê escuro: leve no topo (marca) e forte embaixo (texto).
    sombra = Image.new("RGBA", (L, A), (0, 0, 0, 0))
    d = ImageDraw.Draw(sombra)
    for y in range(A):
        if y < 220:
            alfa = int(150 * (1 - y / 220))
        elif y > A * 0.52:
            t = (y - A * 0.52) / (A * 0.48)
            alfa = int(235 * min(1, t * 1.25))
        else:
            alfa = 0
        d.line([(0, y), (L, y)], fill=ESCURO + (alfa,))
    img.paste(sombra, (0, 0), sombra)

    d = ImageDraw.Draw(img)
    d.rectangle([g.MARGEM, 72, g.MARGEM + 10, 122], fill=CIANO)
    d.text((g.MARGEM + 30, 68), "DMK SMART CORE", font=g.fonte("bold", 44), fill="white")

    f_tit, f_sub = g.fonte("bold", 80), g.fonte("regular", 38)
    largura = L - 2 * g.MARGEM
    lt = g.quebrar(titulo, f_tit, largura, d)
    ls = g.quebrar(subtitulo, f_sub, largura, d)
    y = 1150 - len(lt) * 88 - len(ls) * 50 - 30
    for linha in lt:
        d.text((g.MARGEM, y), linha, font=f_tit, fill="white")
        y += 88
    y += 20
    for linha in ls:
        d.text((g.MARGEM, y), linha, font=f_sub, fill=g.hex_rgb("#D5E1EC"))
        y += 50

    d.line([(g.MARGEM, 1205), (L - g.MARGEM, 1205)], fill=CIANO, width=2)
    d.text((g.MARGEM, 1230), "ESP32-S3  •  Sem internet  •  App  •  Regras  •  Água",
           font=g.fonte("regular", 32), fill=g.hex_rgb("#B8C7D6"))
    return img


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("foto", type=Path)
    ap.add_argument("saida", type=Path, nargs="?", default=g.RAIZ / "manual" / "post-foto.jpg")
    ap.add_argument("--titulo", default="Conheça o DMK Smart Core")
    ap.add_argument("--subtitulo", default="Automação inteligente que funciona mesmo sem internet")
    a = ap.parse_args()
    a.saida.parent.mkdir(parents=True, exist_ok=True)
    montar(a.foto, a.titulo, a.subtitulo).save(a.saida, "JPEG", quality=92, optimize=True)
    print(f"ok  {a.saida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
