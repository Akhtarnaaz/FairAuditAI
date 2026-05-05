import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { modelsAPI } from '../api/client';
import { Upload, CheckCircle } from 'lucide-react';

export default function UploadModelPage() {
  const navigate = useNavigate();
  const [modelName, setModelName] = useState('');
  const [modelType, setModelType] = useState('classification');
  const [file, setFile] = useState(null);
  const [demoModelKey, setDemoModelKey] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [dragOver, setDragOver] = useState(false);

  const demoModels = [
    { key: 'loan', name: 'Loan Approval', desc: 'Standard bias' },
    { key: 'loan_extreme', name: 'Loan (Extreme)', desc: 'Severe bias against demographics' },
    { key: 'hiring', name: 'Hiring Model', desc: 'Standard bias' },
    { key: 'hiring_extreme', name: 'Hiring (Extreme)', desc: 'Severe bias against women/minorities' },
    { key: 'healthcare', name: 'Healthcare', desc: 'Standard bias' },
    { key: 'healthcare_extreme', name: 'Healthcare (Extreme)', desc: 'Severe bias in treatment' }
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
      
      if (demoModelKey) {
        formData.append('demo_model_key', demoModelKey);
      } else if (file) {
        formData.append('file', file);
      } else {
        throw new Error('Please select a file');
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

          <div className="animate-slide-up">
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
