\c proxy;
drop database postgres;
create database postgres;
ALTER DATABASE postgres SET datestyle TO "ISO, DMY";
\c postgres;
\i udt.sql
\i schema.sql
\i audit.sql
\i audit_tables.sql
\i views.sql
\i insert.sql


