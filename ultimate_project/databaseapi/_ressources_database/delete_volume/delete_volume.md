## HOW TO DELETE VOLUME

In a `non-root` env, we can't delete the bind-mount volume in `~ (home)` because `docker` has the perms.

Under the hood, this is the process that manages the volumes which has the auth.

## STEP 1 : MAKE SURE THAT THE PROJECT IS STOPPED

# STEP 2 : BUILD A UBUNTU CONTAINER UPON THE EXISTING VOLUME

docker run --rm -it -v ~/volumes_transcendence:/mnt ubuntu bash

This will take control of the volume through another container

# STEP 3 : FROM WITHIN THE CONTAINER, DELETE THE VOLUME

rm -rf /mnt/postgres

# STEP 4 : DELETE CONTAINER FROM THE HOST MACHINE

docker system prune --all --force