"""Gera post (1080x1350) e story (1080x1920) com um avatar ilustrado do Danilo,
de pé, de farda DMK, apontando para a tela do aplicativo DMK Smart Core.

Uso:
    .venv\\Scripts\\python scripts\\gerar_avatar.py
Saída: manual/avatar-feed.jpg e manual/avatar-story.jpg
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gerar_imagens as g  # noqa: E402
from gerar_apresentador import centro, chips  # noqa: E402

SS = 2  # supersampling para bordas suaves
CIANO = g.hex_rgb("#29B6F6")
VERDE = g.hex_rgb("#2ECC71")
AMBAR = g.hex_rgb("#F5A623")
ESCURO = g.hex_rgb("#0A1522")
CINZA = g.hex_rgb("#B8C7D6")
PELE, PELE_E = (198, 142, 99), (172, 117, 80)
CABELO, BARBA = (28, 21, 17), (40, 29, 22)
FARDA, CALCA, SAPATO = (27, 46, 96), (46, 54, 66), (18, 18, 22)


class Boneco:
    """Desenha em coordenadas do personagem (origem nos pés, y negativo para cima)."""

    def __init__(self, d: ImageDraw.ImageDraw, ox: float, oy: float, k: float):
        self.d, self.ox, self.oy, self.k = d, ox * SS, oy * SS, k * SS

    def p(self, x, y):
        return (self.ox + x * self.k, self.oy + y * self.k)

    def caixa(self, x0, y0, x1, y1):
        (a, b), (c, e) = self.p(x0, y0), self.p(x1, y1)
        return [min(a, c), min(b, e), max(a, c), max(b, e)]

    def membro(self, a, b, w, cor):
        self.d.line([self.p(*a), self.p(*b)], fill=cor, width=int(w * self.k))
        for c in (a, b):
            self.circ(c, w / 2, cor)

    def circ(self, c, r, cor):
        x, y = self.p(*c)
        self.d.ellipse([x - r * self.k, y - r * self.k, x + r * self.k, y + r * self.k], fill=cor)

    def ret(self, x0, y0, x1, y1, r, cor, contorno=None, larg=0):
        self.d.rounded_rectangle(self.caixa(x0, y0, x1, y1), radius=r * self.k, fill=cor,
                                 outline=contorno, width=int(larg * self.k))

    def desenhar(self):
        d = self.d
        d.ellipse(self.caixa(-20, -2.5, 22, 3), fill=(6, 14, 24))  # sombra
        # Pernas e sapatos
        self.membro((-6, -42), (-6.5, -5), 9, CALCA)
        self.membro((6, -42), (7, -5), 9, CALCA)
        self.ret(-14, -6.5, -1, 0, 2.5, SAPATO)
        self.ret(2, -6.5, 16, 0, 2.5, SAPATO)
        # Braço esquerdo (relaxado)
        self.membro((-13, -68), (-16.5, -53), 8, FARDA)
        self.membro((-16.5, -52), (-15.5, -39), 6.4, PELE)
        self.circ((-15.5, -37.5), 3.9, PELE)
        self.membro((-17.5, -55), (-15.5, -55), 1.6, CIANO)  # punho refletivo
        # Tronco
        self.ret(-14, -75, 14, -40, 7, FARDA)
        self.ret(-14, -58.5, 14, -56, 0, CIANO)       # faixa refletiva
        self.ret(-14, -43, 14, -39.5, 1, (20, 30, 50))  # cinto
        self.ret(-3, -75.5, 3, -69, 1.5, PELE_E)        # pescoço
        d.polygon([self.p(-5, -75), self.p(0, -69), self.p(5, -75), self.p(3.5, -76), self.p(0, -72), self.p(-3.5, -76)], fill=CIANO)
        self.ret(-12, -68.5, -2.5, -63, 1.2, CIANO)         # área do logo no peito
        # Braço direito apontando
        self.membro((12, -69), (23, -73.5), 8, FARDA)
        self.membro((21.5, -72.5), (23.5, -74), 1.8, CIANO)
        self.membro((23.5, -74), (33, -80.5), 6.2, PELE)
        self.circ((34, -81.5), 4.1, PELE)
        self.membro((35, -82.5), (40.5, -86), 2.3, PELE)
        # Cabeça
        self.circ((-10.6, -84), 2.6, PELE)
        self.circ((10.6, -84), 2.6, PELE)
        d.ellipse(self.caixa(-10.5, -97, 10.5, -72.5), fill=PELE)
        d.pieslice(self.caixa(-10.7, -93, 10.7, -72.3), 0, 180, fill=BARBA)
        d.ellipse(self.caixa(-7.6, -88.5, 7.6, -80.2), fill=PELE)
        self.ret(-4.8, -81.6, 4.8, -79.4, 1, BARBA)       # bigode
        d.chord(self.caixa(-4, -80.2, 4, -75.2), 0, 180, fill="white", outline=(60, 25, 25), width=int(0.5 * self.k))
        d.pieslice(self.caixa(-11.3, -100, 11.3, -85), 180, 360, fill=CABELO)
        d.ellipse(self.caixa(-6, -101.2, 8.5, -94), fill=CABELO)  # topete
        self.ret(-11, -93, -9.2, -85.5, 0.6, CABELO)
        self.ret(9.2, -93, 11, -85.5, 0.6, CABELO)
        self.membro((-7.2, -90), (-3, -90.6), 1.3, CABELO)
        self.membro((3, -90.6), (7.2, -90), 1.3, CABELO)
        d.ellipse(self.caixa(-1.3, -85.3, 1.3, -82.4), fill=PELE_E)  # nariz
        for x in (-5, 5):  # olhos sorrindo
            d.arc(self.caixa(x - 1.8, -88.3, x + 1.8, -85.2), 200, 340, fill=(25, 20, 20), width=int(0.6 * self.k))
        for x0, x1 in ((-9, -1.3), (1.3, 9)):  # óculos
            self.ret(x0, -89.2, x1, -83.8, 1.6, None, (22, 22, 28), 0.75)
        self.membro((-1.3, -87.3), (1.3, -87.3), 0.6, (22, 22, 28))


def painel(d: ImageDraw.ImageDraw, dy: int):
    """Formas da tela do app (em 2x)."""
    s = lambda *v: [c * SS for c in v]  # noqa: E731
    d.rounded_rectangle(s(612, 362 + dy, 1012, 932 + dy), radius=40 * SS, fill=(9, 20, 34))  # sombra
    d.rounded_rectangle(s(600, 350 + dy, 1000, 920 + dy), radius=40 * SS, fill=(18, 46, 72), outline=CIANO, width=4 * SS)
    d.line(s(630, 462 + dy, 970, 462 + dy), fill=(52, 88, 120), width=2 * SS)
    d.ellipse(s(632, 423 + dy, 646, 437 + dy), fill=VERDE)
    # Caixa d'água
    d.rounded_rectangle(s(640, 495 + dy, 760, 695 + dy), radius=18 * SS, fill=(10, 28, 44), outline=CIANO, width=4 * SS)
    d.rounded_rectangle(s(646, 553 + dy, 754, 689 + dy), radius=12 * SS, fill=(41, 150, 220))
    d.rectangle(s(646, 553 + dy, 754, 566 + dy), fill=(120, 210, 250))
    # Bomba: chave ligada
    d.rounded_rectangle(s(892, 730 + dy, 966, 770 + dy), radius=20 * SS, fill=VERDE)
    d.ellipse(s(930, 734 + dy, 962, 766 + dy), fill="white")
    # Regra
    d.rounded_rectangle(s(630, 800 + dy, 970, 896 + dy), radius=18 * SS, fill=(10, 26, 42), outline=AMBAR, width=3 * SS)


def painel_texto(d: ImageDraw.ImageDraw, dy: int):
    d.text((632, 375 + dy), "App DMK Smart Core", font=g.fonte("bold", 30), fill="white")
    d.text((656, 418 + dy), "Funcionando sem internet", font=g.fonte("regular", 22), fill=VERDE)
    d.text((785, 545 + dy), "72%", font=g.fonte("bold", 54), fill="white")
    d.text((785, 615 + dy), "Caixa d'água", font=g.fonte("regular", 26), fill=CINZA)
    d.text((640, 731 + dy), "Bomba ligada", font=g.fonte("bold", 28), fill="white")
    d.text((652, 812 + dy), "SE nível < 30%", font=g.fonte("bold", 26), fill="white")
    d.text((652, 850 + dy), "→ LIGA a bomba", font=g.fonte("bold", 26), fill=AMBAR)


def planta(d: ImageDraw.ImageDraw, dy: int):
    s = lambda *v: [c * SS for c in v]  # noqa: E731
    for (x, y, r, cor) in [(95, 930, 46, (34, 130, 78)), (60, 980, 40, (46, 160, 92)), (130, 985, 42, (40, 145, 85)),
                           (95, 1005, 44, (52, 172, 100)), (70, 900, 30, (46, 160, 92)), (125, 905, 32, (34, 130, 78))]:
        d.ellipse(s(x - r, y - r + dy, x + r, y + r + dy), fill=cor)
    d.polygon([(55 * SS, (1030 + dy) * SS), (135 * SS, (1030 + dy) * SS), (125 * SS, (1112 + dy) * SS), (65 * SS, (1112 + dy) * SS)], fill=(122, 78, 45))


def arte(altura: int) -> Image.Image:
    story = altura > 1500
    dy = 300 if story else 0
    g.LARGURA, g.ALTURA = 1080, altura
    base = g.fundo(CIANO, 31)

    luz = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(luz).ellipse([60, 420 + dy, 620, 1000 + dy], fill=CIANO + (55,))
    luz = luz.filter(ImageFilter.GaussianBlur(60))
    base.paste(luz, (0, 0), luz)

    grande = base.resize((1080 * SS, altura * SS), Image.LANCZOS)
    d = ImageDraw.Draw(grande)
    planta(d, dy)
    painel(d, dy)
    Boneco(d, 330, 1112 + dy, 7.6).desenhar()
    img = grande.resize((1080, altura), Image.LANCZOS)

    d = ImageDraw.Draw(img)
    painel_texto(d, dy)
    d.text((253, 597 + dy), "DMK", font=g.fonte("bold", 21), fill=ESCURO)  # logo no peito

    topo = 270 if story else 70
    d.rectangle([g.MARGEM, topo + 4, g.MARGEM + 10, topo + 50], fill=CIANO)
    d.text((g.MARGEM + 30, topo), "DMK SMART CORE", font=g.fonte("bold", 40), fill="white")
    f_tit = g.fonte("bold", 64 if story else 60)
    d.text((g.MARGEM, topo + 80), "Conheça o DMK Smart Core", font=f_tit, fill="white")
    d.text((g.MARGEM, topo + 80 + int(f_tit.size * 1.25)), "Automação com ESP32-S3 que funciona sem internet",
           font=g.fonte("regular", 32), fill=CINZA)

    y = chips(d, 1150 + dy + (40 if story else 0), 28 if story else 26)
    if story:
        f = g.fonte("bold", 44)
        t = "Chame no direct  →"
        wb = d.textlength(t, font=f) + 80
        d.rounded_rectangle([(1080 - wb) / 2, y + 20, (1080 + wb) / 2, y + 120], radius=50, fill=CIANO)
        centro(d, y + 40, t, f, ESCURO)
    return img


def main() -> int:
    saida = g.RAIZ / "manual"
    saida.mkdir(exist_ok=True)
    for nome, alt in (("feed", 1350), ("story", 1920)):
        arte(alt).save(saida / f"avatar-{nome}.jpg", "JPEG", quality=92, optimize=True)
        print(f"ok  manual/avatar-{nome}.jpg")
    return 0


if __name__ == "__main__":
    sys.exit(main())
