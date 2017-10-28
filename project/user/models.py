from sqlalchemy import text
from flask import session
from project.util import current_pers, current_gr, parse_fecha, get_fecha
from project.user.forms import OrgForm, DynamicGenMusForm, DynamicAuthorForm, DynamicInterpForm, \
    DynamicLangForm, DynamicThemeForm


# Queries for admin view
def get_users(con):
    query = text("""SELECT nom_usuario, COALESCE(gr_email, pers_email) email, permiso, fecha_registro, prohibido FROM public.usuario 
                      WHERE permiso <> 'ADMIN'""")
    return con.execute(query)


# Queries for InfoForm
def populate_grupos_form(con):
    # List of all agregates
    gr_query = text("""SELECT part_id, nom_part FROM public.grupo;""")
    gr_result = con.execute(gr_query)
    gr_arr = [(str(res.part_id), res.nom_part) for res in gr_result]
    gr_arr.insert(0, ("0", 'Ninguno'))
    return gr_arr


def populate_tipo_grupos_form(con):
    # Get List of possible agregate types
    tipo_grupo_query = text("""SELECT nom_tipo_grupo nom FROM public.tipo_grupo;""")
    tipo_grupo_result = con.execute(tipo_grupo_query)
    tipo_grupo_arr = [(res.nom, res.nom) for res in tipo_grupo_result]
    return tipo_grupo_arr


def populate_genero_form(con):
    # Get List of possible genders
    gender_query = text("""SELECT nom_genero FROM public.genero_persona;""")
    gender_result = con.execute(gender_query)
    gender_arr = [(str(res.nom_genero), res.nom_genero) for res in gender_result]
    gender_arr.sort(key=lambda tup: tup[1])
    return gender_arr


def populate_pais_form(con):
    # Get List of countries
    country_query = text("""SELECT nom_pais FROM public.pais;""")
    country_result = con.execute(country_query)
    country_arr = [(res.nom_pais, res.nom_pais) for res in country_result]
    return country_arr


# Queries for AddCompForm
def populate_part_id_form(con):
    # Get list of all artists
    part_id_query = text("""SELECT part_id, nom_part FROM public.part_view""")
    part_id_result = con.execute(part_id_query)
    part_id_arr = [(str(res.part_id), res.nom_part) for res in part_id_result]
    return part_id_arr


def populate_rol_comp_form(con):
    # list of roles in a composicion
    rol_query = text("""SELECT nom_rol_comp FROM public.rol_composicion""")
    rol_result = con.execute(rol_query)
    rol_arr = [(res.nom_rol_comp, res.nom_rol_comp) for res in rol_result]
    return rol_arr


def populate_idiomas_form(con):
    # list of languages
    idioma_query = text("""SELECT idioma_id, nom_idioma FROM public.idioma""")
    idioma_result = con.execute(idioma_query)
    idioma_arr = [(str(res.idioma_id), res.nom_idioma) for res in idioma_result]
    return idioma_arr


def populate_album_form(con):
    # List of albums
    album_query = text("""SELECT * FROM public.album""")
    album_result = con.execute(album_query)
    album_arr = [(str(res.album_id), res.nom_album) for res in album_result]
    return album_arr


def populate_temas_form(con):
    tema_query = text("""SELECT tema_id, nom_tema FROM public.tema""")
    tema_result = con.execute(tema_query)
    tema_arr = [(str(res.tema_id), res.nom_tema) for res in tema_result]
    return tema_arr


def populate_comps_form(con):
    # List of composicion
    comp_query = text("""SELECT composicion_id, nom_tit FROM public.composicion""")
    comp_result = con.execute(comp_query)
    comp_arr = [(str(res.composicion_id), res.nom_tit) for res in comp_result]
    return comp_arr


# Queries for the AddTrackForm
def populate_instrumento_form(con):
    # Get list of instruments
    instrumento_query = text("""SELECT instrumento_id, nom_inst FROM public.instrumento""")
    instrumento_result = con.execute(instrumento_query)
    instrumento_arr = [(str(res.instrumento_id), res.nom_inst) for res in instrumento_result]
    return instrumento_arr


def populate_rol_pista_form(con):
    # List of possible roles in a pista_son
    rol_query = text("""SELECT nom_rol_pista FROM public.rol_pista_son""")
    rol_result = con.execute(rol_query)
    rol_arr = [(res.nom_rol_pista, res.nom_rol_pista) for res in rol_result]
    return rol_arr


def populate_gen_mus_form(con):
    # List of possible genres of music
    gen_mus_query = text("""SELECT gen_mus_id, nom_gen_mus FROM public.genero_musical""")
    gen_mus_result = con.execute(gen_mus_query)
    gen_mus_arr = [(str(res.gen_mus_id), res.nom_gen_mus) for res in gen_mus_result]
    return gen_mus_arr


def populate_medio_form(con):
    # List of possible mediums of origin for the tracks
    medio_query = text("""SELECT nom_medio FROM public.medio;""")
    medio_result = con.execute(medio_query)
    medio_arr = [(res.nom_medio, res.nom_medio) for res in medio_result]
    return medio_arr


def populate_serie_form(con):
    # list of series
    serie_query = text("""SELECT serie_id, nom_serie FROM public.serie;""")
    serie_result = con.execute(serie_query)
    serie_arr = [(str(res.serie_id), res.nom_serie) for res in serie_result]
    return serie_arr


def populate_cob_form(con):
    cob_query = text("""SELECT cobertura_lic_id
                             , licencia_cobertura
                          FROM public.cobertura_licencia""")
    cob_result = con.execute(cob_query)
    cob_arr = [(str(res.cobertura_lic_id), res.licencia_cobertura) for res in cob_result]
    return cob_arr


def insert_lugar(con, form):
    query_lugar = text("""INSERT INTO public.lugar(ciudad
                                                , subdivision
                                                , pais) 
                                              VALUES (strip(:ciudad)
                                              , strip(:subdivision)
                                              , :pais)
                                            RETURNING lugar_id""")
    result_lugar = con.execute(query_lugar
                               , ciudad=form.ciudad.data
                               , subdivision=form.subdivision.data
                               , pais=form.pais.data).first()[0]
    return result_lugar


def update_lugar(con, form, lugar_id):
    query_lugar = text("""UPDATE public.lugar SET ciudad=strip(:ciudad)
                                                , subdivision=strip(:subdivision)
                                                , pais=:pais
                                             WHERE lugar_id=:lugar_id""")
    con.execute(query_lugar, ciudad=form.ciudad.data, subdivision=form.subdivision.data
                , pais=form.pais.data, lugar_id=lugar_id)


def add_info_choices(con, form):
    for sub_form in form.org_form:
        sub_form.grupo_id.choices = populate_grupos_form(con)
    form.tipo_grupo.choices = populate_tipo_grupos_form(con)
    form.genero.choices = populate_genero_form(con)
    form.pais.choices = populate_pais_form(con)


def add_pista_choices(con, form):
    for sub_form in form.gen_mus_form:
        gen_mus = populate_gen_mus_form(con)
        gen_mus.insert(0, ("0", 'Ninguno'))
        sub_form.gen_mus_id.choices = gen_mus
    for sub_form in form.interp_form:
        sub_form.part_id.choices = populate_part_id_form(con)
        sub_form.rol_pista_son.choices = populate_rol_pista_form(con)
        sub_form.instrumento_id.choices = populate_instrumento_form(con)
    form.medio.choices = populate_medio_form(con)
    series = populate_serie_form(con)
    series.insert(0, ("0", 'Ninguno'))
    form.serie_id.choices = series
    form.comp_id.choices = populate_comps_form(con)
    form.pais.choices = populate_pais_form(con)
    form.pais_cob.choices = populate_pais_form(con)
    form.cobertura.choices = populate_cob_form(con)


def add_comp_choices(con, form):
    for sub_form in form.part_id_form:
        parts = populate_part_id_form(con)
        sub_form.part_id.choices = parts
        sub_form.rol_composicion.choices = populate_rol_comp_form(con)
    for sub_form in form.idioma_form:
        idiomas = populate_idiomas_form(con)
        idiomas.insert(0, ("0", "Ninguno"))
        sub_form.idioma_id.choices = idiomas
    for sub_form in form.tema_form:
        temas = populate_temas_form(con)
        temas.insert(0, ("0", 'Ninguno'))
        sub_form.tema_id.choices = temas
    comps = populate_comps_form(con)
    comps.insert(0, ("0", 'Ninguno'))
    form.composicion_id.choices = comps
    form.cobertura.choices = populate_cob_form(con)
    form.pais_cob.choices = populate_pais_form(con)


def add_part_choices(con, form):
    for sub_form in form.org_form:
        sub_form.grupo_id.choices = populate_grupos_form(con)
    form.tipo_grupo.choices = populate_tipo_grupos_form(con)
    form.genero.choices = populate_genero_form(con)
    form.pais.choices = populate_pais_form(con)
    form.pais_muer.choices = populate_pais_form(con)


def populate_pers_grupo(form, result):
    if result.rowcount == 0:
        org_form = OrgForm()
        org_form.grupo_id = "0"
        org_form.titulo = None
        org_form.fecha_comienzo = None
        org_form.fecha_finale = None

        form.org_form.append_entry(org_form)

    for res in result:
        org_form = OrgForm()
        org_form.grupo_id = str(res.grupo_id)
        org_form.titulo = res.titulo
        org_form.fecha_comienzo = res.fecha_comienzo
        org_form.fecha_finale = res.fecha_finale

        form.org_form.append_entry(org_form)


def insert_archivo(con, audio_file, filename, pista_id):
    query = text("""INSERT into public.archivo(nom_archivo
                                             , pista_son_id
                                             , duracion
                                             , abr
                                             , canales
                                             , codec
                                             , frecuencia) 
                                         VALUES(:nom_archivo
                                              , :pista_son_id
                                              , :duracion
                                              , :abr
                                              , :canales
                                              , :codec
                                              , :frecuencia)
                                              RETURNING archivo_id""")
    result = con.execute(query, nom_archivo=filename
                              , pista_son_id=pista_id
                              , duracion=int(audio_file.info.length)
                              , abr=audio_file.info.bitrate
                              , canales=audio_file.info.channels
                              , codec=audio_file.__class__.__name__
                              , frecuencia=audio_file.info.sample_rate).first()[0]
    return result


def populate_lugar(con, form, lugar_id):
    query = text("""SELECT * from public.lugar WHERE lugar_id=:lugar_id""")
    lugar = con.execute(query, lugar_id=lugar_id).first()
    form.ciudad.data = lugar.ciudad
    form.subdivision.data = lugar.subdivision
    form.pais.data = lugar.pais


# Queries for the info view
def populate_info(con, form):
    # populate the form
    if session['is_person']:
        user = current_pers(con, session['email'])
        pers_org_query = text("""SELECT pa.grupo_id
                                      , public.get_fecha(pa.fecha_comienzo) fecha_comienzo
                                      , public.get_fecha(pa.fecha_finale) fecha_finale
                                      , pa.titulo
                                      FROM public.persona_grupo pa
                                      WHERE pa.persona_id=:id""")
        pers_org_result = con.execute(pers_org_query, id=session['id'])
        populate_pers_grupo(form, pers_org_result)

        form.nom_part.data = user.nom_part
        form.seudonimo.data = user.seudonimo
        form.fecha_comienzo.data = user.fecha_comienzo
        form.nom_paterno.data = user.nom_paterno
        form.nom_materno.data = user.nom_materno
        form.genero.data = user.genero
    else:
        user = current_gr(con, session['email'])
        form.nom_part_gr.data = user.nom_part
        form.fecha_comienzo.data = user.fecha_comienzo
        form.tipo_grupo.data = user.tipo_grupo
    form.coment_part.data = user.coment_part
    form.sitio_web.data = user.sitio_web
    form.direccion.data = user.direccion
    form.telefono.data = user.telefono
    form.ciudad.data = user.ciudad
    form.subdivision.data = user.subdivision
    form.pais.data = user.pais


def estado_serie(con, obra_id, estado, mod_id):
    query = text("""UPDATE public.serie SET estado=:estado, mod_id=:mod_id WHERE serie_id=:obra_id""")
    con.execute(query, obra_id=obra_id, estado=estado, mod_id=mod_id)


def estado_comp(con, obra_id, estado, mod_id):
    query = text("""UPDATE public.composicion SET estado=:estado, mod_id=:mod_id WHERE composicion_id=:obra_id""")
    con.execute(query, obra_id=obra_id, estado=estado, mod_id=mod_id)
    query = text("""UPDATE public.participante_composicion SET estado=:estado, mod_id=:mod_id WHERE composicion_id=:obra_id""")
    con.execute(query, obra_id=obra_id, estado=estado, mod_id=mod_id)


def estado_pista(con, obra_id, estado, mod_id):
    query = text("""UPDATE public.pista_son SET estado=:estado, mod_id=:mod_id WHERE pista_son_id=:obra_id""")
    con.execute(query, obra_id=obra_id, estado=estado, mod_id=mod_id)
    query = text("""UPDATE public.participante_pista_son SET estado=:estado, mod_id=:mod_id WHERE pista_son_id=:obra_id""")
    con.execute(query, obra_id=obra_id, estado=estado, mod_id=mod_id)


def estado_pers(con, obra_id, estado, mod_id):
    query = text("""UPDATE public.persona SET estado=:estado, mod_id=:mod_id WHERE part_id=:obra_id""")
    con.execute(query, obra_id=obra_id, estado=estado, mod_id=mod_id)


def estado_grupo(con, obra_id, estado, mod_id):
    query = text("""UPDATE public.grupo SET estado=:estado, mod_id=:mod_id WHERE part_id=:obra_id""")
    con.execute(query, obra_id=obra_id, estado=estado, mod_id=mod_id)


def upsert_pers_grupos(con, form, usuario_id, pers_id, update=False):
        used_ids = []
        for entry in form.org_form.entries:
            gr_id = int(entry.data['grupo_id'])
            if gr_id != 0 and gr_id not in used_ids:
                used_ids.append(gr_id)
                pers_grupo_insert = text("""INSERT INTO public.persona_grupo(persona_id
                                                                          , grupo_id
                                                                          , fecha_comienzo
                                                                          , fecha_finale
                                                                          , titulo
                                                                          , cargador_id) 
                                                                      VALUES (:pers_id
                                                                            , :grupo_id
                                                                            , :fecha_comienzo
                                                                            , :fecha_finale
                                                                            , strip(:titulo)
                                                                            , :us_id)
                                          ON CONFLICT (persona_id, grupo_id) DO UPDATE
                                          SET fecha_comienzo=EXCLUDED.fecha_comienzo,
                                              fecha_finale=EXCLUDED.fecha_finale,
                                              titulo=EXCLUDED.titulo,
                                              mod_id=EXCLUDED.cargador_id""")
                con.execute(pers_grupo_insert, pers_id=pers_id
                            , grupo_id=gr_id
                            , fecha_comienzo=parse_fecha(entry.data['fecha_comienzo'])
                            , fecha_finale=parse_fecha(entry.data['fecha_finale'])
                            , titulo=entry.data['titulo']
                            , us_id=usuario_id)
        if update:
            pers_grupos_delete = text("""DELETE FROM public.persona_grupo WHERE persona_id=:id AND
                                      grupo_id NOT IN :used""")
            used_ids.append(0)
            con.execute(pers_grupos_delete, id=usuario_id, used=tuple(used_ids))


def update_info(con, form, usuario_id):
    # Update personal info
    if session['is_person']:
        user_query = text("""UPDATE public.pers_view SET nom_part=strip(:nom_part)
                                                 , seudonimo=strip(:seudonimo)
                                                 , nom_materno=strip(:nom_materno)
                                                 , nom_paterno=strip(:nom_paterno)
                                                 , ciudad=strip(:ciudad)
                                                 , subdivision=strip(:subdivision)
                                                 , pais=strip(:pais)
                                                 , fecha_comienzo_insert=:fecha_comienzo
                                                 , sitio_web=strip(:sitio_web)
                                                 , direccion=strip(:direccion)
                                                 , telefono=strip(:telefono)
                                                 , genero=strip(:genero)
                                                 , coment_part=strip(:coment_part)
                                                 , mod_id=:id
                                                 WHERE part_id=:id;""")
        con.execute(user_query, nom_part=form.nom_part.data
                    , seudonimo=form.seudonimo.data
                    , nom_materno=form.nom_materno.data
                    , nom_paterno=form.nom_paterno.data
                    , ciudad=form.ciudad.data
                    , subdivision=form.subdivision.data
                    , pais=form.pais.data
                    , fecha_comienzo=parse_fecha(form.fecha_comienzo.data)
                    , sitio_web=form.sitio_web.data
                    , direccion=form.direccion.data
                    , telefono=form.telefono.data
                    , genero=form.genero.data
                    , coment_part=form.coment_part.data
                    , id=usuario_id)
        upsert_pers_grupos(con, form, usuario_id, usuario_id, update=True)
    else:
        user_query = text("""UPDATE public.gr_view SET nom_part=strip(:nom_part_gr)
                                                 , ciudad=strip(:ciudad)
                                                 , subdivision=strip(:subdivision)
                                                 , pais=strip(:pais)
                                                 , fecha_comienzo_insert=:fecha_comienzo
                                                 , sitio_web=strip(:sitio_web)
                                                 , direccion=strip(:direccion)
                                                 , telefono=strip(:telefono)
                                                 , coment_part=strip(:coment_part)
                                                 , tipo_grupo=strip(:tipo_grupo)
                                                 , mod_id=:id
                                                 WHERE part_id=:id;""")
        con.execute(user_query, nom_part_gr=form.nom_part_gr.data
                    , ciudad=form.ciudad.data
                    , subdivision=form.subdivision.data
                    , pais=form.pais.data
                    , date_formed=parse_fecha(form.fecha_comienzo.data)
                    , sitio_web=form.sitio_web.data
                    , direccion=form.direccion.data
                    , telefono=form.telefono.data
                    , coment_part=form.coment_part.data
                    , tipo_grupo=form.tipo_grupo.data
                    , id=usuario_id)


def query_archivos(con, pista_id):
    query = text("""SELECT * FROM public.archivo WHERE pista_son_id=:pista_id""")
    return con.execute(query, pista_id=pista_id)


# Queries for the profile view
def query_pers_gr(con, part_id):
    query = text("""SELECT a.nom_part
                             , public.get_fecha(pa.fecha_comienzo) fecha_comienzo
                             , public.get_fecha(pa.fecha_finale) fecha_finale
                             , pa.titulo
                            FROM public.persona_grupo pa
                            JOIN public.grupo a
                              ON pa.grupo_id = a.part_id
                              WHERE pa.persona_id=:id""")
    return con.execute(query, id=part_id)


def query_grupos(con, part_id, permission='EDITOR'):
    if permission == 'EDITOR':
        query = text("""SELECT part_id
                             , nom_part
                             , fecha_comienzo
                             , fecha_finale
                             , ciudad
                             , subdivision
                             , pais
                             FROM public.gr_view
                             WHERE cargador_id=:part_id
                             AND cargador_id <> part_id
                             AND (estado = 'PENDIENTE'
                              OR estado = 'PUBLICADO') """)
        result = con.execute(query, part_id=part_id)
    else:
        query = text("""SELECT a.part_id
                             , a.nom_part
                             , a.fecha_comienzo
                             , a.fecha_finale
                             , a.ciudad
                             , a.subdivision
                             , a.pais
                             , a.estado
                             , a.cargador_id
                             , u.nom_usuario
                             FROM public.gr_view a
                             JOIN public.usuario u
                               ON u.usuario_id = a.cargador_id """)
        result = con.execute(query)
    return [res for res in result]


def query_pers(con, part_id, permission='EDITOR'):
    if permission == 'EDITOR':
        query = text("""SELECT part_id
                             , nom_part
                             , seudonimo
                             , nom_paterno
                             , nom_materno
                             , fecha_comienzo
                             , fecha_finale
                             , ciudad
                             , subdivision
                             , pais
                             FROM public.pers_view
                             WHERE cargador_id=:part_id
                             AND cargador_id <> part_id
                             AND (estado = 'PENDIENTE'
                              OR estado = 'PUBLICADO') """)
        result = con.execute(query, part_id=part_id)
    else:
        query = text("""SELECT p.part_id
                             , p.nom_part
                             , p.seudonimo
                             , p.nom_materno
                             , p.nom_paterno
                             , p.fecha_comienzo
                             , p.fecha_finale
                             , p.ciudad
                             , p.subdivision
                             , p.pais
                             , p.estado
                             , p.cargador_id
                             , u.nom_usuario
                             FROM public.pers_view p
                             JOIN public.usuario u
                               ON u.usuario_id = p.cargador_id """)
        result = con.execute(query)
    return [res for res in result]


def query_comps(con, part_id, permission='EDITOR'):
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
    if permission == 'EDITOR':
        query = text("""SELECT c.composicion_id
                             , c.nom_tit
                             , c.nom_alt
                             , c.estado
                             , public.get_fecha(fecha_pub) fecha_pub
                             FROM public.composicion c
                             WHERE c.cargador_id=:id
                             AND (c.estado = 'PENDIENTE'
                              OR c.estado = 'PUBLICADO') """)
        comps = con.execute(query, id=part_id)
    else:
        query = text("""SELECT c.composicion_id
                             , c.nom_tit
                             , c.nom_alt
                             , public.get_fecha(fecha_pub) fecha_pub
                             , c.estado
                             , u.nom_usuario
                             FROM public.composicion c
                             JOIN public.usuario u 
                               ON c.cargador_id = u.usuario_id""")
        comps = con.execute(query)
    comps_arr = [(res, con.execute(autors_query, comp_id=res.composicion_id)) for res in comps]
    return comps_arr


def query_serie(con, part_id, permission='EDITOR'):
    if permission == 'EDITOR':
        query = text("""SELECT s.serie_id
                             , s.nom_serie
                             , s.ruta_foto
                             , s.giro
                             , s.coment_serie
                             , s.estado
                            FROM public.serie s
                            WHERE s.cargador_id=:part_id
                            AND (s.estado = 'PENDIENTE'
                              OR s.estado = 'PUBLICADO')""")
        return con.execute(query, part_id=part_id)
    else:
        query = text("""SELECT s.serie_id
                             , s.nom_serie
                             , s.ruta_foto
                             , s.giro
                             , s.coment_serie
                             , u.nom_usuario
                             , s.estado
                            FROM public.serie s
                            JOIN public.usuario u 
                              ON s.cargador_id = u.usuario_id""")
        return con.execute(query)


def query_pista(con, part_id, permission='EDITOR'):
    if permission == 'EDITOR':
        query = text("""SELECT c.composicion_id
                             , p.pista_son_id
                             , c.nom_tit
                             , l.ciudad
                             , l.subdivision
                             , l.pais
                             , p.estado
                             , public.get_fecha(p.fecha_grab) fecha_grab
                             FROM public.pista_son p
                             JOIN public.composicion c
                               ON p.composicion_id = c.composicion_id
                             LEFT JOIN public.lugar l
                               ON l.lugar_id = p.lugar_id
                             WHERE p.cargador_id=:part_id
                             AND (p.estado = 'PENDIENTE'
                              OR p.estado = 'PUBLICADO') """)
        return con.execute(query, part_id=part_id)
    else:
        query = text("""SELECT c.composicion_id
                             , p.pista_son_id
                             , c.nom_tit
                             , l.ciudad
                             , l.subdivision
                             , l.pais
                             , public.get_fecha(p.fecha_grab) fecha_grab
                             , p.estado
                             , u.nom_usuario
                             FROM public.pista_son p
                             JOIN public.composicion c
                               ON p.composicion_id = c.composicion_id
                             LEFT JOIN public.lugar l
                               ON  l.lugar_id = P.lugar_id
                             JOIN public.usuario u
                               ON u.usuario_id = p.cargador_id""")
        return con.execute(query)


def update_permiso(con, usuario_id, permiso):
    query = text("""UPDATE public.usuario SET permiso=:permiso WHERE usuario_id=:usuario_id""")
    con.execute(query, permiso=permiso, usuario_id=usuario_id)


def update_prohibido(con, usuario_id, prohibido):
    query = text("""UPDATE public.usuario SET prohibido=:prohibido WHERE usuario_id=:usuario_id""")
    con.execute(query, prohibido=prohibido, usuario_id=usuario_id)


def query_perfil(con, part_id, permission=None):
    perfil_dict = {
        'pistas': query_pista(con, part_id, permission),
        'comps': query_comps(con, part_id, permission),
        'grupos': query_grupos(con, part_id, permission),
        'pers': query_pers(con, part_id, permission),
        'series': query_serie(con, part_id, permission)
    }
    if permission == 'EDITOR':
        perfil_dict['editor'] = True
    if permission == 'MOD':
        perfil_dict['mod'] = True
        perfil_dict['editor'] = True
    if permission == 'ADMIN':
        perfil_dict['usuarios'] = get_users(con)
        perfil_dict['mod'] = True
        perfil_dict['editor'] = True
    return perfil_dict


# Queries for the poner_part view
def insert_part(con, form, usuario_id):
    if form.user_type.data == 'persona':
        result_nac = insert_lugar(con, form)
        query_muer = text("""INSERT INTO public.lugar(ciudad
                                                   , subdivision
                                                   , pais)
                                                  VALUES (strip(:ciudad)
                                                        , strip(:subdivision)
                                                        , strip(:pais))
                                                      RETURNING lugar_id""")
        result_muer = con.execute(query_muer, ciudad=form.ciudad_muer.data
                                            , subdivision=form.subdivision_muer.data
                                            , pais=form.pais_muer.data).first()[0]
        user_query = text("""INSERT INTO public.persona (nom_part
                                                           , seudonimo
                                                           , nom_paterno
                                                           , nom_materno
                                                           , lugar_id
                                                           , lugar_muer
                                                           , fecha_comienzo
                                                           , fecha_finale
                                                           , sitio_web
                                                           , email
                                                           , genero
                                                           , coment_part
                                                           , cargador_id)
                                                         VALUES (strip(:nom_part)
                                                               , strip(:seudonimo)
                                                               , strip(:nom_paterno)
                                                               , strip(:nom_materno)
                                                               , :lugar_id
                                                               , :lugar_muer
                                                               , :fecha_comienzo
                                                               , :fecha_finale
                                                               , strip(:sitio_web)
                                                               , strip(:email)
                                                               , strip(:genero)
                                                               , strip(:coment_part)
                                                               , :cargador_id)
                                                               RETURNING part_id""")
        user_result = con.execute(user_query, nom_part=form.nom_part.data
                    , seudonimo=form.seudonimo.data
                    , nom_materno=form.nom_materno.data
                    , nom_paterno=form.nom_paterno.data
                    , lugar_id=result_nac
                    , lugar_muer=result_muer
                    , fecha_comienzo=parse_fecha(form.fecha_comienzo.data)
                    , fecha_finale=parse_fecha(form.fecha_finale.data)
                    , sitio_web=form.sitio_web.data
                    , email=form.email.data
                    , genero=form.genero.data
                    , coment_part=form.coment_part.data
                    , cargador_id=usuario_id).first()[0]

        upsert_pers_grupos(con, form, usuario_id, user_result)
    else:
        user_query = text("""INSERT INTO public.gr_view(nom_part
                                                           , ciudad
                                                           , subdivision
                                                           , pais
                                                           , fecha_comienzo_insert
                                                           , fecha_finale_insert
                                                           , sitio_web
                                                           , direccion
                                                           , telefono
                                                           , email
                                                           , tipo_grupo
                                                           , coment_part
                                                           , cargador_id)
                                                         VALUES (strip(:nom_part)
                                                               , strip(:ciudad)
                                                               , strip(:subdivision)
                                                               , strip(:pais)
                                                               , :fecha_comienzo
                                                               , :fecha_finale
                                                               , strip(:sitio_web)
                                                               , strip(:direccion)
                                                               , strip(:telefono)
                                                               , strip(:email)
                                                               , strip(:tipo_grupo)
                                                               , strip(:coment_part)
                                                               , :cargador_id)""")
        con.execute(user_query, nom_part=form.nom_part_gr.data
                    , ciudad=form.ciudad.data
                    , subdivision=form.subdivision.data
                    , pais=form.pais.data
                    , fecha_comienzo=parse_fecha(form.fecha_comienzo.data)
                    , fecha_finale=parse_fecha(form.fecha_finale.data)
                    , sitio_web=form.sitio_web.data
                    , direccion=form.direccion.data
                    , telefono=form.telefono.data
                    , email=form.email.data
                    , coment_part=form.coment_part.data
                    , tipo_grupo=form.tipo_grupo.data
                    , cargador_id=usuario_id)


def populate_part(form, user):
    form.email.data = user.email
    form.direccion.data = user.direccion
    form.telefono.data = user.telefono
    form.sitio_web.data = user.sitio_web
    form.ciudad.data = user.ciudad
    form.subdivision.data = user.subdivision
    form.pais.data = user.pais
    form.fecha_comienzo.data = user.fecha_comienzo
    form.fecha_finale.data = user.fecha_finale
    form.coment_part.data = user.coment_part


def populate_serie(con, form, obra_id):
    query = text("""SELECT * from public.serie WHERE serie_id=:obra_id""")
    result = con.execute(query, obra_id=obra_id).first()
    form.nom_serie.data = result.nom_serie
    form.archivo.data = result.ruta_foto
    form.giro.data = result.giro
    form.coment_serie.data = result.coment_serie


# Queries for the poner_pers view
def populate_poner_pers(con, form, part_id):
    query = text("""SELECT * FROM public.pers_view WHERE part_id=:part_id""")
    user = con.execute(query, part_id=part_id).first()
    pers_org_query = text("""SELECT pa.grupo_id
                                  , public.get_fecha(pa.fecha_comienzo) fecha_comienzo
                                  , public.get_fecha(pa.fecha_finale) fecha_finale
                                  , pa.titulo
                                  FROM public.persona_grupo pa
                                  WHERE pa.persona_id=:part_id""")
    pers_org_result = con.execute(pers_org_query, part_id=part_id)

    populate_pers_grupo(form, pers_org_result)
    form.nom_part.data = user.nom_part
    form.nom_paterno.data = user.nom_paterno
    form.nom_materno.data = user.nom_materno
    form.seudonimo.data = user.seudonimo
    form.genero.data = user.genero
    form.ciudad_muer.data = user.ciudad_muer
    form.subdivision_muer.data = user.subdivision_muer
    form.pais_muer.data = user.pais_muer
    populate_part(form, user)


def update_poner_pers(con, form, usuario_id, part_id):
    user_query = text("""UPDATE public.pers_view SET nom_part=strip(:nom_part)
                                             , seudonimo=strip(:seudonimo)
                                             , nom_materno=strip(:nom_materno)
                                             , nom_paterno=strip(:nom_paterno)
                                             , ciudad=strip(:ciudad)
                                             , subdivision=strip(:subdivision)
                                             , pais=strip(:pais)
                                             , ciudad_muer=strip(:ciudad_muer)
                                             , subdivision_muer=strip(:subdivision_muer)
                                             , pais_muer=strip(:pais_muer)
                                             , fecha_comienzo_insert=:fecha_comienzo
                                             , fecha_finale_insert=:fecha_finale
                                             , sitio_web=strip(:sitio_web)
                                             , email=strip(:email)
                                             , genero=strip(:genero)
                                             , coment_part=strip(:coment_part)
                                             , mod_id=:mod_id
                                             WHERE part_id=:part_id;""")
    con.execute(user_query, nom_part=form.nom_part.data
                , seudonimo=form.seudonimo.data
                , nom_materno=form.nom_materno.data
                , nom_paterno=form.nom_paterno.data
                , ciudad=form.ciudad.data
                , subdivision=form.subdivision.data
                , pais=form.pais.data
                , ciudad_muer=form.ciudad_muer.data
                , subdivision_muer=form.subdivision_muer.data
                , pais_muer=form.pais_muer.data
                , fecha_comienzo=parse_fecha(form.fecha_comienzo.data)
                , fecha_finale=parse_fecha(form.fecha_finale.data)
                , sitio_web=form.sitio_web.data
                , email=form.email.data
                , genero=form.genero.data
                , coment_part=form.coment_part.data
                , mod_id=usuario_id
                , part_id=part_id)
    upsert_pers_grupos(con, form, usuario_id, part_id, update=True)


# Queries for the poner_gr view
def populate_poner_grupo(con, form, part_id):
    query = text("""SELECT * FROM public.gr_view WHERE part_id=:part_id""")
    user = con.execute(query, part_id=part_id).first()
    form.tipo_grupo.data = user.tipo_grupo
    form.nom_part_gr.data = user.nom_part
    populate_part(form, user)


def update_poner_grupo(con, form, usuario_id, part_id):
    user_query = text("""UPDATE public.gr_view SET nom_part=strip(:nom_part_gr)
                                             , ciudad=strip(:ciudad)
                                             , subdivision=strip(:nom_sudivision)
                                             , pais=strip(:pais)
                                             , fecha_comienzo_insert=:fecha_comienzo
                                             , fecha_comienzo_insert=:fecha_comienzo
                                             , sitio_web=strip(:sitio_web)
                                             , direccion=strip(:direccion)
                                             , telefono=strip(:telefono)
                                             , coment_part=strip(:coment_part)
                                             , tipo_grupo=strip(:tipo_grupo)
                                             , mod_id=:mod_id
                                             WHERE part_id=:part_id;""")
    con.execute(user_query, nom_part_gr=form.nom_part_gr.data
                , ciudad=form.ciudad.data
                , subdivision=form.subdivision.data
                , pais=form.pais.data
                , date_formed=parse_fecha(form.fecha_comienzo.data)
                , sitio_web=form.sitio_web.data
                , direccion=form.direccion.data
                , telefono=form.telefono.data
                , coment_part=form.coment_part.data
                , tipo_grupo=form.tipo_grupo.data
                , mod_id=usuario_id
                , part_i=part_id)


def populate_cob(con, form, ent_id, is_pista=True):
    # Populate copyright section
    if is_pista:
        query = text("""SELECT cobertura_lic_id
                             , public.get_fecha(fecha_comienzo) fecha_comienzo
                             , public.get_fecha(fecha_finale) fecha_finale
                             , pais_cobertura 
                         FROM public.cobertura WHERE pista_son_id=:ent_id""")
    else:
        query = text("""SELECT cobertura_lic_id
                             , public.get_fecha(fecha_comienzo) fecha_comienzo
                             , public.get_fecha(fecha_finale) fecha_finale
                             , pais_cobertura  FROM public.cobertura WHERE composicion_id=:ent_id""")
    cob_result = con.execute(query, ent_id=ent_id).first()
    form.cobertura.data = str(cob_result.cobertura_lic_id)
    form.pais_cob.data = cob_result.pais_cobertura
    form.fecha_comienzo_cob.data = cob_result.fecha_comienzo
    form.fecha_finale_cob.data = cob_result.fecha_finale


# Queries for the poner_comp view
def populate_comp(con, form, comp_id):
    query = text("""SELECT * FROM public.participante_composicion WHERE composicion_id=:comp_id""")
    comps_result = con.execute(query, comp_id=comp_id)
    if comps_result.rowcount == 0:
        aut_form = DynamicAuthorForm()
        aut_form.part_id = "1"
        aut_form.rol_composicion = "Composición"
        form.part_id_form.append_entry(aut_form)
    for res in comps_result:
        aut_form = DynamicAuthorForm()
        aut_form.part_id = str(res.part_id)
        aut_form.rol_composicion = res.rol_composicion
        form.part_id_form.append_entry(aut_form)

    query = text("""SELECT * FROM public.idioma_composicion WHERE composicion_id=:comp_id""")
    comps_result = con.execute(query, comp_id=comp_id)
    if comps_result.rowcount == 0:
        lang_form = DynamicLangForm()
        lang_form.idioma_id = "0"
        form.idioma_form.append_entry(lang_form)
    for res in comps_result:
        lang_form = DynamicLangForm()
        lang_form.idioma_id = str(res.idioma_id)
        form.idioma_form.append_entry(lang_form)

    query = text("""SELECT * FROM public.tema_composicion WHERE composicion_id=:comp_id""")
    comps_result = con.execute(query, comp_id=comp_id)
    if comps_result.rowcount == 0:
        theme_form = DynamicThemeForm()
        theme_form.tema_id = "0"
        form.tema_form.append_entry(theme_form)
    for res in comps_result:
        theme_form = DynamicThemeForm()
        theme_form.tema_id = str(res.tema_id)
        form.tema_form.append_entry(theme_form)
    query = text("""SELECT nom_tit, nom_alt, public.get_fecha(fecha_pub) fecha_pub, 
                          composicion_orig, texto FROM public.composicion WHERE composicion_id=:comp_id""")
    comp = con.execute(query, comp_id=comp_id).first()
    if comp is not None:
        form.nom_tit.data = comp.nom_tit
        form.nom_alt.data = comp.nom_alt
        form.fecha_pub.data = comp.fecha_pub
        form.comp_id = str(comp.composicion_orig)
        form.texto.data = comp.texto
        populate_cob(con, form, comp_id, False)


def insert_cob(con, form, ent_id, is_pista=True):
    if is_pista:
        query = text("""INSERT INTO public.cobertura (cobertura_lic_id
                                                    , pista_son_id
                                                    , pais_cobertura
                                                    , fecha_comienzo
                                                    , fecha_finale)
                                              VALUES (:cobertura
                                                    , :ent_id
                                                    , :pais_cob
                                                    , :fecha_comienzo
                                                    , :fecha_finale)""")
    else:
        query = text("""INSERT INTO public.cobertura (cobertura_lic_id
                                                            , composicion_id
                                                            , pais_cobertura
                                                            , fecha_comienzo
                                                            , fecha_finale)
                                                      VALUES (:cobertura
                                                            , :ent_id
                                                            , :pais_cob
                                                            , :fecha_comienzo
                                                            , :fecha_finale)""")
    con.execute(query, cobertura=form.cobertura.data
                     , ent_id=ent_id
                     , pais_cob=form.pais_cob.data
                     , fecha_comienzo=parse_fecha(form.fecha_comienzo_cob.data)
                     , fecha_finale=parse_fecha(form.fecha_finale_cob.data))


def update_cob(con, form, ent_id, is_pista=True):
    if is_pista:
        query = text("""UPDATE public.cobertura SET cobertura_lic_id=:cobertura
                                                    , pais_cobertura=:pais_cob
                                                    , fecha_comienzo=:fecha_comienzo
                                                    , fecha_finale=:fecha_finale
                                              WHERE pista_son_id=:ent_id""")
    else:
        query = text("""UPDATE public.cobertura SET cobertura_lic_id=:cobertura
                                                    , pais_cobertura=:pais_cob
                                                    , fecha_comienzo=:fecha_comienzo
                                                    , fecha_finale=:fecha_finale
                                              WHERE composicion_id=:ent_id""")
    con.execute(query, cobertura=form.cobertura.data
                     , ent_id=ent_id
                     , pais_cob=form.pais_cob.data
                     , fecha_comienzo=parse_fecha(form.fecha_comienzo_cob.data)
                     , fecha_finale=parse_fecha(form.fecha_finale_cob.data))


def update_comp(con, form, usuario_id, comp_id):
    query = text("""UPDATE public.composicion SET nom_tit=:nom_tit
                                               , nom_alt=:nom_alt
                                               , fecha_pub=:fecha_pub
                                               , composicion_orig=NULLIf(:composicion_orig, 0)
                                               , texto=strip(:texto)
                                               WHERE composicion_id=:comp_id""")
    con.execute(query, nom_tit=form.nom_tit.data
                     , nom_alt=form.nom_alt.data
                     , fecha_pub=parse_fecha(form.fecha_pub.data)
                     , composicion_orig=form.composicion_id.data
                     , texto=form.texto.data
                     , comp_id=comp_id)

    used_ids = []
    for entry in form.tema_form.entries:
        tema_id = int(entry.data['tema_id'])
        if tema_id != 0 and tema_id not in used_ids:
            used_ids.append(tema_id)
            insert_tema_comp = text("""INSERT INTO public.tema_composicion 
                                        VALUES (:comp_id, :tema_id) ON CONFLICT DO NOTHING""")
            con.execute(insert_tema_comp, comp_id=comp_id, tema_id=tema_id)
    delete_tema_comp = text("""DELETE FROM public.tema_composicion WHERE composicion_id=:comp_id
                               AND tema_id NOT IN :used""")
    used_ids.append(0)
    con.execute(delete_tema_comp, used=tuple(used_ids), comp_id=comp_id)

    used_ids = []
    for entry in form.idioma_form.entries:
        idioma_id = int(entry.data['idioma_id'])
        if idioma_id != 0 and idioma_id not in used_ids:
            used_ids.append(idioma_id)
            idioma_comp_insert = text("""INSERT INTO public.idioma_composicion 
                                          VALUES (:comp_id, :idioma_id) ON CONFLICT DO NOTHING""")
            con.execute(idioma_comp_insert, comp_id=comp_id, idioma_id=idioma_id)
    delete_idioma_comp = text("""DELETE FROM public.idioma_composicion WHERE composicion_id=:comp_id
                               AND idioma_id NOT IN :used""")
    used_ids.append(0)
    con.execute(delete_idioma_comp, used=tuple(used_ids), comp_id=comp_id)

    used_ids = []
    for entry in form.part_id_form.entries:
        tuple_id = (int(entry.data['part_id']), entry.data['rol_composicion'])
        if tuple_id not in used_ids:
            used_ids.append(tuple_id)
            part_comp_insert = text("""INSERT INTO public.participante_composicion(composicion_id
                                                                                 , part_id
                                                                                 , rol_composicion
                                                                                 , cargador_id) 
                                                                             VALUES (:comp_id
                                                                                   , :part_id
                                                                                   , :rol_composicion
                                                                                   , :cargador_id)
                                                                               ON CONFLICT DO NOTHING""")
            con.execute(part_comp_insert, comp_id=comp_id
                                        , part_id=tuple_id[0]
                                        , rol_composicion=tuple_id[1]
                                        , cargador_id=usuario_id)
    delete_part_comp = text("""DELETE FROM public.participante_composicion WHERE composicion_id=:comp_id
                                AND (part_id, rol_composicion) NOT IN :used""")

    used_ids.append((0, "Ninguno"))
    con.execute(delete_part_comp, comp_id=comp_id, used=tuple(used_ids))
    update_cob(con, form, comp_id, is_pista=False)


def insert_comp(con, form, usuario_id):
    query = text("""INSERT INTO public.composicion(nom_tit
                                                 , nom_alt
                                                 , fecha_pub
                                                 , composicion_orig
                                                 , texto
                                                 , cargador_id) 
                                                 VALUES (strip(:nom_tit)
                                                       , strip(:nom_alt)
                                                       , :fecha_pub
                                                       , NULLIF(:composicion_orig, 0)
                                                       , strip(:texto)
                                                       , :cargador_id)
                                                       RETURNING composicion_id""")

    comp_result = con.execute(query, nom_tit=form.nom_tit.data
                     , nom_alt=form.nom_alt.data
                     , fecha_pub=parse_fecha(form.fecha_pub.data)
                     , composicion_orig=form.composicion_id.data
                     , texto=form.texto.data
                     , cargador_id=usuario_id).first()[0]
    used_ids = []
    for entry in form.tema_form.entries:
        tema_id = int(entry.data['tema_id'])
        if tema_id != 0 and tema_id not in used_ids:
            used_ids.append(tema_id)
            insert_tema_comp = text("""INSERT INTO public.tema_composicion 
                                        VALUES (:comp_id, :tema_id) ON CONFLICT DO NOTHING""")
            con.execute(insert_tema_comp, comp_id=comp_result, tema_id=tema_id)

    used_ids = []
    for entry in form.idioma_form.entries:
        idioma_id = int(entry.data['idioma_id'])
        if idioma_id != 0 and idioma_id not in used_ids:
            used_ids.append(idioma_id)
            idioma_comp_insert = text("""INSERT INTO public.idioma_composicion 
                                          VALUES (:comp_id, :idioma_id) ON CONFLICT DO NOTHING""")
            con.execute(idioma_comp_insert, comp_id=comp_result, idioma_id=idioma_id)

    used_ids = []
    for entry in form.part_id_form.entries:
        tuple_id = (int(entry.data['part_id']), entry.data['rol_composicion'])
        if tuple_id not in used_ids:
            used_ids.append(tuple_id)
            part_comp_insert = text("""INSERT INTO public.participante_composicion(composicion_id
                                                                                 , part_id
                                                                                 , rol_composicion
                                                                                 , cargador_id) 
                                                                             VALUES (:comp_id
                                                                                   , :part_id
                                                                                   , :rol_composicion
                                                                                   , :cargador_id)""")
            con.execute(part_comp_insert, comp_id=comp_result
                                        , part_id=tuple_id[0]
                                        , rol_composicion=tuple_id[1]
                                        , cargador_id=usuario_id)
    insert_cob(con, form, comp_result, is_pista=False)


# Queries for the poner_pista view
def populate_pista(con, form, pista_id):
    query = text("""SELECT * FROM public.participante_pista_son WHERE pista_son_id=:pista_id""")
    pista_result = con.execute(query, pista_id=pista_id)
    if pista_result.rowcount == 0:
        interp_form = DynamicInterpForm()
        interp_form.part_id = "1"
        interp_form.rol_pista_son = "Lectura en voz alta"
        interp_form.instrumento_id = "1"
        form.interp_form.append_entry(interp_form)
    for res in pista_result:
        interp_form = DynamicInterpForm()
        interp_form.part_id = str(res.part_id)
        interp_form.rol_pista_son = res.rol_pista_son
        interp_form.instrumento_id = str(res.instrumento_id)
        form.interp_form.append_entry(interp_form)

    query = text("""SELECT * FROM public.genero_pista WHERE pista_son_id=:pista_id""")
    pista_result = con.execute(query, pista_id=pista_id)
    if pista_result.rowcount == 0:
        gen_mus_form = DynamicGenMusForm()
        gen_mus_form.gen_mus_id = "0"
        form.gen_mus_form.append_entry(gen_mus_form)
    for res in pista_result:
        gen_mus_form = DynamicGenMusForm()
        gen_mus_form.gen_mus_id = str(res.gen_mus_id)
        form.gen_mus_form.append_entry(gen_mus_form)

    query = text("""SELECT * FROM public.pista_son WHERE pista_son_id=:pista_id""")
    pista = con.execute(query, pista_id=pista_id).first()
    if pista is not None:
        form.comp_id.data = str(pista.composicion_id)
        form.numero_de_pista.data = str(pista.numero_de_pista)
        form.medio.data = pista.medio
        form.serie_id.data = str(pista.serie_id)
        form.fecha_grab.data = get_fecha(pista.fecha_grab)
        form.fecha_dig.data = get_fecha(pista.fecha_dig)
        form.fecha_cont.data = get_fecha(pista.fecha_cont)
        form.coment_pista_son.data = pista.coment_pista_son

        populate_lugar(con, form, pista.lugar_id)
        populate_cob(con, form, pista_id)


def update_pista(con, form, usuario_id, pista_id):
    query = text("""UPDATE public.pista_son SET numero_de_pista=:numero_de_pista
                                                , composicion_id=:composicion_id
                                                , medio=:medio
                                                , serie_id=NULLIF(:serie_id, 0)
                                                , coment_pista_son=:coment_pista_son
                                                , fecha_grab=:fecha_grab
                                                , fecha_dig=:fecha_dig
                                                , fecha_cont=:fecha_cont
                                                , mod_id=:mod_id
                                            WHERE pista_son_id=:pista_id RETURNING lugar_id""")

    pista_son_result = con.execute(query
                     , numero_de_pista=form.numero_de_pista.data
                     , composicion_id=form.comp_id.data
                     , medio=form.medio.data
                     , serie_id=form.serie_id.data
                     , coment_pista_son=form.coment_pista_son.data
                     , fecha_grab=parse_fecha(form.fecha_grab.data)
                     , fecha_dig=parse_fecha(form.fecha_dig.data)
                     , fecha_cont=parse_fecha(form.fecha_cont.data)
                     , mod_id=usuario_id
                     , pista_id=pista_id).first()[0]
    update_lugar(con, form, pista_son_result)

    used_ids = []
    for entry in form.gen_mus_form.entries:
        gen_mus_id = int(entry.data['gen_mus_id'])
        if gen_mus_id != 0 and gen_mus_id not in used_ids:
            used_ids.append(gen_mus_id)
            insert_gen_mus = text("""INSERT INTO public.genero_pista (pista_son_id, gen_mus_id)
                                      VALUES (:pista_son_id, :gen_mus_id) ON CONFLICT DO NOTHING""")
            con.execute(insert_gen_mus, pista_son_id=pista_id, gen_mus_id=gen_mus_id)
    delete_gen_mus = text("""DELETE FROM public.genero_pista WHERE pista_son_id=:pista_id 
                              AND gen_mus_id NOT IN :used""")
    used_ids.append(0)
    con.execute(delete_gen_mus, pista_id=pista_id, used=tuple(used_ids))

    used_ids = []
    for entry in form.interp_form.entries:
        tuple_id = (int(entry.data['part_id']), entry.data['rol_pista_son'], int(entry.data['instrumento_id']))
        if tuple_id not in used_ids:
            used_ids.append(tuple_id)
            insert_part_insert = text("""INSERT INTO public.participante_pista_son(pista_son_id
                                                                                 , part_id
                                                                                 , rol_pista_son
                                                                                 , instrumento_id
                                                                                 , cargador_id) 
                                                                             VALUES (:pista_son_id
                                                                                   , :part_id
                                                                                   , :rol_pista_son
                                                                                   , :instrumento_id
                                                                                   , :cargador_id) ON CONFLICT (
                                                                                   pista_son_id
                                                                                  ,part_id
                                                                                  ,rol_pista_son
                                                                                  ,instrumento_id)
                                                                                   DO UPDATE SET 
                                                                                  mod_id=EXCLUDED.cargador_id""")
            con.execute(insert_part_insert, pista_son_id=pista_id
                        , part_id=tuple_id[0]
                        , rol_pista_son=tuple_id[1]
                        , instrumento_id=tuple_id[2]
                        , cargador_id=usuario_id)
    delete_part_pista = text("""DELETE FROM public.participante_pista_son WHERE pista_son_id=:pista_id 
                              AND (part_id, rol_pista_son, instrumento_id) NOT IN :used""")
    con.execute(delete_part_pista, pista_id=pista_id, used=tuple(used_ids))
    used_ids.append((0, "Ninguno", 0))
    update_cob(con, form, pista_id)


def insert_pista(con, form, usuario_id):
    result_lugar = insert_lugar(con, form)
    query = text("""INSERT INTO public.pista_son( numero_de_pista
                                                , composicion_id
                                                , medio
                                                , lugar_id
                                                , serie_id
                                                , coment_pista_son
                                                , fecha_grab
                                                , fecha_dig
                                                , fecha_cont
                                                , cargador_id)
                                                 VALUES ( :numero_de_pista
                                                        , :composicion_id
                                                        , :medio
                                                        , :lugar_id
                                                        , NULLIF(:serie_id, 0)
                                                        , :coment_pista_son
                                                        , :fecha_grab
                                                        , :fecha_dig
                                                        , :fecha_cont
                                                        , :cargador_id)
                                                       RETURNING pista_son_id""")
    pista_son_result = con.execute(query
                                   , numero_de_pista=form.numero_de_pista.data
                                   , composicion_id=form.comp_id.data
                                   , medio=form.medio.data
                                   , lugar_id=result_lugar
                                   , serie_id=form.serie_id.data
                                   , coment_pista_son=form.coment_pista_son.data
                                   , fecha_grab=parse_fecha(form.fecha_grab.data)
                                   , fecha_dig=parse_fecha(form.fecha_dig.data)
                                   , fecha_cont=parse_fecha(form.fecha_cont.data)
                                   , cargador_id=usuario_id).first()[0]

    used_ids = []
    for entry in form.gen_mus_form.entries:
        gen_mus_id = int(entry.data['gen_mus_id'])
        if gen_mus_id != 0 and gen_mus_id not in used_ids:
            used_ids.append(gen_mus_id)
            gen_mus_insert = text("""INSERT INTO public.genero_pista (pista_son_id, gen_mus_id)
                                      VALUES (:pista_son_id, :gen_mus_id)""")
            con.execute(gen_mus_insert, pista_son_id=pista_son_result, gen_mus_id=gen_mus_id)
    used_ids = []
    for entry in form.interp_form.entries:
        tuple_id = (int(entry.data['part_id']), entry.data['rol_pista_son'], int(entry.data['instrumento_id']))
        if tuple_id not in used_ids:
            used_ids.append(tuple_id)
            part_comp_insert = text("""INSERT INTO public.participante_pista_son(pista_son_id
                                                                                 , part_id
                                                                                 , rol_pista_son
                                                                                 , instrumento_id
                                                                                 , cargador_id) 
                                                                             VALUES (:pista_son_id
                                                                                   , :part_id
                                                                                   , :rol_pista_son
                                                                                   , :instrumento_id
                                                                                   , :cargador_id)""")
            con.execute(part_comp_insert, pista_son_id=pista_son_result
                        , part_id=tuple_id[0]
                        , rol_pista_son=tuple_id[1]
                        , instrumento_id=tuple_id[2]
                        , cargador_id=usuario_id)
    insert_cob(con, form, pista_son_result)
    return pista_son_result


# Query to add an instrument
def populate_inst_fam(con):
    query_inst = text("""SELECT familia_instr_id f_id, nom_familia_instr f_nom FROM public.familia_instrumento""")
    result_inst = con.execute(query_inst)
    inst_arr = [(str(res.f_id), res.f_nom) for res in result_inst]
    return inst_arr


def insert_inst(con, form):
    query = text("""INSERT INTO public.instrumento(nom_inst, familia_instr_id, electronico, instrumento_comentario) 
                    VALUES (strip(:nom_inst), :familia_instr_id, :electronico, strip(:instrumento_comentario))""")
    con.execute(query, nom_inst=form.nom_inst.data
                     , familia_instr_id=form.familia_instr_id.data
                     , electronico=form.electronico.data
                     , instrumento_comentario=form.instrumento_comentario.data)


def insert_serie(con, form, filename):
    query_serie = text("""INSERT INTO public.serie (nom_serie, giro, coment_serie, ruta_foto) VALUES
                          (strip(:nom_serie), strip(:giro), strip(:coment_serie), :filename) RETURNING serie_id""")
    query = con.execute(query_serie, nom_serie=form.nom_serie.data, giro=form.giro.data
                                   , coment_serie=form.coment_serie.data, filename=filename)
    return query.first()[0]


def insert_genero(con, form):
    query_genero = text("""INSERT INTO public.genero_musical (nom_gen_mus, coment_gen_mus) VALUES 
                            (strip(:nom_gen_mus), strip(:coment_gen_mus))""")
    con.execute(query_genero, nom_gen_mus=form.nom_gen_mus.data, coment_gen_mus=form.coment_gen_mus.data)


def insert_tema(con, form):
    query_tema = text("""INSERT INTO public.tema(nom_tema) VALUES (strip(LOWER(:nom_tema)))""")
    con.execute(query_tema, nom_tema=form.nom_tema.data)


def insert_idioma(con, form):
    query_idioma = text("""INSERT INTO public.idioma(nom_idioma) VALUES (strip(:nom_idioma))""")
    con.execute(query_idioma, nom_idioma=form.nom_idioma.data)


def insert_album(con, form):
    query_tema = text("""INSERT INTO public.album (nom_album, serie_id) 
                          VALUES (:nom_album, :serie_id)""")
    con.execute(query_tema, nom_album=form.nom_album.data, serie_id=form.serie_id.data)


def delete_serie(con, serie_id):
    query = text("""DELETE FROM public.serie WHERE serie_id=:serie_id""")
    con.execute(query, serie_id=serie_id)


def delete_album(con, album_id):
    query = text("""DELETE FROM public.album WHERE album_id=:album_id""")
    con.execute(query, album_id=album_id)


def delete_tema(con, tema_id):
    query = text("""DELETE FROM public.tema WHERE tema_id=:tema_id""")
    con.execute(query, tema_id=tema_id)


def delete_inst(con, inst_id):
    query = text("""DELETE FROM public.instrumento WHERE instrumento_id=:inst_id""")
    con.execute(query, inst_id=inst_id)


def delete_idioma(con, idioma_id):
    query = text("""DELETE FROM public.idioma WHERE idioma_id=:idioma_id""")
    con.execute(query, idioma_id=idioma_id)


def delete_genero(con, genero_id):
    query = text("""DELETE FROM public.genero_musical WHERE gen_mus_id=:genero_id""")
    con.execute(query, genero_id=genero_id)


# Query for remove_part view
def delete_persona(con, part_id, usuario_id):
    query = text("""SELECT usuario_id FROM public.usuario""")
    result = con.execute(query)
    result_arr = [res.usuario_id for res in result]
    if part_id in result_arr:
        return False
    query = text("""DELETE FROM public.participante WHERE part_id=:part_id 
                    AND part_id NOT IN (SELECT usuario_id FROM public.usuario)""")
    con.execute(query, part_id=part_id)
    query = text("""UPDATE audit.persona_audit SET mod_id=:usuario_id WHERE part_id=:part_id
                    AND accion = 'D' AND fecha_accion IN (SELECT MAX(fecha_accion) FROM audit.persona_audit 
                    WHERE part_id=:part_id AND accion = 'D')""")
    con.execute(query, part_id=part_id, usuario_id=usuario_id)
    return True


# Query for remove_part view
def delete_grupo(con, part_id, usuario_id):
    query = text("""SELECT usuario_id FROM public.usuario""")
    result = con.execute(query)
    result_arr = [res.usuario_id for res in result]
    if part_id in result_arr:
        return False
    query = text("""DELETE FROM public.participante WHERE part_id=:part_id 
                    AND part_id NOT IN (SELECT usuario_id FROM public.usuario)""")
    con.execute(query, part_id=part_id)
    query = text("""UPDATE audit.grupo_audit SET mod_id=:usuario_id WHERE part_id=:part_id
                    AND accion = 'D' AND fecha_accion IN (SELECT MAX(fecha_accion) FROM audit.grupo_audit 
                    WHERE part_id=:part_id AND accion = 'D')""")
    con.execute(query, part_id=part_id, usuario_id=usuario_id)
    return True


# Query to remove a composicion
def delete_comp(con, comp_id, usuario_id):
    query = text("""SELECT DISTINCT composicion_id FROM public.pista_son""")
    result = con.execute(query)
    result_arr = [res.composicion_id for res in result]
    if comp_id in result_arr:
        return False
    query = text("""DELETE FROM public.composicion WHERE composicion_id=:comp_id""")
    con.execute(query, comp_id=comp_id)
    query = text("""UPDATE audit.composicion_audit SET mod_id=:usuario_id WHERE composicion_id=:comp_id
                    AND accion = 'D' AND fecha_accion IN (SELECT MAX(fecha_accion) FROM audit.composicion_audit 
                    WHERE composicion_id=:comp_id AND accion = 'D')""")
    con.execute(query, comp_id=comp_id, usuario_id=usuario_id)
    return True


def delete_pista(con, pista_id, usuario_id):
    query = text("""SELECT DISTINCT pista_son_id FROM public.archivo""")
    result = con.execute(query)
    result_arr = [res.pista_son_id for res in result]
    if pista_id in result_arr:
        return False
    query = text("""DELETE FROM public.pista_son WHERE pista_son_id=:pista_id""")
    con.execute(query, pista_id=pista_id)
    query = text("""UPDATE audit.pista_son_audit SET mod_id=:usuario_id WHERE pista_son_id=:pista_id
                    AND accion = 'D' AND fecha_accion IN (SELECT MAX(fecha_accion) FROM audit.pista_son_audit 
                    WHERE pista_son_id=:pista_id AND accion = 'D')""")
    con.execute(query, pista_id=pista_id, usuario_id=usuario_id)
    return True


# Queries for init_session
def init_comps(con, part_id):
    comps_query = text("""SELECT composicion_id 
                            FROM public.composicion
                            WHERE cargador_id=:id 
                              AND (estado='PENDIENTE'
                              OR estado='PUBLICADO')""")
    comps_result = con.execute(comps_query, id=part_id)
    return [comp[0] for comp in comps_result]


def init_pistas(con, part_id):
    pista_query = text("""SELECT pista_son_id 
                                FROM public.pista_son
                                WHERE cargador_id=:id
                                  AND (estado='PENDIENTE'
                                  OR estado='PUBLICADO')""")
    pista_result = con.execute(pista_query, id=part_id)
    return [pista[0] for pista in pista_result]


def init_pers(con, part_id):
    pers_query = text("""SELECT part_id 
                           FROM public.persona
                           WHERE cargador_id=:id
                             AND (estado='PENDIENTE'
                             OR estado='PUBLICADO') """)
    pers_result = con.execute(pers_query, id=part_id)
    return [pers[0] for pers in pers_result]


def init_grupos(con, part_id):
    gr_query = text("""SELECT part_id 
                           FROM public.grupo
                           WHERE cargador_id=:id
                             AND (estado='PENDIENTE'
                             OR estado='PUBLICADO')""")
    gr_result = con.execute(gr_query, id=part_id)
    return [ag[0] for ag in gr_result]


def init_series(con, part_id):
    serie_query = text("""SELECT serie_id
                            FROM public.serie
                            WHERE cargador_id=:id
                            AND (estado='PENDIENTE'
                             OR estado='PUBLICADO')""")
    serie_result = con.execute(serie_query, id=part_id)
    return [ag[0] for ag in serie_result]