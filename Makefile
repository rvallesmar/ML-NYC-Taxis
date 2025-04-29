.PHONY: setup run stop clean test format populate

setup:
	docker network create shared_network || true
	cp .env.original .env

populate:
	cd api && cp .env.original .env
	docker-compose up --build -d 

run: 
	docker-compose up --build -d

stop:
	docker-compose down

clean:
	docker-compose down -v
	rm -rf db_data/*
	rm -rf uploads/*
	rm -rf model/models/*

test:
	cd api && docker build -t fastapi_test --progress=plain --target test .
	cd model && docker build -t model_test --progress=plain --target test .
	cd ui && docker build -t ui_test --progress=plain --target test .
	python tests/test_integration.py

format:
	isort --profile=black . && black --line-length 88 . 