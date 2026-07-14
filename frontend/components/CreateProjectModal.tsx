import { useState, FormEvent } from 'react';
import { CreateProjectPayload } from '../lib/projectService';

interface CreateProjectModalProps {
  onConfirm: (payload: CreateProjectPayload) => Promise<void>;
  onCancel: () => void;
}

interface FormState {
  repoName: string;
  repositoryType: 'github' | 'zip';
  repoUrl: string;
  branch: string;
  description: string;
}

interface FormErrors {
  repoName?: string;
  repositoryType?: string;
  repoUrl?: string;
}

function CreateProjectModal({ onConfirm, onCancel }: CreateProjectModalProps) {
  const [form, setForm] = useState<FormState>({
    repoName: '',
    repositoryType: 'github',
    repoUrl: '',
    branch: 'main',
    description: '',
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [submitting, setSubmitting] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  function validate(): FormErrors {
    const errs: FormErrors = {};
    if (!form.repoName.trim()) {
      errs.repoName = 'Project name is required.';
    } else if (form.repoName.trim().length > 100) {
      errs.repoName = 'Project name must not exceed 100 characters.';
    }
    if (!form.repositoryType) {
      errs.repositoryType = 'Repository type is required.';
    }
    if (form.repositoryType === 'github' && form.repoUrl.trim()) {
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

    const payload: CreateProjectPayload = {
      repoName: form.repoName.trim(),
      repositoryType: form.repositoryType,
      repoUrl: form.repoUrl.trim() || null,
      branch: form.branch.trim() || 'main',
      description: form.description.trim() || null,
    };

    setSubmitting(true);
    try {
      await onConfirm(payload);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : 'Failed to create project. Please try again.';
      setApiError(msg);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="create-modal-title">
      <div className="modal-box">
        <div className="modal-header">
          <h2 id="create-modal-title" className="modal-title">Create New Project</h2>
          <button
            id="create-modal-close"
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
            <label className="form-label" htmlFor="create-repo-name">
              Project Name <span className="required">*</span>
            </label>
            <input
              id="create-repo-name"
              className={`form-input ${errors.repoName ? 'form-input-error' : ''}`}
              type="text"
              placeholder="e.g. Bank API"
              value={form.repoName}
              onChange={(e) => setForm({ ...form, repoName: e.target.value })}
              maxLength={100}
            />
            {errors.repoName && <span className="field-error">{errors.repoName}</span>}
          </div>

          {/* Repository Type */}
          <div className="form-group">
            <label className="form-label" htmlFor="create-repo-type">
              Repository Type <span className="required">*</span>
            </label>
            <select
              id="create-repo-type"
              className={`form-input ${errors.repositoryType ? 'form-input-error' : ''}`}
              value={form.repositoryType}
              onChange={(e) =>
                setForm({ ...form, repositoryType: e.target.value as 'github' | 'zip' })
              }
            >
              <option value="github">GitHub</option>
              <option value="zip">ZIP</option>
            </select>
            {errors.repositoryType && (
              <span className="field-error">{errors.repositoryType}</span>
            )}
          </div>

          {/* GitHub URL */}
          {form.repositoryType === 'github' && (
            <div className="form-group">
              <label className="form-label" htmlFor="create-repo-url">
                GitHub URL
              </label>
              <input
                id="create-repo-url"
                className={`form-input ${errors.repoUrl ? 'form-input-error' : ''}`}
                type="url"
                placeholder="https://github.com/user/repo"
                value={form.repoUrl}
                onChange={(e) => setForm({ ...form, repoUrl: e.target.value })}
              />
              {errors.repoUrl && <span className="field-error">{errors.repoUrl}</span>}
            </div>
          )}

          {/* Default Branch */}
          <div className="form-group">
            <label className="form-label" htmlFor="create-branch">
              Default Branch
            </label>
            <input
              id="create-branch"
              className="form-input"
              type="text"
              placeholder="main"
              value={form.branch}
              onChange={(e) => setForm({ ...form, branch: e.target.value })}
            />
          </div>

          {/* Description */}
          <div className="form-group">
            <label className="form-label" htmlFor="create-description">
              Description
            </label>
            <textarea
              id="create-description"
              className="form-input form-textarea"
              placeholder="Optional project description"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              rows={3}
            />
          </div>

          <div className="modal-actions">
            <button
              id="create-modal-cancel"
              type="button"
              className="btn-secondary"
              onClick={onCancel}
              disabled={submitting}
            >
              Cancel
            </button>
            <button
              id="create-modal-submit"
              type="submit"
              className="btn-primary"
              disabled={submitting}
            >
              {submitting ? 'Creating...' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateProjectModal;
