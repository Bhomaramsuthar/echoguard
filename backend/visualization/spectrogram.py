from pathlib import Path

import librosa
import librosa.display
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def create_forensic_spectrogram(audio_path: Path, output_path: Path, sample_rate: int) -> Path:
    y, sr = librosa.load(audio_path, sr=sample_rate, mono=True)
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=2048, hop_length=512, n_mels=128)
    mel_db = librosa.power_to_db(mel, ref=np.max)

    fig, ax = plt.subplots(figsize=(10, 4.8), dpi=140, facecolor="#101419")
    ax.set_facecolor("#101419")
    img = librosa.display.specshow(
        mel_db,
        sr=sr,
        hop_length=512,
        x_axis="time",
        y_axis="mel",
        cmap="magma",
        ax=ax,
    )
    ax.set_title("Mel-frequency forensic spectrogram", color="#eef2ff", pad=12)
    ax.set_xlabel("Time", color="#cbd5e1")
    ax.set_ylabel("Frequency", color="#cbd5e1")
    ax.tick_params(colors="#94a3b8")
    cbar = fig.colorbar(img, ax=ax, format="%+2.0f dB")
    cbar.ax.yaxis.set_tick_params(color="#94a3b8")
    plt.setp(cbar.ax.get_yticklabels(), color="#94a3b8")
    cbar.set_label("Power", color="#cbd5e1")
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    return output_path
