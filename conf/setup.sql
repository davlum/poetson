\c proxy;
drop database postgres;
create database postgres;
ALTER DATABASE postgres SET datestyle TO "ISO, DMY";
\c postgres;
\i udt.sql
\i schema.sql
\i public_views.sql
--\i limbo_views.sql
\i insert.sql 
\i audit.sql
\i audit_tables.sql
INSERT INTO part_ag (nom_part, ciudad, nom_subdivision, tipo_subdivision, pais, tipo_agregar) VALUES
  ('Concordia', 'Montréal', 'Québec', 'Provincia', 'Canadá', 'Universidad');
INSERT INTO part_us (email, nom_usario, contrasena) VALUES 
  ('meza.aurelio@gmail.com', 'AureM', 'Password');
