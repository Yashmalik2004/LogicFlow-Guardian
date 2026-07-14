interface EmptyStateProps {
  onCreateProject: () => void;
}

function EmptyState({ onCreateProject }: EmptyStateProps) {
  return (
    <div className="empty-state">
      <div className="empty-state-icon" aria-hidden="true">📂</div>
      <h2 className="empty-state-title">No projects found.</h2>
      <p className="empty-state-message">
        Create your first project to start analyzing business logic vulnerabilities.
      </p>
      <button
        id="empty-state-create-button"
        className="btn-primary"
        onClick={onCreateProject}
      >
        + Create Project
      </button>
    </div>
  );
}

export default EmptyState;
