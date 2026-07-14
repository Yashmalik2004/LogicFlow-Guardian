import { useState, useEffect, useCallback } from 'react';
import DashboardHeader from '../../components/DashboardHeader';
import ProjectList from '../../components/ProjectList';
import CreateProjectModal from '../../components/CreateProjectModal';
import EditProjectModal from '../../components/EditProjectModal';
import DeleteProjectModal from '../../components/DeleteProjectModal';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorBanner from '../../components/ErrorBanner';
import {
  Project,
  CreateProjectPayload,
  UpdateProjectPayload,
  getProjects,
  createProject,
  updateProject,
  deleteProject,
} from '../../lib/projectService';
import '../../styles/dashboard.css';

type ModalState =
  | { type: 'none' }
  | { type: 'create' }
  | { type: 'edit'; project: Project }
  | { type: 'delete'; project: Project };

function Dashboard() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modal, setModal] = useState<ModalState>({ type: 'none' });

  // ---- Data Fetching ----

  const fetchProjects = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getProjects();
      setProjects(data);
    } catch {
      setError('Failed to load projects. Please refresh the page.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  // ---- Modal Handlers ----

  function openCreateModal() {
    setModal({ type: 'create' });
  }

  function openEditModal(project: Project) {
    setModal({ type: 'edit', project });
  }

  function openDeleteModal(project: Project) {
    setModal({ type: 'delete', project });
  }

  function closeModal() {
    setModal({ type: 'none' });
  }

  // ---- CRUD Operations ----

  async function handleCreateProject(payload: CreateProjectPayload) {
    await createProject(payload);
    closeModal();
    await fetchProjects();
  }

  async function handleUpdateProject(projectId: number, payload: UpdateProjectPayload) {
    await updateProject(projectId, payload);
    closeModal();
    await fetchProjects();
  }

  async function handleDeleteProject(projectId: number) {
    await deleteProject(projectId);
    closeModal();
    await fetchProjects();
  }

  // ---- Render ----

  return (
    <div className="dashboard-layout">
      <DashboardHeader onCreateProject={openCreateModal} />

      <main className="dashboard-main">
        <div className="dashboard-content">
          <div className="dashboard-section-header">
            <h1 className="dashboard-section-title">Your Projects</h1>
            <span className="project-count">
              {!loading && `${projects.length} project${projects.length !== 1 ? 's' : ''}`}
            </span>
          </div>

          {error && (
            <ErrorBanner message={error} onDismiss={() => setError(null)} />
          )}

          {loading ? (
            <LoadingSpinner message="Loading projects..." />
          ) : (
            <ProjectList
              projects={projects}
              onEdit={openEditModal}
              onDelete={openDeleteModal}
              onCreateProject={openCreateModal}
            />
          )}
        </div>
      </main>

      {/* Modals */}
      {modal.type === 'create' && (
        <CreateProjectModal onConfirm={handleCreateProject} onCancel={closeModal} />
      )}

      {modal.type === 'edit' && (
        <EditProjectModal
          project={modal.project}
          onConfirm={handleUpdateProject}
          onCancel={closeModal}
        />
      )}

      {modal.type === 'delete' && (
        <DeleteProjectModal
          project={modal.project}
          onConfirm={handleDeleteProject}
          onCancel={closeModal}
        />
      )}
    </div>
  );
}

export default Dashboard;
