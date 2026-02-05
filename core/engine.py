import torch
import torchaudio
from faster_whisper import WhisperModel
from pyannote.audio import Pipeline

class OmniEngine:
    """
    Core engine using In-memory processing to bypass torchcodec/FFmpeg DLL issues.
    """
    def __init__(self, hf_token, device="cuda"):
        self.device_type = "cuda" if torch.cuda.is_available() and device == "cuda" else "cpu"

        # 1. Load Faster-Whisper
        compute_type = "float16" if self.device_type == "cuda" else "int8"
        self.asr_model = WhisperModel("large-v3", device=self.device_type, compute_type=compute_type)

        # 2. Load Pyannote Diarization (Using the new 'token' parameter)
        self.diarization_pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            token=hf_token
        ).to(torch.device(self.device_type))

    def transcribe_and_diarize(self, audio_path, initial_prompt=""):
        # --- THE IN-MEMORY MAGIC START ---

        # A. Load the audio file into memory as a Tensor
        # torchaudio.load returns (waveform, sample_rate)
        waveform, sample_rate = torchaudio.load(audio_path)

        # B. Ensure Mono (Pyannote requires a single channel)
        # If stereo (2 channels), we average them to mono
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)

        # C. Construct the dictionary that pyannote expects
        audio_in_memory = {
            "waveform": waveform,
            "sample_rate": sample_rate
        }

        # --- THE IN-MEMORY MAGIC END ---

        # 3. Perform Speaker Diarization using the memory buffer
        # This bypasses the code in pyannote that triggers torchcodec error
        diarization_result = self.diarization_pipeline(audio_in_memory)
        
        # Pyannote 3.1 compatibility: Handle DiarizeOutput object
        if hasattr(diarization_result, 'speaker_diarization'):
             diarization = diarization_result.speaker_diarization
        else:
             diarization = diarization_result

        # 4. Perform Transcription with Faster-Whisper
        # Faster-Whisper is usually fine with file paths on Windows
        segments, _ = self.asr_model.transcribe(
            audio_path,
            beam_size=5,
            initial_prompt=initial_prompt,
            vad_filter=True
        )

        # 5. Align segments with speakers (Same logic as before)
        final_results = []
        for seg in segments:
            speaker_id = "Unknown"
            max_overlap = 0
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                overlap = max(0, min(seg.end, turn.end) - max(seg.start, turn.start))
                if overlap > max_overlap:
                    max_overlap = overlap
                    speaker_id = speaker

            final_results.append({
                "start": seg.start,
                "speaker": speaker_id,
                "text": seg.text.strip()
            })

        return final_results