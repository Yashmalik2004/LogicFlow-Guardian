import { ProjectModel, CreateProjectInput, UpdateProjectInput, Project } from '../models/project.model';

export class ProjectService {
  /**
   * Create a new project for the authenticated user.
   */
  static async createProject(
    userId: number,
    body: {
      repoName: string;
      repoUrl?: string | null;
      branch?: string;
      description?: string | null;
      repositoryType: 'github' | 'zip';
    }
  ): Promise<Project> {
    const input: CreateProjectInput = {
      user_id: userId,
      repo_name: body.repoName,
      repo_url: body.repoUrl ?? null,
      branch: body.branch ?? 'main',
      description: body.description ?? null,
      repository_type: body.repositoryType,
    };
    return ProjectModel.create(input);
  }

  /**
   * List all active projects for the authenticated user.
   */
  static async listProjects(userId: number): Promise<Project[]> {
    return ProjectModel.findAllByUser(userId);
  }

  /**
   * Get a single project, enforcing ownership.
   * Returns null if not found, 'forbidden' if not owner.
   */
  static async getProject(
    projectId: number,
    userId: number
  ): Promise<Project | null | 'forbidden'> {
    const project = await ProjectModel.findById(projectId);
    if (!project) return null;
    if (project.user_id !== userId) return 'forbidden';
    return project;
  }

  /**
   * Update a project's editable fields, enforcing ownership.
   * Returns null if not found, 'forbidden' if not owner.
   */
  static async updateProject(
    projectId: number,
    userId: number,
    input: UpdateProjectInput
  ): Promise<Project | null | 'forbidden'> {
    const project = await ProjectModel.findById(projectId);
    if (!project) return null;
    if (project.user_id !== userId) return 'forbidden';
    return ProjectModel.update(projectId, input);
  }

  /**
   * Soft-delete a project, enforcing ownership.
   * Returns false if not found, 'forbidden' if not owner.
   */
  static async deleteProject(
    projectId: number,
    userId: number
  ): Promise<boolean | 'forbidden'> {
    const project = await ProjectModel.findById(projectId);
    if (!project) return false;
    if (project.user_id !== userId) return 'forbidden';
    return ProjectModel.softDelete(projectId);
  }
}
