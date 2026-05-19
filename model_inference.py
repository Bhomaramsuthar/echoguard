from functools import lru_cache
import torch
import torch.nn.functional as F
import torchvision.transforms as transforms
from PIL import Image

from backend.config import IS_PRODUCTION, MODEL_WEIGHTS_PATH
from model_definition import EchoGuardCNN


@lru_cache(maxsize=1)
def _load_model() -> EchoGuardCNN:
    model = EchoGuardCNN()
    if MODEL_WEIGHTS_PATH.exists():
        model.load_state_dict(torch.load(MODEL_WEIGHTS_PATH, map_location=torch.device("cpu")))
        print(f"Loaded trained model weights from: {MODEL_WEIGHTS_PATH}")
    elif IS_PRODUCTION:
        raise RuntimeError(f"Model weights were not found at MODEL_WEIGHTS_PATH={MODEL_WEIGHTS_PATH}")
    else:
        print("No trained weights found. Using initialized network (untrained). Set MODEL_WEIGHTS_PATH for production.")

    model.eval()
    return model


@lru_cache(maxsize=1)
def _image_transform():
    return transforms.Compose(
        [
            transforms.Resize((128, 128)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
        ]
    )


def analyze_spectrogram(image_path: str) -> dict:
    print(f"PyTorch analyzing visual tensor: {image_path}...")

    try:
        model = _load_model()
        img = Image.open(image_path).convert("RGB")
        input_tensor = _image_transform()(img).unsqueeze(0)

        with torch.no_grad():
            output = model(input_tensor)
            probabilities = F.softmax(output, dim=1)
            fake_prob = probabilities[0][0].item()
            real_prob = probabilities[0][1].item()

        if not IS_PRODUCTION:
            print("=" * 40)
            print(f"FAKE SCORE: {fake_prob * 100:.2f}%")
            print(f"REAL SCORE: {real_prob * 100:.2f}%")
            print("=" * 40)

        if fake_prob > 0.60:
            return {
                "verdict": "Synthetic Audio (Deepfake)",
                "threat_score": round(fake_prob, 4),
                "fake_probability": round(fake_prob, 4),
                "human_probability": round(real_prob, 4),
                "risk_level": "high" if fake_prob >= 0.75 else "elevated",
                "ui_color": "red"
            }
        else:
            return {
                "verdict": "Authentic Human Voice",
                "threat_score": round(real_prob, 4),
                "fake_probability": round(fake_prob, 4),
                "human_probability": round(real_prob, 4),
                "risk_level": "low" if fake_prob < 0.35 else "moderate",
                "ui_color": "green"
            }

    except Exception as e:
        print(f"PyTorch inference error: {e}")
        if IS_PRODUCTION:
            raise
        return {"verdict": "Error processing tensor", "threat_score": 0.0, "ui_color": "red"}
