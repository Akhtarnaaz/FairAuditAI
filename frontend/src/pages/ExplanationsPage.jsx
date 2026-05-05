import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { auditsAPI } from '../api/client';
import { AlertTriangle, CheckCircle, ChevronDown, ChevronUp, ArrowLeft, ArrowRight } from 'lucide-react';

export default function ExplanationsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [results, setResults] = useState(null);
  const [expanded, setExpanded] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    auditsAPI.results(id).then(res => {
      setResults(res.data);
      // Auto-expand the first one
      if (res.data.explanations.length > 0) {
        setExpanded({ 0: true });
      }
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [id]);

  const toggle = (i) => setExpanded(prev => ({ ...prev, [i]: !prev[i] }));

  const severityConfig = {
    high: { color: 'var(--color-biased)', bg: 'var(--color-biased-bg)', icon: <AlertTriangle size={20} />, label: 'HIGH' },
    medium: { color: 'var(--color-review)', bg: 'var(--color-review-bg)', icon: <AlertTriangle size={20} />, label: 'MEDIUM' },
    low: { color: 'var(--color-fair)', bg: 'var(--color-fair-bg)', icon: <CheckCircle size={20} />, label: 'LOW' },
  };

  if (loading) return <div className="flex justify-center mt-lg"><div className="spinner" /></div>;
  if (!results) return <div className="page"><h2>Results not found</h2></div>;

  return (
    <div className="page animate-fade-in">
      <div className="page-header">
        <h1>Bias Explanations</h1>
        <p>Understanding why bias occurs in each dimension</p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)', maxWidth: 800 }}>
        {results.explanations.map((expl, i) => {
          const sev = severityConfig[expl.severity] || severityConfig.low;
          const isOpen = expanded[i];

          return (
            <div key={i} className="card-static animate-fade-in" style={{ animationDelay: `${i * 100}ms`, borderLeft: `3px solid ${sev.color}` }}>
              <div className="flex items-center justify-between" style={{ cursor: 'pointer' }} onClick={() => toggle(i)}>
                <div className="flex items-center gap-md">
                  <div style={{ color: sev.color }}>{sev.icon}</div>
                  <div>
                    <h3 style={{ textTransform: 'capitalize', marginBottom: 2 }}>{expl.dimension} Bias</h3>
                    <span className="badge" style={{ background: sev.bg, color: sev.color, border: `1px solid ${sev.color}30` }}>
                      Severity: {sev.label}
                    </span>
                  </div>
                </div>
                {isOpen ? <ChevronUp size={20} color="var(--text-muted)" /> : <ChevronDown size={20} color="var(--text-muted)" />}
              </div>

              {isOpen && (
                <div className="animate-fade-in" style={{ marginTop: 'var(--space-lg)' }}>
                  <div style={{ background: 'var(--bg-input)', borderRadius: 'var(--radius-md)', padding: 'var(--space-md)', marginBottom: 'var(--space-md)', fontSize: '0.9rem', lineHeight: 1.7 }}>
                    {expl.explanation_text}
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-md)' }}>
                    <div>
                      <div className="text-muted" style={{ fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', marginBottom: 4 }}>Root Cause</div>
                      <p style={{ fontSize: '0.85rem', lineHeight: 1.6 }}>{expl.root_cause}</p>
                    </div>
                    <div>
                      <div className="text-muted" style={{ fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', marginBottom: 4 }}>Affected Metric</div>
                      <p style={{ fontSize: '0.85rem' }}>{expl.affected_metric}</p>
                    </div>
                  </div>

                  {expl.legal_implications && (
                    <div style={{ marginTop: 'var(--space-md)', background: 'rgba(225,112,85,0.05)', border: '1px solid rgba(225,112,85,0.15)', borderRadius: 'var(--radius-md)', padding: 'var(--space-md)' }}>
                      <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-biased)', textTransform: 'uppercase', marginBottom: 4 }}>⚖️ Legal Implications</div>
                      <p style={{ fontSize: '0.85rem', lineHeight: 1.6 }}>{expl.legal_implications}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="flex gap-md mt-lg">
        <button className="btn btn-secondary" onClick={() => navigate(`/app/audit/results/${id}`)}>
          <ArrowLeft size={14} /> Back to Results
        </button>
        <button className="btn btn-primary" onClick={() => navigate(`/app/audit/mitigations/${id}`)} id="go-to-mitigations">
          View Mitigations <ArrowRight size={14} />
        </button>
      </div>
    </div>
  );
}
