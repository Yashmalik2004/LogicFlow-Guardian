import { useAuth } from '../app/hooks/useAuth';
import { useNavigate } from 'react-router-dom';

interface DashboardHeaderProps {
  onCreateProject: () => void;
}

function DashboardHeader({ onCreateProject }: DashboardHeaderProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate('/');
  }

  return (
    <header className="dashboard-header">
      <div className="dashboard-header-left">
        <div className="dashboard-logo">
          <span className="dashboard-logo-icon">🛡️</span>
          <span className="dashboard-logo-text">LogicFlow Guardian</span>
        </div>
        {user && (
          <span className="dashboard-welcome">
            Welcome, <strong>{user.name}</strong>
          </span>
        )}
      </div>
      <div className="dashboard-header-right">
        <button
          id="create-project-header-button"
          className="btn-primary"
          onClick={onCreateProject}
        >
          + New Project
        </button>
        <button
          id="logout-button"
          className="btn-logout"
          onClick={handleLogout}
        >
          Logout
        </button>
      </div>
    </header>
  );
}

export default DashboardHeader;
