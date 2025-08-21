-- Kreiranje baze podataka za aplikaciju deljenja fajlova
CREATE DATABASE IF NOT EXISTS room_share CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE room_share;

-- Tabela korisnika
CREATE TABLE korisnici (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ime VARCHAR(50) NOT NULL,
    prezime VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    lozinka_hash VARCHAR(255) NOT NULL,
    smer ENUM('SRT', 'KOT') NULL,
    broj_indeksa VARCHAR(20) NULL,
    rola ENUM('student', 'profesor') DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela soba
CREATE TABLE sobe (
    id INT AUTO_INCREMENT PRIMARY KEY,
    naziv VARCHAR(100) NOT NULL,
    sifra VARCHAR(50) UNIQUE NOT NULL,
    limit_vreme TIMESTAMP NULL,
    creator_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (creator_id) REFERENCES korisnici(id) ON DELETE CASCADE
);

-- Tabela fajlova
CREATE TABLE fajlovi (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_id INT NOT NULL,
    uploader_id INT NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES sobe(id) ON DELETE CASCADE,
    FOREIGN KEY (uploader_id) REFERENCES korisnici(id) ON DELETE CASCADE
);

-- Tabela za praćenje korisnika u sobama
CREATE TABLE korisnici_sobe (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_id INT NOT NULL,
    user_id INT NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES sobe(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES korisnici(id) ON DELETE CASCADE,
    UNIQUE KEY unique_room_user (room_id, user_id)
);

-- Indeksi za bolje performanse
CREATE INDEX idx_korisnici_email ON korisnici(email);
CREATE INDEX idx_sobe_sifra ON sobe(sifra);
CREATE INDEX idx_fajlovi_room ON fajlovi(room_id);
CREATE INDEX idx_fajlovi_uploader ON fajlovi(uploader_id);
CREATE INDEX idx_korisnici_sobe_room ON korisnici_sobe(room_id);
CREATE INDEX idx_korisnici_sobe_user ON korisnici_sobe(user_id);




















