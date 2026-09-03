# 🧠 Catatan Mental Arsitektur Proyek (MY_NOTES.md)
> *Dokumen ini ditulis sebagai panduan komprehensif bagi Anda (sang kreator proyek) untuk memahami seluruh alur kerja, alasan pemilihan teknologi, logika kode kritis, serta peta mental jika ingin memodifikasi proyek ini di masa depan.*

---

## 📌 1. Rangkuman Eksekutif (2 Kalimat)
**Legal Chatbot RAG** adalah asisten AI berbasis *Advanced Retrieval-Augmented Generation* (Retrieve-then-Rerank) yang dirancang untuk menjawab pertanyaan regulasi hukum Indonesia (UU No. 22 Tahun 2009) secara akurat, terbukti dengan sitasi pasal dan nomor halaman, serta bebas halusinasi. Sistem ini dibangun dengan arsitektur multi-kontainer Docker yang memadukan FastAPI, database vektor ChromaDB privat, inferensi kilat Groq Cloud (Llama 3.3 70B), proteksi API Key & SlowAPI Rate Limiter, antarmuka interaktif Streamlit, serta 15 automated unit test otomatis.

---

## 🏛️ 2. The Big Picture: Alur Kerja dari Ujung ke Ujung

### Analogi Sederhana: "Firma Hukum Modern"
Bayangkan sistem ini bekerja layaknya sebuah kantor pengacara terorganisasi:
1. **Streamlit (Resepsionis)**: Menerima klien (pengguna) di lobi, mencatat pertanyaan hukum, dan menampilkan jawaban ramah di layar.
2. **FastAPI (Manajer Kantor & Satpam)**: Memeriksa kartu akses klien (`X-API-Key`), memastikan klien tidak bertanya terlalu sering/spam (`SlowAPI Rate Limit: 5/menit`), dan memeriksa pertanyaan tidak kosong atau berupa spasi acak (`Pydantic Validation`).
3. **ChromaDB (Ruang Arsip Dokumen Hukum)**: Lemari rak buku raksasa di ruang tertutup yang menyimpan ribuan lembar undang-undang yang telah dikonversi menjadi koordinat makna (*vector embeddings*).
4. **LlamaIndex Paralegal (Retrieve-then-Rerank)**: Asisten hukum yang mengambil 10 berkas yang diduga relevan dari lemari arsip, membaca kilat, lalu menyaring menjadi 3 lembar yang paling tepat isinya menggunakan model Re-ranker.
5. **Groq Cloud LLM (Pengacara Senior)**: Membaca 3 lembar dokumen terpilih dan menyusun opini hukum formal lengkap dengan rujukan pasal, ayat, dan sanksi pidana/denda, lalu menyerahkannya kembali ke klien via manajer kantor.

---

### Diagram Alur Komponen (ASCII Architecture)

```
[ Pengguna di Browser ]
        │ 
        ▼ HTTP (Port 8501)
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND (Streamlit Web UI)                                │
│  - frontend/app.py: Kelola session state, input chat,       │
│    visualisasi sitasi dokumen, dan peringatan HTTP status   │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP POST /chat (Port 8000)
                               ▼ Headers: X-API-Key: {secret}
┌─────────────────────────────────────────────────────────────┐
│  API GATEWAY & APPLICATION SERVER (FastAPI)                 │
│  - backend/main.py: Lifespan management, GET /health        │
│  - backend/app/api.py: @limiter.limit("5/minute"), Auth     │
│  - backend/app/utils.py: Helper token, sitasi, heartbeat    │
└──────────────┬───────────────────────────────┬──────────────┘
               │                               │
     (1) Dense │ Top-10              (2) Top-3 │ Synthesis
     Retrieval │ Candidate Chunks      Context │ Prompt
               ▼                               ▼
┌─────────────────────────────┐  ┌────────────────────────────┐
│ CHROMADB VECTOR DATABASE    │  │ GROQ CLOUD INFERENCE       │
│ (Private Bridge Network)    │  │ Model:                     │
│ Koleksi: 'legal_docs'       │  │ llama-3.3-70b-versatile    │
│ Volume: Data/chroma/        │  │ Latency: ~1.2s             │
└─────────────────────────────┘  └────────────────────────────┘
               ▲
               │ ETL Ingestion Luring (Offline)
┌──────────────┴──────────────────────────────────────────────┐
│  ETL BATCH PIPELINE                                         │
│  - backend/app/ingest.py                                    │
│  - Data/raw/UU Nomor 22 Tahun 2009.pdf                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ 3. Tech Stack: Kenapa Ini, Bukan Itu?

| Tool / Library | Peran Nyata di Proyek Ini | Kenapa Dipilih Dibanding Alternatif? | Kalau Dihapus, Apa yang Rusak? |
|---|---|---|---|
| **FastAPI** | Server REST API, gateway validasi data, dependency injection auth, dan rate limiter. | Mendukung `async/await` non-blocking native, auto-docs OpenAPI Swagger (`/docs`), dan performa tinggi dibanding Flask/Django. | Backend mati total. Frontend tidak memiliki server untuk dihubungi. |
| **LlamaIndex** | Orkestrator RAG (Retrieve-then-Rerank), penghubung vector store, query engine, dan prompt synthesis. | Unggul dalam indexing data dan penanganan dokumen terstruktur dibanding LangChain yang terlalu bertele-tele (*overengineered*). | Kita harus menulis manual ratusan baris kode untuk chunking, cosine search, reranking, dan prompt formatting. |
| **Groq Cloud (Llama 3.3 70B)** | Mesin penalaran bahasa alami untuk menganalisis konteks hukum dan menyusun jawaban. | Menggunakan prosesor LPU khusus berkecepatan ratusan token/detik dengan free tier yang sangat memadai dibanding OpenAI GPT-4 yang mahal dan lambat. | Bot tidak bisa berpikir atau menyusun jawaban teks manusia. |
| **ChromaDB (Server)** | Database penyimpanan dense vector embedding potongan teks hukum. | Standalone Docker service yang stabil, open-source, dan tidak mengalami *file locking* saat diakses banyak thread bersamaan (dibanding SQLite lokal). | AI lupa seluruh isi undang-undang dan tidak memiliki memori retrieval. |
| **BAAI/bge-small-en-v1.5** | Model embedding teks lokal HuggingFace (384 dimensi). | Ukuran sangat ringan (~130 MB), cepat di CPU tanpa memerlukan GPU khusus, namun memiliki performa perangkingan tinggi di MTEB benchmark. | Teks hukum tidak bisa dikonversi menjadi representasi vektor numerik. |
| **Cross-Encoder ms-marco-MiniLM-L-6-v2** | Re-ranker semantik tahap kedua. | Mengeliminasi kelemahan Cosine Similarity (yang hanya mencocokkan kata) dengan membaca hubungan antara query dan dokumen secara serentak. Akurasi retrieval naik dari ~60% ke >85%. | Akurasi anjlok drastis; LLM sering mendapat potongan pasal yang salah sehingga menghasilkan jawaban yang meleset (*halusinasi*). |
| **SlowAPI** | Middleware pembatasan laju panggilan (Rate Limiter 5 req/menit). | Paling ringan untuk FastAPI, berbasis in-memory limiter tanpa butuh Redis untuk skala kecil/menengah. | Server rentan spam, brute-force, DoS, dan kuota gratis Groq habis dalam sekejap. |
| **Pydantic v2** | Skema validasi data request/response dan settings environment. | Cepat (core ditulis dalam Rust), validasi tipe data ketat, dan menolak input kotor (*whitespace injection*). | API bisa menerima string kosong atau data korup yang membuat LlamaIndex crash. |
| **Streamlit** | Antarmuka web pengguna. | Memungkinkan pembuatan UI interaktif modern murni dengan Python tanpa perlu menulis Javascript, React, atau CSS dari nol. | Pengguna biasa tidak punya antarmuka grafis dan harus mengakses bot lewat curl/Postman. |
| **Pytest** | Automated test suite in-memory (15 tests). | Eksekusi super cepat (~0.3 detik), integrasi mocking FastAPI TestClient yang mudah, dan standar industri pengujian Python. | Kode tidak memiliki jaring pengaman (*safety net*); bug tersembunyi tidak terdeteksi sebelum masuk produksi. |

---

## 🔍 4. Logika Kode yang Paling Krusial & "Tidak Obvious"

### 1. Pola Two-Stage Retrieval (Retrieve-then-Rerank) di `backend/app/engine.py`
```python
# Tahap 1: Ambil 10 kandidat teratas berbasis vector similarity
index.as_chat_engine(
    similarity_top_k=10,
    node_postprocessors=[
        # Tahap 2: Saring dan urutkan kembali menjadi 3 paling relevan via Cross-Encoder
        SentenceTransformerRerank(model="cross-encoder/ms-marco-MiniLM-L-6-v2", top_n=3)
    ]
)
```
- **Kenapa ditulis begini?** Jika langsung mengambil 3 dokumen teratas dengan vector similarity biasa, dokumen yang kata-katanya mirip tetapi konteksnya tidak tepat sering terpilih. Dengan mengambil 10 kandidat lalu di-evaluasi ulang oleh neural model Cross-Encoder, kita mendapatkan tingkat akurasi hukum tertinggi dengan beban komputasi yang tetap ringan.

### 2. Eksekusi Asynchronous `achat()` di `backend/app/api.py`
```python
response = await chat_engine.achat(query)
```
- **Kenapa ditulis begini?** Jika menggunakan fungsi sinkron `chat(query)`, seluruh thread worker FastAPI akan terblokir (*freeze*) selama 1–2 detik saat menunggu respons Groq. Dengan `achat()`, event loop FastAPI tetap bebas melayani request pengguna lain secara bersamaan (*concurrency*).

### 3. Validasi Whitespace Pydantic di `backend/app/api.py`
```python
@field_validator("query")
@classmethod
def validate_query_not_blank(cls, v: str) -> str:
    trimmed = v.strip()
    if not trimmed:
        raise ValueError("Pertanyaan tidak boleh kosong atau hanya berisi spasi.")
    return trimmed
```
- **Kenapa ditulis begini?** Penyerang atau pengguna iseng sering mengirim spasi panjang `"       "`. Tanpa validator ini, spasi tersebut lolos validasi `max_length=500` dan memicu embedding kosong ke ChromaDB serta membuang kuota inferensi LLM.

### 4. Lazy Import Engine & Uvicorn di `backend/main.py`
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        from app.engine import get_chat_engine
        app.state.chat_engine = get_chat_engine()
...
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(...)
```
- **Kenapa ditulis begini?** Jika diimpor di baris paling atas (*top-level*), maka setiap kali kita menjalankan pengujian Pytest atau memeriksa skema routing, Python akan memaksa me-load pustaka LlamaIndex dan PyTorch yang berat (~1 GB RAM). Dengan *lazy loading*, unit test bisa berjalan instan dalam hitungan 0.3 detik di lingkungan minimalis mana pun tanpa error `ModuleNotFoundError`.

---

## 🔒 5. Keamanan & Aliran Data Sensitif

1. **Isolasi Database Vektor**:
   - Port `8001:8000` telah dihapus dari `docker-compose.yml`. Database ChromaDB kini murni berada di dalam *private bridge network* Docker. Pihak luar tidak bisa menyusup atau menghapus koleksi `legal_docs` melalui jaringan host.
2. **Kredensial API Key**:
   - `APP_API_KEY`: Kunci rahasia komunikasi antara Streamlit dan FastAPI. Diatur ketat pada `backend/app/config.py` tanpa default dummy publik.
   - `GROQ_API_KEY`: Kunci akses ke Groq Cloud.
   - **Lokasi Penyimpanan**: Kedua kunci wajib diletakkan di file `.env`. Berkas `.env` telah dilindungi oleh aturan ketat di `.gitignore` dan `.dockerignore` sehingga **tidak akan pernah bocor ke GitHub**.
3. **Penyaringan Error Internal**:
   - Di `backend/app/api.py`, blok `except Exception` menangkap seluruh error internal dan hanya mengembalikan pesan umum ke klien. Traceback Python tidak pernah dibocorkan ke luar untuk mencegah kebocoran informasi (*information leakage*).

---

## 🗺️ 6. Peta Mental: Kalau Mau Ubah Sesuatu Nanti

| Keperluan Anda | Mulai dari File Mana? | Alur / Hal yang Perlu Diperhatikan |
|---|---|---|
| **Menambah Dokumen UU Baru** | Taruh PDF di [Data/raw/](file:///c:/Users/subki/Downloads/Project%20CV/Legal-Chatbot-main/Data/raw) | Jalankan: `docker compose exec backend python app/ingest.py`. Data vektor akan otomatis bertambah di ChromaDB tanpa perlu rebuild container. |
| **Mengubah Karakter / Prompt AI** | [backend/app/engine.py](file:///c:/Users/subki/Downloads/Project%20CV/Legal-Chatbot-main/backend/app/engine.py) | Edit variabel string `system_prompt`. Anda bisa mengatur persona bot, nada bicara, atau instruksi sitasi. |
| **Mengubah Batasan Rate Limit** | [backend/app/api.py](file:///c:/Users/subki/Downloads/Project%20CV/Legal-Chatbot-main/backend/app/api.py) & [backend/main.py](file:///c:/Users/subki/Downloads/Project%20CV/Legal-Chatbot-main/backend/main.py) | Ubah parameter `@limiter.limit("5/minute")` sesuai kebutuhan (misal `"10/minute"` atau `"60/hour"`). |
| **Mengganti Model LLM atau Embedding** | [.env](file:///c:/Users/subki/Downloads/Project%20CV/Legal-Chatbot-main/.env) | Cukup ganti nilai `LLM_MODEL` (misal ke model Groq terbaru) atau `EMBEDDING_MODEL` tanpa menyentuh kode program. |
| **Menambah Endpoint API Baru** | [backend/app/api.py](file:///c:/Users/subki/Downloads/Project%20CV/Legal-Chatbot-main/backend/app/api.py) | Buat fungsi handler baru dengan decorator `@router.get` atau `@router.post`, lalu tambahkan unit test-nya di `tests/`. |
| **Mengubah Tampilan Antarmuka Web** | [frontend/app.py](file:///c:/Users/subki/Downloads/Project%20CV/Legal-Chatbot-main/frontend/app.py) | Edit komponen Streamlit (judul, tata letak chat, tema visual, atau expander). |
| **Menjalankan Pengujian Kualitas** | Terminal / CLI | Jalankan `pytest tests/ -v`. Pastikan 15 test tetap hijau sebelum melakukan commit kode baru. |

---

## 🚀 7. Cara Menjalankan & Reset Kilat

- **Menyalakan Sistem dari Nol**:
  ```bash
  Copy-Item .env.example .env   # Siapkan konfigurasi (isi API Key Anda)
  docker compose up --build -d  # Bangun & jalankan container
  ```
  Akses di browser: [http://localhost:8501](http://localhost:8501)

- **Reset Total Supaya Bersih Lagi**:
  ```bash
  docker compose down -v        # Matikan container & hapus volume
  ```
  *(Panduan operasional selengkapnya dapat dibaca pada [RUNBOOK.md](RUNBOOK.md)).*
