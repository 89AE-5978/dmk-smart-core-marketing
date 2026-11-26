"""Publica o post do dia no Instagram pela API oficial da Meta (Instagram Graph API).

Só usa a biblioteca padrão do Python.

Variáveis de ambiente:
    IG_ACCESS_TOKEN    token de acesso (segredo; nunca é impresso)
    IG_USER_ID         ID da conta profissional do Instagram
    PAGES_BASE_URL     URL pública onde estão as imagens, ex.: https://usuario.github.io/repo
    GRAPH_HOST         graph.instagram.com (login do Instagram, padrão) ou graph.facebook.com
    GRAPH_API_VERSION  versão da API, ex.: v23.0 (padrão)

Uso:
    python scripts/publicar.py --simular          # mostra o que seria publicado, sem rede
    python scripts/publicar.py --simular --data 2026-12-05
    python scripts/publicar.py                    # publica de verdade
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CONFIG = json.loads((RAIZ / "content" / "config.json").read_text(encoding="utf-8"))
POSTS = json.loads((RAIZ / "content" / "posts.json").read_text(encoding="utf-8"))
HISTORICO = RAIZ / "historico" / "publicacoes.csv"

LIMITE_LEGENDA = 2200
LIMITE_HASHTAGS = 30


class ErroPublicacao(Exception):
    pass


# ---------------------------------------------------------------- conteúdo

def hoje_local() -> dt.date:
    fuso = dt.timezone(dt.timedelta(hours=CONFIG["fuso_utc_horas"]))
    return dt.datetime.now(fuso).date()


def post_do_dia(data: dt.date) -> dict:
    inicio = dt.date.fromisoformat(CONFIG["data_inicio"])
    return POSTS[(data - inicio).days % len(POSTS)]


def nome_imagem(post: dict) -> str:
    return f"post-{post['id']:02d}.jpg"


def montar_legenda(post: dict) -> str:
    partes = [post["legenda"].strip()]
    if CONFIG.get("chamada_padrao") and post.get("tema") != "cta":
        partes.append(CONFIG["chamada_padrao"])
    if CONFIG.get("hashtags"):
        partes.append(" ".join(CONFIG["hashtags"]))
    return "\n\n".join(partes)


def validar_conteudo() -> list[str]:
    erros = []
    ids = [p["id"] for p in POSTS]
    if len(ids) != len(set(ids)):
        erros.append("IDs de posts repetidos em content/posts.json")
    if len(CONFIG.get("hashtags", [])) > LIMITE_HASHTAGS:
        erros.append(f"Mais de {LIMITE_HASHTAGS} hashtags em content/config.json")
    for p in POSTS:
        img = RAIZ / "docs" / CONFIG["pasta_imagens_publica"] / nome_imagem(p)
        if not img.exists():
            erros.append(f"Post {p['id']}: imagem ausente ({img.relative_to(RAIZ)})")
        if len(montar_legenda(p)) > LIMITE_LEGENDA:
            erros.append(f"Post {p['id']}: legenda passa de {LIMITE_LEGENDA} caracteres")
    return erros


# ---------------------------------------------------------------- API

def _env(nome: str) -> str:
    valor = os.environ.get(nome, "").strip()
    if not valor:
        raise ErroPublicacao(f"Variável de ambiente {nome} não definida.")
    return valor


def _base_api() -> str:
    host = os.environ.get("GRAPH_HOST", "graph.instagram.com").strip() or "graph.instagram.com"
    versao = os.environ.get("GRAPH_API_VERSION", "v23.0").strip() or "v23.0"
    return f"https://{host}/{versao}"


def chamar(metodo: str, caminho: str, params: dict) -> dict:
    params = dict(params, access_token=_env("IG_ACCESS_TOKEN"))
    dados = urllib.parse.urlencode(params).encode()
    url = f"{_base_api()}/{caminho}"
    if metodo == "GET":
        req = urllib.request.Request(f"{url}?{dados.decode()}", method="GET")
    else:
        req = urllib.request.Request(url, data=dados, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        corpo = e.read().decode(errors="replace")
        try:
            erro = json.loads(corpo).get("error", {})
            msg = f"{erro.get('type', '')} {erro.get('code', '')}: {erro.get('message', corpo)}"
        except json.JSONDecodeError:
            msg = corpo[:500]
        raise ErroPublicacao(f"API respondeu HTTP {e.code} em {caminho}: {msg}") from None


def checar_imagem_publica(url: str) -> None:
    req = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            tipo = resp.headers.get("Content-Type", "")
            if "jpeg" not in tipo:
                raise ErroPublicacao(f"Imagem {url} não é JPEG (Content-Type: {tipo}).")
    except urllib.error.URLError as e:
        raise ErroPublicacao(f"Imagem não está acessível publicamente: {url} ({e})") from None


def ja_publicado_hoje(ig_user: str, legenda: str, data: dt.date) -> bool:
    """Evita post duplicado se o workflow rodar duas vezes no mesmo dia."""
    resp = chamar("GET", f"{ig_user}/media", {"fields": "id,caption,timestamp", "limit": "10"})
    fuso = dt.timezone(dt.timedelta(hours=CONFIG["fuso_utc_horas"]))
    inicio_legenda = legenda[:80]
    for m in resp.get("data", []):
        ts = dt.datetime.strptime(m["timestamp"], "%Y-%m-%dT%H:%M:%S%z").astimezone(fuso)
        if ts.date() == data and (m.get("caption") or "").startswith(inicio_legenda):
            return True
    return False


def validar_api(post: dict, data: dt.date) -> None:
    """Testa a comunicação real com a API da Meta sem publicar nada."""
    ig_user = _env("IG_USER_ID")
    me = chamar("GET", "me", {"fields": "user_id,username,account_type"})
    esperado = CONFIG.get("conta_instagram", "").lower()
    print(f"Conta: @{me.get('username')}  tipo: {me.get('account_type')}")
    if str(me.get("user_id")) != ig_user:
        raise ErroPublicacao("IG_USER_ID não corresponde ao user_id da conta do token.")
    if esperado and (me.get("username") or "").lower() != esperado:
        raise ErroPublicacao(f"Token pertence a @{me.get('username')}, esperado @{esperado}.")
    if me.get("account_type") not in ("BUSINESS", "MEDIA_CREATOR"):
        raise ErroPublicacao("A conta não é profissional (Comercial/Criador).")
    limite = chamar("GET", f"{ig_user}/content_publishing_limit", {"fields": "quota_usage,config"})
    print(f"Limite de publicação: {json.dumps(limite.get('data', limite), ensure_ascii=False)}")
    base_pages = _env("PAGES_BASE_URL").rstrip("/")
    url_imagem = f"{base_pages}/{CONFIG['pasta_imagens_publica']}/{nome_imagem(post)}"
    checar_imagem_publica(url_imagem)
    print(f"Imagem pública OK: {url_imagem}")
    hoje = ja_publicado_hoje(ig_user, montar_legenda(post), data)
    print(f"Leitura de mídias OK. Post de hoje já publicado: {'sim' if hoje else 'não'}")
    print("VALIDAÇÃO OK: comunicação real com a API da Meta funcionando. Nada foi publicado.")


def publicar(post: dict, data: dt.date) -> str:
    ig_user = _env("IG_USER_ID")
    base_pages = _env("PAGES_BASE_URL").rstrip("/")
    url_imagem = f"{base_pages}/{CONFIG['pasta_imagens_publica']}/{nome_imagem(post)}"
    legenda = montar_legenda(post)

    checar_imagem_publica(url_imagem)
    if ja_publicado_hoje(ig_user, legenda, data):
        print("Post de hoje já foi publicado. Nada a fazer.")
        return ""

    container = chamar("POST", f"{ig_user}/media", {"image_url": url_imagem, "caption": legenda})["id"]
    print(f"Container criado: {container}")

    for _ in range(30):
        status = chamar("GET", container, {"fields": "status_code"}).get("status_code")
        if status == "FINISHED":
            break
        if status in ("ERROR", "EXPIRED"):
            raise ErroPublicacao(f"Container {container} com status {status}.")
        time.sleep(5)
    else:
        raise ErroPublicacao(f"Container {container} não ficou pronto a tempo.")

    media_id = chamar("POST", f"{ig_user}/media_publish", {"creation_id": container})["id"]
    link = chamar("GET", media_id, {"fields": "permalink"}).get("permalink", "")
    print(f"Publicado! media_id={media_id} {link}")
    return media_id


def registrar(data: dt.date, post: dict, media_id: str) -> None:
    HISTORICO.parent.mkdir(parents=True, exist_ok=True)
    novo = not HISTORICO.exists()
    with HISTORICO.open("a", encoding="utf-8", newline="") as f:
        if novo:
            f.write("data,post_id,titulo,media_id\n")
        titulo = post["titulo"].replace('"', "'")
        f.write(f'{data.isoformat()},{post["id"]},"{titulo}",{media_id}\n')


# ---------------------------------------------------------------- CLI

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--simular", action="store_true", help="não chama a API, só mostra o post do dia")
    ap.add_argument("--validar", action="store_true", help="testa token, conta, limite e imagem na API real, sem publicar")
    ap.add_argument("--data", help="data no formato AAAA-MM-DD (padrão: hoje em Brasília)")
    args = ap.parse_args()

    erros = validar_conteudo()
    if erros:
        print("Problemas no conteúdo:\n- " + "\n- ".join(erros), file=sys.stderr)
        return 1

    data = dt.date.fromisoformat(args.data) if args.data else hoje_local()
    post = post_do_dia(data)
    print(f"Data: {data}  |  Post {post['id']}/{len(POSTS)}: {post['titulo']}  |  Imagem: {nome_imagem(post)}")

    if args.simular:
        print("\n--- LEGENDA ---\n" + montar_legenda(post) + "\n---------------")
        print("Modo simulação: nada foi publicado.")
        return 0

    try:
        if args.validar:
            validar_api(post, data)
            return 0
        media_id = publicar(post, data)
    except ErroPublicacao as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 1
    if media_id:
        registrar(data, post, media_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
