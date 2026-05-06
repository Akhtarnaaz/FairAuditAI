import { useState, useEffect } from 'react';
import { userExploreAPI } from '../api/client';
import { 
  Search, Sparkles, Shield, AlertTriangle, CheckCircle, 
  RefreshCcw, Info, History, Download, ArrowRight, User, HelpCircle
} from 'lucide-react';

export default function UserExplorePage() {
  const [query, setQuery] = useState('');
  const [aiResponse, setAiResponse] = useState('');
  const [fairnessResult, setFairnessResult] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [explanation, setExplanation] = useState('');
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [checking, setChecking] = useState(false);
  const [testing, setTesting] = useState(false);

  const [gender, setGender] = useState('Female');
  const [region, setRegion] = useState('Rural');
  const [language, setLanguage] = useState('Hindi');

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const res = await userExploreAPI.history();
      setHistory(res.data);
    } catch (err) {
      console.error('Failed to load history');
    }
  };

  const handleAsk = async (e) => {
    if (e) e.preventDefault();
    if (!query) return;
    setLoading(true);
    setAiResponse('');
    setFairnessResult(null);
    setComparison(null);
    setExplanation('');
    try {
      const res = await userExploreAPI.ask(query);
      setAiResponse(res.data.response);
    } catch (err) {
      alert('Failed to get response');
    } finally {
      setLoading(false);
    }
  };

  const handleCheckFairness = async () => {
    setChecking(true);
    try {
      const res = await userExploreAPI.checkFairness(query, aiResponse);
      setFairnessResult(res.data);
      loadHistory();
    } catch (err) {
      alert('Fairness check failed');
    } finally {
      setChecking(false);
    }
  };

  const handleTestProfile = async () => {
    setTesting(true);
    try {
      const res = await userExploreAPI.testProfile(query, aiResponse, { gender, region, language });
      setComparison(res.data);
    } catch (err) {
      alert('Profile test failed');
    } finally {
      setTesting(false);
    }
  };

  const getStatusConfig = (status) => {
    switch (status) {
      case 'fair': return { color: 'var(--color-fair)', icon: <CheckCircle size={18} />, label: 'Fair' };
      case 'slight_bias': return { color: 'var(--color-review)', icon: <AlertTriangle size={18} />, label: 'Slight Bias' };
      case 'biased': return { color: 'var(--color-biased)', icon: <AlertTriangle size={18} />, label: 'Biased' };
      default: return { color: 'var(--text-muted)', icon: <Info size={18} />, label: 'Unknown' };
    }
  };

  const handleDownload = () => {
    const content = `
FAIRNESS EXPLORATION REPORT
===========================
Query: ${query}
Original Response: ${aiResponse}
Fairness Status: ${fairnessResult?.status || 'Not Checked'}
Explanation: ${fairnessResult?.explanation || 'N/A'}
Counterfactual Test (${gender}, ${region}): ${comparison?.modified_response || 'N/A'}
    `;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'fairness_report.txt';
    a.click();
  };

  return (
    <div className="page animate-fade-in">
      <div className="page-header">
        <h1>
          <Sparkles size={28} style={{ display: 'inline', marginRight: 12, color: 'var(--accent-primary)', verticalAlign: 'bottom' }} />
          Fairness Explorer
        </h1>
        <p>Interactive playground to detect AI bias. Ask questions, swap identities, and see the difference.</p>
      </div>

      <div className="grid-3-1 gap-lg">
        <div className="flex flex-col gap-lg">
          {/* Query Section */}
          <div className="card-static" style={{ borderTop: '4px solid var(--accent-primary)' }}>
            <h3 className="flex items-center gap-sm mb-md"><Search size={20} /> Ask AI Anything</h3>
            <form onSubmit={handleAsk} className="flex gap-md">
              <input 
                className="input" 
                value={query} 
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g., Should this applicant be approved for a micro-loan?"
                style={{ fontSize: '1.1rem', padding: 'var(--space-md)' }}
              />
              <button type="submit" className="btn btn-primary" disabled={loading} style={{ minWidth: 140 }}>
                {loading ? <div className="spinner" /> : 'Get Response'}
              </button>
            </form>
          </div>

          {/* Response Section */}
          {aiResponse && (
            <div className="card-static animate-slide-up">
              <div className="flex items-center justify-between mb-md">
                <h3>AI Response</h3>
                <div className="text-muted" style={{ fontSize: '0.8rem' }}>Real-time simulation</div>
              </div>
              <div className="p-lg bg-glass border-fair" style={{ borderRadius: 'var(--radius-md)', fontSize: '1.2rem', lineHeight: 1.6, background: 'rgba(255,255,255,0.03)' }}>
                "{aiResponse}"
              </div>
              <div className="flex gap-md mt-lg">
                <button className="btn btn-primary" onClick={handleCheckFairness} disabled={checking}>
                  {checking ? <div className="spinner" /> : <><Shield size={18} /> Check Fairness</>}
                </button>
              </div>
            </div>
          )}

          {/* Fairness Result Section */}
          {fairnessResult && (
            <div className="card-static animate-slide-up" style={{ borderLeft: `6px solid ${getStatusConfig(fairnessResult.status).color}` }}>
              <div className="flex items-center justify-between mb-md">
                <h3 className="flex items-center gap-sm">Fairness Indicator</h3>
                <div className={`badge badge-${fairnessResult.status}`} style={{ fontSize: '1.1rem', padding: '6px 12px' }}>
                  {getStatusConfig(fairnessResult.status).icon} {getStatusConfig(fairnessResult.status).label}
                </div>
              </div>
              <div className="p-md mb-lg" style={{ background: 'rgba(255,255,255,0.05)', borderRadius: 'var(--radius-md)' }}>
                <p style={{ fontSize: '1.1rem' }}>{fairnessResult.explanation}</p>
              </div>
              
              <div className="mt-md pt-lg border-t">
                <div className="flex items-center justify-between mb-lg">
                  <div>
                    <h3 className="flex items-center gap-sm">Test Different Profile</h3>
                    <p className="text-secondary mt-xs">Swap identity markers to see if the AI changes its response.</p>
                  </div>
                  <HelpCircle size={20} className="text-muted" />
                </div>
                
                <div className="grid-3 gap-md mb-lg">
                  <div className="form-group">
                    <label>Gender</label>
                    <select className="select" value={gender} onChange={(e) => setGender(e.target.value)}>
                      <option>Male</option>
                      <option>Female</option>
                      <option>Non-binary</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Region</label>
                    <select className="select" value={region} onChange={(e) => setRegion(e.target.value)}>
                      <option>Urban</option>
                      <option>Rural</option>
                      <option>Remote</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Language</label>
                    <select className="select" value={language} onChange={(e) => setLanguage(e.target.value)}>
                      <option>English</option>
                      <option>Hindi</option>
                      <option>Regional</option>
                    </select>
                  </div>
                </div>

                <button className="btn btn-primary btn-lg w-full" onClick={handleTestProfile} disabled={testing} style={{ background: 'var(--accent-secondary)' }}>
                  {testing ? <div className="spinner" /> : <><RefreshCcw size={18} /> Run Identity Swap Test</>}
                </button>
              </div>
            </div>
          )}

          {/* Comparison Result */}
          {comparison && (
            <div className="card-static animate-slide-up" style={{ background: 'rgba(232,90,79,0.05)', border: '1px solid rgba(232,90,79,0.2)' }}>
              <h3 className="mb-lg flex items-center gap-sm">
                <RefreshCcw size={20} /> Counterfactual Comparison
              </h3>
              <div className="grid-2 gap-lg">
                <div className="flex flex-col gap-sm">
                  <div className="badge" style={{ alignSelf: 'flex-start', background: 'rgba(255,255,255,0.1)' }}>Original</div>
                  <div className="p-md bg-glass" style={{ borderRadius: 'var(--radius-md)', minHeight: 100, border: '1px solid rgba(255,255,255,0.1)' }}>
                    {comparison.original_response}
                  </div>
                </div>
                <div className="flex flex-col gap-sm">
                  <div className="badge badge-review" style={{ alignSelf: 'flex-start' }}>Swapped: {gender}, {region}</div>
                  <div className="p-md bg-glass" style={{ 
                    borderRadius: 'var(--radius-md)', 
                    minHeight: 100, 
                    border: comparison.is_different ? '2px solid var(--color-biased)' : '1px solid var(--color-fair)',
                    background: comparison.is_different ? 'rgba(255,71,87,0.05)' : 'rgba(46,213,115,0.05)'
                  }}>
                    {comparison.modified_response}
                  </div>
                </div>
              </div>
              
              <div className="mt-lg p-lg" style={{ borderRadius: 'var(--radius-md)', background: comparison.is_different ? 'rgba(255,71,87,0.1)' : 'rgba(46,213,115,0.1)', color: comparison.is_different ? 'var(--color-biased)' : 'var(--color-fair)' }}>
                {comparison.is_different ? (
                  <div className="flex items-start gap-md">
                    <AlertTriangle size={24} />
                    <div>
                      <strong style={{ fontSize: '1.1rem' }}>Bias Detected in Real-Time!</strong>
                      <p className="mt-xs">The AI model provided a different response when identity markers were swapped. This indicates unfair weighting of sensitive attributes.</p>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-start gap-md">
                    <CheckCircle size={24} />
                    <div>
                      <strong style={{ fontSize: '1.1rem' }}>Fairness Maintained</strong>
                      <p className="mt-xs">The model's output remained consistent across different identities, demonstrating robust demographic parity for this query.</p>
                    </div>
                  </div>
                )}
              </div>

              <div className="mt-xl pt-lg border-t flex justify-between gap-md">
                <button className="btn btn-secondary flex-1" onClick={() => setExplanation('This happens because AI models often learn biased patterns from historical human decisions. If a specific group was historically given lower credit limits, the model learns that as a "rule," even if it is unfair.')}>
                  <HelpCircle size={16} /> Why is this happening?
                </button>
                <button className="btn btn-secondary flex-1" onClick={handleDownload}>
                  <Download size={16} /> Download Result
                </button>
              </div>
              
              {explanation && (
                <div className="mt-lg p-lg bg-glass animate-slide-up" style={{ borderRadius: 'var(--radius-md)', borderLeft: '4px solid var(--accent-primary)', background: 'rgba(255,255,255,0.05)' }}>
                  <h4 className="mb-sm flex items-center gap-sm"><Info size={18} /> Plain-English Insight</h4>
                  <p style={{ lineHeight: 1.6 }}>{explanation}</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Sidebar History */}
        <div className="flex flex-col gap-md">
          <div className="card-static" style={{ position: 'sticky', top: 'var(--space-md)' }}>
            <div className="flex items-center justify-between mb-lg">
              <h3 className="flex items-center gap-sm"><History size={20} /> Your History</h3>
              {history.length > 0 && (
                <button 
                  className="btn btn-secondary btn-sm" 
                  onClick={async () => {
                    if (window.confirm('Are you sure you want to clear your history?')) {
                      try {
                        await userExploreAPI.clearHistory();
                        setHistory([]);
                      } catch(err) {
                        alert('Failed to clear history');
                      }
                    }
                  }}
                  style={{ padding: '4px 8px', fontSize: '0.8rem' }}
                >
                  Clear All
                </button>
              )}
            </div>
            <div className="flex flex-col gap-sm" style={{ maxHeight: '75vh', overflowY: 'auto', paddingRight: '4px' }}>
              {history.length === 0 ? (
                <div className="empty-state" style={{ padding: 'var(--space-lg)' }}>
                  <History size={32} />
                  <p className="mt-md">No queries yet.</p>
                </div>
              ) : (
                history.map((h, i) => (
                  <div key={h.id} className="p-md bg-glass hover-card cursor-pointer animate-fade-in" 
                    style={{ borderRadius: 'var(--radius-md)', animationDelay: `${i * 50}ms`, border: '1px solid rgba(255,255,255,0.05)' }}
                    onClick={() => {
                      setQuery(h.query_text);
                      setAiResponse(h.response_text);
                      setFairnessResult({ status: h.fairness_status, explanation: h.fairness_explanation });
                      setComparison(null);
                      setExplanation('');
                    }}>
                    <div className="text-truncate" style={{ fontWeight: 600, fontSize: '0.95rem' }}>{h.query_text}</div>
                    <div className="flex justify-between items-center mt-sm">
                      <span className={`badge badge-${h.fairness_status}`} style={{ fontSize: '0.7rem', padding: '2px 8px' }}>
                        {h.fairness_status}
                      </span>
                      <span className="text-muted" style={{ fontSize: '0.75rem' }}>{new Date(h.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
