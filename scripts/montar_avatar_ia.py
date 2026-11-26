"""Organiza a imagem do avatar (gerada por IA) no padrão DMK: post 1080x1350 e story 1080x1920.

Uso:
    .venv\\Scripts\\python scripts\\montar_avatar_ia.py [manual\\danilo-avatar.jpg]
Saída: manual/avatar-ia-feed.jpg e manual/avatar-ia-story.jpg
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gerar_imagens as g  # noqa: E402
from gerar_apresentador import centro  # noqa: E402

CIANO = g.hex_rgb("#29B6F6")
NAVY = g.hex_rgb("#0A1522")
NAVY2 = g.hex_rgb("#13294B")
DESTAQUES = "ESP32-S3  •  Sem internet  •  App  •  Regras inteligentes  •  Gestão de água"


def traduzir_tela(img: Image.Image) -> Image.Image:
    """Troca "pump ON" por "Bomba" na tela do celular (coordenadas da imagem original 1122x1402)."""
    img = img.copy()
    if img.size != (1122, 1402):
        return img
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([664, 840, 796, 886], radius=12, fill=(4, 33, 60))
    d.text((672, 843), "Bomba", font=g.fonte("bold", 34), fill="white")
    return img


def botao(d, y, tam=40):
    f = g.fonte("bold", tam)
    t = "Chame no direct  →"
    w = d.textlength(t, font=f) + 72
    h = int(tam * 2.2)
    d.rounded_rectangle([(1080 - w) / 2, y, (1080 + w) / 2, y + h], radius=h // 2, fill=CIANO)
    centro(d, y + (h - tam) / 2 - 6, t, f, NAVY)
    return y + h


def feed(foto: Image.Image) -> Image.Image:
    img = ImageOps.fit(foto, (1080, 1350), centering=(0.5, 0.5))
    # Faixa escura na base para o texto, com degradê suave.
    camada = Image.new("RGBA", img.size, (0, 0, 0, 0))
    c = ImageDraw.Draw(camada)
    for y in range(1120, 1350):
        a = int(235 * min(1, (y - 1120) / 120))
        c.line([(0, y), (1080, y)], fill=NAVY + (a,))
    img.paste(camada, (0, 0), camada)

    d = ImageDraw.Draw(img)
    # Marca e título no céu (texto azul-marinho sobre céu claro).
    f_marca = g.fonte("bold", 34)
    wm = d.textlength("DMK SMART CORE", font=f_marca) + 48
    d.rounded_rectangle([g.MARGEM, 48, g.MARGEM + wm, 104], radius=28, fill=NAVY)
    d.text((g.MARGEM + 24, 55), "DMK SMART CORE", font=f_marca, fill=CIANO)
    d.text((g.MARGEM, 120), "Conheça o DMK Smart Core", font=g.fonte("bold", 64), fill=NAVY)
    d.text((g.MARGEM, 200), "Sua água no automático, mesmo sem internet", font=g.fonte("regular", 34), fill=NAVY2)

    centro(d, 1215, DESTAQUES, g.fonte("bold", 27), "white")
    botao(d, 1262, 30)
    return img


def story(foto: Image.Image) -> Image.Image:
    g.LARGURA, g.ALTURA = 1080, 1920
    img = g.fundo(CIANO, 52)
    d = ImageDraw.Draw(img)
    topo = 250
    d.rectangle([g.MARGEM, topo + 4, g.MARGEM + 10, topo + 50], fill=CIANO)
    d.text((g.MARGEM + 30, topo), "DMK SMART CORE", font=g.fonte("bold", 40), fill="white")
    d.text((g.MARGEM, topo + 75), "Conheça o DMK Smart Core", font=g.fonte("bold", 66), fill="white")
    d.text((g.MARGEM, topo + 160), "Sua água no automático, mesmo sem internet", font=g.fonte("regular", 34), fill=g.hex_rgb("#B8C7D6"))

    # Foto em cartão com cantos arredondados, borda ciano e brilho.
    alt = 1060
    larg = int(foto.width * alt / foto.height)
    cartao = foto.resize((larg, alt), Image.LANCZOS)
    x, y = (1080 - larg) // 2, 490
    brilho = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(brilho).rounded_rectangle([x - 10, y - 10, x + larg + 10, y + alt + 10], radius=48, fill=CIANO + (90,))
    brilho = brilho.filter(ImageFilter.GaussianBlur(24))
    img.paste(brilho, (0, 0), brilho)
    masc = Image.new("L", (larg * 2, alt * 2), 0)
    ImageDraw.Draw(masc).rounded_rectangle([0, 0, larg * 2, alt * 2], radius=80, fill=255)
    img.paste(cartao, (x, y), masc.resize((larg, alt), Image.LANCZOS))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x, y, x + larg, y + alt], radius=40, outline=CIANO, width=5)

    centro(d, y + alt + 26, DESTAQUES, g.fonte("bold", 26), "white")
    botao(d, y + alt + 80, 36)
    return img


def main() -> int:
    origem = Path(sys.argv[1]) if len(sys.argv) > 1 else g.RAIZ / "manual" / "danilo-avatar.jpg"
    foto = traduzir_tela(ImageOps.exif_transpose(Image.open(origem)).convert("RGB"))
    saida = g.RAIZ / "manual"
    feed(foto).save(saida / "avatar-ia-feed.jpg", "JPEG", quality=93, optimize=True)
    story(foto).save(saida / "avatar-ia-story.jpg", "JPEG", quality=93, optimize=True)
    print("ok  manual/avatar-ia-feed.jpg\nok  manual/avatar-ia-story.jpg")
    return 0


if __name__ == "__main__":
    sys.exit(main())
