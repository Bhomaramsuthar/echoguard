from pathlib import Path

from audio_processor import generate_spectrogram
from backend.config import MODEL_DURATION_SECONDS, TEMP_IMAGE_DIR
from backend.preprocessing.audio_pipeline import process_audio
from model_inference import analyze_spectrogram


def analyze_audio_file(original_path: Path, filename: str, is_live_recording: bool = False) -> dict:
    processed = process_audio(original_path)

    model_image_path = TEMP_IMAGE_DIR / f"model_{processed['normalized_path'].stem}.png"
    generated_model_image = generate_spectrogram(
        str(processed["normalized_path"]),
        str(model_image_path),
        duration=MODEL_DURATION_SECONDS,
    )
    if not generated_model_image:
        raise RuntimeError("Failed to generate model spectrogram.")

    analysis = analyze_spectrogram(generated_model_image)
    fake_probability = float(analysis.get("fake_probability", 0))
    human_probability = float(analysis.get("human_probability", 0))
    prediction = "fake" if analysis.get("ui_color") == "red" else "real"
    confidence = fake_probability if prediction == "fake" else human_probability

    return {
        "filename": filename,
        "original_format": processed["original_format"],
        "prediction": prediction,
        "confidence": round(confidence, 4),
        "fake_probability": round(fake_probability, 4),
        "human_probability": round(human_probability, 4),
        "risk_level": analysis.get("risk_level", "unknown"),
        "analysis": analysis,
        "waveform": processed["waveform"],
        "waveform_image_url": processed["waveform_image_url"],
        "waveform_image_path": str(processed["waveform_image_path"]),
        "spectrogram_url": processed["spectrogram_url"],
        "spectrogram_path": str(processed["spectrogram_path"]),
        "converted_wav_path": str(processed["normalized_path"]),
        "is_live_recording": is_live_recording,
        "processing_time": processed["processing_time"],
        "metadata": processed["metadata"],
    }


def build_detection_document_payload(result: dict) -> dict:
    metadata = result.get("metadata", {})
    return {
        "filename": result.get("filename", "unknown"),
        "original_format": result.get("original_format"),
        "converted_wav_path": result.get("converted_wav_path"),
        "waveform_image": result.get("waveform_image_url"),
        "spectrogram_image": result.get("spectrogram_url"),
        "prediction": result.get("prediction"),
        "confidence": result.get("confidence"),
        "duration": metadata.get("duration"),
        "sample_rate": metadata.get("sample_rate"),
        "channels": metadata.get("channels"),
        "processing_time": result.get("processing_time"),
        "is_live_recording": result.get("is_live_recording", False),
        "metadata": metadata,
        "status": "completed",
    }
