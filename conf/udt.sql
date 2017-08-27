
CREATE TYPE fecha AS (
  d date, 
  b boolean
);

CREATE OR REPLACE FUNCTION get_fecha(fecha) 
  RETURNS text AS $$
  BEGIN
    IF $1.b = false THEN
      RETURN EXTRACT(YEAR FROM $1.d);
    ELSE
      RETURN $1.d;
    END IF;
  END $$  
  LANGUAGE plpgsql
  IMMUTABLE
  RETURNS NULL ON NULL INPUT; 

