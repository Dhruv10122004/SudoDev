test:
	python tests/test.py

run:
	python -m uvicorn sudodev.server.main:app --reload --host 0.0.0.0 --port 8000

clean:
	git clean -Xdf
	
docker-up:
	docker-compose up

docker-build:
	docker-compose up --build

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up