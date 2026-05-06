import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, BarChart3, Search, FileCheck, ArrowRight, ExternalLink, ChevronDown } from 'lucide-react';
import './LandingPage.css';

const faqs = [
  { question: "What is AI bias?", answer: "AI bias occurs when machine learning models produce consistently prejudiced or unfair outcomes for specific demographic groups, often due to flawed training data or algorithmic assumptions." },
  { question: "How does FairAudit AI detect bias?", answer: "We use Counterfactual Testing—automatically swapping demographic markers (like names, genders, or regions) in your data to see if the model's prediction changes based solely on identity." },
  { question: "What is counterfactual testing?", answer: "It's a 'what-if' testing methodology. If an applicant is denied a loan, we test if an identical applicant with a different demographic background would have been approved." },
  { question: "Can this tool be used in real-world AI systems?", answer: "Yes. FairAudit AI is built to test standard ML models (.joblib, .pkl) and datasets, providing concrete metrics (like Disparate Impact Ratio) used by compliance teams globally." },
  { question: "Is user data stored securely?", answer: "Absolutely. Models and datasets are processed securely, and you maintain full control over your uploaded artifacts. We use role-based access to protect sensitive audit reports." }
];

function FAQItem({ question, answer, isOpen, onClick }) {
  return (
    <div className={`faq-item ${isOpen ? 'open' : ''}`} onClick={onClick}>
      <div className="faq-question">
        <h4>{question}</h4>
        <ChevronDown size={20} className="faq-icon" />
      </div>
      <div className="faq-answer">
        <p>{answer}</p>
      </div>
    </div>
  );
}

export default function LandingPage() {
  const navigate = useNavigate();
  const [openFaqIndex, setOpenFaqIndex] = useState(null);

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
          <button onClick={() => navigate('/login')} className="btn btn-primary btn-sm">Sign In</button>
        </div>
      </nav>

      {/* ── Hero Section ── */}
      <header className="hero-section container">
        <div className="hero-content animate-slide-up">
          <h1>Bring your own models <br /><span>and we will audit it for bias</span></h1>
          <p>
            Detect, measure, and explain bias in your AI models using advanced 
            counterfactual testing. Build trust through transparency.
          </p>
          <div className="hero-actions">
            <button onClick={() => navigate('/login')} className="btn btn-primary btn-lg">
              Start Your First Audit <ArrowRight size={18} />
            </button>
          </div>
        </div>
        
        <div className="hero-visual animate-fade-in">
          <div className="glass-card dashboard-preview">
            <div className="preview-header">
              <div className="dot red" />
              <div className="dot orange" />
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

      {/* ── Separator ── */}
      <div className="section-separator" />

      {/* ── FAQ Section ── */}
      <section className="faq-section container animate-slide-up">
        <div className="faq-grid">
          <div className="faq-info">
            <h2>Frequently Asked Questions</h2>
            <p>Everything you need to know about AI fairness and our auditing process.</p>
            
            <div className="faq-illustration">
              <Shield size={48} className="text-accent" style={{ opacity: 0.8, marginBottom: 16 }} />
              <h3>Need more help?</h3>
              <p>Our team is here to support you in building fair, transparent, and compliant AI models.</p>
            </div>
          </div>
          
          <div className="faq-list">
            {faqs.map((faq, index) => (
              <FAQItem 
                key={index} 
                question={faq.question} 
                answer={faq.answer} 
                isOpen={openFaqIndex === index}
                onClick={() => setOpenFaqIndex(openFaqIndex === index ? null : index)}
              />
            ))}
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="landing-footer container">
        <div className="footer-brand-center">
          <Shield size={36} className="text-accent" />
          <span className="footer-title">FairAudit AI</span>
        </div>
        <div className="footer-bottom-center">
          <p>Copyright © 2026 FairAudit AI by Team ByteCore. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
