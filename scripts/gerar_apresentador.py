"""Gera post (1080x1350) e story (1080x1920) com o apresentador em retrato circular,
no padrão visual DMK. Funciona com foto real ou avatar.

Uso:
    .venv\\Scripts\\python scripts\\gerar_apresentador.py FOTO --cx 225 --cy 300 --raio 200
(cx, cy, raio = centro e raio do rosto na foto original, em pixels)
Saída: manual/apresentador-feed.jpg e manual/apresentador-story.jpg
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gerar_imagens as g  # noqa: E402

CIANO = g.hex_rgb("#29B6F6")
ESCURO = g.hex_rgb("#0A1522")
CINZA = g.hex_rgb("#B8C7D6")
CHIPS = [("ESP32-S3", "#FF6B6B"), ("Sem internet", "#2ECC71"), ("Aplicativo", "#A78BFA"),
         ("Regras inteligentes", "#F5A623"), ("Gestão de água", "#29B6F6")]


def retrato(foto: Path, cx: int, cy: int, raio: int, diam: int) -> Image.Image:
    img = ImageOps.exif_transpose(Image.open(foto)).convert("RGB")
    rosto = img.crop((cx - raio, cy - raio, cx + raio, cy + raio)).resize((diam, diam), Image.LANCZOS)
    rosto = rosto.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=3))
    mascara = Image.new("L", (diam * 4, diam * 4), 0)
    ImageDraw.Draw(mascara).ellipse([0, 0, diam * 4, diam * 4], fill=255)
    rosto.putalpha(mascara.resize((diam, diam), Image.LANCZOS))
    return rosto


def centro(d, y, texto, f, cor):
    d.text(((1080 - d.textlength(texto, font=f)) / 2, y), texto, font=f, fill=cor)


def chips(d, y, tam):
    f = g.fonte("bold", tam)
    h, gap = int(tam * 1.9), 16
    itens = [(t, g.hex_rgb(c), d.textlength(t, font=f) + 48) for t, c in CHIPS]
    linhas, atual, larg = [], [], 0
    for it in itens:
        if atual and larg + it[2] + gap > 1080 - 2 * g.MARGEM:
            linhas.append(atual); atual, larg = [], 0
        atual.append(it); larg += it[2] + gap
    linhas.append(atual)
    for linha in linhas:
        total = sum(w for _, _, w in linha) + gap * (len(linha) - 1)
        x = (1080 - total) / 2
        for t, c, w in linha:
            d.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, outline=c, width=3, fill=(16, 38, 58))
            d.text((x + 24, y + (h - tam) / 2 - 4), t, font=f, fill="white")
            x += w + gap
        y += h + gap
    return y


def arte(foto, cx, cy, raio, nome, altura):
    story = altura > 1500
    g.LARGURA, g.ALTURA = 1080, altura
    img = g.fundo(CIANO, 9)
    d = ImageDraw.Draw(img)
    topo = 270 if story else 80

    f_marca = g.fonte("bold", 40)
    w = d.textlength("DMK SMART CORE", font=f_marca) + 30
    x0 = (1080 - w) / 2
    d.rectangle([x0, topo + 4, x0 + 10, topo + 50], fill=CIANO)
    d.text((x0 + 30, topo), "DMK SMART CORE", font=f_marca, fill="white")

    diam = 480 if story else 440
    yc = topo + 100
    xc = (1080 - diam) // 2
    brilho = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(brilho).ellipse([xc - 40, yc - 40, xc + diam + 40, yc + diam + 40], fill=CIANO + (70,))
    brilho = brilho.filter(ImageFilter.GaussianBlur(30))
    img.paste(brilho, (0, 0), brilho)
    d = ImageDraw.Draw(img)
    d.ellipse([xc - 12, yc - 12, xc + diam + 12, yc + diam + 12], outline=CIANO, width=8)
    img.paste(retrato(foto, cx, cy, raio, diam), (xc, yc), retrato(foto, cx, cy, raio, diam))

    y = yc + diam + 34
    f_nome = g.fonte("bold", 34)
    texto = nome.upper()
    wn = d.textlength(texto, font=f_nome) + 56
    d.rounded_rectangle([(1080 - wn) / 2, y, (1080 + wn) / 2, y + 62], radius=31, fill=CIANO)
    centro(d, y + 10, texto, f_nome, ESCURO)
    y += 62 + (60 if story else 40)

    f_tit = g.fonte("bold", 76 if story else 68)
    for linha in ("Eu apresento o", "DMK Smart Core"):
        centro(d, y, linha, f_tit, "white")
        y += int(f_tit.size * 1.12)
    y += 10
    f_sub = g.fonte("regular", 36 if story else 32)
    for linha in g.quebrar("Automação inteligente que funciona mesmo sem internet", f_sub, 1080 - 2 * g.MARGEM, d):
        centro(d, y, linha, f_sub, CINZA)
        y += int(f_sub.size * 1.3)
    y = chips(d, y + (50 if story else 28), 30 if story else 26)

    if True:
        f = g.fonte("bold", 44 if story else 38)
        t = "Chame no direct  →"
        wb = d.textlength(t, font=f) + 80
        yb, hb = y + (40 if story else 24), (100 if story else 84)
        d.rounded_rectangle([(1080 - wb) / 2, yb, (1080 + wb) / 2, yb + hb], radius=hb // 2, fill=CIANO)
        centro(d, yb + (hb - f.size) / 2 - 6, t, f, ESCURO)
    return img


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("foto", type=Path)
    ap.add_argument("--cx", type=int, required=True)
    ap.add_argument("--cy", type=int, required=True)
    ap.add_argument("--raio", type=int, required=True)
    ap.add_argument("--nome", default="Danilo • DMK Soluções Smart")
    ap.add_argument("--prefixo", default="apresentador")
    a = ap.parse_args()
    saida = g.RAIZ / "manual"
    for nome_arq, alt in (("feed", 1350), ("story", 1920)):
        destino = saida / f"{a.prefixo}-{nome_arq}.jpg"
        arte(a.foto, a.cx, a.cy, a.raio, a.nome, alt).save(destino, "JPEG", quality=92, optimize=True)
        print(f"ok  {destino.relative_to(g.RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
