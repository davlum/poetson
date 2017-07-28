#!/bin/bash/
# setup poetica_sonora database

dropdb postgres

createuser -s -l postgres

createdb -O postgres postgres

psql postgres -c 'set role postgres;' -c '\i create_schema.sql' -c '\i
udt.sql' -c '\i schema.sql' -c '\i audit_script.sql' -c '\i
audit_tables.sql' -c '\i populate_tema.sql' -c '\i populate_genero_artista.sql'
