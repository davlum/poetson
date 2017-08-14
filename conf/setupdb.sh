#!/bin/bash/
# setup poetica_sonora database

dropdb postgres

createdb -O postgres -E UTF8 -l es_ES.UTF-8 -e postgres

#createuser -s -l postgres

psql postgres -c 'set role postgres;'  -f 'udt.sql' -f 'schema.sql' -f 'audit_script.sql' -f 'audit_tables.sql' -f 'insert.sql'

