import { Project } from '../lib/projectService';

interface ProjectCardProps {
  project: Project;
  onEdit: (project: Project) => void;
  onDelete: (project: Project) => void;
}

const TYPE_LABELS: Record<string, string> = {
  github: 'GitHub',
  zip: 'ZIP',
};

const STATUS_CLASSES: Record<string, string> = {
  ACTIVE: 'status-active',
  DELETED: 'status-deleted',
};

function ProjectCard({ project, onEdit, onDelete }: ProjectCardProps) {
  return (
    <div className="project-card" data-project-id={project.projectId}>
      <div className="project-card-header">
        <div className="project-card-type-badge">
          {TYPE_LABELS[project.repositoryType] ?? project.repositoryType}
        </div>
        <span className={`project-status-badge ${STATUS_CLASSES[project.status] ?? ''}`}>
          {project.status}
        </span>
      </div>

      <h3 className="project-card-name">{project.repoName}</h3>

      {project.repoUrl && (
        <a
          className="project-card-url"
          href={project.repoUrl}
          target="_blank"
          rel="noopener noreferrer"
          title={project.repoUrl}
        >
          {project.repoUrl}
        </a>
      )}

      {project.description && (
        <p className="project-card-description">{project.description}</p>
      )}

      <div className="project-card-meta">
        <span className="project-card-branch">🌿 {project.branch}</span>
        <span className="project-card-date">
          {new Date(project.createdAt).toLocaleDateString()}
        </span>
      </div>

      <div className="project-card-actions">
        <button
          id={`edit-project-${project.projectId}`}
          className="btn-secondary"
          onClick={() => onEdit(project)}
        >
          Edit
        </button>
        <button
          id={`delete-project-${project.projectId}`}
          className="btn-danger"
          onClick={() => onDelete(project)}
        >
          Delete
        </button>
      </div>
    </div>
  );
}

export default ProjectCard;
