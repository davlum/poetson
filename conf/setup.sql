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
\i populate/lookup.sql
INSERT INTO public.us_pers (nom_usuario, email, contrasena) VALUES ('AurMez', 'meza.aurelio@gmail.com', 'password');
\i insert.sql
INSERT INTO public.lugar DEFAULT VALUES;
UPDATE public.persona SET lugar_id=216 WHERE part_id=1;


