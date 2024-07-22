PYTHON_IMAGE ?= python:3.8-slim
IMAGE_NAME ?= satishsverma/telegram-bot

ciDeploy:  buildMultiArchAndPush

# Builds a new image targetting the host architecture
# See `buildMultiArch` and `buildMultiArchAndPush` for multi-arch
build:
	docker build --no-cache \
		--build-arg PYTHON_IMAGE=$(PYTHON_IMAGE) \
		-t $(IMAGE_NAME) .

# Builds targetting linux/amd64 and linux/arm64 using buildx
# It will store the result in cache
buildMultiArch:
	docker buildx build \
		--platform linux/amd64,linux/arm64 \
		--build-arg PYTHON_IMAGE=$(PYTHON_IMAGE) \
		-t $(IMAGE_NAME) .

# Builds targetting linux/amd64 and linux/arm64 using buildx
# And it pushes the images using `--push` flag
buildMultiArchAndPush:
	@echo "$(DOCKER_ACCESS_TOKEN)" | docker login --username "$(DOCKER_USERNAME)" --password-stdin docker.io
	docker buildx build \
		--platform linux/amd64,linux/arm64 \
		--build-arg PYTHON_IMAGE=$(PYTHON_IMAGE) \
		--push \
		-t $(IMAGE_NAME) .
	docker logout

push: env-DOCKER_USERNAME env-DOCKER_ACCESS_TOKEN
	@echo "$(DOCKER_ACCESS_TOKEN)" | docker login --username "$(DOCKER_USERNAME)" --password-stdin docker.io
	docker push $(IMAGE_NAME)
	docker logout

pull:
	docker pull $(IMAGE_NAME)

clean:
	docker compose -f docker-compose.yml down -v \
	&& docker rmi -f $(IMAGE_NAME)

run: clean
	docker compose -f docker-compose.yml up -d

logs:
	docker compose logs -f