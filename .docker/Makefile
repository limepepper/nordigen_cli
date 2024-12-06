# .PHONY: docker test

#docker:  # Ensure this matches "docker"
#	@if [ -n "$(filter $(MAKECMDGOALS),something)" ]; then \
#	  $(MAKE) -C .docker something; \
#	else \
#	  echo "Unknown docker subcommand: $(MAKECMDGOALS)"; \
#	  exit 1; \
#	fi

MAKEFILE_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
ROOT_DIR:=$(shell dirname $(MAKEFILE_DIR))

DOCKER_COMPOSE=docker compose

init: build run
	$(DOCKER_COMPOSE) exec web flask db init
	@echo "Init done, containers running"

build: stuff
	$(DOCKER_COMPOSE) build

#run:
#	@mkdir -p db
#	$(DOCKER_COMPOSE) up -d
#
#test:
#	$(DOCKER_COMPOSE) run -v $(PWD)/tests:/code/tests:ro web tox -e test

path:
	@echo $(ROOT_DIR)

stuff:
	@echo "stuff"
	@echo $(current_dir)
	pwd
	@cd $(ROOT_DIR)/../limepepper_utils; \
		poetry build;
	@cd $(ROOT_DIR)/../limepepper_utils; \
 		unzip -o -d dist ./dist/limepepper_utils-0.1.0-py3-none-any.whl

	@cp -r $(ROOT_DIR)/../limepepper_utils/dist/limepepper_utils-*.whl \
		$(ROOT_DIR)/../nordigen_cli/dist

	@cd $(ROOT_DIR)/../requests_debugger; \
		poetry build;
	@cd $(ROOT_DIR)/../nordigen_cli; \
 		unzip -o -d dist $(ROOT_DIR)/dist/nordigen_cli-*-py3-none-any.whl
	@cp -r $(ROOT_DIR)/../requests_debugger/dist/requests_debugger-*.whl \
		$(ROOT_DIR)/../nordigen_cli/dist
	@cd $(ROOT_DIR)/../nordigen_cli; \
		poetry build;
	@cp -r ~/git/api-client/dist/*.whl \
		$(ROOT_DIR)/../nordigen_cli/dist
