import { useState } from 'react';
import { Project } from '../lib/projectService';

interface DeleteProjectModalProps {
  project: Project;
  onConfirm: (projectId: number) => Promise<void>;
  onCancel: () => void;
}

function DeleteProjectModal({ project, onConfirm, onCancel }: DeleteProjectModalProps) {
  const [deleting, setDeleting] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  async function handleDelete() {
    setApiError(null);
    setDeleting(true);
    try {
      await onConfirm(project.projectId);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : 'Failed to delete project. Please try again.';
      setApiError(msg);
      setDeleting(false);
    }
  }

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="delete-modal-title">
      <div className="modal-box modal-box-sm">
        <div className="modal-header">
          <h2 id="delete-modal-title" className="modal-title modal-title-danger">
            Delete Project
          </h2>
          <button
            id="delete-modal-close"
            className="modal-close"
            onClick={onCancel}
            aria-label="Close"
            disabled={deleting}
          >
            &times;
          </button>
        </div>

        <div className="delete-modal-body">
          <div className="delete-warning-icon" aria-hidden="true">⚠️</div>
          <p className="delete-modal-message">
            Delete project <strong>"{project.repoName}"</strong>?
          </p>
          <p className="delete-modal-warning">This action cannot be undone.</p>
          {apiError && <div className="form-api-error">{apiError}</div>}
        </div>

        <div className="modal-actions">
          <button
            id="delete-modal-cancel"
            type="button"
            className="btn-secondary"
            onClick={onCancel}
            disabled={deleting}
          >
            Cancel
          </button>
          <button
            id="delete-modal-confirm"
            type="button"
            className="btn-danger"
            onClick={handleDelete}
            disabled={deleting}
          >
            {deleting ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default DeleteProjectModal;
