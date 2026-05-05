import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { auditsAPI } from '../api/client';
import { Loader, CheckCircle, XCircle } from 'lucide-react';

export default function AuditProgressPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const poll = setInterval(async () => {
      try {
        const res = await auditsAPI.status(id);
        setStatus(res.data);
        if (res.data.status === 'completed') {
          clearInterval(poll);
          setTimeout(() => navigate(`/app/audit/results/${id}`), 1500);
        }
        if (res.data.status === 'failed') {
          clearInterval(poll);
          setError(res.data.error_message || 'Audit failed');
        }
      } catch (err) {
        clearInterval(poll);
        setError('Failed to check status');
      }
    }, 1000);

    return () => clearInterval(poll);
  }, [id, navigate]);

  const progress = status?.progress || 0;
  const statusText = {
    0: 'Initializing...',
    10: 'Loading dataset...',
    25: 'Generating counterfactual pairs...',
    60: 'Running bias detection...',
    75: 'Calculating fairness scores...',
    90: 'Generating explanations & recommendations...',
    100: 'Audit complete!',
  };

  const getStatusLabel = () => {
    const keys = Object.keys(statusText).map(Number).sort((a, b) => a - b);
    let label = statusText[0];
    for (const k of keys) {
      if (progress >= k) label = statusText[k];
    }
    return label;
  };

  return (
    <div className="page animate-fade-in">
      <div style={{ maxWidth: 600, margin: '0 auto', textAlign: 'center', paddingTop: 'var(--space-2xl)' }}>
        {status?.status === 'completed' ? (
          <div className="animate-fade-in">
            <CheckCircle size={72} color="var(--color-fair)" />
            <h2 style={{ marginTop: 'var(--space-lg)' }}>Audit Complete!</h2>
            <p className="text-secondary mt-md">Redirecting to results...</p>
          </div>
        ) : status?.status === 'failed' ? (
          <div className="animate-fade-in">
            <XCircle size={72} color="var(--color-error)" />
            <h2 style={{ marginTop: 'var(--space-lg)' }}>Audit Failed</h2>
            <p className="text-secondary mt-md">{error}</p>
            <button className="btn btn-primary mt-lg" onClick={() => navigate('/app/audit/configure')}>
              Try Again
            </button>
          </div>
        ) : (
          <>
            <div style={{ marginBottom: 'var(--space-xl)' }}>
              <Loader size={48} color="var(--accent-secondary)" className="animate-pulse" style={{ animation: 'spin 2s linear infinite' }} />
            </div>
            <h2>Running Bias Detection</h2>
            <p className="text-secondary mt-md" style={{ fontSize: '0.95rem' }}>{getStatusLabel()}</p>

            <div style={{ marginTop: 'var(--space-xl)' }}>
              <div className="flex justify-between mb-md" style={{ fontSize: '0.85rem' }}>
                <span className="text-secondary">Progress</span>
                <span style={{ fontWeight: 700, color: 'var(--accent-secondary)' }}>{progress}%</span>
              </div>
              <div className="progress-bar" style={{ height: 12 }}>
                <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
              </div>
            </div>

            {status?.num_test_cases > 0 && (
              <div className="card mt-lg" style={{ textAlign: 'left' }}>
                <div className="flex justify-between" style={{ fontSize: '0.9rem' }}>
                  <span className="text-secondary">Test Cases Generated</span>
                  <span style={{ fontWeight: 600 }}>{status.num_test_cases.toLocaleString()}</span>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
