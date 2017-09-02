# project/main/views.py


#################
#### imports ####
#################

from flask import render_template, Blueprint, request
from sqlalchemy import text
from project import db
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


def artistaQuery(param, yearFrom, yearTo, contains):
    if not yearFrom:
        yearFrom = '500'
    if not yearTo:
        yearTo = time.strftime('%Y')
    query = text("""SELECT pp.part_id
                          , pp.nom_part
                          , pp.nom_segundo
                          , pp.seudonimo
                          , l.ciudad
                          , l.nom_subdivision
                          , l.pais
                          FROM part_pers pp 
                          LEFT JOIN public.lugar l
                            ON l.lugar_id = pp.lugar_nac
                          JOIN public.participante_composicion pc
                            ON pc.part_id = pp.part_id   
                          WHERE pp.nom_part ~* :nom
                            OR pp.seudonimo ~* :nom
                          AND get_fecha(pp.pers_comienzo)
                          BETWEEN :yearFrom AND :yearTo
                          AND pp.coment_participante ~* :contains;""")
    return db.engine.execute(query, nom=param, yearFrom=yearFrom,
                             yearTo=yearTo, contains=contains)


def colectivoQuery(param, yearFrom, yearTo, contains):
    query = text("""SELECT pa.part_id
                          , pa.nom_part
                          , pa.ciudad
                          , pa.nom_subdivision
                          , pa.pais
                          FROM part_ag pa 
                          JOIN public.participante_composicion pc
                            ON pc.part_id = pa.part_id   
                          WHERE pa.nom_part ~* :nom
                          AND get_fecha(pa.fecha_comienzo) 
                          BETWEEN :yearFrom AND :yearTo
                          AND pa.coment_participante ~* :contains;""")
    return db.engine.execute(query, nom=param, yearFrom=yearFrom,
                             yearTo=yearTo, contains=contains)



def composicionQuery(param, yearFrom, yearTo, contains):
    query = text("""SELECT * FROM public.composicion c
                    LEFT JOIN public.lugar l 
                      ON c.lugar_comp = l.lugar_id
                      WHERE c.nom_tit ~* :nom 
                      OR c.nom_alt ~* :nom
                      AND get_fecha(c.fecha_pub) 
                      BETWEEN :yearFrom AND :yearTo
                      AND c.texto ~* :contains;""")
    return db.engine.execute(query, nom=param, yearFrom=yearFrom,
                             yearTo=yearTo, contains=contains)


def serieQuery(param, contains):
    query = text("""SELECT * FROM public.serie s
                    LEFT JOIN public.lugar l 
                      ON s.lugar_id = l.lugar_id
                      WHERE s.nom_serie ~* :nom 
                      AND s.giro ~* :contains;""")
    return db.engine.execute(query, nom=param, contains=contains)


def temaQuery(param, yearFrom, yearTo, contains):
    query = text("""SELECT * FROM public.composicion c
                        JOIN public.tema_composicion tc ON tc.composicion_id = c.composicion_id
                        JOIN public.tema t ON tc.tema_id = t.tema_id
                        WHERE t.nom_tema ~* :nom;""")
    return db.engine.execute(query, nom=param)


def generoQuery(param, yearFrom, yearTo, contains):
    query = text("""SELECT l.pais
                         , l.nom_subdivision
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
    return db.engine.execute(query, nom=param)



def instrumentoQuery(param, yearFrom, yearTo, containas):
    artista_query = text("""SELECT * FROM public.artista WHERE nom_primero ~* :name OR 
                          nom_segundo ~* :name;""")
    return db.engine.execute(artista_query, name=param)


def idiomaQuery(param, yearFrom, yearTo, containas):
    artista_query = text("""SELECT * FROM public.artista WHERE nom_primero ~* :name OR 
                          nom_segundo ~* :name;""")
    return db.engine.execute(artista_query, name=param)


def interpQuery(param, yearFrom, yearTo, containas):
    artista_query = text("""SELECT * FROM public.artista WHERE nom_primero ~* :name OR 
                          nom_segundo ~* :name;""")
    return db.engine.execute(artista_query, name=param)


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
        filt = int(request.args['filter-by'])
        yearFrom = parseInt(request.args['ano-start'])
        yearTo = parseInt(request.args['ano-end'])
        contains = request.args['contains']
        # General search
        if filt == 0:
            result['artista'] = artistaQuery(param, yearFrom, yearTo, contains)
            result['colectivo'] = colectivoQuery(param, yearFrom, yearTo, contains)
            result['composicion'] = composicionQuery(param, yearFrom, yearTo, contains)
            result['serie'] = serieQuery(param, contains)
        # Search through artistas
        if filt == 1:
            result['artista'] = artistaQuery(param, yearFrom, yearTo, contains)
        # Search through colectivos
        if filt == 2:
            result['colectivo'] = colectivoQuery(param, yearFrom, yearTo, contains)
        # search through composicions
        if filt == 3:
            result['composicion'] = composicionQuery(param, yearFrom, yearTo, contains)
        # Search through serie
        if filt == 4:
            result['serie'] = serieQuery(param, contains)
        # Search through composicion by Tema
        if filt == 5:
            result['composicion'] = temaQuery(param, yearFrom, yearTo, contains)
        # Search through pista by Genre
        if filt == 6:
            result['pista'] = generoQuery(param, yearFrom, yearTo, contains)
        # Search through pista by instrument
        if filt == 7:
            result['pista'] = instrumentoQuery(param, yearFrom, yearTo, contains)
        # Search through composicion by language
        if filt == 8:
            result['composicion'] = idiomaQuery(param, yearFrom, yearTo, contains)
        # Search through pista by performer
        if filt == 9:
            result['pista'] = interpQuery(param, yearFrom, yearTo, contains)
        return render_template('main/search.html', result=result)


@main_blueprint.route('/autor/<int:autorid>/')
def autor(autorid):
    result = {}
    # Query author
    author_query = text("""SELECT * FROM part_pers WHERE part_id=:id """)
    author_result = db.engine.execute(author_query, id=autorid).first()

    # Query place_of birth
    lugar_nac_query = text("""SELECT * FROM public.lugar WHERE lugar_id=:id """)
    lugar_nac_result = db.engine.execute(lugar_nac_query, id=author_result.lugar_nac).first()

    # Query place of death
    lugar_muer_query = text("""SELECT * FROM public.lugar WHERE lugar_id=:id """)
    lugar_muer_result = db.engine.execute(lugar_muer_query, id=author_result.lugar_muer).first()

    # Query all compositions including those made by this artist when in a colectivo
    composicion_query = text("""SELECT c.composicion_id
                                     , c.nom_tit
                                     , c.nom_alt
                                     , c.fecha_pub
                                     , l.pais
                                     , l.nom_subdivision
                                     , l.ciudad 
                                  FROM public.persona pers
                                  LEFT JOIN public.persona_agregar pa
                                    ON pers.part_id = pa.persona_id
                                  JOIN public.participante_composicion pc
                                    ON pc.part_id = pa.agregar_id
                                    OR pc.part_id = pers.part_id
                                  JOIN public.composicion c
                                    ON c.composicion_id = pc.composicion_id
                                  LEFT JOIN public.lugar l
                                  ON l.lugar_id = c.lugar_comp
                                  WHERE pers.part_id=:id""")
    result['composicion'] = db.engine.execute(composicion_query, id=autorid)

    return render_template('main/autor.html', autor=author_result, nac=lugar_nac_result,
                           muer=lugar_muer_result, result=result)


@main_blueprint.route('/colectivo/<int:colid>/')
def colectivo(colid):
    result = {}
    # Query colectivo
    colectivo_query = text("""SELECT *
                                   FROM part_ag 
                                   WHERE part_id=:id;""")
    colectivo = db.engine.execute(colectivo_query, id=colid).first()

    # get the list of artists in that colectivo
    author_query = text("""SELECT a.nom_primero
                                , a.nom_segundo
                                , a.seudonimo
                                , l.pais 
                                FROM part_ag paa
                                JOIN persona_agregar pea
                                  ON paa.part_id = pea.agregar_id
                                JOIN part_pers pp
                                  ON pp.part_id = pea.persona_id 
                                JOIN public.lugar l 
                                  ON l.lugar_id = pp.lugar_nac
                                WHERE paa.tipo_agregar = 'colectivo' 
                                AND paa.part_id=:id""")
    result['artista'] = db.engine.execute(author_query, id=colid)

    # Query all compositions including those made by this artist when in a colectivo
    composicion_query = text("""SELECT c.composicion_id
                                     , c.nom_tit
                                     , c.nom_alt
                                     , c.fecha_pub
                                     , c.lugar_comp 
                                  FROM public.composicion c
                                  JOIN public.participante_composicion pc 
                                  ON pc.composicion_id = c.composicion_id
                                  WHERE pc.part_id=:id""")
    result['composicion'] = db.engine.execute(composicion_query, id=colid)

    return render_template('main/colectivo.html', autor=colectivo, result=result)


@main_blueprint.route('/pistason/<int:pistaid>/')
def pistason(pistaid):
    result = {}
    # Query pista_son
    pista_query = text("""SELECT * FROM
                              public.pista_son ps
                              JOIN public.composicion c
                                ON ps.composicion_id = c.composicion_id
                              JOIN public.lugar l
                                ON ps.lugar_interp = l.lugar_id
                              JOIN serie s 
                                ON s.serie_id = ps.serie_id
                                WHERE pista_son_id=:id""")
    pista_result = db.engine.execute(pista_query, id=pistaid).first()

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
    inst_result = db.engine.execute(inst_query, id=pistaid)

    # Query all the associated files with this query
    archivo_query = text("""SELECT etiqueta
                                 , duracion
                                 , abr
                                 , profundidad_de_bits
                                 , canales
                                 , codec
                                 , frecuencia
                                FROM public.archivo
                                WHERE pista_son_id=:id""")
    archivo_result = db.engine.execute(archivo_query, id=pistaid)

    return render_template('main/pistason.html', pista=pista_result, insts=inst_result, archs=archivo_result)


@main_blueprint.route('/composicion/<int:compoid>/')
def composicion(compoid):
    result = {}

    # Query Composicion
    composicion_query = text("""SELECT *
                                     FROM public.composicion c
                                     JOIN public.participante_composicion pc
                                       ON c.composicion_id = pc.composicion_id
                                     LEFT JOIN part_pers pp
                                       ON pp.part_id = pc.part_id
                                     LEFT JOIN part_ag pa
                                       ON pa.part_id = pc.part_id
                                     LEFT JOIN public.lugar l 
                                       ON l.lugar_id = c.lugar_comp
                                     WHERE c.composicion_id=:id """)
    composicion_result = db.engine.execute(composicion_query, id=compoid).first()


    # Query all pista son associated with that composicion
    pista_query = text("""SELECT * 
                          FROM public.pista_son ps
                          JOIN public.composicion c 
                            ON ps.composicion_id = c.composicion_id
                          JOIN public.lugar l 
                            ON ps.lugar_interp = l.lugar_id
                          JOIN public.serie s
                            ON s.serie_id = ps.serie_id
                            WHERE c.composicion_id=:id""")
    result['pista'] = db.engine.execute(pista_query, id=compoid)

    return render_template('main/composicion.html', comp=composicion_result, result=result)

@main_blueprint.route('/serie/<int:serieid>/')
def serie(serieid):
    result = {}

    # Query serie
    serie_query = text("""SELECT s.nom_serie
                             , s.giro
                             , l.pais
                             , l.nom_subdivision
                             , l.ciudad 
                             FROM public.serie s
                             JOIN public.lugar l ON l.lugar_id = s.lugar_id
                             WHERE s.serie_id=:id """)
    serie_result = db.engine.execute(serie_query, id=serieid).first()


    # Query all pista son associated with that serie
    pista_query = text("""SELECT * 
                          FROM public.pista_son ps
                          JOIN public.serie s 
                            ON ps.serie_id = s.serie_id
                          LEFT JOIN public.lugar l 
                            ON ps.lugar_interp = l.lugar_id
                          JOIN public.composicion c
                            ON c.composicion_id = ps.composicion_id
                            WHERE s.serie_id=:id""")
    result['pista'] = db.engine.execute(pista_query, id=serieid)

    return render_template('main/serie.html', serie=serie_result, result=result)

