const METRIC_DEFS = [
  { key: 'hip_shoulder_separation', label: 'Hip-Shoulder Sep', color: 'var(--hip-color)', unit: '\u00b0', description: 'Separation between hip and shoulder rotation (lower half leading)' },
  { key: 'hip_line_angle', label: 'Hip Rotation', color: 'var(--hip-color)', unit: '\u00b0', description: 'Hip line angle from horizontal' },
  { key: 'shoulder_line_angle', label: 'Shoulder Rotation', color: 'var(--shoulder-color)', unit: '\u00b0', description: 'Shoulder line angle from horizontal' },
  { key: 'back_elbow_angle', label: 'Back Elbow', color: 'var(--back-arm)', unit: '\u00b0', description: 'Elbow angle of the back arm (slot/connection)' },
  { key: 'front_elbow_angle', label: 'Front Elbow', color: 'var(--front-arm)', unit: '\u00b0', description: 'Elbow angle of the front arm (lead arm)' },
  { key: 'front_knee_angle', label: 'Front Knee', color: 'var(--front-leg)', unit: '\u00b0', description: 'Front knee angle (front side firmness)' },
  { key: 'back_knee_angle', label: 'Back Knee', color: 'var(--back-leg)', unit: '\u00b0', description: 'Back knee angle (back leg drive)' },
  { key: 'spine_tilt', label: 'Spine Tilt', color: 'var(--spine-color)', unit: '\u00b0', description: 'Spine tilt from vertical (posture)' },
];

export default function MetricsPanel({ frame, frameIndex }) {
  const metrics = frame?.metrics || {};

  return (
    <div style={{ padding: 16 }}>
      <h2 style={{ fontSize: 14, fontWeight: 600, marginBottom: 4, color: 'var(--accent)' }}>
        Frame {frameIndex + 1}
      </h2>
      <h3 style={{ fontSize: 16, fontWeight: 500, marginBottom: 16 }}>
        {frame?.phase || 'No frame selected'}
      </h3>

      {!frame?.landmarks && (
        <p style={{ color: 'var(--text-dim)', fontSize: 13 }}>No pose data detected</p>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {METRIC_DEFS.map(({ key, label, color, unit, description }) => {
          const val = metrics[key];
          if (val === undefined) return null;
          return (
            <div key={key} style={{
              background: 'var(--surface-2)', borderRadius: 6, padding: '8px 12px',
              borderLeft: `3px solid ${color}`,
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                <span style={{ fontSize: 12, color: 'var(--text-dim)' }}>{label}</span>
                <span style={{ fontSize: 18, fontWeight: 600, color, fontVariantNumeric: 'tabular-nums' }}>
                  {val.toFixed(1)}{unit}
                </span>
              </div>
              <div style={{ fontSize: 10, color: 'var(--text-dim)', marginTop: 2 }}>{description}</div>
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div style={{ marginTop: 20, borderTop: '1px solid var(--border)', paddingTop: 12 }}>
        <h4 style={{ fontSize: 12, fontWeight: 600, marginBottom: 8, color: 'var(--text-dim)' }}>COLOR LEGEND</h4>
        {[
          ['Shoulders', 'var(--shoulder-color)'],
          ['Hips', 'var(--hip-color)'],
          ['Spine', 'var(--spine-color)'],
          ['Front Arm', 'var(--front-arm)'],
          ['Back Arm', 'var(--back-arm)'],
          ['Front Leg', 'var(--front-leg)'],
          ['Back Leg', 'var(--back-leg)'],
        ].map(([name, color]) => (
          <div key={name} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 3, fontSize: 11 }}>
            <span style={{ width: 10, height: 10, borderRadius: '50%', background: color, flexShrink: 0 }} />
            {name}
          </div>
        ))}
      </div>
    </div>
  );
}
