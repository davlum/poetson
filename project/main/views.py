# project/main/views.py


#################
#### imports ####
#################

from flask import render_template, Blueprint, request, redirect, url_for, abort
from sqlalchemy import text
from project import engine
from project.main.models import composicion_query, colectivo_query, autor_query, serie_query, genero_query, \
    tema_query, instrumento_query, interp_query, idioma_query, comp_autor_view, pers_grupo_view, comp_grupo_view, \
    comp_view_query, pista_archivo_view, serie_view, comp_serie_view, genero_autor_query, usuario_comp_query, \
    usuario_autor_query, usuario_colectivo_query, lugar_autor_query, lugar_colectivo_query, lugar_comp_query

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


# Tries to parse an Int,
# returns an empty string on failure
def parse_int(s):
    try:
        return abs(int(s))
    except ValueError:
        return None





# The main search page. The logic is designed to be
# comprehensive enough to cover all filtering
@main_blueprint.route('/search')
def search():
    result = {}
    bind_params = {}
    if request.args.get('filtrado', None):
        bind_params['nom'] = request.args['nom']
        filt = request.args['filtrado']
        bind_params['year_from'] = parse_int(request.args['ano-comienzo'])
        bind_params['year_to'] = parse_int(request.args['ano-finale'])
        bind_params['contains'] = request.args['comentario']
        # General search
        con = engine.connect()
        if filt == 'all':
            autor_query(con, bind_params, result)
            colectivo_query(con, bind_params, result)
            composicion_query(con, bind_params, result)
            serie_query(con, bind_params, result)
        # Search through artistas
        if filt == 'autor':
            autor_query(con, bind_params, result)
        # Search through colectivos
        if filt == 'colectivo':
            colectivo_query(con, bind_params, result)
        # search through composicions
        if filt == 'composicion':
            composicion_query(con, bind_params, result)
        # Search through serie
        if filt == 'serie':
            serie_query(con, bind_params, result)
        # Search through comps by Tema
        if filt == 'tema':
            tema_query(con, bind_params, result)
        # Search through comps by Genre
        if filt == 'genero':
            genero_query(con, bind_params, result)
        # Search through comps by instrument
        if filt == 'instrumento':
            instrumento_query(con, bind_params, result)
        # Search through comps by language
        if filt == 'idioma':
            idioma_query(con, bind_params, result)
        # Search through pista by performer
        if filt == 'interp':
            interp_query(con, bind_params, result)
        if filt == 'gender':
            genero_autor_query(con, bind_params, result)
        if filt == 'usuario':
            usuario_autor_query(con, bind_params, result)
            usuario_colectivo_query(con, bind_params, result)
            usuario_comp_query(con, bind_params, result)
        if filt == 'ciudad' or filt == 'subdivision' or filt == 'pais':
            lugar_colectivo_query(con, bind_params, result, filt)
            lugar_comp_query(con, bind_params, result, filt)
            lugar_autor_query(con, bind_params, result, filt)
        con.close()
    return render_template('main/search.html', result=result, bind_params=bind_params)


@main_blueprint.route('/autor/<int:part_id>/')
def autor(part_id):
    result = {}
    # _query author
    con = engine.connect()
    author_query = text("""SELECT * FROM public.pers_view WHERE part_id=:part_id AND estado = 'PUBLICADO'""")
    author = con.execute(author_query, part_id=part_id).first()
    if author is None:
        abort(404)
    result['comps'] = comp_autor_view(con, part_id)
    con.close()
    return render_template('main/autor.html', autor=author, result=result)


@main_blueprint.route('/colectivo/<int:part_id>/')
def colectivo(part_id):
    result = {}
    # query colectivo
    con = engine.connect()
    colectivo_query = text("""SELECT * FROM public.gr_view WHERE part_id=:part_id AND estado = 'PUBLICADO'""")
    colectivo = con.execute(colectivo_query, part_id=part_id).first()
    if colectivo is None:
        abort(404)
    result['pers'] = pers_grupo_view(con, part_id)
    result['comps'] = comp_grupo_view(con, part_id)
    con.close()
    return render_template('main/colectivo.html', autor=colectivo, result=result)


@main_blueprint.route('/composicion/<int:comp_id>/')
def composicion(comp_id):
    result = {}
    con = engine.connect()
    # query composicion ths composicion
    comp, autors = comp_view_query(con, comp_id)
    if comp is None:
        abort(404)
    result = pista_archivo_view(con, comp_id)
    con.close()
    return render_template('main/composicion.html', comp=comp, autors=autors, result=result)


@main_blueprint.route('/serie/<int:serie_id>/')
def serie(serie_id):
    result = {}
    con = engine.connect()
    # query serie
    serie = serie_view(con, serie_id)
    if serie is None:
        abort(404)
    # query all pista son associated with that serie
    result['comps'] = comp_serie_view(con, serie_id)
    con.close()
    return render_template('main/serie.html', serie=serie, result=result)

