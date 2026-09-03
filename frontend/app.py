import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables dari .env jika ada
load_dotenv()
# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="AI Legal Assistant",
    page_icon="⚖️",
    layout="centered"
)

st.title("⚖️ AI Asisten Hukum Indonesia")
st.markdown("---")

# 2. Inisialisasi History Chat (Biar gak lupa ingatan)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Tampilkan Chat Terdahulu
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Kalau ada data tambahan (sumber/metrics), tampilin juga
        if "extras" in message:
            with st.expander("Detail Referensi & Monitoring"):
                st.info(f" Sumber: {', '.join(message['extras']['sources'])}")
                st.caption(f" Waktu Mikir: {message['extras']['latency']} |  Token: {message['extras']['tokens']}")

# 4. Input User
if prompt := st.chat_input("Tanya seputar UU..."):
    # Tampilkan pesan user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 5. Proses ke Backend
    with st.chat_message("assistant"):
        with st.spinner("Sedang menganalisis dokumen hukum..."):
            try:
                backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
                app_api_key = os.getenv("APP_API_KEY")

                if not app_api_key:
                    st.error("❌ Konfigurasi `APP_API_KEY` tidak ditemukan di environment. Silakan set `APP_API_KEY` di file `.env`.")
                    st.stop()

                # Kirim query ke payload body sesuai spec Pydantic baru
                payload = {"query": prompt}
                headers = {
                    "X-API-Key": app_api_key,
                    "Content-Type": "application/json"
                }
                
                response = requests.post(
                    f"{backend_url}/chat",
                    json=payload,
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data['response']
                    sources = data['sources']
                    latency = data.get('latency', 'N/A')
                    tokens = data.get('tokens', 'N/A')
                    
                    st.markdown(answer)
                    
                    with st.expander(" Detail Referensi & Monitoring"):
                        st.info(f"Sumber: {', '.join(sources)}")
                        st.caption(f"Waktu Mikir: {latency} |  Token: {tokens}")
                    
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer,
                        "extras": {"sources": sources, "latency": latency, "tokens": tokens}
                    })
                    
                elif response.status_code == 429:
                    error_detail = response.json().get("detail", "Batas kuota AI atau laju request tercapai.")
                    st.warning(f"⚠️ **Rate Limit**: {error_detail}")
                elif response.status_code == 503:
                    st.error("⚠️ **Layanan Belum Siap**: AI Engine backend sedang offline atau belum siap.")
                elif response.status_code == 403:
                    st.error("🔒 **Akses Ditolak**: API Key tidak valid. Silakan periksa nilai `APP_API_KEY`.")
                elif response.status_code == 422:
                    st.warning("⚠️ **Input Tidak Valid**: Pertanyaan tidak boleh kosong atau melebihi 500 karakter.")
                else:
                    st.error(f"❌ Gagal menghubungi backend: Error {response.status_code} - {response.text}")
                    
            except Exception as e:
                st.error(f"Terjadi kesalahan koneksi: {e}")
