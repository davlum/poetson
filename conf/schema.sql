-- Talk about specifics
CREATE TABLE IF NOT EXISTS lugar ( 
  lugar_id serial PRIMARY KEY
 ,ciudad text NOT NULL
 ,nom_subdivision text
 ,tipo_subdivision text 
 ,pais text NOT NULL
);

COMMENT ON TABLE lugar IS 'City, country, region and specify type of region';

----------------------------------
----- Author related entities ----

CREATE TABLE IF NOT EXISTS autor (
  autor_id serial PRIMARY KEY
 ,coment_autor tsvector
);

COMMENT ON TABLE autor IS 'The author superclass which artista, institucion, and colectivo inherit from.';

CREATE TABLE IF NOT EXISTS genero_artista (
  genero_id serial PRIMARY KEY
 ,genero_nom text UNIQUE NOT NULL
);

COMMENT ON TABLE genero_artista IS 'Comprehensive list of genders. Works as a look up table.';

CREATE TABLE IF NOT EXISTS artista (
  nom_primero text NOT NULL
 ,nom_segundo text
 ,ruta_foto text --/<first letter of artist name>/<artist name>/--hashedfilename
 ,materno_nom text
 ,paterno_nom text
 ,seudonimo text
 ,lugar_nac int REFERENCES lugar
 ,lugar_muer int REFERENCES lugar
 ,fecha_nac fecha
 ,fecha_muer fecha
 ,genero_id int REFERENCES genero_artista
 ,CONSTRAINT artista_id_constr PRIMARY KEY (autor_id)
 ) INHERITS (autor);

COMMENT ON TABLE artista IS 'A singular artist, child class of author';

CREATE TABLE IF NOT EXISTS tipo_institucion (
  tipo_inst_id serial PRIMARY KEY
 ,tipo_inst text UNIQUE NOT NULL
);

COMMENT ON TABLE tipo_institucion IS 'Look up table of abstract institucion type, e.g. streaming service, festival, university.';

CREATE TABLE IF NOT EXISTS institucion (
  institucion_nom text NOT NULL
 ,lugar_id int REFERENCES lugar
 ,tipo_inst int REFERENCES tipo_institucion
 ,fecha_final fecha
 ,CONSTRAINT institucion_id_constr PRIMARY KEY (autor_id)
) INHERITS (autor);

COMMENT ON TABLE institucion IS 'An actual institucion';

CREATE TABLE IF NOT EXISTS colectivo (
  colectivo_nom text NOT NULL
 ,lugar_id int REFERENCES lugar
 ,fecha_comienzo fecha
 ,fecha_final fecha
 ,CONSTRAINT colectivo_id_constr PRIMARY KEY (autor_id)
) INHERITS (autor);

COMMENT ON TABLE colectivo IS 'A collective of authors';

CREATE TABLE IF NOT EXISTS publicador (
  publicador_id serial PRIMARY KEY
 ,autor_id int REFERENCES autor
 ,lugar_id int REFERENCES lugar
 ,tipo tipo_publicador
 ,web_publicador text -- website of publisher
 ,dir_publicador text -- address
 ,email text
 ,telefono text
 ,contact_publicador int REFERENCES autor
 ,coment_publicador tsvector
 ,CONSTRAINT proper_email CHECK (email ~* '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$')
);

COMMENT ON TABLE publicador IS 'Entity that made the resource available, e.g. streaming service or foundation.';

-- This table will be mutable
CREATE TABLE IF NOT EXISTS editor (
  editor_id serial PRIMARY KEY
 ,email text
 ,nom text
 ,apellido text
 ,acceso fecha DEFAULT now()
 ,autor_id int REFERENCES autor 
 ,posicion text DEFAULT 'Servicio social' -- Such as undergrad?
 ,CONSTRAINT proper_email CHECK (email ~* '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$')
);

COMMENT ON TABLE editor IS 'Individual who uploaded the data.';

CREATE TABLE IF NOT EXISTS genero_musical (
  genero_musical serial PRIMARY KEY
 ,nom_genero text UNIQUE NOT NULL
 ,genero_descrip tsvector
);

COMMENT ON TABLE genero_musical IS 'Genres of music. Works as a lookup table.';

CREATE TABLE IF NOT EXISTS idioma (
  idioma_id serial PRIMARY KEY
 ,nom_idioma text UNIQUE NOT NULL
);

COMMENT ON TABLE idioma IS 'Possible Languages. Works as a lookup table.';

CREATE TABLE IF NOT EXISTS serie (
  serie_id serial PRIMARY KEY
 ,nom_serie text NOT NULL
 ,giro text
 ,lugar_id int REFERENCES lugar
);

COMMENT ON TABLE serie IS 'A compilation of pista_son';

CREATE TABLE IF NOT EXISTS album (
  album_id serial PRIMARY KEY
 ,serie_id int REFERENCES serie 
 ,nom_album text
 ,ruta_foto text
);

COMMENT ON TABLE album IS 'a weak entity from serie with nom_album as discrimator.';

CREATE TABLE IF NOT EXISTS familia_instrumento (
  familia_instr_id serial PRIMARY KEY
 ,nom_familia_instr text NOT NULL UNIQUE
);

COMMENT ON TABLE familia_instrumento IS 'Instrument family. Look up table for instrument.';

-- None must be a type of instrument
CREATE TABLE IF NOT EXISTS instrumento (
  instrumento_id serial PRIMARY KEY
 ,nom_inst text DEFAULT 'UNKNOWN'
 ,familia_instr_id int REFERENCES familia_instrumento
 ,electronico boolean
 ,instrumento_comentario tsvector
);

CREATE TABLE IF NOT EXISTS tema (
  tema_id serial PRIMARY KEY
 ,tema_nom text UNIQUE NOT NULL
 ,CONSTRAINT proper_tema CHECK (tema_nom ~ '^[a-zà-ÿ0-9 ()-]+$')
);

COMMENT ON TABLE tema IS 'A tag for the track. Minimum four constraint should be front end. More complex tagging possible';

CREATE TABLE IF NOT EXISTS composicion ( 
  composicion_id serial PRIMARY KEY
 ,nom_tit text NOT NULL
 ,tit_alt text
 ,fecha_pub fecha
 ,fecha_comp fecha
 ,composicion tsvector -- The text itself
 ,lugar_comp int REFERENCES lugar
);

COMMENT ON TABLE composicion IS 'The physical representation of the performed work.';

CREATE TABLE IF NOT EXISTS pista_son (
  pista_son_id serial PRIMARY KEY
 ,nombre_del_archivo text NOT NULL
 ,numero_de_pista int CHECK (numero_de_pista > 1)
 ,composicion_id int REFERENCES composicion
 ,editor_id int REFERENCES editor NOT NULL DEFAULT 1
 ,publicador_id int REFERENCES publicador NOT NULL
 ,medio_id medio 
 ,lugar_interp int REFERENCES lugar
 ,serie_id int REFERENCES serie
 ,comentario_pista_son tsvector
 ,fecha_grab fecha -- fecha recorded
 ,fecha_dig fecha -- fecha digitized
 ,fecha_mod fecha -- fecha migrated
 ,fecha_cont fecha -- fecha donated
 ,fecha_acep fecha -- fecha accepted
 ,fecha_inc timestamp DEFAULT now() -- fecha added
);

COMMENT ON TABLE pista_son IS 'The audio track. Domain Constraint will be put on the front end. Add not null to composicion';
                                 
CREATE TABLE IF NOT EXISTS archivo (
  archivo_id serial PRIMARY KEY
 ,etiqueta text
 ,pista_son_id int REFERENCES pista_son NOT NULL
 ,ruta text NOT NULL -- path of the file /<first letter of artist name>/<artist name>/audio/
 ,duracion TIME NOT NULL
 ,abr int NOT NULL DEFAULT 128000 CHECK (abr > 700)
 ,profundidad_de_bits profundidad_valido
 ,canales int CHECK (canales > 0 AND canales < 12) NOT NULL DEFAULT 2
 ,codec text
 ,frecuencia frecuencia_valido NOT NULL
);

COMMENT ON TABLE archivo IS 'M:1 with pista_son. The different audio codecs that the recorded track is available in.';

-----------------------------------------------------
---------- Relations relating to author -------------

CREATE TABLE IF NOT EXISTS artista_institucion (
  artista_id int REFERENCES artista
 ,institucion_id int REFERENCES institucion
 ,fecha_comienzo fecha
 ,fecha_final fecha
 ,titulo text
 ,PRIMARY KEY (artista_id, institucion_id)
);

COMMENT ON TABLE artista_institucion IS 'M:M relationship of artists and institucions.';

CREATE TABLE IF NOT EXISTS cobertura_tipo (
  cobertura_tipo_id serial PRIMARY KEY
 ,cobertura_tipo text UNIQUE NOT NULL
 ,cobertura_comentario text
);



CREATE TABLE IF NOT EXISTS cobertura (
  cobertura_id serial PRIMARY KEY
 ,cobertura_tipo_id int REFERENCES cobertura_tipo NOT NULL 
 ,pista_son_id int REFERENCES pista_son
 ,composicion_id int REFERENCES composicion
 ,pais_cobertura text NOT NULL
 ,licencia_cobertura text
 ,fecha_comienzo fecha
 ,fecha_final fecha
);

COMMENT ON TABLE cobertura IS 'The copyright associated with a single track.';

CREATE TABLE IF NOT EXISTS cobertura_autor (
  cobertura_id int REFERENCES cobertura
 ,autor_id int REFERENCES autor
 ,PRIMARY KEY (cobertura_id, autor_id)
);

COMMENT ON TABLE cobertura_autor IS 'M:M The copyrights an abstract author may hold.';

CREATE TABLE IF NOT EXISTS composicion_autor (
  composicion_id int REFERENCES composicion
 ,autor_id int REFERENCES autor
 ,tipo_autor tipo_autor
 ,comentario_autor tsvector
 ,PRIMARY KEY (composicion_id, autor_id)
);

COMMENT ON TABLE composicion_autor IS 'M:M The authors involved in a single composicion.';

CREATE TABLE IF NOT EXISTS artista_colectivo (
  artista_id int REFERENCES artista ON DELETE CASCADE
 ,colectivo_id int REFERENCES colectivo ON DELETE CASCADE
 ,fecha_comienzo fecha
 ,fecha_final fecha
 ,PRIMARY KEY (artista_id, colectivo_id)
);

COMMENT ON TABLE artista_colectivo IS 'artists that make up a collective.';

CREATE TABLE IF NOT EXISTS idioma_pista (
  pista_son_id int REFERENCES pista_son
 ,idioma_id int REFERENCES idioma
 ,PRIMARY KEY (pista_son_id, idioma_id)
);

------------------------------------------------------
-------- Other Relationship start here ---------------

COMMENT ON TABLE idioma_pista IS 'M:M relationship of languages and recorded audio.';

CREATE TABLE IF NOT EXISTS genero_pista (
  pista_son_id int REFERENCES pista_son
 ,gen_mus int REFERENCES genero_musical
 ,PRIMARY KEY (pista_son_id, gen_mus)
);

COMMENT ON TABLE genero_pista IS 'M:M relationship of genres and recorded audio.';

CREATE TABLE IF NOT EXISTS intepretacion (
  pista_son_id int REFERENCES pista_son
 ,autor_id int REFERENCES autor
 ,instrumento_id int REFERENCES instrumento DEFAULT 1 
 ,PRIMARY KEY (autor_id, pista_son_id, instrumento_id)
);

COMMENT ON TABLE intepretacion IS 'The interpretacion of a piece. M:M:M of autor, audio track and instrument. 
                                  The default instrument is ninguno which is id 1.';

CREATE TABLE IF NOT EXISTS tema_pista_son (
  pista_son_id int REFERENCES pista_son
 ,tema_id int REFERENCES tema
 ,PRIMARY KEY (pista_son_id, tema_id)
);

COMMENT ON TABLE tema_pista_son IS 'M:M Many tags a single audio track may have.';

