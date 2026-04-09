import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

const CHART_METRICS = [
  { key: 'hip_shoulder_separation', label: 'Hip-Shoulder Sep', color: '#ff6400' },
  { key: 'back_elbow_angle', label: 'Back Elbow', color: '#00ff64' },
  { key: 'front_knee_angle', label: 'Front Knee', color: '#ffe600' },
  { key: 'spine_tilt', label: 'Spine Tilt', color: '#ffffff' },
];

export default function MetricsChart({ frames, activeFrame }) {
  const data = frames.map((f, i) => ({
    name: `${i + 1}`,
    phase: f.phase?.split(' / ')[0] || `F${i+1}`,
    ...(f.metrics || {}),
  }));

  return (
    <div style={{ padding: '8px 16px 16px', borderTop: '1px solid var(--border)' }}>
      <h4 style={{ fontSize: 12, fontWeight: 600, marginBottom: 8, color: 'var(--text-dim)' }}>
        METRICS ACROSS PHASES
      </h4>
      <div style={{ height: 200 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 5, bottom: 5, left: -20 }}>
            <XAxis
              dataKey="name"
              tick={{ fill: '#888', fontSize: 10 }}
              axisLine={{ stroke: '#333' }}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: '#888', fontSize: 10 }}
              axisLine={{ stroke: '#333' }}
              tickLine={false}
            />
            <Tooltip
              contentStyle={{ background: '#222', border: '1px solid #444', borderRadius: 6, fontSize: 12 }}
              labelFormatter={(v) => {
                const f = frames[parseInt(v) - 1];
                return f ? f.phase : v;
              }}
              formatter={(val, name) => [`${val.toFixed(1)}\u00b0`, name]}
            />
            <ReferenceLine x={`${activeFrame + 1}`} stroke="var(--accent)" strokeDasharray="3 3" />
            {CHART_METRICS.map(({ key, label, color }) => (
              <Line
                key={key}
                type="monotone"
                dataKey={key}
                name={label}
                stroke={color}
                strokeWidth={2}
                dot={{ r: 3, fill: color }}
                activeDot={{ r: 5 }}
                connectNulls
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px 12px', marginTop: 8 }}>
        {CHART_METRICS.map(({ key, label, color }) => (
          <div key={key} style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 10 }}>
            <span style={{ width: 8, height: 3, background: color, borderRadius: 1 }} />
            <span style={{ color: '#888' }}>{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
