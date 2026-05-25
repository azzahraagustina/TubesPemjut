from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import urllib.parse
import mysql.connector
from http import cookies
import re
import json

class WebTKHandler(BaseHTTPRequestHandler):
    
    def get_db_connection(self):
        """Menghubungkan Python ke Database MySQL via HeidiSQL"""
        try:
            return mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="db_tk_badak_putih"
            )
        except mysql.connector.Error as err:
            print(f"[DATABASE ERROR]: {err}")
            return None

    def get_logged_in_user(self):
        """Mengecek cookie untuk melacak status login user beserta rolenya"""
        cookie_header = self.headers.get('Cookie')
        if cookie_header:
            cookie = cookies.SimpleCookie(cookie_header)
            if 'session_user_tk' in cookie and 'session_username_tk' in cookie and 'session_role_tk' in cookie:
                return {
                    'nama': cookie['session_user_tk'].value,
                    'username': cookie['session_username_tk'].value,
                    'role': cookie['session_role_tk'].value
                }
        return None

    def do_GET(self):
        user_info = self.get_logged_in_user()
        user_aktif = user_info['nama'] if user_info else None
        username_aktif = user_info['username'] if user_info else None
        role_aktif = user_info['role'] if user_info else None

        # --- ROUTING HALAMAN GET ---
        
        # API endpoint untuk mendapatkan user yang login
        if self.path == '/api/user':
            if user_info:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(user_info).encode())
            else:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'null')
        
        elif self.path == '/' or self.path == '/index.html':
            self.kirim_halaman_beranda('templates/index.html', user_aktif, role_aktif)
        
        elif self.path == '/ppdb.html' or self.path == '/templates/ppdb.html':
            self.kirim_halaman_statis('templates/ppdb.html', user_aktif, role_aktif)
            
        elif self.path == '/profil.html' or self.path == '/templates/profil.html':
            self.kirim_halaman_statis('templates/profil.html', user_aktif, role_aktif)
            
        elif self.path == '/jadwal.html' or self.path == '/templates/jadwal.html':
            self.kirim_halaman_statis('templates/jadwal.html', user_aktif, role_aktif)
        
        elif self.path == '/laporan.html' or self.path == '/templates/laporan.html':
            # Izinkan semua akses tanpa login
            self.kirim_halaman_laporan('templates/laporan.html', user_aktif, username_aktif, role_aktif)

        elif self.path == '/login':
            self.tampilkan_file_mentah('templates/login.html', 'text/html')
            
        elif self.path == '/register':
            self.tampilkan_file_mentah('templates/register.html', 'text/html')
            
        elif self.path == '/logout':
            # Hapus cookie session saat logout
            cookie = cookies.SimpleCookie()
            for key in ['session_user_tk', 'session_username_tk', 'session_role_tk']:
                cookie[key] = ''
                cookie[key]['expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
                cookie[key]['path'] = '/'
            self.send_response(303)
            for c in cookie.values():
                self.send_header('Set-Cookie', c.OutputString())
            self.send_header('Location', '/')
            self.end_headers()
            
        elif self.path.endswith('.jpeg') or self.path.endswith('.jpg') or self.path.endswith('.png'):
            nama_file_gambar = self.path.lstrip('/')
            if os.path.exists(f"static/{nama_file_gambar}"):
                self.tampilkan_file_mentah(f"static/{nama_file_gambar}", 'image/jpeg')
            elif os.path.exists(nama_file_gambar):
                self.tampilkan_file_mentah(nama_file_gambar, 'image/jpeg')
            else:
                self.send_error(404, "Gambar tidak ditemukan")
        else:
            self.send_error(404, "File tidak ditemukan")

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = urllib.parse.parse_qs(post_data)

        user_info = self.get_logged_in_user()
        role_aktif = user_info['role'] if user_info else None

        # 1. POST REGISTER (Otomatis Role Orang Tua)
        if self.path == '/register':
            nama = params.get('nama', [''])[0]
            username = params.get('username', [''])[0]
            password = params.get('password', [''])[0]
            conn = self.get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    sql = "INSERT INTO tbl_users (nama, username, password, role) VALUES (%s, %s, %s, 'orang_tua')"
                    cursor.execute(sql, (nama, username, password))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    self.alihkan_ke('/login')
                except mysql.connector.Error:
                    self.alihkan_ke('/register')

        # 2. POST LOGIN MULTI ROLE
        elif self.path == '/login':
            username = params.get('username', [''])[0]
            password = params.get('password', [''])[0]
            conn = self.get_db_connection()
            user_valid = None
            if conn:
                cursor = conn.cursor(dictionary=True)
                sql = "SELECT * FROM tbl_users WHERE username = %s AND password = %s"
                cursor.execute(sql, (username, password))
                user_valid = cursor.fetchone()
                cursor.close()
                conn.close()

            if user_valid:
                cookie = cookies.SimpleCookie()
                cookie['session_user_tk'] = user_valid['nama']
                cookie['session_user_tk']['path'] = '/'
                cookie['session_username_tk'] = user_valid['username']
                cookie['session_username_tk']['path'] = '/'
                cookie['session_role_tk'] = user_valid['role']
                cookie['session_role_tk']['path'] = '/'
                
                self.send_response(303)
                for c in cookie.values():
                    self.send_header('Set-Cookie', c.OutputString())
                self.send_header('Location', '/')
                self.end_headers()
            else:
                self.alihkan_ke('/login')

        # 3. POST INPUT NILAI (KHUSUS ROLE GURU)
        elif self.path == '/guru/input_laporan':
            if not role_aktif or role_aktif != 'guru':
                self.send_error(403, "Akses dilarang")
                return

            username_ortu  = params.get('username_ortu', [''])[0]
            nama_anak      = params.get('nama_anak',     [''])[0]
            kelas          = params.get('kelas',         [''])[0]
            semester       = params.get('semester',      [''])[0]
            tb             = params.get('tb',            [''])[0]
            bb             = params.get('bb',            [''])[0]
            narasi_agama    = params.get('narasi_agama',    [''])[0]
            narasi_karakter = params.get('narasi_karakter', [''])[0]
            narasi_fisik    = params.get('narasi_fisik',    [''])[0]
            narasi_kognitif = params.get('narasi_kognitif', [''])[0]
            narasi_bahasa   = params.get('narasi_bahasa',   [''])[0]
            narasi_sosem    = params.get('narasi_sosem',    [''])[0]
            narasi_seni     = params.get('narasi_seni',     [''])[0]
            karakter_1 = params.get('karakter_1', ['MM'])[0]
            karakter_2 = params.get('karakter_2', ['MM'])[0]
            karakter_3 = params.get('karakter_3', ['MM'])[0]
            karakter_4 = params.get('karakter_4', ['MM'])[0]
            karakter_5 = params.get('karakter_5', ['MM'])[0]
            kes_mata    = params.get('kes_mata',    ['Baik'])[0]
            kes_telinga = params.get('kes_telinga', ['Baik'])[0]
            kes_gigi    = params.get('kes_gigi',    ['Baik'])[0]
            kes_rapian  = params.get('kes_rapian',  ['Baik'])[0]
            catatan_guru = params.get('catatan_guru', [''])[0]

            conn = self.get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tbl_laporan WHERE username_ortu = %s", (username_ortu,))
                sql = """INSERT INTO tbl_laporan (
                            username_ortu, nama_anak, kelas, semester, tb, bb,
                            narasi_agama, narasi_karakter, narasi_fisik, narasi_kognitif,
                            narasi_bahasa, narasi_sosem, narasi_seni,
                            karakter_1, karakter_2, karakter_3, karakter_4, karakter_5,
                            kes_mata, kes_telinga, kes_gigi, kes_rapian,
                            catatan_guru
                         ) VALUES (
                            %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s,
                            %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s,
                            %s
                         )"""
                cursor.execute(sql, (
                    username_ortu, nama_anak, kelas, semester, tb, bb,
                    narasi_agama, narasi_karakter, narasi_fisik, narasi_kognitif,
                    narasi_bahasa, narasi_sosem, narasi_seni,
                    karakter_1, karakter_2, karakter_3, karakter_4, karakter_5,
                    kes_mata, kes_telinga, kes_gigi, kes_rapian,
                    catatan_guru
                ))
                conn.commit()
                cursor.close()
                conn.close()
            self.alihkan_ke('/laporan.html')

        # 4. POST FORM PPDB 
        elif self.path == '/proses_ppdb':
            nama_anak = params.get('nama_anak', [''])[0]
            nama_ortu = params.get('nama_ortu', [''])[0]
            no_hp = params.get('no_hp', [''])[0]
            alamat = params.get('alamat', [''])[0]
            conn = self.get_db_connection()
            if conn:
                cursor = conn.cursor()
                sql = "INSERT INTO tbl_ppdb (nama_anak, nama_ortu, no_hp, alamat) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (nama_anak, nama_ortu, no_hp, alamat))
                conn.commit()
                cursor.close()
                conn.close()
            self.alihkan_ke('/')

    def alihkan_ke(self, lokasi_tujuan):
        self.send_response(303)
        self.send_header('Location', lokasi_tujuan)
        self.end_headers()

    def tampilkan_file_mentah(self, file_path, content_type):
        try:
            with open(file_path, 'rb') as file:
                self.send_response(200)
                self.send_header('Content-type', f"{content_type}; charset=utf-8")
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_error(404, "File tidak ditemukan")

    def pasang_navbar_dinamis(self, html_content, nama_user, role_user):
        """Menyelaraskan tombol navigasi secara rapi berdasarkan status login"""
        html_content = re.sub(r'<a href="[^"]*login[^"]*" class="nav-btn[^"]*">[^<]*</a>', '', html_content)
        html_content = re.sub(r'<a href="[^"]*" class="nav-btn[^"]*">🔑 MASUK</a>', '', html_content)

        if nama_user:
            txt_role = "Admin" if role_user == 'admin' else "Guru" if role_user == 'guru' else "Orang Tua"
            html_tombol = f'''
            <span style="font-weight: bold; color: #2d3e50; font-size: 0.95rem; background: #fff; padding: 10px 18px; border-radius: 50px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-left: auto;">👤 {txt_role}: {nama_user} ✨</span>
            <a href="/logout" class="nav-btn red" style="text-decoration: none; margin-left: 10px; background-color: #e53935; box-shadow: 0 4px 0 #b71c1c; color: white;">🚪 Keluar</a>
            '''
        else:
            html_tombol = '''
            <a href="/login" class="nav-btn blue" style="text-decoration: none; margin-left: auto; background-color: #2196f3; box-shadow: 0 5px 0 #1565c0; color: white;">🔑 Masuk Portal</a>
            '''
        
        if '</nav>' in html_content:
            parts = html_content.split('</nav>', 1)
            html_content = parts[0] + html_tombol + '</nav>' + parts[1]
        return html_content

    def kirim_halaman_statis(self, jalur_html, nama_user, role_user):
        try:
            with open(jalur_html, 'r', encoding='utf-8') as f:
                konten = f.read()
            konten = self.pasang_navbar_dinamis(konten, nama_user, role_user)
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(konten.encode('utf-8'))
        except Exception:
            self.tampilkan_file_mentah(jalur_html, 'text/html')

    def kirim_halaman_beranda(self, jalur_html, nama_user, role_user):
        try:
            with open(jalur_html, 'r', encoding='utf-8') as f:
                html_content = f.read()

            html_content = self.pasang_navbar_dinamis(html_content, nama_user, role_user)

            if role_user == 'admin':
                conn = self.get_db_connection()
                baris_tabel = ""
                if conn:
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute("SELECT * FROM tbl_ppdb ORDER BY id DESC")
                    rows = cursor.fetchall()
                    cursor.close()
                    conn.close()
                    for r in rows:
                        baris_tabel += f"<tr><td style='padding:12px; border-bottom:1px solid #e2e8f0;'>👧 {r['nama_anak']}</td><td style='padding:12px; border-bottom:1px solid #e2e8f0;'>👨‍👩‍👧 {r['nama_ortu']}</td><td style='padding:12px; border-bottom:1px solid #e2e8f0;'>📞 {r['no_hp']}</td><td style='padding:12px; border-bottom:1px solid #e2e8f0;'>🏠 {r['alamat']}</td></tr>"

                html_tabel_ppdb = f'''
                <div class="card" style="margin-top: 30px; background: white; padding: 25px; border-radius: 32px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); border: 3px solid #1e88e5; text-align: left;">
                    <h3 style="color:#1565c0; margin-bottom:15px; font-size:1.3rem;">📋 Panel Admin: Data Pendaftaran Masuk (PPDB)</h3>
                    <table style="width:100%; border-collapse:collapse; text-align:left;">
                        <thead>
                            <tr style="background:#f1f5f9; color:#475569;">
                                <th style="padding:12px;">Nama Calon Siswa</th><th style="padding:12px;">Nama Orang Tua</th><th style="padding:12px;">No WhatsApp</th><th style="padding:12px;">Alamat Lengkap</th>
                            </tr>
                        </thead>
                        <tbody>
                            {baris_tabel if baris_tabel else "<tr><td colspan='4' style='text-align:center; padding:15px; color:#94a3b8;'>Belum ada murid baru yang mendaftar.</td></tr>"}
                        </tbody>
                    </table>
                </div>
                '''
                if '</main>' in html_content:
                    parts = html_content.split('</main>', 1)
                    html_content = parts[0] + html_tabel_ppdb + '</main>' + parts[1]

            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
        except Exception:
            self.tampilkan_file_mentah(jalur_html, 'text/html')

    def kirim_halaman_laporan(self, jalur_html, nama_user, username_user, role_user):
        try:
            with open(jalur_html, 'r', encoding='utf-8') as f:
                html_content = f.read()

            html_content = self.pasang_navbar_dinamis(html_content, nama_user, role_user)

            if role_user == 'guru':
                html_form_guru = '''
                <div class="card" style="background: white; padding: 35px; border-radius: 32px; box-shadow: 0 15px 30px rgba(0,0,0,0.05); margin-top: 25px; border: 3px solid #4caf50; text-align: left;">
                    <h3 style="color: #2e7d32; margin-bottom: 8px; font-size:1.4rem;">✍️ Ruang Kerja Guru: Input Laporan Perkembangan Anak</h3>
                    <p style="color:#555; margin-bottom:24px; font-size:0.95rem;">Isi seluruh kolom di bawah ini untuk mengirimkan laporan rapor ke orang tua siswa.</p>
                    <form action="/guru/input_laporan" method="POST" style="display:flex; flex-direction:column; gap:20px;">
                        <div style="background:#f1f8e9; border-radius:20px; padding:20px; border-left:5px solid #66bb6a;">
                            <div style="font-weight:800; color:#2e7d32; margin-bottom:14px; font-size:1.05rem;">👤 A. Identitas Siswa</div>
                            <div style="display:grid; grid-template-columns:1fr 1fr; gap:14px;">
                                <div><label style="display:block; font-weight:bold; margin-bottom:6px;">Username Orang Tua *</label><input type="text" name="username_ortu" style="width:100%; padding:11px 14px; border-radius:12px; border:2px solid #c8e6c9; font-family:inherit;" required placeholder="Contoh: hana"></div>
                                <div><label style="display:block; font-weight:bold; margin-bottom:6px;">Nama Lengkap Anak *</label><input type="text" name="nama_anak" style="width:100%; padding:11px 14px; border-radius:12px; border:2px solid #c8e6c9; font-family:inherit;" required placeholder="Contoh: Aisha Farhana"></div>
                                <div><label style="display:block; font-weight:bold; margin-bottom:6px;">Kelas</label><input type="text" name="kelas" style="width:100%; padding:11px 14px; border-radius:12px; border:2px solid #c8e6c9; font-family:inherit;" placeholder="Contoh: TK A"></div>
                                <div><label style="display:block; font-weight:bold; margin-bottom:6px;">Semester / Tahun Ajaran</label><input type="text" name="semester" style="width:100%; padding:11px 14px; border-radius:12px; border:2px solid #c8e6c9; font-family:inherit;" placeholder="Contoh: II / 2024-2025"></div>
                                <div><label style="display:block; font-weight:bold; margin-bottom:6px;">Tinggi Badan (cm)</label><input type="number" name="tb" style="width:100%; padding:11px 14px; border-radius:12px; border:2px solid #c8e6c9; font-family:inherit;" placeholder="Contoh: 112"></div>
                                <div><label style="display:block; font-weight:bold; margin-bottom:6px;">Berat Badan (kg)</label><input type="number" name="bb" style="width:100%; padding:11px 14px; border-radius:12px; border:2px solid #c8e6c9; font-family:inherit;" placeholder="Contoh: 21"></div>
                            </div>
                        </div>
                        <div style="background:#e8f5e9; border-radius:20px; padding:20px; border-left:5px solid #43a047;">
                            <div style="font-weight:800; color:#1b5e20; margin-bottom:14px; font-size:1.05rem;">📝 B. Narasi Aspek Perkembangan</div>
                            <div style="display:flex; flex-direction:column; gap:14px;">
                                <div><label style="display:block; font-weight:bold; margin-bottom:6px; color:#2e7d32;">🕌 Nilai Agama dan Moral</label><textarea name="narasi_agama" rows="3" style="width:100%; padding:11px 14px; border-radius:12px; border:2px solid #c8e6c9; font-family:inherit; resize:vertical;" placeholder="Tuliskan narasi perkembangan nilai agama dan moral anak..."></textarea></div>
                                <div><label style="display:block; font-weight:bold; margin-bottom:6px; color:#1976d2;">⭐ Karakter Siswa</label><textarea name="narasi_karakter" rows="3" style="width:100%; padding:11px 14px; border-radius:12px; border:2px solid #bbdefb; font-family:inherit; resize:vertical;" placeholder="Tuliskan narasi perkembangan karakter siswa..."></textarea></div>
                                <div><label style="display:block; font-weight:bold; margin-bottom:6px; color:#e53935;">🏃 Fisik Motorik</label><textarea name="narasi_fisik" rows="3" style="width:100%; padding:11px 14px; border-radius:12px; border:2px solid #ffcdd2; font-family:inherit; resize:vertical;" placeholder="Tuliskan narasi perkembangan fisik motorik anak..."></textarea></div>
                                <div><label style="display:block; font-weight:bold; margin-bottom:6px; color:#f57c00;">🧠 Kognitif</label><textarea name="narasi_kognitif" rows="3" style="width:100%; padding:11px 14px; border-radius:12px; border:2px solid #ffe0b2; font-family:inherit; resize:vertical;" placeholder="Tuliskan narasi perkembangan kognitif anak..."></textarea></div>
                                <div><label style="display:block; font-weight:bold; margin-bottom:6px; color:#8e24aa;">📚 Bahasa dan Literasi</label><textarea name="narasi_bahasa" rows="3" style="width:100%; padding:11px 14px; border-radius:12px; border:2px solid #e1bee7; font-family:inherit; resize:vertical;" placeholder="Tuliskan narasi perkembangan bahasa dan literasi anak..."></textarea></div>
                                <div><label style="display:block; font-weight:bold; margin-bottom:6px; color:#00838f;">🤝 Sosial Emosional</label><textarea name="narasi_sosem" rows="3" style="width:100%; padding:11px 14px; border-radius:12px; border:2px solid #b2ebf2; font-family:inherit; resize:vertical;" placeholder="Tuliskan narasi perkembangan sosial emosional anak..."></textarea></div>
                                <div><label style="display:block; font-weight:bold; margin-bottom:6px; color:#c0392b;">🎨 Seni dan Kreativitas</label><textarea name="narasi_seni" rows="3" style="width:100%; padding:11px 14px; border-radius:12px; border:2px solid #ffccbc; font-family:inherit; resize:vertical;" placeholder="Tuliskan narasi perkembangan seni dan kreativitas anak..."></textarea></div>
                            </div>
                        </div>
                        <div style="background:#e3f2fd; border-radius:20px; padding:20px; border-left:5px solid #1976d2;">
                            <div style="font-weight:800; color:#0d47a1; margin-bottom:14px; font-size:1.05rem;">⭐ C. Capaian Karakter Siswa</div>
                            <p style="font-size:0.85rem; color:#555; margin-bottom:14px;"><strong>SM</strong> = Sudah Muncul &nbsp;|&nbsp; <strong>MM</strong> = Mulai Muncul &nbsp;|&nbsp; <strong>BM</strong> = Belum Muncul</p>
                            <div style="display:flex; flex-direction:column; gap:10px;">
                                <div style="display:flex; align-items:center; gap:12px; background:white; padding:10px 14px; border-radius:12px;"><span style="flex:1; font-size:0.95rem;">Mandiri, disiplin dan tanggung jawab</span><select name="karakter_1" style="padding:8px 12px; border-radius:10px; border:2px solid #bbdefb;"><option value="SM">SM</option><option value="MM" selected>MM</option><option value="BM">BM</option></select></div>
                                <div style="display:flex; align-items:center; gap:12px; background:white; padding:10px 14px; border-radius:12px;"><span style="flex:1; font-size:0.95rem;">Dermawan, suka menolong dan kerjasama</span><select name="karakter_2" style="padding:8px 12px; border-radius:10px; border:2px solid #bbdefb;"><option value="SM">SM</option><option value="MM" selected>MM</option><option value="BM">BM</option></select></div>
                                <div style="display:flex; align-items:center; gap:12px; background:white; padding:10px 14px; border-radius:12px;"><span style="flex:1; font-size:0.95rem;">Percaya diri, kreatif, dan pantang menyerah</span><select name="karakter_3" style="padding:8px 12px; border-radius:10px; border:2px solid #bbdefb;"><option value="SM">SM</option><option value="MM" selected>MM</option><option value="BM">BM</option></select></div>
                                <div style="display:flex; align-items:center; gap:12px; background:white; padding:10px 14px; border-radius:12px;"><span style="flex:1; font-size:0.95rem;">Pemimpin yang baik dan adil</span><select name="karakter_4" style="padding:8px 12px; border-radius:10px; border:2px solid #bbdefb;"><option value="SM">SM</option><option value="MM" selected>MM</option><option value="BM">BM</option></select></div>
                                <div style="display:flex; align-items:center; gap:12px; background:white; padding:10px 14px; border-radius:12px;"><span style="flex:1; font-size:0.95rem;">Kebersihan, kerapian, kesehatan dan keamanan</span><select name="karakter_5" style="padding:8px 12px; border-radius:10px; border:2px solid #bbdefb;"><option value="SM">SM</option><option value="MM" selected>MM</option><option value="BM">BM</option></select></div>
                            </div>
                        </div>
                        <div style="background:#fce4ec; border-radius:20px; padding:20px; border-left:5px solid #e91e63;">
                            <div style="font-weight:800; color:#880e4f; margin-bottom:14px; font-size:1.05rem;">🏥 D. Tumbuh Kembang Anak (Kesehatan)</div>
                            <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
                                <div><label>👁️ Penglihatan (Mata)</label><input type="text" name="kes_mata" value="Baik"></div>
                                <div><label>👂 Pendengaran (Telinga)</label><input type="text" name="kes_telinga" value="Baik"></div>
                                <div><label>🦷 Kesehatan Mulut dan Gigi</label><input type="text" name="kes_gigi" value="Baik"></div>
                                <div><label>👗 Kerapian dalam Berpakaian</label><input type="text" name="kes_rapian" value="Baik"></div>
                            </div>
                        </div>
                        <div style="background:#fff8e1; border-radius:20px; padding:20px; border-left:5px solid #ffb300;">
                            <div style="font-weight:800; color:#e65100; margin-bottom:10px; font-size:1.05rem;">📝 E. Catatan Guru Kelas</div>
                            <textarea name="catatan_guru" rows="4" style="width:100%; padding:11px 14px; border-radius:12px; border:2px solid #ffe082;" required placeholder="Tuliskan catatan khusus dan pesan untuk orang tua..."></textarea>
                        </div>
                        <button type="submit" style="background:linear-gradient(135deg,#4caf50,#2e7d32); color:white; border:none; padding:16px; border-radius:16px; font-weight:bold; font-size:1.05rem; cursor:pointer;">🚀 Simpan & Kirim Laporan ke Orang Tua</button>
                    </form>
                </div>
                '''
                if '</main>' in html_content:
                    parts = html_content.split('</main>', 1)
                    html_content = parts[0] + html_form_guru + '</main>' + parts[1]
            else:
                conn = self.get_db_connection()
                data_rapor = None
                if conn and username_user:
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute("SELECT * FROM tbl_laporan WHERE username_ortu = %s", (username_user,))
                    data_rapor = cursor.fetchone()
                    cursor.close()
                    conn.close()

                if data_rapor:
                    def badge(val):
                        warna = {'SM':'#e8f5e9;color:#2e7d32', 'MM':'#fff3e0;color:#e65100', 'BM':'#fce4ec;color:#c62828'}.get(val, '#f5f5f5;color:#555')
                        return f'<span style="display:inline-block;padding:3px 14px;border-radius:30px;font-weight:700;font-size:0.85rem;background:{warna}">{val}</span>'

                    karakter_rows = ''.join([
                        f'<tr><td style="padding:9px 12px;border:1px solid #e8f5e9;">{bidang}</td>'
                        f'<td style="padding:9px 12px;border:1px solid #e8f5e9;text-align:center;">{badge(data_rapor.get(col,"MM"))}</td>'
                        f'<td style="padding:9px 12px;border:1px solid #e8f5e9;">{"SM: Sudah Muncul" if data_rapor.get(col,"MM")=="SM" else "MM: Mulai Muncul" if data_rapor.get(col,"MM")=="MM" else "BM: Belum Muncul"}</td>'
                        f'</tr>'
                        for bidang, col in [
                            ("Mandiri, disiplin dan tanggung jawab", "karakter_1"),
                            ("Dermawan, suka menolong dan kerjasama", "karakter_2"),
                            ("Percaya diri, kreatif, dan pantang menyerah", "karakter_3"),
                            ("Pemimpin yang baik dan adil", "karakter_4"),
                            ("Kebersihan, kerapian, kesehatan dan keamanan","karakter_5"),
                        ]
                    ])

                    aspek_html = ''.join([
                        f'<div style="border-radius:16px;overflow:hidden;box-shadow:0 4px 12px rgba(0,0,0,0.05);margin-bottom:14px;">'
                        f'<div style="padding:10px 18px;font-weight:800;font-size:0.97rem;color:white;background:{bg};">{icon} {judul}</div>'
                        f'<div style="padding:14px 18px;font-size:0.96rem;line-height:1.75;color:#3a3a3a;background:#fffdf8;border:2px solid {border};">'
                        f'{data_rapor.get(field) or "<em style=color:#aaa>Belum diisi</em>"}</div></div>'
                        for icon, judul, field, bg, border in [
                            ("🕌","Nilai Agama dan Moral", "narasi_agama", "#43a047","#c8e6c9"),
                            ("⭐","Karakter Siswa", "narasi_karakter", "#1976d2","#bbdefb"),
                            ("🏃","Fisik Motorik", "narasi_fisik", "#e53935","#ffcdd2"),
                            ("🧠","Kognitif", "narasi_kognitif", "#f57c00","#ffe0b2"),
                            ("📚","Bahasa dan Literasi", "narasi_bahasa", "#8e24aa","#e1bee7"),
                            ("🤝","Sosial Emosional", "narasi_sosem", "#00838f","#b2ebf2"),
                            ("🎨","Seni dan Kreativitas", "narasi_seni", "#c0392b","#ffccbc"),
                        ]
                    ])

                    html_box_rapor = f'''
                    <div class="card" style="background:white; padding:0; border-radius:32px; overflow:hidden; box-shadow:0 15px 35px rgba(0,0,0,0.08); margin-top:20px; border:1px solid #ffcd94; text-align:left;">
                        <div style="background:linear-gradient(135deg,#2e7d32,#43a047); padding:22px 28px;">
                            <div style="color:white;">
                                <div style="font-size:0.8rem;">TAMAN KANAK-KANAK</div>
                                <div style="font-size:1.5rem; font-weight:900;">BADAK PUTIH</div>
                                <div style="font-size:0.82rem;">Jl. Arramannik Endah No.3, Bandung 40293</div>
                            </div>
                        </div>
                        <div style="background:#e8f5e9; text-align:center; padding:11px; font-weight:800;">LAPORAN PERKEMBANGAN ANAK DIDIK</div>
                        <div style="display:grid; grid-template-columns:1fr 1fr; padding:15px 20px;">
                            <div><strong>Nama Siswa:</strong> {data_rapor['nama_anak']}</div>
                            <div><strong>Kelas:</strong> {data_rapor.get('kelas','-')}</div>
                            <div><strong>Semester:</strong> {data_rapor.get('semester','-')}</div>
                            <div><strong>Tinggi Badan:</strong> {data_rapor.get('tb','-')} cm</div>
                            <div><strong>Berat Badan:</strong> {data_rapor.get('bb','-')} kg</div>
                        </div>
                        <div style="padding:20px 24px;">{aspek_html}</div>
                        <div style="padding:0 24px 20px;">
                            <div style="font-weight:800;">⭐ Capaian Karakter Siswa</div>
                            <table style="width:100%; border-collapse:collapse;">
                                <thead><tr style="background:#e8f5e9;"><th>Bidang Karakter</th><th>Capaian</th><th>Keterangan</th></tr></thead>
                                <tbody>{karakter_rows}</tbody>
                            </table>
                        </div>
                        <div style="margin:0 24px 20px; background:#fff8e1; border-radius:18px; padding:16px 20px; border-left:6px solid #ffb300;">
                            <div style="font-weight:800;">📝 Catatan Guru Kelas</div>
                            <p>{data_rapor['catatan_guru']}</p>
                        </div>
                    </div>
                    '''
                    if '</main>' in html_content:
                        parts = html_content.split('</main>', 1)
                        html_content = parts[0] + html_box_rapor + '</main>' + parts[1]
                else:
                    html_kosong = '<div class="card" style="background:#fff5f5; border:3px dashed #e53935; padding:35px; border-radius:24px; text-align:center; margin-top:20px; color:#e53935; font-weight:bold;">Laporan Perkembangan Belum Terbit 📭</div>'
                    if '</main>' in html_content:
                        parts = html_content.split('</main>', 1)
                        html_content = parts[0] + html_kosong + '</main>' + parts[1]

            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
        except Exception as e:
            print(f"Error: {e}")
            self.tampilkan_file_mentah(jalur_html, 'text/html')

def run(server_class=HTTPServer, handler_class=WebTKHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Sistem 3-Role Sukses Aktif Sempurna di http://localhost:{port} ... 🚀✨")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[SISTEM]: Web Server berhasil dihentikan dengan aman via Ctrl + C. Sampai jumpa! 👋")
        httpd.server_close()

if __name__ == '__main__':
    run()