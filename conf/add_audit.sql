CREATE OR REPLACE FUNCTION audit_populated_table(target_table regclass, id int, est text) RETURNS void AS $body$
BEGIN
  EXECUTE format('CREATE TEMP TABLE IF NOT EXISTS %I AS TABLE public.%I'
                  , target_table || '_temp', target_table);
  EXECUTE format('ALTER TABLE %I ADD COLUMN cargador_id int, ' ||
                 'ADD COLUMN mod_id int,' ||
                 'ADD COLUMN estado text', target_table || '_temp');
  EXECUTE format('UPDATE %I SET cargador_id = %s, mod_id = %s, estado = %L WHERE TRUE',
                  target_table || '_temp', id, id, est);
  EXECUTE format('DELETE FROM %I WHERE TRUE', target_table);              
  EXECUTE format('SELECT audit_table(%L)', target_table);
  EXECUTE format('INSERT INTO %I SELECT * FROM %I', target_table, target_table || '_temp');
  EXECUTE format('DROP TABLE %I',target_table || '_temp');
END;
$body$
LANGUAGE plpgsql
