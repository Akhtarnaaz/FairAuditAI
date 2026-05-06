import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { datasetsAPI } from '../api/client';
import { Upload, CheckCircle, Table } from 'lucide-react';

export default function UploadDatasetPage() {
  const navigate = useNavigate();
  const [datasetName, setDatasetName] = useState('');
  const [file, setFile] = useState(null);
  const [demoDatasetKey, setDemoDatasetKey] = useState('');

  const demoDatasets = [
    { key: 'loan', name: 'Loan Approval Dataset', desc: 'Financial data' },
    { key: 'loan_extreme', name: 'Loan (Extreme)', desc: 'For extreme bias' },
    { key: 'hiring', name: 'Hiring Dataset', desc: 'HR data' },
    { key: 'hiring_extreme', name: 'Hiring (Extreme)', desc: 'For extreme bias' },
    { key: 'healthcare', name: 'Healthcare Dataset', desc: 'Medical data' },
    { key: 'healthcare_extreme', name: 'Healthcare (Extreme)', desc: 'For extreme bias' }
  ];
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [dragOver, setDragOver] = useState(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files?.[0];
    if (f) {
      setFile(f);
      setDemoDatasetKey('');
    }
  };

  const handleFileChange = (e) => {
    const f = e.target.files?.[0];
    if (f) {
      setFile(f);
      setDemoDatasetKey('');
    }
  };

  const handleDemoSelect = (key) => {
    setDemoDatasetKey(key);
    setFile(null);
    const ds = demoDatasets.find(d => d.key === key);
    if (ds) setDatasetName(ds.name);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file && !demoDatasetKey) { setError('Please select a file or a demo dataset'); return; }
    setError('');
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('dataset_name', datasetName || (demoDatasetKey ? demoDatasets.find(d => d.key === demoDatasetKey).name : file.name.replace(/\.[^.]+$/, '')));
      if (demoDatasetKey) {
        formData.append('demo_dataset_key', demoDatasetKey);
      } else {
        formData.append('file', file);
      }
      const res = await datasetsAPI.upload(formData);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  if (result) {
    return (
      <div className="page animate-fade-in">
        <div className="page-header">
          <h1>Dataset Uploaded ✓</h1>
          <p>Step 2 of 3 — Review your dataset schema</p>
        </div>

        <div className="grid-2 mb-lg">
          <div className="card">
            <h4 style={{ marginBottom: 'var(--space-sm)' }}>Dataset Info</h4>
            <div style={{ fontSize: '0.9rem', display: 'flex', flexDirection: 'column', gap: 8 }}>
              <div className="flex justify-between"><span className="text-secondary">Name:</span><strong>{result.dataset_name}</strong></div>
              <div className="flex justify-between"><span className="text-secondary">Rows:</span><strong>{result.num_rows}</strong></div>
              <div className="flex justify-between"><span className="text-secondary">Columns:</span><strong>{result.num_columns}</strong></div>
            </div>
          </div>
          <div className="card">
            <h4 style={{ marginBottom: 'var(--space-sm)' }}>Schema</h4>
            <div style={{ fontSize: '0.8rem', display: 'flex', flexDirection: 'column', gap: 4 }}>
              {result.schema_info && Object.entries(result.schema_info).map(([col, dtype]) => (
                <div key={col} className="flex justify-between" style={{ padding: '4px 0', borderBottom: '1px solid var(--border-subtle)' }}>
                  <span style={{ fontWeight: 500 }}>{col}</span>
                  <span className="text-muted">{dtype}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {result.preview && result.preview.length > 0 && (
          <div className="card-static mb-lg">
            <h4 style={{ marginBottom: 'var(--space-md)' }}><Table size={16} style={{ display: 'inline', marginRight: 8 }} />Data Preview (First 5 rows)</h4>
            <div className="table-container">
              <table>
                <thead>
                  <tr>{Object.keys(result.preview[0]).map(col => <th key={col}>{col}</th>)}</tr>
                </thead>
                <tbody>
                  {result.preview.map((row, i) => (
                    <tr key={i}>{Object.values(row).map((val, j) => <td key={j}>{String(val)}</td>)}</tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        <button className="btn btn-primary btn-lg" onClick={() => navigate('/app/audit/configure')} id="continue-to-config">
          Continue to Configure Audit →
        </button>
      </div>
    );
  }

  return (
    <div className="page animate-fade-in">
      <div style={{ maxWidth: 640, margin: '0 auto', paddingTop: '2rem' }}>
        <div className="page-header" style={{ borderBottom: 'none', paddingBottom: 0, marginBottom: 'var(--space-lg)' }}>
          <h1>Upload Test Dataset</h1>
          <p>Step 2 of 3 — Upload a CSV or JSON dataset with ≥10 rows</p>
        </div>

        <div className="card-static">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="dataset-name">Dataset Name</label>
            <input id="dataset-name" className="input" value={datasetName}
              onChange={(e) => setDatasetName(e.target.value)}
              placeholder="e.g., Loan Applications Test Set" />
          </div>

          <div className={`upload-zone ${dragOver ? 'dragover' : ''} ${demoDatasetKey ? 'opacity-50' : ''}`}
            onDragOver={(e) => { if(!demoDatasetKey) { e.preventDefault(); setDragOver(true); } }}
            onDragLeave={() => setDragOver(false)}
            onDrop={demoDatasetKey ? undefined : handleDrop}
            onClick={() => !demoDatasetKey && document.getElementById('dataset-file').click()}>
            <input type="file" id="dataset-file" accept=".csv,.json"
              onChange={handleFileChange} disabled={!!demoDatasetKey} />
            <Upload size={32} style={{ color: 'var(--text-muted)', marginBottom: 8 }} />
            {file ? (
              <p style={{ fontWeight: 600, color: 'var(--color-fair)' }}>
                <CheckCircle size={16} style={{ display: 'inline', marginRight: 6 }} />
                {file.name} ({(file.size / 1024).toFixed(0)}KB)
              </p>
            ) : demoDatasetKey ? (
              <p style={{ fontWeight: 600, color: 'var(--accent-primary)' }}>Using Demo: {demoDatasets.find(d => d.key === demoDatasetKey).name}</p>
            ) : (
              <>
                <p style={{ fontWeight: 500 }}>Drop your dataset file here</p>
                <p className="text-muted" style={{ fontSize: '0.8rem' }}>Supports .csv, .json (max 100MB)</p>
              </>
            )}
          </div>

          {error && <div className="login-error mb-md">{error}</div>}

          <button type="submit" className="btn btn-primary btn-lg w-full mt-md" disabled={loading} id="upload-dataset-btn">
            {loading ? <div className="spinner" /> : 'Upload & Preview'}
          </button>
        </form>
      </div>
      </div>
    </div>
  );
}
