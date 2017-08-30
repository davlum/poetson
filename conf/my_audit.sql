CREATE OR REPLACE FUNCTION process_audit() RETURNS TRIGGER AS $body$
DECLARE 
    audit_table text;
BEGIN
    audit_table := 'audit.' || TG_TABLE_NAME || '_audit';
    IF (TG_OP = 'DELETE') THEN
      EXECUTE format('INSERT INTO %I SELECT $1.*, now(), DEFAULT, ''D''', audit_table) USING OLD;
      RETURN OLD;
    ELSE (TG_OP = 'UPDATE') THEN
      EXECUTE format('INSERT INTO %I SELECT $1.*, now(), DEFAULT, ''U''', audit_table) USING OLD;  
      RETURN NEW;
    END IF;
    RETURN NULL; -- result is ignored since this is an AFTER trigger
END;
$body$ 
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION gen_table(target_table regclass) RETURNS void AS $body$
BEGIN
    EXECUTE 'CREATE TABLE IF NOT EXISTS audit.' || quote_ident(target_table::TEXT) ||
    '_audit AS TABLE ' || quote_ident(target_table::TEXT);
    EXECUTE 'ALTER TABLE ' || quote_ident(target_table::TEXT) ||
      ' ADD COLUMN IF NOT EXISTS usario_id int NOT NULL REFERENCES usario';
    EXECUTE ' ALTER TABLE audit.' || quote_ident(target_table::TEXT) ||
      '_audit 
      ADD COLUMN IF NOT EXISTS usario_id int NOT NULL REFERENCES usario,
      ADD COLUMN IF NOT EXISTS valida_desda TIMESTAMP NOT NULL DEFAULT now(),
      ADD COLUMN IF NOT EXISTS valido_hasta TIMESTAMP,
      ADD COLUMN IF NOT EXISTS accion text NOT NULL
        CHECK (accion IN (''I'', ''D'', ''U'', ''T''))';
END;
$body$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION audit_table(target_table regclass) RETURNS void AS $body$
BEGIN
    CREATE SCHEMA IF NOT EXISTS audit;
    EXECUTE gen_table(target_table);
    EXECUTE format('CREATE TRIGGER %I
    AFTER UPDATE OR DELETE ON %I
      FOR EACH ROW EXECUTE PROCEDURE process_audit()', target_table || '_trig', target_table);
END;
$body$
LANGUAGE plpgsql
SET search_path=public,audit;


