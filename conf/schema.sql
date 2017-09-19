-- LOOK UP TABLES FOR THE DATABASE
CREATE TABLE medio (
  nom_medio text PRIMARY KEY
);


CREATE TABLE IF NOT EXISTS rol_pista_son(
  nom_rol_pista text PRIMARY KEY
);


CREATE TABLE IF NOT EXISTS rol_composicion (
  nom_rol_comp text PRIMARY KEY
);


CREATE TABLE IF NOT EXISTS pais (
    nom_pais text PRIMARY KEY
);


CREATE TABLE IF NOT EXISTS lugar ( 
    lugar_id serial PRIMARY KEY
  , ciudad text
  , subdivision text
  , pais text REFERENCES pais
);

COMMENT ON TABLE lugar IS 'City, country, region and specify type of region';


----------------------------------
----- Author related entities ----

CREATE TABLE IF NOT EXISTS participante (
    part_id serial PRIMARY KEY
);

COMMENT ON TABLE participante IS 'The author superclass which persona, grupo, and grupo inherit from.';


CREATE TABLE IF NOT EXISTS genero_persona (
    nom_genero text PRIMARY KEY
);

COMMENT ON TABLE genero_persona IS 'Comprehensive list of genders. Works as a look up table.';

-- CREATE INDEXES ON NAMES AND STUFF
CREATE TABLE IF NOT EXISTS persona (
    part_id int REFERENCES participante ON DELETE CASCADE PRIMARY KEY
  , nom_paterno text
  , nom_materno text
  , seudonimo text
  , ruta_foto text --/<first letter of artist name>/<artist name>/--hashedfilename
  , lugar_muer int REFERENCES lugar
  , genero text REFERENCES genero_persona

    -- Common attributes between persona and grupo
  , email text UNIQUE
  , nom_part text
  , sitio_web text
  , direccion text
  , telefono text
  , lugar_id int REFERENCES lugar
  , fecha_comienzo fecha
  , fecha_finale fecha
  , coment_part text
  , CONSTRAINT proper_email CHECK (email ~* '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$')
);

COMMENT ON TABLE persona IS 'A singular person.';

CREATE TABLE IF NOT EXISTS tipo_grupo (
    nom_tipo_grupo text PRIMARY KEY
);

COMMENT ON TABLE tipo_grupo IS 'Look up table of abstract agregate type, e.g. streaming service, festival, university.';

CREATE TABLE IF NOT EXISTS grupo (
    part_id int REFERENCES participante ON DELETE CASCADE PRIMARY KEY
  , tipo_grupo text REFERENCES tipo_grupo

    -- Common attributes between persona and grupo
  , email text UNIQUE
  , nom_part text
  , sitio_web text
  , direccion text
  , telefono text
  , lugar_id int REFERENCES lugar
  , fecha_comienzo fecha
  , fecha_finale fecha
  , coment_part text
  , CONSTRAINT proper_email CHECK (email ~* '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$')
);

COMMENT ON TABLE grupo IS 'An agregate of people.';


CREATE TABLE IF NOT EXISTS permiso (
  nom_permiso text PRIMARY KEY
);



-- This table will be mutable
CREATE TABLE IF NOT EXISTS usuario (
    usuario_id int REFERENCES participante ON DELETE RESTRICT PRIMARY KEY
  , confirmado boolean NOT NULL DEFAULT false
  , nom_usuario text NOT NULL UNIQUE
  , contrasena text NOT NULL -- hashed and salted
  , gr_email text UNIQUE REFERENCES grupo(email) ON UPDATE CASCADE
  , pers_email text UNIQUE REFERENCES persona(email) ON UPDATE CASCADE
  , fecha_registro TIMESTAMP WITH TIME ZONE DEFAULT now()
  , fecha_confirmado TIMESTAMP WITH TIME ZONE
  , permiso text NOT NULL DEFAULT 'EDITOR' REFERENCES permiso
  , prohibido boolean NOT NULL DEFAULT FALSE
  , CONSTRAINT proper_nom CHECK (nom_usuario ~* '^[a-zÀ-ÿ0-9_-]+$')
  , CONSTRAINT tipo_email CHECK ((gr_email IS NULL AND pers_email IS NOT NULL) OR
                                 (gr_email IS NOT NULL AND pers_email IS NULL))
);

COMMENT ON TABLE usuario IS 'Individual who uploaded the data.';

CREATE TABLE IF NOT EXISTS genero_musical (
    gen_mus_id serial PRIMARY KEY
   ,nom_gen_mus text UNIQUE NOT NULL
   ,coment_gen_mus text
);

COMMENT ON TABLE genero_musical IS 'Genres of music. Works as a lookup table.';


CREATE TABLE IF NOT EXISTS idioma (
    idioma_id serial PRIMARY KEY
   ,nom_idioma text UNIQUE NOT NULL
);

COMMENT ON TABLE idioma IS 'Possible Languages. Works as a lookup table.';

-- search giro?
CREATE TABLE IF NOT EXISTS serie (
    serie_id serial PRIMARY KEY
   ,nom_serie text NOT NULL
   ,giro text
);

COMMENT ON TABLE serie IS 'A compilation of pista_son';


CREATE TABLE IF NOT EXISTS album (
    album_id serial PRIMARY KEY
   ,serie_id int REFERENCES serie ON DELETE CASCADE
   ,nom_album text
   ,ruta_foto text
);

COMMENT ON TABLE album IS 'a 1:M relationship from serie.';


CREATE TABLE IF NOT EXISTS familia_instrumento (
    familia_instr_id serial PRIMARY KEY
   ,nom_familia_instr text NOT NULL UNIQUE
);

COMMENT ON TABLE familia_instrumento IS 'Instrument family. Look up table for instrument.';


-- None must be a type of instrument
CREATE TABLE IF NOT EXISTS instrumento (
    instrumento_id serial PRIMARY KEY
   ,nom_inst text NOT NULL
   ,familia_instr_id int REFERENCES familia_instrumento ON DELETE SET NULL
   ,electronico boolean
   ,instrumento_comentario text
);


CREATE TABLE IF NOT EXISTS tema (
    tema_id serial PRIMARY KEY
   ,nom_tema text UNIQUE NOT NULL
   ,CONSTRAINT proper_tema CHECK (nom_tema ~ '^[a-zà-ÿ0-9_()-]+$')
);

COMMENT ON TABLE tema IS 'A tag for the track. Minimum four constraint should be front end. More complex tagging possible';


CREATE TABLE IF NOT EXISTS composicion ( 
    composicion_id serial PRIMARY KEY
   ,nom_tit text NOT NULL
   ,nom_alt text
   ,fecha_pub fecha
   ,composicion_orig int REFERENCES composicion ON DELETE SET NULL
   ,texto text -- The text itself
);

COMMENT ON TABLE composicion IS 'The physical representation of the performed work.';


CREATE TABLE IF NOT EXISTS pista_son (
    pista_son_id serial PRIMARY KEY
   ,numero_de_pista int CHECK (numero_de_pista > 0)
   ,composicion_id int REFERENCES composicion ON DELETE RESTRICT
   ,medio text REFERENCES medio
   ,lugar_interp int REFERENCES lugar
   ,serie_id int REFERENCES serie ON DELETE SET NULL
   ,coment_pista_son text
   ,fecha_grab fecha -- fecha recorded
   ,fecha_dig fecha -- fecha digitized
   ,fecha_cont fecha -- fecha donated
);

COMMENT ON TABLE pista_son IS 'The audio track. Domain Constraint will be put on the front end. Add not null to composicion';
                                 
CREATE TABLE IF NOT EXISTS archivo (
    archivo_id serial PRIMARY KEY
   ,etiqueta text  -- What is this one more time
   ,nom_archivo text NOT NULL
   ,pista_son_id int NOT NULL -- REFERENCES pista_son
    -- but this row can be present if the
    -- referenced row is not publicly available,
    -- As it may reside in the audit table
   ,duracion int NOT NULL -- in seconds
   ,abr int NOT NULL
   ,canales int NOT NULL
   ,codec text
   ,frecuencia int
);

COMMENT ON TABLE archivo IS 'M:1 with pista_son. The different audio codecs that the recorded track is available in.';

-----------------------------------------------------
---------- Relations relating to author -------------

CREATE TABLE IF NOT EXISTS persona_grupo (
    persona_id int REFERENCES persona ON DELETE CASCADE
  , grupo_id int REFERENCES grupo ON DELETE CASCADE
  , fecha_comienzo fecha
  , fecha_finale fecha
  , titulo text
  , PRIMARY KEY (persona_id, grupo_id)
);

COMMENT ON TABLE persona_grupo IS 'M:M relationship of person and grupos.';


CREATE TABLE IF NOT EXISTS cobertura_tipo (
    tipo_cob text PRIMARY KEY
  , coment_cob text
);


CREATE TABLE IF NOT EXISTS cobertura_licencia (
    cobertura_lic_id serial PRIMARY KEY
   ,tipo_cob text REFERENCES cobertura_tipo
   ,licencia_cobertura text
);

CREATE TABLE IF NOT EXISTS cobertura (
    cobertura_id serial PRIMARY KEY
   ,cobertura_lic_id int NOT NULL REFERENCES cobertura_licencia
   ,pista_son_id int REFERENCES pista_son ON DELETE SET NULL
   ,composicion_id int REFERENCES composicion ON DELETE SET NULL
   ,pais_cobertura text REFERENCES pais
   ,fecha_comienzo fecha
   ,fecha_finale fecha
);

COMMENT ON TABLE cobertura IS 'The copyright associated with a single track.';


CREATE TABLE IF NOT EXISTS participante_cobertura (
    cobertura_id int REFERENCES cobertura ON DELETE CASCADE
   ,part_id int REFERENCES participante ON DELETE CASCADE
   ,PRIMARY KEY (cobertura_id, part_id)
);

COMMENT ON TABLE participante_cobertura IS 'M:M The copyrights a participante may hold.';

CREATE TABLE IF NOT EXISTS participante_composicion (
    composicion_id int REFERENCES composicion ON DELETE CASCADE
  , part_id int REFERENCES participante ON DELETE CASCADE
  , rol_composicion text REFERENCES rol_composicion
  , datos_personalizados json
  , PRIMARY KEY (composicion_id, part_id, rol_composicion)
);

COMMENT ON TABLE participante_composicion IS $body$ 
M:M The many possible different types of relations
as specified by rol_composicion that might occur between a
participante and a composicion. $body$;

CREATE TABLE IF NOT EXISTS participante_pista_son (
    pista_son_id int REFERENCES pista_son ON DELETE CASCADE
  , part_id int REFERENCES participante ON DELETE CASCADE
  , rol_pista_son text REFERENCES rol_pista_son
  , instrumento_id int DEFAULT 1 REFERENCES instrumento ON DELETE SET DEFAULT
  , datos_personalizados json
  , PRIMARY KEY (pista_son_id, part_id, rol_pista_son, instrumento_id)
);

COMMENT ON TABLE participante_pista_son IS $body$
M:M The many possible different types of relations
as specified by rol_pista_son that might occur between a
participante and a pista_son. $body$;

CREATE TABLE IF NOT EXISTS idioma_composicion (
    composicion_id int REFERENCES composicion ON DELETE CASCADE
   ,idioma_id int REFERENCES idioma ON DELETE CASCADE
   ,PRIMARY KEY (composicion_id, idioma_id)
);

COMMENT ON TABLE idioma_composicion IS 'M:M relationship of languages and the composicion.';

------------------------------------------------------
-------- Other Relationship start here ---------------


CREATE TABLE IF NOT EXISTS genero_pista (
    pista_son_id int REFERENCES pista_son ON DELETE CASCADE
  , gen_mus_id int REFERENCES genero_musical ON DELETE CASCADE
  , PRIMARY KEY (pista_son_id, gen_mus_id)
);

COMMENT ON TABLE genero_pista IS 'M:M relationship of genres and recorded audio.';


CREATE TABLE IF NOT EXISTS tema_composicion (
    composicion_id int REFERENCES composicion ON DELETE CASCADE
   ,tema_id int REFERENCES tema ON DELETE CASCADE
   ,PRIMARY KEY (composicion_id, tema_id)
);

COMMENT ON TABLE tema_composicion IS 'M:M Many tags a single audio track may have.';





