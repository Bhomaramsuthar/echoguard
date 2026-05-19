import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  getMicrophoneSupportError,
  getRecorderErrorMessage,
  getSupportedRecordingMimeType,
} from "../utils/browser.js";

export function useRecorder() {
  const [isRecording, setIsRecording] = useState(false);
  const [isPreparing, setIsPreparing] = useState(false);
  const [elapsedMs, setElapsedMs] = useState(0);
  const [liveWaveform, setLiveWaveform] = useState([]);
  const [recordedFile, setRecordedFile] = useState(null);
  const [recordedUrl, setRecordedUrl] = useState("");
  const [error, setError] = useState("");
  const supportError = useMemo(() => getMicrophoneSupportError(), []);

  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const chunksRef = useRef([]);
  const audioContextRef = useRef(null);
  const animationRef = useRef(0);
  const startedAtRef = useRef(0);

  const clearRecording = useCallback(() => {
    if (recordedUrl) URL.revokeObjectURL(recordedUrl);
    setRecordedFile(null);
    setRecordedUrl("");
  }, [recordedUrl]);

  const stopVisualizer = useCallback(() => {
    cancelAnimationFrame(animationRef.current);
    animationRef.current = 0;
    audioContextRef.current?.close();
    audioContextRef.current = null;
  }, []);

  const stopTracks = useCallback(() => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
  }, []);

  const startVisualizer = useCallback((stream) => {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextClass) return;

    const context = new AudioContextClass();
    const analyser = context.createAnalyser();
    analyser.fftSize = 1024;
    context.createMediaStreamSource(stream).connect(analyser);
    const data = new Uint8Array(analyser.frequencyBinCount);
    audioContextRef.current = context;

    const tick = () => {
      analyser.getByteTimeDomainData(data);
      const samples = Array.from(data)
        .filter((_, index) => index % 8 === 0)
        .map((value) => Math.abs((value - 128) / 128));
      setLiveWaveform(samples);
      setElapsedMs(Date.now() - startedAtRef.current);
      animationRef.current = requestAnimationFrame(tick);
    };
    tick();
  }, []);

  const startRecording = useCallback(async () => {
    setError("");

    if (supportError) {
      setError(supportError);
      return { ok: false, error: supportError };
    }

    clearRecording();
    setIsPreparing(true);
    chunksRef.current = [];

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      const mimeType = getSupportedRecordingMimeType();
      const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data);
      };
      recorder.onerror = (event) => {
        setError(getRecorderErrorMessage(event.error));
      };

      mediaRecorderRef.current = recorder;
      streamRef.current = stream;
      startedAtRef.current = Date.now();
      setElapsedMs(0);
      setLiveWaveform([]);

      // Collect small chunks so mobile browsers flush data reliably on stop.
      recorder.start(250);
      setIsRecording(true);
      startVisualizer(stream);
      return { ok: true };
    } catch (exception) {
      const message = getRecorderErrorMessage(exception);
      setError(message);
      stopTracks();
      return { ok: false, error: message };
    } finally {
      setIsPreparing(false);
    }
  }, [clearRecording, startVisualizer, stopTracks, supportError]);

  const stopRecording = useCallback(
    () =>
      new Promise((resolve) => {
        const recorder = mediaRecorderRef.current;
        if (!recorder || recorder.state === "inactive") {
          resolve(null);
          return;
        }

        recorder.onstop = () => {
          const mimeType = recorder.mimeType || getSupportedRecordingMimeType() || "audio/webm";
          const extension = mimeType.includes("ogg") ? "ogg" : mimeType.includes("mp4") ? "m4a" : "webm";
          const blob = new Blob(chunksRef.current, { type: mimeType });
          const file = new File([blob], `live-recording-${Date.now()}.${extension}`, { type: mimeType });

          setIsRecording(false);
          stopVisualizer();
          stopTracks();
          setRecordedFile(file);
          setRecordedUrl(URL.createObjectURL(blob));
          resolve(file);
        };

        recorder.requestData?.();
        recorder.stop();
      }),
    [stopTracks, stopVisualizer],
  );

  useEffect(
    () => () => {
      stopVisualizer();
      stopTracks();
      if (recordedUrl) URL.revokeObjectURL(recordedUrl);
    },
    [recordedUrl, stopTracks, stopVisualizer],
  );

  return {
    elapsedMs,
    error,
    isPreparing,
    isRecording,
    liveWaveform,
    recordedFile,
    recordedUrl,
    supportError,
    clearRecording,
    startRecording,
    stopRecording,
  };
}
