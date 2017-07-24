CREATE TYPE tipo_autor AS ENUM ('Primero', 'Segundo');

CREATE TYPE medio AS ENUM ('Digital', 'CD', 'Tape', 'Vinyl');

CREATE DOMAIN profundidad_valido int CHECK (VALUE = 4 OR
                                            VALUE = 8 OR
                                            VALUE = 11 OR
                                            VALUE = 16 OR
                                            VALUE = 20 OR
                                            VALUE = 24 OR
                                            VALUE = 32 OR
                                            VALUE = 48 OR
                                            VALUE = 64); 

CREATE DOMAIN frecuencia_valido int CHECK (VALUE = 8000 OR
                                           VALUE = 11025 OR
                                           VALUE = 16000 OR
                                           VALUE = 22050 OR
                                           VALUE = 32000 OR
                                           VALUE = 37800 OR
                                           VALUE = 44056 OR
                                           VALUE = 44100 OR
                                           VALUE = 47250 OR
                                           VALUE = 48000 OR
                                           VALUE = 50000 OR
                                           VALUE = 50400 OR
                                           VALUE = 88200 OR
                                           VALUE = 96000 OR
                                           VALUE = 176400 OR
                                           VALUE = 192000 OR
                                           VALUE = 176400 OR
                                           VALUE = 192000 OR 
                                           VALUE = 352800 OR
                                           VALUE = 2822400 OR
                                           VALUE = 5644800);


