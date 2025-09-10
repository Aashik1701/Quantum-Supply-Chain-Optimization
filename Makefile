# Hybrid Quantum-Classical Supply Chain Optimization
# Makefile for development and deployment automation

# Variables
PROJECT_NAME=quantum-supply-chain
BACKEND_DIR=backend
FRONTEND_DIR=frontend
DOCKER_COMPOSE=docker-compose
PYTHON=python3
NODE=node
NPM=npm

# Colors for output
GREEN=\033[0;32m
YELLOW=\033[1;33m
RED=\033[0;31m
NC=\033[0m # No Color

.PHONY: help install build run test clean deploy stop logs status

# Default target
.DEFAULT_GOAL := help

# Help target
help: ## Show this help message
	@echo "$(GREEN)Hybrid Quantum-Classical Supply Chain Optimization$(NC)"
	@echo "$(YELLOW)Available commands:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# =============================================================================
# DEVELOPMENT COMMANDS
# =============================================================================

install: ## Install all dependencies (backend + frontend)
	@echo "$(GREEN)Installing dependencies...$(NC)"
	@make install-backend
	@make install-frontend
	@echo "$(GREEN)All dependencies installed successfully!$(NC)"

install-backend: ## Install backend dependencies
	@echo "$(YELLOW)Installing backend dependencies...$(NC)"
	cd $(BACKEND_DIR) && python -m pip install --upgrade pip
	cd $(BACKEND_DIR) && pip install -r requirements.txt
	@echo "$(GREEN)Backend dependencies installed!$(NC)"

install-frontend: ## Install frontend dependencies
	@echo "$(YELLOW)Installing frontend dependencies...$(NC)"
	cd $(FRONTEND_DIR) && $(NPM) install
	@echo "$(GREEN)Frontend dependencies installed!$(NC)"

# =============================================================================
# BUILD COMMANDS
# =============================================================================

build: ## Build all services (Docker)
	@echo "$(GREEN)Building all services...$(NC)"
	$(DOCKER_COMPOSE) build --no-cache
	@echo "$(GREEN)All services built successfully!$(NC)"

build-backend: ## Build backend service only
	@echo "$(YELLOW)Building backend service...$(NC)"
	$(DOCKER_COMPOSE) build backend

build-frontend: ## Build frontend service only
	@echo "$(YELLOW)Building frontend service...$(NC)"
	$(DOCKER_COMPOSE) build frontend

build-prod: ## Build production images
	@echo "$(GREEN)Building production images...$(NC)"
	$(DOCKER_COMPOSE) -f docker-compose.prod.yml build
	@echo "$(GREEN)Production images built successfully!$(NC)"

# =============================================================================
# RUN COMMANDS
# =============================================================================

run: ## Run the full application stack
	@echo "$(GREEN)Starting the application stack...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)Application is running!$(NC)"
	@echo "$(YELLOW)Frontend: http://localhost:3000$(NC)"
	@echo "$(YELLOW)Backend API: http://localhost:5000$(NC)"
	@echo "$(YELLOW)Database: localhost:5432$(NC)"

run-dev: ## Run in development mode with hot reload
	@echo "$(GREEN)Starting development environment...$(NC)"
	$(DOCKER_COMPOSE) up

run-backend: ## Run backend service only
	@echo "$(YELLOW)Starting backend service...$(NC)"
	cd $(BACKEND_DIR) && $(PYTHON) app.py

run-frontend: ## Run frontend service only
	@echo "$(YELLOW)Starting frontend service...$(NC)"
	cd $(FRONTEND_DIR) && $(NPM) run dev

run-local: ## Run services locally (without Docker)
	@echo "$(GREEN)Starting local development...$(NC)"
	@make run-backend &
	@make run-frontend &
	@echo "$(GREEN)Local services started!$(NC)"

# =============================================================================
# TEST COMMANDS
# =============================================================================

test: ## Run all tests
	@echo "$(GREEN)Running all tests...$(NC)"
	@make test-backend
	@make test-frontend
	@echo "$(GREEN)All tests completed!$(NC)"

test-backend: ## Run backend tests
	@echo "$(YELLOW)Running backend tests...$(NC)"
	cd $(BACKEND_DIR) && python -m pytest tests/ -v --cov=api --cov-report=html

test-frontend: ## Run frontend tests
	@echo "$(YELLOW)Running frontend tests...$(NC)"
	cd $(FRONTEND_DIR) && $(NPM) test

test-integration: ## Run integration tests
	@echo "$(YELLOW)Running integration tests...$(NC)"
	cd $(BACKEND_DIR) && python -m pytest tests/integration/ -v

test-performance: ## Run performance benchmarks
	@echo "$(YELLOW)Running performance benchmarks...$(NC)"
	cd $(BACKEND_DIR) && python scripts/benchmark.py

lint: ## Run code linting
	@echo "$(YELLOW)Linting code...$(NC)"
	cd $(BACKEND_DIR) && flake8 . && black --check .
	cd $(FRONTEND_DIR) && $(NPM) run lint

lint-fix: ## Fix linting issues
	@echo "$(YELLOW)Fixing linting issues...$(NC)"
	cd $(BACKEND_DIR) && black .
	cd $(FRONTEND_DIR) && $(NPM) run lint:fix

# =============================================================================
# DATABASE COMMANDS
# =============================================================================

db-setup: ## Set up database with initial data
	@echo "$(YELLOW)Setting up database...$(NC)"
	$(DOCKER_COMPOSE) exec backend python scripts/setup_database.py
	@echo "$(GREEN)Database setup completed!$(NC)"

db-migrate: ## Run database migrations
	@echo "$(YELLOW)Running database migrations...$(NC)"
	$(DOCKER_COMPOSE) exec backend alembic upgrade head

db-seed: ## Seed database with sample data
	@echo "$(YELLOW)Seeding database with sample data...$(NC)"
	$(DOCKER_COMPOSE) exec backend python scripts/seed_data.py

db-reset: ## Reset database (WARNING: This will delete all data)
	@echo "$(RED)WARNING: This will delete all database data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(DOCKER_COMPOSE) exec backend python scripts/reset_database.py; \
		echo "$(GREEN)Database reset completed!$(NC)"; \
	fi

# =============================================================================
# MONITORING COMMANDS
# =============================================================================

logs: ## View application logs
	@echo "$(YELLOW)Showing application logs...$(NC)"
	$(DOCKER_COMPOSE) logs -f

logs-backend: ## View backend logs
	$(DOCKER_COMPOSE) logs -f backend

logs-frontend: ## View frontend logs
	$(DOCKER_COMPOSE) logs -f frontend

logs-db: ## View database logs
	$(DOCKER_COMPOSE) logs -f postgres

status: ## Check service status
	@echo "$(GREEN)Service Status:$(NC)"
	$(DOCKER_COMPOSE) ps

health: ## Check application health
	@echo "$(YELLOW)Checking application health...$(NC)"
	@curl -f http://localhost:5000/health || echo "$(RED)Backend health check failed$(NC)"
	@curl -f http://localhost:3000 || echo "$(RED)Frontend health check failed$(NC)"

# =============================================================================
# DEPLOYMENT COMMANDS
# =============================================================================

deploy: ## Deploy to production
	@echo "$(GREEN)Deploying to production...$(NC)"
	@make build-prod
	$(DOCKER_COMPOSE) -f docker-compose.prod.yml up -d
	@echo "$(GREEN)Production deployment completed!$(NC)"

deploy-staging: ## Deploy to staging environment
	@echo "$(YELLOW)Deploying to staging...$(NC)"
	$(DOCKER_COMPOSE) -f docker-compose.staging.yml up -d

deploy-local: ## Deploy locally for testing
	@echo "$(YELLOW)Deploying locally...$(NC)"
	@make build
	@make run

# =============================================================================
# UTILITY COMMANDS
# =============================================================================

stop: ## Stop all services
	@echo "$(YELLOW)Stopping all services...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)All services stopped!$(NC)"

restart: ## Restart all services
	@echo "$(YELLOW)Restarting all services...$(NC)"
	@make stop
	@make run

clean: ## Clean up containers, images, and volumes
	@echo "$(YELLOW)Cleaning up...$(NC)"
	$(DOCKER_COMPOSE) down -v --rmi all --remove-orphans
	docker system prune -f
	@echo "$(GREEN)Cleanup completed!$(NC)"

clean-cache: ## Clean application caches
	@echo "$(YELLOW)Cleaning caches...$(NC)"
	cd $(BACKEND_DIR) && find . -type d -name "__pycache__" -delete
	cd $(FRONTEND_DIR) && rm -rf node_modules/.cache
	@echo "$(GREEN)Caches cleaned!$(NC)"

backup: ## Backup database
	@echo "$(YELLOW)Creating database backup...$(NC)"
	$(DOCKER_COMPOSE) exec postgres pg_dump -U postgres supply_chain > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)Database backup created!$(NC)"

# =============================================================================
# DEVELOPMENT TOOLS
# =============================================================================

shell: ## Open shell in backend container
	$(DOCKER_COMPOSE) exec backend /bin/bash

shell-db: ## Open database shell
	$(DOCKER_COMPOSE) exec postgres psql -U postgres -d supply_chain

shell-redis: ## Open Redis CLI
	$(DOCKER_COMPOSE) exec redis redis-cli

format: ## Format code
	@echo "$(YELLOW)Formatting code...$(NC)"
	cd $(BACKEND_DIR) && black . && isort .
	cd $(FRONTEND_DIR) && $(NPM) run format

docs: ## Generate documentation
	@echo "$(YELLOW)Generating documentation...$(NC)"
	cd $(BACKEND_DIR) && sphinx-build -b html docs/ docs/_build/
	@echo "$(GREEN)Documentation generated in backend/docs/_build/$(NC)"

env: ## Create .env file from template
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(GREEN).env file created from template$(NC)"; \
		echo "$(YELLOW)Please edit .env file with your configuration$(NC)"; \
	else \
		echo "$(YELLOW).env file already exists$(NC)"; \
	fi

# =============================================================================
# QUANTUM COMPUTING SPECIFIC
# =============================================================================

quantum-test: ## Test quantum computing setup
	@echo "$(YELLOW)Testing quantum computing setup...$(NC)"
	$(DOCKER_COMPOSE) exec backend python scripts/test_quantum.py

quantum-benchmark: ## Run quantum algorithm benchmarks
	@echo "$(YELLOW)Running quantum benchmarks...$(NC)"
	$(DOCKER_COMPOSE) exec backend python scripts/quantum_benchmark.py

# =============================================================================
# CI/CD COMMANDS
# =============================================================================

ci-install: ## Install dependencies for CI
	@make install-backend
	@make install-frontend

ci-test: ## Run tests for CI
	@make test
	@make lint

ci-build: ## Build for CI
	@make build

ci-deploy: ## Deploy for CI
	@make deploy

# =============================================================================
# MONITORING AND OBSERVABILITY
# =============================================================================

monitoring: ## Start monitoring stack (Prometheus + Grafana)
	@echo "$(GREEN)Starting monitoring stack...$(NC)"
	$(DOCKER_COMPOSE) --profile monitoring up -d
	@echo "$(YELLOW)Prometheus: http://localhost:9090$(NC)"
	@echo "$(YELLOW)Grafana: http://localhost:3001 (admin/admin)$(NC)"

monitoring-stop: ## Stop monitoring stack
	$(DOCKER_COMPOSE) --profile monitoring down

# =============================================================================
# INFORMATION
# =============================================================================

info: ## Show project information
	@echo "$(GREEN)Project Information:$(NC)"
	@echo "Project Name: $(PROJECT_NAME)"
	@echo "Backend Directory: $(BACKEND_DIR)"
	@echo "Frontend Directory: $(FRONTEND_DIR)"
	@echo "Python Version: $(shell $(PYTHON) --version)"
	@echo "Node Version: $(shell $(NODE) --version)"
	@echo "NPM Version: $(shell $(NPM) --version)"
	@echo "Docker Compose Version: $(shell $(DOCKER_COMPOSE) --version)"

urls: ## Show application URLs
	@echo "$(GREEN)Application URLs:$(NC)"
	@echo "$(YELLOW)Frontend:     http://localhost:3000$(NC)"
	@echo "$(YELLOW)Backend API:  http://localhost:5000$(NC)"
	@echo "$(YELLOW)API Docs:     http://localhost:5000/docs$(NC)"
	@echo "$(YELLOW)Database:     postgresql://localhost:5432/supply_chain$(NC)"
	@echo "$(YELLOW)Redis:        redis://localhost:6379$(NC)"
