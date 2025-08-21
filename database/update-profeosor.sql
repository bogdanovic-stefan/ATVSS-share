-- Promeni profesora
UPDATE korisnici 
SET rola = 'profesor', 
    smer = NULL, 
    broj_indeksa = NULL 
WHERE email = 'markomarkovic@gmail.com';