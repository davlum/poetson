
CREATE OR REPLACE VIEW limbo.part_us AS
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
       , u.nom_usario
       , u.contrasena
       , u.permiso
       , u.confirmado
       , u.fecha_confirmado
      FROM limbo.participante_limbo part
      JOIN usario u
        ON u.part_id = part.part_id;

CREATE OR REPLACE FUNCTION limbo.us_insert() RETURNS TRIGGER AS $body$
DECLARE
  id int;
BEGIN
  INSERT INTO limbo.participante_limbo (nom_part
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
                                , id
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
 
DROP TRIGGER IF EXISTS limbo.us_trigger ON limbo.part_us;

CREATE TRIGGER limbo.us_trigger
  INSTEAD OF INSERT ON limbo.part_us
  FOR EACH ROW
  EXECUTE PROCEDURE limbo.us_insert();

---------------------------------------------------------------

CREATE OR REPLACE VIEW limbo.part_pers AS
  SELECT part.part_id pp_id
       , part.nom_part
       , pers.nom_segundo
       , pers.seudonimo
       , pers.nom_paterno
       , pers.nom_materno
       , part.lugar_id lugar_nac
       , l.ciudad
       , l.nom_subdivision
       , l.tipo_subdivision
       , l.pais
       , pers.lugar_muer
       , part.fecha_comienzo
       , part.fecha_finale
       , part.sitio_web
       , part.direccion
       , part.telefono
       , part.email
       , pers.genero
       , part.coment_participante
       , pa.persona_id
       , pa.agregar_id
       , pa.fecha_comienzo tit_comienzo
       , pa.fecha_finale tit_finale
       , pa.titulo
      FROM limbo.participante_limbo part
      JOIN limbo.persona_limbo pers
        ON pers.part_id = part.part_id
      LEFT JOIN public.lugar l
        ON l.lugar_id = part.lugar_id
      LEFT JOIN limbo.persona_agregar_limbo pa
        ON pa.persona_id=pers.part_id;

CREATE OR REPLACE FUNCTION limbo.pers_insert() RETURNS TRIGGER AS $body$
DECLARE
  id int;
BEGIN
  IF TG_OP = 'INSERT' THEN
    INSERT INTO lugar(ciudad
                    , nom_subdivision
                    , tipo_subdivision
                    , pais)
                  VALUES (NEW.ciudad
                        , NEW.nom_subdivision
                        , NEW.tipo_subdivision
                        , NEW.pais)
                      RETURNING lugar_id INTO id;

    INSERT INTO limbo.participante_limbo (nom_part
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
                                  , id
                                  , NEW.telefono
                                  , NEW.email
                                  , NEW.fecha_comienzo
                                  , NEW.fecha_finale
                                  , NEW.coment_participante) 
                                  RETURNING part_id INTO id;
    INSERT INTO limbo.persona_limbo(part_id
                      , nom_segundo
                      , nom_paterno
                      , nom_materno
                      , seudonimo
                      , lugar_muer
                      , genero) 
                    VALUES (id
                          , NEW.nom_segundo
                          , NEW.nom_paterno
                          , NEW.nom_materno
                          , NEW.seudonimo
                          , NEW.lugar_muer
                          , NEW.genero);

    IF NEW.agregar_id < 0 THEN
        INSERT INTO limbo.persona_agregar_limbo VALUES (id
                                          , NEW.agregar_id
                                          , NEW.tit_comienzo
                                          , NEW.tit_finale
                                          , NEW.titulo);
    END IF;
  ELSIF (TG_OP = 'UPDATE') THEN

    UPDATE limbo.participante_limbo SET nom_part=NEW.nom_part
                            , sitio_web=NEW.sitio_web
                            , direccion=NEW.direccion
                            , telefono=NEW.telefono
                            , email=NEW.email
                            , fecha_comienzo=NEW.fecha_comienzo
                            , fecha_finale=NEW.fecha_finale
                            , coment_participante=NEW.coment_participante
                            WHERE part_id=OLD.pp_id
                            RETURNING old.pp_id INTO id;

    UPDATE limbo.persona_limbo SET  nom_segundo=NEW.nom_segundo
                      , nom_paterno=NEW.nom_paterno
                      , nom_materno=NEW.nom_materno
                      , seudonimo=NEW.seudonimo
                      , lugar_muer=NEW.lugar_muer
                      , genero=NEW.genero
                      WHERE part_id=OLD.pp_id;

    UPDATE lugar SET  ciudad=NEW.ciudad
                    , nom_subdivision=NEW.nom_subdivision
                    , tipo_subdivision=NEW.tipo_subdivision
                    , pais=NEW.pais
                    WHERE lugar_id=OLD.lugar_nac;

    IF NEW.agregar_id <> 0 THEN
      INSERT INTO limbo.persona_limbo_agregar VALUES (id
                                        , NEW.agregar_id
                                        , NEW.tit_comienzo
                                        , NEW.tit_finale
                                        , NEW.titulo);
    END IF;
  END IF;
  RETURN NULL;
END;
$body$
LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS limbo.pers_trigger ON limbo.part_pers;

CREATE TRIGGER limbo.pers_trigger
  INSTEAD OF INSERT OR UPDATE ON limbo.part_pers
  FOR EACH ROW
  EXECUTE PROCEDURE limbo.pers_insert();

----------------------------------------------------------

CREATE OR REPLACE VIEW limbo.part_ag AS
  SELECT part.part_id pa_id
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
      FROM limbo.participante_limbo part
      LEFT JOIN public.lugar l
        ON l.lugar_id = part.lugar_id
      JOIN limbo.agregar_limbo ag
        ON ag.part_id = part.part_id;

CREATE OR REPLACE FUNCTION limbo.ag_insert() RETURNS TRIGGER AS $body$
DECLARE
  id int;
BEGIN

  IF (TG_OP = 'INSERT') THEN
    INSERT INTO lugar(ciudad
                    , nom_subdivision
                    , tipo_subdivision
                    , pais)
                  VALUES (NEW.ciudad
                        , NEW.nom_subdivision
                        , NEW.tipo_subdivision
                        , NEW.pais)
                      RETURNING lugar_id INTO id;

    INSERT INTO limbo.participante_limbo (nom_part
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
                                , id
                                , NEW.telefono
                                , NEW.email
                                , NEW.fecha_comienzo
                                , NEW.fecha_finale
                                , NEW.coment_participante)
                              RETURNING part_id INTO id;
    INSERT INTO limbo.agregar_limbo(part_id
                      , tipo_agregar)
                    VALUES (id
                          , NEW.tipo_agregar);

  ELSIF (TG_OP = 'UPDATE') THEN
    UPDATE limbo.participante_limbo SET nom_part=NEW.nom_part
                            , sitio_web=NEW.sitio_web
                            , direccion=NEW.direccion
                            , telefono=NEW.telefono
                            , email=NEW.email
                            , fecha_comienzo=NEW.fecha_comienzo
                            , fecha_finale=NEW.fecha_finale
                            , coment_participante=NEW.coment_participante
                            WHERE part_id=OLD.pa_id;
    
    UPDATE lugar SET ciudad=NEW.ciudad
                   , nom_subdivision=NEW.nom_subdivision
                   , tipo_subdivision=NEW.tipo_subdivision
                   , pais=NEW.pais
                  WHERE lugar_id=OLD.lugar_id;


    UPDATE limbo.agregar_limbo SET tipo_agregar=NEW.tipo_agregar
                      WHERE part_id=OLD.pa_id;


  END IF;
  RETURN NULL;
END;
$body$
LANGUAGE plpgsql;
 
DROP TRIGGER IF EXISTS limbo.ag_trigger ON limbo.part_ag;

CREATE TRIGGER limbo.ag_trigger
  INSTEAD OF INSERT OR UPDATE ON limbo.part_ag
  FOR EACH ROW
  EXECUTE PROCEDURE limbo.ag_insert();

----------------------------------------------------------------

CREATE OR REPLACE VIEW limbo.part_us_pers AS
  SELECT * FROM limbo.part_pers pp
  JOIN usario u
  ON pp_id = u.part_id;

CREATE OR REPLACE FUNCTION limbo.us_pers_insert() RETURNS TRIGGER AS $body$
DECLARE
  id int;
BEGIN
  INSERT INTO lugar(ciudad
                    , nom_subdivision
                    , tipo_subdivision
                    , pais)
                  VALUES (NEW.ciudad
                        , NEW.nom_subdivision
                        , NEW.tipo_subdivision
                        , NEW.pais)
                      RETURNING lugar_id INTO id;

  INSERT INTO limbo.participante_limbo (nom_part
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
                                , id
                                , NEW.telefono
                                , NEW.email
                                , NEW.fecha_comienzo
                                , NEW.fecha_finale
                                , NEW.coment_participante) 
                                RETURNING part_id INTO id;
  INSERT INTO limbo.persona_limbo(part_id
                    , nom_segundo
                    , nom_paterno
                    , nom_materno
                    , seudonimo
                    , lugar_muer
                    , genero) 
                  VALUES (id
                        , NEW.nom_segundo
                        , NEW.nom_paterno
                        , NEW.nom_materno
                        , NEW.seudonimo
                        , NEW.lugar_muer
                        , NEW.genero);
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
 
DROP TRIGGER IF EXISTS us_pers_trigger ON part_us_pers;

CREATE TRIGGER us_pers_trigger
  INSTEAD OF INSERT ON part_us_pers
  FOR EACH ROW
  EXECUTE PROCEDURE limbo.us_pers_insert();

--------------------------------------------------------------

CREATE OR REPLACE VIEW limbo.part_us_ag AS
  SELECT * FROM limbo.part_ag pa
  JOIN usario u
  ON pa_id = u.part_id;

CREATE OR REPLACE FUNCTION limbo.us_ag_insert() RETURNS TRIGGER AS $body$
DECLARE
  id int;
BEGIN
  INSERT INTO lugar(ciudad
                    , nom_subdivision
                    , tipo_subdivision
                    , pais)
                  VALUES (NEW.ciudad
                        , NEW.nom_subdivision
                        , NEW.tipo_subdivision
                        , NEW.pais)
                      RETURNING lugar_id INTO id;

  INSERT INTO limbo.participante_limbo (nom_part
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
                              , id
                              , NEW.telefono
                              , NEW.email
                              , NEW.fecha_comienzo
                              , NEW.fecha_finale
                              , NEW.coment_participante) 
                            RETURNING part_id INTO id;
 
  INSERT INTO limbo.agregar_limbo(part_id
                    , tipo_agregar) 
                  VALUES (id
                        , NEW.tipo_agregar);
  
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
 
DROP TRIGGER IF EXISTS limbo.us_ag_trigger ON limbo.part_us_ag;

CREATE TRIGGER limbo.us_ag_trigger
  INSTEAD OF INSERT ON limbo.part_us_ag
  FOR EACH ROW
  EXECUTE PROCEDURE limbo.us_ag_insert();


