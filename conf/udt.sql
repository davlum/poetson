CREATE TYPE tipo_fecha AS ENUM('FULL', 'MONTH', 'YEAR');

CREATE TYPE fecha AS (
  d date, 
  t tipo_fecha 
);

CREATE OR REPLACE FUNCTION get_fecha(fecha) RETURNS text AS $body$
BEGIN
    IF $1.t = 'YEAR' THEN
      RETURN EXTRACT(YEAR FROM $1.d);
    ELSIF $1.t = 'MONTH' THEN
      RETURN EXTRACT(MONTH FROM $1.d);
    ELSE
      RETURN $1.d;
    END IF;
END;
$body$
LANGUAGE plpgsql
IMMUTABLE
RETURNS NULL ON NULL INPUT; 

