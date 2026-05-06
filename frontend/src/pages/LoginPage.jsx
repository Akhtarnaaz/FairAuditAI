import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Shield, Eye, EyeOff } from 'lucide-react';
import './LoginPage.css';

export default function LoginPage() {
  const [isRegister, setIsRegister] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('admin');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, register } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const userStr = localStorage.getItem('user');
    if (userStr && userStr !== 'undefined' && userStr !== 'null') {
      console.log('User found on login page load, redirecting...');
      window.location.href = '/app';
    }

    window.handleCredentialResponse = (response) => {
      try {
        const payload = JSON.parse(atob(response.credential.split('.')[1]));
        const user = {
          name: payload.name,
          email: payload.email,
          picture: payload.picture
        };
        localStorage.setItem('user', JSON.stringify(user));
        console.log('User stored:', user);
        window.location.href = '/app';
      } catch (e) {
        console.error('Error decoding Google JWT', e);
      }
    };

    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    document.body.appendChild(script);

    return () => {
      delete window.handleCredentialResponse;
    };
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (isRegister) {
        await register(name, email, password, role);
      } else {
        await login(email, password);
      }
      navigate('/app');
    } catch (err) {
      setError(err.response?.data?.detail || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-bg-orbs">
        <div className="orb orb-1" />
        <div className="orb orb-2" />
        <div className="orb orb-3" />
      </div>

      <div className="login-container animate-fade-in">
        <div className="login-header">
          <div className="login-logo">
            <Shield size={28} />
          </div>
          <h1>FairAudit AI</h1>
          <p>AI Bias & Fairness Auditor</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {isRegister && (
            <div className="form-group">
              <label htmlFor="name">Full Name</label>
              <input id="name" className="input" type="text" value={name}
                onChange={(e) => setName(e.target.value)} placeholder="Your name" required />
            </div>
          )}

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input id="email" className="input" type="email" value={email}
              onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" required />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <div className="password-field">
              <input id="password" className="input" type={showPassword ? 'text' : 'password'}
                value={password} onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••" required minLength={4} />
              <button type="button" className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}>
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          {isRegister && (
            <div className="form-group">
              <label className="section-label">Select Your Role</label>
              <div className="role-cards">
                <div 
                  className={`role-card ${role === 'admin' ? 'active' : ''}`}
                  onClick={() => setRole('admin')}
                >
                  <div className="role-icon">🛡️</div>
                  <div className="role-info">
                    <span className="role-name">Admin (Auditor)</span>
                    <span className="role-desc">Full access to upload models, datasets, and run bias audits.</span>
                  </div>
                </div>
                
                <div 
                  className={`role-card ${role === 'user' ? 'active' : ''}`}
                  onClick={() => setRole('user')}
                >
                  <div className="role-icon">👁️</div>
                  <div className="role-info">
                    <span className="role-name">Viewer</span>
                    <span className="role-desc">Read-only access to results, dashboard, and reports.</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {error && <div className="login-error">{error}</div>}

          <button type="submit" className="btn btn-primary btn-lg w-full" disabled={loading} id="login-submit">
            {loading ? <div className="spinner" /> : (isRegister ? 'Create Account' : 'Sign In')}
          </button>

          <div style={{ textAlign: 'center', margin: '16px 0', color: 'var(--text-muted)', fontSize: '0.9rem', fontWeight: 500 }}>
            OR
          </div>

          <div style={{ display: 'flex', justifyContent: 'center' }}>
            <div id="g_id_onload"
                 data-client_id="147176817718-mjru1oe3muc4ko1vn1l7n4gh7bba4qcm.apps.googleusercontent.com"
                 data-callback="handleCredentialResponse">
            </div>
            <div className="g_id_signin" data-type="standard" data-size="large" data-theme="outline" data-text="continue_with" data-shape="rectangular" data-logo_alignment="left" style={{ width: '100%' }}></div>
          </div>
        </form>

        <div className="login-footer">
          <button className="login-toggle" onClick={() => { setIsRegister(!isRegister); setError(''); }}>
            {isRegister ? 'Already have an account? Sign in' : "Don't have an account? Register"}
          </button>
        </div>
      </div>
    </div>
  );
}
