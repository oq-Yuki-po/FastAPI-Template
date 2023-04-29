POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=postgres
env
ls -l

/usr/local/bin/schemaspy \
-u ${POSTGRES_USER} \
-host ${POSTGRES_SERVER} \
-port ${POSTGRES_PORT} \
-db ${POSTGRES_DB} \
-p ${POSTGRES_PASSWORD} \
-s public \
-t pgsql11 \
-connprops useSSL\\\\=false
