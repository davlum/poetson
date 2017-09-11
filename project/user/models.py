from sqlalchemy import text
from flask import session
from project.util import current_pers, current_ag, parse_fecha
from project.user.forms import OrgForm


# Queries for the info view
def populate_info(con, form):
    if session['is_person']:
        user = current_pers(con, session['email'])
        pers_org_query = text("""SELECT pa.agregar_id
                                      , public.get_fecha(pa.fecha_comienzo) fecha_comienzo
                                      , public.get_fecha(pa.fecha_finale) fecha_finale
                                      , pa.titulo
                                      FROM public.persona_agregar pa
                                      WHERE pa.persona_id=:id""")
        pers_org_result = con.execute(pers_org_query, id=session['id'])

        for res in pers_org_result:
            org_form = OrgForm()
            org_form.agregar_id = str(res.agregar_id)
            org_form.titulo = res.titulo
            org_form.fecha_comienzo = res.fecha_comienzo
            org_form.fecha_finale = res.fecha_finale

            form.org_form.append_entry(org_form)

        form.nom_part.data = user.nom_part
        form.nom_segundo.data = user.nom_segundo
        form.seudonimo.data = user.seudonimo
        form.fecha_comienzo.data = user.fecha_comienzo
        form.nom_paterno.data = user.nom_paterno
        form.nom_materno.data = user.nom_materno
        form.genero.data = user.genero
    else:
        user = current_ag(con, session['email'])
        form.nom_part_ag.data = user.nom_part
        form.fecha_comienzo.data = user.fecha_comienzo
        form.tipo_agregar.data = user.tipo_agregar
    form.coment_part.data = user.coment_part
    form.sitio_web.data = user.sitio_web
    form.direccion.data = user.direccion
    form.telefono.data = user.telefono
    form.ciudad.data = user.ciudad
    form.nom_subdivision.data = user.nom_subdivision
    form.tipo_subdivision.data = user.tipo_subdivision
    form.pais.data = user.pais


def update_info(con, form):
    if session['is_person']:
        user_query = text("""UPDATE public.pers_view SET nom_part=strip(:nom_part)
                                                 , nom_segundo=strip(:nom_segundo)
                                                 , seudonimo=strip(:seudonimo)
                                                 , nom_materno=strip(:nom_materno)
                                                 , nom_paterno=strip(:nom_paterno)
                                                 , ciudad=strip(:ciudad)
                                                 , nom_subdivision=strip(:nom_subdivision)
                                                 , tipo_subdivision=strip(:tipo_subdivision)
                                                 , pais=strip(:pais)
                                                 , fecha_comienzo_insert=:fecha_comienzo
                                                 , sitio_web=strip(:sitio_web)
                                                 , direccion=strip(:direccion)
                                                 , telefono=strip(:telefono)
                                                 , genero=strip(:genero)
                                                 , coment_part=strip(:coment_part)
                                                 , cargador_id=:id
                                                 WHERE part_id=:id;""")
        con.execute(user_query, nom_part=form.nom_part.data
                    , nom_segundo=form.nom_segundo.data
                    , seudonimo=form.seudonimo.data
                    , nom_materno=form.nom_materno.data
                    , nom_paterno=form.nom_paterno.data
                    , ciudad=form.ciudad.data
                    , nom_subdivision=form.nom_subdivision.data
                    , tipo_subdivision=form.tipo_subdivision.data
                    , pais=form.pais.data
                    , fecha_comienzo=parse_fecha(form.fecha_comienzo.data)
                    , sitio_web=form.sitio_web.data
                    , direccion=form.direccion.data
                    , telefono=form.telefono.data
                    , genero=form.genero.data
                    , coment_part=form.coment_part.data
                    , id=session['id'])
        pers_ag_delete = text("""DELETE FROM public.persona_agregar WHERE persona_id=:id""")
        con.execute(pers_ag_delete, id=session['id'])
        used_ids = []
        for entry in form.org_form.entries:
            ag_id = int(entry.data['agregar_id'])
            if ag_id != 0 and ag_id not in used_ids:
                used_ids.append(ag_id)
                pers_ag_insert = text("""INSERT INTO public.persona_agregar VALUES (:id
                                          , :agregar_id, :fecha_comienzo
                                          , :fecha_finale, strip(:titulo), :id)""")
                con.execute(pers_ag_insert, id=session['id']
                            , agregar_id=ag_id
                            , fecha_comienzo=parse_fecha(entry.data['fecha_comienzo'])
                            , fecha_finale=parse_fecha(entry.data['fecha_finale'])
                            , titulo=entry.data['titulo'])

    else:
        user_query = text("""UPDATE public.ag_view SET nom_part=strip(:nom_part_ag)
                                                 , ciudad=strip(:ciudad)
                                                 , nom_subdivision=strip(:nom_sudivision)
                                                 , tipo_subdivision=strip(:tipo_sudivision)
                                                 , pais=strip(:pais)
                                                 , fecha_comienzo_insert=:fecha_comienzo
                                                 , sitio_web=strip(:sitio_web)
                                                 , direccion=strip(:direccion)
                                                 , telefono=strip(:telefono)
                                                 , coment_part=strip(:coment_part)
                                                 , tipo_agregar=strip(:tipo_agregar)
                                                 , cargador_id=:id
                                                 WHERE part_id=:id;""")
        con.execute(user_query, nom_part_ag=form.nom_part_ag.data
                    , ciudad=form.ciudad.data
                    , nom_subdivision=form.nom_subdivision.data
                    , tipo_subdivision=form.tipo_subdivision.data
                    , pais=form.pais.data
                    , date_formed=parse_fecha(form.fecha_comienzo.data)
                    , sitio_web=form.sitio_web.data
                    , direccion=form.direccion.data
                    , telefono=form.telefono.data
                    , coment_part=form.coment_part.data
                    , tipo_agregar=form.tipo_agregar.data
                    , id=session['id'])


# Queries for the profile view
def query_pers_ag(con, part_id):
    query = text("""SELECT a.nom_part
                             , public.get_fecha(pa.fecha_comienzo) fecha_comienzo
                             , public.get_fecha(pa.fecha_finale) fecha_finale
                             , pa.titulo
                            FROM public.persona_agregar pa
                            JOIN public.agregar a
                              ON pa.agregar_id = a.part_id
                              WHERE pa.persona_id=:id""")
    return con.execute(query, id=part_id)


def query_ags(con, part_id):
    query = text("""SELECT part_id
                         , nom_part
                         , fecha_comienzo
                         , fecha_finale
                         , ciudad
                         , nom_subdivision
                         , pais
                         FROM public.ag_view
                         WHERE cargador_id=:id
                         AND cargador_id <> part_id
                         AND estado = 'PENDIENTE'
                          OR estado = 'PUBLICADO'""")
    result = con.execute(query, id=part_id)
    return result


def query_pers(con, part_id):
    query = text("""SELECT part_id
                         , nom_part
                         , nom_segundo
                         , seudonimo
                         , fecha_comienzo
                         , fecha_finale
                         , ciudad
                         , nom_subdivision
                         , pais
                         FROM public.pers_view
                         WHERE cargador_id=:id
                         AND cargador_id <> part_id
                         AND estado = 'PENDIENTE'
                          OR estado = 'PUBLICADO'""")
    return con.execute(query, id=part_id)

def query_comps(con, part_id):
    query = text("""SELECT composicion_id
                         , nom_tit
                         , nom_alt
                         , public.get_fecha(fecha_pub) fecha_pub
                         FROM public.composicion c
                         WHERE c.cargador_id=:id
                         AND c.estado = 'PENDIENTE'
                          OR c.estado = 'PUBLICADO'""")
    return con.execute(query, id=part_id)

def query_pista(con, part_id):
    query = text("""SELECT p.pista_son_id
                         , c.nom_tit
                         , l.ciudad
                         , l.nom_subdivision
                         , l.pais
                         , public.get_fecha(p.fecha_grab) fecha_grab
                         FROM public.pista_son p
                         JOIN public.composicion c
                          ON p.composicion_id = c.composicion_id
                         LEFT JOIN public.lugar l
                          ON  l.lugar_id = P.lugar_interp
                         WHERE p.cargador_id=:id
                         AND p.estado = 'PENDIENTE'
                          OR p.estado = 'PUBLICADO'""")
    return con.execute(query, id=part_id)


# Queries for the poner_part view
def insert_part(con, form):
    if form.user_type.data == 'persona':
        query_nac = text("""INSERT INTO public.lugar(ciudad
                                                    , nom_subdivision
                                                    , tipo_subdivision
                                                    , pais) 
                                                  VALUES (strip(:ciudad)
                                                  , strip(:nom_subdivision)
                                                  , strip(:tipo_subdivision)
                                                  , strip(:pais))
                                                RETURNING lugar_id""")
        result_nac = con.execute(query_nac
                                   , ciudad=form.ciudad.data
                                   , nom_subdivision=form.nom_subdivision.data
                                   , tipo_subdivision=form.tipo_subdivision.data
                                   , pais=form.pais.data).first()[0]
        query_muer = text("""INSERT INTO public.lugar(ciudad
                                                   , nom_subdivision
                                                   , tipo_subdivision
                                                   , pais)
                                                  VALUES (strip(:ciudad)
                                                        , strip(:nom_subdivision)
                                                        , strip(:tipo_subdivision)
                                                        , strip(:pais))
                                                      RETURNING lugar_id""")
        result_muer = con.execute(query_muer
                                   , ciudad=form.ciudad_muer.data
                                   , nom_subdivision=form.nom_subdivision_muer.data
                                   , tipo_subdivision=form.tipo_subdivision_muer.data
                                   , pais=form.pais_muer.data).first()[0]
        user_query = text("""INSERT INTO public.persona (nom_part
                                                           , nom_segundo
                                                           , seudonimo
                                                           , nom_paterno
                                                           , nom_materno
                                                           , lugar_id
                                                           , lugar_muer
                                                           , fecha_comienzo
                                                           , fecha_finale
                                                           , sitio_web
                                                           , direccion
                                                           , telefono
                                                           , email
                                                           , genero
                                                           , coment_part
                                                           , cargador_id)
                                                         VALUES (strip(:nom_part)
                                                               , strip(:nom_segundo)
                                                               , strip(:seudonimo)
                                                               , strip(:nom_paterno)
                                                               , strip(:nom_materno)
                                                               , :lugar_id
                                                               , :lugar_muer
                                                               , :fecha_comienzo
                                                               , :fecha_finale
                                                               , strip(:sitio_web)
                                                               , strip(:direccion)
                                                               , strip(:telefono)
                                                               , strip(:email)
                                                               , strip(:genero)
                                                               , strip(:coment_part)
                                                               , :cargador_id)
                                                               RETURNING part_id""")
        user_result = con.execute(user_query, nom_part=form.nom_part.data
                    , nom_segundo=form.nom_segundo.data
                    , seudonimo=form.seudonimo.data
                    , nom_materno=form.nom_materno.data
                    , nom_paterno=form.nom_paterno.data
                    , lugar_id=result_nac
                    , lugar_muer=result_muer
                    , fecha_comienzo=parse_fecha(form.fecha_comienzo.data)
                    , fecha_finale=parse_fecha(form.fecha_finale.data)
                    , sitio_web=form.sitio_web.data
                    , direccion=form.direccion.data
                    , telefono=form.telefono.data
                    , email=form.email.data
                    , genero=form.genero.data
                    , coment_part=form.coment_part.data
                    , cargador_id=session['id']).first()[0]

        used_ids = []
        for entry in form.org_form.entries:
            ag_id = int(entry.data['agregar_id'])
            if ag_id != 0 and ag_id not in used_ids:
                used_ids.append(ag_id)
                pers_ag_insert = text("""INSERT INTO public.persona_agregar VALUES (:id
                                          , :agregar_id, :fecha_comienzo
                                          , :fecha_finale, strip(:titulo), :id)""")
                con.execute(pers_ag_insert, id=user_result
                            , agregar_id=ag_id
                            , fecha_comienzo=parse_fecha(entry.data['fecha_comienzo'])
                            , fecha_finale=parse_fecha(entry.data['fecha_finale'])
                            , titulo=entry.data['titulo'])
    else:
        user_query = text("""INSERT INTO public.ag_view(nom_part
                                                           , ciudad
                                                           , nom_subdivision
                                                           , tipo_subdivision
                                                           , pais
                                                           , fecha_comienzo_insert
                                                           , fecha_finale_insert
                                                           , sitio_web
                                                           , direccion
                                                           , telefono
                                                           , email
                                                           , tipo_agregar
                                                           , coment_part
                                                           , cargador_id)
                                                         VALUES (strip(:nom_part)
                                                               , strip(:ciudad)
                                                               , strip(:nom_subdivision)
                                                               , strip(:tipo_subdivision)
                                                               , strip(:pais)
                                                               , :fecha_comienzo
                                                               , :fecha_finale
                                                               , strip(:sitio_web)
                                                               , strip(:direccion)
                                                               , strip(:telefono)
                                                               , strip(:email)
                                                               , strip(:tipo_agregar)
                                                               , strip(:coment_part)
                                                               , :cargador_id)""")
        con.execute(user_query, nom_part=form.nom_part_ag.data
                    , ciudad=form.ciudad.data
                    , nom_subdivision=form.nom_subdivision.data
                    , tipo_subdivision=form.tipo_subdivision.data
                    , pais=form.pais.data
                    , fecha_comienzo=parse_fecha(form.fecha_comienzo.data)
                    , fecha_finale=parse_fecha(form.fecha_finale.data)
                    , sitio_web=form.sitio_web.data
                    , direccion=form.direccion.data
                    , telefono=form.telefono.data
                    , email=form.email.data
                    , coment_part=form.coment_part.data
                    , tipo_agregar=form.tipo_agregar.data
                    , cargador_id=session['id'])


# Queries for the poner_pers view
def populate_poner_pers(con, form, part_id):
    query = text("""SELECT * FROM public.pers_view WHERE part_id=:part_id""")
    user = con.execute(query, part_id=part_id).first()
    pers_org_query = text("""SELECT pa.agregar_id
                                  , public.get_fecha(pa.fecha_comienzo) fecha_comienzo
                                  , public.get_fecha(pa.fecha_finale) fecha_finale
                                  , pa.titulo
                                  FROM public.persona_agregar pa
                                  WHERE pa.persona_id=:part_id""")
    pers_org_result = con.execute(pers_org_query, part_id=part_id)

    for res in pers_org_result:
        org_form = OrgForm()
        org_form.agregar_id = str(res.agregar_id)
        org_form.titulo = res.titulo
        org_form.fecha_comienzo = res.fecha_comienzo
        org_form.fecha_finale = res.fecha_finale

        form.org_form.append_entry(org_form)

    form.nom_part.data = user.nom_part
    form.nom_segundo.data = user.nom_segundo
    form.seudonimo.data = user.seudonimo
    form.fecha_comienzo.data = user.fecha_comienzo
    form.fecha_comienzo.data = user.fecha_finale
    form.nom_paterno.data = user.nom_paterno
    form.nom_materno.data = user.nom_materno
    form.genero.data = user.genero

    form.email.data = user.email
    form.coment_part.data = user.coment_part
    form.sitio_web.data = user.sitio_web
    form.direccion.data = user.direccion
    form.telefono.data = user.telefono
    form.ciudad.data = user.ciudad
    form.nom_subdivision.data = user.nom_subdivision
    form.tipo_subdivision.data = user.tipo_subdivision
    form.pais.data = user.pais
    form.ciudad_muer.data = user.ciudad_muer
    form.nom_subdivision_muer.data = user.nom_subdivision_muer
    form.tipo_subdivision_muer.data = user.tipo_subdivision_muer
    form.pais_muer.data = user.pais_muer


def update_poner_pers(con, form, part_id):
    user_query = text("""UPDATE public.pers_view SET nom_part=strip(:nom_part)
                                             , nom_segundo=strip(:nom_segundo)
                                             , seudonimo=strip(:seudonimo)
                                             , nom_materno=strip(:nom_materno)
                                             , nom_paterno=strip(:nom_paterno)
                                             , ciudad=strip(:ciudad)
                                             , nom_subdivision=strip(:nom_subdivision)
                                             , tipo_subdivision=strip(:tipo_subdivision)
                                             , pais=strip(:pais)
                                             , ciudad_muer=strip(:ciudad_muer)
                                             , nom_subdivision_muer=strip(:nom_subdivision_muer)
                                             , tipo_subdivision_muer=strip(:tipo_subdivision_muer)
                                             , pais_muer=strip(:pais_muer)
                                             , fecha_comienzo_insert=:fecha_comienzo
                                             , fecha_finale_insert=:fecha_finale
                                             , sitio_web=strip(:sitio_web)
                                             , direccion=strip(:direccion)
                                             , telefono=strip(:telefono)
                                             , email=strip(:email)
                                             , genero=strip(:genero)
                                             , coment_part=strip(:coment_part)
                                             , mod_id=:mod_id
                                             WHERE part_id=:part_id;""")
    con.execute(user_query, nom_part=form.nom_part.data
                , nom_segundo=form.nom_segundo.data
                , seudonimo=form.seudonimo.data
                , nom_materno=form.nom_materno.data
                , nom_paterno=form.nom_paterno.data
                , ciudad=form.ciudad.data
                , nom_subdivision=form.nom_subdivision.data
                , tipo_subdivision=form.tipo_subdivision.data
                , pais=form.pais.data
                , ciudad_muer=form.ciudad_muer.data
                , nom_subdivision_muer=form.nom_subdivision_muer.data
                , tipo_subdivision_muer=form.tipo_subdivision_muer.data
                , pais_muer=form.pais_muer.data
                , fecha_comienzo=parse_fecha(form.fecha_comienzo.data)
                , fecha_finale=parse_fecha(form.fecha_finale.data)
                , sitio_web=form.sitio_web.data
                , direccion=form.direccion.data
                , telefono=form.telefono.data
                , email=form.email.data
                , genero=form.genero.data
                , coment_part=form.coment_part.data
                , mod_id=session['id']
                , part_id=part_id)
    pers_ag_delete = text("""DELETE FROM public.persona_agregar WHERE persona_id=:part_id""")
    con.execute(pers_ag_delete, part_id=part_id)
    used_ids = []
    for entry in form.org_form.entries:
        ag_id = int(entry.data['agregar_id'])
        if ag_id != 0 and ag_id not in used_ids:
            used_ids.append(ag_id)
            pers_ag_insert = text("""INSERT INTO public.persona_agregar VALUES (:id
                                      , :agregar_id, :fecha_comienzo
                                      , :fecha_finale, strip(:titulo), :id)""")
            con.execute(pers_ag_insert, id=part_id
                        , agregar_id=ag_id
                        , fecha_comienzo=parse_fecha(entry.data['fecha_comienzo'])
                        , fecha_finale=parse_fecha(entry.data['fecha_finale'])
                        , titulo=entry.data['titulo'])


# Queries for the poner_ag view
def populate_poner_ag(con, form, part_id):
    print("id is; " + str(part_id))
    query = text("""SELECT * FROM public.ag_view WHERE part_id=:part_id""")
    user = con.execute(query, part_id=part_id).first()
    print(user.nom_part)

    form.nom_part_ag.data = user.nom_part
    form.fecha_comienzo.data = user.fecha_comienzo
    form.fecha_finale.data = user.fecha_finale
    form.tipo_agregar.data = user.tipo_agregar
    form.coment_part.data = user.coment_part
    form.sitio_web.data = user.sitio_web
    form.direccion.data = user.direccion
    form.email.data = user.email
    form.telefono.data = user.telefono
    form.ciudad.data = user.ciudad
    form.nom_subdivision.data = user.nom_subdivision
    form.tipo_subdivision.data = user.tipo_subdivision
    form.pais.data = user.pais


def update_poner_ag(con, form, part_id):
    user_query = text("""UPDATE public.ag_view SET nom_part=strip(:nom_part_ag)
                                             , ciudad=strip(:ciudad)
                                             , nom_subdivision=strip(:nom_sudivision)
                                             , tipo_subdivision=strip(:tipo_sudivision)
                                             , pais=strip(:pais)
                                             , fecha_comienzo_insert=:fecha_comienzo
                                             , fecha_comienzo_insert=:fecha_comienzo
                                             , sitio_web=strip(:sitio_web)
                                             , direccion=strip(:direccion)
                                             , telefono=strip(:telefono)
                                             , coment_part=strip(:coment_part)
                                             , tipo_agregar=strip(:tipo_agregar)
                                             , mod_id=:mod_id
                                             WHERE part_id=:part_id;""")
    con.execute(user_query, nom_part_ag=form.nom_part_ag.data
                , ciudad=form.ciudad.data
                , nom_subdivision=form.nom_subdivision.data
                , tipo_subdivision=form.tipo_subdivision.data
                , pais=form.pais.data
                , date_formed=parse_fecha(form.fecha_comienzo.data)
                , sitio_web=form.sitio_web.data
                , direccion=form.direccion.data
                , telefono=form.telefono.data
                , coment_part=form.coment_part.data
                , tipo_agregar=form.tipo_agregar.data
                , mod_id=session['id']
                , part_i=part_id)

#
def populate_comp(con, form, comp_id):
    query = text("""SELECT """)

def insert_comp(con, form, usario_id):
    comp_id = int(form.comp_id.data)
    if comp_id == 0:
        comp_id = None
    query = text("""INSERT INTO public.composicion(nom_tit
                                                 , nom_alt
                                                 , fecha_pub
                                                 , composicion_orig
                                                 , texto
                                                 , cargador_id) 
                                                 VALUES (strip(:nom_tit)
                                                       , strip(:nom_alt)
                                                       , :fecha_pub
                                                       , :composicion_orig
                                                       , :texto
                                                       , :cargador_id)
                                                       RETURNING composicion_id""")

    comp_result = con.execute(query, nom_tit=form.nom_tit.data
                     , nom_alt=form.nom_alt.data
                     , fecha_pub=parse_fecha(form.fecha_pub.data)
                     , composicion_orig=comp_id
                     , texto=form.texto.data
                     , cargador_id=usario_id).first()[0]
    used_ids = []
    for entry in form.tema_form.entries:
        tema_id = int(entry.data['tema_id'])
        if tema_id != 0 and tema_id not in used_ids:
            used_ids.append(tema_id)
            tema_comp_insert = text("""INSERT INTO public.tema_composicion VALUES (:comp_id
                                                                              , :tema_id)""")
            con.execute(tema_comp_insert, comp_id=comp_result, tema_id=tema_id)

    used_ids = []
    for entry in form.idioma_form.entries:
        idioma_id = int(entry.data['idioma_id'])
        if idioma_id != 0 and idioma_id not in used_ids:
            used_ids.append(idioma_id)
            idioma_comp_insert = text("""INSERT INTO public.idioma_composicion VALUES (:comp_id
                                                                              , :idioma_id)""")
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
                                        , cargador_id=usario_id)


def insert_pista(con, form, usario_id):
    query_lugar = text("""INSERT INTO public.lugar(ciudad
                                                , nom_subdivision
                                                , tipo_subdivision
                                                , pais) 
                                              VALUES (strip(:ciudad)
                                              , strip(:nom_subdivision)
                                              , :tipo_subdivision
                                              , :pais)
                                            RETURNING lugar_id""")
    result_lugar = con.execute(query_lugar
                               , ciudad=form.ciudad.data
                               , nom_subdivision=form.nom_subdivision.data
                               , tipo_subdivision=form.tipo_subdivision.data
                               , pais=form.pais.data).first()[0]

    query = text("""INSERT INTO public.pista_son(numero_de_pista
                                                , composicion_id
                                                , medio
                                                , lugar_interp
                                                , serie_id
                                                , coment_pista_son
                                                , fecha_grab
                                                , fecha_dig
                                                , fecha_cont
                                                , cargador_id)
                                                 VALUES (:numero_de_pista
                                                        , :composicion_id
                                                        , :medio
                                                        , :lugar_interp
                                                        , :serie_id
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
                     , lugar_interp=result_lugar
                     , serie_id=form.serie_id.data
                     , coment_pista_son=form.coment_pista_son.data
                     , fecha_grab=parse_fecha(form.fecha_grab.data)
                     , fecha_dig=parse_fecha(form.fecha_dig.data)
                     , fecha_cont=parse_fecha(form.fecha_cont.data)
                     , cargador_id=usario_id).first()[0]

    used_ids = []
    for entry in form.gen_mus_form.entries:
        gen_mus_id = int(entry.data['gen_mus_id'])
        if gen_mus_id != 0 and gen_mus_id not in used_ids:
            used_ids.append(gen_mus_id)
            gen_mus_insert = text("""INSERT INTO public.genero_pista VALUES (:pista_son_id
                                                                            , :gen_mus_id)""")
            con.execute(gen_mus_insert, pista_son_id=pista_son_result
                        , gen_mus_id=gen_mus_id)
    used_ids = []
    for entry in form.interp_form.entries:
        tuple_id = (int(entry.data['part_id']), entry.data['rol_pista_son'], entry.data['instrumento_id'])
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
                        , cargador_id=usario_id)



# Query for remove_part view
def delete_part(con, part_id):
    query = text("""DELETE FROM public.participante WHERE part_id=:part_id""")
    con.execute(query, part_id=part_id)


# Queries for init_session
def init_comps(con, part_id):
    comps_query = text("""SELECT composicion_id 
                            FROM public.composicion
                            WHERE cargador_id=:id 
                              AND estado='PENDIENTE'
                              OR estado='PUBLICADO'""")
    comps_result = con.execute(comps_query, id=part_id)
    return [comp[0] for comp in comps_result]


def init_pistas(con, part_id):
    pista_query = text("""SELECT pista_son_id 
                                FROM public.pista_son
                                WHERE cargador_id=:id
                                  AND estado='PENDIENTE'
                                  OR estado='PUBLICADO'""")
    pista_result = con.execute(pista_query, id=part_id)
    return [pista[0] for pista in pista_result]


def init_pers(con, part_id):
    pers_query = text("""SELECT part_id 
                           FROM public.persona
                           WHERE cargador_id=:id
                             AND estado='PENDIENTE'
                             OR estado='PUBLICADO'""")
    pers_result = con.execute(pers_query, id=part_id)
    return [pers[0] for pers in pers_result]


def init_ags(con, part_id):
    ag_query = text("""SELECT part_id 
                           FROM public.agregar
                           WHERE cargador_id=:id
                             AND estado='PENDIENTE'
                             OR estado='PUBLICADO'""")
    ag_result = con.execute(ag_query, id=part_id)
    return [ag[0] for ag in ag_result]
