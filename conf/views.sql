CREATE OR REPLACE VIEW part_pers AS
  SELECT pers.part_id
       , part.nom_part
       , pers.nom_segundo
       , pers.seudonimo
       , pers.nom_paterno
       , pers.nom_materno
       , part.lugar_id lugar_nac
       , pers.lugar_muer
       , get_fecha(part.fecha_comienzo) fecha_comienzo
       , get_fecha(part.fecha_finale) fecha_finale
       , part.sitio_web
       , part.direccion
       , part.telefono
       , part.email
       , gp.nom_genero
       , part.coment_participante
      FROM public.participante part
      JOIN persona pers
        ON pers.part_id = part.part_id
      JOIN genero_persona gp
        ON gp.genero_id = pers.genero_id;

CREATE OR REPLACE VIEW part_ag AS
  SELECT ag.part_id
       , part.nom_part
       , l.ciudad
       , l.nom_subdivision
       , l.pais
       , get_fecha(part.fecha_comienzo) fecha_comienzo
       , get_fecha(part.fecha_finale) fecha_finale
       , part.sitio_web
       , part.direccion
       , part.telefono
       , part.email
       , ag.tipo_agregar
       , part.coment_participante
      FROM public.participante part
      LEFT JOIN public.lugar l
        ON l.lugar_id = part.Lugar_id
      JOIN public.agregar ag
        ON ag.part_id = part.part_id;


