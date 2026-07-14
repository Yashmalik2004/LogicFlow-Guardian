import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000';

const api = axios.create({ baseURL: API_BASE_URL });

// Attach JWT to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

// ---- Types ----

export interface Project {
  projectId: number;
  repoName: string;
  repoUrl: string | null;
  branch: string;
  description: string | null;
  repositoryType: 'github' | 'zip';
  status: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateProjectPayload {
  repoName: string;
  repositoryType: 'github' | 'zip';
  repoUrl?: string | null;
  branch?: string;
  description?: string | null;
}

export interface UpdateProjectPayload {
  repoName?: string;
  repoUrl?: string | null;
  branch?: string;
  description?: string | null;
}

// ---- Service Functions ----

export async function getProjects(): Promise<Project[]> {
  const response = await api.get<{ success: boolean; data: Project[] }>('/api/projects');
  return response.data.data;
}

export async function createProject(payload: CreateProjectPayload): Promise<{ projectId: number }> {
  const response = await api.post<{ success: boolean; data: { projectId: number } }>(
    '/api/projects',
    payload
  );
  return response.data.data;
}

export async function updateProject(
  projectId: number,
  payload: UpdateProjectPayload
): Promise<Project> {
  const response = await api.put<{ success: boolean; data: Project }>(
    `/api/projects/${projectId}`,
    payload
  );
  return response.data.data;
}

export async function deleteProject(projectId: number): Promise<void> {
  await api.delete(`/api/projects/${projectId}`);
}
