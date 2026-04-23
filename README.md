# 🛡️ EchoGuard: Vishing Defense

![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-2.11.0-EE4C2C)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136.0-009688)
![Streamlit](https://img.shields.io/badge/Streamlit-1.56.0-FF4B4B)

**EchoGuard** is a defense system against AI-generated voice phishing (Vishing) attacks. By converting audio signals into visual Mel-Spectrogram textures, EchoGuard utilizes a high-performance Convolutional Neural Network (CNN) to mathematically distinguish between authentic human voices and synthetic AI deepfakes.

## ✨ Key Features
- **Real-Time API Processing:** High-performance asynchronous API using FastAPI.
- **Audio-to-Image Transformation:** Uses `librosa` to map time-domain waveforms into frequency-domain Mel-Spectrograms (Magma colormap).
- **Deepfake Classification:** Modified PyTorch ResNet18 architecture tailored specifically for texture-based deepfake artifact detection.
- **Interactive UI Dashboard:** Built with Streamlit for a fast, intuitive, and user-friendly defense dashboard.

## 🛠️ Technology Stack
- **Frontend Dashboard:** Streamlit
- **Backend API:** FastAPI & Uvicorn
- **Audio Signal Processing:** Librosa, Matplotlib, Numpy
- **Artificial Intelligence Framework:** PyTorch & Torchvision

## 🧠 How it Works

1. **Ingestion & Standardization (`main.py`):** The system receives a `.wav` file and processes it via the REST API.
2. **Acoustic Frequency Mapping (`audio_processor.py`):** The audio is standardized to a `22050 Hz` sample rate and strictly zero-padded to 5 seconds. The Fast Fourier Transform (FFT) generates a high-contrast Mel-Spectrogram image representing the audio in decibels (dB), stripping out all axes for pure data pixels.
3. **Neural Network Inference (`model_definition.py` & `model_inference.py`):** The image is normalized and passed into a modified **ResNet18 CNN**. The model is trained to spot mathematical visual anomalies and acoustic artifacts exclusively left by AI voice synthesizers (e.g., ElevenLabs).
4. **Final Verdict:** The network issues a confidence probability, displayed on the Streamlit dashboard alongside the visual spectrogram data.

## 🚀 Installation & Execution

### Prerequisites
Make sure you have Python 3.8+ installed. It is recommended to use a virtual environment.

### 1. Setup the Environment
Clone the repository and install the dependencies:
```bash
python -m venv venv

# On Windows
.\venv\Scripts\activate

# On Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Start the Backend API
You will need to open **two** terminal windows. In the first terminal (ensure the `venv` is active):
```bash
uvicorn main:app --reload
```
*The FastAPI server will start locally on port 8000.*

### 3. Start the Frontend Dashboard
In the second terminal (ensure the `venv` is active):
```bash
streamlit run app.py
```
*Your browser will open automatically to the EchoGuard UI at `http://localhost:8501`.*

## 📂 Project Structure
```
echoguard-vishing/
│
├── app.py                     # Streamlit User Interface
├── main.py                    # FastAPI Backend Server
├── audio_processor.py         # Librosa audio-to-spectrogram pipeline
├── model_definition.py        # PyTorch ResNet18 CNN Architecture
├── model_inference.py         # AI Model inference and threshold logic
├── augment_data.py            # Data augmentation utilities
├── echoguard_weights.pth      # Trained neural network weights
└── requirements.txt           # Python dependencies
```

## ⚠️ Disclaimer
This system is designed as an educational tool for cybersecurity defense and acoustic research. Please do not use it for production-level automated security blocking without further adversarial training.
