// Data Kegiatan Bulanan (Mei 2026 sebagai default)
// Format events: { "YYYY-MM-DD": ["event text", "type"] } type bisa 'normal', 'holiday', 'important', 'sport'
const eventsData = {
    // Mei 2026
    "2026-05-01": ["Libur Hari Buruh", "holiday"],
    "2026-05-02": ["Upacara Hardiknas & Lomba", "important"],
    "2026-05-07": ["Kunjungan ke Balai Kota Anak", "normal"],
    "2026-05-12": ["Pekan Kreativitas (Hari 1)", "important"],
    "2026-05-13": ["Pentas Seni Kelas A", "important"],
    "2026-05-14": ["Pentas Seni Kelas B & Bazaar", "important"],
    "2026-05-20": ["Outing Class: Perpustakaan Umum", "normal"],
    "2026-05-21": ["Workshop Parenting (untuk wali murid)", "normal"],
    "2026-05-28": ["Lomba Da'i Cilik", "sport"],
    "2026-05-30": ["Family Fun Weekend (Sabtu)", "normal"],
    // Juni 2026
    "2026-06-01": ["Lomba Mewarnai & Futsal Mini", "sport"],
    "2026-06-04": ["Libur Idul Adha", "holiday"],
    "2026-06-05": ["Libur Idul Adha", "holiday"],
    "2026-06-15": ["Penanaman Pohon Bersama", "normal"],
    "2026-06-24": ["Peringatan Hari Anak Nasional (awal)", "important"],
    // Juli 2026 (sedikit contoh)
    "2026-07-10": ["Class Meeting", "normal"],
    "2026-07-25": ["Lomba 17an Persiapan", "sport"],
    // Agustus
    "2026-08-17": ["Karnaval Kemerdekaan", "important"],
    "2026-08-18": ["Lomba Makan Kerupuk & Balap Karung", "sport"],
    // September 2026
    "2026-09-05": ["Bakti Sosial & Donasi Buku", "normal"],
    "2026-09-16": ["Maulid Nabi Muhammad SAW", "important"],
    // Oktober libur
    "2026-10-15": ["Libur Semester Gasal", "holiday"],
    "2026-10-16": ["Libur Semester Gasal", "holiday"],
    // November
    "2026-11-10": ["Peringatan Pahlawan (mengenal pahlawan)", "important"],
    "2026-11-25": ["Market Day (jualan hasil karya)", "normal"],
    // Desember event akhir tahun
    "2026-12-15": ["Pentas Akhir Tahun & Rapor", "important"],
    "2026-12-20": ["Libur Akhir Tahun", "holiday"],
};

let currentDate = new Date(2026, 4, 1); // Mei 2026 index 4 = Mei

function renderCalendar() {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth(); // 0-11
    const firstDayOfMonth = new Date(year, month, 1).getDay(); // 0 = Minggu
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    
    // Nama bulan dalam Bahasa Indonesia
    const monthNames = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"];
    document.getElementById("monthYearDisplay").innerText = `${monthNames[month]} ${year}`;
    
    const grid = document.getElementById("calendarGrid");
    grid.innerHTML = "";
    
    // Header hari (Minggu - Sabtu)
    const weekdays = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"];
    weekdays.forEach(day => {
        const dayDiv = document.createElement("div");
        dayDiv.className = "calendar-weekday";
        dayDiv.innerText = day;
        grid.appendChild(dayDiv);
    });
    
    // Menentukan sel kosong sebelum tanggal 1 (berdasarkan firstDayOfMonth)
    let emptyCells = firstDayOfMonth; // karena JS getDay() Minggu = 0
    for (let i = 0; i < emptyCells; i++) {
        const emptyDiv = document.createElement("div");
        emptyDiv.className = "calendar-day";
        emptyDiv.style.backgroundColor = "#fef7e8";
        emptyDiv.style.opacity = "0.6";
        grid.appendChild(emptyDiv);
    }
    
    // Loop untuk tanggal
    for (let d = 1; d <= daysInMonth; d++) {
        const dateKey = `${year}-${String(month+1).padStart(2,'0')}-${String(d).padStart(2,'0')}`;
        const dayDiv = document.createElement("div");
        dayDiv.className = "calendar-day";
        const numberSpan = document.createElement("div");
        numberSpan.className = "day-number";
        numberSpan.innerText = d;
        dayDiv.appendChild(numberSpan);
        
        // Cek event
        if (eventsData[dateKey]) {
            const events = eventsData[dateKey];
            events.forEach(ev => {
                const eventText = typeof ev === 'string' ? ev : ev[0];
                let eventType = 'normal';
                if (Array.isArray(ev) && ev[1]) eventType = ev[1];
                const badge = document.createElement("div");
                badge.className = `event-badge ${eventType === 'holiday' ? 'holiday' : (eventType === 'important' ? 'important' : (eventType === 'sport' ? 'sport' : ''))}`;
                badge.innerText = eventText.length > 28 ? eventText.substring(0,25)+'...' : eventText;
                dayDiv.appendChild(badge);
            });
        } else {
            // optional tambahan kegiatan default untuk hari tertentu (senin-kamis)
            const weekday = new Date(year, month, d).getDay();
            if (weekday === 1 || weekday === 3) {
                const badge = document.createElement("div");
                badge.className = "event-badge";
                badge.innerText = "📚 Kegiatan rutin";
                dayDiv.appendChild(badge);
            } else if (weekday === 4) {
                const badge = document.createElement("div");
                badge.className = "event-badge sport";
                badge.innerText = "⚽ Olahraga";
                dayDiv.appendChild(badge);
            }
        }
        
        // Tooltip klik untuk simulasi detail (alert)
        dayDiv.style.cursor = "pointer";
        dayDiv.addEventListener("click", (function(date, month, year, dayNum) {
            return function() {
                const key = `${year}-${String(month+1).padStart(2,'0')}-${String(dayNum).padStart(2,'0')}`;
                const eventList = eventsData[key];
                if(eventList && eventList.length > 0) {
                    let msg = `📅 Tanggal ${dayNum} ${monthNames[month]} ${year}\n\nKegiatan:\n`;
                    eventList.forEach(ev => {
                        let txt = Array.isArray(ev) ? ev[0] : ev;
                        msg += `- ${txt}\n`;
                    });
                    alert(msg);
                } else {
                    alert(`📌 Tanggal ${dayNum} ${monthNames[month]} ${year}\nTidak ada kegiatan khusus.\nSilakan lihat jadwal mingguan untuk aktivitas rutin.`);
                }
            };
        })(d, month, year, d));
        
        grid.appendChild(dayDiv);
    }
    
    // Hitung total sel agar grid penuh (opsional, untuk estetika tambah kosong di akhir)
    const totalCells = emptyCells + daysInMonth;
    const remaining = totalCells % 7 === 0 ? 0 : 7 - (totalCells % 7);
    for (let i = 0; i < remaining; i++) {
        const emptyDiv = document.createElement("div");
        emptyDiv.className = "calendar-day";
        emptyDiv.style.backgroundColor = "#fef7e8";
        emptyDiv.style.opacity = "0.6";
        grid.appendChild(emptyDiv);
    }
}

function changeMonth(delta) {
    currentDate.setMonth(currentDate.getMonth() + delta);
    renderCalendar();
}

document.getElementById("prevMonth").addEventListener("click", () => changeMonth(-1));
document.getElementById("nextMonth").addEventListener("click", () => changeMonth(1));

// Inisialisasi kalender
renderCalendar();

// Fallback untuk gambar logo jika error
document.querySelector('.logo-circle')?.addEventListener('error', function(e) {
    if(!this.getAttribute('data-fallback')) {
        this.setAttribute('data-fallback', 'true');
        this.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"%3E%3Ccircle fill="%23ffb347" cx="50" cy="50" r="45"/%3E%3Ctext x="50" y="68" font-size="40" text-anchor="middle" fill="white"%3E🦏%3C/text%3E%3C/svg%3E';
    }
});