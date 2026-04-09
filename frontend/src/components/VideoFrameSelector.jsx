import { useState, useCallback } from 'react';

export default function VideoFrameSelector({ session, onConfirm, loading }) {
  const [selected, setSelected] = useState([]);
  const totalFrames = session.extracted_frame_count || session.video_frame_count || 0;
  const sid = session.session_id;

  const toggleFrame = useCallback((idx) => {
    setSelected(prev => {
      if (prev.includes(idx)) return prev.filter(i => i !== idx);
      if (prev.length >= 8) return prev; // Max 8 frames
      return [...prev, idx].sort((a, b) => a - b);
    });
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <header style={{
        padding: '12px 16px', borderBottom: '1px solid var(--border)',
        background: 'var(--surface)', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        <div>
          <h1 style={{ fontSize: 18, fontWeight: 600 }}>Select Swing Frames</h1>
          <p style={{ fontSize: 12, color: 'var(--text-dim)' }}>
            Click to select up to 8 key frames from the video ({selected.length}/8 selected)
          </p>
        </div>
        <button
          className="primary"
          onClick={() => onConfirm(selected)}
          disabled={selected.length === 0 || loading}
        >
          {loading ? 'Processing...' : `Analyze ${selected.length} Frames`}
        </button>
      </header>

      <div style={{
        flex: 1, overflow: 'auto', padding: 16,
        display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))',
        gap: 8,
      }}>
        {Array.from({ length: totalFrames }, (_, i) => {
          const isSelected = selected.includes(i);
          const selIdx = selected.indexOf(i);
          return (
            <div
              key={i}
              onClick={() => toggleFrame(i)}
              style={{
                cursor: 'pointer', borderRadius: 6, overflow: 'hidden',
                border: isSelected ? '2px solid var(--accent)' : '2px solid var(--border)',
                opacity: isSelected ? 1 : 0.65,
                position: 'relative',
              }}
            >
              <img
                src={`/api/video-frame/${sid}/${i}/thumbnail`}
                alt={`Frame ${i}`}
                style={{ width: '100%', display: 'block' }}
                loading="lazy"
              />
              {isSelected && (
                <div style={{
                  position: 'absolute', top: 4, right: 4,
                  width: 22, height: 22, borderRadius: '50%',
                  background: 'var(--accent)', color: '#000',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 12, fontWeight: 700,
                }}>
                  {selIdx + 1}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
