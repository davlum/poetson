# project/main/views.py


#################
#### imports ####
#################

from flask import render_template, Blueprint, request
from sqlalchemy import text
from project import engine
import time


################
#### config ####
################


main_blueprint = Blueprint('main', __name__, template_folder='/main')


################
#### routes ####
################

@main_blueprint.route('/')
def home():
    return render_template('main/home.html')


@main_blueprint.route('/about')
def about():
    return render_template('main/about.html')


@main_blueprint.route('/searchhome')
def searchhome():
    return render_template('main/searchhome.html')


def artista_query(con, param, year_from, year_to, contains):
    if not year_from:
        year_from = '500'
    if not year_to:
        year_to = time.strftime('%Y')
    query = text("""SELECT p.part_id
                          , p.nom_part
                          , p.seudonimo
                          , p.ciudad
                          , p.subdivision
                          , p.pais
                          FROM public.pers_view p 
                          JOIN public.participante_composicion pc
                            ON pc.part_id = p.part_id   
                          WHERE p.nom_part ~* :nom
                            OR p.seudonimo ~* :nom
                            OR p.nom_segundo ~* :nom
                          AND p.fecha_comienzo
                          BETWEEN :year_from AND :year_to
                          AND p.coment_part ~* :contains;""")
    return con.execute(query, nom=param, year_from=year_from, year_to=year_to, contains=contains)


def colectivo_query(con, param, year_from, year_to, contains):
    query = text("""SELECT  a.part_id
                          , a.nom_part
                          , a.ciudad
                          , a.subdivision
                          , a.pais
                          FROM public.ag_view a 
                          JOIN public.participante_composicion pc
                            ON pc.part_id = a.part_id   
                          WHERE a.nom_part ~* :nom
                          AND a.fecha_comienzo
                          BETWEEN :year_from AND :year_to
                          AND a.coment_part ~* :contains;""")
    return con.execute(query, nom=param, year_from=year_from, year_to=year_to, contains=contains)


def composicion_query(con, param, year_from, year_to, contains):
    query = text("""SELECT * FROM public.composicion c
                    LEFT JOIN public.lugar l 
                      ON c.lugar_comp = l.lugar_id
                      WHERE c.nom_tit ~* :nom 
                      OR c.nom_alt ~* :nom
                      AND get_fecha(c.fecha_pub) 
                      BETWEEN :year_from AND :year_to
                      AND c.texto ~* :contains;""")
    return con.execute(query, nom=param, year_from=year_from,year_to=year_to, contains=contains)


def serie_query(con, param, contains):
    query = text("""SELECT * FROM public.serie s
                    LEFT JOIN public.lugar l 
                      ON s.lugar_id = l.lugar_id
                      WHERE s.nom_serie ~* :nom 
                      AND s.giro ~* :contains;""")
    return con.execute(query, nom=param, contains=contains)


def tema_query(con, param, year_from, year_to, contains):
    query = text("""SELECT * FROM public.composicion c
                        JOIN public.tema_composicion tc ON tc.composicion_id = c.composicion_id
                        JOIN public.tema t ON tc.tema_id = t.tema_id
                        WHERE t.nom_tema ~* :nom;""")
    return con.execute(query, nom=param)


def genero_query(con, param, year_from, year_to, contains):
    query = text("""SELECT l.pais
                         , l.subdivision
                         , l.ciudad
                         , c.nom_tit
                         , c.nom_alt 
                         FROM public.pista_son ps
                         LEFT JOIN public.lugar l
                          ON l.lugar_id = ps.lugar_interp
                         JOIN public.genero_pista gp 
                           ON ps.pista_son_id = gp.pista_son_id
                         JOIN public.genero_musical gm
                           ON gm.gen_mus_id = gp.gen_mus_id
                         JOIN public.composicion c
                           ON c.composicion_id = ps.composicion_id
                         JOIN public.serie s
                           ON ps.serie_id = s.serie_id  
                           WHERE gm.nom_genero ~* :nom;""")
    return con.execute(query, nom=param)


# Tries to parse an Int,
# returns an empty string on failure
def parseInt(s):
    try:
        return abs(int(s))
    except ValueError:
        return ""


# The main search page. The logic is designed to be
# comprehensive enough to cover all filtering
@main_blueprint.route('/search')
def search(param=None):
    result = {}
    if request.args.get('filter-by', None):
        param = request.args['search-main']
        filter = int(request.args['filter-by'])
        year_from = parseInt(request.args['ano-start'])
        year_to = parseInt(request.args['ano-end'])
        contains = request.args['contains']
        # General search
        con = engine.connect()
        if filter == 0:
            result['artista'] = artista_query(con, param, year_from, year_to, contains)
            result['colectivo'] = colectivo_query(con, param, year_from, year_to, contains)
            result['composicion'] = composicion_query(con, param, year_from, year_to, contains)
            result['serie'] = serie_query(con, param, contains)
        # Search through artistas
        if filter == 1:
            result['artista'] = artista_query(con, param, year_from, year_to, contains)
        # Search through colectivos
        if filter == 2:
            result['colectivo'] = colectivo_query(con, param, year_from, year_to, contains)
        # search through composicions
        if filter == 3:
            result['composicion'] = composicion_query(con, param, year_from, year_to, contains)
        # Search through serie
        if filter == 4:
            result['serie'] = serie_query(con, param, contains)
        # Search through composicion by Tema
        if filter == 5:
            result['composicion'] = tema_query(con, param, year_from, year_to, contains)
        # Search through pista by Genre
        if filter == 6:
            result['pista'] = genero_query(con, param, year_from, year_to, contains)
        # Search through pista by instrument
        if filter == 7:
            result['pista'] = instrumento_query(con, param, year_from, year_to, contains)
        # Search through composicion by language
        if filter == 8:
            result['composicion'] = idioma_query(con, param, year_from, year_to, contains)
        # Search through pista by performer
        if filter == 9:
            result['pista'] = interp_query(con, param, year_from, year_to, contains)
        con.close()
        return render_template('main/search.html', result=result)


@main_blueprint.route('/autor/<int:autorid>/')
def autor(autorid):
    result = {}
    # _query author
    con = engine.connect()
    author_query = text("""SELECT * FROM part_pers WHERE part_id=:id """)
    author_result = con.execute(author_query, id=autorid).first()

    # _query place_of birth
    lugar_nac_query = text("""SELECT * FROM public.lugar WHERE lugar_id=:id """)
    lugar_nac_result = con.execute(lugar_nac_query, id=author_result.lugar_nac).first()

    # _query place of death
    lugar_muer_query = text("""SELECT * FROM public.lugar WHERE lugar_id=:id """)
    lugar_muer_result = con.execute(lugar_muer_query, id=author_result.lugar_muer).first()

    # _query all compositions including those made by this artist when in a colectivo
    composicion_query = text("""SELECT c.composicion_id
                                     , c.nom_tit
                                     , c.nom_alt
                                     , c.fecha_pub
                                     , l.pais
                                     , l.subdivision
                                     , l.ciudad 
                                  FROM public.persona pers
                                  LEFT JOIN public.persona_grupo pa
                                    ON pers.part_id = pa.persona_id
                                  JOIN public.participante_composicion pc
                                    ON pc.part_id = pa.grupo_id
                                    OR pc.part_id = pers.part_id
                                  JOIN public.composicion c
                                    ON c.composicion_id = pc.composicion_id
                                  LEFT JOIN public.lugar l
                                  ON l.lugar_id = c.lugar_comp
                                  WHERE pers.part_id=:id""")
    result['composicion'] = con.execute(composicion_query, id=autorid)
    con.close()
    return render_template('main/autor.html', autor=author_result, nac=lugar_nac_result,
                           muer=lugar_muer_result, result=result)


@main_blueprint.route('/colectivo/<int:colid>/')
def colectivo(colid):
    result = {}
    # _query colectivo
    con = engine.connect()
    colectivo_query = text("""SELECT *
                                   FROM part_gr 
                                   WHERE part_id=:id;""")
    colectivo = con.execute(colectivo_query, id=colid).first()

    # get the list of artists in that colectivo
    author_query = text("""SELECT p.nom_part
                                , p.nom_paterno
                                , p.seudonimo
                                , p.pais 
                                FROM public.grupo a
                                JOIN public.persona_grupo pa
                                  ON a.part_id = pa.grupo_id
                                JOIN public.pers_view p
                                  ON p.part_id = pa.persona_id 
                                AND a.part_id=:id""")
    result['artista'] = con.execute(author_query, id=colid)

    # _query all compositions including those made by this artist when in a colectivo
    composicion_query = text("""SELECT c.composicion_id
                                     , c.nom_tit
                                     , c.nom_alt
                                     , c.fecha_pub
                                  FROM public.composicion c
                                  JOIN public.participante_composicion pc 
                                  ON pc.composicion_id = c.composicion_id
                                  WHERE pc.part_id=:id""")
    result['composicion'] = con.execute(composicion_query, id=colid)
    con.close()
    return render_template('main/colectivo.html', autor=colectivo, result=result)


@main_blueprint.route('/pistason/<int:pistaid>/')
def pistason(pistaid):
    result = {}
    # _query pista_son
    con = engine.connect()
    pista_query = text("""SELECT * FROM
                              public.pista_son ps
                              JOIN public.composicion c
                                ON ps.composicion_id = c.composicion_id
                              JOIN public.lugar l
                                ON ps.lugar_interp = l.lugar_id
                              JOIN serie s 
                                ON s.serie_id = ps.serie_id
                                WHERE pista_son_id=:id""")
    pista_result = con.execute(pista_query, id=pistaid).first()

    # get the list of Instruments and playters associated with that pista son
    inst_query = text("""SELECT pp.nom_part
                              , pp.nom_segundo
                              , pp.seudonimo
                              , i.nom_inst
                              , pp.part_id 
                                FROM public.participante_pista_son pps
                                JOIN part_pers pp 
                                  ON pp.part_id = pps.part_id 
                                JOIN public.instrumento i 
                                  ON i.instrumento_id = pps.instrumento_id 
                                  WHERE pps.pista_son_id=:id""")
    inst_result = con.execute(inst_query, id=pistaid)

    # _query all the associated files with this query
    archivo_query = text("""SELECT etiqueta
                                 , duracion
                                 , abr
                                 , profundidad_de_bits
                                 , canales
                                 , codec
                                 , frecuencia
                                FROM public.archivo
                                WHERE pista_son_id=:id""")
    archivo_result = con.execute(archivo_query, id=pistaid)
    con.close()
    return render_template('main/pistason.html', pista=pista_result, insts=inst_result, archs=archivo_result)


@main_blueprint.route('/composicion/<int:compoid>/')
def composicion(compoid):
    result = {}
    con = engine.connect()
    # _query Composicion
    composicion_query = text("""SELECT *
                                     FROM public.composicion c
                                     JOIN public.participante_composicion pc
                                       ON c.composicion_id = pc.composicion_id
                                     LEFT JOIN part_pers pp
                                       ON pp.part_id = pc.part_id
                                     LEFT JOIN part_gr pa
                                       ON pa.part_id = pc.part_id
                                     LEFT JOIN public.lugar l 
                                       ON l.lugar_id = c.lugar_comp
                                     WHERE c.composicion_id=:id """)
    composicion_result = con.execute(composicion_query, id=compoid).first()

    # _query all pista son associated with that composicion
    pista_query = text("""SELECT * 
                          FROM public.pista_son ps
                          JOIN public.composicion c 
                            ON ps.composicion_id = c.composicion_id
                          JOIN public.lugar l 
                            ON ps.lugar_interp = l.lugar_id
                          JOIN public.serie s
                            ON s.serie_id = ps.serie_id
                            WHERE c.composicion_id=:id""")
    result['pista'] = con.execute(pista_query, id=compoid)
    con.close()
    return render_template('main/composicion.html', comp=composicion_result, result=result)

@main_blueprint.route('/serie/<int:serieid>/')
def serie(serieid):
    result = {}
    con = engine.connect()
    # _query serie
    serie_query = text("""SELECT s.nom_serie
                             , s.giro
                             , l.pais
                             , l.subdivision
                             , l.ciudad 
                             FROM public.serie s
                             JOIN public.lugar l ON l.lugar_id = s.lugar_id
                             WHERE s.serie_id=:id """)
    serie_result = con.execute(serie_query, id=serieid).first()

    # _query all pista son associated with that serie
    pista_query = text("""SELECT * 
                          FROM public.pista_son ps
                          JOIN public.serie s 
                            ON ps.serie_id = s.serie_id
                          LEFT JOIN public.lugar l 
                            ON ps.lugar_interp = l.lugar_id
                          JOIN public.composicion c
                            ON c.composicion_id = ps.composicion_id
                            WHERE s.serie_id=:id""")
    result['pista'] = con.execute(pista_query, id=serieid)
    con.close()
    return render_template('main/serie.html', serie=serie_result, result=result)

