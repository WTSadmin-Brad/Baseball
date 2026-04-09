import { useCallback, useRef } from 'react';

export default function UploadPanel({ onUploadImages, onUploadVideo, loading }) {
  const imageRef = useRef();
  const videoRef = useRef();

  const handleImages = useCallback((e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) onUploadImages(files);
  }, [onUploadImages]);

  const handleVideo = useCallback((e) => {
    const file = e.target.files[0];
    if (file) onUploadVideo(file);
  }, [onUploadVideo]);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files);
    const videos = files.filter(f => f.type.startsWith('video/'));
    const images = files.filter(f => f.type.startsWith('image/'));
    if (videos.length > 0) onUploadVideo(videos[0]);
    else if (images.length > 0) onUploadImages(images);
  }, [onUploadImages, onUploadVideo]);

  return (
    <div
      onDrop={handleDrop}
      onDragOver={e => e.preventDefault()}
      style={{
        border: '2px dashed var(--border)', borderRadius: 12, padding: 48,
        textAlign: 'center', maxWidth: 500, width: '100%',
        background: 'var(--surface)', cursor: 'pointer',
      }}
    >
      <p style={{ fontSize: 16, marginBottom: 20, color: 'var(--text-dim)' }}>
        Drag & drop images or a video here, or:
      </p>
      <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
        <button className="primary" onClick={() => imageRef.current.click()} disabled={loading}>
          Upload Images
        </button>
        <button onClick={() => videoRef.current.click()} disabled={loading}>
          Upload Video
        </button>
      </div>
      <input ref={imageRef} type="file" accept="image/*" multiple hidden onChange={handleImages} />
      <input ref={videoRef} type="file" accept="video/*" hidden onChange={handleVideo} />
    </div>
  );
}
