import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';

import { modelsAPI, datasetsAPI, auditsAPI } from '../api/client';
import { Settings, Play, Eye } from 'lucide-react';

export default function ConfigCounterfactualPage() {
  const navigate = useNavigate();
  const [models, setModels] = useState([]);
  const [datasets, setDatasets] = useState([]);
  const [selectedModel, setSelectedModel] = useState('');
  const [selectedDataset, setSelectedDataset] = useState('');
  const [dimensions, setDimensions] = useState({ gender: true, caste: true, language: true, region: true });
  const [strategy, setStrategy] = useState('systematic');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([modelsAPI.list(), datasetsAPI.list()])
      .then(([m, d]) => {
        setModels(m.data);
        setDatasets(d.data);
        if (m.data.length) setSelectedModel(m.data[0].id);
        if (d.data.length) setSelectedDataset(d.data[0].id);
      })
      .catch(err => {
        console.error("Failed to load models/datasets:", err);
        setError("Failed to load your models or datasets. Please try refreshing.");
      });
  }, []);

  const toggleDim = (dim) => setDimensions(prev => ({ ...prev, [dim]: !prev[dim] }));

  const handleRun = async () => {
    if (!selectedModel || !selectedDataset) {
      setError('Please select a model and dataset');
      return;
    }
    setError('');
    setLoading(true);
    try {
      const auditRes = await auditsAPI.create({
        model_id: selectedModel,
        dataset_id: selectedDataset,
        dimensions,
        variation_strategy: strategy,
      });
      const auditId = auditRes.data.id;
      await auditsAPI.run(auditId);
      navigate(`/app/audit/progress/${auditId}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start audit');
    } finally {
      setLoading(false);
    }
  };

  const dimInfo = {
    gender: { label: 'Gender', desc: 'Swap he/she, male/female names', emoji: '👤' },
    caste: { label: 'Caste / Identity', desc: 'Swap high-caste ↔ low-caste surnames', emoji: '🏷️' },
    language: { label: 'Language', desc: 'Add Hindi/Tamil language markers', emoji: '🌐' },
    region: { label: 'Region', desc: 'Swap North ↔ South Indian locations', emoji: '📍' },
  };

  return (
    <div className="page animate-fade-in">
      <div className="page-header">
        <h1><Settings size={24} style={{ display: 'inline', marginRight: 8 }} />Configure Counterfactual Tests</h1>
        <p>Step 3 of 3 — Select demographic dimensions and testing strategy</p>
      </div>

      <div className="grid-2">
        <div>
          <div className="card-static mb-lg">
            <h3 style={{ marginBottom: 'var(--space-md)' }}>Select Model & Dataset</h3>
            <div className="form-group">
              <label>Model</label>
              {models.length === 0 ? (
                <div className="text-muted p-sm" style={{ border: '1px dashed var(--border-subtle)', borderRadius: 'var(--radius-md)' }}>
                  No models found. <Link to="/app/upload/model" style={{ textDecoration: 'underline' }}>Upload one</Link>
                </div>
              ) : (
                <select className="select" value={selectedModel} onChange={(e) => setSelectedModel(e.target.value)} id="select-model">
                  {models.map(m => <option key={m.id} value={m.id}>{m.model_name} ({m.model_type})</option>)}
                </select>
              )}
            </div>
            <div className="form-group">
              <label>Dataset</label>
              {datasets.length === 0 ? (
                <div className="text-muted p-sm" style={{ border: '1px dashed var(--border-subtle)', borderRadius: 'var(--radius-md)' }}>
                  No datasets found. <Link to="/app/upload/dataset" style={{ textDecoration: 'underline' }}>Upload one</Link>
                </div>
              ) : (
                <select className="select" value={selectedDataset} onChange={(e) => setSelectedDataset(e.target.value)} id="select-dataset">
                  {datasets.map(d => <option key={d.id} value={d.id}>{d.dataset_name} ({d.num_rows} rows)</option>)}
                </select>
              )}
            </div>

          </div>

          <div className="card-static mb-lg">
            <h3 style={{ marginBottom: 'var(--space-md)' }}>Variation Strategy</h3>
            <div className="radio-group" style={{ flexDirection: 'column' }}>
              {[
                { val: 'systematic', label: 'Systematic', desc: 'Vary one dimension at a time' },
                { val: 'random', label: 'Random', desc: 'Vary random combinations' },
                { val: 'exhaustive', label: 'Exhaustive', desc: 'All possible combinations' },
              ].map(s => (
                <label key={s.val} className={`radio-item ${strategy === s.val ? 'active' : ''}`} style={{ width: '100%' }}>
                  <input type="radio" value={s.val} checked={strategy === s.val}
                    onChange={(e) => setStrategy(e.target.value)} />
                  <div>
                    <div style={{ fontWeight: 600 }}>{s.label}</div>
                    <div className="text-muted" style={{ fontSize: '0.8rem' }}>{s.desc}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>
        </div>

        <div>
          <div className="card-static mb-lg">
            <h3 style={{ marginBottom: 'var(--space-md)' }}>Demographic Dimensions</h3>
            <div className="checkbox-group">
              {Object.entries(dimInfo).map(([key, info]) => (
                <label key={key} className="checkbox-item" style={{ padding: 'var(--space-md)' }}>
                  <input type="checkbox" checked={dimensions[key]} onChange={() => toggleDim(key)} />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600 }}>{info.emoji} {info.label}</div>
                    <div className="text-muted" style={{ fontSize: '0.8rem' }}>{info.desc}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div className="card" style={{ background: 'rgba(232,90,79,0.06)', textAlign: 'center' }}>
            <div className="text-muted" style={{ fontSize: '0.8rem', marginBottom: 4 }}>Estimated Test Cases</div>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--accent-secondary)' }}>
              ~{(datasets.find(d => d.id === selectedDataset)?.num_rows || 100) * Object.values(dimensions).filter(Boolean).length}
            </div>
            <div className="text-muted" style={{ fontSize: '0.8rem' }}>counterfactual pairs</div>
          </div>
        </div>
      </div>

      {error && <div className="login-error mb-md mt-md">{error}</div>}

      <div className="flex gap-md mt-lg">
        <button className="btn btn-primary btn-lg" onClick={handleRun} disabled={loading} id="run-audit-btn">
          {loading ? <div className="spinner" /> : <><Play size={16} /> Run Bias Detection</>}
        </button>
      </div>
    </div>
  );
}
