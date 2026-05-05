import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { auditsAPI, reportsAPI } from '../api/client';
import { Shield, AlertTriangle, CheckCircle, FileText, Download, ArrowRight } from 'lucide-react';

export default function ResultsDashboardPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    auditsAPI.results(id).then(res => {
      console.log('Audit results response:', res.data);
      setResults(res.data);
      setLoading(false);
    }).catch(err => {
      console.error('Failed to load audit results:', err.response?.status, err.response?.data);
      setLoading(false);
    });
  }, [id]);

  const handleGenerateReport = async () => {
    setGenerating(true);
    try {
      await reportsAPI.generate(id);
      alert('Report generated! Check the Reports page.');
    } catch (err) {
      alert('Failed to generate report');
    } finally {
      setGenerating(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 0.8) return 'var(--color-fair)';
    if (score >= 0.5) return 'var(--color-review)';
    return 'var(--color-biased)';
  };

  const getStatusIcon = (status) => {
    if (status === 'fair') return <CheckCircle size={18} color="var(--color-fair)" />;
    if (status === 'review') return <AlertTriangle size={18} color="var(--color-review)" />;
    return <AlertTriangle size={18} color="var(--color-biased)" />;
  };

  const getStatusLabel = (status) => {
    if (status === 'fair') return 'Fair';
    if (status === 'review') return 'Review';
    return 'Biased';
  };

  if (loading) return <div className="flex justify-center mt-lg"><div className="spinner" /></div>;
  if (!results) return <div className="page"><h2>Results not found</h2></div>;

  const overall = results.overall_fairness_score;
  const overallStatus = overall >= 0.8 ? 'FAIR' : overall >= 0.5 ? 'REVIEW REQUIRED' : 'ACTION REQUIRED';
  const overallColor = getScoreColor(overall);

  return (
    <div className="page animate-fade-in">
      <div className="page-header">
        <h1><Shield size={24} style={{ display: 'inline', marginRight: 8 }} />Fairness Dashboard</h1>
        <p>{results.model_name} — {results.num_test_cases.toLocaleString()} test cases analyzed</p>
      </div>

      {/* Overall Score */}
      <div className="card-static mb-lg" style={{ textAlign: 'center', padding: 'var(--space-2xl)', borderTop: `3px solid ${overallColor}` }}>
        <div className="text-muted" style={{ fontSize: '0.8rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1 }}>Overall Fairness Score</div>
        <div style={{ fontSize: '4rem', fontWeight: 800, color: overallColor, lineHeight: 1.2, marginTop: 'var(--space-sm)' }}>
          {overall.toFixed(2)}
        </div>
        <div className={`badge ${overall >= 0.8 ? 'badge-fair' : overall >= 0.5 ? 'badge-review' : 'badge-biased'}`} style={{ fontSize: '0.85rem', marginTop: 'var(--space-sm)' }}>
          {overallStatus}
        </div>
      </div>

      {/* Per-Dimension Scores */}
      <div className="grid-4 mb-lg">
        {results.fairness_scores.map((score, i) => (
          <div key={score.dimension} className="card" style={{ animationDelay: `${i * 100}ms`, borderLeft: `3px solid ${getScoreColor(score.fairness_score)}` }}>
            <div className="flex items-center justify-between mb-md">
              <h4 style={{ textTransform: 'capitalize' }}>{score.dimension}</h4>
              {getStatusIcon(score.status)}
            </div>
            <div style={{ fontSize: '2.2rem', fontWeight: 800, color: getScoreColor(score.fairness_score) }}>
              {score.fairness_score.toFixed(2)}
            </div>
            <div className="flex justify-between mt-md" style={{ fontSize: '0.8rem' }}>
              <span className="text-muted">DI Ratio</span>
              <span style={{ fontWeight: 600 }}>{score.disparity_ratio.toFixed(2)}</span>
            </div>
            <div className="flex justify-between" style={{ fontSize: '0.8rem' }}>
              <span className="text-muted">Status</span>
              <span className={`badge badge-${score.status === 'fair' ? 'fair' : score.status === 'review' ? 'review' : 'biased'}`} style={{ fontSize: '0.7rem' }}>
                {getStatusLabel(score.status)}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Action Buttons */}
      <div className="flex gap-md flex-wrap">
        <button className="btn btn-primary" onClick={() => navigate(`/app/audit/explanations/${id}`)} id="view-explanations-btn">
          <FileText size={16} /> View Explanations <ArrowRight size={14} />
        </button>
        <button className="btn btn-secondary" onClick={() => navigate(`/app/audit/mitigations/${id}`)} id="view-mitigations-btn">
          View Mitigations <ArrowRight size={14} />
        </button>
        <button className="btn btn-secondary" onClick={handleGenerateReport} disabled={generating} id="generate-report-btn">
          {generating ? <div className="spinner" /> : <><Download size={16} /> Generate Report</>}
        </button>
      </div>
    </div>
  );
}
