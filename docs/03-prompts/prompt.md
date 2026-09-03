Analisa Deep Dive Per-File
Saya ingin memahami secara mendalam proyek yang dihasilkan oleh agen AI ini.
Silakan analisis file:

Jelaskan dalam struktur ini:
1. TUJUAN
- Apa tanggung jawab tunggal dari file ini?
- Mengapa file ini ada dalam proyek?

2. PENJELASAN LOGIKA
- Jelaskan kode dari atas ke bawah, blok demi blok
- Untuk setiap fungsi/kelas, jelaskan: apa yang masuk, apa yang terjadi di dalamnya, apa yang keluar
- Tandai logika atau "keajaiban" yang tidak jelas

3. KETERGANTUNGAN
- File/modul apa yang diimpor oleh file INI?
- File lain apa yang diimpor dari file ini?
- Gambarkan peta ketergantungan ASCII sederhana

4. ALIRAN DATA
- Data apa yang masuk ke file ini, dan dari mana?
- Data apa yang keluar dari file ini, dan ke mana tujuannya?
- Jika ada state, di mana letaknya?

5. APA YANG AKAN RUSAK JIKA FILE INI BERUBAH
- Apa yang akan gagal atau berperilaku berbeda jika file ini dihapus atau dimodifikasi?

6. MODEL MENTAL SATU BARIS
- Berikan saya satu kalimat yang dapat saya gunakan untuk mengingat fungsi file ini selamanya.

Bersikaplah lugas, gunakan bahasa yang sederhana, dan berikan contoh konkret menggunakan nama variabel/fungsi sebenarnya dalam kode.





Sekarang gua mau kamu bedah file ini dengan SANGAT detail. Tapi sebelum mulai, lakukan ini dulu:

---

## LANGKAH 0 — CEK KOMPLEKSITAS DULU (WAJIB)

Hitung dan kategorikan file ini:
- Berapa banyak fungsi/method?
- Ada gak logika yang berlapis (loop dalam loop, kondisi dalam kondisi)?
- Ada pattern yang tidak umum (closure, decorator, callback hell, state machine, dsb)?

Lalu putuskan:

JIKA file ini SEDERHANA (< 5 fungsi, logika lurus):
→ Langsung bedah semua dalam 1 respons. Lanjut ke LANGKAH 1.

JIKA file ini KOMPLEKS (banyak fungsi / logika berlapis / pattern tidak umum):
→ JANGAN langsung bedah semua.
→ Tampilkan dulu DAFTAR BAGIAN seperti ini:

"""
File ini cukup kompleks. Gua akan pecah jadi [X] sesi penjelasan biar kamu bener-bener paham, bukan sekadar baca.

BAGIAN 1 — [nama bagian, contoh: "Setup & Konfigurasi Awal"] (baris 1–40)
BAGIAN 2 — [nama bagian, contoh: "Fungsi Utama fetchData()"] (baris 41–90)
BAGIAN 3 — [nama bagian, contoh: "Error Handling & Edge Cases"] (baris 91–130)
...

Mau mulai dari bagian mana? Atau ketik 'mulai dari awal' buat urut dari Bagian 1.
"""

---

## LANGKAH 1 — CARA JELASIN SETIAP BAGIAN

Untuk setiap blok kode yang kamu jelaskan, WAJIB ikuti format ini:

### 🧱 [Nama Blok / Fungsi]
**Kode-nya:**
[tampilkan potongan kode yang sedang dibahas]

**Dalam bahasa manusia:**
[Jelaskan seolah-olah kamu lagi ngobrol sama teman yang belum pernah lihat kode ini.
Hindari jargon teknis. Kalau TERPAKSA pakai istilah teknis, langsung kasih analogi sehari-hari di sebelahnya.]

**Analogi konkret (kalau logikanya tidak obvious):**
[Contoh: "Ini kayak resepsionis yang nerima tamu — dia gak langsung antar ke ruangan, tapi catat nama dulu di buku tamu."]

**Yang masuk:** [data / parameter apa, dalam bentuk apa, dari mana]
**Yang terjadi di dalam:** [step by step, BUKAN ringkasan]
**Yang keluar:** [output-nya apa, pergi ke mana]

**⚠️ Bagian tidak obvious / "keajaiban":**
[Kalau ada baris yang kelihatannya aneh, jelasin KENAPA ditulis begitu.
Contoh: "Kenapa pakai .bind(this) di sini? Karena JavaScript kehilangan konteks 'this' di dalam callback — ini solusinya."]

---

## ATURAN BAHASA (SELALU IKUTI INI)

- Gunakan kata-kata sehari-hari. BUKAN "iterasi" → TAPI "diulang satu-satu"
- BUKAN "menginisialisasi variabel" → TAPI "menyiapkan wadah kosong bernama X"
- BUKAN "mengabstraksi logika" → TAPI "menyembunyikan kerumitan biar bagian lain gak perlu tahu detailnya"
- Kalau ada nama variabel/fungsi yang ambigu (misal: `d`, `tmp`, `handler`), tebak maksudnya dari konteks dan jelaskan tebakan itu
- Selalu sebutkan nama variabel/fungsi yang ASLI dari kode, jangan ganti dengan nama generik

---

## ATURAN PANJANG RESPONS

- Satu sesi = maksimal 1 bagian dari file (bukan seluruh file)
- Di akhir setiap sesi, selalu tanya:
  "Bagian ini sudah jelas? Atau ada baris spesifik yang mau digali lebih dalam sebelum lanjut ke bagian berikutnya?"
- Jangan lanjut ke bagian berikutnya sebelum gua kasih konfirmasi