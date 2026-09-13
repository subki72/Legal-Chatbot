import os
from typing import Any, Optional
import requests
import streamlit as st
from dotenv import load_dotenv

# Load local environment configuration
load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="Indonesian Legal RAG Assistant",
    page_icon="none",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Enterprise CSS Styling
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Header Container */
    .app-header {
        padding: 1.5rem 0 1rem 0;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid rgba(128, 128, 128, 0.2);
    }

    .app-title {
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 0.25rem;
    }

    .app-subtitle {
        font-size: 0.95rem;
        color: #6B7280;
        margin-bottom: 1rem;
        line-height: 1.5;
    }

    /* Badges Row */
    .badge-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }

    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        border: 1px solid transparent;
    }

    .badge-online {
        background-color: rgba(16, 185, 129, 0.15);
        color: #059669;
        border-color: rgba(16, 185, 129, 0.3);
    }

    .badge-degraded {
        background-color: rgba(245, 158, 11, 0.15);
        color: #D97706;
        border-color: rgba(245, 158, 11, 0.3);
    }

    .badge-offline {
        background-color: rgba(239, 68, 68, 0.15);
        color: #DC2626;
        border-color: rgba(239, 68, 68, 0.3);
    }

    .badge-neutral {
        background-color: rgba(107, 114, 128, 0.15);
        color: #4B5563;
        border-color: rgba(107, 114, 128, 0.25);
    }

    /* Card Panels */
    .telemetry-card {
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        background: rgba(128, 128, 128, 0.04);
        margin-bottom: 1rem;
    }

    .telemetry-title {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #6B7280;
        margin-bottom: 0.5rem;
    }

    /* Citation Box */
    .citation-tag {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-radius: 4px;
        color: #2563EB;
        font-size: 0.8rem;
        font-family: 'JetBrains Mono', monospace;
        margin: 0.2rem 0.3rem 0.2rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Backend Environment Resolution
backend_url: str = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
app_api_key: Optional[str] = os.getenv("APP_API_KEY")

# Fetch System Telemetry
backend_status: str = "offline"
provider_label: str = "N/A"
model_label: str = "N/A"

try:
    health_resp = requests.get(f"{backend_url}/health", timeout=3)
    if health_resp.status_code == 200:
        h_data = health_resp.json()
        backend_status = h_data.get("status", "healthy")
        provider_label = h_data.get("provider", "N/A").upper()
        model_label = h_data.get("model", "N/A")
    else:
        backend_status = "degraded"
except Exception:
    backend_status = "offline"

# Header Section
st.markdown(
    """
    <div class="app-header">
        <div class="app-title">Indonesian Legal RAG Intelligence</div>
        <div class="app-subtitle">
            Autonomous statutory consultation and compliance verification engine powered by 
            Law No. 22 of 2009 (Traffic and Road Transportation).
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar Navigation & Telemetry
with st.sidebar:
    st.markdown("### System Telemetry")

    if backend_status == "healthy":
        st.markdown(
            '<div class="status-badge badge-online">STATUS: OPERATIONAL</div>',
            unsafe_allow_html=True,
        )
    elif backend_status == "degraded":
        st.markdown(
            '<div class="status-badge badge-degraded">STATUS: DEGRADED</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="status-badge badge-offline">STATUS: UNREACHABLE</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div class="telemetry-card" style="margin-top: 1rem;">
            <div class="telemetry-title">Active LLM Provider</div>
            <div style="font-weight: 600; font-size: 1rem;">{provider_label}</div>
            <div class="telemetry-title" style="margin-top: 0.75rem;">Model Identifier</div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;">{model_label}</div>
            <div class="telemetry-title" style="margin-top: 0.75rem;">Vector Store</div>
            <div style="font-size: 0.85rem;">ChromaDB (203 pages indexed)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("### Architecture Guidance")
    st.markdown(
        """
        - **Provider Flexibility**: Toggle between local **Ollama** and cloud **Groq** via `.env` (`LLM_PROVIDER=ollama`).
        - **Statutory Precision**: Retrieval responses cite exact statutory Articles and page labels.
        - **Anti-Hallucination**: Out-of-scope inquiries are politely refused per regulatory compliance.
        """
    )

    st.markdown("---")
    if st.button("Clear Conversation History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Initialize Session Chat Memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render Conversation Timeline
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "extras" in message:
            extras: dict[str, Any] = message["extras"]
            with st.expander("Inspection & Source Verification"):
                sources: list[str] = extras.get("sources", [])
                if sources:
                    st.markdown("**Statutory Document Citations:**")
                    citation_html = "".join(
                        f'<span class="citation-tag">{source}</span>' for source in sources
                    )
                    st.markdown(citation_html, unsafe_allow_html=True)
                else:
                    st.caption("No specific statutory document nodes exceeded the similarity threshold.")

                col1, col2, col3 = st.columns(3)
                col1.metric("Execution Latency", extras.get("latency", "N/A"))
                col2.metric("Estimated Tokens", f"~{extras.get('tokens', 'N/A')}")
                col3.metric("Serving Provider", extras.get("provider", "N/A").upper())

# Handle Query Input
if prompt := st.chat_input("Ask a legal question regarding sanctions, licensing, speed limits, or statutory articles..."):
    # Append user prompt to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process Query via Backend RAG Service
    with st.chat_message("assistant"):
        with st.spinner("Analyzing statutory legal documents..."):
            try:
                if not app_api_key:
                    st.error(
                        "Authentication configuration 'APP_API_KEY' is missing in the environment. "
                        "Please configure APP_API_KEY in your .env file."
                    )
                    st.stop()

                payload = {"query": prompt}
                headers = {
                    "X-API-Key": app_api_key,
                    "Content-Type": "application/json",
                }

                response = requests.post(
                    f"{backend_url}/chat",
                    json=payload,
                    headers=headers,
                    timeout=300,  # 300s window accommodates local CPU-bound Ollama inference
                )

                if response.status_code == 200:
                    data = response.json()
                    answer: str = data.get("response", "")
                    sources: list[str] = data.get("sources", [])
                    latency: str = data.get("latency", "N/A")
                    tokens: int = data.get("tokens", 0)
                    resp_provider: str = data.get("provider", "")
                    resp_model: str = data.get("model", "")

                    st.markdown(answer)

                    with st.expander("Inspection & Source Verification"):
                        if sources:
                            st.markdown("**Statutory Document Citations:**")
                            citation_html = "".join(
                                f'<span class="citation-tag">{source}</span>' for source in sources
                            )
                            st.markdown(citation_html, unsafe_allow_html=True)
                        else:
                            st.caption(
                                "No specific statutory document nodes exceeded the similarity threshold."
                            )

                        col1, col2, col3 = st.columns(3)
                        col1.metric("Execution Latency", latency)
                        col2.metric("Estimated Tokens", f"~{tokens}")
                        col3.metric("Serving Provider", resp_provider.upper())

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "extras": {
                                "sources": sources,
                                "latency": latency,
                                "tokens": tokens,
                                "provider": resp_provider,
                                "model": resp_model,
                            },
                        }
                    )

                elif response.status_code == 429:
                    error_detail = response.json().get(
                        "detail", "AI service request rate limit reached."
                    )
                    st.warning(f"Rate Limit Exceeded: {error_detail}")
                elif response.status_code == 503:
                    error_detail = response.json().get(
                        "detail", "Backend AI service is not ready or initializing."
                    )
                    st.error(f"Service Unavailable: {error_detail}")
                elif response.status_code == 403:
                    st.error(
                        "Access Denied: The provided API key is invalid. Please verify APP_API_KEY."
                    )
                elif response.status_code == 422:
                    st.warning(
                        "Invalid Input: Query must not be empty or exceed 500 characters."
                    )
                else:
                    st.error(
                        f"Failed to communicate with backend: HTTP {response.status_code} - {response.text}"
                    )

            except requests.exceptions.Timeout:
                st.error(
                    "Execution Timeout: The inference model exceeded the 300-second execution window. "
                    "When running local Ollama on CPU, consider using a smaller model (e.g., qwen2.5:1.5b) "
                    "or switching to cloud Groq mode in .env for sub-second responses."
                )
            except Exception as e:
                st.error(f"Connection error occurred: {e}")
