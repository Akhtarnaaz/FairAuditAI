import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { reportsAPI, auditsAPI } from '../api/client';
import { FileText, Download, BarChart3, ExternalLink, Trash2 } from 'lucide-react';

export default function ReportsPage() {
  const { isAdmin } = useAuth();
  const navigate = useNavigate();
  const [reports, setReports] = useState([]);
  const [audits, setAudits] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadData = () => {
    Promise.all([reportsAPI.list(), auditsAPI.list()]).then(([r, a]) => {
      setReports(r.data);
      setAudits(a.data);
      setLoading(false);
    }).catch(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleDeleteReport = async (id) => {
    if (!window.confirm('Are you sure you want to delete this report?')) return;
    try {
      await reportsAPI.delete(id);
      loadData();
    } catch (err) {
      alert('Failed to delete report');
    }
  };

  const handleDeleteAudit = async (id) => {
    if (!window.confirm('Are you sure you want to delete this audit?')) return;
    try {
      await auditsAPI.delete(id);
      loadData();
    } catch (err) {
      alert('Failed to delete audit');
    }
  };

  const handleClearAllReports = async () => {
    if (!window.confirm('Are you sure you want to delete ALL reports? This cannot be undone.')) return;
    try {
      await reportsAPI.clearAll();
      loadData();
    } catch (err) {
      alert('Failed to clear reports');
    }
  };

  const handleClearAllAudits = async () => {
    if (!window.confirm('Are you sure you want to delete ALL audits? This cannot be undone.')) return;
    try {
      await auditsAPI.clearAll();
      loadData();
    } catch (err) {
      alert('Failed to clear audits');
    }
  };

  const getScoreBadge = (score) => {
    if (score == null) return <span className="text-muted">—</span>;
    const cls = score >= 0.8 ? 'badge-fair' : score >= 0.5 ? 'badge-review' : 'badge-biased';
    const label = score >= 0.8 ? 'Fair' : score >= 0.5 ? 'Review' : 'Biased';
    return <span className={`badge ${cls}`}>{score.toFixed(2)} {label}</span>;
  };

  const getToken = () => localStorage.getItem('token');

  const handleDownload = async (url, filename) => {
    try {
      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${getToken()}` }
      });
      const blob = await response.blob();
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = filename;
      a.click();
      URL.revokeObjectURL(a.href);
    } catch (err) {
      console.error('Download failed:', err);
    }
  };

  if (loading) return <div className="flex justify-center mt-lg"><div className="spinner" /></div>;

  return (
    <div className="page animate-fade-in">
      <div className="page-header">
        <h1><FileText size={24} style={{ display: 'inline', marginRight: 8 }} />Audit Reports</h1>
        <p>View and download fairness audit reports</p>
      </div>

      {/* Completed audits without reports */}
      {audits.filter(a => a.status === 'completed').length > 0 && reports.length === 0 && (
        <div className="card mb-lg" style={{ background: 'rgba(108,92,231,0.06)' }}>
          <p>You have completed audits. Generate a report from the results page to see it here.</p>
        </div>
      )}

      {reports.length === 0 && audits.filter(a => a.status === 'completed').length === 0 ? (
        <div className="empty-state">
          <BarChart3 size={48} />
          <h3 style={{ marginTop: 'var(--space-md)' }}>No Reports Yet</h3>
          <p className="text-secondary mt-md">Complete a fairness audit to generate reports</p>
        </div>
      ) : (
        <>
          {/* Reports Table */}
          {reports.length > 0 && (
            <div className="card-static mb-lg">
              <div className="flex items-center justify-between mb-md">
                <h3>Generated Reports</h3>
                {isAdmin && <button className="btn btn-danger btn-sm" onClick={handleClearAllReports}>Clear All Reports</button>}
              </div>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Model</th>
                      <th>Fairness Score</th>
                      <th>Generated</th>
                      <th>Downloads</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reports.map((report, i) => (
                      <tr key={report.id} className="animate-fade-in" style={{ animationDelay: `${i * 50}ms` }}>
                        <td style={{ fontWeight: 600 }}>{report.model_name || 'Model'}</td>
                        <td>{getScoreBadge(report.overall_score)}</td>
                        <td className="text-muted">{report.generated_at ? new Date(report.generated_at).toLocaleDateString() : '—'}</td>
                        <td>{report.downloaded_count}</td>
                        <td>
                          <div className="flex gap-sm">
                            <button className="btn btn-primary btn-sm"
                              onClick={() => handleDownload(
                                `http://localhost:8000/api/reports/${report.id}/download/pdf`,
                                `audit_report_${report.id.slice(0,8)}.pdf`
                              )}>
                              <Download size={12} /> PDF
                            </button>
                            <button className="btn btn-secondary btn-sm"
                              onClick={() => handleDownload(
                                `http://localhost:8000/api/reports/${report.id}/download/csv`,
                                `audit_report_${report.id.slice(0,8)}.csv`
                              )}>
                              <Download size={12} /> CSV
                            </button>
                            <button className="btn btn-secondary btn-sm"
                              onClick={() => navigate(`/app/audit/results/${report.audit_run_id}`)}>
                              <ExternalLink size={12} /> View
                            </button>
                            {isAdmin && (
                              <button className="btn btn-danger btn-sm"
                                onClick={() => handleDeleteReport(report.id)}
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
            </div>
          )}

          {/* Completed Audits */}
          <div className="card-static">
            <div className="flex items-center justify-between mb-md">
              <h3>Completed Audits</h3>
              {isAdmin && audits.filter(a => a.status === 'completed').length > 0 && (
                <button className="btn btn-danger btn-sm" onClick={handleClearAllAudits}>Clear All Audits</button>
              )}
            </div>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Model</th>
                    <th>Dataset</th>
                    <th>Test Cases</th>
                    <th>Fairness</th>
                    <th>Date</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {audits.filter(a => a.status === 'completed').map((audit, i) => (
                    <tr key={audit.id} className="animate-fade-in" style={{ animationDelay: `${i * 50}ms` }}>
                      <td style={{ fontWeight: 600 }}>{audit.model_name || '—'}</td>
                      <td>{audit.dataset_name || '—'}</td>
                      <td>{audit.num_test_cases}</td>
                      <td>{getScoreBadge(audit.overall_score)}</td>
                      <td className="text-muted">{audit.created_at ? new Date(audit.created_at).toLocaleDateString() : '—'}</td>
                      <td>
                        <div className="flex gap-sm">
                          <button className="btn btn-secondary btn-sm"
                            onClick={() => navigate(`/app/audit/results/${audit.id}`)}>
                            View Results
                          </button>
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
          </div>
        </>
      )}
    </div>
  );
}
