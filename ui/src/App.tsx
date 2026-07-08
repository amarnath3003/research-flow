import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Config from './pages/Config';
import Research from './pages/Research';
import Explorer from './pages/Explorer';
import Results from './pages/Results';
import ProjectsPage from './pages/ProjectsPage';
import { ProjectProvider, useProjects } from './context/ProjectContext';

function AppRoutes() {
  const { activeProject } = useProjects();

  return (
    <div className="app-shell">
      <Sidebar />
      <main className="main-content">
        <Routes>
          <Route path="/projects" element={<ProjectsPage />} />
          <Route path="/:pid/dashboard" element={<Dashboard />} />
          <Route path="/:pid/config" element={<Config />} />
          <Route path="/:pid/research" element={<Research />} />
          <Route path="/:pid/workflow" element={<Navigate to="./research" replace />} />
          <Route path="/:pid/explorer" element={<Explorer />} />
          <Route path="/:pid/results" element={<Results />} />
          <Route path="*" element={
            activeProject
              ? <Navigate to={`/${activeProject.id}/dashboard`} replace />
              : <Navigate to="/projects" replace />
          } />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <Router>
      <ProjectProvider>
        <AppRoutes />
      </ProjectProvider>
    </Router>
  );
}

export default App;
