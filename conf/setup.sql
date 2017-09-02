\c proxy;
drop database postgres;
create database postgres;
\c postgres;
\i udt.sql
\i schema.sql
\i views.sql
INSERT INTO tipo_agregar VALUES ('Universidad');
INSERT INTO tipo_subdivision VALUES ('Province');
INSERT INTO part_ag (nom_part, ciudad, nom_subdivision, tipo_subdivision, pais, tipo_agregar) VALUES
  ('Concordia', 'Montréal', 'Québec', 'Province', 'Canada', 'Universidad');
INSERT INTO part_us (email, nom_usario, contrasena) VALUES 
  ('meza.aurelio@gmail.com', 'AureM', 'Password');
\i my_audit.sql
SELECT audit_table('participante_pista_son');
