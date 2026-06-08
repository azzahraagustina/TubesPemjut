-- Active: 1780890904155@@acela.proxy.rlwy.net@58195
-- ============================================
-- DATABASE TK BADAK PUTIH - FULL STRUCTURE
-- ============================================

-- Buat database
USE railway;
--CREATE DATABASE IF NOT EXISTS db_tk_badak_putih;
--USE db_tk_badak_putih;

-- ============================================
-- 1. TABEL USERS (3 Role: admin, guru, orang_tua)
-- ============================================
DROP TABLE IF EXISTS tbl_users;
CREATE TABLE tbl_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'guru', 'orang_tua') NOT NULL DEFAULT 'orang_tua'
);

-- ============================================
-- 2. TABEL LAPORAN PERKEMBANGAN ANAK (LENGKAP)
-- ============================================
DROP TABLE IF EXISTS tbl_laporan;
USE railway;

DROP TABLE IF EXISTS tbl_laporan;
CREATE TABLE tbl_laporan (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username_ortu VARCHAR(50) NOT NULL,
    nama_anak VARCHAR(100) NOT NULL,
    kelas VARCHAR(20),
    semester VARCHAR(50),
    tb VARCHAR(10),
    bb VARCHAR(10),
    narasi_agama TEXT,
    narasi_karakter TEXT,
    narasi_fisik TEXT,
    narasi_kognitif TEXT,
    narasi_bahasa TEXT,
    narasi_sosem TEXT,
    narasi_seni TEXT,
    karakter_1 VARCHAR(5),
    karakter_2 VARCHAR(5),
    karakter_3 VARCHAR(5),
    karakter_4 VARCHAR(5),
    karakter_5 VARCHAR(5),
    kes_mata VARCHAR(50),
    kes_telinga VARCHAR(50),
    kes_gigi VARCHAR(50),
    kes_rapian VARCHAR(50),
    catatan_guru TEXT
);

-- ============================================
-- 3. TABEL PENDAFTARAN PPDB
-- ============================================
DROP TABLE IF EXISTS tbl_ppdb;
CREATE TABLE tbl_ppdb (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama_anak VARCHAR(100) NOT NULL,
    nama_ortu VARCHAR(100) NOT NULL,
    no_hp VARCHAR(20) NOT NULL,
    alamat TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 4. DATA SAMPLE / AKUN DEFAULT
-- ============================================

-- Akun Admin (Melihat data PPDB)
INSERT INTO tbl_users (nama, username, password, role) 
VALUES ('Kepala Sekolah Admin', 'admin', 'admin123', 'admin')
ON DUPLICATE KEY UPDATE username=username;

-- Akun Guru (Menginput laporan rapor)
INSERT INTO tbl_users (nama, username, password, role) 
VALUES ('Ibu Guru Pertiwi', 'guru', 'guru123', 'guru')
ON DUPLICATE KEY UPDATE username=username;

-- Akun Orang Tua (Melihat laporan anak)
INSERT INTO tbl_users (nama, username, password, role) 
VALUES ('Bunda Hana', 'hana', 'hana123', 'orang_tua')
ON DUPLICATE KEY UPDATE username=username;

INSERT INTO tbl_users (nama, username, password, role) 
VALUES ('Bapak Budi', 'budi', 'budi123', 'orang_tua')
ON DUPLICATE KEY UPDATE username=username;

-- ============================================
-- 5. SAMPLE DATA LAPORAN (Untuk testing)
-- ============================================

-- Laporan untuk user 'hana'
INSERT INTO tbl_laporan (
    username_ortu, nama_anak, kelas, semester, tb, bb,
    narasi_agama, narasi_karakter, narasi_fisik, narasi_kognitif,
    narasi_bahasa, narasi_sosem, narasi_seni,
    karakter_1, karakter_2, karakter_3, karakter_4, karakter_5,
    kes_mata, kes_telinga, kes_gigi, kes_rapian, catatan_guru
) VALUES (
    'hana', 'Aisha Putri', 'TK A', 'I / 2025-2026', '112', '19',
    'Aisha sudah mulai terbiasa mengucapkan doa sebelum dan sesudah belajar. Ia juga sudah hafal surat Al-Fatihah dan doa makan.',
    'Aisha adalah anak yang mandiri, bertanggung jawab, dan selalu membantu teman yang kesulitan.',
    'Motorik kasar Aisha berkembang baik. Ia lincah berlari dan melompat. Untuk motorik halus, hasil mewarnainya sudah rapi.',
    'Aisha mampu mengenal angka 1-20, huruf hijaiyah, dan sudah bisa membaca suku kata sederhana.',
    'Kosakata Aisha berkembang pesat. Ia sudah bisa bercerita tentang pengalamannya dengan kalimat yang runtut.',
    'Aisha mudah bergaul dengan teman-teman. Ia juga peka terhadap perasaan orang lain.',
    'Aisha sangat kreatif dalam menggambar dan membuat karya dari barang bekas.',
    'SM', 'SM', 'SM', 'MM', 'SM',
    'Baik', 'Baik', 'Baik', 'Sangat Baik',
    'Aisha adalah anak yang cerdas dan aktif. Pertahankan semangat belajarnya. Orang tua diharapkan terus mendampingi hafalan surat pendek di rumah.'
);

-- Laporan untuk user 'budi'
INSERT INTO tbl_laporan (
    username_ortu, nama_anak, kelas, semester, tb, bb,
    narasi_agama, narasi_karakter, narasi_fisik, narasi_kognitif,
    narasi_bahasa, narasi_sosem, narasi_seni,
    karakter_1, karakter_2, karakter_3, karakter_4, karakter_5,
    kes_mata, kes_telinga, kes_gigi, kes_rapian, catatan_guru
) VALUES (
    'budi', 'Rizky Ramadhan', 'TK B', 'II / 2025-2026', '118', '22',
    'Rizky sudah hafal doa harian dengan baik. Ia juga rajin melaksanakan sholat dhuha berjamaah di sekolah.',
    'Rizky memiliki jiwa kepemimpinan yang baik. Ia sering menjadi ketua kelompok saat bermain.',
    'Rizky sangat aktif dalam olahraga. Ia mewakili sekolah dalam lomba lari anak tingkat kecamatan.',
    'Rizky mampu berhitung 1-50, penjumlahan sederhana, dan sudah bisa membaca 2-3 suku kata.',
    'Rizky senang bercerita dan memiliki imajinasi yang tinggi. Ia sering membuat cerita sendiri.',
    'Rizky disukai banyak teman. Ia selalu mau berbagi dan menjadi penengah saat ada perselisihan.',
    'Rizky berbakat dalam seni tari. Ia aktif dalam latihan tari untuk acara pentas seni.',
    'SM', 'SM', 'SM', 'SM', 'MM',
    'Baik', 'Baik', 'Perlu Perawatan', 'Baik',
    'Rizky memiliki potensi besar. Terus asah bakat kepemimpinannya. Untuk kesehatan gigi, orang tua diharapkan lebih memperhatikan kebersihan gigi anak.'
);

-- ============================================
-- 6. SAMPLE DATA PPDB (Untuk testing admin)
-- ============================================

INSERT INTO tbl_ppdb (nama_anak, nama_ortu, no_hp, alamat) VALUES 
('Naura Azzahra', 'Bapak Ahmad Fauzi', '081234567891', 'Jl. Mawar Indah No. 12, Bandung'),
('M. Fathir Akbar', 'Ibu Dewi Sartika', '081234567892', 'Jl. Melati Raya No. 45, Bandung'),
('Kayla Maharani', 'Bapak Rizki Ramadhan', '081234567893', 'Jl. Kenanga Permai No. 7, Bandung');

-- ============================================
-- 7. CEK HASIL (Query untuk verifikasi)
-- ============================================

-- Cek semua user
SELECT * FROM tbl_users;

-- Cek semua laporan
SELECT * FROM tbl_laporan;

-- Cek semua PPDB
SELECT * FROM tbl_ppdb;db_tk_badak_putih