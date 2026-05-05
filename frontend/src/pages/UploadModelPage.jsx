import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { modelsAPI } from '../api/client';
import { Upload, FileCode, Link as LinkIcon, CheckCircle } from 'lucide-react';

export default function UploadModelPage() {
  const navigate = useNavigate();
  const [modelName, setModelName] = useState('');
  const [modelType, setModelType] = useState('classification');
  const [uploadType, setUploadType] = useState('file');
  const [file, setFile] = useState(null);
  const [apiEndpoint, setApiEndpoint] = useState('');
  const [demoModelKey, setDemoModelKey] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [dragOver, setDragOver] = useState(false);

  const demoModels = [
    { key: 'bias_logistic', name: 'Biased Logistic Regression', desc: 'Linear model with historical bias weights' },
    { key: 'bias_rf', name: 'Biased Random Forest', desc: 'Non-linear model capturing complex bias patterns' },
    { key: 'neutral', name: 'Neutral (Fair) Model', desc: 'Trained without sensitive attributes for comparison' }
  ];

  const handleFileChange = (e) => {
    const f = e.target.files?.[0];
    if (f) {
      setFile(f);
      setDemoModelKey(''); // Clear demo if file selected
    }
  };

  const handleDemoSelect = (key) => {
    setDemoModelKey(key);
    setFile(null); // Clear file if demo selected
    const model = demoModels.find(m => m.key === key);
    if (model) setModelName(model.name);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files?.[0];
    if (f) {
      setFile(f);
      setDemoModelKey('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('model_name', modelName || (demoModelKey ? demoModels.find(m => m.key === demoModelKey).name : 'Unnamed Model'));
      formData.append('model_type', modelType);
      formData.append('model_version', '1.0');
      
      if (uploadType === 'file') {
        if (demoModelKey) {
          formData.append('demo_model_key', demoModelKey);
        } else if (file) {
          formData.append('file', file);
        } else {
          throw new Error('Please select a file or a demo model');
        }
      } else if (uploadType === 'api') {
        formData.append('api_endpoint', apiEndpoint);
      }
      
      await modelsAPI.upload(formData);
      setSuccess(true);
      setTimeout(() => navigate('/app/upload/dataset'), 1500);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="page animate-fade-in flex flex-col items-center justify-center" style={{ minHeight: '60vh' }}>
        <div style={{ color: 'var(--color-fair)', marginBottom: 'var(--space-md)' }}>
          <CheckCircle size={64} />
        </div>
        <h2 className="text-glow">Model Registered Successfully!</h2>
        <p className="text-secondary mt-md">Moving to data preparation step...</p>
      </div>
    );
  }

  return (
    <div className="page animate-fade-in">
      <div className="page-header">
        <h1>Model Setup</h1>
        <p>Choose an AI model to audit for bias and fairness</p>
      </div>

      <div className="card-static" style={{ maxWidth: 680, margin: '0 auto' }}>
        <form onSubmit={handleSubmit}>
          <div className="grid-2 gap-md mb-md">
            <div className="form-group">
              <label htmlFor="model-name">Model Name</label>
              <input id="model-name" className="input" value={modelName}
                onChange={(e) => setModelName(e.target.value)}
                placeholder="e.g., Credit Scorer v2" />
            </div>

            <div className="form-group">
              <label>Model Task</label>
              <select className="select" value={modelType} onChange={(e) => setModelType(e.target.value)} id="model-type">
                <option value="classification">Binary Classification</option>
                <option value="regression">Regression (Continuous)</option>
                <option value="multiclass">Multi-class Classification</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>Upload Method</label>
            <div className="radio-group" style={{ gridTemplateColumns: '1fr 1fr' }}>
              <label className={`radio-item ${uploadType === 'file' ? 'active' : ''}`}>
                <input type="radio" value="file" checked={uploadType === 'file'}
                  onChange={(e) => setUploadType(e.target.value)} />
                <FileCode size={16} /> Model File / Presets
              </label>
              <label className={`radio-item ${uploadType === 'api' ? 'active' : ''}`}>
                <input type="radio" value="api" checked={uploadType === 'api'}
                  onChange={(e) => setUploadType(e.target.value)} />
                <LinkIcon size={16} /> Live API URL
              </label>
            </div>
          </div>

          {uploadType === 'file' && (
            <div className="animate-slide-up">
              <div className="mb-md">
                <label style={{ fontSize: '0.85rem', marginBottom: 8, display: 'block', opacity: 0.8 }}>Choose a Demo Model (Quick Start)</label>
                <div className="grid-3 gap-sm">
                  {demoModels.map((m) => (
                    <div 
                      key={m.key}
                      className={`card-interactive p-sm text-center ${demoModelKey === m.key ? 'active-border' : ''}`}
                      onClick={() => handleDemoSelect(m.key)}
                      style={{ cursor: 'pointer', background: 'rgba(255,255,255,0.03)', border: demoModelKey === m.key ? '1px solid var(--accent-primary)' : '1px solid rgba(255,255,255,0.1)' }}
                    >
                      <div style={{ fontWeight: 600, fontSize: '0.8rem' }}>{m.name.split(' ')[0]}</div>
                      <div className="text-muted" style={{ fontSize: '0.7rem' }}>{m.key === 'neutral' ? 'Fair' : 'Biased'}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="divider-text"><span>OR UPLOAD CUSTOM FILE</span></div>

              <div className={`upload-zone ${dragOver ? 'dragover' : ''} ${demoModelKey ? 'opacity-50' : ''}`}
                onDragOver={(e) => { if(!demoModelKey) { e.preventDefault(); setDragOver(true); } }}
                onDragLeave={() => setDragOver(false)}
                onDrop={demoModelKey ? undefined : handleDrop}
                onClick={() => !demoModelKey && document.getElementById('file-input').click()}>
                <input type="file" id="file-input" accept=".pkl,.h5,.pickle,.joblib"
                  onChange={handleFileChange} disabled={!!demoModelKey} />
                <Upload size={32} style={{ color: 'var(--text-muted)', marginBottom: 8 }} />
                {file ? (
                  <p style={{ fontWeight: 600, color: 'var(--color-fair)' }}>{file.name} ({(file.size / 1024 / 1024).toFixed(1)}MB)</p>
                ) : demoModelKey ? (
                  <p style={{ fontWeight: 600, color: 'var(--accent-primary)' }}>Using Demo: {demoModels.find(m => m.key === demoModelKey).name}</p>
                ) : (
                  <>
                    <p style={{ fontWeight: 500 }}>Drop your model file here</p>
                    <p className="text-muted" style={{ fontSize: '0.8rem' }}>Supports .pkl, .joblib, .pickle</p>
                  </>
                )}
              </div>
            </div>
          )}

          {uploadType === 'api' && (
            <div className="form-group animate-slide-up">
              <label htmlFor="api-url">API Endpoint URL</label>
              <input id="api-url" className="input" value={apiEndpoint}
                onChange={(e) => setApiEndpoint(e.target.value)}
                placeholder="https://api.example.com/predict" />
              <p className="text-muted mt-sm" style={{ fontSize: '0.8rem' }}>Make sure your API follows the expected input/output format.</p>
            </div>
          )}

          {error && <div className="login-error mb-md animate-shake">{error}</div>}

          <div className="flex gap-md mt-lg">
            <button type="button" className="btn btn-secondary w-full" onClick={() => navigate('/app')}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary btn-lg w-full" disabled={loading} id="upload-model-btn">
              {loading ? <div className="spinner" /> : 'Continue to Dataset'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
