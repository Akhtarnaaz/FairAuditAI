import { useAuth } from '../../context/AuthContext';
import { LogOut } from 'lucide-react';

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <header className="navbar">
      <div />
      <div className="navbar-right">
        <div className="navbar-user">
          <div className="navbar-avatar">
            {user?.name?.[0]?.toUpperCase() || 'U'}
          </div>
          <div className="navbar-user-info">
            <span className="navbar-user-name">{user?.name || 'User'}</span>
            <span className="navbar-user-role">{user?.role || 'user'}</span>
          </div>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={logout} id="logout-btn">
          <LogOut size={14} /> Logout
        </button>
      </div>
    </header>
  );
}
