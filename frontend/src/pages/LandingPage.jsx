import { useNavigate } from 'react-router-dom';
import { Shield, BarChart3, Search, FileCheck, ArrowRight, ExternalLink } from 'lucide-react';
import './LandingPage.css';

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="landing-page">
      {/* ── Background Orbs ── */}
      <div className="landing-bg-orbs">
        <div className="orb orb-1" />
        <div className="orb orb-2" />
        <div className="orb orb-3" />
      </div>

      {/* ── Navigation ── */}
      <nav className="landing-nav animate-fade-in">
        <div className="nav-logo">
          <Shield size={24} className="text-accent" />
          <span>FairAudit AI</span>
        </div>
        <div className="nav-links">
          <button onClick={() => navigate('/login')} className="nav-btn-text">Sign In</button>
          <button onClick={() => navigate('/login')} className="btn btn-primary btn-sm">Get Started</button>
        </div>
      </nav>

      {/* ── Hero Section ── */}
      <header className="hero-section container">
        <div className="hero-content animate-slide-up">
          <div className="badge">v1.0 is now live</div>
          <h1>Make AI Fairness <br /><span>Quantifiable & Actionable</span></h1>
          <p>
            Detect, measure, and explain bias in your AI models using advanced 
            counterfactual testing. Build trust through transparency.
          </p>
          <div className="hero-actions">
            <button onClick={() => navigate('/login')} className="btn btn-primary btn-lg">
              Start Your First Audit <ArrowRight size={18} />
            </button>
            <button className="btn btn-outline btn-lg">
              <ExternalLink size={18} /> Documentation
            </button>
          </div>
        </div>
        
        <div className="hero-visual animate-fade-in">
          <div className="glass-card dashboard-preview">
            <div className="preview-header">
              <div className="dot red" />
              <div className="dot yellow" />
              <div className="dot green" />
              <span className="preview-title">Fairness Dashboard</span>
            </div>
            <div className="preview-body">
              <div className="preview-chart">
                <div className="bar" style={{ height: '60%' }} />
                <div className="bar active" style={{ height: '85%' }} />
                <div className="bar" style={{ height: '45%' }} />
                <div className="bar" style={{ height: '70%' }} />
              </div>
              <div className="preview-stats">
                <div className="stat-item">
                  <span className="stat-label">Disparate Impact</span>
                  <span className="stat-value text-error">0.72 (Alert)</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Demographic Parity</span>
                  <span className="stat-value text-success">0.91 (Passed)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* ── Features ── */}
      <section className="features-section container">
        <div className="section-header text-center">
          <h2>Trust, Built on Data</h2>
          <p>Our comprehensive toolset handles the heavy lifting of bias auditing.</p>
        </div>

        <div className="features-grid">
          <div className="feature-card glass-card">
            <div className="feature-icon"><Search /></div>
            <h3>Counterfactual Testing</h3>
            <p>Automatically generate thousands of "what-if" scenarios by swapping demographic markers.</p>
          </div>
          
          <div className="feature-card glass-card">
            <div className="feature-icon"><BarChart3 /></div>
            <h3>Bias Scoring</h3>
            <p>Industry-standard metrics including Disparate Impact Ratio and Equality of Opportunity.</p>
          </div>
          
          <div className="feature-card glass-card">
            <div className="feature-icon"><FileCheck /></div>
            <h3>Mitigation Engine</h3>
            <p>Get actionable code-level and data-level recommendations to fix detected biases.</p>
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="landing-footer container">
        <p>© 2026 FairAudit AI. Built for the future of responsible AI.</p>
      </footer>
    </div>
  );
}
