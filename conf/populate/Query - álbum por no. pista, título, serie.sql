SELECT c.nom_tit AS "Título", a.nom_album AS "Álbum", p.numero_de_pista AS "No. pista", s.nom_serie AS "Serie" FROM pista_son AS "p", composicion AS "c", album AS "a", serie AS "s"
WHERE (a.serie_id=s.serie_id) AND (p.serie_id=s.serie_id) AND (c.composicion_id=p.composicion_id)
ORDER BY nom_serie, nom_album, numero_de_pista;