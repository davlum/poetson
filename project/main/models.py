from sqlalchemy import text
import time


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


def genero_tags(con, pista_ids):
    generos = text("""SELECT gm.nom_gen_mus, COUNT(gp.gen_mus_id) count
                           FROM public.genero_musical gm
                           JOIN public.genero_pista gp
                             ON gm.gen_mus_id = gp.gen_mus_id
                           WHERE gp.pista_son_id IN :pista_ids
                           GROUP BY gm.nom_gen_mus""")
    return con.execute(generos, pista_ids=pista_ids)


def usuario_comp_tags(con, comp_ids):
    comps = text("""SELECT u.nom_usuario, COUNT(c.composicion_id) count
                           FROM public.usuario u
                           JOIN public.composicion c
                             ON u.usuario_id = c.cargador_id    
                           WHERE c.composicion_id IN :comp_ids
                           GROUP BY u.nom_usuario""")
    return con.execute(comps, comp_ids=comp_ids)


def usuario_pista_tags(con, pista_ids):
    pistas = text("""SELECT u.nom_usuario, COUNT(c.pista_son_id) count
                           FROM public.usuario u
                           JOIN public.pista_son c
                             ON u.usuario_id = c.cargador_id    
                           WHERE c.pista_son_id IN :pista_ids
                           GROUP BY u.nom_usuario""")
    return con.execute(pistas, pista_ids=pista_ids)


def usuario_persona_tags(con, part_ids):
    personas = text("""SELECT u.nom_usuario, COUNT(p.part_id) count
                           FROM public.usuario u
                           JOIN public.persona p
                             ON u.usuario_id = p.cargador_id    
                           WHERE p.part_id IN :part_ids
                           GROUP BY u.nom_usuario""")
    return con.execute(personas, part_ids=part_ids)


def usuario_grupo_tags(con, part_ids):
    grupos = text("""SELECT u.nom_usuario, COUNT(g.part_id) count
                           FROM public.usuario u
                           JOIN public.grupo g
                             ON u.usuario_id = g.cargador_id    
                           WHERE g.part_id IN :part_ids
                           GROUP BY u.nom_usuario""")
    return con.execute(grupos, part_ids=part_ids)


def set_years(binds_params, year_from, year_to):
    if year_from is None:
        year_from = 500
    binds_params['year_from'] = year_from
    if year_to is None:
        year_to = int(time.strftime('%Y'))+1
    binds_params['year_to'] = year_to


def autor_query(con, nom, year_from, year_to, contains):
    bind_params = {}
    bind_params['nom'] = nom
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
    if year_from is not None or year_to is not None:
        query_string += """AND EXTRACT(YEAR FROM (p.fecha_comienzo_insert).d) BETWEEN :year_from AND :year_to """
    if contains is not None and contains != "":
        query_string += "AND p.coment_part ~* :contains"
        bind_params['contains'] = contains
    set_years(bind_params, year_from, year_to)
    query = text(query_string)
    return con.execute(query, bind_params)


def colectivo_query(con, nom, year_from, year_to, contains):
    bind_params = {}
    bind_params['nom'] = nom
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
    if year_from is not None or year_to is not None:
        query_string += """AND EXTRACT(YEAR FROM (g.fecha_comienzo_insert).d)
                            BETWEEN :year_from AND :year_to """
    if contains is not None and contains != "":
        query_string += "AND g.coment_part ~* :contains"
        bind_params['contains'] = contains
    set_years(bind_params, year_from, year_to)
    query = text(query_string)
    return con.execute(query, bind_params)


def composicion_query(con, nom, year_from, year_to, contains):
    bind_params = {}
    bind_params['nom'] = nom
    query_string = """SELECT * FROM public.composicion
                          WHERE nom_tit ~* :nom 
                          OR nom_alt ~* :nom 
                          and estado = 'PUBLICADO' """
    if year_from is not None or year_to is not None:
        query_string += """AND EXTRACT(YEAR FROM (fecha_pub).d)
                            BETWEEN :year_from AND :year_to """
    if contains is not None and contains != "":
        query_string += "AND texto ~* :contains"
        bind_params['contains'] = contains
    set_years(bind_params, year_from, year_to)
    query = text(query_string)
    comps = con.execute(query, bind_params)
    comps_arr = [(res, con.execute(autors_comps_query(), comp_id=res.composicion_id)) for res in comps]
    comp_ids = tuple([res[0].composicion_id for res in comps_arr])
    temas = tema_tags(con, comp_ids)
    idiomas = idioma_tags(con, comp_ids)
    usuarios = usuario_comp_tags(con, comp_ids)
    return comps_arr, temas, idiomas, usuarios


def serie_query(con, nom, contains):
    bind_params = {}
    bind_params['nom'] = nom
    query_string = """SELECT * 
                        FROM public.serie
                          WHERE nom_serie ~* :nom """
    if contains is not None and contains != "":
        query_string += "AND giro ~* :contains"
        bind_params['contains'] = contains
    query = text(query_string)
    return con.execute(query, bind_params)


def tema_query(con, nom, year_from, year_to, contains):
    bind_params = {}
    bind_params['nom'] = nom
    query_string = """SELECT * FROM public.composicion c
                          JOIN public.tema_composicion tc
                            ON c.composicion_id = tc.composicion_id
                          JOIN public.tema t
                            ON t.tema_id = tc.tema_id  
                          WHERE t.nom_tema ~* :nom  """
    if year_from is not None or year_to is not None:
        query_string += """AND EXTRACT(YEAR FROM (c.fecha_pub).d)
                            BETWEEN :year_from AND :year_to """
    if contains is not None and contains != "":
        query_string += "AND c.texto ~* :contains"
        bind_params['contains'] = contains
    set_years(bind_params, year_from, year_to)
    query = text(query_string)
    return con.execute(query, bind_params)


def genero_query(con, nom, year_from, year_to, contains):
    bind_params = {}
    bind_params['nom'] = nom
    query_string = """SELECT * FROM public.composicion c
                          JOIN public.pista_son p
                            ON p.composicion_id = c.composicion_id
                          JOIN public.genero_pista gp
                            ON gp.pista_son_id = p.pista_son_id
                          JOIN public.genero_musical gm
                            ON gm.gen_mus_id = gp.gen_mus_id  
                          WHERE gm.nom_gen_mus ~* :nom """
    if year_from is not None or year_to is not None:
        query_string += """AND EXTRACT(YEAR FROM (p.fecha_grab).d)
                            BETWEEN :year_from AND :year_to """
    if contains is not None and contains != "":
        query_string += "AND p.coment_pista_son ~* :contains"
        bind_params['contains'] = contains
    set_years(bind_params, year_from, year_to)
    query = text(query_string)
    return con.execute(query, bind_params)


def instrumento_query(con, nom, year_from, year_to, contains):
    bind_params = {}
    bind_params['nom'] = nom
    query_string = """SELECT * FROM public.composicion c
                          JOIN public.pista_son p
                            ON p.composicion_id = c.composicion_id
                          JOIN public.participante_pista_son pps
                            ON pps.pista_son_id = p.pista_son_id
                          JOIN public.instrumento i
                            ON i.instrumento_id = pps.instrumento_id
                          WHERE i.nom_inst ~* :nom """
    if year_from is not None or year_to is not None:
        query_string += """AND EXTRACT(YEAR FROM (p.fecha_grab).d)
                            BETWEEN :year_from AND :year_to """
    if contains is not None and contains != "":
        query_string += "AND p.coment_pista_son ~* :contains"
        bind_params['contains'] = contains
    set_years(bind_params, year_from, year_to)
    query = text(query_string)
    return con.execute(query, bind_params)


def idioma_query(con, nom, year_from, year_to, contains):
    bind_params = {}
    bind_params['nom'] = nom
    query_string = """SELECT * FROM public.composicion c
                          JOIN public.idioma_composicion ic
                            ON ic.composicion_id = c.composicion_id
                          JOIN public.idioma i
                            ON i.idioma_id = ic.idioma_id  
                          WHERE i.nom_idioma ~* :nom """
    if year_from is not None or year_to is not None:
        query_string += """AND EXTRACT(YEAR FROM (c.fecha_pub).d)
                            BETWEEN :year_from AND :year_to """
    if contains is not None and contains != "":
        query_string += "AND texto ~* :contains"
        bind_params['contains'] = contains
    set_years(bind_params, year_from, year_to)
    query = text(query_string)
    return con.execute(query, bind_params)


def interp_query(con, nom, year_from, year_to, contains):
    bind_params = {}
    bind_params['nom'] = nom
    query_string = """SELECT * FROM public.composicion c
                          JOIN public.pista_son ps
                            ON ps.composicion_id = c.composicion_id
                          JOIN public.participante_pista_son pps
                            ON pps.pista_son_id = ps.pista_son_id
                          JOIN public.persona p
                            ON p.part_id = pps.part_id
                          WHERE p.nom_part ~* :nom
                            OR p.seudonimo ~* :nom
                            OR p.nom_materno ~* :nom
                            OR p.nom_paterno ~* :nom 
                           AND pps.rol_pista_son = 'Interpretación musical' """
    if year_from is not None or year_to is not None:
        query_string += """AND EXTRACT(YEAR FROM (p.fecha_comienzo).d)
                            BETWEEN :year_from AND :year_to """
    if contains is not None and contains != "":
        query_string += "AND p.coment_part ~* :contains"
        bind_params['contains'] = contains
    set_years(bind_params, year_from, year_to)
    query = text(query_string)
    return con.execute(query, bind_params)


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
    return con.execute(author_query, part_id=part_id)


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
                        ON l.lugar_id = ps.lugar_interp
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
                            ON g.part_id = p.part_id     
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
                               , c.fecha_pub
                              FROM public.composicion c
                              JOIN public.pista_son ps
                                ON ps.composicion_id = c.composicion_id  
                              WHERE ps.serie_id = :serie_id
                              AND ps.estado = 'PUBLICADO'""")
        comps = con.execute(query, serie_id=serie_id)
        comps_arr = [(res, con.execute(autors_comps_query(), comp_id=res.composicion_id)) for res in comps]
        return comps_arr
