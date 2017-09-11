
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
       , part.coment_part
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
  INSERT INTO public.participante (nom_part
                          , sitio_web
                          , direccion
                          , lugar_id
                          , telefono
                          , email
                          , fecha_comienzo
                          , fecha_finale
                          , coment_part)
                          VALUES (NEW.nom_part
                                , NEW.sitio_web
                                , NEW.direccion
                                , id
                                , NEW.telefono
                                , NEW.email
                                , NEW.fecha_comienzo
                                , NEW.fecha_finale
                                , NEW.coment_part)
                                RETURNING part_id INTO id;
 INSERT INTO public.usario ( part_id
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
 
DROP TRIGGER IF EXISTS us_trigger ON part_us;

CREATE TRIGGER us_trigger
  INSTEAD OF INSERT ON part_us
  FOR EACH ROW
  EXECUTE PROCEDURE us_insert();

---------------------------------------------------------------

CREATE OR REPLACE VIEW part_pers AS
  SELECT part.part_id pp_id
       , part.nom_part
       , pers.nom_segundo
       , pers.seudonimo
       , pers.nom_paterno
       , pers.nom_materno
       , part.lugar_id
       , l1.ciudad
       , l1.nom_subdivision
       , l1.tipo_subdivision
       , l1.pais
       , pers.lugar_muer
       , l2.ciudad ciudad_muer
       , l2.nom_subdivision nom_subdivision_muer
       , l2.tipo_subdivision tipo_subdivision_muer
       , l2.pais pais_muer
       , get_fecha(part.fecha_comienzo) fecha_comienzo
       , get_fecha(part.fecha_finale) fecha_finale
       , part.fecha_comienzo fecha_comienzo_insert
       , part.fecha_finale fecha_finale_insert
       , part.sitio_web
       , part.direccion
       , part.telefono
       , part.email
       , pers.genero
       , part.coment_part
       , part.cargador_id
       , part.estado
     FROM public.participante part
      JOIN public.persona pers
        ON pers.part_id = part.part_id
      LEFT JOIN public.lugar l1
        ON l1.lugar_id = part.lugar_id
      LEFT JOIN public.lugar l2
        ON l2.lugar_id = pers.lugar_muer;

CREATE OR REPLACE FUNCTION pers_insert() RETURNS TRIGGER AS $body$
DECLARE
  id int;
  id_nac int;
  id_muer int;

BEGIN
  IF TG_OP = 'INSERT' THEN
    INSERT INTO public.lugar(ciudad
                    , nom_subdivision
                    , tipo_subdivision
                    , pais)
                  VALUES (NEW.ciudad
                        , NEW.nom_subdivision
                        , NEW.tipo_subdivision
                        , NEW.pais)
                      RETURNING lugar_id INTO id_nac;

    INSERT INTO public.lugar(ciudad
                    , nom_subdivision
                    , tipo_subdivision
                    , pais)
                  VALUES (NEW.ciudad_muer
                        , NEW.nom_subdivision_muer
                        , NEW.tipo_subdivision_muer
                        , NEW.pais_muer)
                      RETURNING lugar_id INTO id_muer;

    INSERT INTO public.participante (nom_part
                            , sitio_web
                            , direccion
                            , lugar_id
                            , telefono
                            , email
                            , fecha_comienzo
                            , fecha_finale
                            , coment_part
                            , cargador_id
                            , mod_id
                            , estado)
                            VALUES (NEW.nom_part
                                  , NEW.sitio_web
                                  , NEW.direccion
                                  , id_nac
                                  , NEW.telefono
                                  , NEW.email
                                  , NEW.fecha_comienzo_insert
                                  , NEW.fecha_finale_insert
                                  , NEW.coment_part
                                  , NEW.cargador_id
                                  , NEW.mod_id
                                  , NEW.estado)
                                  RETURNING part_id INTO id;

    INSERT INTO public.persona(part_id
                      , nom_segundo
                      , nom_paterno
                      , nom_materno
                      , seudonimo
                      , lugar_muer
                      , genero
                      , cargador_id) 
                    VALUES (id
                          , NEW.nom_segundo
                          , NEW.nom_paterno
                          , NEW.nom_materno
                          , NEW.seudonimo
                          , id_muer
                          , NEW.genero
                          , NEW.cargador_id
                          , NEW.mod_id
                          , NEW.estado);

  ELSIF (TG_OP = 'UPDATE') THEN

    UPDATE public.participante SET nom_part=NEW.nom_part
                            , sitio_web=NEW.sitio_web
                            , direccion=NEW.direccion
                            , telefono=NEW.telefono
                            , email=NEW.email
                            , fecha_comienzo=NEW.fecha_comienzo_insert
                            , fecha_finale=NEW.fecha_finale_insert
                            , coment_part=NEW.coment_part
                            , cargador_id=NEW.cargador_id
                            , mod_id=NEW.mod_id
                            , estado=NEW.estado
                            WHERE part_id=OLD.pp_id;

    UPDATE public.persona SET nom_segundo=NEW.nom_segundo
                      , nom_paterno=NEW.nom_paterno
                      , nom_materno=NEW.nom_materno
                      , seudonimo=NEW.seudonimo
                      , lugar_muer=NEW.lugar_muer
                      , genero=NEW.genero
                      , cargador_id=NEW.cargador_id
                      , mod_id=NEW.mod_id
                      , estado=NEW.estado
                      WHERE part_id=OLD.pp_id;

    UPDATE public.lugar SET ciudad=NEW.ciudad
                    , nom_subdivision=NEW.nom_subdivision
                    , tipo_subdivision=NEW.tipo_subdivision
                    , pais=NEW.pais
                    WHERE lugar_id=OLD.lugar_id;

    UPDATE public.lugar SET ciudad=NEW.ciudad_muer
                    , nom_subdivision=NEW.nom_subdivision_muer
                    , tipo_subdivision=NEW.tipo_subdivision_muer
                    , pais=NEW.pais_muer
                    WHERE lugar_id=OLD.lugar_muer;

  END IF;
  RETURN NULL;
END;
$body$
LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS pers_trigger ON part_pers;

CREATE TRIGGER pers_trigger
  INSTEAD OF INSERT OR UPDATE ON part_pers
  FOR EACH ROW
  EXECUTE PROCEDURE pers_insert();

----------------------------------------------------------

CREATE OR REPLACE VIEW part_ag AS
  SELECT part.part_id pa_id
       , part.nom_part
       , part.lugar_id
       , l.ciudad
       , l.nom_subdivision
       , l.tipo_subdivision
       , l.pais
       , get_fecha(part.fecha_comienzo) fecha_comienzo
       , get_fecha(part.fecha_finale) fecha_finale
       , part.fecha_comienzo fecha_comienzo_insert
       , part.fecha_finale fecha_finale_insert
       , part.sitio_web
       , part.direccion
       , part.telefono
       , part.email
       , ag.tipo_agregar
       , part.coment_part
      FROM public.participante part
      LEFT JOIN public.lugar l
        ON l.lugar_id = part.lugar_id
      JOIN public.agregar ag
        ON ag.part_id = part.part_id;

CREATE OR REPLACE FUNCTION ag_insert() RETURNS TRIGGER AS $body$
DECLARE
  id int;
BEGIN

  IF (TG_OP = 'INSERT') THEN
    INSERT INTO public.lugar(ciudad
                    , nom_subdivision
                    , tipo_subdivision
                    , pais)
                  VALUES (NEW.ciudad
                        , NEW.nom_subdivision
                        , NEW.tipo_subdivision
                        , NEW.pais)
                      RETURNING lugar_id INTO id;

    INSERT INTO public.participante (nom_part
                            , sitio_web
                            , direccion
                            , lugar_id
                            , telefono
                            , email
                            , fecha_comienzo
                            , fecha_finale
                            , coment_part
                            , cargador_id
                            , mod_id
                            , estado)
                          VALUES (NEW.nom_part
                                , NEW.sitio_web
                                , NEW.direccion
                                , id
                                , NEW.telefono
                                , NEW.email
                                , NEW.fecha_comienzo_insert
                                , NEW.fecha_finale_insert
                                , NEW.coment_part
                                , NEW.cargador_id
                                , NEW.mod_id
                                , NEW.estado)
                              RETURNING part_id INTO id;

    INSERT INTO public.agregar(part_id
                      , tipo_agregar
                      , cargador_id
                      , mod_id
                      , estado)
                    VALUES (id
                          , NEW.tipo_agregar
                          , NEW.cargador_id
                          , NEW.mod_id
                          , NEW.estado);

  ELSIF (TG_OP = 'UPDATE') THEN
    UPDATE public.participante SET nom_part=NEW.nom_part
                            , sitio_web=NEW.sitio_web
                            , direccion=NEW.direccion
                            , telefono=NEW.telefono
                            , email=NEW.email
                            , fecha_comienzo=NEW.fecha_comienzo_insert
                            , fecha_finale=NEW.fecha_finale_insert
                            , coment_part=NEW.coment_part
                            , cargador_id=NEW.cargador_id
                            , mod_id=NEW.mod_id
                            , estado=NEW.estado
                          WHERE part_id=OLD.pa_id;
    
    UPDATE public.lugar SET ciudad=NEW.ciudad
                   , nom_subdivision=NEW.nom_subdivision
                   , tipo_subdivision=NEW.tipo_subdivision
                   , pais=NEW.pais
                   , cargador_id=NEW.cargador_id
                   , mod_id=NEW.mod_id
                   , estado=NEW.estado
                  WHERE lugar_id=OLD.lugar_id;

    UPDATE public.agregar SET tipo_agregar=NEW.tipo_agregar WHERE part_id=OLD.pa_id;
  END IF;
  RETURN NULL;
END;
$body$
LANGUAGE plpgsql;
 
DROP TRIGGER IF EXISTS ag_trigger ON part_ag;

CREATE TRIGGER ag_trigger
  INSTEAD OF INSERT OR UPDATE ON part_ag
  FOR EACH ROW
  EXECUTE PROCEDURE ag_insert();

----------------------------------------------------------------

CREATE OR REPLACE VIEW part_us_pers AS
  SELECT * FROM part_pers pp
  JOIN public.usario u
  ON pp_id = u.part_id;

CREATE OR REPLACE FUNCTION us_pers_insert() RETURNS TRIGGER AS $body$
DECLARE
  id_comienzo int;
  id int;
BEGIN
  INSERT INTO public.lugar(ciudad
                    , nom_subdivision
                    , tipo_subdivision
                    , pais)
                  VALUES (NEW.ciudad
                        , NEW.nom_subdivision
                        , NEW.tipo_subdivision
                        , NEW.pais)
                      RETURNING lugar_id INTO id_comienzo;

  INSERT INTO public.participante (nom_part
                          , sitio_web
                          , direccion
                          , lugar_id
                          , telefono
                          , email
                          , fecha_comienzo
                          , fecha_finale
                          , coment_part
                          , estado)
                          VALUES (NEW.nom_part
                                , NEW.sitio_web
                                , NEW.direccion
                                , id_comienzo
                                , NEW.telefono
                                , NEW.email
                                , NEW.fecha_comienzo_insert
                                , NEW.fecha_finale_insert
                                , NEW.coment_part
                                , 'PENDIENTE')
                                RETURNING part_id INTO id;

  INSERT INTO public.persona(part_id
                    , nom_segundo
                    , nom_paterno
                    , nom_materno
                    , seudonimo
                    , lugar_muer
                    , genero
                    , cargador_id
                    , mod_id
                    , estado)
                  VALUES (id
                        , NEW.nom_segundo
                        , NEW.nom_paterno
                        , NEW.nom_materno
                        , NEW.seudonimo
                        , NEW.lugar_muer
                        , NEW.genero
                        , id
                        , 'PENDIENTE');

  INSERT INTO public.usario (part_id
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
  EXECUTE PROCEDURE us_pers_insert();

--------------------------------------------------------------

CREATE OR REPLACE VIEW part_us_ag AS
  SELECT * FROM part_ag pa
  JOIN public.usario u
  ON pa_id = u.part_id;

CREATE OR REPLACE FUNCTION us_ag_insert() RETURNS TRIGGER AS $body$
DECLARE
  id_comienzo int;
  id int;
BEGIN
  INSERT INTO public.lugar(ciudad
                    , nom_subdivision
                    , tipo_subdivision
                    , pais)
                  VALUES (NEW.ciudad
                        , NEW.nom_subdivision
                        , NEW.tipo_subdivision
                        , NEW.pais)
                      RETURNING lugar_id INTO id_comienzo;

  INSERT INTO public.participante (nom_part
                          , sitio_web
                          , direccion
                          , lugar_id
                          , telefono
                          , email
                          , fecha_comienzo
                          , fecha_finale
                          , coment_part
                          , estado)
                        VALUES (NEW.nom_part
                              , NEW.sitio_web
                              , NEW.direccion
                              , id_comienzo
                              , NEW.telefono
                              , NEW.email
                              , NEW.fecha_comienzo_insert
                              , NEW.fecha_finale_insert
                              , NEW.coment_part
                              , 'PENDIENTE')
                            RETURNING part_id INTO id;
 
  INSERT INTO public.agregar(part_id
                    , tipo_agregar
                    , cargador_id
                    , estado)
                  VALUES (id
                        , NEW.tipo_agregar
                        , id
                        , 'PENDIENTE');
  
  INSERT INTO public.usario (part_id
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
 
DROP TRIGGER IF EXISTS us_ag_trigger ON public.part_us_ag;

CREATE TRIGGER us_ag_trigger
  INSTEAD OF INSERT ON part_us_ag
  FOR EACH ROW
  EXECUTE PROCEDURE us_ag_insert();


