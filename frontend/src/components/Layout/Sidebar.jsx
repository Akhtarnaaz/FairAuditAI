import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  LayoutDashboard, Upload, Settings, BarChart3,
  FileText, Shield, AlertTriangle, Wrench,
} from 'lucide-react';

export default function Sidebar() {
  const { isAdmin } = useAuth();

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <div className="logo-icon"><Shield size={20} /></div>
          <h2>FairAudit AI</h2>
        </div>
      </div>

      <nav className="sidebar-nav">
        <NavLink to="/app" end className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
          <LayoutDashboard size={18} /> Dashboard
        </NavLink>

        {isAdmin && (
          <>
            <div className="sidebar-section">Audit Workflow</div>
            <NavLink to="/app/upload/model" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
              <Upload size={18} /> Upload Model
            </NavLink>
            <NavLink to="/app/upload/dataset" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
              <Upload size={18} /> Upload Dataset
            </NavLink>
            <NavLink to="/app/audit/configure" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
              <Settings size={18} /> Configure Audit
            </NavLink>
          </>
        )}

        <div className="sidebar-section">Results</div>
        <NavLink to="/app/reports" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
          <FileText size={18} /> Reports
        </NavLink>
      </nav>
    </aside>
  );
}
