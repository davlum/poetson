# project/main/views.py


#################
#### imports ####
#################

from flask import render_template, Blueprint, request, redirect, url_for, abort
from sqlalchemy import text
from project import engine
from project.main.models import composicion_query, colectivo_query, autor_query, serie_query, genero_query, \
    tema_query, instrumento_query, interp_query, idioma_query, comp_autor_view, pers_grupo_view, comp_grupo_view, \
    comp_view_query, pista_archivo_view, serie_view, comp_serie_view

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


def add_tags(old_tags, new_tags):
    if not isinstance(old_tags, dict):
        old_tags = {res[0]: res.count for res in old_tags}
    new_tags = {res[0]: res.count for res in new_tags}
    return {k: old_tags.get(k, 0) + new_tags.get(k, 0) for k in set(old_tags) | set(new_tags)}


# The main search page. The logic is designed to be
# comprehensive enough to cover all filtering
@main_blueprint.route('/search')
def search():
    result = {}
    if request.args.get('filter-by', None):
        param = request.args['search-main']
        filt = request.args['filter-by']
        year_from = parse_int(request.args['ano-start'])
        year_to = parse_int(request.args['ano-end'])
        contains = request.args['contains']
        # General search
        con = engine.connect()
        if filt == 'all':
            result['pers'], new_lugars, \
            result['genders'], new_usuarios = autor_query(con, param, year_from, year_to, contains)
            result['usuarios'] = {res[0]: res.count for res in new_usuarios}
            result['lugars'] = {res[0]: res.count for res in new_lugars}

            result['grupos'], new_lugars, \
            new_usuarios = colectivo_query(con, param, year_from, year_to, contains)
            result['usuarios'] = add_tags(result['usuarios'], new_usuarios)
            result['lugars'] = add_tags(result['lugars'], new_lugars)

            result['comps'], result['temas'], \
            result['idiomas'], result['generos'], \
            new_usuarios = composicion_query(con, param, year_from, year_to, contains)
            result['usuarios'] = add_tags(result['usuarios'], new_usuarios)

            result['serie'] = serie_query(con, param, contains)
        # Search through artistas
        if filt == 'autor':
            result['pers'], new_lugars, \
            result['genders'], new_usuarios = autor_query(con, param, year_from, year_to, contains)
            result['usuarios'] = {res[0]: res.count for res in new_usuarios}
            result['lugars'] = {res[0]: res.count for res in new_lugars}
        # Search through colectivos
        if filt == 'colectivo':
            result['grupos'], new_lugars, \
            new_usuarios = colectivo_query(con, param, year_from, year_to, contains)
            result['usuarios'] = {res[0]: res.count for res in new_usuarios}
            result['lugars'] = {res[0]: res.count for res in new_lugars}
        # search through composicions
        if filt == 'composicion':
            result['comps'], result['temas'], \
            result['idiomas'], result['generos'], \
            new_usuarios = composicion_query(con, param, year_from, year_to, contains)
            result['usuarios'] = {res[0]: res.count for res in new_usuarios}
        # Search through serie
        if filt == 'serie':
            result['serie'] = serie_query(con, param, contains)
        # Search through comps by Tema
        if filt == 'tema':
            result['comps'], result['temas'], \
            result['idiomas'], result['generos'], \
            new_usuarios = tema_query(con, param, year_from, year_to, contains)
            result['usuarios'] = {res[0]: res.count for res in new_usuarios}
        # Search through comps by Genre
        if filt == 'genero':
            result['comps'], result['temas'], \
            result['idiomas'], result['generos'], \
            new_usuarios = genero_query(con, param, year_from, year_to, contains)
            result['usuarios'] = {res[0]: res.count for res in new_usuarios}
        # Search through comps by instrument
        if filt == 'instrumento':
            result['comps'], result['temas'], \
            result['idiomas'], result['generos'], \
            new_usuarios = instrumento_query(con, param, year_from, year_to, contains)
            result['usuarios'] = {res[0]: res.count for res in new_usuarios}
        # Search through comps by language
        if filt == 'idioma':
            result['comps'], result['temas'], \
            result['idiomas'], result['generos'], \
            new_usuarios = idioma_query(con, param, year_from, year_to, contains)
            result['usuarios'] = {res[0]: res.count for res in new_usuarios}
        # Search through pista by performer
        if filt == 'interp':
            result['comps'], result['temas'], \
            result['idiomas'], result['generos'], \
            new_usuarios = interp_query(con, param, year_from, year_to, contains)
            result['usuarios'] = {res[0]: res.count for res in new_usuarios}
        con.close()
    return render_template('main/search.html', result=result)


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

