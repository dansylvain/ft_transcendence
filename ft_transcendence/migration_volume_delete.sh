#! /bin/sh

# Make sure containers are stopped
docker compose stop

# Delete those fucking migrations
rm -rf ./databaseapi/databaseapi_app/migrations/

# Launch an Ubuntu container and delete the volume from within the container
docker run --rm -v ~/volumes_transcendence:/mnt ubuntu bash -c "rm -rf /mnt/postgres && echo 'Postgres volume deleted successfully'"