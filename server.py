from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import urllib.parse
import mysql.connector
from http import cookies
import re

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
        if self.path == '/' or self.path == '/index.html':
            self.kirim_halaman_beranda('templates/index.html', user_aktif, role_aktif)
        
        # TAMBAHAN: Rute untuk menampilkan halaman PPDB
        elif self.path == '/ppdb.html' or self.path == '/templates/ppdb.html':
            self.kirim_halaman_statis('templates/ppdb.html', user_aktif, role_aktif)
            
        elif self.path == '/profil.html' or self.path == '/templates/profil.html':
            self.kirim_halaman_statis('templates/profil.html', user_aktif, role_aktif)
        elif self.path == '/jadwal.html' or self.path == '/templates/jadwal.html':
            self.kirim_halaman_statis('templates/jadwal.html', user_aktif, role_aktif)
        
        elif self.path == '/laporan.html' or self.path == '/templates/laporan.html':
            if not user_aktif:
                self.alihkan_ke('/login')
            else:
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
            
        # TAMBAHAN OLEH SYSTEM: Membaca semua gambar .jpeg (tk.jpeg, foto-anak.jpeg, dll) secara dinamis
        elif self.path.endswith('.jpeg') or self.path.endswith('.jpg'):
            # Menghapus tanda '/' di awal path file gambar
            nama_file_gambar = self.path.lstrip('/')
            # Jika file ada di folder static, arahkan ke folder static
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
            username_ortu = params.get('username_ortu', [''])[0]
            nama_anak = params.get('nama_anak', [''])[0]
            aspek_agama = params.get('aspek_agama', [''])[0]
            aspek_motorik = params.get('aspek_motorik', [''])[0]
            aspek_kognitif = params.get('aspek_kognitif', [''])[0]
            aspek_sosial = params.get('aspek_sosial', [''])[0]
            catatan_guru = params.get('catatan_guru', [''])[0]

            conn = self.get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tbl_laporan WHERE username_ortu = %s", (username_ortu,))
                sql = """INSERT INTO tbl_laporan (username_ortu, nama_anak, aspek_agama, aspek_motorik, aspek_kognitif, aspek_sosial, catatan_guru) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (username_ortu, nama_anak, aspek_agama, aspek_motorik, aspek_kognitif, aspek_sosial, catatan_guru))
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

            # JIKA ADMIN LOGIN: Suntikkan tabel rekap PPDB di bagian paling bawah kontainer <main> asli
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

            # JIKA GURU LOGIN: Suntikkan form pengisian nilai rapor anak
            if role_user == 'guru':
                html_form_guru = '''
                <div class="card" style="background: white; padding: 35px; border-radius: 32px; box-shadow: 0 15px 30px rgba(0,0,0,0.05); margin-top: 25px; border: 3px solid #4caf50; text-align: left;">
                    <h3 style="color: #2e7d32; margin-bottom: 20px; font-size:1.4rem;">✍️ Ruang Kerja Guru: Input Rapor Digital</h3>
                    <form action="/guru/input_laporan" method="POST" style="display:flex; flex-direction:column; gap:15px;">
                        <div><label style="display:block; font-weight:bold; margin-bottom:6px;">Username Orang Tua:</label><input type="text" name="username_ortu" style="width:100%; padding:12px; border-radius:12px; border:2px solid #cbd5e1;" required placeholder="Contoh: hana"></div>
                        <div><label style="display:block; font-weight:bold; margin-bottom:6px;">Nama Lengkap Anak Didik:</label><input type="text" name="nama_anak" style="width:100%; padding:12px; border-radius:12px; border:2px solid #cbd5e1;" required placeholder="Contoh: Aisha Farhana"></div>
                        <div><label style="display:block; font-weight:bold; margin-bottom:6px;">Nilai Nilai Agama & Moral:</label><select name="aspek_agama" style="width:100%; padding:12px; border-radius:12px; border:2px solid #cbd5e1;"><option>Berkembang Sangat Baik (BSB)</option><option>Berkembang Sesuai Harapan (BSH)</option><option>Mulai Berkembang (MB)</option></select></div>
                        <div><label style="display:block; font-weight:bold; margin-bottom:6px;">Nilai Fisik Motorik:</label><select name="aspek_motorik" style="width:100%; padding:12px; border-radius:12px; border:2px solid #cbd5e1;"><option>Berkembang Sangat Baik (BSB)</option><option>Berkembang Sesuai Harapan (BSH)</option><option>Mulai Berkembang (MB)</option></select></div>
                        <div><label style="display:block; font-weight:bold; margin-bottom:6px;">Nilai Kognitif:</label><select name="aspek_kognitif" style="width:100%; padding:12px; border-radius:12px; border:2px solid #cbd5e1;"><option>Berkembang Sangat Baik (BSB)</option><option>Berkembang Sesuai Harapan (BSH)</option><option>Mulai Berkembang (MB)</option></select></div>
                        <div><label style="display:block; font-weight:bold; margin-bottom:6px;">Nilai Sosial Emosional:</label><select name="aspek_sosial" style="width:100%; padding:12px; border-radius:12px; border:2px solid #cbd5e1;"><option>Berkembang Sangat Baik (BSB)</option><option>Berkembang Sesuai Harapan (BSH)</option><option>Mulai Berkembang (MB)</option></select></div>
                        <div><label style="display:block; font-weight:bold; margin-bottom:6px;">Catatan Penilaian Guru:</label><textarea name="catatan_guru" rows="3" style="width:100%; padding:12px; border-radius:12px; border:2px solid #cbd5e1;" required placeholder="Tuliskan ulasan perkembangan anak..."></textarea></div>
                        <button type="submit" style="background:#4caf50; color:white; border:none; padding:14px; border-radius:14px; font-weight:bold; font-size:1rem; cursor:pointer; box-shadow:0 5px 0 #2e7d32;">🚀 Kirim Rapor ke Orang Tua</button>
                    </form>
                </div>
                '''
                if '</main>' in html_content:
                    parts = html_content.split('</main>', 1)
                    html_content = parts[0] + html_form_guru + '</main>' + parts[1]
            else:
                conn = self.get_db_connection()
                data_rapor = None
                if conn:
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute("SELECT * FROM tbl_laporan WHERE username_ortu = %s", (username_user,))
                    data_rapor = cursor.fetchone()
                    cursor.close()
                    conn.close()

                if data_rapor:
                    html_box_rapor = f'''
                    <div class="card" style="background: white; padding: 30px; border-radius: 24px; box-shadow: 0 10px 20px rgba(0,0,0,0.04); margin-top: 20px; border: 1px solid #ffcd94; text-align: left;">
                        <h3 style="color: #2d3e50; font-size:1.4rem;">Nama Ananda: <span style="color: #ff8c42;">{data_rapor['nama_anak']}</span> ✨</h3>
                        <p style="color: #7a8b9e; font-size:0.9rem; margin-bottom: 20px;">Lembar Capaian Tingkat Perkembangan Anak</p>
                        <div style="display: flex; flex-direction: column; gap: 12px; font-size:1.05rem;">
                            <div style="display:flex; justify-content:space-between; padding-bottom:8px; border-bottom:1px dashed #ddd;"><strong>✨ Nilai Agama & Moral:</strong> <span style="color:#2196f3; font-weight:bold;">{data_rapor['aspek_agama']}</span></div>
                            <div style="display:flex; justify-content:space-between; padding-bottom:8px; border-bottom:1px dashed #ddd;"><strong>🏃 Fisik Motorik:</strong> <span style="color:#2ecc71; font-weight:bold;">{data_rapor['aspek_motorik']}</span></div>
                            <div style="display:flex; justify-content:space-between; padding-bottom:8px; border-bottom:1px dashed #ddd;"><strong>🧠 Kognitif (Berpikir):</strong> <span style="color:#ff9800; font-weight:bold;">{data_rapor['aspek_kognitif']}</span></div>
                            <div style="display:flex; justify-content:space-between; padding-bottom:8px; border-bottom:1px dashed #ddd;"><strong>🤝 Sosial Emosional:</strong> <span style="color:#e91e63; font-weight:bold;">{data_rapor['aspek_sosial']}</span></div>
                        </div>
                        <div style="margin-top: 25px; background: #fff9e8; padding: 18px; border-radius: 16px; border-left: 6px solid #ffb347;">
                            <strong style="color: #4a2a0e; display:block; margin-bottom:5px;">📝 Catatan Ulasan Guru:</strong>
                            <p style="color: #5c4026; line-height:1.5;">"{data_rapor['catatan_guru']}"</p>
                        </div>
                    </div>
                    '''
                    if '</main>' in html_content:
                        parts = html_content.split('</main>', 1)
                        html_content = parts[0] + html_box_rapor + '</main>' + parts[1]
                else:
                    html_kosong = '<div class="card" style="background:#fff5f5; border:3px dashed #e53935; padding:35px; border-radius:24px; text-align:center; margin-top:20px; color:#e53935; font-weight:bold; font-size:1.1rem;">Laporan Perkembangan Belum Terbit 📭</div>'
                    if '</main>' in html_content:
                        parts = html_content.split('</main>', 1)
                        html_content = parts[0] + html_kosong + '</main>' + parts[1]

            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
        except Exception:
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