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
INSERT INTO part_pers (nom_part, nom_segundo, email, persona_id, agregar_id, titulo, nom_usario, contrasena, tipo) VALUES 
  ('Aurelio', 'Meza', 'meza.aurelio@gmail.com', 1, 1, 'Coordinador', 'AureM', 'Password', 'ADMIN');
