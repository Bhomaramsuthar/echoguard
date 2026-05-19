# EchoGuard

EchoGuard is a forensic AI audio analysis platform for detecting synthetic or deepfake voice clips. The upgraded app includes a responsive React cybersecurity dashboard, FastAPI backend, live microphone capture, multi-format audio conversion, waveform visualization, spectrogram generation, metadata extraction, and model inference through the existing PyTorch pipeline.

## Features

- Responsive React + Vite dashboard with TailwindCSS, glass panels, dark mode, and Framer Motion animations
- Drag-and-drop upload for `.wav`, `.aac`, `.m4a`, `.flac`, `.mp3`, `.aiff`, `.ogg`, `.wma`, `.dsf`, and `.dff`
- Live microphone recording with `MediaRecorder` and browser waveform preview
- Centralized backend `process_audio()` pipeline using FFmpeg + pydub, librosa, matplotlib, and PyTorch
- Normalized WAV conversion at 22,050 Hz, mono, PCM 16-bit
- Waveform data, dark forensic spectrograms, confidence meters, risk labels, and audio metadata
- Session detection history in the UI

## Project Structure

```text
backend/
  api/                 FastAPI routes
  models/              Model-facing package boundary
  preprocessing/       Validation, conversion, normalization, waveform, metadata
  services/            Detection orchestration
  uploads/             Runtime upload, processed WAV, and spectrogram output
  utils/               Filename and asset helpers
  visualization/       Spectrogram rendering
frontend/src/
  components/          Reusable dashboard UI
  hooks/               Microphone recording hook
  layouts/             Responsive app shell
  pages/               Dashboard page
  services/            API client
  utils/               Formatting helpers
```

## Backend Setup

```powershell
cd "c:\Users\aadir\Desktop\eaco gaurd\echoguard"
..\venv\Scripts\python.exe -m pip install -r requirements.txt
```

Create a `.env` file from `.env.example`:

```powershell
Copy-Item .env.example .env
```

Default local settings:

```env
ENVIRONMENT=development
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=echoguard
UPLOAD_DIR=uploads
FFMPEG_PATH=ffmpeg
MODEL_WEIGHTS_PATH=echoguard_weights.pth
```

Start MongoDB locally, or replace `MONGODB_URL` with your MongoDB Atlas connection string.

Start the API:

```powershell
..\venv\Scripts\uvicorn.exe main:app --reload --host 127.0.0.1 --port 8000
```

Health check:

```text
http://127.0.0.1:8000/health
```

## Frontend Setup

```powershell
cd "c:\Users\aadir\Desktop\eaco gaurd\echoguard\frontend"
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

## Microphone Testing

Browser microphone APIs only work in a secure context:

- Works locally: `http://localhost:5173` or `http://127.0.0.1:5173`
- Works in production: HTTPS deployment
- Does not work: plain HTTP from another device, such as `http://192.168.x.x:5173`

Chrome, Edge, Firefox, and most Android browsers require you to allow microphone permission when prompted. If permission was denied earlier, open the browser site settings and reset microphone access.

For desktop testing, do not open the LAN IP. Use:

```text
http://127.0.0.1:5173
```

For mobile or another device on your LAN, run Vite with HTTPS:

```powershell
npm run dev:https
```

Open the HTTPS LAN URL shown by Vite, for example:

```text
https://192.168.0.116:5173
```

The browser will show a self-signed certificate warning during local development. Accept it only for your own dev machine.

If you have your own trusted certificate, you can provide it:

```powershell
$env:VITE_HTTPS="true"
$env:VITE_HTTPS_KEY="C:\path\to\localhost-key.pem"
$env:VITE_HTTPS_CERT="C:\path\to\localhost-cert.pem"
npm run dev -- --host 0.0.0.0
```

The Vite dev server proxies `/api` and `/assets` to FastAPI, so mobile browsers can call the backend through the same HTTPS origin.

Optional API override:

```powershell
$env:VITE_API_BASE_URL="http://127.0.0.1:8000"
npm run dev
```

## Production Checklist

Before pushing to a new public or private repo:

- Do not commit `.env`, uploaded audio, generated images, logs, `node_modules`, `dist`, virtualenvs, or model weight files. These are covered by `.gitignore`.
- Keep `echoguard_weights.pth` outside git. In production, provide it through secure storage or a mounted volume and set `MODEL_WEIGHTS_PATH`.
- Set `ENVIRONMENT=production` to disable interactive API docs and reduce internal error leakage.
- Set `CORS_ORIGINS` to the exact frontend origin, for example `https://app.example.com`.
- Set `ALLOWED_HOSTS` to the API hostnames, for example `api.example.com,localhost`.
- Set `MONGODB_URL` from your secret manager, not in source control.
- Install FFmpeg on the host/container and set `FFMPEG_PATH` if it is not on `PATH`.
- Keep `MAX_UPLOAD_SIZE_MB` aligned with your reverse proxy limit.

Minimal production API environment:

```env
ENVIRONMENT=production
MONGODB_URL=mongodb+srv://USER:PASSWORD@cluster.example.mongodb.net
DATABASE_NAME=echoguard
CORS_ORIGINS=https://app.example.com
ALLOWED_HOSTS=api.example.com
UPLOAD_DIR=/data/uploads
TEMP_AUDIO_DIR=/data/temp_audio
TEMP_IMAGE_DIR=/data/temp_images
FFMPEG_PATH=/usr/bin
MODEL_WEIGHTS_PATH=/models/echoguard_weights.pth
MAX_UPLOAD_SIZE_MB=25
```

Build checks:

```powershell
..\venv\Scripts\python.exe -m compileall main.py backend model_inference.py
cd frontend
npm run build
```

Docker API image:

```powershell
docker build -t echoguard-api .
docker run --env-file .env -p 8000:8000 -v ${PWD}\uploads:/data/uploads -v ${PWD}\echoguard_weights.pth:/models/echoguard_weights.pth:ro echoguard-api
```

Docker Compose for the API, frontend, and MongoDB:

```powershell
docker compose up --build
```

Compose expects `echoguard_weights.pth` to exist in the project root and mounts it read-only into the API container. Open the app at:

```text
http://localhost:8080
```

## FFmpeg Setup on Windows

Multi-format decoding depends on FFmpeg and ffprobe being available on `PATH`.

Recommended install with winget:

```powershell
winget install Gyan.FFmpeg
```

Then restart the terminal and verify:

```powershell
ffmpeg -version
ffprobe -version
```

If winget is unavailable, download a Windows FFmpeg build, extract it, and add its `bin` folder to your system `PATH`.

## Verification

Backend syntax/import checks:

```powershell
..\venv\Scripts\python.exe -m compileall main.py backend model_inference.py
..\venv\Scripts\python.exe -c "import main; print(main.app.title)"
```

Frontend production build:

```powershell
cd frontend
npm run build
```

## Notes

- The existing CNN spectrogram inference path remains in use through `audio_processor.py` and `model_inference.py`.
- Without FFmpeg on `PATH`, pydub may still handle simple WAV files, but compressed formats and live browser recordings can fail.
- Generated runtime files are stored under `uploads/` and `temp_images/`.
- Detection history is stored in MongoDB through Motor + Beanie. If MongoDB is not reachable, analysis can still return a result, but persisted history APIs return `503`.
- Uploaded and generated artifacts are stored in `uploads/audio/`, `uploads/waveforms/`, and `uploads/spectrograms/`.
