import { useRef, useEffect, useState, useCallback } from 'react';

const COLORS = {
  hip: '#ff6400', shoulder: '#00c8ff', spine: '#ffffff',
  front_arm: '#64ff00', back_arm: '#00ff64',
  front_leg: '#ffe600', back_leg: '#e6c800',
  head: '#ffffff', bat: '#ffb400', plumb: '#888888',
};

const JOINT_GROUPS = {
  0: 'head', 7: 'head', 8: 'head',
  11: 'shoulder', 12: 'shoulder',
  13: 'front_arm', 14: 'back_arm',
  15: 'front_arm', 16: 'back_arm',
  23: 'hip', 24: 'hip',
  25: 'front_leg', 26: 'back_leg',
  27: 'front_leg', 28: 'back_leg',
};

const SWING_LANDMARKS = [0, 7, 8, 11, 12, 13, 14, 15, 16, 19, 20, 23, 24, 25, 26, 27, 28];

export default function FrameViewer({ session, frame, frameIndex, viewMode, config, onUpdateLandmarks }) {
  const canvasRef = useRef(null);
  const imgRef = useRef(null);
  const containerRef = useRef(null);
  const [imgLoaded, setImgLoaded] = useState(false);
  const [dragging, setDragging] = useState(null);
  const [localLandmarks, setLocalLandmarks] = useState(null);
  const [dirty, setDirty] = useState(false);

  const sid = session?.session_id;
  const landmarks = localLandmarks || frame?.landmarks;

  // Reset local state when frame changes
  useEffect(() => {
    setLocalLandmarks(null);
    setDirty(false);
  }, [frameIndex, sid]);

  const imgSrc = viewMode === 'annotated'
    ? `/api/frame/${sid}/${frameIndex}/annotated`
    : `/api/frame/${sid}/${frameIndex}/image`;

  // Get connections from config
  const connections = config?.connections || [];

  const drawCanvas = useCallback(() => {
    const canvas = canvasRef.current;
    const img = imgRef.current;
    if (!canvas || !img || !imgLoaded) return;

    const container = containerRef.current;
    const cw = container.clientWidth;
    const ch = container.clientHeight;

    // Fit image in container
    const scale = Math.min(cw / img.naturalWidth, ch / img.naturalHeight);
    const dw = img.naturalWidth * scale;
    const dh = img.naturalHeight * scale;
    const ox = (cw - dw) / 2;
    const oy = (ch - dh) / 2;

    canvas.width = cw;
    canvas.height = ch;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, cw, ch);

    // Don't draw markers in annotated or original mode
    if (viewMode !== 'markers' || !landmarks) return;

    const px = (lm) => {
      if (!lm || lm.visibility < 0.15) return null;
      return [ox + lm.x * dw, oy + lm.y * dh];
    };

    // Draw skeleton lines
    for (const conn of connections) {
      const a = px(landmarks[conn.from]);
      const b = px(landmarks[conn.to]);
      if (a && b) {
        ctx.beginPath();
        ctx.moveTo(a[0], a[1]);
        ctx.lineTo(b[0], b[1]);
        ctx.strokeStyle = COLORS[conn.group] || '#666';
        ctx.lineWidth = 2.5;
        ctx.stroke();
      }
    }

    // Spine line
    const ls = px(landmarks[11]), rs = px(landmarks[12]);
    const lh = px(landmarks[23]), rh = px(landmarks[24]);
    if (ls && rs && lh && rh) {
      const ms = [(ls[0]+rs[0])/2, (ls[1]+rs[1])/2];
      const mh = [(lh[0]+rh[0])/2, (lh[1]+rh[1])/2];
      ctx.beginPath();
      ctx.moveTo(ms[0], ms[1]);
      ctx.lineTo(mh[0], mh[1]);
      ctx.strokeStyle = COLORS.spine;
      ctx.lineWidth = 2.5;
      ctx.stroke();
    }

    // Plumb line from nose
    const nose = px(landmarks[0]);
    if (nose) {
      ctx.beginPath();
      ctx.moveTo(nose[0], 0);
      ctx.lineTo(nose[0], ch);
      ctx.strokeStyle = COLORS.plumb;
      ctx.lineWidth = 1;
      ctx.setLineDash([6, 4]);
      ctx.stroke();
      ctx.setLineDash([]);
    }

    // Draw joint markers
    const markerR = Math.max(5, dw * 0.008);
    for (const idx of SWING_LANDMARKS) {
      const pt = px(landmarks[idx]);
      if (!pt) continue;
      const group = JOINT_GROUPS[idx] || 'head';
      ctx.beginPath();
      ctx.arc(pt[0], pt[1], markerR, 0, Math.PI * 2);
      ctx.fillStyle = COLORS[group];
      ctx.fill();
      ctx.strokeStyle = '#fff';
      ctx.lineWidth = 1.5;
      ctx.stroke();
    }

    // Highlight dragged marker
    if (dragging !== null) {
      const pt = px(landmarks[dragging]);
      if (pt) {
        ctx.beginPath();
        ctx.arc(pt[0], pt[1], markerR + 4, 0, Math.PI * 2);
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 2;
        ctx.stroke();
      }
    }
  }, [imgLoaded, landmarks, viewMode, connections, dragging]);

  useEffect(() => { drawCanvas(); }, [drawCanvas]);

  // Mouse handlers for marker dragging
  const getImageCoords = useCallback((e) => {
    const canvas = canvasRef.current;
    const img = imgRef.current;
    const container = containerRef.current;
    if (!canvas || !img || !container) return null;

    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;

    const cw = container.clientWidth;
    const ch = container.clientHeight;
    const scale = Math.min(cw / img.naturalWidth, ch / img.naturalHeight);
    const dw = img.naturalWidth * scale;
    const dh = img.naturalHeight * scale;
    const ox = (cw - dw) / 2;
    const oy = (ch - dh) / 2;

    return { mx, my, ox, oy, dw, dh, scale };
  }, []);

  const handleMouseDown = useCallback((e) => {
    if (viewMode !== 'markers' || !landmarks) return;
    const coords = getImageCoords(e);
    if (!coords) return;

    const { mx, my, ox, oy, dw, dh } = coords;
    const hitR = Math.max(10, dw * 0.015);

    // Find closest landmark
    let closest = null;
    let closestDist = Infinity;
    for (const idx of SWING_LANDMARKS) {
      const lm = landmarks[idx];
      if (!lm || lm.visibility < 0.15) continue;
      const px = ox + lm.x * dw;
      const py = oy + lm.y * dh;
      const d = Math.hypot(mx - px, my - py);
      if (d < hitR && d < closestDist) {
        closestDist = d;
        closest = idx;
      }
    }
    if (closest !== null) {
      setDragging(closest);
      e.preventDefault();
    }
  }, [viewMode, landmarks, getImageCoords]);

  const handleMouseMove = useCallback((e) => {
    if (dragging === null || !landmarks) return;
    const coords = getImageCoords(e);
    if (!coords) return;

    const { mx, my, ox, oy, dw, dh } = coords;
    const nx = Math.max(0, Math.min(1, (mx - ox) / dw));
    const ny = Math.max(0, Math.min(1, (my - oy) / dh));

    const updated = landmarks.map((lm, i) =>
      i === dragging ? { ...lm, x: nx, y: ny } : lm
    );
    setLocalLandmarks(updated);
    setDirty(true);
  }, [dragging, landmarks, getImageCoords]);

  const handleMouseUp = useCallback(() => {
    setDragging(null);
  }, []);

  const handleSave = useCallback(async () => {
    if (!localLandmarks || !dirty) return;
    await onUpdateLandmarks(frameIndex, localLandmarks);
    setLocalLandmarks(null);
    setDirty(false);
  }, [localLandmarks, dirty, frameIndex, onUpdateLandmarks]);

  const handleReset = useCallback(() => {
    setLocalLandmarks(null);
    setDirty(false);
  }, []);

  return (
    <div style={{ flex: 1, position: 'relative', overflow: 'hidden', background: '#000' }}>
      <div ref={containerRef} style={{ width: '100%', height: '100%', position: 'relative' }}>
        <img
          ref={imgRef}
          src={imgSrc}
          alt=""
          onLoad={() => setImgLoaded(true)}
          style={{
            position: 'absolute', top: '50%', left: '50%',
            transform: 'translate(-50%, -50%)',
            maxWidth: '100%', maxHeight: '100%', objectFit: 'contain',
          }}
          key={`${sid}-${frameIndex}-${viewMode}`}
        />
        <canvas
          ref={canvasRef}
          style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', cursor: dragging !== null ? 'grabbing' : 'default' }}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        />
      </div>

      {/* Phase label */}
      {frame && (
        <div style={{
          position: 'absolute', top: 8, left: 8,
          background: 'rgba(0,0,0,0.7)', padding: '4px 12px', borderRadius: 6,
          fontSize: 14, fontWeight: 600,
        }}>
          {frameIndex + 1}. {frame.phase}
        </div>
      )}

      {/* Marker edit controls */}
      {viewMode === 'markers' && dirty && (
        <div style={{
          position: 'absolute', bottom: 12, left: '50%', transform: 'translateX(-50%)',
          display: 'flex', gap: 8,
        }}>
          <button className="primary" onClick={handleSave}>Save Changes</button>
          <button onClick={handleReset}>Reset</button>
        </div>
      )}

      {viewMode === 'markers' && !dirty && (
        <div style={{
          position: 'absolute', bottom: 12, left: '50%', transform: 'translateX(-50%)',
          background: 'rgba(0,0,0,0.6)', padding: '4px 12px', borderRadius: 6,
          fontSize: 12, color: 'var(--text-dim)',
        }}>
          Drag markers to adjust positions
        </div>
      )}
    </div>
  );
}
