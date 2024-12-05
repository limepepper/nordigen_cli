# .PHONY: docker test

#docker:  # Ensure this matches "docker"
#	@if [ -n "$(filter $(MAKECMDGOALS),something)" ]; then \
#	  $(MAKE) -C .docker something; \
#	else \
#	  echo "Unknown docker subcommand: $(MAKECMDGOALS)"; \
#	  exit 1; \
#	fi

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

stuff:
	@echo "stuff"
	pwd
	@cd ../limepepper_utils; \
		poetry build;
	@cd ../limepepper_utils; \
 		unzip -o -d dist ./dist/limepepper_utils-0.1.0-py3-none-any.whl
	@cp -r ../limepepper_utils/dist/limepepper_utils-*.whl \
		../nordigen_cli/dist
	@cd ../requests_debugger; \
		poetry build;
	@cd ../nordigen_cli; \
 		unzip -o -d dist ./dist/nordigen_cli-*-py3-none-any.whl
	@cp -r ../requests_debugger/dist/requests_debugger-*.whl \
		../nordigen_cli/dist
	@cd ../nordigen_cli; \
		poetry build;
	@cp -r /home/tomhodder/git/api-client/dist/*.whl \
		../nordigen_cli/dist
