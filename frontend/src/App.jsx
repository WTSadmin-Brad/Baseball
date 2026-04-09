import { useState, useEffect } from 'react';
import './index.css';
import useSession from './hooks/useSession';
import UploadPanel from './components/UploadPanel';
import FrameCarousel from './components/FrameCarousel';
import FrameViewer from './components/FrameViewer';
import MetricsPanel from './components/MetricsPanel';
import MetricsChart from './components/MetricsChart';
import VideoFrameSelector from './components/VideoFrameSelector';

function App() {
  const {
    session, loading, error, config,
    activeFrame, setActiveFrame, currentFrame,
    loadConfig, uploadImages, uploadVideo,
    selectVideoFrames, updateLandmarks,
  } = useSession();

  const [viewMode, setViewMode] = useState('annotated'); // 'original' | 'annotated' | 'markers'
  const [showChart, setShowChart] = useState(false);

  useEffect(() => { loadConfig(); }, [loadConfig]);

  // No session yet — show upload
  if (!session) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', gap: 24 }}>
        <h1 style={{ fontSize: 28, fontWeight: 600, letterSpacing: '-0.5px' }}>Swing Analysis</h1>
        <p style={{ color: 'var(--text-dim)', maxWidth: 500, textAlign: 'center' }}>
          Upload swing sequence images or a video to get started with pose detection and swing mechanics analysis.
        </p>
        <UploadPanel onUploadImages={uploadImages} onUploadVideo={uploadVideo} loading={loading} />
        {error && <p style={{ color: 'var(--danger)' }}>{error}</p>}
      </div>
    );
  }

  // Video mode — selecting frames
  if (session.mode === 'video_select') {
    return (
      <VideoFrameSelector
        session={session}
        onConfirm={(indices) => selectVideoFrames(session.session_id, indices)}
        loading={loading}
      />
    );
  }

  // Main analysis view
  const frames = session.frames || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Header */}
      <header style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '8px 16px', borderBottom: '1px solid var(--border)', background: 'var(--surface)',
        flexShrink: 0,
      }}>
        <h1 style={{ fontSize: 18, fontWeight: 600 }}>Swing Analysis</h1>
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={() => setViewMode('annotated')} className={viewMode === 'annotated' ? 'primary' : ''}>
            Annotated
          </button>
          <button onClick={() => setViewMode('markers')} className={viewMode === 'markers' ? 'primary' : ''}>
            Markers
          </button>
          <button onClick={() => setViewMode('original')} className={viewMode === 'original' ? 'primary' : ''}>
            Original
          </button>
          <span style={{ width: 1, background: 'var(--border)' }} />
          <button onClick={() => setShowChart(v => !v)} className={showChart ? 'primary' : ''}>
            Chart
          </button>
        </div>
      </header>

      {/* Main content */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Left: Frame viewer */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <FrameViewer
            session={session}
            frame={currentFrame}
            frameIndex={activeFrame}
            viewMode={viewMode}
            config={config}
            onUpdateLandmarks={updateLandmarks}
          />
          <FrameCarousel
            frames={frames}
            activeFrame={activeFrame}
            onSelect={setActiveFrame}
            sessionId={session.session_id}
          />
        </div>

        {/* Right: Metrics */}
        <div style={{
          width: 320, borderLeft: '1px solid var(--border)', background: 'var(--surface)',
          overflow: 'auto', flexShrink: 0,
        }}>
          <MetricsPanel frame={currentFrame} frameIndex={activeFrame} />
          {showChart && <MetricsChart frames={frames} activeFrame={activeFrame} />}
        </div>
      </div>

      {loading && (
        <div style={{
          position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 100, fontSize: 18,
        }}>
          Processing...
        </div>
      )}
    </div>
  );
}

export default App;
