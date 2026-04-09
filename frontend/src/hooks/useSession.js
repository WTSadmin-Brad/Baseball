import { useState, useCallback } from 'react';

const api = (path, opts = {}) =>
  fetch(`/api${path}`, opts).then(r => {
    if (!r.ok) throw new Error(`API error: ${r.status}`);
    return r.json();
  });

export default function useSession() {
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeFrame, setActiveFrame] = useState(0);
  const [config, setConfig] = useState(null);

  const loadConfig = useCallback(async () => {
    const cfg = await api('/config');
    setConfig(cfg);
    return cfg;
  }, []);

  const uploadImages = useCallback(async (files) => {
    setLoading(true);
    setError(null);
    try {
      const form = new FormData();
      files.forEach(f => form.append('files', f));
      const { session_id } = await api('/upload/images', { method: 'POST', body: form });
      // Run detection
      await api(`/detect/${session_id}`, { method: 'POST' });
      // Load session
      const data = await api(`/session/${session_id}`);
      setSession(data);
      setActiveFrame(0);
      return data;
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const uploadVideo = useCallback(async (file) => {
    setLoading(true);
    setError(null);
    try {
      const form = new FormData();
      form.append('file', file);
      const data = await api('/upload/video', { method: 'POST', body: form });
      setSession({ ...data, mode: 'video_select' });
      return data;
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const selectVideoFrames = useCallback(async (sessionId, indices) => {
    setLoading(true);
    try {
      await api(`/video/${sessionId}/select-frames`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(indices),
      });
      await api(`/detect/${sessionId}`, { method: 'POST' });
      const data = await api(`/session/${sessionId}`);
      setSession(data);
      setActiveFrame(0);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const updateLandmarks = useCallback(async (frameId, landmarks) => {
    if (!session) return;
    try {
      const { metrics } = await api(`/landmarks/${session.session_id}/${frameId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ landmarks }),
      });
      // Refresh session
      const data = await api(`/session/${session.session_id}`);
      setSession(data);
      return metrics;
    } catch (e) {
      setError(e.message);
    }
  }, [session]);

  const saveAnnotations = useCallback(async (frameId, annotations) => {
    if (!session) return;
    await api(`/annotations/${session.session_id}/${frameId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(annotations),
    });
  }, [session]);

  const currentFrame = session?.frames?.[activeFrame] || null;

  return {
    session, loading, error, config,
    activeFrame, setActiveFrame,
    currentFrame,
    loadConfig, uploadImages, uploadVideo,
    selectVideoFrames, updateLandmarks, saveAnnotations,
  };
}
