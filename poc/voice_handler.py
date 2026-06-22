"""
Voice I/O handler using Amazon Transcribe (STT) + Amazon Polly (TTS).

Flow:
  Audio bytes  →  S3 upload  →  Transcribe job  →  transcript text
  Answer text  →  Polly       →  MP3 audio bytes
"""
import boto3, json, time, uuid, urllib.request
from config import AWS_REGION, S3_BUCKET_NAME

transcribe = boto3.client("transcribe", region_name=AWS_REGION)
polly      = boto3.client("polly",      region_name=AWS_REGION)
s3         = boto3.client("s3",         region_name=AWS_REGION)

VOICE_S3_PREFIX = "voice-input/"

# ── Supported Polly voices ─────────────────────────────────────────────────────
POLLY_VOICES = {
    "English (Female)":  {"VoiceId": "Joanna",  "LanguageCode": "en-US", "Engine": "neural"},
    "English (Male)":    {"VoiceId": "Matthew",  "LanguageCode": "en-US", "Engine": "neural"},
    "Japanese (Female)": {"VoiceId": "Mizuki",   "LanguageCode": "ja-JP", "Engine": "neural"},
    "Japanese (Male)":   {"VoiceId": "Takumi",   "LanguageCode": "ja-JP", "Engine": "neural"},
}

# ── Transcribe language map ───────────────────────────────────────────────────
TRANSCRIBE_LANG = {
    "English (Female)":  "en-US",
    "English (Male)":    "en-US",
    "Japanese (Female)": "ja-JP",
    "Japanese (Male)":   "ja-JP",
}


# ── STT: Audio → Text ─────────────────────────────────────────────────────────
def transcribe_audio(
    audio_bytes: bytes,
    audio_format: str = "wav",
    language: str = "English (Female)",
) -> str:
    """
    Upload audio to S3, run a Transcribe batch job, return transcript text.
    Takes ~20–60 seconds depending on audio length.
    """
    job_name = f"ev-chatbot-{uuid.uuid4().hex[:10]}"
    s3_key   = f"{VOICE_S3_PREFIX}{job_name}.{audio_format}"

    # 1. Upload audio to S3
    s3.put_object(Bucket=S3_BUCKET_NAME, Key=s3_key, Body=audio_bytes)

    # 2. Start transcription job
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={"MediaFileUri": f"s3://{S3_BUCKET_NAME}/{s3_key}"},
        MediaFormat=audio_format,
        LanguageCode=TRANSCRIBE_LANG.get(language, "en-US"),
    )

    # 3. Poll until complete
    for _ in range(60):
        job = transcribe.get_transcription_job(
            TranscriptionJobName=job_name
        )["TranscriptionJob"]

        status = job["TranscriptionJobStatus"]

        if status == "COMPLETED":
            uri = job["Transcript"]["TranscriptFileUri"]
            with urllib.request.urlopen(uri) as r:
                result = json.loads(r.read())
            _cleanup(s3_key, job_name)
            text = result["results"]["transcripts"][0]["transcript"]
            return text.strip() if text.strip() else "Could not understand audio."

        if status == "FAILED":
            _cleanup(s3_key, job_name)
            raise RuntimeError(f"Transcription failed: {job.get('FailureReason', 'Unknown error')}")

        time.sleep(5)

    _cleanup(s3_key, job_name)
    raise TimeoutError("Transcription timed out after 5 minutes.")


def _cleanup(s3_key: str, job_name: str):
    """Remove temp S3 file and Transcribe job record."""
    try:
        s3.delete_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        transcribe.delete_transcription_job(TranscriptionJobName=job_name)
    except Exception:
        pass


# ── TTS: Text → Audio ─────────────────────────────────────────────────────────
def synthesize_speech(
    text: str,
    voice_option: str = "English (Female)",
) -> bytes:
    """
    Convert answer text to speech using Amazon Polly.
    Returns MP3 audio bytes ready for st.audio().
    """
    cfg = POLLY_VOICES.get(voice_option, POLLY_VOICES["English (Female)"])

    # Polly has 3,000 char limit per request — truncate gracefully
    if len(text) > 2900:
        text = text[:2900] + "... Please read the full answer on screen."

    resp = polly.synthesize_speech(
        Text=text,
        OutputFormat="mp3",
        VoiceId=cfg["VoiceId"],
        Engine=cfg["Engine"],
        LanguageCode=cfg["LanguageCode"],
    )
    return resp["AudioStream"].read()


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    sample = "The SHARP EV has a maximum range of 400 kilometres on a full charge."
    print("Testing Polly TTS...")
    audio_bytes = synthesize_speech(sample, "English (Female)")
    with open("/tmp/test_tts.mp3", "wb") as f:
        f.write(audio_bytes)
    print(f"[✓] TTS saved to /tmp/test_tts.mp3  ({len(audio_bytes)} bytes)")
