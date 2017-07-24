#!/bin/bash/
# setup poetica_sonora database

psql -U davidlum -d davidlum -a -f poet_son_sch.pgsql

psql -U davidlum -d davidlum -a -f poet_son_dtypes.pgsql

psql -U davidlum -d davidlum -a -f poet_son_ddl.pgsql

psql -U davidlum -d davidlum -a -f audit.sql

psql -U davidlum -d davidlum -a -f poet_son_audit_tables.pgsql
