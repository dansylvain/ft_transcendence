## HOW TO DELETE VOLUME

In a `non-root` env, we can't delete the bind-mount volume in `~ (home)` because `docker` has the perms.

Under the hood, this is the process that manages the volumes which has the auth.

## STEP 1 : MAKE SURE THAT THE PROJECTS IS RUNNING

make re

# STEP 2 : ENTER IN THE POSTGRES DOCKER RUNNING :

docker exec -it ctn_database bash

# STEP 3 : WHILE IN THE CONTAINER, CHANGE OWNERSHIP :

chown -R 1000:1000 /var/lib/postgresql/data

Change ownership to the first non root user in Unix Systems

# STEP 4 : STOP CONTAINERS

# STEP 5 : DELETE THE VOLUME