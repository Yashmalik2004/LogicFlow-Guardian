import { Project } from '../lib/projectService';
import ProjectCard from './ProjectCard';
import EmptyState from './EmptyState';

interface ProjectListProps {
  projects: Project[];
  onEdit: (project: Project) => void;
  onDelete: (project: Project) => void;
  onCreateProject: () => void;
}

function ProjectList({ projects, onEdit, onDelete, onCreateProject }: ProjectListProps) {
  if (projects.length === 0) {
    return <EmptyState onCreateProject={onCreateProject} />;
  }

  return (
    <div className="project-list">
      {projects.map((project) => (
        <ProjectCard
          key={project.projectId}
          project={project}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}

export default ProjectList;
