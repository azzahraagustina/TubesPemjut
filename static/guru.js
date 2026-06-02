function switchTab(id) {
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    const idx = ['tab-input','tab-daftar','tab-nilai'].indexOf(id);
    document.querySelectorAll('.tab-btn')[idx].classList.add('active');
    if (id === 'tab-daftar') renderDaftar();
}

function showToast(msg, ok) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.style.background = ok === false ? '#c62828' : '#2e7d32';
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 3000);
}

function getKarakterRows() {
    const rows = document.querySelectorAll('#karakter_rows .karakter-row');
    return Array.from(rows).map(r => ({
        bidang: r.querySelector('label').textContent.trim(),
        capaian: r.querySelector('select').value
    }));
}

function simpanLaporan() {
    const nama = document.getElementById('inp_nama').value.trim();
    if (!nama) { showToast('⚠️ Nama anak wajib diisi!', false); return; }

    const data = {
        nama,
        kelas:          document.getElementById('inp_kelas').value,
        semester:       document.getElementById('inp_semester').value,
        fase:           document.getElementById('inp_fase').value,
        tb:             document.getElementById('inp_tb').value,
        bb:             document.getElementById('inp_bb').value,
        guru:           document.getElementById('inp_guru').value,
        agama:          document.getElementById('inp_agama').value,
        karakter_narasi: document.getElementById('inp_karakter_narasi').value,
        fisik:          document.getElementById('inp_fisik').value,
        kognitif:       document.getElementById('inp_kognitif').value,
        bahasa:         document.getElementById('inp_bahasa').value,
        sosem:          document.getElementById('inp_sosem').value,
        seni:           document.getElementById('inp_seni').value,
        karakter_capaian: getKarakterRows(),
        mata:           document.getElementById('inp_mata').value,
        telinga:        document.getElementById('inp_telinga').value,
        gigi:           document.getElementById('inp_gigi').value,
        rapian:         document.getElementById('inp_rapian').value,
        catatan:        document.getElementById('inp_catatan').value,
        tanggal:        new Date().toLocaleDateString('id-ID', {year:'numeric',month:'long',day:'numeric'})
    };

    // Simpan laporan
    const lKey = 'laporan_' + nama.replace(/\s+/g,'_').toLowerCase();
    localStorage.setItem(lKey, JSON.stringify(data));

    // Daftarkan ke daftar_murid
    let murid = [];
    try { murid = JSON.parse(localStorage.getItem('daftar_murid') || '[]'); } catch {}
    const sudahAda = murid.find(m => m.nama.toLowerCase() === nama.toLowerCase());
    if (!sudahAda) {
        murid.push({ id: Date.now().toString(), nama, kelas: data.kelas });
        localStorage.setItem('daftar_murid', JSON.stringify(murid));
    }

    showToast('✅ Laporan ' + nama + ' berhasil disimpan!');
}

function renderDaftar() {
    const container = document.getElementById('daftar_container');
    let murid = [];
    try { murid = JSON.parse(localStorage.getItem('daftar_murid') || '[]'); } catch {}

    const punya = murid.filter(m => {
        const k = 'laporan_' + m.nama.replace(/\s+/g,'_').toLowerCase();
        return !!localStorage.getItem(k);
    });

    if (!punya.length) {
        container.innerHTML = '<div class="empty-state">🦏 Belum ada laporan tersimpan</div>';
        return;
    }

    container.innerHTML = '<div class="laporan-list">' + punya.map(m => {
        const k = 'laporan_' + m.nama.replace(/\s+/g,'_').toLowerCase();
        let lap = null;
        try { lap = JSON.parse(localStorage.getItem(k)); } catch {}
        return `
        <div class="laporan-item">
            <div>
                <h4>👧 ${m.nama} <span class="badge-sm">${m.kelas}</span></h4>
                <p>📅 ${lap ? lap.tanggal : '-'} &nbsp;|&nbsp; Semester: ${lap ? lap.semester : '-'}</p>
            </div>
            <div style="display:flex;gap:8px;flex-wrap:wrap;">
                <button class="btn-hapus" onclick="editLaporan('${m.id}','${m.nama.replace(/'/g,"\\'")}')">✏️ Edit</button>
                <button class="btn-hapus" style="background:#fff3e0;color:#e65100;" onclick="hapusLaporan('${m.id}','${m.nama.replace(/'/g,"\\'")}')">🗑️ Hapus</button>
            </div>
        </div>`;
    }).join('') + '</div>';
}

function hapusLaporan(id, nama) {
    if (!confirm('Hapus laporan untuk ' + nama + '?')) return;
    const lKey = 'laporan_' + nama.replace(/\s+/g,'_').toLowerCase();
    localStorage.removeItem(lKey);
    let murid = [];
    try { murid = JSON.parse(localStorage.getItem('daftar_murid') || '[]'); } catch {}
    murid = murid.filter(m => m.id !== id);
    localStorage.setItem('daftar_murid', JSON.stringify(murid));
    renderDaftar();
    showToast('🗑️ Laporan ' + nama + ' dihapus');
}

function editLaporan(id, nama) {
    const lKey = 'laporan_' + nama.replace(/\s+/g,'_').toLowerCase();
    let lap = null;
    try { lap = JSON.parse(localStorage.getItem(lKey)); } catch {}
    if (!lap) return;

    document.getElementById('inp_nama').value = lap.nama || '';
    document.getElementById('inp_kelas').value = lap.kelas || 'TK A';
    document.getElementById('inp_semester').value = lap.semester || '';
    document.getElementById('inp_fase').value = lap.fase || 'Fondasi';
    document.getElementById('inp_tb').value = lap.tb || '';
    document.getElementById('inp_bb').value = lap.bb || '';
    document.getElementById('inp_guru').value = lap.guru || '';
    document.getElementById('inp_agama').value = lap.agama || '';
    document.getElementById('inp_karakter_narasi').value = lap.karakter_narasi || '';
    document.getElementById('inp_fisik').value = lap.fisik || '';
    document.getElementById('inp_kognitif').value = lap.kognitif || '';
    document.getElementById('inp_bahasa').value = lap.bahasa || '';
    document.getElementById('inp_sosem').value = lap.sosem || '';
    document.getElementById('inp_seni').value = lap.seni || '';
    document.getElementById('inp_mata').value = lap.mata || 'Baik';
    document.getElementById('inp_telinga').value = lap.telinga || 'Baik';
    document.getElementById('inp_gigi').value = lap.gigi || 'Baik';
    document.getElementById('inp_rapian').value = lap.rapian || 'Baik';
    document.getElementById('inp_catatan').value = lap.catatan || '';

    if (lap.karakter_capaian) {
        const rows = document.querySelectorAll('#karakter_rows .karakter-row');
        lap.karakter_capaian.forEach((kc, i) => {
            if (rows[i]) rows[i].querySelector('select').value = kc.capaian;
        });
    }

    switchTab('tab-input');
    window.scrollTo({ top: 0, behavior: 'smooth' });
    showToast('📂 Data laporan dimuat, siap diedit');
}