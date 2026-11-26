"""Renova o token de longa duração (60 dias) da API do Instagram com login do Instagram.

Lê IG_ACCESS_TOKEN do ambiente e grava o token novo no arquivo indicado
(nunca imprime o token). O workflow depois salva esse arquivo no segredo do GitHub.

Uso:
    python scripts/renovar_token.py CAMINHO_DO_ARQUIVO_DE_SAIDA

Observação: só se aplica ao caminho "login do Instagram" (graph.instagram.com).
Quem usa token de Usuário do Sistema (login do Facebook) não precisa renovar.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    token = os.environ.get("IG_ACCESS_TOKEN", "").strip()
    if not token:
        print("ERRO: IG_ACCESS_TOKEN não definido.", file=sys.stderr)
        return 1

    params = urllib.parse.urlencode({"grant_type": "ig_refresh_token", "access_token": token})
    try:
        with urllib.request.urlopen(f"https://graph.instagram.com/refresh_access_token?{params}", timeout=60) as r:
            dados = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f"ERRO: HTTP {e.code} ao renovar token: {e.read().decode(errors='replace')[:300]}", file=sys.stderr)
        return 1

    novo = dados.get("access_token")
    if not novo:
        print("ERRO: resposta sem access_token.", file=sys.stderr)
        return 1
    # Mascara o token nos logs do GitHub Actions, caso apareça por engano.
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::add-mask::{novo}")
    with open(sys.argv[1], "w", encoding="utf-8") as f:
        f.write(novo)
    dias = int(dados.get("expires_in", 0)) // 86400
    print(f"Token renovado. Validade aproximada: {dias} dias.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
