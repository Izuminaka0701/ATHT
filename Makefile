COMPOSE := compose/docker-compose.yml
COMPOSE_DIR := compose

# Auto-detect python command (Windows: python, Linux/Mac: python3)
ifeq ($(OS),Windows_NT)
    PYTHON := python
    PIP := pip
else
    PYTHON := python3
    PIP := pip3
endif

.PHONY: preflight up attack defend verify export-evidence down pin-digests clean

preflight:
	@echo "=== Preflight ==="
	@command -v docker >/dev/null 2>&1 || (echo "ERROR: docker not found" && exit 1)
	@docker compose version >/dev/null 2>&1 || (echo "ERROR: docker compose not found" && exit 1)
	@$(PYTHON) --version
	@$(PIP) install -q -r tests/requirements.txt
	@echo "Preflight OK"

up: pin-digests
	docker compose -f $(COMPOSE) build
	docker compose -f $(COMPOSE) up -d
	@echo "Waiting for services..."
	@sleep 15
	@docker compose -f $(COMPOSE) ps

attack:
	@$(PYTHON) scripts/attack.py

defend:
	@$(PYTHON) scripts/defend.py

verify: export-evidence
	@echo "=== Running pytest ==="
	@$(PYTHON) -m pytest tests/ -v --tb=short

export-evidence:
	@$(PYTHON) -c "import os; os.makedirs('evidence', exist_ok=True)"
	@$(PYTHON) scripts/generate_flow_diagram.py
	@$(PYTHON) scripts/generate_connectivity_matrix.py
	@$(PYTHON) scripts/export_config_evidence.py
	@docker compose -f $(COMPOSE) config > evidence/compose-resolved.yml 2>/dev/null || true
	@cp config/policy/default-deny.yaml evidence/policy-default-deny.yaml
	@$(PYTHON) scripts/generate_manifest.py

down:
	docker compose -f $(COMPOSE) down -v --remove-orphans

pin-digests:
	@$(PYTHON) scripts/pin_digests.py

clean: down
	rm -rf evidence/*.mmd evidence/*.json evidence/*.yml evidence/MANIFEST.txt
