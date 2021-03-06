
-- FK for participante
CREATE OR REPLACE FUNCTION participante_insert() RETURNS TRIGGER AS $$
  DECLARE child_id int;
  BEGIN
    INSERT INTO public.participante DEFAULT VALUES RETURNING part_id INTO child_id;
    NEW.part_id := child_id;
    RETURN NEW;
  END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER persona_insert
  BEFORE INSERT ON public.persona
  FOR EACH ROW
  EXECUTE PROCEDURE participante_insert();

CREATE TRIGGER grupo_insert
  BEFORE INSERT ON public.grupo
  FOR EACH ROW
  EXECUTE PROCEDURE participante_insert();

CREATE OR REPLACE FUNCTION process_audit() RETURNS TRIGGER AS $body$
DECLARE 
    audit_table text;
BEGIN
    audit_table := TG_TABLE_NAME || '_audit';
    IF (TG_OP = 'DELETE') THEN
      EXECUTE format('INSERT INTO audit.%I SELECT $1.*, now(), ''D''', audit_table) USING OLD;
      RETURN OLD;
    ELSIF (TG_OP = 'INSERT') THEN
      EXECUTE format('INSERT INTO audit.%I SELECT $1.*, now(), ''I''', audit_table) USING NEW;
      RETURN NEW;
    ELSIF (TG_OP = 'UPDATE') THEN
      EXECUTE format('INSERT INTO audit.%I SELECT $1.*, now(), ''U''', audit_table) USING NEW;
      RETURN NEW;
    END IF;
    RETURN NULL; -- result is ignored since this is an AFTER trigger
END;
$body$ 
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION gen_table(target_table regclass) RETURNS void AS $body$
DECLARE
  pk_name text; -- key of the
BEGIN

  EXECUTE format('ALTER TABLE %I ' ||
                 'ADD COLUMN IF NOT EXISTS cargador_id int NOT NULL ' ||
                 'REFERENCES public.participante ON DELETE RESTRICT, '
                 'ADD COLUMN IF NOT EXISTS mod_id int REFERENCES usuario, ' ||
                 'ADD COLUMN IF NOT EXISTS estado text NOT NULL DEFAULT ''PENDIENTE''' ||
                 'CHECK (estado IN (''DEPOSITAR'', ''RECHAZADO'', ''PENDIENTE'', ''PUBLICADO''))'
                  , target_table);
  EXECUTE format('CREATE TABLE IF NOT EXISTS audit.%I (LIKE %I INCLUDING DEFAULTS)'
                  , target_table || '_audit', target_table);
  EXECUTE format('ALTER TABLE audit.%I ' ||
                 'ADD COLUMN IF NOT EXISTS fecha_accion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(), ' ||
                 'ADD COLUMN IF NOT EXISTS accion text NOT NULL ' ||
                 'CHECK (accion IN (''I'', ''D'', ''U'', ''T''))', target_table || '_audit');
END;
$body$
LANGUAGE plpgsql;

COMMENT ON FUNCTION gen_table(regclass) IS $body$
Take note that the audited tables are only created including defaults. This is
order to keep the sequence values from the original tables. Other constraints are not
copied as the tables audited are not a complete copy of the database, and therefore
some foreign key constraints may be unenforceable. Worth considering also INCLUDING INDEXES
for the audit.table, but may take up too much space.
$body$;

CREATE OR REPLACE FUNCTION audit_table(target_table regclass) RETURNS VOID AS $body$
BEGIN
    CREATE SCHEMA IF NOT EXISTS audit;
    EXECUTE gen_table(target_table);
    EXECUTE format('CREATE TRIGGER %I
    AFTER UPDATE OR DELETE OR INSERT ON %I
      FOR EACH ROW EXECUTE PROCEDURE process_audit()', target_table || '_audit_trig', target_table);
END;
$body$
LANGUAGE plpgsql;

COMMENT ON FUNCTION audit_table(regclass) IS $body$
This function creates two tables based off of the given table name.
One table resides in the limbo schema. This data awaits approval to be
inserted into the public schema. Once in the public schema the data is audited
by a trigger which inserts into a table in the audit schema.
The standard search_path = public, and the data residing in the alternate schemas will
not be viewable to the majority of users.
$body$;

CREATE OR REPLACE FUNCTION usuario_id_insert() RETURNS trigger AS $body$
BEGIN
  IF NEW.cargador_id IS NULL THEN
     NEW.cargador_id := NEW.part_id;
  END IF;
  RETURN NEW;
END;
$body$
LANGUAGE plpgsql;

CREATE TRIGGER usuario_id_trig
  BEFORE INSERT ON public.persona
  FOR EACH ROW
  EXECUTE PROCEDURE usuario_id_insert();

CREATE TRIGGER usuario_id_trig
  BEFORE INSERT ON public.grupo
  FOR EACH ROW
  EXECUTE PROCEDURE usuario_id_insert();

/*
CREATE OR REPLACE FUNCTION publish(pk_id int, usr_id int, target_table REGCLASS) RETURNS VOID AS $body$
DECLARE
  pk_name text; -- primary key of the given table
BEGIN
  EXECUTE format('SELECT a.attname
              FROM pg_index i
              JOIN pg_attribute a
              ON a.attrelid = i.indrelid
                AND a.attnum = ANY(i.indkey)
                WHERE i.indrelid = ''%I''::regclass
                AND i.indisprimary', target_table) INTO pk_name;

  EXECUTE format('CREATE TEMP TABLE temp_table (like limbo.%I)', target_table || '_limbo');
  EXECUTE format('UPDATE limbo.%I SET mod_id = $1 WHERE %I = $2'
        , target_table || '_limbo', pk_name) USING usr_id, pk_id;
  EXECUTE format('INSERT INTO temp_table SELECT * FROM limbo.%I WHERE %I = $1'
            , target_table || '_limbo', pk_name) USING pk_id;
  ALTER TABLE temp_table
    DROP COLUMN fecha_sumado,
    DROP COLUMN cargador_id,
    DROP COLUMN estado;
  EXECUTE format('INSERT INTO %I SELECT * FROM temp_table', target_table);
  DROP TABLE temp_table;
  EXECUTE format('UPDATE limbo.%I SET estado = ''Publicado'' WHERE %I = $1'
        , target_table || '_limbo', pk_name) USING pk_id;
END;
$body$
LANGUAGE plpgsql;

COMMENT ON FUNCTION publish(int, int, regclass) IS $body$
Publish an a record from the limbo schema into the public schema.
This id of record and id of the mod performing the action is given
along with the name of the table in the public schema.
The article remains in the limbo schema, but with status 'Publicado'.
$body$;
*/
