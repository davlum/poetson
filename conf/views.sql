CREATE OR REPLACE VIEW part_us AS
  SELECT part.part_id
       , part.nom_part
       , part.lugar_id
       , part.fecha_comienzo
       , part.fecha_finale
       , part.sitio_web
       , part.direccion
       , part.telefono
       , part.email
       , part.coment_participante
       , u.part_id part_us_id
       , u.nom_usario
       , u.contrasena
       , u.permiso
       , u.confirmado
       , u.fecha_confirmado
      FROM public.participante part
      JOIN public.usario u
        ON u.part_id = part.part_id;

CREATE OR REPLACE FUNCTION us_insert() RETURNS TRIGGER AS $body$
DECLARE
  id int;
BEGIN
  INSERT INTO participante (nom_part
                          , sitio_web
                          , direccion
                          , lugar_id
                          , telefono
                          , email
                          , fecha_comienzo
                          , fecha_finale
                          , coment_participante)
                          VALUES (NEW.nom_part
                                , NEW.sitio_web
                                , NEW.direccion
                                , NEW.lugar_id
                                , NEW.telefono
                                , NEW.email
                                , NEW.fecha_comienzo
                                , NEW.fecha_finale
                                , NEW.coment_participante) 
                                RETURNING part_id INTO id;
 INSERT INTO usario ( part_id
                    , nom_usario
                    , contrasena
                    , permiso
                    , confirmado
                    , fecha_confirmado)
                  VALUES (id
                        , NEW.nom_usario
                        , NEW.contrasena
                        , DEFAULT
                        , DEFAULT
                        , NEW.fecha_confirmado);
  RETURN NULL;
END;
$body$
LANGUAGE plpgsql;
 
CREATE TRIGGER us_trigger
  INSTEAD OF INSERT ON part_us
  FOR EACH ROW
  EXECUTE PROCEDURE us_insert();

CREATE OR REPLACE VIEW part_pers AS
  SELECT part.part_id
       , part.nom_part
       , pers.nom_segundo
       , pers.seudonimo
       , pers.nom_paterno
       , pers.nom_materno
       , part.lugar_id lugar_nac
       , pers.lugar_muer
       , part.fecha_comienzo pers_comienzo
       , part.fecha_finale pers_finale
       , part.sitio_web
       , part.direccion
       , part.telefono
       , part.email p_email
       , gp.genero_id
       , gp.nom_genero
       , part.coment_participante
       , pa.persona_id
       , pa.agregar_id
       , pa.fecha_comienzo tit_comienzo
       , pa.fecha_finale tit_finale
       , pa.titulo
       , u.part_id us_id
       , u.nom_usario
       , u.contrasena
       , u.permiso
      FROM public.participante part
      JOIN public.persona pers
        ON pers.part_id = part.part_id
      LEFT JOIN public.genero_persona gp
        ON gp.genero_id = pers.genero_id
      LEFT JOIN public.persona_agregar pa
        ON pa.persona_id=pers.part_id
      LEFT JOIN public.usario u
        ON u.part_id = part.part_id;

CREATE OR REPLACE FUNCTION pers_insert() RETURNS TRIGGER AS $body$
DECLARE
  id int;
BEGIN
  INSERT INTO participante (nom_part
                          , sitio_web
                          , direccion
                          , lugar_id
                          , telefono
                          , email
                          , fecha_comienzo
                          , fecha_finale
                          , coment_participante)
                          VALUES (NEW.nom_part
                                , NEW.sitio_web
                                , NEW.direccion
                                , NEW.lugar_nac
                                , NEW.telefono
                                , NEW.p_email
                                , NEW.pers_comienzo
                                , NEW.pers_finale
                                , NEW.coment_participante) 
                                RETURNING part_id INTO id;
  INSERT INTO persona(part_id
                    , nom_segundo
                    , nom_paterno
                    , nom_materno
                    , seudonimo
                    , lugar_muer
                    , genero_id) 
                  VALUES (id
                        , NEW.nom_segundo
                        , NEW.nom_paterno
                        , NEW.nom_materno
                        , NEW.seudonimo
                        , NEW.lugar_muer
                        , NEW.genero_id);
  INSERT INTO persona_agregar VALUES (id
                                    , NEW.agregar_id
                                    , NEW.tit_comienzo
                                    , NEW.tit_finale
                                    , NEW.titulo);

  INSERT INTO usario (part_id
                    , nom_usario
                    , contrasena
                    , permiso
                    , confirmado
                    , fecha_confirmado)
                  VALUES (id
                        , NEW.nom_usario
                        , NEW.contrasena
                        , DEFAULT
                        , DEFAULT
                        , NEW.fecha_confirmado);
 RETURN NULL;
END;
$body$
LANGUAGE plpgsql;
 
CREATE TRIGGER pers_trigger
  INSTEAD OF INSERT ON part_pers
  FOR EACH ROW
  EXECUTE PROCEDURE pers_insert();

CREATE OR REPLACE VIEW part_ag AS
  SELECT part.part_id
       , part.nom_part
       , part.lugar_id
       , l.ciudad
       , l.nom_subdivision
       , l.tipo_subdivision
       , l.pais
       , part.fecha_comienzo
       , part.fecha_finale
       , part.sitio_web
       , part.direccion
       , part.telefono
       , part.email
       , ag.tipo_agregar
       , part.coment_participante
      FROM public.participante part
      LEFT JOIN public.lugar l
        ON l.lugar_id = part.Lugar_id
      LEFT JOIN public.usario u
        ON u.part_id = part.part_id
      JOIN public.agregar ag
        ON ag.part_id = part.part_id;

CREATE OR REPLACE FUNCTION ag_insert() RETURNS TRIGGER AS $body$
DECLARE
  id int;
BEGIN
  INSERT INTO participante (nom_part
                          , sitio_web
                          , direccion
                          , lugar_id
                          , telefono
                          , email
                          , fecha_comienzo
                          , fecha_finale
                          , coment_participante)
                        VALUES (NEW.nom_part
                              , NEW.sitio_web
                              , NEW.direccion
                              , NEW.lugar_id
                              , NEW.telefono
                              , NEW.email
                              , NEW.fecha_comienzo
                              , NEW.fecha_finale
                              , NEW.coment_participante) 
                            RETURNING part_id INTO id;
  INSERT INTO agregar(part_id
                    , tipo_agregar) 
                  VALUES (id
                        , NEW.tipo_agregar);
  RETURN NULL;
END;
$body$
LANGUAGE plpgsql;
 
CREATE TRIGGER ag_trigger
  INSTEAD OF INSERT ON part_ag
  FOR EACH ROW
  EXECUTE PROCEDURE ag_insert();


