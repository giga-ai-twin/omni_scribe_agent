import streamlit as st
import datetime
import os
import yaml # Needed for glossary editing
import warnings

# Suppress annoying but harmless warnings on Windows
warnings.filterwarnings("ignore", message=".*torchcodec is not installed correctly.*")
warnings.filterwarnings("ignore", message=".*Torchaudio's I/O functions now support.*")
warnings.filterwarnings("ignore", message=".*In 2.9, this function's implementation will be changed.*")

from dotenv import load_dotenv
from core.engine import OmniEngine
from core.processor import TextProcessor

load_dotenv()
# Load API Keys
DEFAULT_HF_TOKEN = os.getenv("HF_TOKEN")
DEFAULT_GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GLOSSARY_PATH = "config/glossary.yaml"

st.set_page_config(page_title="Agentic Omni Scriber", layout="wide")

# --- Helper Functions ---
def load_glossary():
    with open(GLOSSARY_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def save_glossary(data):
    with open(GLOSSARY_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True)

# --- Initialize Logic ---
@st.cache_resource
def init_system(hf_token):
    return OmniEngine(hf_token), TextProcessor()

# --- Sidebar Configuration ---
# --- Glossary Editor ---
st.sidebar.subheader("📖 Industry Jargon (Glossary)")
glossary_data = load_glossary()
domain_list = list(glossary_data.keys())

domain_choice = st.sidebar.selectbox("Industry Domain", domain_list)

with st.sidebar.expander("✏️ Edit Jargon/Black Talk"):
    # Convert dict to list of dicts for data_editor
    current_terms = glossary_data.get(domain_choice, {})
    # Prepare data for editor: [{'Term': k, 'Definition': v}, ...]
    editable_data = [{"Term": k, "Definition": v} for k, v in current_terms.items()]
    
    edited_df = st.data_editor(editable_data, num_rows="dynamic")

    if st.button("Save Glossary Changes"):
        # Convert back to dict
        new_terms = {row["Term"]: row["Definition"] for row in edited_df if row["Term"]}
        glossary_data[domain_choice] = new_terms
        save_glossary(glossary_data)
        st.success("Glossary saved! Reloading...")
        # Force reload text processor to pick up changes
        st.cache_resource.clear()
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.title("🛠️ System Config")
hf_token = st.sidebar.text_input(
    "Hugging Face Token",
    value=DEFAULT_HF_TOKEN if DEFAULT_HF_TOKEN else "",
    type="password",
    help="Required for Pyannote Speaker Diarization"
)
st.sidebar.markdown("---")
st.sidebar.subheader("🤖 LLM Post-Processing (Gemini)")

# Hardcoded to Gemini as requested
llm_provider = "Google Gemini"
llm_api_key = st.sidebar.text_input(
    "Google Gemini API Key", 
    value=DEFAULT_GEMINI_KEY if DEFAULT_GEMINI_KEY else "",
    type="password", 
    help="Get key from: aistudio.google.com"
)
model_choice = st.sidebar.selectbox("Model", ["gemini-3-flash-preview", "gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-1.5-pro"], index=0)

enable_correction = st.sidebar.checkbox("Enable Grammar/Code-switching Correction", value=True)
enable_summary = st.sidebar.checkbox("Generate Meeting Summary", value=True)

# Domain selection moved to Glossary Editor section
# domain_choice = st.sidebar.selectbox("Industry Domain", ["semiconductor", "general_tech"])

if hf_token:
    engine, processor = init_system(hf_token)

    st.title("🤖 Agentic Omni Scriber")
    st.markdown("### Hybrid Multi-lingual Meeting Transcription System")

    tab_upload, tab_record = st.tabs(["📂 Upload Audio", "🎙️ Record Audio"])

    audio_source = None
    
    with tab_upload:
        uploaded_file = st.file_uploader("Upload Meeting Audio", type=["wav", "mp3"])
        if uploaded_file:
            audio_source = uploaded_file

    with tab_record:
        recorded_audio = st.audio_input("Record Meeting")
        st.caption('Try saying: "Today\'s meeting 咱欲來討論這咧 (lán beh lâi thó-lūn tsit-ê) 蛋糕盒的spec跟size"')
        if recorded_audio:
            audio_source = recorded_audio

    if audio_source:
        audio_path = "temp_audio.wav"
        with open(audio_path, "wb") as f:
            f.write(audio_source.getbuffer())

        st.audio(audio_source)

        if st.button("Start Agentic Processing"):
            with st.spinner("Analyzing audio with OmniEngine..."):
                try:
                    # 1. Processing with Hot-word Boosting (Initial Prompt)
                    raw_results = engine.transcribe_and_diarize(
                        audio_path,
                        initial_prompt="This is a tech meeting in Taiwan with Mandarin, English, and Taiwanese."
                    )
                except Exception as e:
                    st.error(f"Error during transcription: {e}")
                    st.stop()

                # 2. Refinement & LLM Layer
                st.subheader("📝 Professional Transcript")
                
                full_transcript = []

                for item in raw_results:
                    # A. Glossary Replacement
                    text_step1 = processor.apply_glossary(item['text'], domain=domain_choice)
                    
                    # B. LLM Correction (Code-switching/Taiwanese)
                    if enable_correction and llm_api_key:
                        refined_text = processor.correct_transcription(
                            text_step1, 
                            llm_provider="gemini", # Force Gemini
                            llm_api_key=llm_api_key, 
                            model=model_choice
                        )
                    else:
                        refined_text = text_step1

                    full_transcript.append(f"{item['speaker']}: {refined_text}")

                    # UI Presentation
                    with st.container():
                        col1, col2 = st.columns([1, 6])
                        time_str = str(datetime.timedelta(seconds=int(item['start'])))
                        col1.markdown(f"**{time_str}**")
                        col1.caption(f"👤 {item['speaker']}")
                        col2.write(refined_text)
                
                # 3. Summary Generation
                if enable_summary and llm_api_key:
                    st.markdown("---")
                    st.subheader("📋 Meeting Summary")
                    with st.spinner("Generating summary..."):
                        summary = processor.summarize_agent(
                            "\n".join(full_transcript), 
                            llm_provider="gemini", # Force Gemini
                            llm_api_key=llm_api_key,
                            model=model_choice
                        )
                        st.info(summary)
                elif enable_summary and not llm_api_key:
                    st.warning("Skipping summary: No LLM API Key provided.")

else:
    st.warning("Please enter your Hugging Face Token in the sidebar to initialize the engine.")