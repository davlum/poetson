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

INSERT INTO public.cobertura_tipo  VALUES
('Dominio público', 'Sin licencia'),
('Copyleft débil', 'Permisos liberados sin limitaciones hasta donde la legislación de cada país lo permita'),
('Copyleft fuerte', 'Permisos liberados pero con ciertas limitaciones'),
('Licencia propietaria', 'Algunos permisos restringidos'),
('Secreto comercial', 'Todos los permisos restringidos'),
('Desconocido', 'Tipo de licencia no identificado');

INSERT INTO public.cobertura_licencia (licencia_cobertura, tipo_cob) VALUES
('(CC BY) Creative Commons Atribución', 'Copyleft fuerte'),
('(CC BY-SA) Creative Commons Atribución-CompartirIgual', 'Copyleft fuerte'),
('(CC BY-ND)Creative Commons Atribución-SinDerivadas', 'Copyleft fuerte'),
('(CC BY-NC) Creative Commons Atribución-NoComercial', 'Copyleft fuerte'),
('(CC BY-NC-SA) Creative Commons Atribución-NoComercial-CompartirIgual', 'Copyleft fuerte'),
('(CC BY-NC-ND) Creative Commons Atribución-NoComercial-SinDerivadas', 'Copyleft fuerte'),
('(CC0) Sin derechos reservados', 'Copyleft débil'),
('(GPL) Licencia pública general GNU', 'Copyleft fuerte'),
('(C) Copyright', 'Licencia propietaria'),
('(LGPL) Licencia pública menos general GNU', 'Copyleft débil'),
('Dominio público', 'Dominio público'),
('Patente', 'Secreto comercial'),
('Por confirmar', 'Desconocido');