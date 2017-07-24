-- THINK ABOUT KEEPING IT VERSATILE ENOUGH TO STORE ANALYTICS

CREATE TABLE IF NOT EXISTS poetica_sonora.autor (
  autor_id serial PRIMARY KEY
 ,coment_autor tsvector
);

CREATE TABLE IF NOT EXISTS poetica_sonora.artista (
  nom_primero text NOT NULL
 ,nom_segundo text
 ,apellido text
 ,ruta_foto text --/<first letter of artist name>/<artist name>/--hashedfilename
 ,materno_nom text
 ,paterno_nom text
 ,seudonimo text
 ,local_nac int REFERENCES lugar
 ,local_muer int REFERENCES lugar
 ,fecha_nac date
 ,fecha_muer date
 ,tipo_id int REFERENCES tipo
 ,CONSTRAINT artista_id_constr PRIMARY KEY (autor_id)
) INHERITS (autor);

CREATE TABLE IF NOT EXISTS poetica_sonora.tipo (
  tipo_id serial PRIMARY KEY
 ,tipo_nom text UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS poetica_sonora.artista_institucion (
  artista_id int REFERENCES artista
 ,institucion_id int REFERENCES institucion
 ,fecha_comenzio date
 ,fecha_finale date
 ,titulo text
 ,PRIMARY KEY (artista_id, institucion_id)
);

CREATE TABLE IF NOT EXISTS poetica_sonora.lugar ( 
  lugar_id serial PRIMARY KEY
 ,ciudad text NOT NULL
 ,provincio text NOT NULL
 ,pais text NOT NULL
);

CREATE TABLE IF NOT EXISTS poetica_sonora.colectivo (
  colectivo_nom text NOT NULL
 ,lugar_id int REFERENCES lugar
 ,fecha_comenzio date
 ,fecha_final date
 ,CONSTRAINT colectivo_id_constr PRIMARY KEY (autor_id)
) INHERITS (autor);
 
CREATE TABLE IF NOT EXISTS poetica_sonora.institucion (
  institucion_nom text NOT NULL
 ,lugar_id int REFERENCES lugar
 ,tipo_inst int REFERENCES tipo_institucion
 ,fecha_comenzio date
 ,CONSTRAINT institucion_id_constr PRIMARY KEY (autor_id)
) INHERITS (autor);

CREATE TABLE IF NOT EXISTS poetica_sonora.tipo_institucion (
  tipo_inst_id serial PRIMARY KEY
 ,tipo_inst text UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS poetica_sonora.artista_colectivo (
  artista_id int REFERENCES artista ON DELETE CASCADE
 ,colectivo_id int REFERENCES colectivo ON DELETE CASCADE
 ,PRIMARY KEY (artista_id, colectivo_id)
);

CREATE TABLE IF NOT EXISTS poetica_sonora.publicador (
  publicador_id serial PRIMARY KEY
 ,autor_id int REFERENCES autor
 ,clave_publicador varchar(4) UNIQUE
 ,lugar_id int REFERENCES lugar
 ,web_publidacor text -- website of publisher
 ,dir_publicador text -- address
 ,email text
 ,telefono text
 ,contact_publicador int REFERENCES autor -- maybe not have this as an FK
 ,coment_publicador tsvector
 ,CONSTRAINT proper_email CHECK (email ~* '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$')
);

CREATE TABLE IF NOT EXISTS poetica_sonora.contribuidor (
  contribuidor_id serial PRIMARY KEY 
 ,autor_id int REFERENCES autor
 ,nom_contribuidor text               
 ,clave_contribuidor varchar(4) UNIQUE
 ,sitio_web text
 ,direccion text
 ,email text
 ,telefono text
 ,contrib_contacto text
 ,contrib_comentario tsvector
 ,CONSTRAINT proper_email CHECK (email ~* '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$')
);

CREATE TABLE IF NOT EXISTS poetica_sonora.genero_musical (
  genero_musical serial PRIMARY KEY
 ,nom_genero text UNIQUE NOT NULL
 ,genero_descrip tsvector
);

CREATE TABLE IF NOT EXISTS poetica_sonora.idioma (
  idioma_id serial PRIMARY KEY
 ,nom_idioma text UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS poetica_sonora.serie (
  serie_id serial PRIMARY KEY
 ,nom_serie text NOT NULL
 ,giro text
 ,lugar_id int REFERENCES lugar
);

CREATE TABLE IF NOT EXISTS poetica_sonora.album (
  album_id serial PRIMARY KEY
 ,nom_album text NOT NULL
 ,giro text
 ,lugar_id int REFERENCES lugar
);

CREATE TABLE IF NOT EXISTS poetica_sonora.album_serie (
  album_id int REFERENCES album
 ,serie_id int REFERENCES serie
 ,PRIMARY KEY (album_id, serie_id)
);

-- None mus be a type of instrument
CREATE TABLE IF NOT EXISTS poetica_sonora.instrumento (
  instrumento_id serial PRIMARY KEY
 ,nom_inst text NOT NULL
 ,familia_inst text REFERENCES familia_instrumento
 ,electronico boolean
 ,orig_inst text
 ,marc_inst text
 ,mod_inst text
 ,inv_inst text
 ,instrumento_comentario text
);

CREATE TABLE IF NOT EXISTS poetica_sonora.familia_instrumento (
  nom_familia_inst text PRIMARY KEY
);

-- Where the copyrights of the track apply
CREATE TABLE IF NOT EXISTS poetica_sonora.cobertura (
  cobertura_id serial PRIMARY KEY
 ,pais_cobertura text NOT NULL
 ,license_cobertura text
 ,fecha_comenzio date
 ,fecha_final date
);

CREATE TABLE IF NOT EXISTS poetica_sonora.cobertura_pista (
  cobertura_id int REFERENCES cobertura
 ,pista_son_id int REFERENCES pista_son
 ,PRIMARY KEY (cobertura_id, pista_son_id)
);

CREATE TABLE IF NOT EXISTS poetica_sonora.cobertura_composicion (
  cobertura_id int REFERENCES cobertura
 ,composicion_id int REFERENCES composicion
 ,PRIMARY KEY (cobertura_id, composicion_id)
);

-- This table will be mutable
CREATE TABLE IF NOT EXISTS poetica_sonora.editor (
  editor_id serial PRIMARY KEY
 ,email text
 ,acceso date DEFAULT now()
 ,autor_id int REFERENCES autor -- Necessary?
 ,clave varchar(4) UNIQUE
 ,puesto text DEFAULT 'Servicio social' -- And this
 ,CONSTRAINT proper_email CHECK (email ~* '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$')
);

CREATE TABLE IF NOT EXISTS poetica_sonora.codec (
  codec_id serial PRIMARY KEY
 ,nom_codec text UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS poetica_sonora.pista_son (
  pista_son_id serial PRIMARY KEY
 ,nom_pista text NOT NULL
 ,numero_de_pista int CHECK (numero_de_pista > 1)
 ,composicion_id int REFERENCES composicion NOT NULL
 ,editor_id int REFERENCES editor NOT NULL DEFAULT 1
 ,contribuidor_id int REFERENCES contribuidor NOT NULL
 ,publicador_id int REFERENCES publicador NOT NULL
 ,medio_id medio 
 ,lugar_interp int REFERENCES lugar
 ,serie_id int REFERENCES serie
 ,album_id int REFERENCES album
 ,etiqueta text
 ,comentario tsvector
 ,fecha_grab date -- date recorded
 ,fecha_dig date -- date digitized
 ,fecha_mod date -- date migrated
 ,fecha_cont date -- date donated
 ,fecha_acep date -- date accepted
 ,fecha_inc timestamp DEFAULT now() -- date added
);

-- SOUNDFILE                                  
CREATE TABLE IF NOT EXISTS poetica_sonora.archivo (
  archivo_id serial PRIMARY KEY
 ,pista_son_id int REFERENCES pista_son NOT NULL
 ,ruta text NOT NULL -- path of the file /<first letter of artist name>/<artist name>/audio/
 ,duracion TIME NOT NULL
 ,abr int NOT NULL DEFAULT 128000 CHECK (abr > 700)
 ,profundidad_de_bits profundidad_valido
 ,canales int CHECK (canales > 0 AND canales < 12) NOT NULL DEFAULT 2
 ,codec int REFERENCES codec 
 ,frecuencia frecuencia_valido NOT NULL
 ,tamano numeric(5,2) NOT NULL -- in MBs
);  

CREATE TABLE IF NOT EXISTS poetica_sonora.genero_pista (
  pista_son_id int REFERENCES pista_son
 ,gen_mus int REFERENCES genero_musical
 ,PRIMARY KEY (pista_son_id, gen_mus)
);

CREATE TABLE IF NOT EXISTS poetica_sonora.idioma_pista (
  pista_son_id int REFERENCES pista_son
 ,idioma_id int REFERENCES idioma
 ,PRIMARY KEY (pista_son_id, idioma_id)
);

CREATE TABLE IF NOT EXISTS poetica_sonora.intepretacion (
  pista_son_id int REFERENCES pista_son
 ,autor_id int REFERENCES autor
 ,instrumento_id int REFERENCES instrumento
 ,PRIMARY KEY (autor_id, pista_son_id, instrumento_id)
);

CREATE TABLE IF NOT EXISTS poetica_sonora.composicion_autor (
  composicion_id int REFERENCES composicion
 ,autor_id int REFERENCES autor
 ,tipo_autor tipo_autor
 ,PRIMARY KEY (composicion_id, autor_id)
);

CREATE TABLE IF NOT EXISTS poetica_sonora.composicion ( -- what is this? composition? own entity or relation
  composicion_id serial PRIMARY KEY
 ,nom_tit text NOT NULL
 ,tit_alt text
 ,ano_pub int CONSTRAINT ano_pub_constr CHECK (ano_pub > 1000 AND ano_pub < 3000)
 ,fecha_comp date -- Null
 ,composicion tsvector -- Text itself
 ,lugar_comp int REFERENCES lugar -- place reference place entity
);

CREATE TABLE IF NOT EXISTS poetica_sonora.termas (
  terma_id serial PRIMARY KEY
 ,terma text UNIQUE NOT NULL
 ,CONSTRAINT proper_terma CHECK (terma ~ '[a-z][a-z0-9_]+')
);

CREATE TABLE IF NOT EXISTS poetica_sonora.termas_pista_son (
  pista_son_id int REFERENCES pista_son
 ,terma_id int REFERENCES termas
 ,PRIMARY KEY (pista_son_id, terma_id)
);

-- List all indexes at end, make sure to include FKs and tsvectors. Use GIN
