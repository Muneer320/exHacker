/**
 * exHacker API Service Client
 * Thin layer over the FastAPI backend.
 * G racefully falls back to mock data when backend is offline.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// ── Types ──────────────────────────────────────────────────────────────────

export interface Project {
  id: string;
  name: string;
  description: string | null;
  idea: string;
  status: 'draft' | 'processing' | 'ready' | 'archived';
  created_at: string;
  updated_at: string;
}

export interface CreateProjectPayload {
  idea: string;
  name?: string;
  description?: string;
}

export interface UpdateProjectPayload {
  name?: string;
  description?: string;
  idea?: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  error?: {
    code: string;
    message: string;
    detail?: Record<string, unknown>;
    suggestion?: string;
  };
}

// ── Client ─────────────────────────────────────────────────────────────────

async function request<T>(
  endpoint: string,
  options?: RequestInit,
): Promise<ApiResponse<T>> {
  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options?.headers || {}),
      },
    });

    const body = await res.json();

    if (!res.ok) {
      console.error(`[exHacker API] ${endpoint} failed:`, body);
    }

    return body as ApiResponse<T>;
  } catch (err) {
    console.error(`[exHacker API] Network error on ${endpoint}:`, err);
    return {
      success: false,
      data: null as unknown as T,
      error: {
        code: 'NETWORK_ERROR',
        message: 'Could not reach the backend.',
        suggestion: 'Make sure the backend is running on port 8000.',
      },
    };
  }
}

// ── Mock Data (for development without backend) ───────────────────────────

const MOCK_PROJECTS: Project[] = [
  {
    id: 'mock-001',
    name: 'Student Budget AI',
    description: null,
    idea: 'A mobile app that helps students budget their money using AI',
    status: 'draft',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
];

let mockIdCounter = 1;

function createMockProject(payload: CreateProjectPayload): Project {
  const project: Project = {
    id: `mock-${String(++mockIdCounter).padStart(3, '0')}`,
    name: payload.name || payload.idea.slice(0, 60) + (payload.idea.length > 60 ? '...' : ''),
    description: payload.description || null,
    idea: payload.idea,
    status: 'draft',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };
  MOCK_PROJECTS.unshift(project);
  return project;
}

// ── Endpoints ──────────────────────────────────────────────────────────────

export async function createProject(
  payload: CreateProjectPayload,
): Promise<ApiResponse<{ project: Project }>> {
  const res = await request<{ id: string; name: string; description: string | null; idea: string; status: string; created_at: string; updated_at: string }>(
    '/projects',
    { method: 'POST', body: JSON.stringify(payload) },
  );

  if (res.success) {
    return {
      ...res,
      data: { project: res.data as unknown as Project },
    };
  }

  // Fallback to mock
  console.warn('[exHacker API] Using mock project creation');
  const mockProject = createMockProject(payload);
  return {
    success: true,
    data: { project: mockProject },
    message: 'Mock project created.',
  };
}

export async function listProjects(): Promise<ApiResponse<{ projects: Project[] }>> {
  const res = await request<{ projects: Project[] }>('/projects');

  if (res.success) {
    return res;
  }

  // Fallback to mock
  console.warn('[exHacker API] Using mock project list');
  return {
    success: true,
    data: { projects: MOCK_PROJECTS },
    message: 'Mock projects (backend offline).',
  };
}

export async function getProject(
  id: string,
): Promise<ApiResponse<{ project: Project }>> {
  const res = await request<Project>('/projects/' + id);

  if (res.success) {
    return { ...res, data: { project: res.data as unknown as Project } };
  }

  // Fallback to mock
  const mock = MOCK_PROJECTS.find((p) => p.id === id);
  if (mock) {
    return { success: true, data: { project: mock } };
  }

  return {
    success: false,
    data: null as unknown as { project: Project },
    error: { code: 'PROJECT_NOT_FOUND', message: 'Project not found.' },
  };
}

export async function deleteProject(id: string): Promise<ApiResponse<null>> {
  return request<null>('/projects/' + id, { method: 'DELETE' });
}

export async function transitionProject(
  id: string,
  transition: string,
): Promise<ApiResponse<{ id: string; status: string; message: string }>> {
  return request<{ id: string; status: string; message: string }>(
    '/projects/' + id + '/transition',
    { method: 'POST', body: JSON.stringify({ transition }) },
  );
}
