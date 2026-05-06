import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { auditsAPI, reportsAPI } from '../api/client';
import { Wrench, ArrowLeft, Download, Zap, Database, Code, Cpu, CheckCircle } from 'lucide-react';

export default function MitigationsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    auditsAPI.results(id).then(res => {
      setResults(res.data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [id]);

  const typeConfig = {
    data_level: { icon: <Database size={18} />, color: '#74b9ff', label: 'Data-Level Fix' },
    feature_level: { icon: <Code size={18} />, color: '#a29bfe', label: 'Feature-Level Fix' },
    output_level: { icon: <Zap size={18} />, color: '#e67e22', label: 'Output-Level Fix' },
    model_level: { icon: <Cpu size={18} />, color: '#e17055', label: 'Model-Level Fix' },
    best_practice: { icon: <CheckCircle size={18} />, color: '#00cec9', label: 'Best Practice' },
  };

  const effortColors = { low: 'var(--color-fair)', medium: 'var(--color-review)', high: 'var(--color-biased)' };
  const impactColors = { low: 'var(--text-muted)', medium: 'var(--color-review)', high: 'var(--color-fair)', very_high: '#00cec9' };

  const handleGenerateReport = async () => {
    setGenerating(true);
    try {
      await reportsAPI.generate(id);
      navigate('/app/reports');
    } catch { alert('Failed to generate report'); }
    finally { setGenerating(false); }
  };

  if (loading) return <div className="flex justify-center mt-lg"><div className="spinner" /></div>;
  if (!results) return <div className="page"><h2>Results not found</h2></div>;

  // Group by dimension
  const byDimension = {};
  results.mitigations.forEach(m => {
    if (!byDimension[m.dimension]) byDimension[m.dimension] = [];
    byDimension[m.dimension].push(m);
  });

  return (
    <div className="page animate-fade-in">
      <div className="page-header">
        <h1><Wrench size={24} style={{ display: 'inline', marginRight: 8 }} />Mitigation Recommendations</h1>
        <p>Actionable strategies to reduce detected bias, ranked by priority</p>
      </div>

      {/* Effort vs Impact Legend */}
      <div className="card-static mb-lg" style={{ maxWidth: 800 }}>
        <div className="flex gap-lg flex-wrap" style={{ fontSize: '0.8rem' }}>
          <div>
            <span className="text-muted" style={{ fontWeight: 600 }}>Effort: </span>
            {['low', 'medium', 'high'].map(e => (
              <span key={e} className="badge" style={{ marginLeft: 6, color: effortColors[e], background: `${effortColors[e]}15`, border: `1px solid ${effortColors[e]}30` }}>
                {e}
              </span>
            ))}
          </div>
          <div>
            <span className="text-muted" style={{ fontWeight: 600 }}>Impact: </span>
            {['medium', 'high', 'very_high'].map(e => (
              <span key={e} className="badge" style={{ marginLeft: 6, color: impactColors[e], background: `${impactColors[e]}15`, border: `1px solid ${impactColors[e]}30` }}>
                {e.replace('_', ' ')}
              </span>
            ))}
          </div>
        </div>
      </div>

      {Object.entries(byDimension).map(([dim, recs]) => (
        <div key={dim} style={{ marginBottom: 'var(--space-xl)', maxWidth: 800 }}>
          <h3 style={{ textTransform: 'capitalize', marginBottom: 'var(--space-md)' }}>
            {dim} Dimension
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
            {recs.map((rec, i) => {
              const tc = typeConfig[rec.recommendation_type] || typeConfig.data_level;
              return (
                <div key={i} className="card animate-fade-in" style={{ animationDelay: `${i * 60}ms`, padding: 'var(--space-md)' }}>
                  <div className="flex items-center gap-md">
                    <div style={{ background: `${tc.color}15`, color: tc.color, padding: 8, borderRadius: 'var(--radius-md)', flexShrink: 0 }}>
                      {tc.icon}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div className="flex items-center gap-sm mb-md" style={{ marginBottom: 4 }}>
                        <span className="badge" style={{ background: `${tc.color}15`, color: tc.color, border: `1px solid ${tc.color}30`, fontSize: '0.7rem' }}>
                          #{rec.priority} {tc.label}
                        </span>
                      </div>
                      <p style={{ fontSize: '0.88rem', lineHeight: 1.6 }}>{rec.recommendation_text}</p>
                      <div className="flex gap-md mt-md" style={{ fontSize: '0.8rem' }}>
                        <span>
                          Effort: <strong style={{ color: effortColors[rec.effort_level] }}>{rec.effort_level}</strong>
                        </span>
                        <span>
                          Impact: <strong style={{ color: impactColors[rec.impact_level] }}>{rec.impact_level.replace('_', ' ')}</strong>
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}

      <div className="flex gap-md mt-lg">
        <button className="btn btn-secondary" onClick={() => navigate(`/app/audit/results/${id}`)}>
          <ArrowLeft size={14} /> Back to Results
        </button>
        <button className="btn btn-primary" onClick={handleGenerateReport} disabled={generating} id="generate-report-btn-2">
          {generating ? <div className="spinner" /> : <><Download size={16} /> Generate Report</>}
        </button>
      </div>
    </div>
  );
}
