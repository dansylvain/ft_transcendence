# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: seblin <seblin@student.42.fr>              +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2025/01/29 13:35:00 by seblin            #+#    #+#              #
#    Updated: 2025/02/07 14:57:35 by seblin           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

all:
	-docker-compose up --build

prod: clean 
	-docker-compose -f docker-compose.yml up --build

clean:
	-docker stop $$(docker ps -qa)
	-docker rm $$(docker ps -qa)
# -docker rmi $$(docker images -qa)
	-docker volume rm $$(docker volume ls -q)
	-echo y | docker network rm $$(docker network ls -q)
	rm -rf staticfiles/*

re: clean all

# all:
# 	docker-compose up

# build:
# 	docker-compose build

# prod: clean 
# 	docker-compose -f docker-compose.yml up

# clean:
# 	-docker-compose down -v
# 	rm -rf staticfiles/*

# re: clean build all