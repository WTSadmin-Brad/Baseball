export default function FrameCarousel({ frames, activeFrame, onSelect, sessionId }) {
  return (
    <div style={{
      display: 'flex', gap: 4, padding: '8px 12px',
      borderTop: '1px solid var(--border)', background: 'var(--surface)',
      overflowX: 'auto', flexShrink: 0,
    }}>
      {frames.map((f, i) => (
        <div
          key={i}
          onClick={() => onSelect(i)}
          style={{
            cursor: 'pointer', borderRadius: 6, overflow: 'hidden',
            border: i === activeFrame ? '2px solid var(--accent)' : '2px solid transparent',
            opacity: i === activeFrame ? 1 : 0.6,
            transition: 'all 0.15s', flexShrink: 0,
          }}
        >
          <img
            src={`/api/frame/${sessionId}/${i}/thumbnail`}
            alt={f.phase}
            style={{ height: 64, display: 'block' }}
          />
          <div style={{
            fontSize: 10, padding: '2px 4px', textAlign: 'center',
            background: i === activeFrame ? 'var(--accent)' : 'var(--surface-2)',
            color: i === activeFrame ? '#000' : 'var(--text-dim)',
            fontWeight: i === activeFrame ? 600 : 400,
          }}>
            {i + 1}. {f.phase.split(' / ')[0]}
          </div>
        </div>
      ))}
    </div>
  );
}
