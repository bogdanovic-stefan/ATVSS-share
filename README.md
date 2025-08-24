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

Proverite da li su podaci za konekciju ispravni:
   ```py
    'host': 'localhost_ili_drugo_ime',
    'port': vas_port (3306),
    'user': 'ime_usera',
    'password': 'vasa_lozinka',
    'database': 'room_share',
    'charset': 'utf8mb4'

   ```

## Korak 3: Instalacija backend-a

CMD:
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

## Korak 4: Instalacija frontend-a

CMD:
cd frontend
npm install

## Korak 5: Pokretanje aplikacije


**Terminal 1 - Backend:**
CMD:
cd backend
python app.py

**Terminal 2 - Frontend:**
CMD:
cd frontend
npm run dev

## Pristup aplikaciji

- **Frontend:** http://localhost:8080
- **Backend API:** http://localhost:5000

## Prvi koraci

1. Otvorite http://localhost:8080 u browseru
2. Registrujte se kao student
3. Prijavite se sa kreiranim nalogom
4. Kreirajte sobu ili pridružite se postojećoj

## Dodavanje profesora

Profesori se tako sto se prvo registruje kao student i onda se preko sql u bazi promeni rola sa "student" na "profesor"

```sql
UPDATE korisnici 
SET rola = 'profesor', 
    smer = NULL, 
    broj_indeksa = NULL 
WHERE email = 'markomarkovic@gmail.com';
```

## Rešavanje problema

### Problem sa konekcijom na bazu
- Proverite da li MySQL server radi
- Proverite port
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




















