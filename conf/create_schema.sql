DROP SCHEMA IF EXISTS poetica_sonora CASCADE;

DROP SCHEMA IF EXISTS audit CASCADE;

CREATE SCHEMA poetica_sonora;

--CREATE ROLE aurelio WITH NOSUPERUSER NOCREATEDB NOCREATEROLE LOGIN;

ALTER ROLE postgres SET search_path TO audit, public, poetica_sonora;
