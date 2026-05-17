from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import urllib.parse
import mysql.connector

class WebTKHandler(BaseHTTPRequestHandler):
    
    def get_db_connection(self):
        """Fungsi untuk menghubungkan Python ke Database MySQL via HeidiSQL"""
        try:
            return mysql.connector.connect(
                host="localhost",
                user="root",       # Sesuaikan dengan user MySQL kamu
                password="",       # Sesuaikan dengan password MySQL kamu
                database="db_tk_badak_putih"
            )
        except mysql.connector.Error as err:
            print(f"Error Database: {err}")
            return None

    def do_GET(self):
        # Halaman Utama
        if self.path == '/':
            self.tampilkan_file('templates/index.html', 'text/html')
        
        # Logo 
        elif self.path == '/tk.jpeg':
            self.tampilkan_file('tk.jpeg', 'image/jpeg')

        # File Static (CSS / JS)
        elif self.path.startswith('/static/'):
            file_path = self.path[1:]
            if file_path.endswith('.css'):
                self.tampilkan_file(file_path, 'text/css')
            elif file_path.endswith('.js'):
                self.tampilkan_file(file_path, 'application/javascript')
        else:
            self.send_error(404, "File Tidak Ditemukan")

    def do_POST(self):
        """Menangani data yang dikirim (Submit Form) dari Website ke Database"""
        if self.path == '/submit-ppdb':
            # Mengambil panjang data yang dikirim
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            # Parsing data dari form HTML
            params = urllib.parse.parse_qs(post_data)
            nama_anak = params.get('nama_anak', [''])[0]
            nama_ortu = params.get('nama_ortu', [''])[0]
            no_hp = params.get('no_hp', [''])[0]
            alamat = params.get('alamat', [''])[0]

            # Simpan ke HeidiSQL / MySQL
            conn = self.get_db_connection()
            if conn:
                cursor = conn.cursor()
                sql = "INSERT INTO tbl_ppdb (nama_anak, nama_ortu, no_hp, alamat) VALUES (%s, %s, %s, %s)"
                val = (nama_anak, nama_ortu, no_hp, alamat)
                cursor.execute(sql, val)
                conn.commit()
                cursor.close()
                conn.close()

            # Redirect kembali ke halaman utama setelah sukses
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()

    def tampilkan_file(self, file_path, content_type):
        try:
            with open(file_path, 'rb') as file:
                self.send_response(200)
                self.send_header('Content-type', f"{content_type}; charset=utf-8")
                self.end_headers()
                self.wfile.write(file.read())
        except:
            self.send_error(404)

if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, WebTKHandler)
    print("Server Berjalan Aktif! Buka http://localhost:8000")
    httpd.serve_forever()