const API = 'http://localhost:3000/api';
let filtered = [], currentId = null, deleteId = null, page = 1;
const PER_PAGE = 10;

async function loadStats() {
    try {
        const j = await (await fetch(`${API}/ppdb/stats`)).json();
        if (!j.success) return;
        document.getElementById('statTotal').textContent   = j.data.total;
        document.getElementById('statPending').textContent  = j.data.pending;
        document.getElementById('statDiterima').textContent = j.data.diterima;
        document.getElementById('statDitolak').textContent  = j.data.ditolak;
    } catch(e) {}
}

async function loadData() {
    const search = document.getElementById('searchInput').value.trim();
    const status = document.getElementById('filterStatus').value;
    try {
        const j = await (await fetch(`${API}/ppdb?search=${encodeURIComponent(search)}&status=${status}`)).json();
        if (!j.success) { showToast('Gagal memuat data', 'error'); return; }
        filtered = j.data; page = 1; renderTable();
    } catch(e) {
        document.getElementById('tableBody').innerHTML =
            `<tr><td colspan="7"><div class="empty-state"><div class="emoji">❌</div><p>Tidak dapat terhubung ke server. Pastikan backend berjalan.</p></div></td></tr>`;
    }
}

function renderTable() {
    const tbody = document.getElementById('tableBody');
    const total = filtered.length;
    const start = (page-1)*PER_PAGE;
    const slice = filtered.slice(start, start+PER_PAGE);
    document.getElementById('pageInfo').textContent =
        total===0 ? 'Tidak ada data' : `Menampilkan ${start+1}–${Math.min(start+PER_PAGE,total)} dari ${total} pendaftar`;
    renderPagination(total);
    if (!slice.length) { tbody.innerHTML=`<tr><td colspan="7"><div class="empty-state"><div class="emoji">🔍</div><p>Tidak ada data yang cocok</p></div></td></tr>`; return; }
    const badges = { pending:'<span class="badge badge-pending">⏳ Pending</span>', diterima:'<span class="badge badge-diterima">✅ Diterima</span>', ditolak:'<span class="badge badge-ditolak">❌ Ditolak</span>' };
    tbody.innerHTML = slice.map((d,i) => {
        const ini = d.nama_siswa.split(' ').slice(0,2).map(w=>w[0]).join('').toUpperCase();
        const tgl = d.created_at ? new Date(d.created_at).toLocaleDateString('id-ID',{day:'2-digit',month:'short',year:'numeric'}) : '—';
        return `<tr>
            <td style="color:#a0693a;font-size:0.82rem;font-weight:700;">${start+i+1}</td>
            <td><div class="cell-nama"><div class="avatar">${esc(ini)}</div><div><div class="name">${esc(d.nama_siswa)}</div><div class="wali">Wali: ${esc(d.nama_wali)}</div></div></div></td>
            <td style="font-size:0.88rem;">${esc(d.no_hp)}</td>
            <td style="font-size:0.84rem;color:#a0693a;max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${esc(d.alamat)}</td>
            <td style="font-size:0.83rem;color:#a0693a;">${tgl}</td>
            <td>${badges[d.status]||''}</td>
            <td><div class="action-group">
                <button class="aksi-btn edit" onclick="openDetail(${d.id})">✏️ Edit</button>
                <button class="aksi-btn del"  onclick="openDeleteConfirm(${d.id},'${esc(d.nama_siswa)}')">🗑️</button>
            </div></td>
        </tr>`;
    }).join('');
}

function renderPagination(total) {
    const pages=Math.ceil(total/PER_PAGE), wrap=document.getElementById('pageBtns');
    if (pages<=1){wrap.innerHTML='';return;}
    wrap.innerHTML=Array.from({length:pages},(_,i)=>`<button class="page-btn ${i+1===page?'active':''}" onclick="goPage(${i+1})">${i+1}</button>`).join('');
}
function goPage(p){page=p;renderTable();}

async function openDetail(id) {
    currentId=id;
    try {
        const j = await (await fetch(`${API}/ppdb/${id}`)).json();
        if (!j.success) return;
        const d=j.data;
        document.getElementById('modalNama').textContent = d.nama_siswa;
        document.getElementById('modalSub').textContent  = `ID #${d.id} · Didaftarkan ${new Date(d.created_at).toLocaleDateString('id-ID',{day:'2-digit',month:'long',year:'numeric'})}`;
        document.getElementById('modalStatus').value     = d.status;
        document.getElementById('modalCatatan').value    = d.catatan||'';
        const tglLahir = d.tanggal_lahir ? new Date(d.tanggal_lahir).toLocaleDateString('id-ID') : '—';
        document.getElementById('detailGrid').innerHTML=`
            <div class="detail-box"><div class="d-label">Nama Wali</div><div class="d-value">${esc(d.nama_wali)}</div></div>
            <div class="detail-box"><div class="d-label">No. HP</div><div class="d-value">${esc(d.no_hp)}</div></div>
            <div class="detail-box"><div class="d-label">Tgl Lahir</div><div class="d-value">${tglLahir}</div></div>
            <div class="detail-box"><div class="d-label">Jenis Kelamin</div><div class="d-value">${d.jenis_kelamin==='L'?'👦 Laki-laki':'👧 Perempuan'}</div></div>
            <div class="detail-box wide"><div class="d-label">Alamat Lengkap</div><div class="d-value">${esc(d.alamat)}</div></div>`;
        document.getElementById('detailOverlay').classList.add('show');
    } catch(e){showToast('Gagal memuat detail','error');}
}
function closeDetailModal(){document.getElementById('detailOverlay').classList.remove('show');}
function closeDetail(e){if(e.target===e.currentTarget)closeDetailModal();}

async function saveStatus() {
    const status=document.getElementById('modalStatus').value, catatan=document.getElementById('modalCatatan').value;
    try {
        const j=await (await fetch(`${API}/ppdb/${currentId}/status`,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({status,catatan})})).json();
        if(!j.success){showToast(j.message,'error');return;}
        showToast('Status berhasil diperbarui ✅','success');
        closeDetailModal();loadData();loadStats();
    } catch(e){showToast('Gagal menyimpan','error');}
}

function openDeleteConfirm(id,nama){deleteId=id;document.getElementById('confirmNama').textContent=nama;document.getElementById('confirmOverlay').classList.add('show');}
function closeConfirmModal(){document.getElementById('confirmOverlay').classList.remove('show');}
function closeConfirm(e){if(e.target===e.currentTarget)closeConfirmModal();}

async function confirmDelete() {
    try {
        const j=await (await fetch(`${API}/ppdb/${deleteId}`,{method:'DELETE'})).json();
        if(!j.success){showToast(j.message,'error');return;}
        showToast('Data berhasil dihapus 🗑️','success');
        closeConfirmModal();loadData();loadStats();
    } catch(e){showToast('Gagal menghapus','error');}
}

function exportCSV() {
    if(!filtered.length){showToast('Tidak ada data untuk di-export','error');return;}
    const h=['ID','Nama Siswa','Nama Wali','No HP','Alamat','Jenis Kelamin','Status','Catatan','Tgl Daftar'];
    const rows=filtered.map(d=>[d.id,d.nama_siswa,d.nama_wali,d.no_hp,d.alamat,d.jenis_kelamin==='L'?'Laki-laki':'Perempuan',d.status,d.catatan||'',new Date(d.created_at).toLocaleDateString('id-ID')].map(v=>`"${String(v).replace(/"/g,'""')}"`).join(','));
    const blob=new Blob(['\uFEFF'+[h.join(','),...rows].join('\n')],{type:'text/csv;charset=utf-8;'});
    const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=`ppdb-${new Date().toISOString().slice(0,10)}.csv`;a.click();
    showToast('CSV berhasil diunduh 📥','success');
}

let tt;
function showToast(msg,type=''){
    const el=document.getElementById('toast');el.textContent=msg;el.className=`show ${type}`;
    clearTimeout(tt);tt=setTimeout(()=>el.className='',3000);
}
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}

loadStats();
loadData();