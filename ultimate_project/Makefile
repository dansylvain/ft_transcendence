# all : calls all the compose
all: create_volume
	bash -c "source ./get_ip.sh"
	-docker compose -f docker-compose.yaml -f docker-compose.override.yaml up --build
# all : calls only the classic compose
prod: clean	create_volume 
	-docker compose -f docker-compose.yaml up --build

clean:
	-test -n "$$(docker ps -qa)" && docker stop $$(docker ps -qa)
	-test -n "$$(docker ps -qa)" && docker rm $$(docker ps -qa)
	-test -n "$$(docker volume ls -q)" && docker volume rm $$(docker volume ls -q)    
	-echo y | docker network rm $$(docker network ls --filter "type=custom" -q)
	docker image prune -f

	rm -rf staticfiles/*

re: clean all

# Prune does removes volumes, including the DB.
prune:
	docker system prune --all --volumes --force

create_volume:
	@echo "\n\033[1;33m***| Creating PostgreSQL Volume |***\033[0m\n"
	@mkdir -p ~/volumes_transcendence/postgres
	@echo "\n\033[1;32m***| PostgreSQL Volume Created |***\033[0m\n"

# Using this rule actually deletes the DB. Run it at your own risks.
delete_volume:
	@echo "\n\033[1;33m***| Deleting MIGRATIONS and VOLUMES |***\033[0m\n"
	@bash migration_volume_delete.sh
	@echo "\n\033[1;32m***| MIGRATIONS and VOLUMES deleted |***\033[0m\n"

rebuild: delete_volume clean prune all


.PHONY: all prod clean re create_volume delete_volume prune rebuild