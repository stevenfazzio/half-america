import './ErrorOverlay.css';

interface ErrorOverlayProps {
  message: string;
  onRetry: () => void;
}

export function ErrorOverlay({ message, onRetry }: ErrorOverlayProps) {
  return (
    <div className="error-overlay">
      <div className="error-content">
        <h1>Error Loading Data</h1>
        <p>{message}</p>
        <button onClick={onRetry} className="retry-button">
          Try Again
        </button>
      </div>
    </div>
  );
}
