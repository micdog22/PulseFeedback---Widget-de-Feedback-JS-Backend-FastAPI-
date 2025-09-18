# PulseFeedback — Widget de Feedback (JS) + Backend (FastAPI)

PulseFeedback é um sistema leve e auto‑hospedado para coletar feedback de usuários dentro de qualquer site ou app web.  
Inclui um **widget JS embutível** (um botão flutuante com modal) e um **backend FastAPI** com painel simples para triagem.

> Foco: outra área além de bots/APIs financeiras — aqui você tem um produto de UX/Produto que encaixa em qualquer projeto (landing pages, SaaS, e‑commerce).

---

## Recursos

- **Widget embutível**: um único `<script>` adiciona um botão flutuante com modal.
- **Coleta estruturada**: título, descrição, tipo (Bug, Ideia, Dúvida), URL atual, user agent.
- **Proteção por token**: cada projeto usa `PROJECT_ID` e `INGEST_TOKEN` para envio.
- **Admin Panel**: lista, busca e muda o status (Aberto, Em análise, Resolvido, Rejeitado).
- **API REST** documentada em `/docs`.
- **Banco local** SQLite (SQLAlchemy).

Roadmap sugerido no final do README.

---

## Demo Rápida

1. Clone e rode localmente (ou com Docker).
2. Copie o snippet do widget e coloque em qualquer página HTML.
3. Envie feedback e visualize no painel.

---

## Estrutura do Projeto

```
PulseFeedback/
├─ app/
│  ├─ main.py
│  ├─ db.py
│  ├─ models.py
│  ├─ schemas.py
│  ├─ templates/
│  │  ├─ index.html        # Admin: lista/filtra feedbacks
│  │  └─ login.html        # Admin: login simples (token)
│  └─ static/
│     ├─ admin/styles.css  # CSS do painel
│     └─ widget/widget.js  # Widget injetável no seu site
├─ .env.example
├─ requirements.txt
├─ Dockerfile
├─ docker-compose.yml
├─ LICENSE
└─ README.md
```

---

## Instalação (local)

Pré‑requisitos: Python 3.11+

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edite .env e defina ADMIN_TOKEN, PROJECT_ID e INGEST_TOKEN
uvicorn app.main:app --reload --host 0.0.0.0 --port 7000
```

Acesse:
- Admin: `http://localhost:7000/`  
- Docs: `http://localhost:7000/docs`

---

## Variáveis de Ambiente

- `DATABASE_URL` — padrão `sqlite:///./pulsefeedback.db`.
- `ADMIN_TOKEN` — token para login do painel.
- `PROJECT_ID` — identificador de projeto usado no widget.
- `INGEST_TOKEN` — token secreto para permitir ingest no endpoint público do widget.

Copie `.env.example` para `.env` e ajuste os valores.

---

## Usando o Widget no seu site

1. Hospede este projeto em `https://pulse.seudominio.tld` (ou local).
2. Adicione o snippet abaixo **no `<head>` ou antes de fechar `<body>`** da página onde quer o botão:

```html
<script defer src="https://pulse.seudominio.tld/static/widget/widget.js"
  data-pulse-project="SEU_PROJECT_ID"
  data-pulse-endpoint="https://pulse.seudominio.tld/api/ingest"
  data-pulse-token="SEU_INGEST_TOKEN"></script>
```

3. O botão flutuante será exibido. Ao abrir, o usuário preenche o formulário e o envio ocorre via `fetch` para o endpoint informado.

> Se você preferir, pode self‑hostar o `widget.js` diretamente no seu app. O arquivo não tem dependências externas.

---

## Admin Panel

- Login simples por `ADMIN_TOKEN` (cookie de sessão assinado em memória).
- Lista registros mais recentes, busca por texto e filtro por status.
- Ação de alterar status sem recarregar a página (POST simples).

> Sugestão: em produção, coloque o app atrás de um proxy (Nginx) com autenticação adicional, se necessário.

---

## API

- `POST /api/ingest` — endpoint público de ingestão usado pelo widget.  
  Headers obrigatórios:
  - `X-Project-ID: <PROJECT_ID>`
  - `X-Ingest-Token: <INGEST_TOKEN>`  
  Body JSON:
  ```json
  {
    "title": "Erro no checkout",
    "type": "bug",
    "description": "Botão não responde.",
    "page_url": "https://meusite.tld/checkout",
    "user_agent": "Mozilla/5.0 ..."
  }
  ```
  Retorna `{"status": "stored", "id": 123}`.

- `GET /api/feedback` — lista feedbacks (query: `q`, `status`).  
- `POST /api/feedback/{id}/status` — muda status (requer `ADMIN_TOKEN` via header `X-Admin-Token`).

A documentação interativa está em `/docs`.

---

## Docker

```bash
docker build -t pulsefeedback:latest .
docker run --env-file .env -p 7000:7000 pulsefeedback:latest
```
Ou com `docker-compose`:
```bash
docker compose up --build
```

---

## Segurança

- `INGEST_TOKEN` impede spam simples. Para cenários públicos, considere usar um proxy com rate limit.
- Os dados trafegam em JSON simples; configure HTTPS no seu reverse proxy.
- O painel usa token fixo de admin por simplicidade. Para multiusuários, implemente autenticação completa (OAuth/Keycloak).

---

## Customização

- Cores e posição do botão no `widget.js`.
- Campos extras: adicione no `schemas.py` e no formulário do widget.
- Integrações: crie um webhook interno no `main.py` para enviar para Slack/Discord/Telegram.

---

## Roadmap Sugerido

- Upload opcional de screenshot do DOM (via html2canvas no widget).
- Captura de console errors (listener `window.onerror`).
- SSO para painel (Google OAuth) e RBAC básico.
- Exportação CSV/JSON.
- Multi‑projeto com tabela separada de projetos e rotação de tokens.

---

## Licença

MIT. Veja `LICENSE`.
