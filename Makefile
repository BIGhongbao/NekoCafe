COMPOSE ?= docker compose
TAG ?= 0.1.0
REGISTRY ?= ghcr.io/your-org/nekocafe

.PHONY: test build up down logs scan helm-lint rollback

test:
	python -m pytest services/reservation/tests -q
	python -m pytest services/member/tests -q

build:
	docker build -t $(REGISTRY)/reservation-service:$(TAG) services/reservation
	docker build -t $(REGISTRY)/member-service:$(TAG) services/member

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down -v

logs:
	$(COMPOSE) logs -f --tail=100

scan:
	trivy image --severity HIGH,CRITICAL --exit-code 1 $(REGISTRY)/reservation-service:$(TAG)
	trivy image --severity HIGH,CRITICAL --exit-code 1 $(REGISTRY)/member-service:$(TAG)

helm-lint:
	helm lint infra/helm/nekocafe -f infra/helm/nekocafe/values-dev.yaml
	helm lint infra/helm/nekocafe -f infra/helm/nekocafe/values-staging.yaml
	helm lint infra/helm/nekocafe -f infra/helm/nekocafe/values-prod.yaml

rollback:
	sh scripts/rollback.sh staging nekocafe
