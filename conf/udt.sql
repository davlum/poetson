

CREATE OR REPLACE FUNCTION strip(text) RETURNS text AS $body$
BEGIN
    IF $1 IS NULL THEN
      RETURN NULL;
    END IF;
    RETURN NULLIF(TRIM($1), '');
END;
$body$
LANGUAGE plpgsql
RETURNS NULL ON NULL INPUT;

COMMENT ON FUNCTION strip(text) IS 'function that strips whitespace and returns null if empty string or null input';

CREATE TYPE tipo_fecha AS ENUM('FULL', 'MONTH', 'YEAR');

CREATE TYPE fecha AS (
  d date, 
  t tipo_fecha 
);

CREATE OR REPLACE FUNCTION set_fecha(fecha) RETURNS fecha AS $body$
BEGIN
    IF ($1.d IS NULL) THEN
      RETURN ((NULL, NULL));
    END IF;
    RETURN $1;
END;
$body$
LANGUAGE plpgsql
RETURNS NULL ON NULL INPUT;


CREATE OR REPLACE FUNCTION get_fecha(fecha) RETURNS text AS $body$
BEGIN
    IF $1.t = 'YEAR' THEN
      RETURN to_char($1.d, 'YYYY');
    ELSIF $1.t = 'MONTH' THEN
      RETURN to_char($1.d, 'MM/YYYY');
    ELSE
      RETURN to_char($1.d, 'DD/MM/YYYY');
    END IF;
END;
$body$
LANGUAGE plpgsql
IMMUTABLE
RETURNS NULL ON NULL INPUT; 

