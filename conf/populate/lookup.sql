INSERT INTO public.medio VALUES ('Digital'), ('CD'), ('Cinta'),('Vinilo');

INSERT INTO public.permiso VALUES ('EDITOR'), ('MOD'), ('ADMIN');

INSERT INTO public.rol_composicion VALUES
('Compositor'),
('Traductor');

INSERT INTO public.rol_pista_son VALUES
('Lectura en voz alta'),
('Interpretación musical'),
('Ingeniería de sonido'),
('Producción'),
('Dirección'),
('Post-producción'),
('Auxiliar de sonido');

INSERT INTO public.cobertura_tipo (cobertura_tipo, cobertura_comentario) VALUES
('Dominio público', 'Sin licencia'),
('Copyleft débil', 'Permisos liberados sin limitaciones hasta donde la legislación de cada país lo permita'),
('Copyleft fuerte', 'Permisos liberados pero con ciertas limitaciones'),
('Licencia propietaria', 'Algunos permisos restringidos'),
('Secreto comercial', 'Todos los permisos restringidos'),
('Desconocido', 'Tipo de licencia no identificado');

INSERT INTO public.cobertura (licencia_cobertura, cobertura_tipo) VALUES
('(C) Copyright', 4),
('(CC BY) Creative Commons Atribución', 3),
('(CC BY-SA) Creative Commons Atribución-CompartirIgual', 3),
('(CC BY-ND)Creative Commons Atribución-SinDerivadas', 3),
('(CC BY-NC) Creative Commons Atribución-NoComercial', 3),
('(CC BY-NC-SA) Creative Commons Atribución-NoComercial-CompartirIgual', 3),
('(CC BY-NC-ND) Creative Commons Atribución-NoComercial-SinDerivadas', 3),
('(CC0) Sin derechos reservados', 2),
('(GPL) Licencia pública general GNU', 3),
('(LGPL) Licencia pública menos general GNU', 2),
('Dominio público', 1),
('Patente', 5),
('Por confirmar', 6);