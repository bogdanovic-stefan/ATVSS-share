from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import pymysql
import bcrypt
import os
import uuid
from datetime import datetime, timedelta
import json
from contextlib import contextmanager

# -----------------------------------------------> Konfiguracija <-------------------------------------------------------

# Direktna konfiguracija baze podataka
DB_CONFIG = {
    'host': 'localhost',
    'port': 3307,
    'user': 'root',
    'password': 'root',
    'database': 'room_share',
    'charset': 'utf8mb4'
}

# -----------------------------------------------> Baza podataka - povezivanje <-------------------------------------------------------

# Funkcija za konekciju sa bazom
def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

# Kontekst menadzer za operacije baze podataka
@contextmanager
def get_db_cursor():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# JWT i Flask konfiguracija
JWT_SECRET_KEY = 'vasa_stvarna_jwt_tajna_kljuc'
FLASK_SECRET_KEY = 'vasa_stvarna_flask_tajna_kljuc'

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB

# Omogucavanje CORS-a
CORS(app)

# Inicijalizacija JWT
jwt = JWTManager(app)

# -----------------------------------------------> Greske - obavestenja <-------------------------------------------------------

# JWT gresake
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    print("JWT token expired")
    return jsonify({'error': 'Token je istekao'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    print(f"Invalid JWT token: {error}")
    return jsonify({'error': 'Nevažeći token'}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    print(f"Missing JWT token: {error}")
    return jsonify({'error': 'Token je obavezan'}), 401

# Ostale greske
@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'Fajl je prevelik. Maksimalna veličina je 100 MB.'}), 413

# -----------------------------------------------> Pomocne funkcije <-------------------------------------------------------

# Kreiranje uploads direktorijuma ako ne postoji
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

 

# Funkcija za hash-ovanje lozinke
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Funkcija za proveru lozinke
def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# Funkcija za brisanje isteklih soba
def cleanup_expired_rooms():
    """Brisanje soba koje su istekle i oslobadjanje sifri"""
    try:
        with get_db_cursor() as cursor:
            # Pronalazenje isteklih soba
            cursor.execute("""
                SELECT id, sifra FROM sobe 
                WHERE limit_vreme IS NOT NULL AND limit_vreme < NOW()
            """)
            
            expired_rooms = cursor.fetchall()
            
            if expired_rooms:
                print(f"Brisanje {len(expired_rooms)} isteklih soba...")
                
                for room in expired_rooms:
                    room_id, sifra = room
                    
                    # Brisanje fajlova iz sobe
                    cursor.execute("DELETE FROM fajlovi WHERE room_id = %s", (room_id,))
                    
                    # Brisanje korisnika iz sobe
                    cursor.execute("DELETE FROM korisnici_sobe WHERE room_id = %s", (room_id,))
                    
                    # Brisanje sobe
                    cursor.execute("DELETE FROM sobe WHERE id = %s", (room_id,))
                    
                    print(f"Obrisana soba {room_id} sa šifrom '{sifra}'")
                
                print(f"Uspešno obrisano {len(expired_rooms)} isteklih soba")
        
    except Exception as e:
        print(f"Greška pri brisanju isteklih soba: {str(e)}")

# -----------------------------------------------> Autentifikacija <-------------------------------------------------------

@app.route('/register', methods=['POST'])
def register():
    """Registracija novog studenta"""
    try:
        data = request.get_json()
        
        # Validacija podataka
        required_fields = ['ime', 'prezime', 'email', 'smer', 'broj_indeksa', 'lozinka']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Polje {field} je obavezno'}), 400
        
        # Hash-ovanje lozinke
        hashed_password = hash_password(data['lozinka'])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Provera da li email već postoji
        cursor.execute("SELECT id FROM korisnici WHERE email = %s", (data['email'],))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Email već postoji'}), 400
        
        # Unos novog korisnika
        cursor.execute("""
            INSERT INTO korisnici (ime, prezime, email, lozinka_hash, smer, broj_indeksa, rola)
            VALUES (%s, %s, %s, %s, %s, %s, 'student')
        """, (data['ime'], data['prezime'], data['email'], hashed_password, 
              data['smer'], data['broj_indeksa']))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Uspešna registracija'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    """Prijava korisnika"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('lozinka'):
            return jsonify({'error': 'Email i lozinka su obavezni'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Pronalazenje korisnika
        cursor.execute("""
            SELECT id, ime, prezime, email, lozinka_hash, smer, broj_indeksa, rola
            FROM korisnici WHERE email = %s
        """, (data['email'],))
        
        user = cursor.fetchone()
        conn.close()
        
        if not user or not check_password(data['lozinka'], user[4]):  # lozinka_hash je na indeksu 4
            return jsonify({'error': 'Pogrešan email ili lozinka'}), 401
        
        # Kreiranje JWT tokena
        access_token = create_access_token(identity=str(user[0]))  # id je na indeksu 0
        
        return jsonify({
            'token': access_token,
            'user': {
                'id': user[0],
                'ime': user[1],
                'prezime': user[2],
                'email': user[3],
                'smer': user[5],
                'broj_indeksa': user[6],
                'rola': user[7]
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -----------------------------------------------> Profil korisnika <-------------------------------------------------------

@app.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Дохватање профила корисника"""
    try:
        user_id = int(get_jwt_identity())
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, ime, prezime, email, smer, broj_indeksa, rola
            FROM korisnici WHERE id = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({'error': 'Korisnik nije pronađen'}), 404
        
        return jsonify({
            'id': user[0],
            'ime': user[1],
            'prezime': user[2],
            'email': user[3],
            'smer': user[4],
            'broj_indeksa': user[5],
            'rola': user[6]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Ažuriranje profila korisnika"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Validacija podataka
        if not data.get('ime') or not data.get('prezime') or not data.get('smer') or not data.get('broj_indeksa'):
            return jsonify({'error': 'Sva polja su obavezna'}), 400
        
        # Validacija smera
        if data.get('smer') not in ['SRT', 'KOT']:
            return jsonify({'error': 'Smer mora biti SRT ili KOT'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Azuriranje podataka (osim email-a i role)
        cursor.execute("""
            UPDATE korisnici 
            SET ime = %s, prezime = %s, smer = %s, broj_indeksa = %s
            WHERE id = %s
        """, (data.get('ime'), data.get('prezime'), data.get('smer'), 
              data.get('broj_indeksa'), user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Profil uspešno ažuriran'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -----------------------------------------------> Upravljanje sobama <-------------------------------------------------------

@app.route('/rooms', methods=['POST'])
@jwt_required()
def create_room():
    """Kreiranje nove sobe"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data.get('naziv') or not data.get('sifra'):
            return jsonify({'error': 'Naziv i šifra sobe su obavezni'}), 400
        
        # Provera da li je korisnik profesor
        with get_db_cursor() as cursor:
            cursor.execute("SELECT rola FROM korisnici WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            
            if not user or user[0] != 'profesor':
                return jsonify({'error': 'Samo profesori mogu da kreiraju sobe'}), 403
            
            # Automatsko ciscenje isteklih soba pre kreiranja nove
            cleanup_expired_rooms()
            
            # Izracunavanje limit vremena ako je navedeno
            limit_vreme = None
            if data.get('limit_sati'):
                limit_vreme = datetime.now() + timedelta(hours=int(data['limit_sati']))
            
            # Provera da li sifra vec postoji
            cursor.execute("SELECT id FROM sobe WHERE sifra = %s", (data['sifra'],))
            if cursor.fetchone():
                return jsonify({'error': 'Šifra sobe već postoji'}), 400
            
            # Kreiranje sobe
            cursor.execute("""
                INSERT INTO sobe (naziv, sifra, limit_vreme, creator_id)
                VALUES (%s, %s, %s, %s)
            """, (data['naziv'], data['sifra'], limit_vreme, user_id))
            
            room_id = cursor.lastrowid
            
            # Dodavanje kreatora u sobu
            cursor.execute("""
                INSERT INTO korisnici_sobe (room_id, user_id)
                VALUES (%s, %s)
            """, (room_id, user_id))
            
            return jsonify({
                'message': 'Soba uspešno kreirana',
                'room_id': room_id
            }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/rooms/join', methods=['POST'])
@jwt_required()
def join_room():
    """Pridruživanje sobi pomoću šifre"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data.get('sifra'):
            return jsonify({'error': 'Šifra sobe je obavezna'}), 400
        
        # Automatsko ciscenje isteklih soba pre pridruživanja
        cleanup_expired_rooms()
        
        with get_db_cursor() as cursor:
            # Pronalazenje sobe
            cursor.execute("SELECT id, naziv FROM sobe WHERE sifra = %s", (data['sifra'],))
            room = cursor.fetchone()
            
            if not room:
                return jsonify({'error': 'Soba sa tom šifrom ne postoji'}), 404
            
            # Provera da li je korisnik vec u sobi
            cursor.execute("""
                SELECT id FROM korisnici_sobe 
                WHERE room_id = %s AND user_id = %s
            """, (room[0], user_id))  # room[0] je id
            
            if cursor.fetchone():
                return jsonify({'error': 'Već ste u ovoj sobi'}), 400
            
            # Dodavanje korisnika u sobu
            cursor.execute("""
                INSERT INTO korisnici_sobe (room_id, user_id)
                VALUES (%s, %s)
            """, (room[0], user_id))  # room[0] je id
            
            return jsonify({
                'message': 'Uspešno pridruživanje sobi',
                'room_id': room[0],  # room[0] je id
                'room_name': room[1]  # room[1] je naziv
            }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Lista soba korisnika (za Dashboard)
@app.route('/user/rooms', methods=['GET'])
@jwt_required()
def get_user_rooms():
    """Dobijanje soba u kojima je korisnik učlanjen"""
    try:
        user_id = int(get_jwt_identity())
        
        # Automatsko ciscenje isteklih soba pre prikazivanja
        cleanup_expired_rooms()
        
        with get_db_cursor() as cursor:
            # Pronalazenje soba u kojima je korisnik uclanjen
            query = """
                SELECT s.id, s.naziv, s.sifra, s.created_at, k.ime, k.prezime
                FROM sobe s
                JOIN korisnici_sobe ks ON s.id = ks.room_id
                JOIN korisnici k ON s.creator_id = k.id
                WHERE ks.user_id = %s
                ORDER BY s.created_at DESC
            """
            
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
            
            rooms = []
            for row in rows:
                room = {
                    'id': row[0],
                    'naziv': row[1],
                    'sifra': row[2],
                    'created_at': row[3].isoformat() if row[3] else None,
                    'creator_name': f"{row[4]} {row[5]}"
                }
                rooms.append(room)
            
            return jsonify(rooms)
        
    except Exception as e:
        print(f"ERROR in get_user_rooms: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# -----------------------------------------------> Sobe (informacije/napuštanje/brisanje) <-------------------------------

@app.route('/rooms/<int:room_id>', methods=['GET'])
@jwt_required()
def get_room_info(room_id):
    """Dohvatanje informacija o sobi"""
    try:
        user_id = int(get_jwt_identity())
        
        with get_db_cursor() as cursor:
            # Provera da li je korisnik u sobi
            cursor.execute("""
                SELECT id FROM korisnici_sobe 
                WHERE room_id = %s AND user_id = %s
            """, (room_id, user_id))
            
            if not cursor.fetchone():
                return jsonify({'error': 'Niste u ovoj sobi'}), 403
            
            # Dohvatanje informacija o sobi
            cursor.execute("""
                SELECT s.id, s.naziv, s.sifra, s.created_at, s.limit_vreme, s.creator_id,
                       k.ime, k.prezime
                FROM sobe s
                JOIN korisnici k ON s.creator_id = k.id
                WHERE s.id = %s
            """, (room_id,))
            
            room = cursor.fetchone()
            
            if not room:
                return jsonify({'error': 'Soba nije pronađena'}), 404
            
            return jsonify({
                'id': room[0],
                'naziv': room[1],
                'sifra': room[2],
                'created_at': room[3].isoformat() if room[3] else None,
                'limit_vreme': room[4].isoformat() if room[4] else None,
                'creator_id': room[5],
                'creator_name': f"{room[6]} {room[7]}"
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

 

@app.route('/rooms/<int:room_id>/leave', methods=['POST'])
@jwt_required()
def leave_room(room_id):
    """Napuštanje sobe"""
    try:
        user_id = int(get_jwt_identity())
        
        with get_db_cursor() as cursor:
            # Provera da li je korisnik u sobi
            cursor.execute("""
                SELECT id FROM korisnici_sobe 
                WHERE room_id = %s AND user_id = %s
            """, (room_id, user_id))
            
            if not cursor.fetchone():
                return jsonify({'error': 'Niste u ovoj sobi'}), 400
            
            # Uklanjanje korisnika iz sobe
            cursor.execute("""
                DELETE FROM korisnici_sobe 
                WHERE room_id = %s AND user_id = %s
            """, (room_id, user_id))
            
            return jsonify({'message': 'Uspešno napuštanje sobe'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/rooms/<int:room_id>', methods=['DELETE'])
@jwt_required()
def delete_room(room_id):
    """Brisanje sobe (samo kreator može)"""
    try:
        user_id = int(get_jwt_identity())
        
        with get_db_cursor() as cursor:
            # Provera da li je korisnik kreator sobe
            cursor.execute("""
                SELECT creator_id FROM sobe WHERE id = %s
            """, (room_id,))
            
            room = cursor.fetchone()
            if not room:
                return jsonify({'error': 'Soba nije pronađena'}), 404
            
            if room[0] != user_id:
                return jsonify({'error': 'Možete brisati samo sobe koje ste kreirali'}), 403
            
            # Brisanje svih fajlova iz sobe
            cursor.execute("SELECT stored_filename FROM fajlovi WHERE room_id = %s", (room_id,))
            files = cursor.fetchall()
            
            for file in files:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file[0])
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            # Brisanje fajlova iz baze
            cursor.execute("DELETE FROM fajlovi WHERE room_id = %s", (room_id,))
            
            # Brisanje korisnika iz sobe
            cursor.execute("DELETE FROM korisnici_sobe WHERE room_id = %s", (room_id,))
            
            # Brisanje sobe
            cursor.execute("DELETE FROM sobe WHERE id = %s", (room_id,))
            
            return jsonify({'message': 'Soba uspešno obrisana'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -----------------------------------------------> Upravljanje fajlovima <-------------------------------------------------------

@app.route('/rooms/<int:room_id>/files', methods=['GET'])
@jwt_required()
def get_room_files(room_id):
    """Dohvatanje liste fajlova u sobi"""
    try:
        user_id = int(get_jwt_identity())
        
        with get_db_cursor() as cursor:
            # Provera da li je korisnik u sobi
            cursor.execute("""
                SELECT id FROM korisnici_sobe 
                WHERE room_id = %s AND user_id = %s
            """, (room_id, user_id))
            
            if not cursor.fetchone():
                return jsonify({'error': 'Niste u ovoj sobi'}), 403
            
            # Dohvatanje fajlova
            cursor.execute("""
                SELECT f.id, f.original_filename, f.upload_time, 
                       k.ime, k.prezime, f.uploader_id, f.room_id
                FROM fajlovi f
                JOIN korisnici k ON f.uploader_id = k.id
                WHERE f.room_id = %s
                ORDER BY f.upload_time DESC
            """, (room_id,))
            
            rows = cursor.fetchall()
            
            # Formatiranje podataka u objekte
            files = []
            for row in rows:
                files.append({
                    'id': row[0],
                    'original_filename': row[1],
                    'upload_time': row[2].isoformat() if row[2] else None,
                    'ime': row[3],
                    'prezime': row[4],
                    'uploader_id': row[5],
                    'room_id': row[6]
                })
            
            return jsonify(files), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/rooms/<int:room_id>/files', methods=['POST'])
@jwt_required()
def upload_file(room_id):
    """Upload fajla u sobu"""
    try:
        user_id = int(get_jwt_identity())
        
        if 'file' not in request.files:
            return jsonify({'error': 'Nema fajla'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nema izabranog fajla'}), 400
        
        with get_db_cursor() as cursor:
            # Provera da li je korisnik u sobi
            cursor.execute("""
                SELECT id FROM korisnici_sobe 
                WHERE room_id = %s AND user_id = %s
            """, (room_id, user_id))
            
            if not cursor.fetchone():
                return jsonify({'error': 'Niste u ovoj sobi'}), 403
            
            # Generisanje jedinstvenog imena fajla
            file_extension = os.path.splitext(file.filename)[1]
            stored_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], stored_filename)
            
            # Cuvanje fajla
            file.save(file_path)
            
            # Unos u bazu
            cursor.execute("""
                INSERT INTO fajlovi (room_id, uploader_id, original_filename, stored_filename)
                VALUES (%s, %s, %s, %s)
            """, (room_id, user_id, file.filename, stored_filename))
            
            return jsonify({'message': 'Fajl uspešno postavljen'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/files/<int:file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    """Brisanje fajla (samo uploader može)"""
    try:
        user_id = int(get_jwt_identity())
        
        with get_db_cursor() as cursor:
            # Pronalaženje fajla
            cursor.execute("""
                SELECT stored_filename, uploader_id, room_id FROM fajlovi WHERE id = %s
            """, (file_id,))
            
            file = cursor.fetchone()
            if not file:
                return jsonify({'error': 'Fajl nije pronađen'}), 404
            
            # Provera da li je korisnik u sobi
            cursor.execute("""
                SELECT id FROM korisnici_sobe 
                WHERE room_id = %s AND user_id = %s
            """, (file[2], user_id))  # file[2] je room_id
            
            if not cursor.fetchone():
                return jsonify({'error': 'Niste u ovoj sobi'}), 403
            
            # Provera da li je korisnik uploader ILI profesor u sobi
            if file[1] != user_id:  # file[1] je uploader_id
                # Ako nije uploader, proveri da li je profesor
                cursor.execute("""
                    SELECT k.rola FROM korisnici k
                    JOIN korisnici_sobe ks ON k.id = ks.user_id
                    WHERE k.id = %s AND ks.room_id = %s
                """, (user_id, file[2]))  # file[2] je room_id
                
                user_role = cursor.fetchone()
                if not user_role or user_role[0] != 'profesor':
                    return jsonify({'error': 'Možete brisati samo svoje fajlove'}), 403
            
            # Brisanje fajla sa diska
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file[0])  # file[0] je stored_filename
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Brisanje iz baze
            cursor.execute("DELETE FROM fajlovi WHERE id = %s", (file_id,))
            
            return jsonify({'message': 'Fajl uspešno obrisan'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/files/<int:file_id>/download', methods=['GET'])
@jwt_required()
def download_file(file_id):
    """Preuzimanje fajla"""
    try:
        user_id = int(get_jwt_identity())
        
        with get_db_cursor() as cursor:
            # Pronalazenje fajla i provera da li je korisnik u sobi
            cursor.execute("""
                SELECT f.stored_filename, f.original_filename, f.room_id
                FROM fajlovi f
                JOIN korisnici_sobe ks ON f.room_id = ks.room_id
                WHERE f.id = %s AND ks.user_id = %s
            """, (file_id, user_id))
            
            file = cursor.fetchone()
            
            if not file:
                return jsonify({'error': 'Fajl nije pronađen ili nemate pristup'}), 404
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file[0])  # file[0] je stored_filename
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Fajl ne postoji na serveru'}), 404
        
        # Osiguraj da je originalno ime string
        original_filename = str(file[1]) if file[1] else 'fajl'
        
        # Pokusaj da prevedes cirilicne karaktere u latinicu
        try:
            # Jednostavan prevod za ceste karaktere
            translation_map = {
                'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ж': 'zh', 'з': 'z',
                'и': 'i', 'ј': 'j', 'к': 'k', 'л': 'l', 'љ': 'lj', 'м': 'm', 'н': 'n', 'њ': 'nj',
                'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'ћ': 'c', 'у': 'u', 'ф': 'f',
                'х': 'h', 'ц': 'c', 'ч': 'ch', 'џ': 'dz', 'ш': 'sh',
                'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ж': 'Zh', 'З': 'Z',
                'И': 'I', 'Ј': 'J', 'К': 'K', 'Л': 'L', 'Љ': 'Lj', 'М': 'M', 'Н': 'N', 'Њ': 'Nj',
                'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'Ћ': 'C', 'У': 'U', 'Ф': 'F',
                'Х': 'H', 'Ц': 'C', 'Ч': 'Ch', 'Џ': 'Dz', 'Ш': 'Sh'
            }
            
            latin_filename = original_filename
            for cyrillic, latin in translation_map.items():
                latin_filename = latin_filename.replace(cyrillic, latin)
            
            download_filename = latin_filename
        except:
            download_filename = original_filename
        
        # URL encode ime fajla za sigurno prosledivanje
        import urllib.parse
        encoded_filename = urllib.parse.quote(download_filename)
        
        # Koristi Response objekat sa custom header-ima
        from flask import Response
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        response = Response(file_content)
        response.headers['Content-Type'] = 'application/octet-stream'
        response.headers['Content-Disposition'] = f'attachment; filename="{download_filename}"; filename*=UTF-8\'\'{encoded_filename}'
        
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -----------------------------------------------> Administracija <-------------------------------------------------------

@app.route('/admin/cleanup', methods=['POST'])
def cleanup_rooms():
    """Ručno brisanje isteklih soba (za testiranje)"""
    try:
        cleanup_expired_rooms()
        return jsonify({'message': 'Čišćenje završeno'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -----------------------------------------------> Pokretanje aplikacije <-------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
