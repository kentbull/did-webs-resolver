VERSION=0.2.1

define DOCKER_WARNING
In order to use the multi-platform build enable the containerd image store
The containerd image store is not enabled by default.
To enable the feature for Docker Desktop:
	Navigate to Settings in Docker Desktop.
	In the General tab, check Use containerd for pulling and storing images.
	Select Apply and Restart."
endef

build-webs: .warn
	@docker build \
		--platform=linux/amd64,linux/arm64 \
		-f images/webs.dockerfile \
		-t gleif/webs:$(VERSION) .

publish-webs:
	@docker push gleif/webs:$(VERSION)

tag-webs-latest:
	@$(MAKE) tag IMAGE_NAME=gleif/webs VERSION=$(VERSION)

tag-latest: tag-webs-latest tag-did-webs-service-latest tag-did-webs-resolver-service-latest

build-did-webs-service: .warn
	@docker build \
		--platform=linux/amd64,linux/arm64 \
		-f images/did-webs-service.dockerfile \
		-t gleif/did-webs-service:latest \
		-t gleif/did-webs-service:$(VERSION) .

publish-did-webs-service:
	@docker push gleif/did-webs-service:$(VERSION)

tag-did-webs-service-latest:
	@$(MAKE) tag IMAGE_NAME=gleif/did-webs-service VERSION=$(VERSION)

build-did-webs-resolver-service: .warn
	@docker build \
		--platform=linux/amd64,linux/arm64 \
		-f images/did-webs-resolver-service.dockerfile \
		-t gleif/did-webs-resolver-service:latest \
		-t gleif/did-webs-resolver-service:$(VERSION) .

publish-did-webs-resolver-service:
	@docker push gleif/did-webs-resolver-service:$(VERSION)

tag-did-webs-resolver-service-latest:
	@$(MAKE) tag IMAGE_NAME=gleif/did-webs-resolver-service VERSION=$(VERSION)

run-agent:
	@docker run -p 5921:5921 -p 5923:5923 --name agent gleif/did-webs-resolver:$(VERSION)

publish-latest:
	@docker push gleif/webs:latest
	@docker push gleif/did-webs-service:latest
	@docker push gleif/did-webs-resolver-service:latest

.warn:
	@echo -e ${RED}"$$DOCKER_WARNING"${NO_COLOUR}

tag:
	@IMAGE_ID=$$(docker images --format "{{.ID}}" $(IMAGE_NAME):$(VERSION) | head -n 1); \
	if [ -z "$$IMAGE_ID" ]; then \
		echo "Error: No local image found for '$(IMAGE_NAME)'"; \
		exit 1; \
	fi; \
	docker tag $$IMAGE_ID $(IMAGE_NAME):latest; \
	echo "Successfully tagged $(IMAGE_NAME) ($$IMAGE_ID) as $(IMAGE_NAME):latest"

fmt:
	@uv tool run ruff check --select I --fix
	@uv tool run ruff format

# used by ci
check:
	uv tool run ruff check --select I
	uv tool run ruff format --check

RED="\033[0;31m"
NO_COLOUR="\033[0m"
export DOCKER_WARNING