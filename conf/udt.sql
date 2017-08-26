
CREATE TYPE fecha AS (f1 date, f2 boolean);

CREATE DOMAIN proper_email AS text CHECK (VALUE ~* '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$');
