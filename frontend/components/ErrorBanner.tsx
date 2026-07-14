interface ErrorBannerProps {
  message: string;
  onDismiss?: () => void;
}

function ErrorBanner({ message, onDismiss }: ErrorBannerProps) {
  return (
    <div className="error-banner" role="alert">
      <span>{message}</span>
      {onDismiss && (
        <button
          id="error-banner-dismiss"
          className="error-banner-dismiss"
          onClick={onDismiss}
          aria-label="Dismiss error"
        >
          &times;
        </button>
      )}
    </div>
  );
}

export default ErrorBanner;
