interface LoadingSpinnerProps {
  message?: string;
}

function LoadingSpinner({ message = 'Loading...' }: LoadingSpinnerProps) {
  return (
    <div className="loading-screen" role="status" aria-live="polite">
      <div className="spinner-container">
        <div className="spinner" aria-hidden="true" />
        <span>{message}</span>
      </div>
    </div>
  );
}

export default LoadingSpinner;
