import { Link } from 'react-router-dom';

function Home() {
  return (
    <div className="container-wide">
      <section className="hero">
        <div className="orb orb-1"></div>
        <div className="orb orb-2"></div>

        <div className="hero-content">
          <div className="hero-badge">
            <div className="hero-badge-dot"></div>
            AI Model v2.0 — Gender, Lifestyle & Environment Aware
          </div>

          <h1 className="hero-title">
            <span className="gradient-text">Kidney Health</span><br />
            Diagnostic Platform
          </h1>

          <p className="hero-subtitle">
            Advanced 6-class XGBoost model trained on 120,000+ samples. Now analyzing
            <strong>gender</strong>, <strong>smoking impact</strong>, and
            <strong>water quality by location</strong> for comprehensive risk assessment.
          </p>

          <div className="hero-actions">
            <Link to="/diagnosis" className="btn btn-primary btn-lg">
              🔬 Start Diagnosis
            </Link>
            <Link to="/analytics" className="btn btn-ghost btn-lg">
              📊 View Analytics
            </Link>
          </div>
        </div>
      </section>

      <div className="stats-bar">
        <div className="stat-item animate-in">
          <div className="stat-value gradient-text">120K+</div>
          <div className="stat-label">Training Samples</div>
        </div>
        <div className="stat-item animate-in delay-1">
          <div className="stat-value gradient-text">11</div>
          <div className="stat-label">Features Analyzed</div>
        </div>
        <div className="stat-item animate-in delay-2">
          <div className="stat-value gradient-text">6</div>
          <div className="stat-label">Diagnostic Classes</div>
        </div>
        <div className="stat-item animate-in delay-3">
          <div className="stat-value gradient-text">60+</div>
          <div className="stat-label">Locations Mapped</div>
        </div>
      </div>

      <section className="features-section">
        <div className="text-center mb-3">
          <h2 className="section-title gradient-text">What's New in V2</h2>
          <p className="section-subtitle">Three critical risk dimensions added to the diagnostic engine</p>
        </div>

        <div className="grid-3">
          <div className="feature-card animate-in delay-1">
            <div className="feature-icon" style={{ background: 'rgba(59,130,246,0.12)' }}>⚧</div>
            <div className="feature-title">Gender-Aware Analysis</div>
            <div className="feature-desc">
              Males and females have different creatinine baselines, hormonal protection levels,
              and kidney stone prevalence. The model now accounts for these clinical differences.
            </div>
          </div>

          <div className="feature-card animate-in delay-2">
            <div className="feature-icon" style={{ background: 'rgba(249,115,22,0.12)' }}>🚬</div>
            <div className="feature-title">Smoking Impact Scoring</div>
            <div className="feature-desc">
              Smoking accelerates kidney damage through vasoconstriction and oxidative stress.
              See exactly how much smoking shifts your risk profile vs. a non-smoker.
            </div>
          </div>

          <div className="feature-card animate-in delay-3">
            <div className="feature-icon" style={{ background: 'rgba(16,185,129,0.12)' }}>💧</div>
            <div className="feature-title">Location Water Quality</div>
            <div className="feature-desc">
              Select your city or region — we map it to local water sodium levels.
              High-sodium water is a direct trigger for kidney stones and hypertension.
            </div>
          </div>
        </div>
      </section>

      <section className="how-section mt-4">
        <div className="text-center mb-3">
          <h2 className="section-title gradient-text-accent">How It Works</h2>
          <p className="section-subtitle">Three steps to a comprehensive kidney risk assessment</p>
        </div>

        <div style={{ maxWidth: '600px', margin: '0 auto' }}>
          <div className="step-card animate-in delay-1">
            <div className="step-number">1</div>
            <div>
              <div className="step-title">Enter Patient Data</div>
              <div className="step-desc">Input lab results, demographics, lifestyle factors, and select your location for water quality analysis.</div>
            </div>
          </div>
          <div className="step-card animate-in delay-2">
            <div className="step-number">2</div>
            <div>
              <div className="step-title">AI Analysis</div>
              <div className="step-desc">The XGBoost model processes 11 features including engineered ratios to classify across 6 kidney conditions.</div>
            </div>
          </div>
          <div className="step-card animate-in delay-3">
            <div className="step-number">3</div>
            <div>
              <div className="step-title">Deep Analytics</div>
              <div className="step-desc">Get gender comparisons, smoking impact scores, water quality assessments, and personalized recommendations.</div>
            </div>
          </div>
        </div>
      </section>

      <section className="cta-section mt-4 mb-4">
        <div className="cta-card animate-in glass-card text-center">
          <div className="cta-title section-title gradient-text">Ready to Analyze?</div>
          <p className="cta-desc section-subtitle">Start with the diagnostic form to get your AI-powered kidney health assessment with environment and lifestyle risk factors.</p>
          <Link to="/diagnosis" className="btn btn-primary btn-lg">
            🔬 Begin Diagnosis Now
          </Link>
        </div>
      </section>

      <footer className="footer">
        <p>Kidney Diagnostic Analytics Platform — AI-Powered Research Tool</p>
        <p style={{ marginTop: '4px' }}>Model trained on synthetic data. For research and educational purposes only. Not a substitute for professional medical advice.</p>
      </footer>
    </div>
  );
}

export default Home;
