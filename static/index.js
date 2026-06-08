async function renderAuth() {
    const authZone = document.getElementById('authZone');
    try {
        const res = await fetch('/api/user');
        const user = await res.json();
        
        if (user && user.nama) {
            authZone.innerHTML = `
                <span style="background:#fff; padding:10px 18px; border-radius:50px;">👤 ${user.role === 'admin' ? 'Admin' : user.role === 'guru' ? 'Guru' : 'Orang Tua'}: ${user.nama}</span>
                <a href="/logout" class="nav-btn red" style="background:#e53935;">🚪 Keluar</a>
            `;
        } else {
            authZone.innerHTML = `<a href="/login.html" class="nav-btn blue">🔑 Masuk Portal</a>`;
        }
    } catch(e) {
        authZone.innerHTML = `<a href="/login.html" class="nav-btn blue">🔑 Masuk Portal</a>`;
    }
}

// Jalankan fungsi saat file dimuat
renderAuth();