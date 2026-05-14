import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { listProjects, createProject as apiCreateProject } from '../api';

interface ProjectInfo {
  id: string;
  name: string;
  description: string;
  createdAt: string;
  status: string;
  isDefault: boolean;
}

interface ProjectContextType {
  projects: ProjectInfo[];
  activeProject: ProjectInfo | null;
  loading: boolean;
  setActive: (p: ProjectInfo) => void;
  refreshProjects: () => Promise<void>;
  createProject: (name: string, description: string) => Promise<ProjectInfo>;
}

const ProjectContext = createContext<ProjectContextType>(null!);

export function ProjectProvider({ children }: { children: ReactNode }) {
  const [projects, setProjects] = useState<ProjectInfo[]>([]);
  const [activeProject, setActiveProject] = useState<ProjectInfo | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = async () => {
    try {
      const data = await listProjects();
      setProjects(data);
      setLoading(false);
    } catch { setLoading(false); }
  };

  useEffect(() => { refresh(); }, []);

  const setActive = (p: ProjectInfo) => {
    setActiveProject(p);
    localStorage.setItem('activeProjectId', p.id);
  };

  // Auto-select default or last-used project
  useEffect(() => {
    if (projects.length === 0) {
      setActiveProject(null);
      localStorage.removeItem('activeProjectId');
      return;
    }
    const lastId = localStorage.getItem('activeProjectId');
    const last = projects.find((p) => p.id === lastId);
    if (last) { setActive(last); return; }
    const def = projects.find((p) => p.isDefault);
    if (def) { setActive(def); return; }
    setActive(projects[0]);
  }, [projects.length]);

  const createProject = async (name: string, description: string) => {
    const p = await apiCreateProject(name, description);
    await refresh();
    return p;
  };

  return (
    <ProjectContext.Provider value={{ projects, activeProject, loading, setActive, refreshProjects: refresh, createProject }}>
      {children}
    </ProjectContext.Provider>
  );
}

export const useProjects = () => useContext(ProjectContext);
