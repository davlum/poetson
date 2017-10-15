from sqlalchemy import text
from copy import deepcopy
import time


def add_tags(old_tags, new_tags):
    return {k: old_tags.get(k, 0) + new_tags.get(k, 0) for k in set(old_tags) | set(new_tags)}


def autors_comps_query():
    autors_query = text("""SELECT p.part_id pers_id
                                , g.part_id gr_id
                                , g.nom_part nom_part_ag
                                , p.nom_part
                                , p.seudonimo
                                , p.nom_paterno
                                , p.nom_paterno
                                FROM public.participante_composicion pc
                                LEFT JOIN public.grupo g
                                  ON g.part_id = pc.part_id
                                LEFT JOIN public.persona p
                                  ON p.part_id = pc.part_id
                                  WHERE pc.composicion_id=:comp_id""")
    return autors_query


def tema_tags(con, comp_ids):
    temas = text("""SELECT t.nom_tema, COUNT(tc.tema_id) count
                           FROM public.tema t
                           JOIN public.tema_composicion tc
                             ON t.tema_id = tc.tema_id
                           WHERE tc.composicion_id IN :comp_ids
                           GROUP BY t.nom_tema""")
    return con.execute(temas, comp_ids=comp_ids)


def idioma_tags(con, comp_ids):
    idiomas = text("""SELECT i.nom_idioma, COUNT(ic.idioma_id) count
                           FROM public.idioma i
                           JOIN public.idioma_composicion ic
                             ON i.idioma_id = ic.idioma_id
                           WHERE ic.composicion_id IN :comp_ids
                           GROUP BY i.nom_idioma""")
    return con.execute(idiomas, comp_ids=comp_ids)


def genero_tags(con, comp_ids):
    generos = text("""SELECT gm.nom_gen_mus, COUNT(gp.gen_mus_id) count
                           FROM public.genero_musical gm
                           JOIN public.genero_pista gp
                             ON gm.gen_mus_id = gp.gen_mus_id
                           JOIN public.pista_son ps
                             ON ps.pista_son_id = gp.pista_son_id
                           WHERE ps.composicion_id IN :comp_ids
                           GROUP BY gm.nom_gen_mus""")
    return con.execute(generos, comp_ids=comp_ids)


def usuario_tags(con, part_ids, tbl_name, id_name):
    usuarios_str = "SELECT u.nom_usuario, COUNT(t." + id_name + """) count
              FROM public.usuario u JOIN public.""" + tbl_name + """ t ON u.usuario_id = t.cargador_id
                              WHERE t.""" + id_name + """ IN :part_ids
                              GROUP BY u.nom_usuario """
    usuarios = con.execute(text(usuarios_str), part_ids=part_ids)
    return {res[0]: res.count for res in usuarios}


def lugar_tags(con, part_ids, tipo_lugar, tbl_name, id_name):
    lugars_str = "SELECT l." + tipo_lugar + ", COUNT(t." + id_name + """) count
              FROM public.lugar l JOIN public.""" + tbl_name + """ t ON l.lugar_id = t.lugar_id
                              WHERE t.""" + id_name + """ IN :part_ids
                              GROUP BY l.""" + tipo_lugar
    lugars = con.execute(text(lugars_str), part_ids=part_ids)
    return {res[0]: res.count for res in lugars}


def gender_tags(con, part_ids):
    lugars = text("""SELECT genero, COUNT(part_id) count
                        FROM public.persona
                          WHERE part_id IN :part_ids
                          GROUP BY genero """)
    return con.execute(lugars, part_ids=part_ids)


def gen_comp_tags(con, comps, result):
    comps_arr = [(res, con.execute(autors_comps_query(), comp_id=res.composicion_id)) for res in comps]
    comp_ids = tuple([res[0].composicion_id for res in comps_arr])
    temas, idiomas, usuarios, generos, ciudads, subdivisions, paiss = ({} for i in range(7))
    if len(comp_ids) > 0:
        temas = tema_tags(con, comp_ids)
        idiomas = idioma_tags(con, comp_ids)
        generos = genero_tags(con, comp_ids)
        usuarios = usuario_tags(con, comp_ids, "composicion", "composicion_id")
        ciudads = lugar_tags(con, comp_ids, "ciudad", "pista_son", "pista_son_id")
        subdivisions = lugar_tags(con, comp_ids, "subdivision", "pista_son", "pista_son_id")
        paiss = lugar_tags(con, comp_ids, "pais", "pista_son", "pista_son_id")
    result['comps'] = comps_arr
    result['temas'] = temas
    result['idiomas'] = idiomas
    result['generos'] = generos
    try:
        add_tags(result['usuarios'], usuarios)
    except KeyError:
        result['usuarios'] = usuarios
    try:
        add_tags(result['ciudads'], ciudads)
    except KeyError:
        result['ciudads'] = ciudads
    try:
        add_tags(result['subdivisions'], subdivisions)
    except KeyError:
        result['subdivisions'] = subdivisions
    try:
        add_tags(result['paiss'], paiss)
    except KeyError:
        result['paiss'] = paiss


def gen_pers_tags(con, parts, result):
    parts_arr = [res for res in parts]
    part_ids = tuple([res.part_id for res in parts_arr])
    genders, usuarios, ciudads, subdivisions, paiss = ({} for i in range(5))
    if len(part_ids) > 0:
        ciudads = lugar_tags(con, part_ids, "ciudad", "persona", "part_id")
        subdivisions = lugar_tags(con, part_ids, "subdivision", "persona", "part_id")
        paiss = lugar_tags(con, part_ids, "pais", "persona", "part_id")
        usuarios = usuario_tags(con, part_ids, "persona", "part_id")
        genders = gender_tags(con, part_ids)
    result['pers'] = parts_arr
    result['genders'] = genders
    try:
        add_tags(result['usuarios'], usuarios)
    except KeyError:
        result['usuarios'] = usuarios
    try:
        add_tags(result['ciudads'], ciudads)
    except KeyError:
        result['ciudads'] = ciudads
    try:
        add_tags(result['subdivisions'], subdivisions)
    except KeyError:
        result['subdivisions'] = subdivisions
    try:
        add_tags(result['paiss'], paiss)
    except KeyError:
        result['paiss'] = paiss


def gen_grupo_tags(con, parts, result):
    parts_arr = [res for res in parts]
    part_ids = tuple([res.part_id for res in parts_arr])
    usuarios, ciudads, subdivisions, paiss = ({} for i in range(4))
    if len(part_ids) > 0:
        ciudads = lugar_tags(con, part_ids, "ciudad", "grupo", "part_id")
        subdivisions = lugar_tags(con, part_ids, "subdivision", "grupo", "part_id")
        paiss = lugar_tags(con, part_ids, "pais", "grupo", "part_id")
        usuarios = usuario_tags(con, part_ids, "grupo", "part_id")
    result['grupos'] = parts_arr
    try:
        add_tags(result['usuarios'], usuarios)
    except KeyError:
        result['usuarios'] = usuarios
    try:
        add_tags(result['ciudads'], ciudads)
    except KeyError:
        result['ciudads'] = ciudads
    try:
        add_tags(result['subdivisions'], subdivisions)
    except KeyError:
        result['subdivisions'] = subdivisions
    try:
        add_tags(result['paiss'], paiss)
    except KeyError:
        result['paiss'] = paiss


def set_years(bind_params):
    if bind_params['year_from'] is None:
        bind_params['year_from'] = 500
    if bind_params['year_to'] is None:
        bind_params['year_to'] = int(time.strftime('%Y'))+1


def autor_query(con, bind_params, result):
    local_params = deepcopy(bind_params)
    query_string = """SELECT p.part_id
                          , p.nom_part
                          , p.seudonimo
                          , p.nom_paterno
                          , p.nom_materno
                          , p.ciudad
                          , p.subdivision
                          , p.pais
                          , p.fecha_comienzo
                          , p.fecha_finale
                          FROM public.pers_view p 
                          LEFT JOIN public.participante_composicion pc
                            ON pc.part_id = p.part_id   
                          WHERE (p.nom_part ~* :nom
                            OR p.seudonimo ~* :nom
                            OR p.nom_materno ~* :nom
                            OR p.nom_paterno ~* :nom) 
                            AND p.estado='PUBLICADO' """
    if local_params['year_from'] is not None or local_params['year_to'] is not None:
        query_string += """AND EXTRACT(YEAR FROM (p.fecha_comienzo_insert).d) 
                            BETWEEN :year_from AND :year_to """
    if local_params['contains'] is not None and local_params['contains'] != "":
        query_string += "AND p.coment_part ~* :contains"
    set_years(local_params)
    query = text(query_string)
    parts = con.execute(query, local_params)
    gen_pers_tags(con, parts, result)


def colectivo_query(con, bind_params, result):
    local_params = deepcopy(bind_params)
    query_string = """SELECT g.part_id
                           , g.nom_part
                           , g.ciudad
                           , g.subdivision
                           , g.pais
                           , g.fecha_comienzo
                           , g.fecha_finale
                          FROM public.gr_view g 
                          WHERE g.tipo_grupo = 'Colectivo'
                            AND g.nom_part ~* :nom 
                            AND g.estado = 'PUBLICADO' """
    if local_params['year_from'] is not None or local_params['year_to'] is not None:
        query_string += """AND EXTRACT(YEAR FROM (g.fecha_comienzo_insert).d)
                            BETWEEN :year_from AND :year_to """
    if local_params['contains'] is not None and local_params['contains'] != "":
        query_string += "AND g.coment_part ~* :contains"
    set_years(local_params)
    query = text(query_string)
    parts = con.execute(query, local_params)
    gen_grupo_tags(con, parts, result)


def composicion_query(con, bind_params, result):
    local_params = deepcopy(bind_params)
    query_string = """SELECT composicion_id
                            , public.get_fecha(fecha_pub) fecha_pub
                            ,nom_tit
                            ,nom_alt
                          FROM public.composicion
                          WHERE (nom_tit ~* :nom 
                          OR nom_alt ~* :nom) 
                          AND estado = 'PUBLICADO' """
    if local_params['year_from'] is not None or local_params['year_to'] is not None:
        query_string += """AND EXTRACT(YEAR FROM (fecha_pub).d)
                            BETWEEN :year_from AND :year_to """
    if local_params['contains'] is not None and local_params['contains'] != "":
        query_string += "AND texto ~* :contains"
    set_years(local_params)
    query = text(query_string)
    comps = con.execute(query, local_params)
    gen_comp_tags(con, comps, result)


def serie_query(con, bind_params, result):
    query_string = """SELECT * 
                        FROM public.serie
                          WHERE nom_serie ~* :nom """
    if bind_params['contains'] is not None and bind_params['contains'] != "":
        query_string += "AND giro ~* :contains"
    query = text(query_string)
    result['serie'] = con.execute(query, bind_params)


def tema_query(con, bind_params, result):
    local_params = deepcopy(bind_params)
    query_string = """SELECT c.composicion_id
                            ,public.get_fecha(c.fecha_pub) fecha_pub
                            ,c.nom_tit
                            ,c.nom_alt 
                          FROM public.composicion c
                          JOIN public.tema_composicion tc
                            ON c.composicion_id = tc.composicion_id
                          JOIN public.tema t
                            ON t.tema_id = tc.tema_id  
                          WHERE t.nom_tema ~* :nom 
                            AND c.estado = 'PUBLICADO' """
    if local_params['year_from'] is not None or local_params['year_to'] is not None:
        query_string += """AND EXTRACT(YEAR FROM (c.fecha_pub).d)
                            BETWEEN :year_from AND :year_to """
    if local_params['contains'] is not None and local_params['contains'] != "":
        query_string += "AND c.texto ~* :contains"
    set_years(local_params)
    query = text(query_string)
    comps = con.execute(query, local_params)
    gen_comp_tags(con, comps, result)


def genero_query(con, bind_params, result):
    local_params = deepcopy(bind_params)
    query_string = """SELECT c.composicion_id
                            , get_fecha(c.fecha_pub) fecha_pub
                            ,c.nom_tit
                            ,c.nom_alt 
                            FROM public.composicion c
                          JOIN public.pista_son p
                            ON p.composicion_id = c.composicion_id
                          JOIN public.genero_pista gp
                            ON gp.pista_son_id = p.pista_son_id
                          JOIN public.genero_musical gm
                            ON gm.gen_mus_id = gp.gen_mus_id  
                          WHERE gm.nom_gen_mus ~* :nom 
                            AND c.estado = 'PUBLICADO' """
    if local_params['year_from'] is not None or local_params['year_to'] is not None:
        query_string += """AND EXTRACT(YEAR FROM (p.fecha_grab).d)
                            BETWEEN :year_from'] AND :year_to """
    if local_params['contains'] is not None and local_params['contains'] != "":
        query_string += "AND p.coment_pista_son ~* :contains"
    set_years(local_params)
    query = text(query_string)
    comps = con.execute(query, local_params)
    gen_comp_tags(con, comps, result)


def lugar_comp_query(con, bind_params, result, tipo_lugar):
    local_params = deepcopy(bind_params)
    query_string = """SELECT c.composicion_id
                            , get_fecha(c.fecha_pub) fecha_pub
                            ,c.nom_tit
                            ,c.nom_alt 
                          FROM public.composicion c
                          JOIN public.pista_son p
                            ON p.composicion_id = c.composicion_id
                          JOIN public.lugar l
                            ON l.lugar_id = p.lugar_id 
                          WHERE l.""" + tipo_lugar + " ~* :nom " \
                           "AND c.estado = 'PUBLICADO' "
    if local_params['year_from'] is not None or local_params['year_to'] is not None:
        query_string += """AND EXTRACT(YEAR FROM (p.fecha_grab).d)
                            BETWEEN :year_from'] AND :year_to """
    if local_params['contains'] is not None and local_params['contains'] != "":
        query_string += "AND p.coment_pista_son ~* :contains"
    set_years(local_params)
    query = text(query_string)
    comps = con.execute(query, local_params)
    gen_comp_tags(con, comps, result)


def lugar_autor_query(con, bind_params, result, tipo_lugar):
    local_params = deepcopy(bind_params)
    query_string = """SELECT p.part_id
                          , p.nom_part
                          , p.seudonimo
                          , p.nom_paterno
                          , p.nom_materno
                          , p.ciudad
                          , p.subdivision
                          , p.pais
                          , p.fecha_comienzo
                          , p.fecha_finale
                          FROM public.pers_view p
                          LEFT JOIN public.participante_composicion pc
                            ON pc.part_id = p.part_id   
                          WHERE p.""" + tipo_lugar + """ ~* :nom
                            AND p.estado='PUBLICADO' """
    if local_params['year_from'] is not None or local_params['year_to'] is not None:
        query_string += """AND EXTRACT(YEAR FROM (p.fecha_comienzo_insert).d) 
                            BETWEEN :year_from AND :year_to """
    if local_params['contains'] is not None and local_params['contains'] != "":
        query_string += "AND p.coment_part ~* :contains"
    set_years(local_params)
    query = text(query_string)
    parts = con.execute(query, local_params)
    gen_pers_tags(con, parts, result)


def lugar_colectivo_query(con, bind_params, result, tipo_lugar):
    local_params = deepcopy(bind_params)
    query_string = """SELECT g.part_id
                           , g.nom_part
                           , g.ciudad
                           , g.subdivision
                           , g.pais
                           , g.fecha_comienzo
                           , g.fecha_finale
                          FROM public.gr_view g 
                          WHERE g.tipo_grupo = 'Colectivo'
                            AND g.""" + tipo_lugar + """ ~* :nom 
                            AND g.estado = 'PUBLICADO' """
    if local_params['year_from'] is not None or local_params['year_to'] is not None:
        query_string += """AND EXTRACT(YEAR FROM (g.fecha_comienzo_insert).d)
                            BETWEEN :year_from AND :year_to """
    if local_params['contains'] is not None and local_params['contains'] != "":
        query_string += "AND g.coment_part ~* :contains"
    set_years(local_params)
    query = text(query_string)
    parts = con.execute(query, local_params)
    gen_grupo_tags(con, parts, result)


def usuario_comp_query(con, bind_params, result):
    local_params = deepcopy(bind_params)
    query_string = """SELECT c.composicion_id
                            , public.get_fecha(c.fecha_pub) fecha_pub
                            ,c.nom_tit
                            ,c.nom_alt
                          FROM public.composicion c
                          JOIN public.usuario u
                            ON u.usuario_id = c.cargador_id
                          WHERE u.nom_usuario ~* :nom 
                          AND c.estado = 'PUBLICADO' """
    if local_params['year_from'] is not None or local_params['year_to'] is not None:
        query_string += """AND EXTRACT(YEAR FROM (fecha_pub).d)
                            BETWEEN :year_from AND :year_to """
    if local_params['contains'] is not None and local_params['contains'] != "":
        query_string += "AND texto ~* :contains"
    set_years(local_params)
    query = text(query_string)
    comps = con.execute(query, local_params)
    gen_comp_tags(con, comps, result)


def usuario_autor_query(con, bind_params, result):
    local_params = deepcopy(bind_params)
    query_string = """SELECT p.part_id
                          , p.nom_part
                          , p.seudonimo
                          , p.nom_paterno
                          , p.nom_materno
                          , p.ciudad
                          , p.subdivision
                          , p.pais
                          , p.fecha_comienzo
                          , p.fecha_finale
                          FROM public.pers_view p 
                          JOIN public.usuario u
                            ON p.cargador_id = u.usuario_id
                          LEFT JOIN public.participante_composicion pc
                            ON pc.part_id = p.part_id   
                          WHERE u.nom_usuario ~* :nom
                            AND p.estado='PUBLICADO' """
    if local_params['year_from'] is not None or local_params['year_to'] is not None:
        query_string += """AND EXTRACT(YEAR FROM (p.fecha_comienzo_insert).d) 
                            BETWEEN :year_from AND :year_to """
    if local_params['contains'] is not None and local_params['contains'] != "":
        query_string += "AND p.coment_part ~* :contains"
    set_years(local_params)
    query = text(query_string)
    parts = con.execute(query, local_params)
    gen_pers_tags(con, parts, result)


def usuario_colectivo_query(con, bind_params, result):
    local_params = deepcopy(bind_params)
    query_string = """SELECT g.part_id
                           , g.nom_part
                           , g.ciudad
                           , g.subdivision
                           , g.pais
                           , g.fecha_comienzo
                           , g.fecha_finale
                          FROM public.gr_view g 
                          JOIN public.usuario u
                            ON u.usuario_id =  g.cargador_id
                          WHERE g.tipo_grupo = 'Colectivo'
                            AND u.nom_usuario ~* :nom 
                            AND g.estado = 'PUBLICADO' """
    if local_params['year_from'] is not None or local_params['year_to'] is not None:
        query_string += """AND EXTRACT(YEAR FROM (g.fecha_comienzo_insert).d)
                            BETWEEN :year_from AND :year_to """
    if local_params['contains'] is not None and local_params['contains'] != "":
        query_string += "AND g.coment_part ~* :contains"
    set_years(local_params)
    query = text(query_string)
    parts = con.execute(query, local_params)
    gen_grupo_tags(con, parts, result)


def genero_autor_query(con, bind_params, result):
    local_params = deepcopy(bind_params)
    query_string = """SELECT p.part_id
                          , p.nom_part
                          , p.seudonimo
                          , p.nom_paterno
                          , p.nom_materno
                          , p.ciudad
                          , p.subdivision
                          , p.pais
                          , p.fecha_comienzo
                          , p.fecha_finale
                          FROM public.pers_view p 
                          LEFT JOIN public.participante_composicion pc
                            ON pc.part_id = p.part_id   
                          WHERE p.genero ~* :nom
                            AND p.estado='PUBLICADO' """
    if local_params['year_from'] is not None or local_params['year_to'] is not None:
        query_string += """AND EXTRACT(YEAR FROM (p.fecha_comienzo_insert).d) 
                            BETWEEN :year_from AND :year_to """
    if local_params['contains'] is not None and local_params['contains'] != "":
        query_string += "AND p.coment_part ~* :contains"
    set_years(local_params)
    query = text(query_string)
    parts = con.execute(query, local_params)
    gen_pers_tags(con, parts, result)


def instrumento_query(con, bind_params, result):
    local_params = deepcopy(bind_params)
    query_string = """SELECT c.composicion_id
                            , get_fecha(c.fecha_pub) fecha_pub
                            ,c.nom_tit
                            ,c.nom_alt
                          FROM public.composicion c
                          JOIN public.pista_son p
                            ON p.composicion_id = c.composicion_id
                          JOIN public.participante_pista_son pps
                            ON pps.pista_son_id = p.pista_son_id
                          JOIN public.instrumento i
                            ON i.instrumento_id = pps.instrumento_id
                          WHERE i.nom_inst ~* :nom 
                            AND c.estado = 'PUBLICADO' """
    if local_params['year_from'] is not None or local_params['year_to'] is not None:
        query_string += """AND EXTRACT(YEAR FROM (p.fecha_grab).d)
                            BETWEEN :year_from AND :year_to """
    if local_params['contains'] is not None and local_params['contains'] != "":
        query_string += "AND p.coment_pista_son ~* :contains"
    set_years(local_params)
    query = text(query_string)
    comps = con.execute(query, local_params)
    gen_comp_tags(con, comps, result)


def idioma_query(con, bind_params, result):
    local_params = deepcopy(bind_params)
    query_string = """SELECT c.composicion_id
                            ,get_fecha(c.fecha_pub) fecha_pub
                            ,c.nom_tit
                            ,c.nom_alt 
                          FROM public.composicion c
                          JOIN public.idioma_composicion ic
                            ON ic.composicion_id = c.composicion_id
                          JOIN public.idioma i
                            ON i.idioma_id = ic.idioma_id  
                          WHERE i.nom_idioma ~* :nom 
                            AND c.estado = 'PUBLICADO'"""
    if local_params['year_from'] is not None or local_params['year_to'] is not None:
        query_string += """AND EXTRACT(YEAR FROM (c.fecha_pub).d)
                            BETWEEN :year_from AND :year_to """
    if local_params['contains'] is not None and local_params['contains'] != "":
        query_string += "AND texto ~* :contains"
    set_years(local_params)
    query = text(query_string)
    comps = con.execute(query, local_params)
    gen_comp_tags(con, comps, result)


def interp_query(con, bind_params, result):
    local_params = deepcopy(bind_params)
    query_string = """SELECT c.composicion_id
                            ,get_fecha(c.fecha_pub) fecha_pub
                            ,c.nom_tit
                            ,c.nom_alt 
                          FROM public.composicion c
                          JOIN public.pista_son ps
                            ON ps.composicion_id = c.composicion_id
                          JOIN public.participante_pista_son pps
                            ON pps.pista_son_id = ps.pista_son_id
                          JOIN public.persona p
                            ON p.part_id = pps.part_id
                          WHERE (p.nom_part ~* :nom
                            OR p.seudonimo ~* :nom
                            OR p.nom_materno ~* :nom
                            OR p.nom_paterno ~* :nom) 
                           AND pps.rol_pista_son = 'Interpretación musical' 
                           AND c.estado = 'PUBLICADO' """
    if local_params['year_from'] is not None or local_params['year_to'] is not None:
        query_string += """AND EXTRACT(YEAR FROM (p.fecha_comienzo).d)
                            BETWEEN :year_from AND :year_to """
    if local_params['contains'] is not None and local_params['contains'] != "":
        query_string += "AND p.coment_part ~* :contains"
    set_years(local_params)
    query = text(query_string)
    comps = con.execute(query, local_params)
    gen_comp_tags(con, comps, result)


def comp_autor_view(con, part_id):
    # query all compositions including those made by this artist when in a colectivo
    composicion_query = text("""SELECT c.composicion_id
                                     , c.nom_tit
                                     , c.nom_alt
                                     , public.get_fecha(c.fecha_pub) fecha_pub
                                  FROM public.persona pers
                                  LEFT JOIN public.persona_grupo pa
                                    ON pers.part_id = pa.persona_id
                                  JOIN public.participante_composicion pc
                                    ON pc.part_id = pa.grupo_id
                                    OR pc.part_id = pers.part_id
                                  JOIN public.composicion c
                                    ON c.composicion_id = pc.composicion_id
                                  WHERE pers.part_id=:part_id
                                  AND c.estado = 'PUBLICADO'""")
    comps = con.execute(composicion_query, part_id=part_id)
    comps_arr = [(res, con.execute(autors_comps_query(), comp_id=res.composicion_id)) for res in comps]
    return comps_arr


def pers_grupo_view(con, part_id):
    # get the list of artists in that colectivo
    author_query = text("""SELECT p.part_id
                                , p.nom_part
                                , p.nom_paterno
                                , p.seudonimo
                                , p.pais 
                                FROM public.grupo a
                                JOIN public.persona_grupo pa
                                  ON a.part_id = pa.grupo_id
                                JOIN public.pers_view p
                                  ON p.part_id = pa.persona_id 
                                AND a.part_id=:part_id
                                and p.estado = 'PUBLICADO'""")
    return [res for res in con.execute(author_query, part_id=part_id)]


def comp_grupo_view(con, part_id):
    # list of composicions by this grupo
    composicion_query = text("""SELECT c.composicion_id
                                     , c.nom_tit
                                     , c.nom_alt
                                     , get_fecha(c.fecha_pub)
                                  FROM public.composicion c
                                  JOIN public.participante_composicion pc 
                                  ON pc.composicion_id = c.composicion_id
                                  WHERE pc.part_id=:part_id
                                    AND c.estado = 'PUBLICADO' """)
    comps = con.execute(composicion_query, part_id=part_id)
    comps_arr = [(res, con.execute(autors_comps_query(), comp_id=res.composicion_id)) for res in comps]
    return comps_arr


def comp_view_query(con, comp_id):
    autors = con.execute(autors_comps_query(), comp_id=comp_id)
    composicion_query = text("""SELECT c.nom_tit
                                     , c.nom_alt
                                     , public.get_fecha(fecha_pub) fecha_pub
                                     , g.nom_part 
                                     , p.nom_part
                                     , p.seudonimo
                                     , p.nom_paterno
                                     , s.serie_id
                                     , s.nom_serie
                                     FROM public.composicion c
                                     JOIN public.participante_composicion pc
                                       ON c.composicion_id = pc.composicion_id
                                     LEFT JOIN public.pista_son ps
                                       ON ps.composicion_id = c.composicion_id
                                     LEFT JOIN public.serie s
                                       ON s.serie_id = ps.serie_id   
                                     LEFT JOIN public.pers_view p
                                       ON p.part_id = pc.part_id
                                     LEFT JOIN public.gr_view g
                                       ON g.part_id = pc.part_id
                                     WHERE c.composicion_id=:comp_id 
                                     AND c.estado = 'PUBLICADO' """)
    comp = con.execute(composicion_query, comp_id=comp_id).first()
    return (comp, autors)


def pista_archivo_view(con, comp_id):
    # query all pista son associated with that composicion and return first flac archivo associated with each one
    pista_query = text("""SELECT DISTINCT ON
                             (a.pista_son_id) 
                             a.nom_archivo
                           , a.archivo_id
                           , a.codec
                           , ps.pista_son_id
                           , public.get_fecha(ps.fecha_grab) fecha_grab
                           , l.ciudad
                           , l.subdivision
                           , l.pais
                           , s.nom_serie
                      FROM public.pista_son ps
                      JOIN public.archivo a
                        ON a.pista_son_id = ps.pista_son_id
                      LEFT JOIN public.serie s
                        ON s.serie_id = ps.serie_id
                      LEFT JOIN public.lugar l
                        ON l.lugar_id = ps.lugar_id
                        WHERE ps.composicion_id=:comp_id
                          AND ps.estado = 'PUBLICADO' """)
    result = con.execute(pista_query, comp_id=comp_id)
    inst_query = text("""SELECT g.part_id gr_id
                               , p.part_id pers_id 
                               , g.nom_part nom_part_ag
                               , p.nom_part
                               , p.seudonimo
                               , p.nom_paterno
                               , i.nom_inst
                               , pps.rol_pista_son                         
                          FROM public.participante_pista_son pps
                          LEFT JOIN public.persona p
                            ON p.part_id = pps.part_id
                          LEFT JOIN public.grupo g
                            ON g.part_id = pps.part_id     
                          JOIN public.instrumento i
                            ON i.instrumento_id = pps.instrumento_id     
                            WHERE pps.pista_son_id=:pista_id """)
    result_arr = [(res, con.execute(inst_query, pista_id=res.pista_son_id)) for res in result]
    return result_arr


def serie_view(con, serie_id):
    serie_query = text("""SELECT nom_serie
                                ,giro
                             FROM public.serie s
                             WHERE serie_id=:serie_id """)
    return con.execute(serie_query, serie_id=serie_id).first()


def comp_serie_view(con, serie_id):
        query = text("""SELECT c.composicion_id
                               , c.nom_tit
                               , c.nom_alt
                               , public.get_fecha(c.fecha_pub) fecha_pub
                              FROM public.composicion c
                              JOIN public.pista_son ps
                                ON ps.composicion_id = c.composicion_id  
                              WHERE ps.serie_id = :serie_id
                              AND ps.estado = 'PUBLICADO'""")
        comps = con.execute(query, serie_id=serie_id)
        comps_arr = [(res, con.execute(autors_comps_query(), comp_id=res.composicion_id)) for res in comps]
        return comps_arr
