PROJECT_NAME=??
ENV?=staging
PY_MODULE=$(PROJECT_NAME)

PUSH_REGISTRY=ART_LOC
PULL_REGISTRY=ART_LOC
SOURCE_DIR=var/sources/
DAG_DIR=var/dag_files/

MODULE?=$(PROJECT_NAME)

BUILDER_VERSION=$(shell ./docker/builder-version.sh)
DOCKER_VERSION=$(shell ./docker/$(MODULE)-version.sh)
DOCKERFILE=Dockerfile-$(MODULE)

DOCKER_TAG=$(PROJECT_NAME):$(DOCKER_VERSION)
DOCKER_WORKDIR=/home/$(PROJECT_NAME)/$(shell pwd | xargs basename)
BUILDER_MAKE=$(MAKE) DOCKER_VERSION=$(BUILDER_VERSION)

default: help

help:
	@echo 'Usage: make [target] ...'
	@echo
	@echo 'Targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	| awk 'BEGIN {FS = ":.*?## "}; {printf "%-16s %s\n", $$1, $$2}'

#----------- SETUP_COMMANDS------------------------------------------------------------
rename-dirs: ##rename the directory's to the correct naem
	mv main $(PROJECT_NAME)
#----------- DOCKER ------------------------------------------------------------
builder-ver: ##Get the builder version
	@echo $(BUILDER_VERSION)

builder-ex: ## Buildception: builds the builder docker image
		DOCKERFILE='Dockerfile-builder' $(BUILDER_MAKE) docker \
		&& $(BUILDER_MAKE) push


builder: ## Buildception: builds the builder docker image
	@$(BUILDER_MAKE) pull || ( \
		DOCKERFILE='Dockerfile-builder' $(BUILDER_MAKE) docker \
		&& $(BUILDER_MAKE) push \
		)

docker-ver: ## Get the docker version
	@echo $(DOCKER_VERSION)

docker: ### Build the docker image
	docker build \
	  -t $(PUSH_REGISTRY)/$(DOCKER_TAG) \
	  -t $(PULL_REGISTRY)/$(DOCKER_TAG) \
	  -t $(DOCKER_TAG) \
	  --build-arg BUILDER_VERSION=$(BUILDER_VERSION) \
	  -f docker/$(DOCKERFILE) .

push: ## Push the docker image
	docker push $(PUSH_REGISTRY)/$(DOCKER_TAG)

pull: ## Pull the docker image
	docker pull $(PULL_REGISTRY)/$(DOCKER_TAG)
	docker tag $(PULL_REGISTRY)/$(DOCKER_TAG) $(DOCKER_TAG)
	docker tag $(PULL_REGISTRY)/$(DOCKER_TAG) $(PUSH_REGISTRY)/$(DOCKER_TAG)

#---- Run -----
clean-dir:
	@rm -rf ${SOURCE_DIR}
	@rm -rf ${DAG_DIR}
	@mkdir -p ${SOURCE_DIR}

#----------- TEST --------------------------------------------------------------
test: ## Lint and unit test python code
	@$(PRE_ACTIVATE) $(MAKE) -j4 --no-print-directory \
	  test-mypy \
	  test-black \
	  test-pylint \
	  test-unit \
	  test-isort

test-black:
	black -l 80 $(PY_MODULE) --check --exclude version.py

test-mypy:
	mypy $(PY_MODULE)

test-pylint:
	pylint -f parseable --rcfile=setup.cfg -j 4 ${PY_MODULE} test

test-unit:
	@rm -f var/.coverage var/.coverage.*
	@mkdir -p var
	pytest test -m "not integration" -rf -q --cov $(PY_MODULE) \
	  --cov-branch --cov-report term $(PYTESTFLAGS) \
	  --ignore=test/it

test-integration:
	pytest test/it -vvv -s

test-isort:
	isort -l80 -m3 -tc -rc -c $(PY_MODULE)

test-docker: ## Run test within docker
	docker run \
	  -v $(shell pwd):$(DOCKER_WORKDIR) \
	  -w $(DOCKER_WORKDIR) \
	  $(PULL_REGISTRY)/$(PROJECT_NAME):$(BUILDER_VERSION) \
	  make test

#----------- DEV ---------------------------------------------------------------
black: ## Format all the python code
	black -l 80 $(PY_MODULE)

black-docker: ## Run black with docker
	docker run \
	  -u 10000:$(shell id -u) \
	  -v $(shell pwd):$(DOCKER_WORKDIR) \
	  -w $(DOCKER_WORKDIR) \
	  $(PULL_REGISTRY)/$(PROJECT_NAME):$(BUILDER_VERSION) \
	  make black

isort: ## Sort imports in the python module
	isort -l80 -m3 -tc -rc $(PY_MODULE)

isort-docker: ## Sort imports with docker
	docker run \
	  -u 10000:$(shell id -u) \
	  -v $(shell pwd):$(DOCKER_WORKDIR) \
	  -w $(DOCKER_WORKDIR) \
	  $(PULL_REGISTRY)/$(PROJECT_NAME):$(BUILDER_VERSION) \
	  make isort

install-deps: ## Install dependencies via pipenv
	pipenv install --dev
	pipenv run pip install -e .

.PHONY: help docker-ver docker build push pull test pull-sources test-black \
  test-mypy test-pylint test-unit test-docker black black-docker install-deps
