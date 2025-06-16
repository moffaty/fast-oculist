include .env.docker
export $(shell sed 's/=.*//' .env.docker)

.PHONY: run lint test

shell:
	poetry shell
run:
	poetry run python app/main.py
docker-start:
	make docker-build; make docker-run
# Команда для сборки Docker-образа
docker-build:
	docker build -t $(IMAGE_NAME) .
# Команда для запуска контейнера
docker-run:
	docker run --rm -d -p $(PORT):$(PORT) --name $(CONTAINER_NAME) $(IMAGE_NAME)
# Команда для запуска контейнера в интерактивном режиме (с терминалом)
docker-run-it:
	docker run --rm -it -p $(PORT):$(PORT) --name $(CONTAINER_NAME) $(IMAGE_NAME) /bin/bash
# Команда для остановки контейнера
docker-stop:
	docker stop $(CONTAINER_NAME)
# Команда для удаления Docker-образа
docker-clean:
	docker rmi $(IMAGE_NAME)
# Команда для просмотра логов контейнера
docker-logs:
	docker logs -f $(CONTAINER_NAME)
# Команда для запуска контейнера с пробросом текущей директории (для разработки)
docker-dev:
	docker run --rm -it -v $(PWD):/app -p $(PORT):$(PORT) --name $(CONTAINER_NAME) $(IMAGE_NAME) /bin/bash
setup-tileserver:
	docker volume create osm-data; docker run  -v $PWD/zambia-latest.osm.pbf:/data/region.osm.pbf  -v osm-data:/data/database/  overv/openstreetmap-tile-server  import
delete-tileserver:
	docker ps -a | grep overv | awk '{print $1}' | xargs -r docker stop && docker ps -a | grep overv | awk '{print $1}' | xargs -r docker rm
download-map:
	wget https://download.geofabrik.de/russia-latest.osm.pbf
lint:
	poetry run black .
test:
	PYTHONPATH=. poetry run pytest
run-webrtc:
	GO111MODULE=on go run RTSPtoWebRTC/*.go