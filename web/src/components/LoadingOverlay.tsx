import './LoadingOverlay.css';

interface LoadingOverlayProps {
  loaded: number;
  total: number;
}

export function LoadingOverlay({ loaded, total }: LoadingOverlayProps) {
  const percent = Math.round((loaded / total) * 100);

  return (
    <div className="loading-overlay">
      <div className="loading-content">
        <h1>Half of America</h1>
        <p>Loading map data...</p>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${percent}%` }} />
        </div>
        <p className="progress-text">{loaded} / {total} files</p>
      </div>
    </div>
  );
}
