# 📖 Panduan Operasional Proyek (Runbook & Quickstart)

Panduan praktis langkah demi langkah untuk menjalankan proyek **Legal Chatbot RAG** dari nol (*zero to hero*), serta panduan **reset total & pembersihan** agar repositori kembali rapi setelah selesai digunakan.

---

## 📌 1. Prasyarat Sistem
Sebelum memulai, pastikan perangkat Anda telah terinstal:
- **Git**
- **Docker Desktop** (Pastikan Docker Daemon sedang aktif / *running*)
- **Python 3.10+** *(Opsional, hanya dibutuhkan jika ingin menjalankan unit test secara lokal tanpa Docker)*

---

## 🚀 2. Menjalankan Proyek dari Nol (0 to 100)

### Langkah 1: Siapkan Konfigurasi Lingkungan (`.env`)
Salin file template konfigurasi [.env.example](.env.example) menjadi `.env`:

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**Linux / macOS (Bash):**
```bash
cp .env.example .env
```

Buka file `.env` dan lengkapi nilai variabel berikut:
1. **`GROQ_API_KEY`**: Dapatkan API Key gratis di [console.groq.com](https://console.groq.com/keys).
2. **`APP_API_KEY`**: Kunci rahasia untuk komunikasi aman antar frontend dan backend. Anda bisa membuat string acak yang aman dengan perintah berikut:
   ```powershell
   # PowerShell
   [Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))
   ```
   *(Atau isi dengan string unik panjang, contoh: `sk-legal-production-secret-98765`)*

---

### Langkah 2: Bangun & Jalankan Kontainer (Docker Compose)
Jalankan seluruh ekosistem (ChromaDB, Backend FastAPI, dan Frontend Streamlit) dengan satu perintah:

```bash
docker compose up --build -d
```

> **Catatan:**
> - `-d` (*detached mode*) menjalankan kontainer di latar belakang.
> - Pada build pertama kali, Docker akan mendownload base image dan menginstal dependensi (berlangsung sekitar 1–2 menit).

---

### Langkah 3: Pantau Status & Log Kontainer
Untuk memastikan seluruh service telah berjalan normal:

```bash
# Periksa status seluruh kontainer (pastikan STATUS bernilai "Up")
docker compose ps

# Pantau log secara real-time
docker compose logs -f
```

Untuk keluar dari pemantauan log, tekan `Ctrl + C`.

---

### Langkah 4: Akses Antarmuka & Layanan

| Komponen | URL / Port | Keterangan |
|---|---|---|
| 🌐 **Frontend UI (Streamlit)** | [http://localhost:8501](http://localhost:8501) | Antarmuka interaktif konsultasi hukum |
| ⚡ **Backend API Docs (Swagger)** | [http://localhost:8000/docs](http://localhost:8000/docs) | Dokumentasi OpenAPI dan test API manual |
| 🩺 **Healthcheck Endpoint** | [http://localhost:8000/health](http://localhost:8000/health) | Endpoint status kesiapan AI Engine & ChromaDB |

---

### Langkah 5: Ingest Dokumen Hukum Baru (Jika Diperlukan)
Dokumen default (UU No. 22 Tahun 2009) sudah tersedia di folder `Data/raw/`. Jika Anda menambahkan file PDF regulasi baru ke dalam folder `Data/raw/`:

Jalankan script ETL ingestion di dalam kontainer backend:
```bash
docker compose exec backend python app/ingest.py
```

---

### Langkah 6: Menjalankan Suite Pengujian Otomatis (Pytest)
Jika Anda ingin memverifikasi integritas kode, otentikasi API Key, skema validasi Pydantic, dan fungsi utilitas secara lokal:

```powershell
# Jalankan seluruh 15 unit test
pytest tests/ -v
```

---

## 🧹 3. Panduan Reset Total & Pembersihan (Supaya Rapi Lagi)

Gunakan panduan ini jika Anda telah selesai mendemokan/menguji aplikasi dan ingin mengembalikan kondisi komputer serta repositori ke keadaan bersih dan rapi.

### Opsi A: Matikan Aplikasi Sementara (Simpan Data)
Jika Anda hanya ingin mematikan aplikasi tanpa menghapus hasil index vektor ChromaDB:

```bash
docker compose stop
```

Untuk menyalakannya kembali: `docker compose start`.

---

### Opsi B: Hentikan & Hapus Seluruh Kontainer
Jika ingin mematikan dan mencopot seluruh kontainer, network, dan volume:

```bash
docker compose down -v
```

---

### Opsi C: Reset Total Database Vektor (Hapus Data Chroma)
Jika Anda ingin menghapus seluruh index database ChromaDB agar bisa di-ingest ulang dari awal:

**Windows (PowerShell):**
```powershell
docker compose down -v
Remove-Item -Path "Data\chroma" -Recurse -Force -ErrorAction SilentlyContinue
```

**Linux / macOS (Bash):**
```bash
docker compose down -v
rm -rf Data/chroma
```

---

### Opsi D: Bersihkan Seluruh File Sampah & Cache Lokal (One-Liner)
Perintah praktis satu baris untuk menyapu bersih seluruh file cache Python (`__pycache__`), cache Pytest (`.pytest_cache`), dan log sementara:

**Windows (PowerShell):**
```powershell
Get-ChildItem -Path . -Include __pycache__,.pytest_cache -Recurse -Force | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
```

**Linux / macOS (Bash):**
```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".pytest_cache" -exec rm -rf {} +
```

---

### Opsi E: Bersihkan Image Docker yang Tidak Terpakai
Jika ingin menghemat ruang hard disk komputer dari cache build Docker yang menumpuk:

```bash
docker system prune -f
```

---

### Opsi F: Reset File Lingkungan `.env` ke Kondisi Awal
Jika Anda ingin menghapus kredensial pribadi sebelum melakukan `git push`:

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env -Force
```

**Linux / macOS (Bash):**
```bash
cp .env.example .env
```

---

## 🛠️ 4. Solusi Masalah Umum (Troubleshooting)

1. **Error: `Port 8000 or 8501 is already allocated`**
   - Aplikasi lain di komputer Anda sedang menggunakan port tersebut.
   - Matikan proses terkait atau ubah port host pada file `docker-compose.yml` (misal: `"8502:8501"`).

2. **UI Menampilkan: `Akses Ditolak: API Key tidak valid`**
   - Pastikan nilai `APP_API_KEY` pada file `.env` terisi sama persis dan terbaca oleh Docker Compose.
   - Restart kontainer: `docker compose restart`.

3. **UI Menampilkan: `Rate Limit Exceeded` (HTTP 429)**
   - Anda mengirim pertanyaan lebih dari 5 kali dalam 1 menit (SlowAPI limit), atau kuota gratis Groq API per menit telah tercapai. Tunggu 60 detik sebelum mengirim pertanyaan kembali.

4. **Koneksi ke ChromaDB Gagal saat Startup**
   - Pastikan service `chromadb` berstatus *healthy* dengan menjalankan `docker compose ps`. Kontainer `backend` telah diatur untuk menunggu kesiapan service `chromadb`.
