# Makefile - BotChatWhatsAppPizzaria
# Comandos comuns de desenvolvimento

.PHONY: help install test lint format typecheck security docker-build docker-up docker-down docker-logs clean

# Default target
help:
	@echo "BotChatWhatsAppPizzaria - Comandos disponíveis:"
	@echo ""
	@echo "Desenvolvimento:"
	@echo "  make install       - Instala dependências"
	@echo "  make test          - Executa testes com coverage"
	@echo "  make lint          - Executa ruff (linting)"
	@echo "  make format        - Formata código com ruff"
	@echo "  make typecheck     - Executa mypy (type checking)"
	@echo "  make security      - Executa bandit + safety"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build  - Build da imagem Docker"
	@echo "  make docker-up     - Sobe stack completo (docker-compose)"
	@echo "  make docker-down   - Para stack"
	@echo "  make docker-logs   - Mostra logs"
	@echo "  make docker-shell  - Shell no container app"
	@echo ""
	@echo "Utilitários:"
	@echo "  make clean         - Remove arquivos temporários"
	@echo "  make db-setup      - Inicializa banco SQLite"
	@echo "  make simulate      - Roda simulação de 100 pedidos"

# ==============================================================================
# DESENVOLVIMENTO
# ==============================================================================

install:
	pip install --upgrade pip
	pip install -r requirements.txt

test:
	pytest -v --cov=chatbot --cov=app --cov=models --cov=session_manager --cov=config --cov=security \
		--cov-report=term-missing --cov-report=html --cov-fail-under=70

test-watch:
	ptw --runner "pytest -v --cov=chatbot --cov=app --cov=models" .

lint:
	ruff check . --output-format=github

format:
	ruff format .

format-check:
	ruff format --check .

typecheck:
	mypy chatbot/ app.py config.py models.py security.py session_manager.py tasks.py celery_app.py --ignore-missing-imports

security:
	bandit -r . -f json -o bandit-report.json --severity-level medium --confidence-level high || true
	bandit -r . --severity-level medium --confidence-level high
	safety check --json --output safety-report.json || true
	safety check

# ==============================================================================
# DOCKER
# ==============================================================================

docker-build:
	docker build -t pizzaria-bot:latest .

docker-up:
	docker-compose up -d --build

docker-down:
	docker-compose down -v

docker-logs:
	docker-compose logs -f --tail=100

docker-shell:
	docker-compose exec app bash

docker-ps:
	docker-compose ps

# ==============================================================================
# UTILITÁRIOS
# ==============================================================================

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	rm -f .coverage coverage.xml bandit-report.json safety-report.json celerybeat-schedule celerybeat.pid

db-setup:
	python -c "from chatbot.storage.sqlite import setup_database; setup_database(); print('Banco inicializado')"

simulate:
	python test_simulacao_100_pedidos.py

run-dev:
	python app.py

run-worker:
	celery -A celery_app worker -l INFO -Q sheets,excel,database,default

run-beat:
	celery -A celery_app beat -l INFO --scheduler celery.beat.PersistentScheduler

run-flower:
	celery -A celery_app flower --port=5555

# ==============================================================================
# CI/CD LOCAL
# ==============================================================================

ci-local: format-check lint typecheck test security
	@echo "✅ Todos os checks locais passaram!"

pre-commit: format-check lint typecheck test
	@echo "✅ Pre-commit checks passed!"

# ==============================================================================
# DEPLOY (exemplos)
# ==============================================================================

deploy-staging:
	@echo "Deploy para staging..."
	# kubectl set image deployment/pizzaria-bot pizzaria-bot=ghcr.io/user/repo:staging

deploy-prod:
	@echo "Deploy para produção..."
	# kubectl set image deployment/pizzaria-bot pizzaria-bot=ghcr.io/user/repo:latest