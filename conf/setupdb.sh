#!/bin/bash/
# setup poetica_sonora database

dropdb postgres

createdb -O postgres postgres

createuser -s -l postgres

psql postgres -c 'set role postgres;' -f 'create_schema.sql' -f 'udt.sql' -f 'schema.sql' -f 'audit_script.sql' -f 'audit_tables.sql' -c 'set search_path = audit, public' -f 'insert.sql'
