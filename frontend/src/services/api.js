const isLocalBrowser =
  window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" || window.location.hostname === "::1";
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? (isLocalBrowser ? "http://127.0.0.1:8000" : "/api");

export async function analyzeAudio(file, endpoint = "/analyze") {
  const formData = new FormData();
  formData.append("audio_file", file);

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: "POST",
    body: formData,
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(getErrorMessage(data, `Analysis failed with status ${response.status}`));
  }

  return normalizeResult(data);
}

export function toAssetUrl(path) {
  if (!path) return "";
  if (path.startsWith("/assets") && API_BASE_URL === "/api") return path;
  return path.startsWith("http") ? path : `${API_BASE_URL}${path}`;
}

export async function fetchDetections({ page = 1, limit = 20, search = "", prediction = "" } = {}) {
  const params = new URLSearchParams({ page: String(page), limit: String(limit) });
  if (search) params.set("search", search);
  if (prediction) params.set("prediction", prediction);

  const response = await fetch(`${API_BASE_URL}/detections?${params.toString()}`);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(getErrorMessage(data, `Could not load detections (${response.status})`));
  }

  return {
    ...data,
    items: (data.items ?? []).map(normalizeDetectionRecord),
  };
}

export async function deleteDetection(id) {
  const response = await fetch(`${API_BASE_URL}/detections/${id}`, { method: "DELETE" });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(getErrorMessage(data, `Could not delete detection (${response.status})`));
  }
  return data;
}

function getErrorMessage(data, fallback) {
  if (typeof data.detail === "string") return data.detail;
  if (data.detail?.error && data.detail?.details) return `${data.detail.error}: ${data.detail.details}`;
  if (data.detail?.error?.message) return data.detail.error.message;
  if (data.error && data.details) return `${data.error}: ${data.details}`;
  if (data.error?.message) return data.error.message;
  if (typeof data.error === "string") return data.error;
  return fallback;
}

function normalizeResult(data) {
  const prediction = data.prediction ?? (data.analysis?.ui_color === "red" ? "fake" : "real");
  const fakeProbability = Number(data.fake_probability ?? data.analysis?.fake_probability ?? 0);
  const humanProbability = Number(data.human_probability ?? data.analysis?.human_probability ?? 0);
  const confidence = Number(data.confidence ?? (prediction === "fake" ? fakeProbability : humanProbability));

  return {
    filename: data.filename,
    verdict: prediction === "fake" ? "Synthetic" : "Human",
    label: data.analysis?.verdict ?? "Analysis complete",
    isFake: prediction === "fake",
    confidenceScore: Math.round(confidence * 100),
    fakeProbability: Math.round(fakeProbability * 100),
    humanProbability: Math.round(humanProbability * 100),
    riskLevel: data.risk_level ?? data.analysis?.risk_level ?? "unknown",
    waveform: data.waveform ?? [],
    spectrogramUrl: toAssetUrl(data.spectrogram_url ?? data.spectrogram_path),
    metadata: data.metadata ?? {},
    raw: data,
  };
}

function normalizeDetectionRecord(item) {
  const prediction = item.prediction ?? "unknown";
  return {
    id: item.id,
    filename: item.filename,
    verdict: prediction === "fake" ? "Synthetic" : "Human",
    prediction,
    isFake: prediction === "fake",
    score: Math.round(Number(item.confidence ?? 0) * 100),
    confidence: Number(item.confidence ?? 0),
    time: item.uploaded_at ? new Date(item.uploaded_at).toLocaleString() : "Unknown",
    waveformImageUrl: toAssetUrl(item.waveform_image),
    spectrogramUrl: toAssetUrl(item.spectrogram_image),
    duration: item.duration,
    sampleRate: item.sample_rate,
    isLiveRecording: item.is_live_recording,
    raw: item,
  };
}
