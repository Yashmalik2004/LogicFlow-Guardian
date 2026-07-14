import { useState, FormEvent, useEffect } from 'react';
import { Project, UpdateProjectPayload } from '../lib/projectService';

interface EditProjectModalProps {
  project: Project;
  onConfirm: (projectId: number, payload: UpdateProjectPayload) => Promise<void>;
  onCancel: () => void;
}

interface FormState {
  repoName: string;
  repoUrl: string;
  branch: string;
  description: string;
}

interface FormErrors {
  repoName?: string;
  repoUrl?: string;
}

function EditProjectModal({ project, onConfirm, onCancel }: EditProjectModalProps) {
  const [form, setForm] = useState<FormState>({
    repoName: project.repoName,
    repoUrl: project.repoUrl ?? '',
    branch: project.branch,
    description: project.description ?? '',
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [submitting, setSubmitting] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  // Sync form if the selected project changes
  useEffect(() => {
    setForm({
      repoName: project.repoName,
      repoUrl: project.repoUrl ?? '',
      branch: project.branch,
      description: project.description ?? '',
    });
    setErrors({});
    setApiError(null);
  }, [project.projectId]);

  function validate(): FormErrors {
    const errs: FormErrors = {};
    if (!form.repoName.trim()) {
      errs.repoName = 'Project name is required.';
    } else if (form.repoName.trim().length > 100) {
      errs.repoName = 'Project name must not exceed 100 characters.';
    }
    if (form.repoUrl.trim()) {
      try {
        new URL(form.repoUrl.trim());
      } catch {
        errs.repoUrl = 'Please enter a valid URL.';
      }
    }
    return errs;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setApiError(null);

    const errs = validate();
    setErrors(errs);
    if (Object.keys(errs).length > 0) return;

    const payload: UpdateProjectPayload = {
      repoName: form.repoName.trim(),
      repoUrl: form.repoUrl.trim() || null,
      branch: form.branch.trim() || 'main',
      description: form.description.trim() || null,
    };

    setSubmitting(true);
    try {
      await onConfirm(project.projectId, payload);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : 'Failed to update project. Please try again.';
      setApiError(msg);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="edit-modal-title">
      <div className="modal-box">
        <div className="modal-header">
          <h2 id="edit-modal-title" className="modal-title">Edit Project</h2>
          <button
            id="edit-modal-close"
            className="modal-close"
            onClick={onCancel}
            aria-label="Close"
          >
            &times;
          </button>
        </div>

        {apiError && <div className="form-api-error">{apiError}</div>}

        <form className="modal-form" onSubmit={handleSubmit} noValidate>
          {/* Project Name */}
          <div className="form-group">
            <label className="form-label" htmlFor="edit-repo-name">
              Project Name <span className="required">*</span>
            </label>
            <input
              id="edit-repo-name"
              className={`form-input ${errors.repoName ? 'form-input-error' : ''}`}
              type="text"
              value={form.repoName}
              onChange={(e) => setForm({ ...form, repoName: e.target.value })}
              maxLength={100}
            />
            {errors.repoName && <span className="field-error">{errors.repoName}</span>}
          </div>

          {/* Repository Type — read-only, cannot be changed */}
          <div className="form-group">
            <label className="form-label">Repository Type</label>
            <input
              className="form-input form-input-readonly"
              type="text"
              value={project.repositoryType === 'github' ? 'GitHub' : 'ZIP'}
              readOnly
            />
            <span className="field-hint">Repository type cannot be changed.</span>
          </div>

          {/* GitHub URL */}
          <div className="form-group">
            <label className="form-label" htmlFor="edit-repo-url">
              GitHub URL
            </label>
            <input
              id="edit-repo-url"
              className={`form-input ${errors.repoUrl ? 'form-input-error' : ''}`}
              type="url"
              placeholder="https://github.com/user/repo"
              value={form.repoUrl}
              onChange={(e) => setForm({ ...form, repoUrl: e.target.value })}
            />
            {errors.repoUrl && <span className="field-error">{errors.repoUrl}</span>}
          </div>

          {/* Default Branch */}
          <div className="form-group">
            <label className="form-label" htmlFor="edit-branch">
              Default Branch
            </label>
            <input
              id="edit-branch"
              className="form-input"
              type="text"
              value={form.branch}
              onChange={(e) => setForm({ ...form, branch: e.target.value })}
            />
          </div>

          {/* Description */}
          <div className="form-group">
            <label className="form-label" htmlFor="edit-description">
              Description
            </label>
            <textarea
              id="edit-description"
              className="form-input form-textarea"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              rows={3}
            />
          </div>

          <div className="modal-actions">
            <button
              id="edit-modal-cancel"
              type="button"
              className="btn-secondary"
              onClick={onCancel}
              disabled={submitting}
            >
              Cancel
            </button>
            <button
              id="edit-modal-submit"
              type="submit"
              className="btn-primary"
              disabled={submitting}
            >
              {submitting ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default EditProjectModal;
