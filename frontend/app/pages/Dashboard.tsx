import { useAuth } from '../hooks/useAuth';
import { useNavigate } from 'react-router-dom';
import '../../styles/auth.css';

function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate('/');
  }

  return (
    <div className="dashboard-page">
      <div className="dashboard-card">
        <h1 className="dashboard-title">Welcome</h1>
        <p className="dashboard-message">Logged in successfully.</p>
        {user && (
          <p className="dashboard-user">
            Hello, <strong>{user.name}</strong>
          </p>
        )}
        <button id="logout-button" className="logout-button" onClick={handleLogout}>
          Logout
        </button>
      </div>
    </div>
  );
}

export default Dashboard;
