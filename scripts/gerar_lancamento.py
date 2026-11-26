"""Gera as artes de lançamento para publicação manual: feed (1080x1350) e story (1080x1920).

Uso:
    .venv\\Scripts\\python scripts\\gerar_lancamento.py
Saída: manual/lancamento-feed.jpg e manual/lancamento-story.jpg
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gerar_imagens as g  # noqa: E402

SAIDA = g.RAIZ / "manual"
CIANO = g.hex_rgb("#29B6F6")
VERDE = g.hex_rgb("#2ECC71")
CINZA = g.hex_rgb("#B8C7D6")
ESCURO = g.hex_rgb("#0A1522")

RECURSOS = [
    ("Automação com ESP32-S3", "#FF6B6B"),
    ("Funciona sem internet", "#2ECC71"),
    ("Controle pelo aplicativo", "#A78BFA"),
    ("Regras inteligentes", "#F5A623"),
    ("Gestão de água", "#29B6F6"),
]


def fundo(largura: int, altura: int, semente: int) -> Image.Image:
    g.LARGURA, g.ALTURA = largura, altura
    return g.fundo(CIANO, semente)


def marca(d: ImageDraw.ImageDraw, y: int) -> None:
    d.rectangle([g.MARGEM, y + 4, g.MARGEM + 10, y + 54], fill=CIANO)
    d.text((g.MARGEM + 30, y), "DMK SMART CORE", font=g.fonte("bold", 44), fill="white")


def pilula(d: ImageDraw.ImageDraw, x: int, y: int, texto: str, cor, tam: int = 30) -> int:
    f = g.fonte("bold", tam)
    w = d.textlength(texto, font=f)
    h = int(tam * 1.85)
    d.rounded_rectangle([x, y, x + w + 48, y + h], radius=h // 2, fill=cor)
    d.text((x + 24, y + (h - tam) // 2 - 4), texto, font=f, fill=ESCURO)
    return h


def lista_recursos(d: ImageDraw.ImageDraw, y: int, tam: int, passo: int) -> int:
    f = g.fonte("regular", tam)
    for texto, cor in RECURSOS:
        c = g.hex_rgb(cor)
        r = tam // 2
        cx, cy = g.MARGEM + r, y + int(tam * 0.62)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
        # "check" dentro do círculo
        d.line([(cx - r * 0.45, cy), (cx - r * 0.1, cy + r * 0.38), (cx + r * 0.5, cy - r * 0.35)], fill=ESCURO, width=max(3, tam // 9))
        d.text((g.MARGEM + tam + 24, y), texto, font=f, fill="white")
        y += passo
    return y


def titulo(d: ImageDraw.ImageDraw, y: int, texto: str, tam: int) -> int:
    f = g.fonte("bold", tam)
    for linha in g.quebrar(texto, f, 1080 - 2 * g.MARGEM, d):
        d.text((g.MARGEM, y), linha, font=f, fill="white")
        y += int(tam * 1.1)
    return y


def feed() -> Image.Image:
    img = fundo(1080, 1350, 2026)
    d = ImageDraw.Draw(img)
    marca(d, 88)
    y = 560
    y += pilula(d, g.MARGEM, y, "LANÇAMENTO", VERDE) + 28
    y = titulo(d, y, "Chegou o DMK Smart Core", 96) + 30
    y = lista_recursos(d, y, 40, 64)
    d.line([(g.MARGEM, 1210), (1080 - g.MARGEM, 1210)], fill=CIANO, width=2)
    d.text((g.MARGEM, 1236), "Automação local, inteligente e sem depender da nuvem.", font=g.fonte("regular", 32), fill=CINZA)
    return img


def story() -> Image.Image:
    img = fundo(1080, 1920, 77)
    d = ImageDraw.Draw(img)
    # Áreas de segurança do story: ~250 px livres no topo e na base.
    marca(d, 270)
    y = 760
    y += pilula(d, g.MARGEM, y, "NOVIDADE", VERDE, 34) + 34
    y = titulo(d, y, "Sua automação não para quando a internet cai", 92) + 50
    y = lista_recursos(d, y, 44, 74) + 40
    # Chamada para ação
    f = g.fonte("bold", 44)
    texto = "Chame no direct  →"
    w = d.textlength(texto, font=f)
    d.rounded_rectangle([g.MARGEM, y, g.MARGEM + w + 80, y + 100], radius=50, fill=CIANO)
    d.text((g.MARGEM + 40, y + 20), texto, font=f, fill=ESCURO)
    return img


def main() -> int:
    SAIDA.mkdir(exist_ok=True)
    feed().save(SAIDA / "lancamento-feed.jpg", "JPEG", quality=92, optimize=True)
    story().save(SAIDA / "lancamento-story.jpg", "JPEG", quality=92, optimize=True)
    print("ok  manual/lancamento-feed.jpg\nok  manual/lancamento-story.jpg")
    return 0


if __name__ == "__main__":
    sys.exit(main())
