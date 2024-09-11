install: build start ## Spin-up the project with minimal data

build: ## Build docker containers
	$(DOCKER_COMP) build
	@echo ">>> Base build done!"

log:
	docker logs backend_app
	@echo "=> webapp's logs"

shell: ## Run bash inside dxloo container
	${APP} bash

rebuild: ## Build docker containers without cache
	$(DOCKER_COMP) build --no-cache
	@echo ">>> Rebuild done!"

start: ## Start all services
	${DOCKER_COMP} up -d
	@echo ">>> Containers started!"

stop: ## Stop all services
	${DOCKER_COMP} stop
	@echo ">>> Containers stopped!"

destroy: ## Stop and remove all containers, networks, images, and volumes
	${DOCKER_COMP} down --volumes --remove-orphans
	@echo ">>> Containers destroyed!"

create_roles: ## Create all roles
	${APP} python manage.py create_roles
	@echo ">>> Roles done!"

collectstatic: ## Collectstatic
	${APP} python manage.py collectstatic --noinput
	${APP} chown -R $(CURRENT_UID):$(CURRENT_GID) staticfiles
	@echo ">>> Controller done!"

makemigrations: ## Make migrations
	${APP} python manage.py makemigrations
	@echo ">>> Controller done!"

migrate: ## Create new migration
	${APP} python manage.py migrate
	@echo ">>> Migration done!"

celery: ## Run celery server
	${APP} celery -A config worker --loglevel=INFO
	@echo ">>> Celery started"

lint:  ## Python lint
	flake8 src
	@echo ">>> Lint done"
