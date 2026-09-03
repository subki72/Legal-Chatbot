# 📚 Indeks Dokumentasi Proyek (Project Documentation)

Selamat datang di direktori dokumentasi terpusat untuk proyek **Legal Chatbot RAG** (Indonesian Law Assistant). Seluruh dokumen teknis, alur kerja sistem, kumpulan prompt AI agent, serta laporan audit kualitas dan keamanan tersimpan di sini secara terstruktur.

---

## 🗂️ Struktur Direktori Dokumentasi

```
docs/
├── README.md                     # File indeks navigasi dokumentasi ini
├── 01-project-documentation/     # Spesifikasi proyek, arsitektur, dan referensi sistem
│   └── RUNBOOK.md                # 🚀 Panduan operasional dari nol & reset total
├── 02-workflows/                 # Alur data detail per-file dan trace end-to-end
│   └── WORKFLOW-PER-FILE-TRACE.md
├── 03-prompts/                   # Koleksi prompt agen AI untuk maintenance & audit
│   ├── pre-coding-setup-prompt-master.md
│   ├── prompt-cleanup-project.md
│   ├── prompt-fix-generic-ui.md
│   ├── prompt-production-readiness-audit.md
│   ├── prompt-qa-security-audit.md
│   ├── prompt-workflow-per-file-detail.md
│   ├── prompt.md
│   └── UNDERSTAND_ME.md
└── 04-audits-logs/               # Laporan audit kesiapan produksi, keamanan, dan log perbaikan
    ├── CLEANUP-REPORT.md
    └── PRODUCTION-READINESS-ASSESSMENT.md
```

---

## 📖 Ringkasan Dokumen Utama

### 1. Workflows & Alur Data
- [WORKFLOW-PER-FILE-TRACE.md](file:///c:/Users/subki/Downloads/Project%20CV/Legal-Chatbot-main/docs/02-workflows/WORKFLOW-PER-FILE-TRACE.md)  
  Dokumentasi mendalam setingkat *function-call* yang memetakan seluruh file dalam proyek, daftar fungsi/kelas publik, pemanggil (*caller*), fungsi yang dipanggil (*callee*), input/output, efek samping, serta 3 rekonstruksi alur *end-to-end* lintas modul.

### 2. Audit & Kesiapan Produksi
- [PRODUCTION-READINESS-ASSESSMENT.md](file:///c:/Users/subki/Downloads/Project%20CV/Legal-Chatbot-main/docs/04-audits-logs/PRODUCTION-READINESS-ASSESSMENT.md)  
  Laporan evaluasi komprehensif 8 dimensi kesiapan produksi (Kualitas Kode, Arsitektur, Pengujian, Keamanan, Observabilitas, Deployment, Operasional, dan Dokumentasi), pemetaan isu jalur kritis (*Phase 0 Blockers*), dan roadmap remedi bertahap.

### 3. Kumpulan Prompt Agen AI (`03-prompts/`)
Koleksi instruksi spesifik untuk memandu agen AI dalam tugas pemeliharaan, audit, dan pengembangan lanjutan:
- `UNDERSTAND_ME.md`: Panduan memahami arsitektur dan mental model proyek.
- `prompt-workflow-per-file-detail.md`: Template audit alur data per file.
- `prompt-production-readiness-audit.md`: Template asesmen kesiapan produksi.
- `prompt-qa-security-audit.md`: Template audit keamanan dan pengujian kualitas.
- `prompt-fix-generic-ui.md`: Panduan peningkatan visual antarmuka web Streamlit.
- `prompt-cleanup-project.md`: Panduan pembersihan dan penataan repositori.
