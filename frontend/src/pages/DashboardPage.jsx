import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { auditsAPI, modelsAPI, datasetsAPI } from '../api/client';
import { Plus, BarChart3, FileText, Upload, Shield, TrendingUp, AlertTriangle, CheckCircle, Trash2 } from 'lucide-react';

export default function DashboardPage() {
  const { user, isAdmin } = useAuth();
  const navigate = useNavigate();
  const [audits, setAudits] = useState([]);
  const [stats, setStats] = useState({ models: 0, datasets: 0, audits: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log('Dashboard loaded, checking auth...');
    const userStr = localStorage.getItem('user');
    
    if (!userStr || userStr === 'undefined' || userStr === 'null') {
      console.log('No user found on dashboard, redirecting to /login');
      window.location.href = '/login';
      return;
    }

    try {
      const parsedUser = JSON.parse(userStr);
      console.log('Dashboard user confirmed:', parsedUser);
    } catch (e) {
      console.log('Failed to parse user, redirecting to /login');
      window.location.href = '/login';
      return;
    }

    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [auditRes, modelRes, datasetRes] = await Promise.all([
        auditsAPI.list(),
        modelsAPI.list(),
        datasetsAPI.list(),
      ]);
      setAudits(auditRes.data);
      setStats({
        models: modelRes.data.length,
        datasets: datasetRes.data.length,
        audits: auditRes.data.length,
      });
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAudit = async (id) => {
    if (!window.confirm('Are you sure you want to delete this audit?')) return;
    try {
      await auditsAPI.delete(id);
      loadData();
    } catch (err) {
      console.error('Failed to delete audit:', err);
      alert('Failed to delete audit');
    }
  };

  const handleClearAllAudits = async () => {
    if (!window.confirm('Are you sure you want to delete ALL audits? This cannot be undone.')) return;
    try {
      await auditsAPI.clearAll();
      loadData();
    } catch (err) {
      console.error('Failed to clear audits:', err);
      alert('Failed to clear audits');
    }
  };

  const getStatusBadge = (status) => {
    const map = { completed: 'badge-fair', running: 'badge-running', failed: 'badge-biased', pending: 'badge-pending' };
    return <span className={`badge ${map[status] || 'badge-pending'}`}>{status}</span>;
  };

  const getScoreBadge = (score) => {
    if (score == null) return <span className="text-muted">—</span>;
    const cls = score >= 0.8 ? 'badge-fair' : score >= 0.5 ? 'badge-review' : 'badge-biased';
    const label = score >= 0.8 ? 'Fair' : score >= 0.5 ? 'Review' : 'Biased';
    return <span className={`badge ${cls}`}>{score.toFixed(2)} {label}</span>;
  };

  if (loading) return <div className="flex justify-center mt-lg"><div className="spinner" /></div>;

  return (
    <div className="page animate-fade-in">
      <div className="page-header">
        <h1>Welcome back, {user?.name?.split(' ')[0]} 👋</h1>
        <p>Monitor AI fairness across your models and datasets</p>
      </div>

      <div className="grid-4 mb-lg">
        <div className="card" style={{ borderLeft: '3px solid var(--accent-primary)' }}>
          <div className="flex items-center gap-md">
            <div style={{ padding: 10, borderRadius: 'var(--radius-md)', background: 'rgba(232,90,79,0.1)' }}>
              <Shield size={22} color="var(--accent-secondary)" />
            </div>
            <div>
              <div className="text-muted" style={{ fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase' }}>Total Audits</div>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-white)' }}>{stats.audits}</div>
            </div>
          </div>
        </div>
        <div className="card" style={{ borderLeft: '3px solid var(--color-fair)' }}>
          <div className="flex items-center gap-md">
            <div style={{ padding: 10, borderRadius: 'var(--radius-md)', background: 'var(--color-fair-bg)' }}>
              <TrendingUp size={22} color="var(--color-fair)" />
            </div>
            <div>
              <div className="text-muted" style={{ fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase' }}>Models</div>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-white)' }}>{stats.models}</div>
            </div>
          </div>
        </div>
        <div className="card" style={{ borderLeft: '3px solid var(--color-review)' }}>
          <div className="flex items-center gap-md">
            <div style={{ padding: 10, borderRadius: 'var(--radius-md)', background: 'var(--color-review-bg)' }}>
              <FileText size={22} color="var(--color-review)" />
            </div>
            <div>
              <div className="text-muted" style={{ fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase' }}>Datasets</div>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-white)' }}>{stats.datasets}</div>
            </div>
          </div>
        </div>
        <div className="card" style={{ borderLeft: '3px solid var(--color-biased)' }}>
          <div className="flex items-center gap-md">
            <div style={{ padding: 10, borderRadius: 'var(--radius-md)', background: 'var(--color-biased-bg)' }}>
              <AlertTriangle size={22} color="var(--color-biased)" />
            </div>
            <div>
              <div className="text-muted" style={{ fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase' }}>Issues Found</div>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-white)' }}>
                {audits.filter(a => a.overall_score != null && a.overall_score < 0.8).length}
              </div>
            </div>
          </div>
        </div>
      </div>

      {isAdmin && (
        <div className="card mb-lg" style={{ background: 'linear-gradient(135deg, rgba(232,90,79,0.08), rgba(233,128,116,0.05))' }}>
          <div className="flex items-center justify-between flex-wrap gap-md">
            <div>
              <h3>Start a New Fairness Audit</h3>
              <p className="text-secondary" style={{ fontSize: '0.9rem', marginTop: 4 }}>Upload your model and dataset, configure counterfactual tests, and detect bias</p>
            </div>
            <button className="btn btn-primary" onClick={() => navigate('/app/upload/model')} id="new-audit-btn">
              <Plus size={16} /> New Audit
            </button>
          </div>
        </div>
      )}

      <div className="card-static">
        <div className="flex items-center justify-between mb-md">
          <h3>Recent Audits</h3>
          <div className="flex gap-sm">
            {isAdmin && audits.length > 0 && (
              <button className="btn btn-danger btn-sm" onClick={handleClearAllAudits}>Clear All</button>
            )}
            {isAdmin && (
              <Link to="/reports" className="btn btn-secondary btn-sm">View All</Link>
            )}
          </div>
        </div>
        {audits.length === 0 ? (
          <div className="empty-state">
            <BarChart3 size={48} />
            <p>No audits yet. Start by uploading a model.</p>
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Model</th>
                  <th>Dataset</th>
                  <th>Status</th>
                  <th>Test Cases</th>
                  <th>Fairness</th>
                  <th>Date</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {audits.slice(0, 10).map((audit, i) => (
                  <tr key={audit.id} style={{ animationDelay: `${i * 50}ms` }} className="animate-fade-in">
                    <td style={{ fontWeight: 600 }}>{audit.model_name || '—'}</td>
                    <td>{audit.dataset_name || '—'}</td>
                    <td>{getStatusBadge(audit.status)}</td>
                    <td>{audit.num_test_cases}</td>
                    <td>{getScoreBadge(audit.overall_score)}</td>
                    <td className="text-muted">{audit.created_at ? new Date(audit.created_at).toLocaleDateString() : '—'}</td>
                    <td>
                      <div className="flex gap-sm">
                        {audit.status === 'completed' && (
                          <button className="btn btn-secondary btn-sm"
                            onClick={() => navigate(`/app/audit/results/${audit.id}`)}>
                            View
                          </button>
                        )}
                        {audit.status === 'running' && (
                          <button className="btn btn-secondary btn-sm"
                            onClick={() => navigate(`/app/audit/progress/${audit.id}`)}>
                            Progress
                          </button>
                        )}
                        {isAdmin && (
                          <button className="btn btn-danger btn-sm"
                            onClick={() => handleDeleteAudit(audit.id)}
                            style={{ padding: '0.4rem', color: 'var(--color-biased)' }}>
                            <Trash2 size={16} />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
