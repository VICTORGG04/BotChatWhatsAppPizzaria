# BotChatWhatsAppPizzaria v2.0

Bot inteligente para pedidos de pizza via WhatsApp Business API, com IA (Google Gemini), persistência multi-storage e arquitetura escalável.

## 🚀 Funcionalidades

- **WhatsApp Business API** - Webhook seguro com verificação HMAC-SHA256
- **IA Conversacional** - Google Gemini para entendimento natural e resumo de conversas
- **Máquina de Estados** - Fluxo robusto de pedidos (sabor → tamanho → qtd → pagamento → endereço)
- **Persistência Híbrida** - SQLite (local) + Google Sheets (cloud) + Excel (backup)
- **Processamento Assíncrono** - Celery + Redis para tarefas de I/O não-bloqueantes
- **Sessões Distribuídas** - Redis para escalabilidade horizontal
- **Type Safety** - Pydantic v2 para validação de dados
- **Observabilidade** - Structlog (JSON) + Health checks
- **Containerização** - Docker + Docker Compose prontos para produção

## 🏗️ Arquitetura

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  WhatsApp   │────▶│   Flask      │────▶│  Session    │
│  Business   │     │   Webhook    │     │  Manager    │
│  API        │     │  (app.py)    │     │  (Redis)    │
└─────────────┘     └──────┬───────┘     └─────────────┘
                           │
                    ┌──────▼───────┐
                    │  Chatbot     │
                    │  Core        │
                    │ (states.py)  │
                    └──────┬───────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │  SQLite    │  │Google Sheets│ │   Excel    │
    │  (tasks)   │  │  (tasks)    │  │  (tasks)   │
    └────────────┘  └────────────┘  └────────────┘
           ▲               ▲               ▲
           └───────────────┼───────────────┘
                           ▼
                    ┌────────────┐
                    │   Celery   │
                    │  Workers   │
                    └────────────┘
```

## 📦 Estrutura do Projeto

```
BotChatWhatsAppPizzaria/
├── app.py                 # Flask app + webhook endpoints
├── config.py              # Configuração centralizada (Pydantic Settings)
├── models.py              # Modelos Pydantic (type-safe)
├── security.py            # Verificação HMAC WhatsApp
├── session_manager.py     # Gerenciador de sessões Redis
├── celery_app.py          # Configuração Celery
├── tasks.py               # Tasks assíncronas (I/O)
├── requirements.txt       # Dependências pinned
├── Dockerfile             # Imagem Docker otimizada
├── docker-compose.yml     # Orquestração local
├── .env.example           # Template de variáveis de ambiente
├── .github/workflows/     # CI/CD GitHub Actions
├── chatbot/               # Módulo principal do bot
│   ├── __init__.py        # Exports públicos
│   ├── cardapio.py        # Gerenciamento de cardápio
│   ├── states.py          # Máquina de estados
│   ├── service.py         # Orquestração de pedidos
│   ├── ai.py              # Integração Gemini
│   └── storage/           # Backends de persistência
│       ├── __init__.py
│       ├── sqlite.py
│       ├── sheets.py
│       └── excel.py
├── tests/                 # Testes automatizados
│   ├── test_models.py
│   ├── test_security_session.py
│   └── test_webhook.py
└── simulacao_pizzaria.py  # Simulador de pedidos (dev)
```

## ⚙️ Configuração

### 1. Clone e configure o ambiente

```bash
git clone https://github.com/SEU_USUARIO/BotChatWhatsAppPizzaria.git
cd BotChatWhatsAppPizzaria

# Copie o template de variáveis
cp .env.example .env

# Edite com suas credenciais
nano .env
```

### 2. Variáveis Obrigatórias

| Variável | Descrição | Onde obter |
|----------|-----------|------------|
| `WHATSAPP_VERIFY_TOKEN` | Token para verificação do webhook | Meta Developer Console |
| `WHATSAPP_PHONE_NUMBER_ID` | ID do número de telefone | Meta Developer Console |
| `WHATSAPP_ACCESS_TOKEN` | Token de acesso (curta duração) | Meta Developer Console |
| `WHATSAPP_APP_SECRET` | App Secret para HMAC | Meta Developer Console > Configurações > Básico |
| `GEMINI_API_KEY` | Chave da API Gemini | Google AI Studio |
| `GOOGLE_CREDENTIALS_PATH` | Caminho para credentials.json | Google Cloud Console (Service Account) |

### 3. Google Sheets Setup

1. Crie um Service Account no [Google Cloud Console](https://console.cloud.google.com/)
2. Ative **Google Sheets API** e **Google Drive API**
3. Baixe o JSON de credenciais → salve como `credentials.json`
4. Crie uma planilha chamada "Pedidos da Pizzaria"
5. Compartilhe com o email do Service Account (editor)

## 🐳 Execução com Docker (Recomendado)

```bash
# Build e start de todos os serviços
docker-compose up -d --build

# Ver logs
docker-compose logs -f app

# Parar
docker-compose down
```

Serviços incluídos:
- **app** - Flask webhook (porta 5000)
- **redis** - Cache/sessões/broker
- **worker** - Celery worker (tasks assíncronas)
- **beat** - Celery beat (scheduler)

## 💻 Execução Local (Desenvolvimento)

```bash
# Criar venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependências
pip install -r requirements.txt

# Iniciar Redis (separado)
redis-server

# Terminal 1: Celery worker
celery -A celery_app worker -l INFO -Q sheets,excel,database,default

# Terminal 2: Celery beat (opcional)
celery -A celery_app beat -l INFO

# Terminal 3: Flask app
python app.py
```

## 🧪 Testes

```bash
# Todos os testes com coverage
pytest -v --cov=chatbot --cov=app --cov=models --cov=session_manager --cov=config --cov=security

# Testes específicos
pytest tests/test_models.py -v
pytest tests/test_security_session.py -v
pytest tests/test_webhook.py -v

# Linting
ruff check .
ruff format --check .

# Type checking
mypy chatbot/ app.py config.py models.py security.py session_manager.py tasks.py celery_app.py
```

## 📡 Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/health` | Health check (Docker/load balancer) |
| `GET` | `/webhook` | Verificação do webhook WhatsApp (challenge) |
| `POST` | `/webhook` | Recebe mensagens do WhatsApp |
| `GET` | `/admin/pedidos` | Lista pedidos do dia (admin) |
| `GET` | `/admin/stats` | Estatísticas do dia (admin) |

## 🔒 Segurança

- **HMAC-SHA256** - Verificação de assinatura do WhatsApp em toda request POST
- **Non-root Docker** - Container roda como usuário `appuser`
- **Secrets via Env** - Nenhum segredo no código
- **Rate Limiting** - Implementar no load balancer (nginx/Traefik)
- **HTTPS Obrigatório** - WhatsApp requer TLS válido

## 📊 Monitoramento

```bash
# Health check
curl http://localhost:5000/health

# Métricas Celery (Flower)
pip install flower
celery -A celery_app flower --port=5555
# Acesse http://localhost:5555
```

## 🚀 Deploy em Produção

### Opção 1: Docker Swarm / Kubernetes
```bash
# Build e push para registry
docker build -t ghcr.io/seu-usuario/pizzaria-bot:latest .
docker push ghcr.io/seu-usuario/pizzaria-bot:latest

# Deploy com stack deploy.yml
# docker stack deploy -c docker-compose.yml pizzaria
```

### Opção 2: VPS com Systemd
```bash
# Copie arquivos para /opt/pizzaria-bot
# Configure .env de produção
# Crie service systemd para app, worker, beat
sudo systemctl enable pizzaria-bot-app pizzaria-bot-worker pizzaria-bot-beat
sudo systemctl start pizzaria-bot-app pizzaria-bot-worker pizzaria-bot-beat
```

### Variáveis de Produção
```bash
APP_ENV=production
DEBUG=false
LOG_LEVEL=WARNING
SESSION_TTL_SECONDS=3600
# Use Redis gerenciado (AWS ElastiCache, Azure Redis, etc.)
REDIS_HOST=seu-redis.xxxxxx.use1.cache.amazonaws.com
REDIS_PASSWORD=senha_forte
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -m 'feat: adiciona nova funcionalidade'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra Pull Request

### Padrões de Commit
- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `refactor:` Refatoração
- `docs:` Documentação
- `test:` Testes
- `chore:` Manutenção

## 📄 Licença

MIT License - veja [LICENSE](LICENSE)

## 🆘 Suporte

- **Issues**: [GitHub Issues](https://github.com/SEU_USUARIO/BotChatWhatsAppPizzaria/issues)
- **Discussões**: [GitHub Discussions](https://github.com/SEU_USUARIO/BotChatWhatsAppPizzaria/discussions)

---

**Desenvolvido com ❤️ para automação de pizzarias**