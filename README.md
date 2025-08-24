# Instrukcije za Instalaciju i Pokretanje

## Preduslovi

1. **Python 3.8+** - [Preuzmite sa python.org](https://www.python.org/downloads/)
2. **Node.js 16+** - [Preuzmite sa nodejs.org](https://nodejs.org/)
3. **MySQL Server** - [Preuzmite sa mysql.com](https://dev.mysql.com/downloads/mysql/)
4. **MySQL Workbench** - [Preuzmite sa mysql.com](https://dev.mysql.com/downloads/workbench/)

## Korak 1: Kreiranje baze podataka

1. Otvorite MySQL Workbench
2. Povežite se na vašu MySQL instancu (localhost:3306)
3. Otvorite fajl `database/schema.sql`
4. Pokrenite skriptu za kreiranje baze podataka

## Korak 2: Konfiguracija backend-a

1. Otvorite `backend/config.env`
2. Proverite da li su podaci za konekciju ispravni:
   ```
   DB_HOST=127.0.0.1
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=vaša_lozinka
   DB_NAME=room_share
   JWT_SECRET_KEY=vas_jwt_kljuc_123
   FLASK_SECRET_KEY=vas_flask_kljuc_456
   ```

## Korak 3: Instalacija backend-a

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Korak 4: Instalacija frontend-a

```bash
cd frontend
npm install
```

## Korak 5: Pokretanje aplikacije

### Opcija 1: Automatsko pokretanje (Windows)
```bash
start.bat
```

### Opcija 2: Ručno pokretanje

**Terminal 1 - Backend:**
```bash
cd backend
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run serve
```

## Pristup aplikaciji

- **Frontend:** http://localhost:8080
- **Backend API:** http://localhost:5000

## Prvi koraci

1. Otvorite http://localhost:8080 u browseru
2. Registrujte se kao student
3. Prijavite se sa kreiranim nalogom
4. Kreirajte sobu ili pridružite se postojećoj

## Dodavanje profesora

Profesori se dodaju direktno u bazu podataka:

```sql
INSERT INTO korisnici (ime, prezime, email, lozinka_hash, rola) 
VALUES ('Ime', 'Prezime', 'profesor@fakultet.com', 'hash_lozinke', 'profesor');
```

Za hash-ovanje lozinke koristite bcrypt sa salt-om.

## Rešavanje problema

### Problem sa konekcijom na bazu
- Proverite da li MySQL server radi
- Proverite port (3307)
- Proverite korisničko ime i lozinku

### Problem sa CORS
- Backend je konfigurisan za CORS
- Frontend koristi proxy za development

### Problem sa upload-om fajlova
- Proverite da li `backend/uploads` direktorijum postoji
- Proverite dozvole za pisanje

## Struktura projekta

```
room-share/
├── backend/
│   ├── app.py              # Flask aplikacija
│   ├── requirements.txt    # Python zavisnosti
│   ├── config.env         # Konfiguracija
│   └── uploads/           # Upload-ovani fajlovi
├── frontend/
│   ├── src/
│   │   ├── views/         # Vue komponente
│   │   ├── store/         # Vuex store
│   │   └── router/        # Vue Router
│   ├── package.json       # Node.js zavisnosti
│   └── vue.config.js      # Vue konfiguracija
├── database/
│   └── schema.sql         # SQL skripta za bazu
└── README.md              # Opis projekta
```




















