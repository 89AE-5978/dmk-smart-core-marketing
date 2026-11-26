# DMK Smart Core — Publicação automática no Instagram

Publica **uma propaganda por dia às 08h (Brasília)** no Instagram do DMK Smart Core, usando a
**API oficial da Meta** e o **GitHub Actions** (gratuito). São 30 posts prontos em rodízio sobre
ESP32-S3, funcionamento local sem internet, aplicativo, regras inteligentes e gestão de água.

## Estrutura

| Caminho | O que é |
|---|---|
| `content/posts.json` | 30 posts: título e subtítulo da arte e legenda |
| `content/config.json` | data de início do rodízio, hashtags, chamada final, fuso |
| `docs/images/post-XX.jpg` | artes 1080×1350 (servidas pelo GitHub Pages) |
| `scripts/gerar_imagens.py` | gera as artes a partir dos textos (uso local, requer Pillow) |
| `scripts/publicar.py` | publica o post do dia (só biblioteca padrão do Python) |
| `scripts/renovar_token.py` | renova o token de 60 dias |
| `.github/workflows/publicar-instagram.yml` | agendamento diário 11:00 UTC = 08:00 Brasília |
| `.github/workflows/renovar-token.yml` | renovação mensal do token |
| `historico/publicacoes.csv` | criado automaticamente com cada publicação |

O post do dia é escolhido pela data: `(hoje − data_inicio) mod 30`. Não há estado a manter, e o
script verifica na própria conta se o post do dia já saiu, evitando duplicidade.

## 1. Configurar a conta do Instagram e a Meta (feito por você)

1. **Instagram → Configurações → Tipo de conta**: mude para **Comercial** ou **Criador de conteúdo**.
2. Em **developers.facebook.com**, crie (ou use) sua conta de desenvolvedor.
3. **Criar app** → tipo *Business* → adicione o produto **Instagram** →
   **"API do Instagram com login do Instagram"** (não exige Página do Facebook).
4. Em *Funções do app*, garanta que a conta do Instagram do DMK tenha função (admin/testador).
5. Gere o token com as permissões `instagram_business_basic` e
   `instagram_business_content_publish`. Converta para **token de longa duração** (60 dias).
6. Anote o **ID da conta do Instagram** (`user_id`), exibido no painel ao gerar o token
   (ou via `GET https://graph.instagram.com/me?fields=user_id,username`).

> Alternativa: "API do Instagram com login do Facebook" (exige Página do Facebook vinculada).
> Nesse caso use `GRAPH_HOST=graph.facebook.com`, um token de **Usuário do Sistema** do
> Business Manager (não expira) e **desative** o workflow de renovação de token.

## 2. Criar o repositório no GitHub

1. Crie um repositório (público, para o GitHub Pages gratuito) e envie esta pasta.
2. **Settings → Pages**: *Deploy from a branch* → `main` → pasta `/docs`.
   Confira se `https://SEU-USUARIO.github.io/SEU-REPO/images/post-01.jpg` abre.
3. **Settings → Secrets and variables → Actions**:

   | Tipo | Nome | Valor |
   |---|---|---|
   | Secret | `IG_ACCESS_TOKEN` | token de longa duração |
   | Secret | `IG_USER_ID` | ID da conta do Instagram |
   | Secret | `GH_PAT` | token fine-grained do GitHub com *Secrets: Read and write* só neste repo (para renovar o token) |
   | Variable | `PAGES_BASE_URL` | `https://SEU-USUARIO.github.io/SEU-REPO` |
   | Variable | `PUBLICACAO_ATIVA` | `false` até testar; depois `true` |
   | Variable (opcional) | `GRAPH_HOST` | `graph.instagram.com` (padrão) |
   | Variable (opcional) | `GRAPH_API_VERSION` | `v23.0` (padrão) |

4. **Settings → Actions → General → Workflow permissions**: mantenha *Read repository contents*
   (padrão seguro). O workflow de publicação já pede `contents: write` só para ele mesmo.
5. Anote a **data de expiração do `GH_PAT`** e renove-o antes do vencimento; sem ele, a
   renovação mensal do token do Instagram falha e o token expira 60 dias depois.

## 3. Testar e ligar

1. **Actions → Publicar no Instagram → Run workflow** com modo `validar`: testa token,
   conta @dmksmartcore, limite de publicação e imagem pública na API real, sem publicar.
2. Para o primeiro post real: defina `PUBLICACAO_ATIVA=true` e rode manualmente com modo
   `publicar`. Confira o post no Instagram.
3. A partir daí, o agendamento publica sozinho todo dia às 08h.
4. Para pausar a qualquer momento: `PUBLICACAO_ATIVA=false`.

## Uso local

```powershell
python scripts\publicar.py --simular
python scripts\publicar.py --simular --data 2026-12-05
```

Para editar textos e regenerar as artes:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install pillow
.venv\Scripts\python scripts\gerar_imagens.py
```

Para usar artes próprias, substitua `docs/images/post-XX.jpg` mantendo o nome (JPEG,
proporção entre 4:5 e 1,91:1).

## Observações

- O GitHub pode atrasar execuções agendadas em alguns minutos.
- Repositórios sem atividade por 60 dias têm agendamentos desativados; o commit diário do
  histórico evita isso.
- Revise as legendas em `content/posts.json` para garantir que todas as afirmações
  correspondem ao produto atual.
