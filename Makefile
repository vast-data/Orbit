.PHONY: trino-up trino-wait trino-down test test-cov lint

TRINO_IMAGE ?= trinodb/trino:latest

trino-up:
	docker run -d --name trino -p 8080:8080 $(TRINO_IMAGE)

trino-wait:
	@echo "Waiting for Trino..."
	@for i in $$(seq 1 30); do \
	  if curl -fsS http://localhost:8080/v1/info | grep -q '"starting":false'; then \
	    echo "Trino ready"; exit 0; fi; \
	  sleep 5; done; \
	echo "Trino not ready"; exit 1

trino-down:
	-docker rm -f trino

test:
	pytest -v

test-cov:
	pytest --cov=vastorbit --cov-report=term-missing --cov-report=xml
