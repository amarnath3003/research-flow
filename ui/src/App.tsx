import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Config from './pages/Config';
import Workflow from './pages/Workflow';
import Explorer from './pages/Explorer';
import Results from './pages/Results';

function App() {
  return (
    <Router>
      <Sidebar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/config" element={<Config />} />
          <Route path="/workflow" element={<Workflow />} />
          <Route path="/explorer" element={<Explorer />} />
          <Route path="/results" element={<Results />} />
        </Routes>
      </main>
    </Router>
  );
}

export default App;
