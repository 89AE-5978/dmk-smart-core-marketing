"""Gera as artes (JPEG 1080x1350) de cada post a partir de content/posts.json.

Uso (local, uma vez ou quando mudar textos):
    .venv\\Scripts\\python scripts\\gerar_imagens.py

Requer Pillow. As imagens vão para docs/images/, que é publicado pelo GitHub Pages.
Para usar artes próprias, basta substituir os arquivos post-XX.jpg mantendo o nome.
"""
from __future__ import annotations

import json
import os
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
POSTS = RAIZ / "content" / "posts.json"
SAIDA = RAIZ / "docs" / "images"

LARGURA, ALTURA = 1080, 1350
MARGEM = 80

CORES_TEMA = {
    "agua": ("#29B6F6", "GESTÃO DE ÁGUA"),
    "local": ("#2ECC71", "FUNCIONA SEM INTERNET"),
    "app": ("#A78BFA", "APLICATIVO"),
    "regras": ("#F5A623", "REGRAS INTELIGENTES"),
    "esp32": ("#FF6B6B", "ESP32-S3"),
    "uso": ("#29B6F6", "APLICAÇÕES"),
    "como": ("#2ECC71", "COMO FUNCIONA"),
    "mito": ("#F5A623", "MITO OU VERDADE"),
    "pergunta": ("#A78BFA", "PERGUNTA DO DIA"),
    "resumo": ("#29B6F6", "RESUMO"),
    "cta": ("#2ECC71", "FALE COM A DMK"),
}

FONTES_WINDOWS = {
    "bold": "C:/Windows/Fonts/segoeuib.ttf",
    "regular": "C:/Windows/Fonts/segoeui.ttf",
    "light": "C:/Windows/Fonts/segoeuil.ttf",
}
FONTES_LINUX = {
    "bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "regular": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "light": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
}


def fonte(peso: str, tamanho: int) -> ImageFont.FreeTypeFont:
    for tabela in (FONTES_WINDOWS, FONTES_LINUX):
        caminho = tabela[peso]
        if os.path.exists(caminho):
            return ImageFont.truetype(caminho, tamanho)
    return ImageFont.load_default(tamanho)


def hex_rgb(cor: str) -> tuple[int, int, int]:
    cor = cor.lstrip("#")
    return tuple(int(cor[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def quebrar(texto: str, f: ImageFont.FreeTypeFont, largura_max: int, draw: ImageDraw.ImageDraw) -> list[str]:
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = f"{atual} {palavra}".strip()
        if draw.textlength(teste, font=f) <= largura_max:
            atual = teste
        else:
            if atual:
                linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas


def fundo(acento: tuple[int, int, int], semente: int) -> Image.Image:
    img = Image.new("RGB", (LARGURA, ALTURA))
    topo, base = hex_rgb("#0A1522"), hex_rgb("#0F2C44")
    d = ImageDraw.Draw(img)
    for y in range(ALTURA):
        t = y / ALTURA
        d.line([(0, y), (LARGURA, y)], fill=tuple(int(topo[i] + (base[i] - topo[i]) * t) for i in range(3)))

    camada = Image.new("RGBA", (LARGURA, ALTURA), (0, 0, 0, 0))
    c = ImageDraw.Draw(camada)
    # Anéis grandes e suaves (remetem a sensor / onda).
    cx, cy = LARGURA - 120, 330
    for i, r in enumerate(range(140, 620, 90)):
        c.ellipse([cx - r, cy - r, cx + r, cy + r], outline=acento + (max(10, 60 - i * 9),), width=3)

    # Trilhas de circuito com nós.
    rnd = random.Random(semente)
    for _ in range(9):
        x = rnd.randrange(MARGEM, LARGURA - MARGEM)
        y = rnd.randrange(170, 620)
        pontos = [(x, y)]
        for _ in range(3):
            if rnd.random() < 0.5:
                x += rnd.choice([-1, 1]) * rnd.randrange(60, 200)
            else:
                y = min(640, max(190, y + rnd.choice([-1, 1]) * rnd.randrange(40, 140)))
            pontos.append((x, y))
        c.line(pontos, fill=acento + (55,), width=3)
        for px, py in (pontos[0], pontos[-1]):
            c.ellipse([px - 7, py - 7, px + 7, py + 7], fill=acento + (110,))
    img.paste(camada, (0, 0), camada)
    return img


def desenhar(post: dict, total: int) -> Image.Image:
    cor_hex, rotulo = CORES_TEMA.get(post["tema"], CORES_TEMA["resumo"])
    acento = hex_rgb(cor_hex)
    img = fundo(acento, post["id"])
    d = ImageDraw.Draw(img)

    # Marca no topo.
    d.rectangle([MARGEM, 92, MARGEM + 10, 142], fill=acento)
    d.text((MARGEM + 30, 88), "DMK SMART CORE", font=fonte("bold", 44), fill="white")

    # Bloco de texto ancorado na parte de baixo.
    largura_texto = LARGURA - 2 * MARGEM
    f_titulo = fonte("bold", 92)
    linhas_titulo = quebrar(post["titulo"], f_titulo, largura_texto, d)
    while len(linhas_titulo) > 4 and f_titulo.size > 60:
        f_titulo = fonte("bold", f_titulo.size - 6)
        linhas_titulo = quebrar(post["titulo"], f_titulo, largura_texto, d)
    f_sub = fonte("regular", 42)
    linhas_sub = quebrar(post["subtitulo"], f_sub, largura_texto, d)
    f_rotulo = fonte("bold", 30)

    alt_titulo = int(f_titulo.size * 1.12)
    alt_sub = int(f_sub.size * 1.3)
    y = 1080 - len(linhas_titulo) * alt_titulo - len(linhas_sub) * alt_sub - 40 - 80

    # Rótulo do tema (pílula).
    lw = d.textlength(rotulo, font=f_rotulo)
    d.rounded_rectangle([MARGEM, y, MARGEM + lw + 48, y + 56], radius=28, fill=acento)
    d.text((MARGEM + 24, y + 9), rotulo, font=f_rotulo, fill=hex_rgb("#0A1522"))
    y += 80

    for linha in linhas_titulo:
        d.text((MARGEM, y), linha, font=f_titulo, fill="white")
        y += alt_titulo
    y += 40
    for linha in linhas_sub:
        d.text((MARGEM, y), linha, font=f_sub, fill=hex_rgb("#B8C7D6"))
        y += alt_sub

    # Rodapé.
    d.line([(MARGEM, 1180), (LARGURA - MARGEM, 1180)], fill=acento, width=2)
    f_rod = fonte("regular", 32)
    d.text((MARGEM, 1210), "ESP32-S3  •  Local, sem internet  •  App  •  Regras  •  Água", font=f_rod, fill=hex_rgb("#B8C7D6"))
    return img


def main() -> int:
    posts = json.loads(POSTS.read_text(encoding="utf-8"))
    SAIDA.mkdir(parents=True, exist_ok=True)
    for post in posts:
        destino = SAIDA / f"post-{post['id']:02d}.jpg"
        desenhar(post, len(posts)).save(destino, "JPEG", quality=90, optimize=True)
        print(f"ok  {destino.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
