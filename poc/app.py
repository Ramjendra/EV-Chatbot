"""
SHARP EV AI Chatbot — Streamlit POC
Multi-modal: Text + Voice + Image inputs

Run: streamlit run app.py
"""
import streamlit as st
from kendra_rag    import rag_stream, query_kendra
from voice_handler import transcribe_audio, synthesize_speech, POLLY_VOICES
from image_handler import analyze_image
from config        import APP_TITLE, APP_SUBTITLE, MODULES, KENDRA_INDEX_ID

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .stApp { background-color: #F4F7FB; }

  /* Header */
  .sharp-header {
    background: linear-gradient(135deg, #1F497D 0%, #2E74B5 100%);
    padding: 16px 24px; border-radius: 12px; margin-bottom: 14px;
    display: flex; align-items: center; gap: 16px;
  }
  .sharp-title  { color: white; font-size: 1.5rem; font-weight: 700; margin: 0; }
  .sharp-sub    { color: #B8D4F0; font-size: 0.82rem; margin: 0; }
  .sharp-brand  { color: #FF3333; font-size: 1.9rem; font-weight: 900; letter-spacing: 2px; }

  /* Chat bubbles */
  .user-msg {
    background: #1F497D; color: white;
    padding: 11px 16px; border-radius: 18px 18px 4px 18px;
    margin: 6px 0; max-width: 75%; float: right; clear: both;
    font-size: 0.93rem;
  }
  .bot-msg {
    background: white; color: #1A1A2E;
    padding: 11px 16px; border-radius: 18px 18px 18px 4px;
    margin: 6px 0; max-width: 82%; float: left; clear: both;
    border: 1px solid #DDE6F0; box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    font-size: 0.93rem;
  }
  .clearfix { clear: both; margin-bottom: 4px; }

  /* Input mode tabs */
  .mode-badge {
    display: inline-block; padding: 4px 12px; border-radius: 20px;
    font-size: 0.8rem; font-weight: 600; margin-right: 6px;
  }
  .mode-text  { background: #E3F2FD; color: #1565C0; }
  .mode-voice { background: #EDE7F6; color: #6A1B9A; }
  .mode-image { background: #E8F5E9; color: #2E7D32; }

  /* Source badges */
  .src-high   { background: #E8F5E9; color: #2E7D32; padding: 2px 8px; border-radius: 10px; font-size: 0.75rem; }
  .src-medium { background: #FFF9C4; color: #F57F17; padding: 2px 8px; border-radius: 10px; font-size: 0.75rem; }
  .src-low    { background: #FFEBEE; color: #C62828; padding: 2px 8px; border-radius: 10px; font-size: 0.75rem; }

  /* Detection result box */
  .detect-box {
    background: #F3E5F5; border: 1px solid #CE93D8;
    border-radius: 8px; padding: 8px 12px; margin: 6px 0;
    font-size: 0.82rem; color: #4A148C;
  }

  /* Warning box */
  .warn-box {
    background: #FFF9C4; border: 1px solid #F9A825;
    border-radius: 8px; padding: 10px 14px; color: #5D4037;
    font-size: 0.84rem; margin: 8px 0;
  }

  .stButton > button {
    border-radius: 20px !important;
    font-weight: 600 !important;
  }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
defaults = {
    "messages":        [],
    "selected_module": "EV Usage Consultation",
    "last_sources":    [],
    "last_audio":      None,   # MP3 bytes of last TTS response
    "input_mode":      "Text", # Text | Voice | Image
    "voice_option":    "English (Female)",
    "tts_enabled":     True,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚡ SHARP EV Chatbot")
    st.markdown("---")

    # Module selector
    st.markdown("**Module**")
    for mod_name, mod_cfg in MODULES.items():
        is_active = st.session_state.selected_module == mod_name
        if st.button(
            f"{mod_cfg['icon']}  {mod_name}",
            key=f"mod_{mod_name}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.selected_module = mod_name
            st.session_state.messages    = []
            st.session_state.last_sources = []
            st.session_state.last_audio   = None
            st.rerun()

    st.markdown("---")

    # Voice settings
    st.markdown("**Voice Settings**")
    st.session_state.voice_option = st.selectbox(
        "Polly Voice",
        options=list(POLLY_VOICES.keys()),
        index=0,
        label_visibility="collapsed",
    )
    st.session_state.tts_enabled = st.toggle(
        "🔊 Speak responses (TTS)", value=st.session_state.tts_enabled
    )

    st.markdown("---")

    # Status
    st.markdown("**Kendra Status**")
    if KENDRA_INDEX_ID:
        st.success(f"✓ Index configured")
        st.caption(f"`{KENDRA_INDEX_ID[:18]}…`")
    else:
        st.error("✗ No index\nRun `setup_kendra.py`")

    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages    = []
        st.session_state.last_sources = []
        st.session_state.last_audio   = None
        st.rerun()

    st.markdown("---")
    st.caption("POC · Kendra + Bedrock Claude 3\nAp-northeast-1 (Tokyo)")


# ── Header ────────────────────────────────────────────────────────────────────
mod_active = MODULES[st.session_state.selected_module]
st.markdown(f"""
<div class="sharp-header">
  <span class="sharp-brand">SHARP</span>
  <div>
    <p class="sharp-title">⚡ {APP_TITLE}</p>
    <p class="sharp-sub">
      {APP_SUBTITLE} &nbsp;|&nbsp;
      {mod_active['icon']} {st.session_state.selected_module}
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

if not KENDRA_INDEX_ID:
    st.markdown("""
    <div class="warn-box">
    ⚠️ <b>Setup required:</b> Run <code>python setup_kendra.py</code>
    then <code>python ingest.py --docs ./docs/</code>
    </div>""", unsafe_allow_html=True)


# ── Main layout ───────────────────────────────────────────────────────────────
chat_col, src_col = st.columns([2, 1])


# ── Sources panel ─────────────────────────────────────────────────────────────
with src_col:
    st.markdown("### 📄 Kendra Sources")
    if st.session_state.last_sources:
        for i, src in enumerate(st.session_state.last_sources, 1):
            score     = src.get("score", "LOW")
            score_cls = (
                "src-high"   if score in ("VERY_HIGH", "HIGH")
                else "src-medium" if score == "MEDIUM"
                else "src-low"
            )
            with st.expander(f"Source {i} · {src['title'][:38]}"):
                st.markdown(
                    f'<span class="{score_cls}">Confidence: {score}</span>',
                    unsafe_allow_html=True,
                )
                st.markdown(f"_{src.get('excerpt', '')[:280]}…_")
                if src.get("source_uri"):
                    st.caption(f"📎 {src['source_uri']}")
    else:
        st.caption("Sources from Kendra appear here after each query.")

    # TTS audio player
    if st.session_state.last_audio:
        st.markdown("---")
        st.markdown("**🔊 Voice Response**")
        st.audio(st.session_state.last_audio, format="audio/mp3")


# ── Chat panel ────────────────────────────────────────────────────────────────
with chat_col:

    # ── Render chat history ───────────────────────────────────────────────────
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            icon = "🎤" if msg.get("mode") == "voice" else "📷" if msg.get("mode") == "image" else "🧑"
            st.markdown(
                f'<div class="user-msg">{icon} {msg["content"]}</div>'
                '<div class="clearfix"></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="bot-msg">🤖 {msg["content"]}</div>'
                '<div class="clearfix"></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Input mode selector ───────────────────────────────────────────────────
    input_mode = st.radio(
        "Input mode",
        ["📝 Text", "🎤 Voice", "📷 Image"],
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state.input_mode = input_mode.split(" ")[1]  # Text | Voice | Image

    st.markdown("---")
    query_to_send = None
    detected_info = None

    # ── TEXT input ────────────────────────────────────────────────────────────
    if st.session_state.input_mode == "Text":
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            text_query = st.text_input(
                "Ask a question",
                placeholder="e.g. What is the maximum range on a full charge?",
                key="text_input",
                label_visibility="collapsed",
            )
        with col_btn:
            send_text = st.button("Send ➤", use_container_width=True, key="send_text")

        if send_text and text_query.strip():
            query_to_send = text_query.strip()

        # Quick example prompts
        st.markdown("**Quick questions:**")
        examples = {
            "EV Usage Consultation": [
                "What is the maximum range on full charge?",
                "How long does a full charge take?",
                "How do I activate regenerative braking?",
                "What does the yellow battery light mean?",
            ],
            "Self-Diagnosis": [
                "Battery warning light is on. What does it mean?",
                "Error code P0A80 — what should I do?",
                "Range dropped suddenly — is that normal?",
                "Unusual noise from the motor. Is it critical?",
            ],
            "General Chat": [
                "What are the benefits of EVs over petrol cars?",
                "How does regenerative braking work?",
                "Tips for maximising EV battery life?",
                "What is the ideal temperature for EV batteries?",
            ],
            "Automotive Guidance": [
                "Best practices for highway driving in an EV?",
                "How often should I service an electric vehicle?",
                "Is it safe to charge in rain?",
                "What is the correct tyre pressure for an EV?",
            ],
        }
        ex_list = examples.get(st.session_state.selected_module, [])
        ex_cols = st.columns(2)
        for i, ex in enumerate(ex_list):
            if ex_cols[i % 2].button(f"💬 {ex}", key=f"ex_{i}", use_container_width=True):
                query_to_send = ex

    # ── VOICE input ───────────────────────────────────────────────────────────
    elif st.session_state.input_mode == "Voice":
        st.markdown(
            '<span class="mode-badge mode-voice">🎤 Voice Input</span>'
            " Record your question — it will be transcribed automatically.",
            unsafe_allow_html=True,
        )
        st.caption(f"Voice: {st.session_state.voice_option} | TTS: {'On' if st.session_state.tts_enabled else 'Off'}")

        audio_input = st.audio_input(
            "Click to record your question",
            key="audio_recorder",
        )

        if audio_input is not None:
            audio_bytes = audio_input.read()
            if st.button("🎤 Transcribe & Send", type="primary", key="send_voice"):
                with st.spinner("Transcribing audio with Amazon Transcribe…"):
                    try:
                        transcript = transcribe_audio(
                            audio_bytes,
                            audio_format="wav",
                            language=st.session_state.voice_option,
                        )
                        if transcript:
                            st.success(f"Transcribed: **{transcript}**")
                            query_to_send = transcript
                            detected_info = f"🎤 Transcribed: \"{transcript}\""
                    except Exception as e:
                        st.error(f"Transcription error: {e}")

        # Fallback: type if mic not available
        st.markdown("---")
        st.caption("No microphone? Type instead:")
        fallback = st.text_input("Type your question", key="voice_fallback", label_visibility="collapsed")
        if st.button("Send typed", key="send_voice_typed") and fallback.strip():
            query_to_send = fallback.strip()

    # ── IMAGE input ───────────────────────────────────────────────────────────
    elif st.session_state.input_mode == "Image":
        st.markdown(
            '<span class="mode-badge mode-image">📷 Image Input</span>'
            " Take a photo or upload an image of the warning light / dashboard.",
            unsafe_allow_html=True,
        )

        img_tab1, img_tab2 = st.tabs(["📷 Camera", "📁 Upload"])

        image_bytes = None

        with img_tab1:
            camera_img = st.camera_input("Take a photo of the dashboard / warning light")
            if camera_img:
                image_bytes = camera_img.read()

        with img_tab2:
            uploaded_img = st.file_uploader(
                "Upload dashboard photo",
                type=["jpg", "jpeg", "png", "webp"],
                key="img_upload",
            )
            if uploaded_img:
                image_bytes = uploaded_img.read()
                st.image(uploaded_img, caption="Uploaded image", width=300)

        if image_bytes:
            if st.button("🔍 Analyse Image & Ask", type="primary", key="send_image"):
                with st.spinner("Analysing image with Amazon Rekognition…"):
                    try:
                        result = analyze_image(image_bytes)
                        query_to_send = result["query"]
                        detected_info = f"📷 Detected: {result['summary']}"
                        st.markdown(
                            f'<div class="detect-box">🔍 {result["summary"]}</div>',
                            unsafe_allow_html=True,
                        )
                        # Show labels in expander
                        with st.expander("Rekognition details"):
                            col_l, col_t = st.columns(2)
                            with col_l:
                                st.markdown("**Labels**")
                                for l in result["labels"][:8]:
                                    tag = "★" if l["relevant"] else "·"
                                    st.caption(f"{tag} {l['name']} ({l['confidence']}%)")
                            with col_t:
                                st.markdown("**Detected Text**")
                                if result["texts"]:
                                    for t in result["texts"][:6]:
                                        st.caption(f"`{t['text']}` ({t['confidence']}%)")
                                else:
                                    st.caption("No text detected")
                    except Exception as e:
                        st.error(f"Image analysis error: {e}")


# ── Process query → Kendra → Bedrock ─────────────────────────────────────────
if query_to_send:
    system_prompt = MODULES[st.session_state.selected_module]["system_prompt"]
    mode_label    = st.session_state.input_mode.lower()

    # Append user message to history
    user_msg = {"role": "user", "content": query_to_send, "mode": mode_label}
    if detected_info:
        user_msg["content"] = f"{detected_info}\n\n{query_to_send}"
    st.session_state.messages.append(user_msg)

    if not KENDRA_INDEX_ID:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "⚠️ Kendra not configured. Run `python setup_kendra.py` first.",
        })
        st.rerun()

    # Stream Bedrock response
    with st.spinner("Searching knowledge base…"):
        try:
            stream, sources = rag_stream(query_to_send, system_prompt)
            st.session_state.last_sources = sources

            full_response = ""
            placeholder   = st.empty()

            for chunk in stream:
                full_response += chunk
                placeholder.markdown(
                    f'<div class="bot-msg">🤖 {full_response}▌</div>'
                    '<div class="clearfix"></div>',
                    unsafe_allow_html=True,
                )
            placeholder.empty()

            st.session_state.messages.append({
                "role": "assistant", "content": full_response,
            })

            # TTS: synthesize response if enabled
            if st.session_state.tts_enabled and full_response:
                with st.spinner("Generating voice response with Amazon Polly…"):
                    try:
                        audio_bytes = synthesize_speech(
                            full_response,
                            st.session_state.voice_option,
                        )
                        st.session_state.last_audio = audio_bytes
                    except Exception as e:
                        st.warning(f"TTS error (answer still shown above): {e}")

        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"❌ Error: {str(e)}",
            })

    st.rerun()
