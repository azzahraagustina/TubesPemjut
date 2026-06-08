const express = require('express');
const mysql = require('mysql2/promise');
const cookieParser = require('cookie-parser');
const path = require('path');

const app = express();

// PERBAIKAN PORT: Menggunakan port bawaan Railway, atau port 3000 jika di local komputer
const port = process.env.PORT || 3000;

// Middleware
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(cookieParser());

// Serve static files (untuk file CSS/JS/Gambar di folder static)
app.use('/static', express.static(path.join(__dirname, 'static')));

// Serve template files langsung sebagai static HTML
app.use(express.static(path.join(__dirname, 'templates')));

// Bagian bawah kode ini (app.listen atau rute database lainnya) jangan dihapus, biarkan saja

// Serve images in root directory (like tk.jpeg)
app.use(express.static(__dirname, {
    setHeaders: (res, path) => {
        if (path.endsWith('.jpeg') || path.endsWith('.jpg') || path.endsWith('.png')) {
            res.setHeader('Content-Type', 'image/jpeg');
        }
    }
}));

// Database Connection function (Sudah Terhubung ke Cloud Railway)
async function getDbConnection() {
    try {
        const connection = await mysql.createConnection({
            host: process.env.MYSQLHOST || 'acela.proxy.rlwy.net',                     // Alamat host public/private Railway kamu
            user: process.env.MYSQLUSER || 'root',                                     // Username bawaan Railway
            password: process.env.MYSQLPASSWORD || 'gNwREBAZxLqJfMzvPLWGttsRtmxnZlYG', // Password MYSQL_ROOT_PASSWORD kamu
            database: process.env.MYSQLDATABASE || 'railway',                          // Nama database utama Railway kamu
            port: process.env.MYSQLPORT ? parseInt(process.env.MYSQLPORT) : 58195      // Port public/private unik milikmu
        });
        return connection;
    } catch (error) {
        console.error("[DATABASE ERROR]:", error.message);
        return null;
    }
}

// Helper to get user from cookie
function getLoggedInUser(req) {
    if (req.cookies.session_user_tk && req.cookies.session_username_tk && req.cookies.session_role_tk) {
        return {
            nama: req.cookies.session_user_tk,
            username: req.cookies.session_username_tk,
            role: req.cookies.session_role_tk
        };
    }
    return null;
}

// ==== API ROUTES ====

app.get('/api/user', (req, res) => {
    const user = getLoggedInUser(req);
    res.json(user || null);
});

app.get('/api/admin/ppdb', async (req, res) => {
    const user = getLoggedInUser(req);
    if (!user || user.role !== 'admin') {
        return res.status(403).json({ error: "Unauthorized" });
    }
    
    const conn = await getDbConnection();
    if (conn) {
        try {
            const [rows] = await conn.execute("SELECT * FROM tbl_ppdb ORDER BY id DESC");
            res.json(rows);
        } catch (err) {
            res.status(500).json({ error: "Database error" });
        } finally {
            await conn.end();
        }
    } else {
        res.status(500).json({ error: "Database connection failed" });
    }
});

app.get('/api/guru/ortu-list', async (req, res) => {
    const user = getLoggedInUser(req);
    if (!user || (user.role !== 'guru' && user.role !== 'admin')) {
        return res.status(403).json({ error: "Unauthorized" });
    }
    
    const conn = await getDbConnection();
    if (conn) {
        try {
            const [rows] = await conn.execute("SELECT username, nama FROM tbl_users WHERE role = 'orang_tua' ORDER BY nama ASC");
            res.json(rows);
        } catch (err) {
            res.status(500).json({ error: "Database error" });
        } finally {
            await conn.end();
        }
    } else {
        res.status(500).json({ error: "Database connection failed" });
    }
});

app.get('/api/guru/laporan', async (req, res) => {
    const user = getLoggedInUser(req);
    if (!user || (user.role !== 'guru' && user.role !== 'admin')) {
        return res.status(403).json({ error: "Unauthorized" });
    }
    
    const conn = await getDbConnection();
    if (conn) {
        try {
            const [rows] = await conn.execute("SELECT * FROM tbl_laporan ORDER BY id DESC");
            res.json(rows);
        } catch (err) {
            res.status(500).json({ error: "Database error" });
        } finally {
            await conn.end();
        }
    } else {
        res.status(500).json({ error: "Database connection failed" });
    }
});

app.get('/api/guru/laporan/:username_ortu', async (req, res) => {
    const user = getLoggedInUser(req);
    if (!user || (user.role !== 'guru' && user.role !== 'admin')) {
        return res.status(403).json({ error: "Unauthorized" });
    }
    
    const { username_ortu } = req.params;
    const conn = await getDbConnection();
    if (conn) {
        try {
            const [rows] = await conn.execute("SELECT * FROM tbl_laporan WHERE username_ortu = ?", [username_ortu]);
            if (rows.length > 0) {
                res.json(rows[0]);
            } else {
                res.status(404).json({ error: "Laporan tidak ditemukan" });
            }
        } catch (err) {
            res.status(500).json({ error: "Database error" });
        } finally {
            await conn.end();
        }
    } else {
        res.status(500).json({ error: "Database connection failed" });
    }
});

app.delete('/api/guru/laporan/:username_ortu', async (req, res) => {
    const user = getLoggedInUser(req);
    if (!user || (user.role !== 'guru' && user.role !== 'admin')) {
        return res.status(403).json({ error: "Unauthorized" });
    }
    
    const { username_ortu } = req.params;
    const conn = await getDbConnection();
    if (conn) {
        try {
            await conn.execute("DELETE FROM tbl_laporan WHERE username_ortu = ?", [username_ortu]);
            res.json({ success: true, message: "Laporan berhasil dihapus" });
        } catch (err) {
            res.status(500).json({ error: "Database error" });
        } finally {
            await conn.end();
        }
    } else {
        res.status(500).json({ error: "Database connection failed" });
    }
});

app.get('/api/ortu/rapor', async (req, res) => {
    const user = getLoggedInUser(req);
    if (!user || user.username === undefined) {
        return res.status(401).json({ error: "Unauthorized" });
    }

    const conn = await getDbConnection();
    if (conn) {
        try {
            const [rows] = await conn.execute("SELECT * FROM tbl_laporan WHERE username_ortu = ?", [user.username]);
            if (rows.length > 0) {
                res.json(rows[0]);
            } else {
                res.json(null); // No report yet
            }
        } catch (err) {
            res.status(500).json({ error: "Database error" });
        } finally {
            await conn.end();
        }
    } else {
        res.status(500).json({ error: "Database connection failed" });
    }
});

// ==== PAGE ROUTES (Optional, as express.static handles them, but good for custom paths) ====

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates', 'index.html'));
});

app.get('/login.html', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates', 'login.html'));
});

app.get('/register', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates', 'register.html'));
});

app.get('/logout', (req, res) => {
    res.clearCookie('session_user_tk');
    res.clearCookie('session_username_tk');
    res.clearCookie('session_role_tk');
    res.redirect('/');
});


// ==== POST ROUTES ====

app.post('/register', async (req, res) => {
    const { nama, username, password } = req.body;
    const conn = await getDbConnection();
    if (conn) {
        try {
            await conn.execute("INSERT INTO tbl_users (nama, username, password, role) VALUES (?, ?, ?, 'orang_tua')", [nama || '', username || '', password || '']);
            res.redirect('/login.html');
        } catch (err) {
            res.redirect('/register');
        } finally {
            await conn.end();
        }
    } else {
        res.redirect('/register');
    }
});

// ==========================================
// KODE OTOMATIS BIKIN AKUN DEMO & FIX ROUTING
// ==========================================

// Fungsi rahasia agar server otomatis ngisi akun admin & guru kalau DB masih kosong
async function autoCreateAccounts(conn) {
    try {
        const [rows] = await conn.execute("SELECT COUNT(*) as count FROM tbl_users");
        if (rows[0].count === 0) {
            console.log("[SYSTEM]: Database masih kosong, otomatis mendaftarkan akun demo...");
            await conn.execute("INSERT INTO tbl_users (nama, username, password, role) VALUES ('Kepala Sekolah', 'admin', 'admin123', 'admin')");
            await conn.execute("INSERT INTO tbl_users (nama, username, password, role) VALUES ('Ibu Guru Badak', 'guru', 'guru123', 'guru')");
            await conn.execute("INSERT INTO tbl_users (nama, username, password, role) VALUES ('Bapak Budi', 'budi', 'budi123', 'orang_tua')");
            console.log("[SYSTEM]: Akun admin, guru, dan budi siap dipakai!");
        }
    } catch (err) {
        console.error("Gagal auto-create akun:", err.message);
    }
}

// Handler login tunggal
const prosesMasukPintu = async (req, res) => {
    const { username, password } = req.body;
    const conn = await getDbConnection();
    let userValid = null;

    if (conn) {
        try {
            // Panggil fungsi pembuat akun otomatis
            await autoCreateAccounts(conn);

            const [rows] = await conn.execute("SELECT * FROM tbl_users WHERE username = ? AND password = ?", [username || '', password || '']);
            if (rows.length > 0) {
                userValid = rows[0];
            }
        } catch (err) {
            console.error("Error login:", err.message);
        } finally {
            await conn.end();
        }
    }

    if (userValid) {
        res.cookie('session_user_tk', userValid.nama, { path: '/' });
        res.cookie('session_username_tk', userValid.username, { path: '/' });
        res.cookie('session_role_tk', userValid.role, { path: '/' });
        res.redirect('/');
    } else {
        res.redirect('/login.html');
    }
};

// Daftarkan rute POST biar gak error 405 lagi di browser
app.post('/login.html', prosesMasukPintu);
app.post('/login', prosesMasukPintu);

// Biar kalau ketik URL tanpa .html tetep kebuka halaman loginnya
app.get('/login', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates', 'login.html'));
});

app.post('/guru/input_laporan', async (req, res) => {
    const user = getLoggedInUser(req);
    if (!user || (user.role !== 'guru' && user.role !== 'admin')) {
        return res.status(403).send("Akses dilarang");
    }

    const { 
        username_ortu, nama_anak, kelas, semester, tb, bb, 
        narasi_agama, narasi_karakter, narasi_fisik, narasi_kognitif, narasi_bahasa, narasi_sosem, narasi_seni,
        karakter_1 = 'MM', karakter_2 = 'MM', karakter_3 = 'MM', karakter_4 = 'MM', karakter_5 = 'MM',
        kes_mata = 'Baik', kes_telinga = 'Baik', kes_gigi = 'Baik', kes_rapian = 'Baik',
        catatan_guru
    } = req.body;

    const conn = await getDbConnection();
    if (conn) {
        try {
            await conn.execute("DELETE FROM tbl_laporan WHERE username_ortu = ?", [username_ortu || '']);
            
            const sql = `INSERT INTO tbl_laporan (
                username_ortu, nama_anak, kelas, semester, tb, bb,
                narasi_agama, narasi_karakter, narasi_fisik, narasi_kognitif,
                narasi_bahasa, narasi_sosem, narasi_seni,
                karakter_1, karakter_2, karakter_3, karakter_4, karakter_5,
                kes_mata, kes_telinga, kes_gigi, kes_rapian,
                catatan_guru
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`;

            await conn.execute(sql, [
                username_ortu || '', nama_anak || '', kelas || '', semester || '', tb || '', bb || '',
                narasi_agama || '', narasi_karakter || '', narasi_fisik || '', narasi_kognitif || '',
                narasi_bahasa || '', narasi_sosem || '', narasi_seni || '',
                karakter_1, karakter_2, karakter_3, karakter_4, karakter_5,
                kes_mata, kes_telinga, kes_gigi, kes_rapian,
                catatan_guru || ''
            ]);
        } catch (err) {
            console.error(err);
        } finally {
            await conn.end();
        }
    }
    if (req.headers['content-type'] === 'application/json' || req.xhr) {
        return res.json({ success: true, message: "Laporan berhasil disimpan" });
    }
    res.redirect('/laporan.html');
});

app.post('/proses_ppdb', async (req, res) => {
    const { nama_anak, nama_ortu, no_hp, alamat } = req.body;
    const conn = await getDbConnection();
    if (conn) {
        try {
            await conn.execute("INSERT INTO tbl_ppdb (nama_anak, nama_ortu, no_hp, alamat) VALUES (?, ?, ?, ?)", [nama_anak || '', nama_ortu || '', no_hp || '', alamat || '']);
        } catch (err) {
            console.error(err);
        } finally {
            await conn.end();
        }
    }
    res.redirect('/');
});

app.listen(port, () => {
    console.log(`Sistem 3-Role 100% JS API Aktif di http://localhost:${port} ... 🚀✨`);
});
