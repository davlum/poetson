CREATE OR REPLACE view public.part_view AS
  SELECT pa.part_id
       , COALESCE(a.nom_part,
         CONCAT(pe.nom_part, ' ''', pe.seudonimo, ''' ', pe.nom_paterno)) nom_part
    FROM public.participante pa
    LEFT JOIN public.persona pe
      ON pa.part_id = pe.part_id
    LEFT JOIN public.agregar a
      ON pa.part_id = a.part_id;


CREATE OR REPLACE VIEW public.pers_view AS
  SELECT pers.part_id
       , pers.seudonimo
       , pers.nom_paterno
       , pers.nom_materno
       , pers.genero
        -- Join with lugar
       , pers.lugar_muer
       , l2.ciudad ciudad_muer
       , l2.subdivision subdivision_muer
       , l2.pais pais_muer
        -- Common attrs
       , pers.nom_part
       , get_fecha(pers.fecha_comienzo) fecha_comienzo
       , get_fecha(pers.fecha_finale) fecha_finale
       , pers.fecha_comienzo fecha_comienzo_insert
       , pers.fecha_finale fecha_finale_insert
       , pers.sitio_web
       , pers.direccion
       , pers.telefono
       , pers.email
       , pers.coment_part
        -- Join with lugar
       , pers.lugar_id
       , l1.ciudad
       , l1.subdivision
       , l1.pais
        -- Audit attrs
       , pers.mod_id
       , pers.cargador_id
       , pers.estado
     FROM public.persona pers
      LEFT JOIN public.lugar l1
        ON l1.lugar_id = pers.lugar_id
      LEFT JOIN public.lugar l2
        ON l2.lugar_id = pers.lugar_muer;

CREATE OR REPLACE FUNCTION pers_insert() RETURNS TRIGGER AS $body$
DECLARE
  id_nac int;
  id_muer int;

BEGIN
  IF TG_OP = 'INSERT' THEN
    INSERT INTO public.lugar(ciudad
                    , subdivision
                    , pais)
                  VALUES (NEW.ciudad
                        , NEW.subdivision
                        , NEW.pais)
                      RETURNING lugar_id INTO id_nac;

    INSERT INTO public.lugar(ciudad
                    , subdivision
                    , pais)
                  VALUES (NEW.ciudad_muer
                        , NEW.subdivision_muer
                        , NEW.pais_muer)
                      RETURNING lugar_id INTO id_muer;

    INSERT INTO public.persona(nom_paterno
                              , nom_materno
                              , seudonimo
                              , lugar_muer
                              , genero
                              -- Common attrs
                              , nom_part
                              , sitio_web
                              , direccion
                              , lugar_id
                              , telefono
                              , email
                              , fecha_comienzo
                              , fecha_finale
                              , coment_part
                              -- Audit attr
                              , cargador_id)
                            VALUES (NEW.nom_paterno
                                  , NEW.nom_materno
                                  , NEW.seudonimo
                                  , id_muer
                                  , NEW.genero
                                    -- Common attrs
                                  , NEW.nom_part
                                  , NEW.sitio_web
                                  , NEW.direccion
                                  , id_nac
                                  , NEW.telefono
                                  , NEW.email
                                  , NEW.fecha_comienzo_insert
                                  , NEW.fecha_finale_insert
                                  , NEW.coment_part
                                  -- Audit attrs
                                  , NEW.cargador_id);

  ELSIF (TG_OP = 'UPDATE') THEN

    UPDATE public.persona SET nom_paterno=NEW.nom_paterno
                            , nom_materno=NEW.nom_materno
                            , seudonimo=NEW.seudonimo
                            , lugar_muer=NEW.lugar_muer
                            , genero=NEW.genero
                            -- Common attrs
                            , nom_part=NEW.nom_part
                            , sitio_web=NEW.sitio_web
                            , direccion=NEW.direccion
                            , telefono=NEW.telefono
                            , email=NEW.email
                            , fecha_comienzo=NEW.fecha_comienzo_insert
                            , fecha_finale=NEW.fecha_finale_insert
                            , coment_part=NEW.coment_part
                            -- Audit attrs
                            , cargador_id=NEW.cargador_id
                            , mod_id=NEW.mod_id
                            , estado=NEW.estado
                      WHERE part_id=OLD.part_id;

    UPDATE public.lugar SET ciudad=NEW.ciudad
                    , subdivision=NEW.subdivision
                    , pais=NEW.pais
                    WHERE lugar_id=OLD.lugar_id;

    UPDATE public.lugar SET ciudad=NEW.ciudad_muer
                    , subdivision=NEW.subdivision_muer
                    , pais=NEW.pais_muer
                    WHERE lugar_id=OLD.lugar_muer;

  END IF;
  RETURN NULL;
END;
$body$
LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS pers_trigger ON public.pers_view;

CREATE TRIGGER pers_trigger
  INSTEAD OF INSERT OR UPDATE ON public.pers_view
  FOR EACH ROW
  EXECUTE PROCEDURE pers_insert();


----------------------------------------------------------------
CREATE OR REPLACE VIEW public.ag_view AS
  SELECT ag.part_id
       , ag.tipo_agregar
        -- Common attrs
       , ag.nom_part
       , get_fecha(ag.fecha_comienzo) fecha_comienzo
       , get_fecha(ag.fecha_finale) fecha_finale
       , ag.fecha_comienzo fecha_comienzo_insert
       , ag.fecha_finale fecha_finale_insert
       , ag.sitio_web
       , ag.direccion
       , ag.telefono
       , ag.email
       , ag.coment_part
        -- Join with lugar
       , ag.lugar_id
       , l1.ciudad
       , l1.subdivision
       , l1.pais
        -- Audit attrs
       , ag.cargador_id
       , ag.mod_id
       , ag.estado
     FROM public.agregar ag
     LEFT JOIN public.lugar l1
       ON l1.lugar_id = ag.lugar_id;

CREATE OR REPLACE FUNCTION ag_insert() RETURNS TRIGGER AS $body$
DECLARE
  id_comienzo int;
BEGIN
  IF TG_OP = 'INSERT' THEN
    INSERT INTO public.lugar(ciudad
                    , subdivision
                    , pais)
                  VALUES (NEW.ciudad
                        , NEW.subdivision
                        , NEW.pais)
                      RETURNING lugar_id INTO id_comienzo;

    INSERT INTO public.agregar(tipo_agregar
                              -- Common attrs
                              , nom_part
                              , sitio_web
                              , direccion
                              , lugar_id
                              , telefono
                              , email
                              , fecha_comienzo
                              , fecha_finale
                              , coment_part
                              -- Audit attr
                              , cargador_id)
                            VALUES (NEW.tipo_agregar
                                    -- Common attrs
                                  , NEW.nom_part
                                  , NEW.sitio_web
                                  , NEW.direccion
                                  , id_comienzo
                                  , NEW.telefono
                                  , NEW.email
                                  , NEW.fecha_comienzo_insert
                                  , NEW.fecha_finale_insert
                                  , NEW.coment_part
                                  -- Audit attrs
                                  , NEW.cargador_id);

  ELSIF (TG_OP = 'UPDATE') THEN

    UPDATE public.agregar SET tipo_agregar=NEW.tipo_agregar
                            -- Common attrs
                            , nom_part=NEW.nom_part
                            , sitio_web=NEW.sitio_web
                            , direccion=NEW.direccion
                            , telefono=NEW.telefono
                            , email=NEW.email
                            , fecha_comienzo=NEW.fecha_comienzo_insert
                            , fecha_finale=NEW.fecha_finale_insert
                            , coment_part=NEW.coment_part
                            -- Audit attrs
                            , cargador_id=NEW.cargador_id
                            , mod_id=NEW.mod_id
                            , estado=NEW.estado
                      WHERE part_id=OLD.part_id;

      UPDATE public.lugar SET ciudad=NEW.ciudad
                      , subdivision=NEW.subdivision
                      , pais=NEW.pais
                      WHERE lugar_id=OLD.lugar_id;

  END IF;
  RETURN NULL;
END;
$body$
LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS ag_trigger ON public.ag_view;

CREATE TRIGGER ag_trigger
  INSTEAD OF INSERT OR UPDATE ON public.ag_view
  FOR EACH ROW
  EXECUTE PROCEDURE ag_insert();


----------------------------------------------------------------

CREATE OR REPLACE VIEW public.us_pers AS
  SELECT * FROM public.pers_view p
  JOIN public.usuario u
  ON p.part_id = u.usuario_id;

CREATE OR REPLACE FUNCTION us_pers_insert() RETURNS TRIGGER AS $body$
DECLARE
  id_comienzo int;
  id int;
BEGIN

  INSERT INTO public.lugar DEFAULT VALUES RETURNING lugar_id INTO id_comienzo;

  INSERT INTO public.persona(seudonimo
                            -- Common attrs
                            , email
                            , lugar_id)
                  VALUES (NEW.nom_usuario
                        -- Common attrs
                        , NEW.email
                        , id_comienzo)
                        RETURNING part_id INTO id;

  INSERT INTO public.usuario (usuario_id
                            , nom_usuario
                            , pers_email
                            , contrasena)
                  VALUES (id
                        , NEW.nom_usuario
                        , NEW.email
                        , NEW.contrasena);

  RETURN NULL;
END;
$body$
LANGUAGE plpgsql;
 
DROP TRIGGER IF EXISTS us_pers_trigger ON public.us_pers;

CREATE TRIGGER us_pers_trigger
  INSTEAD OF INSERT ON public.us_pers
  FOR EACH ROW
  EXECUTE PROCEDURE us_pers_insert();

--------------------------------------------------------------

CREATE OR REPLACE VIEW public.us_ag AS
  SELECT * FROM public.ag_view a
  JOIN public.usuario u
  ON a.part_id = u.usuario_id;

CREATE OR REPLACE FUNCTION us_ag_insert() RETURNS TRIGGER AS $body$
DECLARE
  id_comienzo int;
  id int;
BEGIN
  INSERT INTO public.lugar DEFAULT VALUES RETURNING lugar_id INTO id_comienzo;

  INSERT INTO public.agregar(nom_part, email, lugar_id) VALUES
    (NEW.nom_usuario, NEW.email, id_comienzo) RETURNING part_id INTO id;

  INSERT INTO public.usuario (usuario_id
                            , nom_usuario
                            , ag_email
                            , contrasena)
                          VALUES (id
                                , NEW.nom_usuario
                                , NEW.email
                                , NEW.contrasena);

  RETURN NULL;
END;
$body$
LANGUAGE plpgsql;
 
DROP TRIGGER IF EXISTS us_ag_trigger ON public.us_ag;

CREATE TRIGGER us_ag_trigger
  INSTEAD OF INSERT ON public.us_ag
  FOR EACH ROW
  EXECUTE PROCEDURE us_ag_insert();


