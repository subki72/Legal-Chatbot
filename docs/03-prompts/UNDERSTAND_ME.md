# 🧠 UNDERSTAND_ME.md
> Prompt pack untuk memahami project yang lo build dengan AI agent.
> Copy-paste prompt di bawah ke AI agent (Claude Code, Cursor, Windsurf, dll) setelah project selesai.

---

## Cara Pakai

1. Taruh file ini di root folder project lo
2. Setelah project selesai di-build, buka sesi baru dengan AI agent
3. Mulai dengan: _"Baca UNDERSTAND_ME.md dan jalankan prompt yang relevan untuk project ini"_
4. Atau jalankan prompt satu per satu sesuai kebutuhan

---

## Prompt 1 — Big Picture: Workflow & Arsitektur

```
Aku baru selesai build project ini tapi belum paham alur besarnya.
Tolong jelaskan:
1. Gambaran besar cara kerja project ini dari ujung ke ujung (user action → response)
2. Komponen/module utama apa saja dan peran masing-masing
3. Bagaimana data mengalir antar komponen tersebut

Gunakan analogi sederhana dulu, baru masuk ke teknis.
Sertakan diagram ASCII kalau membantu.
```

---

## Prompt 2 — Tech Stack: Kenapa Ini, Bukan Itu

```
Jelaskan setiap library/framework/tool yang dipakai di project ini:
- Apa fungsinya dalam konteks project ini (bukan definisi umum)
- Kenapa dipilih dibanding alternatif lainnya
- Kalau aku hapus ini, apa yang akan rusak?

Format per-tool, mulai dari yang paling inti.
```

---

## Prompt 3 — Logika Kode yang Bikin Bingung

```
Tunjukkan bagian kode yang paling kompleks atau "tidak obvious" di project ini.
Untuk setiap bagian:
1. Jelaskan apa yang sedang dilakukan baris per baris
2. Kenapa ditulis seperti ini (bukan cara yang lebih simpel)
3. Apa yang terjadi kalau logika ini salah/dihapus

Mulai dari yang paling krusial untuk jalannya aplikasi.
```

---

## Prompt 4 — DevOps: Pipeline & Infrastructure

```
Aku tidak paham bagian DevOps dari project ini. Tolong jelaskan:
1. Alur dari "aku push code" sampai "user bisa akses perubahan itu" step by step
2. Setiap file config (docker, CI/CD, env, nginx, dll) — apa fungsinya
3. Apa yang terjadi kalau salah satu bagian pipeline ini gagal
4. Environment mana saja yang ada (dev/staging/prod) dan bedanya

Anggap aku belum pernah belajar DevOps sama sekali.
```

---

## Prompt 5 — Security & Data Flow

```
Jelaskan bagaimana project ini menangani:
1. Autentikasi & otorisasi — siapa yang boleh akses apa
2. Data sensitif — disimpan di mana, dienkripsi atau tidak
3. Celah keamanan paling obvious yang mungkin ada sekarang
4. Environment variable apa saja yang krusial dan kenapa tidak boleh bocor
```

---

## Prompt 6 — Mental Map: Kalau Mau Ubah Sesuatu

```
Aku ingin bisa mandiri kalau perlu edit project ini nanti.
Buatkan "peta" untuk:
1. Kalau mau tambah fitur baru → mulai dari file mana, ikuti alur mana
2. Kalau ada bug → cara trace-nya dari error message ke sumber masalah
3. File/folder mana yang paling sering perlu disentuh vs yang jangan diutak-atik
4. Dependencies antar module — mana yang kalau diubah berdampak ke banyak tempat
```

---

## Prompt 7 — Rangkuman Eksekutif (Simpan Sebagai Dokumentasi)

```
Buatkan "README untuk diriku sendiri" tentang project ini yang mencakup:
- Apa yang project ini lakukan dalam 2 kalimat
- Stack lengkap + alasan singkat tiap pilihan
- Alur utama aplikasi (diagram atau bullet)
- File-file penting dan fungsinya
- Hal yang paling mudah salah/rusak dan cara fixnya
- Cara run di lokal dari nol

Tulis seolah aku adalah orang yang build ini tapi baru balik setelah 6 bulan tidak menyentuhnya.
Simpan hasilnya sebagai MY_NOTES.md di root project ini.
```

---

## Tips Penggunaan

- **Jalankan semua sekaligus?** Cukup paste Prompt 7 dulu — hasilnya jadi fondasi, sisanya untuk deep dive.
- **Project ada DevOps-nya?** Prioritaskan Prompt 4 dan 5.
- **Mau ngerti kodenya?** Mulai dari Prompt 1 → 3 → 6 secara berurutan.
- **Mau audit keamanan cepat?** Langsung Prompt 5.
- **Simpan `MY_NOTES.md`** yang dihasilkan Prompt 7 di repo — berguna banget kalau balik ke project ini beberapa bulan kemudian.

---

*File ini dibuat untuk membantu developer yang build dengan AI agent tetap punya pemahaman nyata atas proyeknya sendiri.*


AI For Intelligent Suply Chain/
├── Prompt/                               # Dokumen acuan & prompt master
│   ├── Proposal_Intelligent_Supply_Chain.pdf
│   ├── pre-coding-setup-prompt-master.md
│   └── ...
│
├── docs/                                 # 13 Dokumen Fondasi (4 Fase)
│   ├── fase-1-pemahaman-masalah/
│   │   ├── 01_SRS.md
│   │   ├── 02_GLOSSARY_DOMAIN.md
│   │   └── 03_BUSINESS_RULES.md
│   ├── fase-2-desain-solusi/
│   │   ├── 04_ARSITEKTUR.md
│   │   ├── 05_KONTRAK_DATA.md
│   │   ├── 06_DOKUMENTASI_API.md
│   │   └── 07_ADR.md
│   ├── fase-3-setup-implementasi/
│   │   ├── 08_ROOT_DIREKTORI.md
│   │   ├── 09_TOOLS_DAN_LIBRARY.md
│   │   └── 10_KONVENSI_DAN_STANDAR.md
│   └── fase-4-operasional/
│       ├── 11_ENVIRONMENT_DAN_SETUP.md
│       ├── 12_CARA_JALANIN.md
│       └── 13_TESTING_STRATEGY.md
│
├── backend/                              # Backend FastAPI & ML Pipeline
│   ├── app/
│   │   ├── api/v1/endpoints/             # REST Endpoints (vision, inventory, negotiation, docs, approvals)
│   │   ├── core/                         # Config & Database Session
│   │   ├── models/                       # ORM DB Models (Stock, Vendor, PO)
│   │   ├── schemas/                      # Pydantic Request/Response
│   │   ├── services/                     # Core Intelligence & Agents:
│   │   │   ├── vision_service.py         # OpenCV + YOLOv8 inference & counting
│   │   │   ├── forecasting_service.py    # Scikit-Learn ROP & Safety Stock
│   │   │   ├── compliance_service.py     # SOP Rule Engine
│   │   │   ├── negotiation_agent.py      # Groq Multi-Agent LLM (Llama 3.3)
│   │   │   └── pdf_service.py            # ReportLab PO Generator
│   │   └── main.py                       # Entry point server
│   └── data/
│       ├── images/                       # Sampel gambar rak gudang (Normal, Low, Critical)
│       ├── weights/                      # File bobot model (yolov8n.pt)
│       └── sop/                          # Rule SOP pengadaan (JSON/Markdown)
│
├── frontend/                             # Web Dashboard UI
│   ├── index.html                        # Real-Time Monitoring & Approval UI
│   ├── css/style.css
│   └── js/app.js
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
