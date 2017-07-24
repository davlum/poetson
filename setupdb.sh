#!/bin/bash/
# setup poetica_sonora database

dropdb postgres

createdb -O postgres postgres

psql postgres -c 'set role postgres;' -c '\i poet_son_sch.pgsql' -c '\i
poet_son_dtypes.pgsql' -c '\i poet_son_ddl.pgsql' -c '\i audit.sql' -c '\i poet_son_audit_tables.pgsql'
