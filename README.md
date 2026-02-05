# 🤖 Agentic Omni Scriber

![Banner](assets/banner.png)

**Hybrid Multi-lingual Meeting Transcription System**  
*Specialized for Mandarin, English, and Taiwanese Hokkien code-switching environments.*

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![Streamlit](https://img.shields.io/badge/streamlit-1.40%2B-ff4b4b)

## 🌟 Overview

Agentic Omni Scriber is an advanced meeting assistant designed to tackle the challenges of multi-lingual tech meetings in Taiwan. It combines state-of-the-art local AI models with powerful cloud-based LLMs to deliver accurate, speaker-diarized transcripts and summaries.

## ✨ Key Features

-   **🎙️ Flexible Input**: Support for **File Upload** (`.wav`, `.mp3`) and **Live Recording** via browser.
-   **🗣️ Speaker Diarization**: Identifies "Who said what" using `pyannote.audio`.
-   **📝 Code-Switching Expert**: Uses **Google Gemini** (or OpenAI) to correct mixed-language grammar (e.g., "Today's meeting 咱欲來討論這咧 (lán beh lâi thó-lūn tsit-ê) 蛋糕盒的spec跟size").
-   **📖 Glossary Editor**: Built-in sidebar editor to manage industry jargon (e.g., `蛋糕盒` -> `Wafer Cassette`).
-   **⚡ Agentic Processing**:
    -   **Fast Transcription**: Powered by `faster-whisper`.
    -   **Auto-Correction**: Fixes phonetic errors in Taiwanese Hokkien.
    -   **Summarization**: Generates concise meeting minutes.

## 🛠️ Installation

### Prerequisites
1.  **Python 3.10+** installed.
2.  **FFmpeg** installed and added to system PATH.

### Steps
1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/omni_scribe_agent.git
    cd omni_scribe_agent
    ```

2.  Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Mac/Linux
    source .venv/bin/activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: On Windows, you might see `torchcodec` warnings, which this app handles gracefully.*

## ⚙️ Configuration

1.  Create a `.env` file in the root directory:
    ```env
    # Required for Speaker Diarization
    HF_TOKEN=your_huggingface_token

    # Required for AI Correction & Summarization
    GEMINI_API_KEY=your_google_gemini_api_key
    ```
    -   **HF_TOKEN**: Get from [Hugging Face Settings](https://huggingface.co/settings/tokens). You must accept user conditions for `pyannote/speaker-diarization-3.1`.
    -   **GEMINI_API_KEY**: Get from [Google AI Studio](https://aistudio.google.com/).

## 🚀 Usage

Run the Streamlit application:
```bash
streamlit run app.py
```

### Sidebar Controls
1.  **Glossary Editor**: Add your company's "Black Talk" (Jargon) here.
2.  **System Config**: Verify your HF Token.
3.  **LLM Post-Processing**: Select the latest Gemini model (e.g., `gemini-2.0-flash-exp`).

## 🏗️ Tech Stack

-   **Frontend**: Streamlit
-   **ASR (Transcription)**: Faster-Whisper (OpenAI Whisper)
-   **Diarization**: Pyannote.audio
-   **LLM Engine**: Google Gemini API (via `google.generativeai`)

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

[MIT](LICENSE)
